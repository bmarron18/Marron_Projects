#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Sep 19 12:27:53 2026
@author: bruce-vdb, claude-opus-5

========================================================
Batch document translation with the OpenAI Responses API.
=========================================================

Features
--------
* Translates **many** documents in one run (explicit file list, one or more
  directories, or the configured default input directory).
* Handles **three input families**:
    - PDF          -> uploaded to the Files API and sent as `input_file`
    - text formats -> read locally and sent as delimited `input_text`
                      (.txt, .md, .html, .csv, .tsv, .xml, .tex, .json,
                       .rtf, .py, .js, .css, .srt, .vtt ...)
    - images       -> uploaded and sent as `input_image` (the model reads and
                      translates the text it sees)
* Produces a **unique output file for every input file** in the requested
  output format (.txt, .md, .html, .tex, .json).
* Uploaded files are deleted from OpenAI storage as soon as the job is done.
* Per-file error isolation, retry with exponential back-off, run summary.

Defaults
----------
DEFAULT_MODEL = "gpt-5.6"
DEFAULT_INPUT_DIR = Path.home() / "Desktop" / "to_translate"
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "translated"
DEFAULT_SOURCE_LANGUAGE = "English"
DEFAULT_TARGET_LANGUAGE = "Spanish"
DEFAULT_OUTPUT_FORMAT = "txt"


Run script in Spyder (no command line):
-------------
    * *Run* (f5)                        <== defaults
    *  type in Ipython Console
        -- main([])                     <== defaults
        -- main(["-t", "German"])       <== w/ toggles


Run script from command line
-------------
cd ~/spyder-6/envs && 
source ./ai-apis/bin/activate
(ai-apis) $ pip install --upgrade openai
   
(ai-apis) $ python3  ~/Desktop/translate_docs_openai_v2.0.py               <== use defaults
(ai-apis) $ python3  ~/Desktop/translate_docs_openai_v2.0.py --dry-run     <== show the plan only


Toggles
-----------
see 'Command-line interface' in script for optional toggles
For example, 

        # translate just one file to French
    python3 translate_docs_gemini_v2.0.py ~/Desktop/*.pdf -t French
    
        #change name of input directory, change name of output directory, change output file type
    python3 translate_docs_gemini_v2.0.py -i ~/Desktop/in -o ~/Desktop/out -r -f md
    python translate_docs_openai_v2.0.py -i ~/Desktop/in -o ~/Desktop/out -r -f html


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
from typing import Any, Iterable, Iterator, Sequence

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
LOGGER = logging.getLogger("openai_translate")

DEFAULT_MODEL = "gpt-5.6"
DEFAULT_INPUT_DIR = Path.home() / "Desktop" / "to_translate"
DEFAULT_OUTPUT_DIR = Path.home() / "Desktop" / "translated"
DEFAULT_SOURCE_LANGUAGE = "English"
DEFAULT_TARGET_LANGUAGE = "Spanish"
DEFAULT_OUTPUT_FORMAT = "txt"

REQUEST_TIMEOUT_SECONDS = 900.0
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 5.0
MAX_INLINE_CHARACTERS = 400_000            # guard against context overflow

PDF_EXTENSIONS = frozenset({".pdf"})
IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif"})
TEXT_EXTENSIONS = frozenset({
    ".txt", ".text", ".md", ".markdown", ".html", ".htm", ".xml", ".csv",
    ".tsv", ".json", ".tex", ".rtf", ".srt", ".vtt", ".py", ".js", ".css",
})
SUPPORTED_EXTENSIONS = PDF_EXTENSIONS | IMAGE_EXTENSIONS | TEXT_EXTENSIONS
# NOTE: .docx/.odt/.pptx are not read directly - export them to PDF first
#       (e.g. `libreoffice --headless --convert-to pdf file.docx`).

TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "cp1252", "latin-1")


@dataclass(frozen=True)
class OutputFormat:
    """Extension, response format and prompt wording of an output format."""

    extension: str
    response_format: str          # "text" or "json_object"
    description: str


OUTPUT_FORMATS: dict[str, OutputFormat] = {
    "txt": OutputFormat(".txt", "text", "plain UTF-8 text (.txt)"),
    "md": OutputFormat(".md", "text", "GitHub-flavoured Markdown (.md)"),
    "html": OutputFormat(".html", "text",
                         "one complete, valid HTML5 document (.html)"),
    "tex": OutputFormat(".tex", "text",
                        "a compilable LaTeX source document (.tex)"),
    "json": OutputFormat(".json", "json_object",
                         'a single JSON object with the keys "source_file", '
                         '"target_language" and "translation"'),
}

SYSTEM_PROMPT = (
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
    kind: str                     # "pdf" | "text" | "image"
    destination: Path


# --------------------------------------------------------------------------- #
# File discovery / output naming
# --------------------------------------------------------------------------- #
def classify(path: Path) -> str | None:
    """Return 'pdf', 'text', 'image' or None for an unsupported extension."""
    suffix = path.suffix.lower()
    if suffix in PDF_EXTENSIONS:
        return "pdf"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in TEXT_EXTENSIONS:
        return "text"
    return None


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
    """Keep only files this script knows how to send to the API."""
    selected: list[tuple[Path, str]] = []
    for path in paths:
        kind = classify(path)
        if kind is None:
            LOGGER.warning("Skipping '%s' - unsupported file type '%s'.",
                           path.name, path.suffix or "<none>")
            continue
        selected.append((path, kind))
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

    for source, kind in files:
        try:                                    # mirror sub-directories
            sub_dir = source.parent.relative_to(input_root)
        except ValueError:
            sub_dir = Path(".")
        name = f"{source.stem}_{language_slug}{output_format.extension}"
        destination = unique_path(output_dir / sub_dir / name, taken, overwrite)
        taken.add(destination)
        jobs.append(TranslationJob(source, kind, destination))

    return jobs


def read_text(path: Path) -> str:
    """Read a text file, trying a few common encodings before giving up."""
    for encoding in TEXT_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_bytes().decode("utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# Translator
# --------------------------------------------------------------------------- #
class OpenAITranslator:
    """Thin, reusable wrapper around `client.responses.create`."""

    def __init__(
        self,
        client: OpenAI,
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

    # -- public API -------------------------------------------------------- #
    def translate(self, job: TranslationJob) -> str:
        """Translate one document and return the translated text."""
        content, uploaded_id = self._build_content(job)
        try:
            response = self._create_response(content)
        finally:
            self._cleanup(uploaded_id)

        text = (getattr(response, "output_text", "") or "").strip()
        if not text:
            raise RuntimeError(
                f"The model returned no text (status: "
                f"{getattr(response, 'status', 'unknown')!r})."
            )
        return text

    # -- helpers ----------------------------------------------------------- #
    def _build_prompt(self, job: TranslationJob) -> str:
        subject = {
            "pdf": "the attached PDF document",
            "image": "the text visible in the attached image",
            "text": "the document supplied below between the "
                    "<<<DOCUMENT>>> markers",
        }[job.kind]
        return (
            f"Translate {subject} ('{job.source.name}') from "
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
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Build the `content` list and return any uploaded file id."""
        prompt = self._build_prompt(job)

        if job.kind == "text":
            body = read_text(job.source)
            if len(body) > MAX_INLINE_CHARACTERS:
                LOGGER.warning("'%s' is very large (%d characters); consider "
                               "splitting it.", job.source.name, len(body))
            content = [{
                "type": "input_text",
                "text": f"{prompt}\n\n<<<DOCUMENT>>>\n{body}\n<<<END DOCUMENT>>>",
            }]
            return content, None

        purpose = "vision" if job.kind == "image" else "user_data"
        with open(job.source, "rb") as fh:
            uploaded = self.client.files.create(file=fh, purpose=purpose)
        LOGGER.debug("Uploaded '%s' as %s.", job.source.name, uploaded.id)

        attachment_type = "input_image" if job.kind == "image" else "input_file"
        content = [
            {"type": attachment_type, "file_id": uploaded.id},
            {"type": "input_text", "text": prompt},
        ]
        return content, uploaded.id

    def _create_response(self, content: list[dict[str, Any]]):
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": SYSTEM_PROMPT,
            "input": [{"role": "user", "content": content}],
            "text": {"format": {"type": self.output_format.response_format}},
        }

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return self.client.responses.create(**kwargs)
            except (RateLimitError, APIConnectionError, APITimeoutError) as exc:
                retryable = True
            except APIStatusError as exc:                      # noqa: F841
                retryable = exc.status_code >= 500
                if not retryable:
                    raise
            if attempt == MAX_ATTEMPTS:
                raise
            delay = BACKOFF_SECONDS * 2 ** (attempt - 1)
            LOGGER.warning("API error - retrying in %.0f s (%d/%d).",
                           delay, attempt, MAX_ATTEMPTS)
            time.sleep(delay)
        raise RuntimeError("Unreachable")       # pragma: no cover

    def _cleanup(self, file_id: str | None) -> None:
        if file_id is None:
            return
        try:
            self.client.files.delete(file_id)
            LOGGER.debug("Deleted remote file %s.", file_id)
        except Exception as exc:                # noqa: BLE001 - never fatal
            LOGGER.debug("Could not delete %s: %s", file_id, exc)


# --------------------------------------------------------------------------- #
# Command-line interface
# --------------------------------------------------------------------------- #
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate one or many documents with the OpenAI API.",
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
                     ", ".join(sorted(SUPPORTED_EXTENSIONS)))
        return 1

    jobs = build_jobs(files, args.input_dir, args.output_dir.expanduser(),
                      args.target_language, output_format, args.overwrite)

    LOGGER.info("%d document(s) queued -> %s (%s)",
                len(jobs), args.output_dir, output_format.extension)
    for job in jobs:
        LOGGER.info("  [%-5s] %-40s -> %s",
                    job.kind, job.source.name, job.destination.name)
    if args.dry_run:
        return 0

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        LOGGER.error("Environment variable OPENAI_API_KEY is not set.")
        return 2

    translator = OpenAITranslator(
        client=OpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS,
                      max_retries=0),          # retries handled in this script
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