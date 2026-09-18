#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 09:32:08 2026

@author: bruce-vdb, Claude Sonnet 5
"""


from __future__ import annotations

import asyncio
import os
import queue
import signal
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import sounddevice as sd
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
IN_RATE       = 16_000          # Hz sent to the model (Live API input contract)
OUT_RATE      = 24_000          # Hz returned by the Live API (PCM16 mono)
CHANNELS      = 1
CHUNK_MS      = 100             # mic chunk size streamed upstream
MIC_QUEUE_MAX = 40              # ~4 s of backlog per session, then drop oldest
IDLE_FLUSH_S  = 1.5             # flush a transcript line after this much silence

MODE            = os.getenv("MODE", "dual").strip().lower()
TARGET_LANG     = os.getenv("TARGET_LANG", "es-US")
SOURCE_LANG     = os.getenv("SOURCE_LANG", "en-US")
TRANSLATE_MODEL = os.getenv("TRANSLATE_MODEL", "gemini-3.5-live-translate-preview")
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "gemini-3.5-transcribe-live")
API_VERSION     = os.getenv("GENAI_API_VERSION", "v1beta")
AUDIO_INPUT_DEVICE    = os.getenv("AUDIO_INPUT_DEVICE")
PLAY_TRANSLATED_AUDIO = os.getenv("PLAY_TRANSLATED_AUDIO", "0") == "1"

TRANSCRIPT_DIR = Path(os.getenv("TRANSCRIPT_DIR", str(Path.home() / "Desktop")))
OUT_FILE = TRANSCRIPT_DIR / f"live_translation_{datetime.now():%Y%m%d_%H%M%S}.txt"

CHUNK_FRAMES = int(IN_RATE * CHUNK_MS / 1000)


def log_note(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Defensive SDK feature detection
#
# The Live API surface is still in preview and field names move between
# google-genai releases.  Instead of crashing at import time (script 01's
# TranslationConfig bug), we probe for each type/field and silently drop what
# the installed SDK does not understand.
# ---------------------------------------------------------------------------
def _T(name: str):
    return getattr(types, name, None)


def _make(name: str, **kwargs):
    """Instantiate types.<name>(**kwargs), dropping unsupported kwargs."""
    cls = _T(name)
    if cls is None:
        return None
    kw = dict(kwargs)
    while True:
        try:
            return cls(**kw)
        except Exception as exc:  # pydantic ValidationError / TypeError
            bad = _offending_key(exc, kw)
            if bad is None:
                return None
            kw.pop(bad)


def _offending_key(exc: Exception, kwargs: dict) -> str | None:
    text = str(exc)
    for key in list(kwargs):
        if key in text:
            return key
    return None


def build_live_config(**kwargs) -> types.LiveConnectConfig:
    """LiveConnectConfig that tolerates unknown/unsupported keys."""
    kw = {k: v for k, v in kwargs.items() if v is not None}
    while True:
        try:
            return types.LiveConnectConfig(**kw)
        except Exception as exc:
            bad = _offending_key(exc, kw)
            if bad is None:
                raise
            log_note(f"[config] this google-genai build rejects '{bad}' -> dropped")
            kw.pop(bad)


# ---------------------------------------------------------------------------
# Transcript log: incremental console streaming + timestamped file lines
# ---------------------------------------------------------------------------
class TranscriptLog:
    """
    Fixes script 01's 'flush only on turn_complete' stall: text is echoed to the
    console as it arrives and a line is committed to disk on turn/generation
    complete OR after IDLE_FLUSH_S of silence for that language.
    """

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self._buf: dict[str, str] = {}
        self._touched: dict[str, float] = {}
        self._last_tag: str | None = None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"Live EN -> ES session  mode={MODE}  started {datetime.now():%Y-%m-%d %H:%M:%S}\n\n",
            encoding="utf-8",
        )

    def feed(self, tag: str, text: str) -> None:
        if not text:
            return
        with self._lock:
            if self._last_tag != tag:
                sys.stdout.write(f"\n{tag}  ")
                self._last_tag = tag
            sys.stdout.write(text)
            sys.stdout.flush()
            self._buf[tag] = self._buf.get(tag, "") + text
            self._touched[tag] = time.monotonic()

    def flush(self, tags: Iterable[str] | None = None) -> None:
        with self._lock:
            for tag in list(tags or self._buf.keys()):
                line = self._buf.pop(tag, "").strip()
                self._touched.pop(tag, None)
                if not line:
                    continue
                stamp = datetime.now().strftime("%H:%M:%S")
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(f"[{stamp}] {tag}: {line}\n")
            self._last_tag = None

    def flush_idle(self) -> None:
        now = time.monotonic()
        with self._lock:
            stale = [t for t, ts in self._touched.items() if now - ts >= IDLE_FLUSH_S]
        if stale:
            self.flush(stale)


async def idle_flusher(log: TranscriptLog, stop: asyncio.Event) -> None:
    while not stop.is_set():
        await asyncio.sleep(0.4)
        log.flush_idle()


# ---------------------------------------------------------------------------
# Microphone: one capture stream, fanned out to N bounded asyncio queues
# ---------------------------------------------------------------------------
class MicBroadcaster:
    def __init__(self, device, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._subs: list[asyncio.Queue[bytes]] = []
        self._dropped = 0
        self.rate, self._resample = self._negotiate_rate(device)
        blocksize = int(self.rate * CHUNK_MS / 1000)
        self.stream = sd.InputStream(
            samplerate=self.rate,
            channels=CHANNELS,
            dtype="int16",
            blocksize=blocksize,
            device=device,
            callback=self._callback,
        )

    @staticmethod
    def _negotiate_rate(device) -> tuple[int, bool]:
        """Prefer 16 kHz; fall back to the device default + linear resampling."""
        try:
            sd.check_input_settings(device=device, channels=CHANNELS,
                                    dtype="int16", samplerate=IN_RATE)
            return IN_RATE, False
        except Exception:
            info = sd.query_devices(device, kind="input") if device is not None \
                else sd.query_devices(kind="input")
            native = int(info["default_samplerate"])
            log_note(f"[audio] device refuses {IN_RATE} Hz; capturing at {native} Hz "
                     f"and resampling to {IN_RATE} Hz")
            return native, True

    def subscribe(self) -> asyncio.Queue[bytes]:
        q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=MIC_QUEUE_MAX)
        self._subs.append(q)
        return q

    def _callback(self, indata, frames, time_info, status):  # noqa: ANN001
        if status:
            print(f"[audio] {status}", file=sys.stderr, flush=True)
        mono = indata[:, 0]
        if self._resample:
            n_out = max(1, int(round(len(mono) * IN_RATE / self.rate)))
            src = np.linspace(0.0, 1.0, num=len(mono), endpoint=False)
            dst = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
            mono = np.interp(dst, src, mono.astype(np.float32)).astype(np.int16)
        payload = mono.copy().tobytes()
        self._loop.call_soon_threadsafe(self._fanout, payload)

    def _fanout(self, payload: bytes) -> None:
        for q in self._subs:
            if q.full():                      # bounded: drop oldest, keep latency low
                try:
                    q.get_nowait()
                    self._dropped += 1
                except asyncio.QueueEmpty:
                    pass
            q.put_nowait(payload)

    def __enter__(self):
        self.stream.start()
        return self

    def __exit__(self, *exc):
        try:
            self.stream.stop()
            self.stream.close()
        finally:
            if self._dropped:
                log_note(f"[audio] dropped {self._dropped} chunks under backpressure")


# ---------------------------------------------------------------------------
# Speaker playback on a worker thread (script 01 blocked the event loop here)
# ---------------------------------------------------------------------------
class Speaker:
    def __init__(self, rate: int = OUT_RATE):
        self.rate = rate
        self._q: queue.Queue[bytes | None] = queue.Queue(maxsize=200)
        self._thread = threading.Thread(target=self._run, name="speaker", daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._q.put(None)
        self._thread.join(timeout=3)

    def _run(self) -> None:
        try:
            with sd.RawOutputStream(samplerate=self.rate, channels=1, dtype="int16") as out:
                while True:
                    item = self._q.get()
                    if item is None:
                        break
                    out.write(item)
        except Exception:
            print("[speaker] playback thread failed:", file=sys.stderr)
            traceback.print_exc()

    def play(self, pcm: bytes) -> None:
        try:
            self._q.put_nowait(pcm)
        except queue.Full:
            pass  # prefer dropping audio over growing latency

    def reset(self) -> None:
        """Called on 'interrupted' so stale audio is not played over new speech."""
        while True:
            try:
                self._q.get_nowait()
            except queue.Empty:
                return


# ---------------------------------------------------------------------------
# Session configs
# ---------------------------------------------------------------------------
def _resumption(handle: str | None):
    return _make("SessionResumptionConfig", handle=handle)


def _compression():
    sliding = _make("SlidingWindow")
    return _make("ContextWindowCompressionConfig", sliding_window=sliding)


def _vad():
    aad = _make(
        "AutomaticActivityDetection",
        disabled=False,
        prefix_padding_ms=200,
        silence_duration_ms=700,
    )
    return _make("RealtimeInputConfig", automatic_activity_detection=aad)


def translate_config(handle: str | None, want_en_text: bool) -> types.LiveConnectConfig:
    """
    Speech-to-speech EN -> ES.  response_modalities MUST be AUDIO for this model;
    the EN/ES *text* comes exclusively from the two transcription configs.
    """
    tx = _make("AudioTranscriptionConfig")
    translation = _make("TranslationConfig",
                        target_language_code=TARGET_LANG,
                        source_language_code=SOURCE_LANG,
                        echo_target_language=False)

    kw = dict(
        response_modalities=["AUDIO"],
        output_audio_transcription=tx,
        input_audio_transcription=(_make("AudioTranscriptionConfig") if want_en_text else None),
        realtime_input_config=_vad(),
        context_window_compression=_compression(),
        session_resumption=_resumption(handle),
        translation_config=translation,
    )

    if translation is None:
        # Fallback for SDKs / models without a dedicated translation_config:
        # steer with speech language + a system instruction instead.
        log_note("[config] TranslationConfig unavailable -> using speech_config + "
                 "system_instruction fallback")
        kw["speech_config"] = _make("SpeechConfig", language_code=TARGET_LANG)
        kw["system_instruction"] = types.Content(
            role="user",
            parts=[types.Part(text=(
                "You are a simultaneous interpreter. Render every English "
                "utterance you hear into natural spoken Spanish immediately. "
                "Never answer, comment, or add anything of your own."
            ))],
        )
    return build_live_config(**kw)


def transcribe_config(handle: str | None) -> types.LiveConnectConfig:
    """Transcription-only English session (no translation)."""
    return build_live_config(
        response_modalities=["TEXT"],
        input_audio_transcription=_make("AudioTranscriptionConfig"),
        realtime_input_config=_vad(),
        context_window_compression=_compression(),
        session_resumption=_resumption(handle),
    )


# ---------------------------------------------------------------------------
# Session worker: send/receive + auto-reconnect with session resumption
# ---------------------------------------------------------------------------
class SessionWorker:
    def __init__(
        self,
        name: str,
        model: str,
        config_builder: Callable[[str | None], types.LiveConnectConfig],
        client: genai.Client,
        mic: MicBroadcaster,
        log: TranscriptLog,
        stop: asyncio.Event,
        speaker: Speaker | None,
        en_from_input: bool,
        es_from_output: bool,
        text_tag: str,
    ):
        self.name = name
        self.model = model
        self.config_builder = config_builder
        self.client = client
        self.q = mic.subscribe()
        self.log = log
        self.stop = stop
        self.speaker = speaker
        self.en_from_input = en_from_input
        self.es_from_output = es_from_output
        self.text_t

