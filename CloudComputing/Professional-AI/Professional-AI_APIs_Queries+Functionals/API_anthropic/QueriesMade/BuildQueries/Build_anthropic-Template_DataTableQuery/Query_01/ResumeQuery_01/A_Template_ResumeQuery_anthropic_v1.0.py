#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 07 Nov 2026
Authors : bruce-vdb, claude

-------------------------------------------------
A_Template_ResumeQuery_anthropic_v1.0.py
-------------------------------------------------
  * Finish a streamed run that was cut off (internet failure, crash, etc.)
  * Pulls the partial reply for ONE run out of the output file written by
    A_Template_AnalysisQuery_anthropic_v3.4.py (found by its "Run:" timestamp)
  * Re-sends the ORIGINAL files + prompt, then the partial reply as the
    assistant's turn, then asks the model to continue exactly where it stopped
  * Streams only the NEW text to a continuation file (flushed on every chunk)
  * Writes a merged file = partial + continuation
  * If the connection drops again, it retries and resumes from everything
    received so far (nothing is lost, nothing is re-generated)

  COST NOTE: the original files and the partial reply are sent again as INPUT
  tokens. You pay for the input again, but only for the MISSING part as output.


---------------------------------------------------------------------------
QUICK START
---------------------------------------------------------------------------
  1. Set your API key as ENV VARIABLE (once)
  
  2. Edit SECTION 1 below:
       * RUN_STAMP   -> the "Run: ..." time from the header of the cut-off run
       * INPUT_FILES -> the SAME files as the original run
       * usr_msg     -> the SAME prompt as the original run
     (If the files or the prompt changed since the original run, restore them
      first, otherwise the continuation will not line up.)
     
  3. Preview first (nothing is sent):
runfile('/home/bruce-vdb/Desktop/A_Template_ResumeQuery_anthropic_v1.0.py', args='--dry-run')

  4. Run it with runfile(...) and no args)

  Command-line examples:
     ./A_Template_ResumeQuery_...py --dry-run
     ./A_Template_ResumeQuery_...py --run-stamp "2026-11-06 10:53:11"
     ./A_Template_ResumeQuery_...py --list-runs
     ./A_Template_ResumeQuery_...py --partial-file QueryResponse_Anthropic.txt
     ./A_Template_ResumeQuery_...py --prompt-file my_prompt.txt


-----------
OUTPUTS  (in DOC_DIR)
-----------
  Resumed_Response_continuation.txt   <== only the new text (streamed, flushed)
  Resumed_Response_merged.txt         <== partial + continuation (the full answer)
"""

from __future__ import annotations

import argparse
import base64
import re
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    sys.exit("The 'anthropic' package is not installed.  Run:  pip install --upgrade anthropic")


# =========================================================================
#  SECTION 1 -- CONFIGURATION / USER SETTINGS  (edit these)
# =========================================================================

# ---- Folder with the input files and the output file of the cut-off run ---
DOC_DIR = Path.home() / "Desktop"

# ---- Output file written by the original run (v3.4) -----------------------
PARTIAL_FILE = "QueryResponse_Anthropic.txt"

# ---- Which run to resume: the time shown in its header --------------------
#      ( Run: 2026-11-06 10:53:11  |  Model: ... )
RUN_STAMP = "2026-11-06 10:53:11"

# ---- Input files: the SAME ones the original run used ----------------------
INPUT_FILES = [
    "Partial_Response.txt",
    "Analysis.txt",
    "Script.txt",
    "A_Template_AnalysisQuery_anthropic_v3.4.py",
]

# ---- Prompt: the SAME one the original run used ----------------------------
usr_msg = (
    "Review a) Partial_Response.txt (sample of a truncated run), b) Analysis.txt (analysis of what "
    "went wrong), c) Script.txt (earlier attempt), d) A_Template_AnalysisQuery_anthropic_v3.4.py (format "
    "template). Write a new script named `A_Template_DataTableQuery_anthropic_v2.0.py` for "
    "`claude-opus-5-5` that turns given, partial, or sourced data (user to specify: files / URL / web "
    "search) into an organized table. Requirements: (1) stream the API call; (2) the model emits one "
    "JSON object per line for each chunk, and Python parses, de-duplicates, sorts and merges them, "
    "tolerating a cut-off final line; (3) keep d)'s structure and fold in c)'s parse/sort/write logic, "
    "fixing c)'s bugs; (4) write three files: `.md` table, `.csv` table, and `.txt` commentary covering "
    "data sufficiency, completeness, accuracy, table construction, legend and flags. Data source, "
    "columns, key column, sort order and overwrite/ append are all per-run settings, editable in SECTION "
    "1 and overridable by CLI flags. When left blank, columns are inferred from the first chunk, "
    "de-duplication uses the whole row, and order is the arrival order. Constraints: stdlib plus "
    "`anthropic` only; save partial output if interrupted; [overwrite/append]; keep the v3.4 header and "
    "docstring style."
)

# System-level message (None = no system prompt) -- same as the original run
sys_msg = "You are an expert analyst and Python coder."

# ---- Output names -------------------------------------------------------
OUTPUT_PREFIX = "Resumed_Response"

# ---- Model / output size -----------------------------------------------
MODEL = "claude-fable-5-1"      # same model as the original run
MAX_TOKENS = 128000             # max output tokens per pass
MAX_CONTINUATIONS = 3           # extra passes if the reply hits max_tokens again
MAX_RETRIES = 5                 # consecutive connection failures tolerated
RETRY_WAIT = 15                 # seconds between retries (grows each time)


# =========================================================================
#  SECTION 2 -- FIXED SETTINGS  (normally no need to edit)
# =========================================================================

BAR = "=" * 70

IMAGE_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp",
}

CONTINUE_PROMPT = (
    "Your previous reply was cut off before it was finished. Continue exactly "
    "where you stopped -- no preamble, no repeated text. If the text above "
    "ends in the middle of a word, line or code block, begin with the rest of "
    "that word, line or block."
)


# =========================================================================
#  SECTION 3 -- HELPER FUNCTIONS
# =========================================================================

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Resume a cut-off streamed run: re-send files + prompt + "
                    "the partial reply and stream only the missing remainder.")
    p.add_argument("files", nargs="*",
                   help="input files (default: INPUT_FILES in the script)")
    p.add_argument("-d", "--dir", type=Path, default=DOC_DIR,
                   help=f"folder for input/output files (default: {DOC_DIR})")
    p.add_argument("--partial-file", default=PARTIAL_FILE,
                   help=f"output file of the cut-off run (default: {PARTIAL_FILE})")
    p.add_argument("--run-stamp", default=RUN_STAMP,
                   help=f"'Run:' time of the cut-off run (default: {RUN_STAMP})")
    p.add_argument("-p", "--prompt", default=None,
                   help="prompt text (default: usr_msg in the script)")
    p.add_argument("--prompt-file", type=Path, default=None,
                   help="read the prompt from a text file")
    p.add_argument("-s", "--system", default=sys_msg, help="optional system prompt")
    p.add_argument("-m", "--model", default=MODEL, help=f"model id (default: {MODEL})")
    p.add_argument("--max-tokens", type=int, default=MAX_TOKENS,
                   help=f"max output tokens per pass (default: {MAX_TOKENS})")
    p.add_argument("--list-runs", action="store_true",
                   help="list the runs found in the partial file, then exit")
    p.add_argument("--dry-run", action="store_true",
                   help="show what would be sent (and the tail of the partial), then exit")
    args = p.parse_args()
    args.dir = args.dir.expanduser()
    return args


def make_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: environment variable ANTHROPIC_API_KEY is not set.")
    return Anthropic(api_key=api_key)


def resolve_prompt(args: argparse.Namespace) -> str:
    """Prompt priority: --prompt-file, then --prompt, then usr_msg."""
    if args.prompt_file:
        path = args.prompt_file.expanduser()
        if not path.is_absolute():
            path = args.dir / path
        if not path.is_file():
            sys.exit(f"ERROR: prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    return args.prompt if args.prompt else usr_msg


# ---- reading the partial reply --------------------------------------------

def list_runs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"^ Run: (.+?)\s+\|", text, flags=re.M)


def extract_partial(path: Path, stamp: str) -> str:
    """Return the reply text of the run whose header shows `stamp`."""
    if not path.is_file():
        sys.exit(f"ERROR: partial file not found: {path}")
    text = path.read_text(encoding="utf-8")

    i = text.find(f" Run: {stamp}")
    if i < 0:
        found = list_runs(path)
        sys.exit(f"ERROR: no run with stamp '{stamp}' in {path.name}.\n"
                 "       Runs found: " + (", ".join(found) or "(none)"))

    # The header ends with a line of "=" characters followed by a blank line.
    close = text.find(f"\n{BAR}\n", i)
    if close < 0:
        sys.exit("ERROR: could not find the end of the run header.")
    start = close + len(f"\n{BAR}\n")
    if text.startswith("\n", start):          # the blank line after the header
        start += 1

    # The reply ends where the next run header starts (or at end of file).
    end = text.find(f"\n\n{BAR}\n Run:", start)
    if end < 0:
        end = len(text)

    partial = text[start:end]
    if not partial.strip():
        sys.exit("ERROR: that run has no reply text -- nothing to resume.")
    return partial


# ---- rebuilding the original request ------------------------------------

def resolve_files(entries, doc_dir: Path) -> list[Path]:
    files, problems = [], []
    for name in entries:
        path = Path(str(name)).expanduser()
        if not path.is_absolute():
            path = doc_dir / path
        (files if path.is_file() else problems).append(path)
    if problems:
        sys.exit("ERROR: input file(s) not found:\n" +
                 "\n".join(f"  {p}" for p in problems))
    if not files:
        sys.exit("ERROR: no input files given.")
    return files


def build_content(files: list[Path], prompt: str) -> list[dict]:
    """Files first (as in the original run), prompt last. Files are sent
    inline, so nothing is uploaded and nothing needs cleaning up."""
    blocks: list[dict] = []
    for path in files:
        ext = path.suffix.lower()
        data = path.read_bytes()
        if ext == ".pdf":
            blocks.append({
                "type": "document", "title": path.name,
                "source": {"type": "base64", "media_type": "application/pdf",
                           "data": base64.standard_b64encode(data).decode("ascii")},
            })
        elif ext in IMAGE_TYPES:
            blocks.append({"type": "text", "text": f"Image: {path.name}"})
            blocks.append({
                "type": "image",
                "source": {"type": "base64", "media_type": IMAGE_TYPES[ext],
                           "data": base64.standard_b64encode(data).decode("ascii")},
            })
        else:
            try:
                content = data.decode("utf-8")
            except UnicodeDecodeError:
                sys.exit(f"ERROR: {path.name} is not UTF-8 text, PDF or image. "
                         "This resume script does not support sandbox (container) files.")
            blocks.append({
                "type": "document", "title": path.name,
                "source": {"type": "text", "media_type": "text/plain",
                           "data": content},
            })
    blocks.append({"type": "text", "text": prompt})
    return blocks


# ---- streaming with automatic resume --------------------------------------

def stream_continuation(client: Anthropic, prefix: list[dict], partial: str,
                        cont_file, new_chunks: list[str], *, model: str,
                        max_tokens: int, system: str | None) -> list[str]:
    """Stream the missing remainder to `cont_file`. Chunks are appended to the
    caller's `new_chunks` list as they arrive, so they survive any exception.
    On a connection failure, retries and resumes from partial + everything
    received so far. Also continues if the reply hits max_tokens again."""
    retries = 0
    passes = 0

    while True:
        assistant_text = partial + "".join(new_chunks)
        messages = prefix + [
            {"role": "assistant", "content": assistant_text},
            {"role": "user", "content": CONTINUE_PROMPT},
        ]
        request = dict(model=model, max_tokens=max_tokens, messages=messages)
        if system:
            request["system"] = system

        received_before = len(new_chunks)
        try:
            with client.messages.stream(**request) as stream:
                for text in stream.text_stream:
                    cont_file.write(text)
                    cont_file.flush()                 # nothing lost if the run dies
                    new_chunks.append(text)
                final = stream.get_final_message()
        except (anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            if len(new_chunks) > received_before:
                retries = 0                           # made progress, reset counter
            retries += 1
            if retries > MAX_RETRIES:
                print(f"Giving up after {MAX_RETRIES} consecutive failures: {e}")
                raise
            wait = RETRY_WAIT * retries
            print(f"Connection problem ({type(e).__name__}). Retry {retries}/"
                  f"{MAX_RETRIES} in {wait}s, resuming after "
                  f"{len(''.join(new_chunks)):,} new characters ...")
            time.sleep(wait)
            continue

        retries = 0
        print(f"Pass finished: stop_reason = {final.stop_reason}, "
              f"input tokens = {final.usage.input_tokens}, "
              f"output tokens = {final.usage.output_tokens}")

        if final.stop_reason != "max_tokens":
            return new_chunks

        passes += 1
        if passes > MAX_CONTINUATIONS:
            warning = ("\n\n[WARNING: reply still incomplete after all "
                       "continuation passes. Raise MAX_CONTINUATIONS.]\n")
            cont_file.write(warning)
            print(warning)
            return new_chunks
        print("Reply hit max_tokens -- requesting another continuation ...")


# =========================================================================
#  SECTION 4 -- MAIN
# =========================================================================

def main() -> int:
    args = parse_args()
    partial_path = args.dir / args.partial_file

    if args.list_runs:
        if not partial_path.is_file():
            sys.exit(f"ERROR: partial file not found: {partial_path}")
        print("Runs found in", partial_path.name)
        for stamp in list_runs(partial_path):
            print("  ", stamp)
        return 0

    partial = extract_partial(partial_path, args.run_stamp)
    files = resolve_files(args.files or INPUT_FILES, args.dir)
    prompt = resolve_prompt(args)

    print(f"\nRun to resume : {args.run_stamp}")
    print(f"Partial reply : {len(partial):,} characters "
          f"(~{len(partial) // 4:,} tokens, rough estimate)")
    print("Input files   : " + ", ".join(f.name for f in files))
    print("\n--- last 400 characters of the partial reply ---")
    print(partial[-400:])
    print("--- end of tail ---\n")

    if args.dry_run:
        print("Dry run -- nothing sent.")
        return 0

    client = make_client()
    prefix = [{"role": "user", "content": build_content(files, prompt)}]

    cont_path = args.dir / f"{OUTPUT_PREFIX}_continuation.txt"
    merged_path = args.dir / f"{OUTPUT_PREFIX}_merged.txt"
    new_chunks: list[str] = []

    try:
        with open(cont_path, "w", encoding="utf-8") as cont:
            stream_continuation(
                client, prefix, partial, cont, new_chunks,
                model=args.model, max_tokens=args.max_tokens,
                system=args.system)
        print(f"Continuation written to {cont_path}")
        return 0

    except anthropic.APIError as e:
        print(f"API ERROR: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted -- what was received so far was saved.", file=sys.stderr)
        return 130
    finally:
        # The streamed chunks are collected in the list as they arrive; the
        # continuation file is already on disk. Always write the merged file.
        merged_path.write_text(partial + "".join(new_chunks), encoding="utf-8")
        print(f"Merged file written to {merged_path} "
              f"({datetime.now():%H:%M:%S})")


if __name__ == "__main__":
    sys.exit(main())
