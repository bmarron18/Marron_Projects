#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Live EN -> ES speech translation / transcription via the Gemini Live API.

v1.7 — bug-fix release over v1.6/v1.5b.

Fixed in this revision
----------------------
1.  FATAL: `asyncio.create_task(asyncio.gather(...))` raised
        TypeError: a coroutine was expected, got <_GatheringFuture pending>
    gather() returns a Future, not a coroutine.  Replaced with a real
    coroutine wrapper; asyncio.wait() now only ever receives Tasks.
2.  Mic queues are now subscribed BEFORE the capture stream starts, so no
    leading audio is fanned out to zero subscribers.
3.  Added a config-degradation ladder: if the server rejects an optional
    config field (temperature / systemInstruction / speechConfig / ...),
    that field is dropped and the SAME model is retried, instead of
    falling into an endless reconnect-with-backoff loop or rotating off a
    working model.
4.  Field-rejection errors are no longer misclassified as model errors.
5.  Model discovery filters out non-bidi "live-looking" ids
    (lyria-realtime-exp, robotics streaming, gemini-3.5-transcribe, ...).
6.  Each session worker flushes only its own transcript tags.
7.  Speaker shutdown can no longer lose its stop sentinel.
8.  Mic-level monitor warns while running if the input stays silent.
9.  --check now also probes the real session configs.

@author: bruce-vdb, Claude Opus 5
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import os
import queue
import signal
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Sequence

try:
    import numpy as np
    import sounddevice as sd
except Exception as exc:                                     # pragma: no cover
    print(f"FATAL: audio stack unavailable ({exc}).\n"
          "       pip install sounddevice numpy   (and: sudo apt install libportaudio2)",
          file=sys.stderr)
    raise SystemExit(3)

try:
    from google import genai
    from google.genai import types
except Exception as exc:                                     # pragma: no cover
    print(f"FATAL: google-genai not importable ({exc}).\n"
          "       pip install -U google-genai", file=sys.stderr)
    raise SystemExit(3)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
IN_RATE       = 16_000      # Hz required by the Live API input contract
OUT_RATE      = 24_000      # Hz returned by the Live API (PCM16 mono)
CHANNELS      = 1
CHUNK_MS      = 100         # mic chunk streamed upstream
MIC_QUEUE_MAX = 40          # ~4 s backlog per session, then drop oldest
IDLE_FLUSH_S  = 1.5         # commit a transcript line after this much silence
SILENCE_PEAK  = 200         # below this peak amplitude we consider input silent

TARGET_LANG = os.getenv("TARGET_LANG", "es-US")
SOURCE_LANG = os.getenv("SOURCE_LANG", "en-US")

# API versions to try, in order.  The Live endpoint for the 3.x models is
# served on v1beta for this key; v1alpha is kept as an automatic fallback.
API_VERSIONS = [v.strip() for v in
                os.getenv("GENAI_API_VERSION", "v1beta,v1alpha").split(",")
                if v.strip()]

# -- Models -----------------------------------------------------------------
# Confirmed reachable by --check on this key:
#   gemini-3.5-live-translate-preview  (AUDIO out, speech->speech translation)
#   gemini-3.5-transcribe-live         (TEXT  out, live transcription)
# Override with TRANSLATE_MODEL / TRANSCRIBE_MODEL (comma-separated allowed).
TRANSLATE_MODELS = [
    m.strip() for m in os.getenv(
        "TRANSLATE_MODEL",
        "gemini-3.5-live-translate-preview,"      # purpose-built speech translation
        "gemini-3.8-live,"
        "gemini-3.1-flash-live-preview,"
        "gemini-2.5-flash-native-audio-latest",
    ).split(",") if m.strip()
]
TRANSCRIBE_MODELS = [
    m.strip() for m in os.getenv(
        "TRANSCRIBE_MODEL",
        "gemini-3.5-transcribe-live,"             # purpose-built live transcription
        "gemini-3.1-flash-live-preview,"
        "gemini-3.8-live,"
        "gemini-2.5-flash-native-audio-latest",
    ).split(",") if m.strip()
]

# Models that advertise streaming/"live"-ish names but are NOT usable as
# bidiGenerateContent speech sessions.  Never auto-added as fallbacks.
DISCOVERY_DENY = (
    "lyria",            # music generation
    "robotics",         # robotics embodied reasoning streaming
    "imagen", "veo", "embedding", "tts",
)

INTERPRETER_PROMPT = (
    "You are a simultaneous interpreter. Render every English utterance you "
    "hear into natural, spoken Latin-American Spanish, immediately and "
    "completely. Do not answer questions, do not comment, do not add, omit or "
    "summarise anything, and never speak English. Output only the Spanish "
    "interpretation of what the speaker said."
)
SILENT_PROMPT = (
    "You are a silent transcription endpoint. Never produce any output of any "
    "kind. Do not reply, acknowledge, or comment."
)

CHUNK_FRAMES = int(IN_RATE * CHUNK_MS / 1000)


def log_note(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Defensive SDK feature detection
# ---------------------------------------------------------------------------
def _T(name: str):
    return getattr(types, name, None)


def _make(name: str, **kwargs):
    """types.<name>(**kwargs), silently dropping kwargs this SDK rejects."""
    cls = _T(name)
    if cls is None:
        return None
    kw = dict(kwargs)
    while True:
        try:
            return cls(**kw)
        except Exception as exc:                 # pydantic ValidationError / TypeError
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
# Client pool: one client per API version, created on demand
# ---------------------------------------------------------------------------
class ClientPool:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._cache: dict[str, genai.Client] = {}

    def get(self, api_version: str) -> genai.Client:
        if api_version not in self._cache:
            self._cache[api_version] = genai.Client(
                api_key=self.api_key,
                http_options={"api_version": api_version},
            )
        return self._cache[api_version]


# ---------------------------------------------------------------------------
# Model discovery
# ---------------------------------------------------------------------------
def _denied(name: str) -> bool:
    low = name.lower()
    return any(bad in low for bad in DISCOVERY_DENY)


def _looks_live(name: str) -> bool:
    """Heuristic for bidi-capable *speech* models when the API omits actions."""
    low = name.lower()
    if _denied(low):
        return False
    if "live" in low:                       # ...-live, live-translate, flash-live
        return True
    if "native-audio" in low:               # native audio dialog models
        return True
    return False


def discover_live_models(client: genai.Client) -> list[str]:
    """Live/bidi-capable model ids visible to this key (best effort)."""
    found: list[str] = []
    try:
        for m in client.models.list():
            name = (getattr(m, "name", "") or "")
            if name.startswith("models/"):
                name = name[len("models/"):]
            if not name or _denied(name):
                continue
            actions = getattr(m, "supported_actions", None) or []
            if actions:
                if any("bidi" in str(a).lower() for a in actions):
                    found.append(name)
                continue
            if _looks_live(name):
                found.append(name)
    except Exception as exc:
        log_note(f"[models] models.list() unavailable "
                 f"({type(exc).__name__}: {exc}); using built-in list only")
    seen, ordered = set(), []
    for n in found:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    return ordered


def order_candidates(preferred: list[str], discovered: list[str],
                     kind: str) -> list[str]:
    """Preferred list first, then any other plausible live model this key sees."""
    priority = ("translate", "live", "native-audio") if kind == "translate" \
        else ("transcribe-live", "transcribe", "live", "native-audio")

    def score(name: str) -> int:
        low = name.lower()
        for i, key in enumerate(priority):
            if key in low:
                return i
        return len(priority)

    extra = [n for n in discovered
             if n not in preferred and _looks_live(n)]
    extra.sort(reverse=True)          # newer version strings first
    extra.sort(key=score)             # stable: purpose-built models first
    return preferred + extra


# ---------------------------------------------------------------------------
# Transcript log: incremental console streaming + timestamped file lines
# ---------------------------------------------------------------------------
class TranscriptLog:
    def __init__(self, path: Path, mode: str):
        self.path = path
        self._lock = threading.Lock()
        self._buf: dict[str, str] = {}
        self._touched: dict[str, float] = {}
        self._last_tag: str | None = None
        self.lines = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"Gemini Live session  mode={mode}  "
            f"{SOURCE_LANG} -> {TARGET_LANG}  "
            f"started {datetime.now():%Y-%m-%d %H:%M:%S}\n\n",
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
            targets = list(tags) if tags is not None else list(self._buf.keys())
            wrote = False
            for tag in targets:
                line = self._buf.pop(tag, "").strip()
                self._touched.pop(tag, None)
                if not line:
                    continue
                stamp = datetime.now().strftime("%H:%M:%S")
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(f"[{stamp}] {tag}: {line}\n")
                self.lines += 1
                wrote = True
            if wrote or self._last_tag in targets:
                self._last_tag = None

    def flush_idle(self) -> None:
        now = time.monotonic()
        with self._lock:
            stale = [t for t, ts in self._touched.items()
                     if now - ts >= IDLE_FLUSH_S]
        if stale:
            self.flush(stale)


async def idle_flusher(log: TranscriptLog, stop: asyncio.Event) -> None:
    try:
        while not stop.is_set():
            await asyncio.sleep(0.4)
            log.flush_idle()
    except asyncio.CancelledError:
        pass


# ---------------------------------------------------------------------------
# Microphone: one capture stream fanned out to N bounded asyncio queues
# ---------------------------------------------------------------------------
def resolve_device(spec: str | None):
    if spec is None or str(spec).strip() == "":
        return None
    spec = str(spec).strip()
    try:
        return int(spec)
    except ValueError:
        return spec


class MicBroadcaster:
    def __init__(self, device, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._subs: list[asyncio.Queue[bytes]] = []
        self._dropped = 0
        self.frames = 0
        self.peak = 0
        self.device = device
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
        """Prefer 16 kHz; otherwise capture native and resample linearly."""
        try:
            sd.check_input_settings(device=device, channels=CHANNELS,
                                    dtype="int16", samplerate=IN_RATE)
            return IN_RATE, False
        except Exception:
            pass
        try:
            info = (sd.query_devices(device, kind="input") if device is not None
                    else sd.query_devices(kind="input"))
            native = int(float(info["default_samplerate"]))
        except Exception as exc:
            log_note(f"[audio] cannot read device default rate "
                     f"({type(exc).__name__}: {exc}); forcing {IN_RATE} Hz")
            return IN_RATE, False
        if native == IN_RATE:
            return IN_RATE, False
        log_note(f"[audio] device refuses {IN_RATE} Hz; capturing at {native} Hz "
                 f"and resampling to {IN_RATE} Hz")
        return native, True

    def subscribe(self) -> asyncio.Queue[bytes]:
        q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=MIC_QUEUE_MAX)
        self._subs.append(q)
        return q

    def _callback(self, indata, frames, time_info, status):      # noqa: ANN001
        if status:
            print(f"\n[audio] {status}", file=sys.stderr, flush=True)
        mono = indata[:, 0]
        self.frames += len(mono)
        if len(mono):
            self.peak = max(self.peak, int(np.abs(mono).max()))
        if self._resample:
            n_out = max(1, int(round(len(mono) * IN_RATE / self.rate)))
            src = np.linspace(0.0, 1.0, num=len(mono), endpoint=False)
            dst = np.linspace(0.0, 1.0, num=n_out, endpoint=False)
            mono = np.interp(dst, src, mono.astype(np.float32)).astype(np.int16)
        payload = mono.copy().tobytes()
        try:
            self._loop.call_soon_threadsafe(self._fanout, payload)
        except RuntimeError:
            pass                                  # loop already closed on shutdown

    def _fanout(self, payload: bytes) -> None:
        for q in self._subs:
            if q.full():                          # bounded: drop oldest, keep latency low
                with contextlib.suppress(asyncio.QueueEmpty):
                    q.get_nowait()
                    self._dropped += 1
            with contextlib.suppress(asyncio.QueueFull):
                q.put_nowait(payload)

    def __enter__(self):
        self.stream.start()
        dev = self.device if self.device is not None else "default"
        log_note(f"[audio] capturing from {dev!r} at {self.rate} Hz, "
                 f"{CHUNK_MS} ms chunks, {len(self._subs)} subscriber(s)")
        return self

    def __exit__(self, *exc):
        with contextlib.suppress(Exception):
            self.stream.stop()
            self.stream.close()
        if self._dropped:
            log_note(f"[audio] dropped {self._dropped} chunks under backpressure")
        secs = self.frames / float(self.rate or IN_RATE)
        log_note(f"[audio] captured {secs:.1f} s, peak amplitude {self.peak}/32767")
        if secs >= 1.0 and self.peak < SILENCE_PEAK:
            log_note("[audio] WARNING: input was essentially silent — wrong device "
                     "or muted mic? Run with --list-devices.")


async def mic_monitor(mic: MicBroadcaster, stop: asyncio.Event) -> None:
    """Warn while running (not only at exit) if nothing is reaching the mic."""
    try:
        warned = False
        deadline = 6.0
        while not stop.is_set():
            await asyncio.sleep(1.0)
            if mic.frames / float(mic.rate or IN_RATE) < deadline:
                continue
            if mic.peak < SILENCE_PEAK:
                log_note("[audio] WARNING: still no signal from the input device "
                         f"after {deadline:.0f} s (peak {mic.peak}). "
                         "Check --device / mute / OS input permissions.")
                warned = True
            elif warned:
                log_note(f"[audio] signal detected (peak {mic.peak}/32767)")
                warned = False
            deadline += 30.0
    except asyncio.CancelledError:
        pass


# ---------------------------------------------------------------------------
# Speaker playback on a worker thread (never block the event loop)
# ---------------------------------------------------------------------------
class Speaker:
    def __init__(self, rate: int = OUT_RATE):
        self.rate = rate
        self._q: queue.Queue[bytes | None] = queue.Queue(maxsize=200)
        self._thread = threading.Thread(target=self._run, name="speaker",
                                        daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        # Drain first: a full queue must not swallow the stop sentinel.
        self.reset()
        with contextlib.suppress(Exception):
            self._q.put(None, timeout=1.0)
        self._thread.join(timeout=3)

    def _run(self) -> None:
        try:
            with sd.RawOutputStream(samplerate=self.rate, channels=1,
                                    dtype="int16") as out:
                while True:
                    item = self._q.get()
                    if item is None:
                        break
                    out.write(item)
        except Exception:
            print("\n[speaker] playback thread failed:", file=sys.stderr)
            traceback.print_exc()

    def play(self, pcm: bytes) -> None:
        with contextlib.suppress(queue.Full):
            self._q.put_nowait(pcm)              # drop audio rather than add latency

    def reset(self) -> None:
        """On 'interrupted', discard stale audio so it is not played over new speech."""
        while True:
            try:
                item = self._q.get_nowait()
            except queue.Empty:
                return
            if item is None:                     # keep a pending shutdown request
                with contextlib.suppress(queue.Full):
                    self._q.put_nowait(None)
                return


# ---------------------------------------------------------------------------
# Session config fragments + degradation ladder
# ---------------------------------------------------------------------------
# Order in which optional fields are surrendered when the *server* rejects
# them.  Everything here is a nice-to-have; the transcription configs and
# response_modalities are never dropped.
DEGRADE_ORDER: tuple[str, ...] = (
    "temperature",
    "context_window_compression",
    "session_resumption",
    "system_instruction",
    "realtime_input_config",
    "speech_config",
)

# snake_case -> what the backend calls it in error messages
_CAMEL = {
    "temperature": "temperature",
    "context_window_compression": "contextwindowcompression",
    "session_resumption": "sessionresumption",
    "system_instruction": "systeminstruction",
    "realtime_input_config": "realtimeinputconfig",
    "speech_config": "speechconfig",
}


def _resumption(handle: str | None):
    return _make("SessionResumptionConfig", handle=handle)


def _compression():
    sliding = _make("SlidingWindow")
    return _make("ContextWindowCompressionConfig", sliding_window=sliding)


def _vad():
    aad = _make("AutomaticActivityDetection",
                disabled=False,
                prefix_padding_ms=200,
                silence_duration_ms=700)
    return _make("RealtimeInputConfig", automatic_activity_detection=aad)


def _instruction(text: str):
    return types.Content(role="user", parts=[types.Part(text=text)])


def _finalize(kw: dict, drop: Sequence[str]) -> types.LiveConnectConfig:
    for key in drop:
        kw.pop(key, None)
    return build_live_config(**kw)


def translate_config(handle: str | None,
                     drop: Sequence[str] = ()) -> types.LiveConnectConfig:
    """
    EN speech -> ES speech (gemini-3.5-live-translate-preview).
    response_modalities must be AUDIO for the live translation models, so the
    EN/ES *text* comes from the two transcription configs:
      input_audio_transcription  -> English (what you said)
      output_audio_transcription -> Spanish (what the model said)
    """
    return _finalize(dict(
        response_modalities=["AUDIO"],
        input_audio_transcription=_make("AudioTranscriptionConfig"),
        output_audio_transcription=_make("AudioTranscriptionConfig"),
        speech_config=_make("SpeechConfig", language_code=TARGET_LANG),
        system_instruction=_instruction(INTERPRETER_PROMPT),
        realtime_input_config=_vad(),
        context_window_compression=_compression(),
        session_resumption=_resumption(handle),
        temperature=0.0,
    ), drop)


def transcribe_config(handle: str | None,
                      drop: Sequence[str] = ()) -> types.LiveConnectConfig:
    """Transcription-only English session (gemini-3.5-transcribe-live)."""
    return _finalize(dict(
        response_modalities=["TEXT"],
        input_audio_transcription=_make("AudioTranscriptionConfig"),
        system_instruction=_instruction(SILENT_PROMPT),
        realtime_input_config=_vad(),
        context_window_compression=_compression(),
        session_resumption=_resumption(handle),
        temperature=0.0,
    ), drop)


# ---------------------------------------------------------------------------
# SDK compatibility shim for sending audio
# ---------------------------------------------------------------------------
async def send_audio(session, pcm: bytes) -> None:
    mime = f"audio/pcm;rate={IN_RATE}"
    if hasattr(session, "send_realtime_input"):
        blob = _make("Blob", data=pcm, mime_type=mime)
        if blob is not None:
            await session.send_realtime_input(audio=blob)
            return
        await session.send_realtime_input(audio={"data": pcm, "mime_type": mime})
        return
    await session.send(input={"data": pcm, "mime_type": mime})    # legacy SDKs


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------
#   APIError: 1008 None. models/<id> is not found for API version v1beta,
#             or is not supported for bidiGenerateContent.
_MODEL_ERRORS = (
    "not found for api version", "is not found", "was not found",
    "not_found", "unsupported model", "bidigeneratecontent",
    "model not supported",
)
_CONFIG_ERRORS = (
    "invalid argument", "invalid_argument", "unknown name", "unknown field",
    "cannot be set", "is not allowed", "unexpected field", "1007",
    "failed_precondition", "invalid json payload",
)
_AUTH_ERRORS = ("api key", "api_key", "unauthenticated", "permission_denied",
                "permission denied", "401", "403", "quota", "resource_exhausted")


def _is_model_error(low: str) -> bool:
    return any(k in low for k in _MODEL_ERRORS)


def _is_config_error(low: str) -> bool:
    return any(k in low for k in _CONFIG_ERRORS)


def _is_auth_error(low: str) -> bool:
    return any(k in low for k in _AUTH_ERRORS)


def _mentioned_field(low: str, remaining: Sequence[str]) -> str | None:
    """Return the first still-enabled optional field named in the error text."""
    squashed = low.replace("_", "").replace(" ", "")
    for key in remaining:
        if key in low or _CAMEL[key] in squashed:
            return key
    return None


# ---------------------------------------------------------------------------
# Session worker: send/receive + auto-reconnect with session resumption
# ---------------------------------------------------------------------------
class SessionWorker:
    def __init__(
        self,
        name: str,
        models: list[str],
        config_builder: Callable[[str | None, Sequence[str]],
                                 types.LiveConnectConfig],
        pool: ClientPool,
        mic: MicBroadcaster,
        log: TranscriptLog,
        stop: asyncio.Event,
        speaker: Speaker | None,
        input_tag: str | None,
        output_tag: str | None,
        api_versions: list[str] | None = None,
    ):
        self.name = name
        versions = list(api_versions or API_VERSIONS) or ["v1beta"]
        # candidate = (model, api_version); model-major ordering
        self.candidates = [(m, v) for m in models for v in versions]
        self._ci = 0
        self.config_builder = config_builder
        self.pool = pool
        self.q = mic.subscribe()                 # subscribe before stream start
        self.log = log
        self.stop = stop
        self.speaker = speaker
        self.input_tag = input_tag
        self.output_tag = output_tag
        self.handle: str | None = None
        self.reconnects = 0
        self.model: str | None = None
        self.api_version: str | None = None
        self.dropped_fields: list[str] = []
        self._reconnect_now = False

    # -- helpers ----------------------------------------------------------
    @property
    def tags(self) -> list[str]:
        return [t for t in (self.input_tag, self.output_tag) if t]

    def _remaining_droppable(self) -> list[str]:
        return [k for k in DEGRADE_ORDER if k not in self.dropped_fields]

    def _degrade(self, low: str) -> bool:
        """Drop one optional config field; True if something was dropped."""
        remaining = self._remaining_droppable()
        if not remaining:
            return False
        field = _mentioned_field(low, remaining) or remaining[0]
        self.dropped_fields.append(field)
        if field == "session_resumption":
            self.handle = None
        log_note(f"[{self.name}] server rejected session config -> retrying "
                 f"without '{field}'")
        return True

    # -- upstream ---------------------------------------------------------
    async def _send(self, session) -> None:
        while not self.stop.is_set():
            try:
                chunk = await asyncio.wait_for(self.q.get(), timeout=0.25)
            except asyncio.TimeoutError:
                continue
            await send_audio(session, chunk)

    # -- downstream -------------------------------------------------------
    def _handle_msg(self, msg) -> None:
        upd = getattr(msg, "session_resumption_update", None)
        if upd is not None and getattr(upd, "resumable", False) \
                and getattr(upd, "new_handle", None):
            self.handle = upd.new_handle

        if getattr(msg, "go_away", None) is not None:
            left = getattr(msg.go_away, "time_left", None)
            log_note(f"[{self.name}] server GoAway (time_left={left}); "
                     f"will reconnect")
            self._reconnect_now = True

        sc = getattr(msg, "server_content", None)
        if sc is None:
            return

        if self.input_tag:
            it = getattr(sc, "input_transcription", None)
            if it is not None and getattr(it, "text", None):
                self.log.feed(self.input_tag, it.text)

        if self.output_tag:
            ot = getattr(sc, "output_transcription", None)
            if ot is not None and getattr(ot, "text", None):
                self.log.feed(self.output_tag, ot.text)

        if getattr(sc, "interrupted", False) and self.speaker:
            self.speaker.reset()

        if self.speaker is not None:
            data = getattr(msg, "data", None)
            if data:
                self.speaker.play(data)
            else:
                mt = getattr(sc, "model_turn", None)
                for part in (getattr(mt, "parts", None) or []):
                    inline = getattr(part, "inline_data", None)
                    if inline is not None and getattr(inline, "data", None):
                        self.speaker.play(inline.data)

        if getattr(sc, "turn_complete", False) or \
                getattr(sc, "generation_complete", False):
            self.log.flush(self.tags)            # only our own tags

    async def _recv(self, session) -> None:
        async for msg in session.receive():
            self._handle_msg(msg)
            if self._reconnect_now or self.stop.is_set():
                return

    # -- supervisor -------------------------------------------------------
    async def run(self) -> None:
        backoff = 1.0
        while not self.stop.is_set():
            if self._ci >= len(self.candidates):
                log_note(f"[{self.name}] no usable live model left; tried: "
                         + ", ".join(f"{m}@{v}" for m, v in self.candidates))
                log_note(f"[{self.name}] run with --check to see which models "
                         f"this API key can reach")
                break

            model, api_version = self.candidates[self._ci]
            self._reconnect_now = False
            try:
                client = self.pool.get(api_version)
                cfg = self.config_builder(self.handle, tuple(self.dropped_fields))
                async with client.aio.live.connect(model=model,
                                                   config=cfg) as session:
                    self.model, self.api_version = model, api_version
                    extra = (f" (resumed)" if self.handle else "")
                    if self.dropped_fields:
                        extra += f" [without: {', '.join(self.dropped_fields)}]"
                    log_note(f"[{self.name}] connected: {model} "
                             f"({api_version}){extra}")
                    backoff = 1.0
                    sender = asyncio.create_task(self._send(session),
                                                 name=f"{self.name}-send")
                    try:
                        await self._recv(session)
                    finally:
                        sender.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await sender
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if self.stop.is_set():
                    break
                text = f"{type(exc).__name__}: {exc}"
                low = text.lower()
                log_note(f"[{self.name}] session error "
                         f"({model}@{api_version}): {text}")

                # 1) hard credential/quota problems: no point retrying
                if _is_auth_error(low) and not _is_model_error(low):
                    log_note(f"[{self.name}] credential/quota problem — aborting")
                    self.stop.set()
                    break

                # 2) the server named one of our optional config fields
                field = _mentioned_field(low, self._remaining_droppable())
                if field is not None:
                    self._degrade(low)
                    continue

                # 3) model or API version simply not available
                if _is_model_error(low):
                    self._ci += 1
                    self.handle = None
                    if self._ci < len(self.candidates):
                        nm, nv = self.candidates[self._ci]
                        log_note(f"[{self.name}] model/version rejected -> trying "
                                 f"{nm} ({nv})")
                    continue

                # 4) generic bad-config: surrender one optional field
                if _is_config_error(low) and self._degrade(low):
                    continue

                # 5) transport hiccup: back off and resume
                self.reconnects += 1
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 15.0)
            else:
                if not self.stop.is_set():
                    self.reconnects += 1
                    log_note(f"[{self.name}] stream closed; reconnecting")
                    await asyncio.sleep(0.5)
        self.log.flush(self.tags)
        log_note(f"[{self.name}] stopped after {self.reconnects} reconnect(s)")


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
def list_devices() -> int:
    print(sd.query_devices())
    try:
        din, dout = sd.default.device
        print(f"\ndefault input index : {din}\ndefault output index: {dout}")
    except Exception:
        pass
    print("\nPick a name or index, then:  --device 3   or   --device pulse")
    return 0


async def check(pool: ClientPool) -> int:
    print("google-genai :", getattr(genai, "__version__", "unknown"))
    print("api versions :", ", ".join(API_VERSIONS))

    discovered: list[str] = []
    for ver in API_VERSIONS:
        names = discover_live_models(pool.get(ver))
        if names:
            print(f"\nlive-capable models visible to this key ({ver}):")
            for n in names:
                print("   ", n)
            for n in names:
                if n not in discovered:
                    discovered.append(n)

    translate = order_candidates(TRANSLATE_MODELS, discovered, "translate")
    transcribe = order_candidates(TRANSCRIBE_MODELS, discovered, "transcribe")

    async def probe_bare(model: str, modality: str) -> str | None:
        for ver in API_VERSIONS:
            try:
                cfg = build_live_config(response_modalities=[modality])
                async with pool.get(ver).aio.live.connect(model=model, config=cfg):
                    print(f"connect OK   : {model}  ({ver}, {modality})")
                    return ver
            except Exception as exc:
                print(f"connect FAIL : {model}  ({ver}, {modality})  ->  "
                      f"{type(exc).__name__}: {exc}")
        return None

    async def probe_full(model: str, ver: str, builder) -> list[str]:
        """Connect with the real config, degrading fields as needed."""
        dropped: list[str] = []
        while True:
            try:
                cfg = builder(None, tuple(dropped))
                async with pool.get(ver).aio.live.connect(model=model, config=cfg):
                    if dropped:
                        print(f"session OK   : {model} ({ver}) without: "
                              f"{', '.join(dropped)}")
                    else:
                        print(f"session OK   : {model} ({ver}) with full config")
                    return dropped
            except Exception as exc:
                low = f"{type(exc).__name__}: {exc}".lower()
                remaining = [k for k in DEGRADE_ORDER if k not in dropped]
                field = _mentioned_field(low, remaining)
                if field is None and _is_config_error(low) and remaining:
                    field = remaining[0]
                if field is None:
                    print(f"session FAIL : {model} ({ver})  ->  "
                          f"{type(exc).__name__}: {exc}")
                    return dropped
                print(f"session retry: {model} ({ver}) dropping '{field}'")
                dropped.append(field)

    good_translate: tuple[str, str] | None = None
    good_transcribe: tuple[str, str] | None = None

    print("\n-- translate candidates (AUDIO out) --")
    for m in translate[:6]:
        ver = await probe_bare(m, "AUDIO")
        if ver:
            await probe_full(m, ver, translate_config)
            good_translate = (m, ver)
            break

    print("\n-- transcribe candidates (TEXT out) --")
    for m in transcribe[:6]:
        ver = await probe_bare(m, "TEXT")
        if ver:
            await probe_full(m, ver, transcribe_config)
            good_transcribe = (m, ver)
            break

    print()
    if good_translate:
        print(f"TRANSLATE_MODEL  ->  {good_translate[0]}  ({good_translate[1]})")
    else:
        print("TRANSLATE_MODEL  ->  none of the candidates connected")
    if good_transcribe:
        print(f"TRANSCRIBE_MODEL ->  {good_transcribe[0]}  ({good_transcribe[1]})")
    else:
        print("TRANSCRIBE_MODEL ->  none of the candidates connected")

    return 0 if (good_translate or good_transcribe) else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Live EN->ES speech translation / transcription "
                    "(Gemini Live API).")
    p.add_argument("--mode", choices=("translate", "transcribe", "dual"),
                   default=os.getenv("MODE", "translate"),
                   help="translate: EN+ES from one session (default). "
                        "transcribe: EN only. dual: two sessions (2x quota).")
    p.add_argument("--device", default=os.getenv("AUDIO_INPUT_DEVICE"),
                   help="input device index or name (see --list-devices)")
    p.add_argument("--play-audio", action="store_true",
                   default=os.getenv("PLAY_TRANSLATED_AUDIO", "0") == "1",
                   help="play the Spanish audio through the speakers")
    p.add_argument("--duration", type=float,
                   default=float(os.getenv("DURATION", "0")),
                   help="stop automatically after N seconds (0 = run until Ctrl-C)")
    p.add_argument("--out-dir", default=os.getenv("TRANSCRIPT_DIR",
                                                  str(Path.home() / "Desktop")))
    p.add_argument("--api-version", default=None,
                   help="force a single API version (e.g. v1beta or v1alpha)")
    p.add_argument("--translate-model", default=None,
                   help="override the translate model id")
    p.add_argument("--transcribe-model", default=None,
                   help="override the transcribe model id")
    p.add_argument("--no-discover", action="store_true",
                   help="do not query models.list() for extra fallbacks")
    p.add_argument("--list-devices", action="store_true")
    p.add_argument("--check", action="store_true",
                   help="verify key, SDK, model reachability, then exit")
    return p.parse_args(argv)


async def _await_all(tasks: Sequence[asyncio.Task]) -> None:
    """Coroutine wrapper — create_task() cannot accept a gather() Future."""
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def async_main(args: argparse.Namespace, api_key: str) -> int:
    pool = ClientPool(api_key)

    if args.check:
        return await check(pool)

    translate_models = ([args.translate_model] if args.translate_model
                        else list(TRANSLATE_MODELS))
    transcribe_models = ([args.transcribe_model] if args.transcribe_model
                         else list(TRANSCRIBE_MODELS))

    if args.mode in ("translate", "dual") and not translate_models:
        print("FATAL: no translate model candidates (TRANSLATE_MODEL is empty)",
              file=sys.stderr)
        return 2
    if args.mode in ("transcribe", "dual") and not transcribe_models:
        print("FATAL: no transcribe model candidates (TRANSCRIBE_MODEL is empty)",
              file=sys.stderr)
        return 2

    if not args.no_discover:
        discovered = discover_live_models(pool.get(API_VERSIONS[0]))
        if discovered:
            for want, label in ((translate_models, "translate"),
                                (transcribe_models, "transcribe")):
                missing = [m for m in want if m not in discovered]
                if missing:
                    log_note(f"[models] {label}: not advertised by this key -> "
                             + ", ".join(missing))
            translate_models = order_candidates(translate_models, discovered,
                                                "translate")
            transcribe_models = order_candidates(transcribe_models, discovered,
                                                 "transcribe")

    loop = asyncio.get_running_loop()
    stop = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError, AttributeError, ValueError):
            loop.add_signal_handler(sig, stop.set)

    out_file = (Path(args.out_dir).expanduser()
                / f"live_translation_{datetime.now():%Y%m%d_%H%M%S}.txt")
    log = TranscriptLog(out_file, args.mode)

    device = resolve_device(args.device)
    try:
        mic = MicBroadcaster(device, loop)
    except Exception as exc:
        print(f"FATAL: cannot open audio input {device!r}: "
              f"{type(exc).__name__}: {exc}\n"
              "       run with --list-devices to see valid choices",
              file=sys.stderr)
        return 4

    print("=" * 72)
    print(f"  Gemini Live  |  mode={args.mode}  |  {SOURCE_LANG} -> {TARGET_LANG}")
    if args.mode in ("translate", "dual"):
        print(f"  translate   : {translate_models[0]}")
    if args.mode in ("transcribe", "dual"):
        print(f"  transcribe  : {transcribe_models[0]}")
    print(f"  transcript  : {out_file}")
    print(f"  audio out   : {'on' if args.play_audio else 'off'}"
          f"   |  duration: {args.duration or 'until Ctrl-C'}")
    print("  Speak English. Ctrl-C to stop.")
    print("=" * 72, flush=True)

    workers: list[SessionWorker] = []
    speaker_cm = Speaker(OUT_RATE) if args.play_audio else contextlib.nullcontext()

    # NOTE: workers are constructed (and therefore subscribe to the mic)
    # BEFORE the capture stream is started, so no audio is lost.
    with speaker_cm as speaker:
        if args.mode in ("translate", "dual"):
            workers.append(SessionWorker(
                "translate", translate_models, translate_config, pool, mic, log,
                stop, speaker if args.play_audio else None,
                input_tag=None if args.mode == "dual" else "EN",
                output_tag="ES",
            ))
        if args.mode in ("transcribe", "dual"):
            workers.append(SessionWorker(
                "transcribe", transcribe_models, transcribe_config, pool, mic,
                log, stop, None, input_tag="EN", output_tag=None,
            ))

        with mic:
            worker_tasks = [asyncio.create_task(w.run(), name=w.name)
                            for w in workers]
            aux_tasks = [
                asyncio.create_task(idle_flusher(log, stop), name="flusher"),
                asyncio.create_task(mic_monitor(mic, stop), name="mic-monitor"),
            ]

            if args.duration and args.duration > 0:
                async def timer() -> None:
                    with contextlib.suppress(asyncio.CancelledError):
                        await asyncio.sleep(args.duration)
                        log_note("[main] duration reached")
                        stop.set()
                aux_tasks.append(asyncio.create_task(timer(), name="timer"))

            # Finish when the user/timer asks us to stop, or when every session
            # worker has given up (no usable model / fatal credential problem).
            waiter = asyncio.create_task(stop.wait(), name="stop")
            all_workers = asyncio.create_task(_await_all(worker_tasks),
                                              name="workers")

            try:
                await asyncio.wait({waiter, all_workers},
                                   return_when=asyncio.FIRST_COMPLETED)
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:            # Windows / no signal handler
                pass
            finally:
                stop.set()
                pending = [*worker_tasks, *aux_tasks, waiter, all_workers]
                for t in pending:
                    t.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await asyncio.gather(*pending, return_exceptions=True)

    # -- shutdown summary ---------------------------------------------------
    log.flush()
    print()
    connected = [w for w in workers if w.model]
    for w in workers:
        if w.model:
            extra = (f", dropped: {', '.join(w.dropped_fields)}"
                     if w.dropped_fields else "")
            log_note(f"[{w.name}] last model: {w.model} ({w.api_version}), "
                     f"{w.reconnects} reconnect(s){extra}")
        else:
            log_note(f"[{w.name}] never connected to any candidate model")
    log_note(f"[main] transcript written: {out_file}  ({log.lines} line(s))")

    if not connected:
        log_note("[main] nothing connected — try:  --check   "
                 "(or set TRANSLATE_MODEL / TRANSCRIBE_MODEL)")
        return 5
    return 0


def main(argv: list[str] | None = None) -> int:
    global API_VERSIONS

    args = parse_args(argv)

    if args.list_devices:
        return list_devices()

    if args.api_version:
        API_VERSIONS = [args.api_version.strip()]
    if not API_VERSIONS:
        API_VERSIONS = ["v1beta"]

    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
               or os.getenv("GOOGLE_GENAI_API_KEY"))
    if not api_key:
        print("FATAL: no API key. Set GEMINI_API_KEY (or GOOGLE_API_KEY):\n"
              "       export GEMINI_API_KEY='...'\n"
              "       key: https://aistudio.google.com/apikey", file=sys.stderr)
        return 2

    try:
        return asyncio.run(async_main(args, api_key))
    except KeyboardInterrupt:
        print("\n[main] interrupted", flush=True)
        return 130
    except Exception:
        print("\nFATAL: unhandled exception:", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
