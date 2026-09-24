#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 11:20:22 2025
Updated: 11 Sept 2026
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

    (ai-apis)$ pip install spyder-kernels google-genai openai
    (ai-apis)$ pip install pandas NumPy python-dateutil pytz tzdata
    (ai-apis)$ pip install "pandas[performance]"
    (ai-apis)$ pip install "pandas[computation]"
    (ai-apis)$ pip install plotnine
    (ai-apis):~$ deactivate

"pandas[performance]" contains:
    numexpr
    bottleneck
    numba
    
"pandas[computation]" contains:
    SciPy
    xarray


Successfully installed NumPy-2.5.1 pandas-3.0.5 pytz-2026.3.post1 tzdata-2026.3
Successfully installed bottleneck-1.6.0 llvmlite-0.48.0 numba-0.66.0 numexpr-2.14.2 numpy-2.4.6

Successfully installed scipy-1.18.0 xarray-2026.7.0
Successfully installed contourpy-1.3.3 cycler-0.12.1 fonttools-4.63.0
kiwisolver-1.5.0 matplotlib-3.11.1 mizani-0.14.4 patsy-1.0.2 pillow-12.3.0 
plotnine-0.15.7 pyparsing-3.3.2 statsmodels-0.14.6



# %%

'''

To bridge the Google GenAI SDK with your computer's local physical audio 
hardware, you can use PyAudio.The script below captures live microphone 
speech, chunks it into standard 16kHz 16-bit Mono PCM audio (the native 
stream format required by Gemini's multimodal layer), sends it up to the 
gemini-2.0-flash-exp (or gemini-2.5-flash variants) live websocket, 
receives the raw real-time Spanish audio reply, and passes it out 
directly through your computer speakers.

You must have the PortAudio system library installed before installing 
PyAudio

'''

# %%
'''
Install PortAudio
'''

$ sudo apt-get install portaudio19-dev python3-pyaudio


'''
Install PyAudio into virtual env along with google-genai SDK
'''

$ pip install google-genai pyaudio

# %%

'''
Complete Code: Audio I/O 
'''


import asyncio
import os
import sys
import pyaudio
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Audio Configurations (Native Gemini Live Spec: 16kHz, 16-bit, Mono PCM)
# ---------------------------------------------------------------------------
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_SIZE = 1024

# System Instructions directing the model to act as a strict audio translator
SYSTEM_INSTRUCTION = (
    "You are a live, real-time audio translator. Every sound, word, or phrase "
    "you hear in English must be instantly translated and spoken out loud in Spanish. "
    "Do not engage in conversation, do not add commentary, and do not say things like 'Here is your translation'. "
    "Only respond with the natural Spanish translation of what you hear."
)

async def send_mic_audio(session, p_audio):
    """Continuously captures audio from the microphone and streams it to Gemini."""
    mic_stream = p_audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    print("\n🎤 Microphone active. Start speaking in English...")
    
    try:
        while True:
            # Read raw PCM bytes from the mic buffer (non-blocking simulation in async loop)
            # Using exception_on_overflow=False prevents crashes on slow buffer reads
            data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
            
            # Send the raw PCM blob directly down the active live WebSocket session
            await session.send(
                input={"data": data, "mime_type": f"audio/pcm;rate={RATE}"}
            )
            # Yield control back to the async loop briefly
            await asyncio.sleep(0.001)
            
    except asyncio.CancelledError:
        pass
    finally:
        mic_stream.stop_stream()
        mic_stream.close()

async def receive_speaker_audio(session, p_audio):
    """Continuously listens for translated Spanish audio packets from Gemini and plays them."""
    speaker_stream = p_audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    try:
        # Asynchronously iterate through messages streaming back over the WebSocket
        async for response in session.receive():
            server_content = response.server_content
            
            if server_content is None:
                continue
                
            model_turn = server_content.model_turn
            if model_turn:
                for part in model_turn.parts:
                    # Check if the part contains raw executable audio data
                    if part.inline_data and part.inline_data.data:
                        audio_bytes = part.inline_data.data
                        # Write raw audio frames instantly out to physical speakers
                        speaker_stream.write(audio_bytes)
                        
            # If the model detects the user interrupted or stop signal
            if server_content.turn_complete:
                pass
                
    except asyncio.CancelledError:
        pass
    finally:
        speaker_stream.stop_stream()
        speaker_stream.close()

async def main():
    # Verify API key is local
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not detected.", file=sys.stderr)
        return

    # Initialize Google GenAI client
    client = genai.Client()
    
    # Target standard low-latency multimodal live models
    model_id = "gemini-2.0-flash-exp" 
    
    # Configure the live connection properties
    config = types.LiveConnectConfig(
        response_modalities=[types.LiveModality.AUDIO], # We want native voice backend output
        system_instruction=types.Content(
            parts=[types.Part.from_text(SYSTEM_INSTRUCTION)]
        ),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                # Select preferred native sounding voice profile (Aoede, Charon, Fenrir, Kore, Puck)
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        )
    )

    # Initialize the PyAudio hardware link
    p_audio = pyaudio.PyAudio()

    print("=" * 60)
    print("   GEMINI LIVE API: HARDWARE MIC-TO-SPEAKER TRANSLATOR    ")
    print("=" * 60)
    print("Connecting to Gemini Live WebSocket platform...")

    # Establish the bidirectional WebSocket stream context
    async with client.aio.live.connect(model=model_id, config=config) as session:
        print("Connected! Connection session open successfully.")
        
        # Concurrently schedule the microphone reading loop and the speaker playing loop
        mic_task = asyncio.create_task(send_mic_audio(session, p_audio))
        speaker_task = asyncio.create_task(receive_speaker_audio(session, p_audio))
        
        try:
            await asyncio.gather(mic_task, speaker_task)
        except KeyboardInterrupt:
            print("\nShutting down session gracefully...")
        finally:
            mic_task.cancel()
            speaker_task.cancel()
            await asyncio.gather(mic_task, speaker_task, return_exceptions=True)

    # Clean up the audio objects
    p_audio.terminate()
    print("Hardware wrapper destroyed. Session closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
        
# %%

'''
Complete Code: Audio + Text
'''

import asyncio
import os
import sys
import pyaudio
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Audio Configurations (Native Gemini Live Spec: 16kHz, 16-bit, Mono PCM)
# ---------------------------------------------------------------------------
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_SIZE = 1024

SYSTEM_INSTRUCTION = (
    "You are a live, real-time audio translator. Every sound, word, or phrase "
    "you hear in English must be instantly translated and spoken out loud in Spanish. "
    "Do not engage in conversation, do not add commentary. Only respond with the "
    "natural Spanish translation of what you hear."
)

async def send_mic_audio(session, p_audio):
    """Continuously captures audio from the microphone and streams it to Gemini."""
    mic_stream = p_audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    print("\n🎤 Microphone active. Speak in English anytime...")
    
    try:
        while True:
            data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
            await session.send(
                input={"data": data, "mime_type": f"audio/pcm;rate={RATE}"}
            )
            await asyncio.sleep(0.001)
    except asyncio.CancelledError:
        pass
    finally:
        mic_stream.stop_stream()
        mic_stream.close()

async def receive_speaker_and_text(session, p_audio):
    """Receives translation packets and outputs Spanish audio and text simultaneously."""
    speaker_stream = p_audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    # Simple state tracking to format terminal output cleanly
    is_printing_text = False
    
    try:
        async for response in session.receive():
            server_content = response.server_content
            if server_content is None:
                continue
                
            model_turn = server_content.model_turn
            if model_turn:
                for part in model_turn.parts:
                    # --- Handle Live Text Translation Stream ---
                    if part.text:
                        if not is_printing_text:
                            # Start a new block for the translation response
                            print("\n🇪🇸 Spanish: ", end="", flush=True)
                            is_printing_text = True
                        print(part.text, end="", flush=True)
                        
                    # --- Handle Live Audio Stream ---
                    if part.inline_data and part.inline_data.data:
                        audio_bytes = part.inline_data.data
                        speaker_stream.write(audio_bytes)
                        
            # When Gemini is finished speaking/typing this thought turn
            if server_content.turn_complete:
                if is_printing_text:
                    print() # Print newline
                    is_printing_text = False
                
    except asyncio.CancelledError:
        pass
    finally:
        speaker_stream.stop_stream()
        speaker_stream.close()

async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not found.", file=sys.stderr)
        return

    client = genai.Client()
    model_id = "gemini-2.0-flash-exp" 
    
    config = types.LiveConnectConfig(
        # CRITICAL: Ask for both TEXT token delivery and AUDIO rendering modalities
        response_modalities=[types.LiveModality.TEXT, types.LiveModality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(SYSTEM_INSTRUCTION)]
        ),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        )
    )

    p_audio = pyaudio.PyAudio()

    print("=" * 60)
    print("      GEMINI LIVE API: AUDIO & TEXT STREAM TRANSLATOR       ")
    print("=" * 60)
    print("Connecting to Gemini Live WebSocket platform...")

    async with client.aio.live.connect(model=model_id, config=config) as session:
        print("Connected!")
        
        mic_task = asyncio.create_task(send_mic_audio(session, p_audio))
        receive_task = asyncio.create_task(receive_speaker_and_text(session, p_audio))
        
        try:
            await asyncio.gather(mic_task, receive_task)
        except KeyboardInterrupt:
            print("\nShutting down session...")
        finally:
            mic_task.cancel()
            receive_task.cancel()
            await asyncio.gather(mic_task, receive_task, return_exceptions=True)

    p_audio.terminate()
    print("\nSession cleanly terminated.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)

# %%

'''
If you want to customize this further, let me know:
    Would you like to add a visual toggle (like a keystroke) to switch translation 
    directions from Spanish-to-English on the fly?
    
    Do you want to configure the session to save a localized markdown transcript log 
    of the translations to your hard drive?

'''


