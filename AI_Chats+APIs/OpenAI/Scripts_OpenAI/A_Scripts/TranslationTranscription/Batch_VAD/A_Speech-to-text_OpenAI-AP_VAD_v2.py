#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Revised: added diagnostics to fix "runs fine, prints nothing" issue.

@author: bruce-vdb, Claude Opus 5
"""


import io
import os
import queue
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
SAMPLE_RATE      = 16_000      # Hz, what the speech models like
CHANNELS         = 1
BLOCK_MS         = 30          # audio block size fed to the VAD
SILENCE_MS       = 700         # trailing silence that ends an utterance
MIN_UTTERANCE_MS = 400         # ignore blips shorter than this
MAX_UTTERANCE_MS = 15_000      # force a flush on very long monologues
CALIBRATION_S    = 1.0         # seconds of room tone used for the noise floor
PRE_ROLL_BLOCKS  = 5           # blocks kept before speech onset (~150 ms)
HEARTBEAT_S      = 1.0         # how often to print the live RMS diagnostic

# How many multiples of the noise floor count as "speech". Lower this
# (e.g. export VAD_MARGIN=1.8) if the heartbeat shows your voice never
# clears the threshold.
VAD_MARGIN = float(os.getenv("VAD_MARGIN", "3.0"))

# Pin a specific input device if the default one isn't your mic. Accepts
# either a device index (e.g. "2") or a substring of the device name
# (e.g. "USB"). Leave unset to use the system default.
AUDIO_INPUT_DEVICE = os.getenv("AUDIO_INPUT_DEVICE")

STT_MODEL        = "gpt-4o-transcribe"   # newest speech-to-text model
TRANSLATE_MODEL  = "gpt-4.1-mini"        # fast, cheap, good translations
SOURCE_LANG      = "en"

DESKTOP   = Path("/home/bruce-vdb/Desktop")
OUT_FILE  = DESKTOP / f"live_translation_{datetime.now():%Y%m%d_%H%M%S}.txt"

BLOCK_FRAMES   = int(SAMPLE_RATE * BLOCK_MS / 1000)
SILENCE_BLOCKS = max(1, SILENCE_MS // BLOCK_MS)
MIN_BLOCKS     = max(1, MIN_UTTERANCE_MS // BLOCK_MS)
MAX_BLOCKS     = max(1, MAX_UTTERANCE_MS // BLOCK_MS)


# API_KEY is saved as an ENV VARIABLE on home computer
client = OpenAI(api_key= os.getenv("OPENAI_API_KEY"))


audio_q: "queue.Queue[np.ndarray]" = queue.Queue()         # mic -> VAD
work_q:  "queue.Queue[np.ndarray | None]" = queue.Queue()  # VAD -> API worker
stop_event = threading.Event()

file_lock = threading.Lock()


# ----------------------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------------------
def write_pair(english: str, spanish: str) -> None:
    stamp = datetime.now().strftime("%H:%M:%S")
    with file_lock, OUT_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"[{stamp}] EN: {english}\n")
        fh.write(f"[{stamp}] ES: {spanish}\n\n")
        fh.flush()
        os.fsync(fh.fileno())


# ----------------------------------------------------------------------------
# Device selection helper
# ----------------------------------------------------------------------------
def resolve_input_device():
    """Print available input devices; resolve AUDIO_INPUT_DEVICE if set."""
    devices = sd.query_devices()
    print("Available input devices:", flush=True)
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            default_flag = ""
            try:
                if idx == sd.default.device[0]:
                    default_flag = "  <-- current default"
            except Exception:
                pass
            print(f"  [{idx}] {dev['name']}{default_flag}", flush=True)

    if not AUDIO_INPUT_DEVICE:
        return None  # use system default

    # Try as an integer index first.
    try:
        idx = int(AUDIO_INPUT_DEVICE)
        print(f"Using AUDIO_INPUT_DEVICE index {idx}", flush=True)
        return idx
    except ValueError:
        pass

    # Otherwise treat it as a substring match on device name.
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0 and AUDIO_INPUT_DEVICE.lower() in dev["name"].lower():
            print(f"Using device [{idx}] {dev['name']} (matched '{AUDIO_INPUT_DEVICE}')", flush=True)
            return idx

    print(
        f"[warning] AUDIO_INPUT_DEVICE='{AUDIO_INPUT_DEVICE}' did not match any device; "
        f"falling back to system default.",
        file=sys.stderr,
        flush=True,
    )
    return None


# ----------------------------------------------------------------------------
# OpenAI calls
# ----------------------------------------------------------------------------
def pcm_to_wav_bytes(pcm: np.ndarray) -> io.BytesIO:
    buf = io.BytesIO()
    sf.write(buf, pcm, SAMPLE_RATE, format="WAV", subtype="PCM_16")
    buf.seek(0)
    buf.name = "utterance.wav"          # the SDK uses the extension as a hint
    return buf


def transcribe(pcm: np.ndarray) -> str:
    resp = client.audio.transcriptions.create(
        model=STT_MODEL,
        file=pcm_to_wav_bytes(pcm),
        language=SOURCE_LANG,
        response_format="text",
        prompt="Transcribe verbatim. Do not translate.",
    )
    return (resp if isinstance(resp, str) else resp.text).strip()


def translate(text: str) -> str:
    # Chat Completions is used here (rather than the Responses API) for
    # broad compatibility and simpler, well-documented error behavior.
    resp = client.chat.completions.create(
        model=TRANSLATE_MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional translator. Translate the user's "
                    "English text into natural, fluent Latin-American Spanish. "
                    "Output ONLY the Spanish translation: no notes, quotes, or "
                    "explanations."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return resp.choices[0].message.content.strip()


# ----------------------------------------------------------------------------
# Worker: utterance -> transcription -> translation -> outputs
# ----------------------------------------------------------------------------
def worker() -> None:
    while True:
        pcm = work_q.get()
        if pcm is None:                       # shutdown sentinel
            work_q.task_done()
            return
        try:
            english = transcribe(pcm)
            if english and any(c.isalnum() for c in english):
                spanish = translate(english)
                print(f"\nEN  {english}\nES  {spanish}\n", flush=True)
                write_pair(english, spanish)
            else:
                print("[info] Utterance produced no usable transcription (silence/noise?)",
                      flush=True)
        except Exception:                       # noqa: BLE001
            print("[error] worker failed on this utterance:", file=sys.stderr, flush=True)
            traceback.print_exc()
        finally:
            work_q.task_done()


# ----------------------------------------------------------------------------
# Microphone callback
# ----------------------------------------------------------------------------
def audio_callback(indata, frames, time_info, status):   # noqa: ANN001
    if status:
        print(f"[audio] {status}", file=sys.stderr, flush=True)
    audio_q.put(indata[:, 0].copy())


# ----------------------------------------------------------------------------
# Main loop: capture + VAD segmentation
# ----------------------------------------------------------------------------
def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set.  export OPENAI_API_KEY='sk-...'")

    DESKTOP.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        f"Live English -> Spanish session started {datetime.now():%Y-%m-%d %H:%M:%S}\n\n",
        encoding="utf-8",
    )

    threading.Thread(target=worker, daemon=True).start()

    device = resolve_input_device()

    try:
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            blocksize=BLOCK_FRAMES,
            device=device,
            callback=audio_callback,
        )
    except Exception:
        print("[error] Could not open the input stream:", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)

    in_use = sd.query_devices(device, kind="input") if device is not None else sd.query_devices(kind="input")
    print(f"Input device : {in_use['name']}", flush=True)
    print(f"Transcript   : {OUT_FILE}", flush=True)
    print(f"VAD_MARGIN   : {VAD_MARGIN}", flush=True)
    print("Calibrating background noise, stay quiet for a second...", flush=True)

    with stream:
        # --- noise-floor calibration -------------------------------------
        levels, t0 = [], time.time()
        while time.time() - t0 < CALIBRATION_S:
            try:
                levels.append(float(np.sqrt(np.mean(audio_q.get(timeout=1) ** 2))))
            except queue.Empty:
                break

        if not levels:
            print(
                "[warning] No audio blocks were captured during calibration. "
                "The input stream may be silent (wrong device, muted mic, or "
                "permissions issue). Check the device list above.",
                file=sys.stderr,
                flush=True,
            )

        noise_floor = max(float(np.median(levels)) if levels else 0.0, 1e-4)
        threshold = noise_floor * VAD_MARGIN
        if levels:
            print(
                f"Calibration levels -> min {min(levels):.5f}  "
                f"median {np.median(levels):.5f}  max {max(levels):.5f}",
                flush=True,
            )
        print(f"Noise floor {noise_floor:.5f} -> speech threshold {threshold:.5f}", flush=True)
        print("Listening. Speak English.  Ctrl+C to stop.\n", flush=True)

        # --- segmentation -------------------------------------------------
        pre_roll: list[np.ndarray] = []
        buffer:   list[np.ndarray] = []
        speaking = False
        silent_blocks = 0
        last_heartbeat = time.time()
        last_rms = 0.0

        try:
            while True:
                try:
                    block = audio_q.get(timeout=0.5)
                except queue.Empty:
                    # No audio arriving at all -- surface this loudly rather
                    # than sitting silent.
                    now = time.time()
                    if now - last_heartbeat >= HEARTBEAT_S:
                        print("[heartbeat] no audio blocks received in the last 0.5s+ "
                              "-- check mic/device.", flush=True)
                        last_heartbeat = now
                    continue

                rms = float(np.sqrt(np.mean(block ** 2)))
                last_rms = rms
                loud = rms > threshold

                if not speaking:
                    pre_roll.append(block)
                    if len(pre_roll) > PRE_ROLL_BLOCKS:
                        pre_roll.pop(0)
                    if loud:
                        speaking = True
                        silent_blocks = 0
                        buffer = pre_roll[:] + []
                        pre_roll = []
                        print("  ...recording", end="\r", flush=True)
                    else:
                        # slow adaptation of the noise floor during silence
                        noise_floor = 0.995 * noise_floor + 0.005 * rms
                        threshold = max(noise_floor * VAD_MARGIN, 1e-4)
                else:
                    buffer.append(block)
                    silent_blocks = 0 if loud else silent_blocks + 1

                    if silent_blocks >= SILENCE_BLOCKS or len(buffer) >= MAX_BLOCKS:
                        speaking = False
                        if len(buffer) >= MIN_BLOCKS:
                            work_q.put(np.concatenate(buffer))
                            print("  ...processing ", end="\r", flush=True)
                        buffer = []

                # Live heartbeat so you can watch RMS vs threshold in
                # real time and confirm the mic is actually live.
                now = time.time()
                if not speaking and now - last_heartbeat >= HEARTBEAT_S:
                    print(
                        f"[heartbeat] rms={last_rms:.5f}  threshold={threshold:.5f}  "
                        f"{'ABOVE (should trigger)' if last_rms > threshold else 'below'}",
                        end="\r",
                        flush=True,
                    )
                    last_heartbeat = now

        except KeyboardInterrupt:
            print("\nStopping...", flush=True)
            if speaking and len(buffer) >= MIN_BLOCKS:
                work_q.put(np.concatenate(buffer))

    work_q.put(None)
    work_q.join()
    print(f"Done. Transcript saved to {OUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
