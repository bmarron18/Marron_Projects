#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 17:09:27 2026

@author: bruce-vdb
"""

# %%

'''
    # Run script in virtual env
$ cd ~/spyder-6/envs
$ source ./ai-apis/bin/activate &&
$(ai-apis):$ python3 ~/Desktop/SCRIPT_Google_02.py
$(ai-apis):~$ deactivate

cd ~/spyder-6/envs &&
source ./ai-apis/bin/activate &&
python3 ~/Desktop/SCRIPT_Google_02.py

'''

# %%

import asyncio
import pyaudio
import nest_asyncio

# Required for Spyder's IPython event loop compatibility
nest_asyncio.apply()

from google import genai
from google.genai import types
import os
import sys

# -----------------------------
# Configuration
# -----------------------------
OUTPUT_FILE_PATH = "/home/bruce-vdb/Desktop/translation_output.txt"

    # Initialize the Gemini Client with API Key
    # API_KEY is saved as an ENV VARIABLE on home compu
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)


    # Initialize PyAudio and configure your hardware input stream
    # Audio Recording Settings (16kHz 16-bit Mono PCM is standard for Live API)
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,          # Gemini works great with 16kHz
    input=True,
    frames_per_buffer=1024
)


    # Live API Model
MODEL_ID = "gemini-3.5-transcribe-live"  # Currently supports real-time Live streaming

SYSTEM_INSTRUCTION = (
    "You are a real-time speech translator. Listen carefully to the incoming spoken English audio \
    and immediately translate it into natural Spanish text. Only output the Spanish translation text. \
    Do not add explanations, conversational responses, or timestamps."
)


async def audio_stream_loop(session):
    print("🎤 Microphone is live. Start speaking...")
    try:
        while True:
            # Read raw PCM data from the initialized stream
            # exception_on_overflow=False prevents crashes if your loop lags slightly
            data = stream.read(1024, exception_on_overflow=False)
            
            # Forward the audio binary chunk to Gemini
            await session.send_realtime_input(
                audio=types.Blob(
                    data=data, 
                    mime_type="audio/pcm;rate=16000"
                )
            )
            # Yield control briefly to let the event loop process receiving data
            await asyncio.sleep(0.001)
            
    except asyncio.CancelledError:
        print("Stopping microphone stream...")
    finally:
        # Clean up stream assets when done
        stream.stop_stream()
        stream.close()
        p.terminate()


async def receive_translation(session, file_handle, stop_event):
    """Receives real-time translated text from Gemini and prints/saves it."""
    try:
        async for response in session.receive():
            server_content = response.server_content


           # Look specifically for the transcription payload
            if server_content and server_content.input_transcription:
               transcript_text = server_content.input_transcription.text        

               file_handle.write(transcript_text + "\n")
               file_handle.flush()
               print("Transcript:", transcript_text)

                          
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[Error in receiving]: {e}", file=sys.stderr)


async def main():

    # Configure the live session
    config = types.LiveConnectConfig(
        response_modalities=["TEXT"],
        system_instruction=types.Content(
            parts=[types.Part(text=SYSTEM_INSTRUCTION)]
        ),
    )

    stop_event = asyncio.Event()

    print("=" * 60)
    print(" Gemini Live English-to-Spanish Audio Translation Active")
    print(f" Saving to: {OUTPUT_FILE_PATH}")
    print(" Speak in English. Press Ctrl+C in console to stop.")
    print("=" * 60 + "\n")
    
    with open(OUTPUT_FILE_PATH, "a", encoding="utf-8") as file_handle:
        file_handle.write("\n--- New Translation Session Started ---\n")
        file_handle.flush()

        

        async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
            # Create concurrent background tasks for streaming up and receiving down
            send_task = asyncio.create_task(audio_stream_loop(session))
            receive_task = asyncio.create_task(
                receive_translation(session, file_handle, stop_event)
            )

            try:
                # Keep running until interrupted
                await asyncio.gather(send_task, receive_task)
            except (KeyboardInterrupt, asyncio.CancelledError):
                print("\n\nStopping session...")
            finally:
                stop_event.set()
                send_task.cancel()
                receive_task.cancel()

    # Cleanup audio hardware
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Session stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")

