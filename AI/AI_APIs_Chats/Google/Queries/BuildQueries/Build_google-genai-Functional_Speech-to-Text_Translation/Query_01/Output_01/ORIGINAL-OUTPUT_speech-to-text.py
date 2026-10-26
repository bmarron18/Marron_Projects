#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 11:20:22 2025
Updated: 12 Sept 2026
@author: bmarron

"""

# %%


This script must be run in a virtual envirnment (ai-apis). Set Spyder to run in (ai-apis) by
pointing the Python interpreter (found under the Wrench) to:
    /home/bruce-vdb/spyder-6/envs/ai-apis/bin/python3.12

To create the virtual env, ai-apis
    $ cd ~/spyder-6/envs
	$ python3 -m venv ai-apis
	$ source ./ai-apis/bin/activate


the following packages have been installed into (ai-apis):
    (ai-apis)$ pip install --upgrade spyder-kernels google-genai openai pyaudio nest_asyncio
    

# %%


$ pip install --upgrade google-genai

   # as of 11 Sept 2026
google-genai-2.23.0

# %%
'''
To translate live spoken English audio into written Spanish in real time, you will use 
the **Google GenAI Multimodal Live API** over a bidirectional WebSocket.

Since Spyder runs on top of an IPython kernel (which already runs an event loop), this 
script includes `nest_asyncio` to prevent event-loop conflicts.

'''
# %%

### Step 1: Install System & Python Dependencies

Open your terminal on Linux Mint and install the required audio drivers and 
Python packages:

```bash
# Install Linux audio libraries
sudo apt update &&
sudo apt install -y portaudio19-dev python3-pyaudio

# Install Python packages into virtual environment
pip install --upgrade google-genai
pip install --upgrade pyaudio nest_asyncio
```


# %%

### How to Run in Spyder:
1. Make sure your microphone is selected in Linux Mint's **Sound Settings**.
2. Run the file by pressing **F5** in Spyder.
3. Speak English into the microphone. The translated Spanish text will stream character-by-character into both the **Spyder Console** and the file `/home/bruce-vdb/Desktop/translation_output.txt`.
4. Click into the Spyder console and press **Ctrl + C** (or click the red stop button) 
to stop recording.

# %%

'''
CLOSE BUT NO GO! Throws this error after trying to synch:
    
    ⏳ Synchronizing connection with Gemini Live backend...
    [Error in receiving loop]: 1008 None. The operation was aborted.
'''


import asyncio
import os
import sys

from google import genai
import nest_asyncio
import pyaudio

# -----------------------------
# Configuration
# -----------------------------

# Required for Spyder's IPython event loop compatibility
nest_asyncio.apply()

# Secure desktop path discovery cross-platform
DEFAULT_OUTPUT = os.path.join(os.path.expanduser("~"), "Desktop", "translation_output.txt")
OUTPUT_FILE_PATH = os.getenv("TRANSLATION_OUTPUT_PATH", DEFAULT_OUTPUT)

# FIX 1: Use the standard production-level live model identifier
MODEL_ID = "gemini-3.1-flash-live-preview"  

SYSTEM_INSTRUCTION = (
    "You are a real-time speech-to-text translator. Listen to the incoming spoken "
    "English audio and immediately translate it into natural Spanish text. "
    "Only output the Spanish translation text. "
    "Do not add conversational replies, explanations, or timestamps."
)

# Verify API credentials early
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
    sys.exit(1)

# FIX 2: Initialize standard Client without manual api_version overrides to fix 404 errors
client = genai.Client(api_key=gemini_api_key)

# Audio Hardware Recording Framework (16kHz, 16-bit Mono PCM)
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_SIZE = 1024

p = pyaudio.PyAudio()
stream = p.open(
    format=AUDIO_FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK_SIZE,
)

# FIX 3: Flat dictionary definition with standard "AUDIO" modality strings
config = {
    "response_modalities": ["AUDIO"],
    "system_instruction": {
        "parts": [{"text": SYSTEM_INSTRUCTION}]
    }
}


async def audio_stream_loop(session, stream, stop_event, setup_complete_event):
    """Reads audio frames from microphone buffer and pushes payload to Gemini Live socket."""
    print("⏳ Synchronizing connection with Gemini Live backend...")
    await setup_complete_event.wait()
    
    print("🎤 Microphone is live. Start speaking in English...")
    try:
        while not stop_event.is_set():
            data = await asyncio.to_thread(
                stream.read, CHUNK_SIZE, exception_on_overflow=False
            )
            if not data:
                continue

            # Stream real-time little-endian audio buffers securely 
            await session.send(
                input={"data": data, "mime_type": f"audio/pcm;rate={RATE}"}
            )
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[Error in audio send loop]: {e}", file=sys.stderr)


async def receive_translation(session, file_handle, stop_event, setup_complete_event):
    """Validates socket handshake and logs the text components of the model response."""
    try:
        async for response in session.receive():
            # Intercept setup confirmation handshake frame from server
            if hasattr(response, "setup_complete") and response.setup_complete:
                print("✅ Handshake complete. Connection established.")
                setup_complete_event.set()
                continue

            server_content = response.server_content
            if not server_content:
                continue

            # Intercept text chunks generated inline within model_turn bounds
            if server_content.model_turn and server_content.model_turn.parts:
                for part in server_content.model_turn.parts:
                    if part.text:
                        # Stream the Spanish translation text instantly to the monitor
                        print(part.text, end="", flush=True)
                        
                        # Append content incrementally into the file
                        file_handle.write(part.text)
                        file_handle.flush()

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[Error in receiving loop]: {e}", file=sys.stderr)


async def main():
    stop_event = asyncio.Event()
    setup_complete_event = asyncio.Event()

    print("=" * 60)
    print(" Gemini Live English-to-Spanish Audio Translation")
    print(f" Output target: {OUTPUT_FILE_PATH}")
    print(" Press Ctrl+C in the Spyder console to terminate.")
    print("=" * 60 + "\n")

    try:
        with open(OUTPUT_FILE_PATH, "a", encoding="utf-8") as file_handle:
            file_handle.write("\n--- New Translation Session Started ---\n")
            file_handle.flush()

            # Open live session cleanly
            async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
                send_task = asyncio.create_task(
                    audio_stream_loop(session, stream, stop_event, setup_complete_event)
                )
                receive_task = asyncio.create_task(
                    receive_translation(session, file_handle, stop_event, setup_complete_event)
                )

                await asyncio.gather(send_task, receive_task)

    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n\nStopping translation session...")
    finally:
        stop_event.set()
        try:
            if stream.is_active():
                stream.stop_stream()
            stream.close()
        except Exception:
            pass
        finally:
            p.terminate()
        print("Audio hardware released and resources stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")

# %%


















