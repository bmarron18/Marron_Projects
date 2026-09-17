#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 19:30:11 2026

@author: bruce-vdb
"""

# %%

'''
Update pip and check packages installes in virtual environment (ai-apis)

<<< bash
cd ~/spyder-6/envs &&
source ./ai-apis/bin/activate
(ai-apis) pip install --upgrade pip &&
pip list
(ai-apis) deactivate
>>>bash

'''

# %%

'''
List of Installed Packages
(as of 13 Sept 2026)


Package                 Version
----------------------- ------------
annotated-types         0.8.0
anthropic               1.5.0
anyio                   4.14.2
arabic-reshaper         3.0.1
asttokens               3.0.2
Bottleneck              1.6.0
certifi                 2026.7.22
cffi                    2.1.1
charset-normalizer      3.4.9
cloudpickle             3.1.2
comm                    0.2.3
contourpy               1.3.3
cryptography            50.0.0
cycler                  0.12.1
debugpy                 1.8.21
distro                  1.9.0
docstring_parser        0.18.0
executing               2.2.1
fonttools               4.63.0
google-auth             2.56.3
google-genai            2.23.0
h11                     0.16.0
httpcore                1.0.9
httpcore2               2.12.0
httpx                   0.28.1
httpx2                  2.12.0
idna                    3.18
ipykernel               6.31.0
ipython                 9.16.1
ipython_pygments_lexers 1.1.1
jedi                    0.20.0
jiter                   0.16.0
jupyter_client          8.9.1
jupyter_core            5.9.1
kiwisolver              1.5.0
llvmlite                0.48.0
matplotlib              3.11.1
matplotlib-inline       0.2.2
mizani                  0.14.4
nest-asyncio            1.6.0
numba                   0.66.0
numexpr                 2.14.2
numpy                   2.4.6
openai                  3.13.0
packaging               26.3
pandas                  3.0.5
parso                   0.8.7
patsy                   1.0.2
pexpect                 4.9.0
pillow                  12.3.0
pip                     26.2.1
platformdirs            4.11.0
plotnine                0.15.7
prompt_toolkit          3.0.53
psutil                  7.2.2
ptyprocess              0.7.0
pure_eval               0.2.3
pyasn1                  0.6.4
pyasn1_modules          0.4.2
PyAudio                 0.2.14
pycparser               3.0
pydantic                2.13.4
pydantic_core           2.46.4
Pygments                2.20.0
pyparsing               3.3.2
pypdf                   6.16.1
python-bidi             0.6.11
python-dateutil         2.9.0.post0
pytz                    2026.3.post1
pyxdg                   0.28
pyzmq                   27.1.0
requests                2.34.2
scipy                   1.18.0
six                     1.17.0
sniffio                 1.3.1
sounddevice             0.5.6
soundfile               0.14.0
spyder-kernels          3.1.5
stack-data              0.6.3
statsmodels             0.14.6
tenacity                9.1.4
tornado                 6.5.7
tqdm                    4.70.0
traitlets               5.16.1
truststore              0.10.4
typing_extensions       4.16.0
typing-inspection       0.4.2
tzdata                  2026.3
urllib3                 2.7.0
wcwidth                 0.8.2
websocket-client        1.9.2
websockets              16.1.1
wurlitzer               3.1.1
xarray                  2026.7.0

'''



# %%


'''
    # Run script in (ai-apis) virtual environment
<<< bash
cd ~/spyder-6/envs &&
source ./ai-apis/bin/activate
(ai-apis) python3 ~/Desktop/Anthropic_speech-to-text_translation-transcription.py

(ai-apis) deactivate
>>>bash


'''


# %%

"""
Real-time English speech -> English text -> Spanish text.

Pipeline
  1. Microphone capture (sounddevice, 16 kHz mono)
  2. Energy-based voice-activity detection chops the stream into utterances
  3. Each utterance -> OpenAI  gpt-4o-transcribe        (English text)
  4. English text   -> OpenAI  gpt-4.1-mini             (Spanish text)
  5. Both texts appended to a file on the Desktop; Spanish also printed.

Stop with Ctrl+C.
"""

# %%


import io
import os
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from openai import OpenAI
from anthropic import Anthropic

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
VAD_MARGIN       = 3.0         # speech when RMS > noise_floor * VAD_MARGIN
PRE_ROLL_BLOCKS  = 5           # blocks kept before speech onset (~150 ms)

STT_MODEL        = "gpt-4o-transcribe"   # newest speech-to-text model
TRANSLATE_MODEL  = "gpt-4.1-mini"        # fast, cheap, good translations
SOURCE_LANG      = "en"

DESKTOP   = Path("/home/bruce-vdb/Desktop")
OUT_FILE  = DESKTOP / f"live_translation_{datetime.now():%Y%m%d_%H%M%S}.txt"

BLOCK_FRAMES  = int(SAMPLE_RATE * BLOCK_MS / 1000)
SILENCE_BLOCKS = max(1, SILENCE_MS // BLOCK_MS)
MIN_BLOCKS     = max(1, MIN_UTTERANCE_MS // BLOCK_MS)
MAX_BLOCKS     = max(1, MAX_UTTERANCE_MS // BLOCK_MS)


    # API_KEY is saved as an ENV VARIABLE on home compu
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


audio_q: "queue.Queue[np.ndarray]" = queue.Queue()      # mic -> VAD
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
    resp = client.responses.create(
        model=TRANSLATE_MODEL,
        instructions=(
            "You are a professional translator. Translate the user's English "
            "text into natural, fluent Latin-American Spanish. Output ONLY the "
            "Spanish translation: no notes, quotes, or explanations."
        ),
        input=text,
        temperature=0.2,
    )
    return resp.output_text.strip()


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
        except Exception as exc:                       # noqa: BLE001
            print(f"[error] {exc}", file=sys.stderr, flush=True)
        finally:
            work_q.task_done()


# ----------------------------------------------------------------------------
# Microphone callback
# ----------------------------------------------------------------------------
def audio_callback(indata, frames, time_info, status):   # noqa: ANN001
    if status:
        print(f"[audio] {status}", file=sys.stderr)
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

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCK_FRAMES,
        callback=audio_callback,
    )

    print(f"Input device : {sd.query_devices(kind='input')['name']}")
    print(f"Transcript   : {OUT_FILE}")
    print("Calibrating background noise, stay quiet for a second...")

    with stream:
        # --- noise-floor calibration -------------------------------------
        levels, t0 = [], time.time()
        while time.time() - t0 < CALIBRATION_S:
            try:
                levels.append(float(np.sqrt(np.mean(audio_q.get(timeout=1) ** 2))))
            except queue.Empty:
                break
        noise_floor = max(float(np.median(levels)) if levels else 0.0, 1e-4)
        threshold = noise_floor * VAD_MARGIN
        print(f"Noise floor {noise_floor:.5f} -> speech threshold {threshold:.5f}")
        print("Listening. Speak English.  Ctrl+C to stop.\n", flush=True)

        # --- segmentation -------------------------------------------------
        pre_roll: list[np.ndarray] = []
        buffer:   list[np.ndarray] = []
        speaking = False
        silent_blocks = 0

        try:
            while True:
                try:
                    block = audio_q.get(timeout=0.5)
                except queue.Empty:
                    continue

                rms = float(np.sqrt(np.mean(block ** 2)))
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

        except KeyboardInterrupt:
            print("\nStopping...")
            if speaking and len(buffer) >= MIN_BLOCKS:
                work_q.put(np.concatenate(buffer))

    work_q.put(None)
    work_q.join()
    print(f"Done. Transcript saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
# %%
    
