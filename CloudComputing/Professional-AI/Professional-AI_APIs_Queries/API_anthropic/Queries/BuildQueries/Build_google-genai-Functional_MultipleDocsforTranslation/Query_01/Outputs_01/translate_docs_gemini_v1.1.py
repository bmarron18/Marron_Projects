#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Sep 19 12:22:40 2026
@author: bruce-vdb, claude-opus-5

Batch document translation with the Google Gemini API.
======================================================

Features
--------
* Translates **many** documents in one run (explicit file list, one or more
  directories, or the configured default input directory).
* Accepts **several input types** - anything Gemini can read as inline data or
  through the Files API (.pdf, .txt, .md, .html, .csv, .xml, .rtf, .tex,
  .json, .py, .js, .css ...).
* Produces a **unique output file for every input file**, in the requested
  output format (.txt, .md, .html, .tex, .json).
* Small files are sent inline; large files (> 18 MB) go through the Files API
  and are deleted again as soon as the translation is finished.
* Per-file error isolation, retry with exponential back-off, run summary.

Defaults
---------
DEFAULT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_INPUT_DIR = Path.home() / "Desktop" / "to_translate"
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "translated"
DEFAULT_SOURCE_LANGUAGE = "English"
DEFAULT_TARGET_LANGUAGE = "Spanish"
DEFAULT_OUTPUT_FORMAT = "txt"


Run from command line
[In Spyder (no command line): just press *Run* (f5) to run defaults]
-------------
    cd ~/spyder-6/envs && 
    source ./ai-apis/bin/activate
   
    python3  ~/Desktop/translate_doc s_gemini_v1.1.py                       # use defaults
    python3  ~/Desktop/translate_doc s_gemini_v1.1.py --dry-run             # show the plan only


see 'Command-line interface' in script for optional toggles
For example, 

        # translate just one file to French
    python3 translate_doc s_gemini_v1.1.py ~/Desktop/*.pdf -t French
    
        #change name of input directory, change name of output directory, change output file type
    python3 translate_doc s_gemini_v1.1.py -i ~/Desktop/in -o ~/Desktop/out -r -f md
    

"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
LOGGER = logging.getLogger("gemini_translate")

DEFAULT_MODEL = "gemini-3.1-pro-preview"
DEFAULT_INPUT_DIR = Path.home() / "Desktop" / "to_translate"
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "translated"
DEFAULT_SOURCE_LANGUAGE = "English"
DEFAULT_TARGET_LANGUAGE = "Spanish"
DEFAULT_OUTPUT_FORMAT = "txt"

INLINE_LIMIT_BYTES = 18 * 1024 * 1024      # larger payloads -> Files API
UPLOAD_POLL_SECONDS = 2.0
UPLOAD_TIMEOUT_SECONDS = 300.0
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 5.0
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})


#: Input extension -> MIME type accepted by Gemini.
INPUT_MIME_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".text": "text/plain",
    ".tex": "text/plain",
    ".json": "text/plain",
    ".srt": "text/plain",
    ".vtt": "text/plain",
    ".md": "text/md",
    ".markdown": "text/md",
    ".csv": "text/csv",
    ".tsv": "text/csv",
    ".html": "text/html",
    ".htm": "text/html",
    ".xml": "text/xml",
    ".rtf": "text/rtf",
    ".css": "text/css",
    ".js": "text/javascript",
    ".py": "text/x-python",
}
# NOTE: .docx/.odt/.pptx are *not* natively supported - export them to PDF
#       first (e.g. `libreoffice --headless --convert-to pdf file.docx`).


@dataclass(frozen=True)
class OutputFormat:
    """Extension, response MIME type and prompt wording of an output format."""

    extension: str
    response_mime_type: str | None
    description: str


OUTPUT_FORMATS: dict[str, OutputFormat] = {
    "txt": OutputFormat(".txt", "text/plain", "plain UTF-8 text (.txt)"),
    "md": OutputFormat(".md", "text/plain", "GitHub-flavoured Markdown (.md)"),
    "html": OutputFormat(".html", "text/plain",
                         "one complete, valid HTML5 document (.html)"),
    "tex": OutputFormat(".tex", "text/plain",
                        "a compilable LaTeX source document (.tex)"),
    "json": OutputFormat(".json", "application/json",
                         'a single JSON object with the keys "source_file", '
                         '"target_language" and "translation"'),
}

SYSTEM_INSTRUCTION = (
    "You are an expert linguist specialising in document translation. "
    "Preserve the meaning, register and tone of the source text, and keep the "
    "original layout intact: line breaks, indentation, spacing, paragraphs, "
    "headings, lists, tables, footnotes and quotations. Do not summarise, "
    "omit or add content, and never include commentary, preambles, "
    "explanations or alternative translations. Return the translation and "
    "nothing else."
)


@dataclass(frozen=True)
class TranslationJob:
    """One source document and the file its translation will be written to."""

    source: Path
    mime_type: str
    destination: Path


# --------------------------------------------------------------------------- #
# File discovery / output naming
# --------------------------------------------------------------------------- #
def iter_candidate_files(
    sources: Sequence[Path],
    input_dir: Path,
    pattern: str,
    recursive: bool,
) -> Iterator[Path]:
    """Yield every unique file found in `sources` (or in `input_dir`)."""
    roots = [p.expanduser() for p in sources] or [input_dir.expanduser()]
    seen: set[Path] = set()

    for root in roots:
        if root.is_dir():
            globber = root.rglob if recursive else root.glob
            found = sorted(p for p in globber(pattern) if p.is_file())
        elif root.is_file():
            found = [root]
        else:
            LOGGER.warning("Skipping '%s' - no such file or directory.", root)
            continue

        for path in found:
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield resolved


def select_translatable(paths: Iterable[Path]) -> list[tuple[Path, str]]:
    """Keep only files whose extension maps to a Gemini-readable MIME type."""
    selected: list[tuple[Path, str]] = []
    for path in paths:
        mime_type = INPUT_MIME_TYPES.get(path.suffix.lower())
        if mime_type is None:
            LOGGER.warning("Skipping '%s' - unsupported file type '%s'.",
                           path.name, path.suffix or "<none>")
            continue
        selected.append((path, mime_type))
    return selected


def slugify(text: str) -> str:
    """'Brazilian Portuguese' -> 'brazilian_portuguese' (safe for filenames)."""
    return re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower() or "translated"


def unique_path(candidate: Path, taken: set[Path], overwrite: bool) -> Path:
    """Return `candidate`, or `name_01.ext`, `name_02.ext` ... if it is taken."""
    stem, suffix = candidate.with_suffix(""), candidate.suffix
    result, counter = candidate, 1
    while result in taken or (not overwrite and result.exists()):
        result = Path(f"{stem}_{counter:02d}{suffix}")
        counter += 1
    return result


def build_jobs(
    files: Sequence[tuple[Path, str]],
    input_dir: Path,
    output_dir: Path,
    target_language: str,
    output_format: OutputFormat,
    overwrite: bool,
) -> list[TranslationJob]:
    """Pair every source file with a unique destination file."""
    jobs: list[TranslationJob] = []
    taken: set[Path] = set()
    language_slug = slugify(target_language)
    input_root = input_dir.expanduser().resolve()

    for source, mime_type in files:
        try:                                    # mirror sub-directories
            sub_dir = source.parent.relative_to(input_root)
        except ValueError:
            sub_dir = Path(".")
        name = f"{source.stem}_{language_slug}{output_format.extension}"
        destination = unique_path(output_dir / sub_dir / name, taken, overwrite)
        taken.add(destination)
        jobs.append(TranslationJob(source, mime_type, destination))

    return jobs


# --------------------------------------------------------------------------- #
# Translator
# --------------------------------------------------------------------------- #
class GeminiTranslator:
    """Thin, reusable wrapper around `client.models.generate_content`."""

    def __init__(
        self,
        client: genai.Client,
        model: str,
        source_language: str,
        target_language: str,
        output_format: OutputFormat,
    ) -> None:
        self.client = client
        self.model = model
        self.source_language = source_language
        self.target_language = target_language
        self.output_format = output_format
        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            response_mime_type=output_format.response_mime_type,
        )

    # -- public API -------------------------------------------------------- #
    def translate(self, job: TranslationJob) -> str:
        """Translate one document and return the translated text."""
        content, uploaded = self._build_content(job)
        try:
            response = self._generate([content, self._build_prompt(job)])
        finally:
            self._cleanup(uploaded)

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise RuntimeError(
                f"Gemini returned no text (finish reason: "
                f"{self._finish_reason(response)!r})."
            )
        return text

    # -- helpers ----------------------------------------------------------- #
    def _build_prompt(self, job: TranslationJob) -> str:
        return (
            f"Translate the attached document '{job.source.name}' from "
            f"{self.source_language} into standard, natural, fluent "
            f"{self.target_language}.\n"
            "Reproduce the original formatting as faithfully as the output "
            "format allows (line breaks, indentation, spacing, paragraphs, "
            "headings, lists, tables and quotations).\n"
            "Leave code, mathematical notation, URLs, file names and "
            "bibliographic references untranslated.\n"
            f"Return the result as {self.output_format.description}, encoded "
            "in UTF-8, with no extra commentary."
        )

    def _build_content(
        self, job: TranslationJob
    ) -> tuple[types.Part | types.File, types.File | None]:
        """Inline small documents; upload large ones via the Files API."""
        size = job.source.stat().st_size
        if size <= INLINE_LIMIT_BYTES:
            part = types.Part.from_bytes(
                data=job.source.read_bytes(), mime_type=job.mime_type
            )
            return part, None

        LOGGER.info("Uploading '%s' (%.1f MB) via the Files API ...",
                    job.source.name, size / 1024 ** 2)
        uploaded = self.client.files.upload(
            file=job.source,
            config=types.UploadFileConfig(
                mime_type=job.mime_type, display_name=job.source.name
            ),
        )
        return self._wait_until_active(uploaded), uploaded

    def _wait_until_active(self, file_obj: types.File) -> types.File:
        deadline = time.monotonic() + UPLOAD_TIMEOUT_SECONDS
        while self._state(file_obj) == "PROCESSING":
            if time.monotonic() > deadline:
                raise TimeoutError(f"Upload of '{file_obj.name}' timed out.")
            time.sleep(UPLOAD_POLL_SECONDS)
            file_obj = self.client.files.get(name=file_obj.name)
        if self._state(file_obj) == "FAILED":
            raise RuntimeError(f"Gemini failed to process '{file_obj.name}'.")
        return file_obj

    def _generate(self, contents: list) -> types.GenerateContentResponse:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return self.client.models.generate_content(
                    model=self.model, config=self.config, contents=contents
                )
            except genai_errors.APIError as exc:
                status = getattr(exc, "code", None)
                if attempt == MAX_ATTEMPTS or status not in RETRYABLE_STATUS:
                    raise
                delay = BACKOFF_SECONDS * 2 ** (attempt - 1)
                LOGGER.warning("API error %s - retrying in %.0f s (%d/%d).",
                               status, delay, attempt, MAX_ATTEMPTS)
                time.sleep(delay)
        raise RuntimeError("Unreachable")       # pragma: no cover

    def _cleanup(self, uploaded: types.File | None) -> None:
        if uploaded is None:
            return
        try:
            self.client.files.delete(name=uploaded.name)
            LOGGER.debug("Deleted remote file '%s'.", uploaded.name)
        except Exception as exc:                # noqa: BLE001 - never fatal
            LOGGER.debug("Could not delete '%s': %s", uploaded.name, exc)

    @staticmethod
    def _state(file_obj: types.File) -> str:
        state = getattr(file_obj, "state", None)
        return getattr(state, "name", str(state)).upper()

    @staticmethod
    def _finish_reason(response) -> str | None:
        try:
            return str(response.candidates[0].finish_reason)
        except (AttributeError, IndexError, TypeError):
            return None


# --------------------------------------------------------------------------- #
# Command-line interface
# --------------------------------------------------------------------------- #
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate one or many documents with the Gemini API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("sources", nargs="*", type=Path,
                        help="Files and/or directories to translate "
                             "(default: --input-dir).")
    parser.add_argument("-i", "--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("-o", "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-s", "--source-language", default=DEFAULT_SOURCE_LANGUAGE)
    parser.add_argument("-t", "--target-language", default=DEFAULT_TARGET_LANGUAGE)
    parser.add_argument("-f", "--format", dest="output_format",
                        choices=sorted(OUTPUT_FORMATS), default=DEFAULT_OUTPUT_FORMAT)
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL)
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Descend into sub-directories.")
    parser.add_argument("--pattern", default="*",
                        help="Glob pattern applied to directories.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing outputs instead of "
                             "creating name_01, name_02 ...")
    parser.add_argument("--workers", type=int, default=1,
                        help="Documents translated in parallel.")
    parser.add_argument("--dry-run", action="store_true",
                        help="List what would be translated and exit.")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    output_format = OUTPUT_FORMATS[args.output_format]
    files = select_translatable(
        iter_candidate_files(args.sources, args.input_dir,
                             args.pattern, args.recursive)
    )
    if not files:
        LOGGER.error("No translatable files found. Supported types: %s",
                     ", ".join(sorted(INPUT_MIME_TYPES)))
        return 1

    jobs = build_jobs(files, args.input_dir, args.output_dir.expanduser(),
                      args.target_language, output_format, args.overwrite)

    LOGGER.info("%d document(s) queued -> %s (%s)",
                len(jobs), args.output_dir, output_format.extension)
    for job in jobs:
        LOGGER.info("  %-45s -> %s", job.source.name, job.destination.name)
    if args.dry_run:
        return 0

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        LOGGER.error("Environment variable GEMINI_API_KEY is not set.")
        return 2

    translator = GeminiTranslator(
        client=genai.Client(api_key=api_key),
        model=args.model,
        source_language=args.source_language,
        target_language=args.target_language,
        output_format=output_format,
    )

    def run(job: TranslationJob) -> tuple[TranslationJob, str | None]:
        started = time.monotonic()
        try:
            text = translator.translate(job)
            job.destination.parent.mkdir(parents=True, exist_ok=True)
            with open(job.destination, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text.rstrip("\n") + "\n")
        except Exception as exc:                # noqa: BLE001 - isolate failures
            LOGGER.error("FAILED  %s: %s", job.source.name, exc)
            return job, str(exc)
        LOGGER.info("OK      %s (%.1f s, %d chars) -> %s",
                    job.source.name, time.monotonic() - started,
                    len(text), job.destination)
        return job, None

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        results = list(pool.map(run, jobs))

    failures = [(job, err) for job, err in results if err]
    LOGGER.info("Finished: %d succeeded, %d failed.",
                len(results) - len(failures), len(failures))
    for job, err in failures:
        LOGGER.info("  %s: %s", job.source.name, err)
    return 0 if not failures else 3


if __name__ == "__main__":
    sys.exit(main())