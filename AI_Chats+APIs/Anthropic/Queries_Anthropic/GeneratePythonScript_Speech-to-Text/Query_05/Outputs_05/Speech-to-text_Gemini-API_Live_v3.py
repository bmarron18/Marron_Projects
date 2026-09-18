#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New: continuous, real-time English speech -> Spanish speech + text, using
Google's Gemini Live API (WebSocket streaming), instead of the old
VAD-then-batch design.

@author: bruce-vdb
"""

# %%

'''
Update pip and check packages installed in virtual environment (ai-apis)

<<< bash
cd ~/spyder-6/envs &&
source ./ai-apis/bin/activate
(ai-apis) pip install --upgrade pip &&
pip install --upgrade google-genai &&
pip list
(ai-apis) deactivate
>>>bash

'''

# %%

'''
    # Run script in (ai-apis) virtual environment
<<< bash
cd ~/spyder-6/envs &&
source ./ai-apis/bin/activate
export AUDIO_INPUT_DEVICE=pulse
export GEMINI_API_KEY='...'
(ai-apis) python3 ~/Desktop/Gemini_speech-to-text_translation-transcription_live.py

(ai-apis) deactivate
>>>bash

    # Optional tuning knobs:
    export AUDIO_INPUT_DEVICE=2   # index or name-substring from device list
    export PLAY_TRANSLATED_AUDIO=1  # also play the Spanish audio out loud
'''

# %%

"""
Real-time English speech -> Spanish speech, with EN/ES text transcripts.

Pipeline (fundamentally different from the old VAD/batch script)
  1. Microphone audio is streamed continuously, in small chunks, straight
     into a persistent WebSocket session with Gemini's Live API.
  2. gemini-3.5-live-translate-preview does speech-to-speech translation on
     that stream directly -- there is no separate "detect an utterance,
     then call STT, then call a translator" pipeline. The model itself
     decides where sentences begin/end (via its own built-in VAD) and
     streams back translated Spanish audio continuously, a few seconds
     behind the speaker.
  3. Because input_audio_transcription / output_audio_transcription are
     enabled in the session config, the model also streams back the
     English and Spanish TEXT transcripts alongside the Spanish audio, so
     we can still keep a running EN/ES text log exactly like the old
     script did.
  4. (Optional) The translated Spanish audio can also be played back
     through your speakers in real time -- set PLAY_TRANSLATED_AUDIO=1.

Stop with Ctrl+C.

NOTE ON gemini-3.5-transcribe-live
-------------------------------------
That model is a separate, transcription-ONLY Live API model (no
translation). Since gemini-3.5-live-translate-preview already returns both
the English and Spanish transcripts itself (via
input_audio_transcription / output_audio_transcription), a single
Live Translate session covers this script's whole job and we don't need a
second concurrent transcribe-live session. If you ever want raw English
transcription only (no translation), gemini-3.5-transcribe-live is the
model to reach for instead, following the same streaming pattern used here.
"""

# %%

import asyncio
import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
from google import genai
from google.genai import types

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
INPUT_SAMPLE_RATE  = 16_000     # Hz -- what we send to the model
OUTPUT_SAMPLE_RATE = 24_000     # Hz -- what the Live API sends back (PCM16)
CHANNELS           = 1
CHUNK_MS           = 100        # size of each audio chunk streamed out

AUDIO_INPUT_DEVICE = os.getenv("AUDIO_INPUT_DEVICE")
PLAY_TRANSLATED_AUDIO = os.getenv("PLAY_TRANSLATED_AUDIO", "0") == "1"

STT_MODEL       = "gemini-3.5-transcribe-live"        # (see note above; unused by default)
TRANSLATE_MODEL = "gemini-3.5-live-translate-preview"  # speech-to-speech EN -> ES
SOURCE_LANG     = "en"
TARGET_LANG     = "es"

DESKTOP  = Path("/home/bruce-vdb/Desktop")
OUT_FILE = DESKTOP / f"live_translation_{datetime.now():%Y%m%d_%H%M%S}.txt"

CHUNK_FRAMES = int(INPUT_SAMPLE_RATE * CHUNK_MS / 1000)

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

file_lock = threading.Lock()


# ----------------------------------------------------------------------------
# Output helpers
# ----------------------------------------------------------------------------
def write_line(lang_tag: str, text: str) -> None:
    if not text:
        return
    stamp = datetime.now().strftime("%H:%M:%S")
    with file_lock, OUT_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"[{stamp}] {lang_tag}: {text}\n")
        fh.flush()
        os.fsync(fh.fileno())


# ----------------------------------------------------------------------------
# Device selection helper
# ----------------------------------------------------------------------------
def resolve_input_device():
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
        return None

    try:
        idx = int(AUDIO_INPUT_DEVICE)
        print(f"Using AUDIO_INPUT_DEVICE index {idx}", flush=True)
        return idx
    except ValueError:
        pass

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
# Microphone -> asyncio queue
# ----------------------------------------------------------------------------
class MicStreamer:
    """Bridges the blocking sounddevice callback thread into asyncio."""

    def __init__(self, device, loop: asyncio.AbstractEventLoop):
        self.queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._loop = loop
        self.stream = sd.InputStream(
            samplerate=INPUT_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_FRAMES,
            device=device,
            callback=self._callback,
        )

    def _callback(self, indata, frames, time_info, status):  # noqa: ANN001
        if status:
            print(f"[audio] {status}", file=sys.stderr, flush=True)
        pcm_bytes = indata[:, 0].copy().tobytes()
        self._loop.call_soon_threadsafe(self.queue.put_nowait, pcm_bytes)

    def __enter__(self):
        self.stream.start()
        return self

    def __exit__(self, *exc):
        self.stream.stop()
        self.stream.close()


# ----------------------------------------------------------------------------
# Optional speaker playback of the translated Spanish audio
# ----------------------------------------------------------------------------
class SpeakerPlayer:
    def __init__(self):
        self.stream = sd.RawOutputStream(
            samplerate=OUTPUT_SAMPLE_RATE,
            channels=1,
            dtype="int16",
        )

    def __enter__(self):
        self.stream.start()
        return self

    def __exit__(self, *exc):
        self.stream.stop()
        self.stream.close()

    def play(self, pcm_bytes: bytes) -> None:
        self.stream.write(pcm_bytes)


# ----------------------------------------------------------------------------
# Sender: mic queue -> Live API session
# ----------------------------------------------------------------------------
async def sender(session, mic: MicStreamer, stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            chunk = await asyncio.wait_for(mic.queue.get(), timeout=0.5)
        except asyncio.TimeoutError:
            continue
        await session.send_realtime_input(
            audio=types.Blob(data=chunk, mime_type=f"audio/pcm;rate={INPUT_SAMPLE_RATE}")
        )


# ----------------------------------------------------------------------------
# Receiver: Live API session -> text log (+ optional audio playback)
# ----------------------------------------------------------------------------
async def receiver(session, stop: asyncio.Event, player: "SpeakerPlayer | None") -> None:
    current_en, current_es = "", ""
    try:
        async for response in session.receive():
            if stop.is_set():
                break
            server_content = response.server_content
            if not server_content:
                continue

            if server_content.input_transcription and server_content.input_transcription.text:
                current_en += server_content.input_transcription.text

            if server_content.output_transcription and server_content.output_transcription.text:
                current_es += server_content.output_transcription.text

            if player is not None and server_content.model_turn:
                for part in server_content.model_turn.parts or []:
                    if part.inline_data and part.inline_data.data:
                        player.play(part.inline_data.data)

            if server_content.turn_complete:
                current_en = current_en.strip()
                current_es = current_es.strip()
                if current_en or current_es:
                    print(f"\nEN  {current_en}\nES  {current_es}\n", flush=True)
                    write_line("EN", current_en)
                    write_line("ES", current_es)
                current_en, current_es = "", ""
    except Exception:
        print("[error] receiver failed:", file=sys.stderr, flush=True)
        traceback.print_exc()
    finally:
        stop.set()


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
async def main_async() -> None:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        f"Live English -> Spanish session started {datetime.now():%Y-%m-%d %H:%M:%S}\n\n",
        encoding="utf-8",
    )

    device = resolve_input_device()
    in_use = sd.query_devices(device, kind="input") if device is not None else sd.query_devices(kind="input")
    print(f"Input device : {in_use['name']}", flush=True)
    print(f"Transcript   : {OUT_FILE}", flush=True)
    print(f"Model        : {TRANSLATE_MODEL}", flush=True)
    print(f"Playback     : {'on' if PLAY_TRANSLATED_AUDIO else 'off'} "
          f"(set PLAY_TRANSLATED_AUDIO=1 to hear the Spanish audio)", flush=True)

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        translation_config=types.TranslationConfig(
            target_language_code=TARGET_LANG,
            echo_target_language=False,
        ),
    )

    loop = asyncio.get_running_loop()
    stop = asyncio.Event()

    try:
        async with client.aio.live.connect(model=TRANSLATE_MODEL, config=config) as session:
            print("Connected. Listening. Speak English.  Ctrl+C to stop.\n", flush=True)

            with MicStreamer(device, loop) as mic:
                player_cm = SpeakerPlayer() if PLAY_TRANSLATED_AUDIO else None
                player = player_cm.__enter__() if player_cm else None
                try:
                    await asyncio.gather(
                        sender(session, mic, stop),
                        receiver(session, stop, player_cm),
                    )
                finally:
                    if player_cm:
                        player_cm.__exit__(None, None, None)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        print(f"\nDone. Transcript saved to {OUT_FILE}", flush=True)


def main() -> None:
    if not os.getenv("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY is not set.  export GEMINI_API_KEY='...'")
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nStopping...", flush=True)


if __name__ == "__main__":
    main()
# %%
