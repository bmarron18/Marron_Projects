#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : Nov 2026        (v1.x)
Revised : 10 Nov 2026     (v2.0)
Authors : bruce-vdb, claude-opus-5-5

-------------------------------------------------
A_Template_DataTableQuery_anthropic_v2.0.py
-------------------------------------------------
  * Send a source text file (plus an optional earlier, partial solution) to
    Claude and ask for ONE delimited row per item
  * Stream the reply to a raw text file (nothing is lost if the run dies)
  * Continue automatically if the reply is cut off by the output-token limit:
    the incomplete last row is discarded and Claude resumes after the last
    complete row
  * Parse, de-duplicate and sort the rows, then write three tables:
        <OUT_STEM>.md    Markdown table (code columns in backticks)
        <OUT_STEM>.txt   fixed-width, word-wrapped plain-text table
        <OUT_STEM>.csv   CSV (UTF-8 with BOM, opens cleanly in Excel)
  * Print / record the message ID (msg_...) of each pass, and the run time
  * Report clearly when the API's safety system refuses the request


---------------------------------------------------------------------------
QUICK START
---------------------------------------------------------------------------
  1. Check packages installed in venv (ai-apis) and perform updates

<<< bash
    cd ~/spyder-6/envs && source ./ai-apis/bin/activate &&
    pip list &&

    python3 -m pip install --upgrade pip &&
    pip install --upgrade anthropic &&
    deactivate

>>>

  2. Set your API key as ENV VARIABLE (once)
  3. Edit SECTION 1 below (files, columns, prompt)

  4. Run file (runs in Spyder within virtual environment, ai-apis)
      * To run file w/o CLI toggles
          a) Click on the green Run file icon in Toolbar or press F5

      * To run file w/ CLI toggles
          a) place copy of file on Desktop
          b) run file using IPython interpreter
runfile('/home/bruce-vdb/Desktop/A_Template_DataTableQuery_anthropic_v2.0.py', args='--show-prompt')

  Command-line examples (every option defaults to its SECTION 1 value):
     ./A_Template_...py                             # call the API, build the tables
     ./A_Template_...py --show-prompt               # preview the prompt, no API call
     ./A_Template_...py --parse-only                # rebuild tables from RAW_FILE, no API call
     ./A_Template_...py --parse-only old_raw.txt    # ...or from another saved reply
     ./A_Template_...py --src cmds.txt --partial earlier.txt -o my_table
     ./A_Template_...py --timestamp                 # my_table_20261110_143000.md / .txt / .csv
     ./A_Template_...py -m claude-opus-5-5 --max-tokens 32000 --max-continuations 5
     ./A_Template_...py --help


---------------------------------------------------------------------------
HOW A RUN WORKS
---------------------------------------------------------------------------
  prompt     SRC_FILE (required) and PARTIAL_FILE (optional) are embedded in
             the prompt as plain text.  The row-format instructions are built
             from COLUMNS / COLUMN_NOTES / DELIM, so changing the columns
             changes the prompt automatically.
  reply      Claude returns one row per line:
                 Category ¦ Command ¦ Tier ¦ Explanation ¦ Example
             A '+' in front of the Tier (e.g. +2) marks a row Claude ADDED
             that was not in the source material.  The parser moves that
             mark into a separate "Added" column.
  raw file   Every text chunk is written to RAW_FILE as it arrives.  Lines in
             square brackets ([message id: ...], [Runtime: ...]) are markers,
             not data; the parser ignores them.
  parsing    Each line is split on the FIRST len(COLUMNS)-1 delimiters only,
             so a stray delimiter in the last column cannot shift the row.
             Header / separator lines are skipped, a non-numeric Tier becomes
             DEFAULT_TIER, duplicates (by KEY_COL, or by the whole row when
             KEY_COL is blank) are merged keeping the first occurrence, and
             the rows are sorted by SORT_BY (case-insensitive).
  reuse      To use this script for another project edit only SECTION 1.


---------------------------------------------------------------------------
ID, RUN-TIME AND REFUSAL LINES
---------------------------------------------------------------------------
  * Message ID : printed to the console at the START of every pass, as soon
                 as the stream opens (so it is available even if the
                 connection drops).  It is also written to the raw file as
                     [message id: msg_... | pass N]
  * Run time   : the streaming call is timed.  The console prints
                 "Runtime: ..." and the raw file ends with
                     [Runtime: 4m 12s]
                 This is written even if the run fails or is interrupted.
  * Refusal    : if the API stops a pass with stop_reason == "refusal" (the
                 safety system declined to answer), a boxed message with the
                 message ID is printed to the console and a matching
                 "[REFUSED BY SAFETY SYSTEM ...]" line is written to the raw
                 file.  No tables are written and the script exits with
                 code 3.  The message ID is what to quote if you contact
                 Anthropic support.
  * Interrupt  : Ctrl+C stops the stream; the rows received so far are still
                 parsed and written to the three tables (exit code 130).


-----------
REVISIONS
-----------
Revised : v1.2 -- single streamed request; parse / sort / write .md .txt .csv
Revised : v2.0 -- reorganized to the AnalysisQuery v3.6 layout (SECTION 1-4,
                  argparse with SECTION 1 defaults, DOC_DIR-relative names);
                  automatic continuation passes with the cut-off tail dropped;
                  de-duplication by KEY_COL; case-insensitive sort; config
                  validation; message ID, run time and refusal reporting;
                  Ctrl+C still builds tables from the partial raw file;
                  blank PARTIAL_FILE no longer prints a bogus "not found";
                  prompt column notes generated from COLUMNS; .md backtick
                  escaping; .txt no longer breaks commands at hyphens;
                  --timestamp option so outputs are not clobbered
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from textwrap import wrap

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    sys.exit("The 'anthropic' package is not installed.  Run:  pip install --upgrade anthropic")


# =========================================================================
#  SECTION 1 -- CONFIGURATION / USER SETTINGS  (edit these)
# =========================================================================

# ---- Directory that holds the input files and receives the output ---------
DOC_DIR = Path.home() / "Desktop"

# ---- Input files (relative to DOC_DIR, or absolute) -----------------------
SRC_FILE = "gcloud-cli_Commands.txt"     # a) incomplete source list (required)
PARTIAL_FILE = ""                        # b) earlier partial solution (optional;
                                         #    blank = none, missing = skipped with a note)

# ---- Output ---------------------------------------------------------------
OUT_STEM = "gcloud_commands_table"       # -> .md, .txt, .csv
RAW_FILE = "raw_response.txt"            # streamed reply, parsed to build the tables
TIMESTAMP_OUTPUTS = False                # True = OUT_STEM_YYYYmmdd_HHMMSS.*  (never clobber)

# ---- Table definition -----------------------------------------------------
#   COLUMNS       columns Claude must return, in order.  Only the LAST column
#                 may safely contain extra DELIM characters.
#   COLUMN_NOTES  one-line guidance per column, inserted into the prompt
#   DELIM         separator; "¦" is safe for shell commands (unlike "|")
COLUMNS = ["Category", "Command", "Tier", "Explanation", "Example"]
COLUMN_NOTES = {
    "Category":    "a functional category (e.g. Config, Auth, IAM, Storage, "
                   "Compute, Networking, Logging).",
    "Tier":        "1 = used daily, 2 = common, 3 = occasional or rare.",
    "Explanation": "one sentence.",
    "Example":     "one realistic invocation.",
}
DELIM = "¦"

# ---- Post-processing ------------------------------------------------------
TIER_COL = "Tier"            # rank column; a '+' prefix = row added by Claude
                             # (blank = no tier handling, no Added column)
ADDED_COL = "Added"          # name of the flag column inserted after TIER_COL
ADDED_FLAG = "yes"           # value written in ADDED_COL for added rows
DEFAULT_TIER = 3             # used when the tier is missing / not a number
KEY_COL = "Command"          # de-duplicate on this column (blank = whole row)
SORT_BY = ["Tier", "Category", "Command"]        # blank list = arrival order
CODE_COLS = {"Command", "Example"}               # wrapped in backticks in .md
TXT_WIDTHS = {"Category": 12, "Command": 34, "Tier": 4, "Added": 5,
              "Explanation": 44, "Example": 52}  # .txt column widths
TXT_DEFAULT_WIDTH = 20                           # for columns not listed above


################
# PROMPT
#################
# ---- Use adjacent string literals = no stray spaces ----------
# Placeholders @@TEXT@@ / @@PARTIAL@@ are filled with str.replace (not
# .format) so braces inside your source files can never break the template.

    # Introduction when both files are given
intro_two_files = (
    "I am giving you two files.\n\n"
    "<commands_list>\n@@TEXT@@\n</commands_list>\n\n"
    "<partial_solution>\n@@PARTIAL@@\n</partial_solution>\n\n"
    "The first is an incomplete list of gcloud CLI commands. The second is an "
    "earlier, partial attempt to organize them. Use both as source material, "
    "and correct any errors.\n\n"
)

    # Introduction when only the source file is given
intro_one_file = (
    "Below is an incomplete list of gcloud CLI commands.\n\n"
    "<commands_list>\n@@TEXT@@\n</commands_list>\n\n"
    "Use it as source material, and correct any errors.\n\n"
)

    # What one row represents, and the task rules (the row FORMAT itself is
    # generated from COLUMNS / COLUMN_NOTES / DELIM -- see build_instructions)
item_name = "command"
task_rules = (
    "Cover every command in the provided material, merging duplicates into a "
    "single row. Then add common, useful commands that are missing, marking "
    "their Tier with a '+' prefix (e.g. +1). "
    "Output only the rows, with no header, preamble, or commentary."
)

    # System-level message, Optional (None = no system prompt)
sys_msg = (
    "You are an expert in the Google Cloud gcloud CLI. "
    "Output only the requested delimited rows, with no preamble, header, or commentary."
)

# ---- Model / output size ---------------------------------------------------
MODEL = "claude-opus-5-5"   # API model string uses hyphens, not dots
MAX_TOKENS = 64000          # lower this if the API rejects it for your model
MAX_CONTINUATIONS = 3       # extra passes if the reply is cut off
API_TIMEOUT = 1800.0        # seconds; long tables take a while to stream


# =========================================================================
#  SECTION 2 -- FIXED SETTINGS  (normally no need to edit)
# =========================================================================

EXIT_REFUSED = 3                            # exit code when the API refuses

SEPARATOR_CHARS = set("-:| ")               # a first cell made only of these = table rule

CONTINUE_PROMPT = (
    "Your previous reply was cut off by the output-token limit. "
    "The last complete row you produced was:\n@@LAST@@\n"
    "Continue with the row that follows it, in exactly the same format -- "
    "no preamble, no header, no repeated rows."
)


# =========================================================================
#  SECTION 3 -- HELPER FUNCTIONS
# =========================================================================

# ---- command line --------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Command-line options; every option defaults to the SECTION 1 value."""
    p = argparse.ArgumentParser(
        description="Send a source text file + instructions to Claude, stream "
                    "back one delimited row per item, and build .md / .txt / "
                    ".csv tables.",
    )
    p.add_argument("-d", "--dir", type=Path, default=DOC_DIR,
                   help=f"folder for input/output files (default: {DOC_DIR})")
    p.add_argument("--src", default=SRC_FILE,
                   help=f"source text file, required (default: {SRC_FILE})")
    p.add_argument("--partial", default=PARTIAL_FILE,
                   help="earlier partial solution, optional "
                        f"(default: {PARTIAL_FILE or 'none'})")
    p.add_argument("-o", "--out-stem", default=OUT_STEM,
                   help=f"output stem for .md/.txt/.csv (default: {OUT_STEM})")
    p.add_argument("--raw", default=RAW_FILE,
                   help=f"file that receives the streamed reply (default: {RAW_FILE})")
    p.add_argument("--timestamp", action="store_true", default=TIMESTAMP_OUTPUTS,
                   help="append _YYYYmmdd_HHMMSS to the output stem")
    p.add_argument("-s", "--system", default=sys_msg,
                   help="optional system prompt")
    p.add_argument("-m", "--model", default=MODEL,
                   help=f"model id (default: {MODEL})")
    p.add_argument("--max-tokens", type=int, default=MAX_TOKENS,
                   help=f"max output tokens per pass (default: {MAX_TOKENS})")
    p.add_argument("--max-continuations", type=int, default=MAX_CONTINUATIONS,
                   help=f"extra passes if cut off (default: {MAX_CONTINUATIONS})")
    p.add_argument("--parse-only", nargs="?", const="", default=None, metavar="RAW_FILE",
                   help="skip the API call and rebuild the tables from a saved "
                        "reply (default file: --raw)")
    p.add_argument("--show-prompt", action="store_true",
                   help="print the assembled prompt and exit (no API call)")
    args = p.parse_args()
    args.dir = args.dir.expanduser()
    return args


def resolve_path(name: str, doc_dir: Path) -> Path:
    """Relative names live in doc_dir; absolute paths are used as-is."""
    path = Path(name).expanduser()
    return path if path.is_absolute() else doc_dir / path


def check_config() -> None:
    """Fail early on SECTION 1 mistakes that would otherwise surface mid-run."""
    problems = []
    if len(DELIM) != 1:
        problems.append(f"DELIM must be a single character, got {DELIM!r}")
    if DELIM == "|":
        problems.append("DELIM '|' clashes with Markdown tables and shell pipes")
    if len(COLUMNS) < 2:
        problems.append("COLUMNS needs at least two entries")
    if len(set(COLUMNS)) != len(COLUMNS):
        problems.append("COLUMNS contains a duplicate name")
    if TIER_COL and TIER_COL not in COLUMNS:
        problems.append(f"TIER_COL {TIER_COL!r} is not in COLUMNS")
    if TIER_COL and ADDED_COL in COLUMNS:
        problems.append(f"ADDED_COL {ADDED_COL!r} clashes with a COLUMNS entry")
    if KEY_COL and KEY_COL not in COLUMNS:
        problems.append(f"KEY_COL {KEY_COL!r} is not in COLUMNS")
    header = output_header()
    for col in SORT_BY:
        if col not in header:
            problems.append(f"SORT_BY column {col!r} is not in the output header {header}")
    for col in CODE_COLS:
        if col not in header:
            problems.append(f"CODE_COLS column {col!r} is not in the output header")
    if problems:
        sys.exit("ERROR: problem(s) in SECTION 1 settings:\n  " + "\n  ".join(problems))


# ---- client / prompt -----------------------------------------------------

def make_client() -> Anthropic:
    """Create the API client (key read from the ANTHROPIC_API_KEY env var)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: environment variable ANTHROPIC_API_KEY is not set.")
    return Anthropic(api_key=api_key, timeout=API_TIMEOUT)


def read_sources(args: argparse.Namespace) -> tuple[str, str | None]:
    """Return (source text, partial text or None)."""
    src = resolve_path(args.src, args.dir)
    if not src.is_file():
        sys.exit(f"ERROR: source file not found: {src}")
    text = src.read_text(encoding="utf-8")
    if not text.strip():
        sys.exit(f"ERROR: source file is empty: {src}")

    partial = None
    if args.partial.strip():
        p = resolve_path(args.partial, args.dir)
        if p.is_file():
            partial = p.read_text(encoding="utf-8")
            if not partial.strip():
                print(f"Note: {p.name} is empty; continuing without it.")
                partial = None
        else:
            print(f"Note: {p} not found; continuing without it.")
    return text, partial


def build_instructions() -> str:
    """Row-format instructions generated from COLUMNS / COLUMN_NOTES / DELIM."""
    lines = [
        f"Produce one row per {item_name}, one per line, using the character "
        f"{DELIM} as the separator, in exactly this format:",
        f" {DELIM} ".join(COLUMNS),
    ]
    for col in COLUMNS:
        if col in COLUMN_NOTES:
            lines.append(f"- {col}: {COLUMN_NOTES[col]}")
    lines.append(f"Do not use the {DELIM} character inside any field.")
    lines.append("")
    lines.append(task_rules)
    return "\n".join(lines)


def build_prompt(text: str, partial: str | None) -> str:
    """Introduction (one or two files) + generated instructions."""
    intro = intro_two_files if partial else intro_one_file
    prompt = intro.replace("@@TEXT@@", text)
    if partial:
        prompt = prompt.replace("@@PARTIAL@@", partial)
    return prompt + build_instructions()


# ---- run time ------------------------------------------------------------

def fmt_elapsed(seconds: float) -> str:
    """Seconds -> 'Hh MMm SSs' (or 'Mm SSs' / 'Ss')."""
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


# ---- raw file ------------------------------------------------------------

class RawLog:
    """Streams text to the raw file immediately (nothing lost if the run
    dies) while keeping a copy, so the incomplete tail of a cut-off pass can
    be removed from the file before the next pass continues."""

    def __init__(self, fh):
        self.fh = fh
        self.parts: list[str] = []

    def write(self, s: str) -> None:
        self.parts.append(s)
        self.fh.write(s)
        self.fh.flush()

    def text(self) -> str:
        return "".join(self.parts)

    def drop_tail(self, n_chars: int) -> None:
        """Remove the last n_chars characters from the file and the copy."""
        if n_chars <= 0:
            return
        kept = self.text()[:-n_chars]
        self.parts = [kept]
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write(kept)
        self.fh.flush()


# ---- refusal reporting ---------------------------------------------------

def report_refusal(log: RawLog, message, msg_id: str, pass_no: int, model: str) -> None:
    """Tell the user, on the console and in the raw file, that the API's
    safety system refused (stop_reason == 'refusal'). Includes the message ID."""
    bar = "=" * 70
    details = getattr(message, "stop_details", None)
    detail_line = f" Details      : {details}\n" if details else ""
    out_tokens = getattr(message.usage, "output_tokens", "?")

    print(
        f"\n{bar}\n"
        f" REFUSED BY SAFETY SYSTEM\n"
        f"{bar}\n"
        f" The API stopped this request (stop_reason = refusal).\n"
        f" This is NOT a crash or a connection problem.\n"
        f"\n"
        f" Message ID   : {msg_id}\n"
        f" Pass         : {pass_no}\n"
        f" Model        : {model}\n"
        f" Output tokens: {out_tokens}\n"
        f"{detail_line}"
        f"\n"
        f" What to try:\n"
        f"   1. Run with another model, e.g.  -m claude-opus-5-5\n"
        f"   2. Trim the source file to find which part triggers it\n"
        f"   3. If you believe it is a false positive, quote the message ID to\n"
        f"      Anthropic support\n"
        f"{bar}\n"
    )
    if not log.text().endswith("\n"):
        log.write("\n")
    log.write(
        f"[REFUSED BY SAFETY SYSTEM -- stop_reason = refusal | "
        f"pass {pass_no} | model {model} | message id: {msg_id}]\n"
    )


# ---- API call ------------------------------------------------------------

def run_query(client: Anthropic, prompt: str, log: RawLog, *, model: str,
              max_tokens: int, max_continuations: int,
              system: str | None) -> str | None:
    """Stream the reply into `log`. If a pass is cut off (max_tokens) the
    incomplete last line is dropped and Claude is asked to continue after
    the last complete row. Returns the final stop_reason."""
    messages: list[dict] = [{"role": "user", "content": prompt}]
    stop_reason: str | None = None

    for attempt in range(max_continuations + 1):
        request = dict(model=model, max_tokens=max_tokens, messages=messages)
        if system:
            request["system"] = system

        msg_id = "unknown"
        chunks: list[str] = []
        with client.messages.stream(**request) as stream:
            for event in stream:
                if event.type == "message_start":
                    # msg_... id, available as soon as the stream opens
                    msg_id = event.message.id
                    print(f"Pass {attempt + 1}: message id = {msg_id}")
                    if not log.text().endswith("\n"):
                        log.write("\n")
                    log.write(f"[message id: {msg_id} | pass {attempt + 1}]\n")
                elif event.type == "content_block_delta" and \
                        event.delta.type == "text_delta":
                    chunks.append(event.delta.text)
                    log.write(event.delta.text)       # nothing lost if the run dies
            final = stream.get_final_message()

        text = "".join(chunks)
        stop_reason = final.stop_reason
        print(f"Pass {attempt + 1}: stop_reason = {stop_reason}, "
              f"input tokens = {final.usage.input_tokens}, "
              f"output tokens = {final.usage.output_tokens}")

        if stop_reason == "refusal":                  # safety system said no
            report_refusal(log, final, msg_id if msg_id != "unknown" else final.id,
                           attempt + 1, model)
            return stop_reason

        if stop_reason != "max_tokens":
            return stop_reason                        # finished normally

        # ---- cut off: discard the incomplete last line ------------------
        cut = text.rfind("\n")
        kept, dropped = (text[:cut + 1], text[cut + 1:]) if cut >= 0 else ("", text)
        if dropped:
            log.drop_tail(len(dropped))
            print(f"Pass {attempt + 1}: dropped incomplete tail "
                  f"({len(dropped)} chars): {dropped[:60]!r}...")

        if attempt == max_continuations:              # out of retries
            warning = ("\n[WARNING: reply still incomplete (stop_reason = "
                       "max_tokens) after all continuation passes. Raise "
                       "MAX_TOKENS or MAX_CONTINUATIONS.]\n")
            log.write(warning)
            print(warning)
            return stop_reason

        if not kept.strip():
            print("Reply was empty -- cannot continue.")
            return stop_reason

        last_row = kept.rstrip("\n").rsplit("\n", 1)[-1]
        messages.append({"role": "assistant", "content": kept.rstrip()})
        messages.append({"role": "user",
                         "content": CONTINUE_PROMPT.replace("@@LAST@@", last_row)})
        print("Reply hit max_tokens -- requesting continuation...")

    return stop_reason


# ---- parsing -------------------------------------------------------------

def output_header() -> list[str]:
    """COLUMNS with the Added flag column inserted after the tier column."""
    header = list(COLUMNS)
    if TIER_COL:
        header.insert(COLUMNS.index(TIER_COL) + 1, ADDED_COL)
    return header


def norm(value) -> str:
    """Normalized form of a cell for de-duplication."""
    return " ".join(str(value).split()).lower()


def row_key(cells: list, header: list[str]) -> tuple:
    """De-duplication key: KEY_COL, or the whole row (minus Added) if blank."""
    if KEY_COL:
        return (norm(cells[header.index(KEY_COL)]),)
    return tuple(norm(c) for h, c in zip(header, cells) if h != ADDED_COL)


def sort_key(cells: list, idx: list[int]) -> tuple:
    """Ints sort numerically, strings case-insensitively."""
    return tuple(c if isinstance(c, int) else str(c).lower()
                 for c in (cells[i] for i in idx))


def parse(raw: str) -> tuple[list[str], list[list], dict]:
    """Return (header, rows, stats). Each line is split on the first
    len(COLUMNS)-1 delimiters only; markers, headers and separators are
    skipped; duplicates are merged; rows are sorted by SORT_BY."""
    n = len(COLUMNS)
    header = output_header()
    t = COLUMNS.index(TIER_COL) if TIER_COL else -1
    rows: list[list] = []
    seen: set = set()
    stats = dict(malformed=0, bad_tier=0, duplicates=0, added=0)

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.count(DELIM) < n - 1:
            if DELIM in line:                         # looks like a broken row
                stats["malformed"] += 1
            continue                                  # marker / prose line
        cells = [c.strip() for c in line.split(DELIM, n - 1)]
        if not any(cells):
            continue                                  # blank row
        first = cells[0]
        if first.lower() == COLUMNS[0].lower() or (first and set(first) <= SEPARATOR_CHARS):
            continue                                  # header or separator line

        added = ""
        if TIER_COL:
            tier_raw = cells[t]
            added = ADDED_FLAG if tier_raw.startswith("+") else ""
            tier_raw = tier_raw.lstrip("+").strip()
            if tier_raw.isdigit():
                cells[t] = int(tier_raw)
            else:
                cells[t] = DEFAULT_TIER
                stats["bad_tier"] += 1
            cells.insert(t + 1, added)

        key = row_key(cells, header)
        if key in seen:
            stats["duplicates"] += 1
            continue
        seen.add(key)
        if added:
            stats["added"] += 1
        rows.append(cells)

    if SORT_BY:
        idx = [header.index(c) for c in SORT_BY]
        rows.sort(key=lambda r: sort_key(r, idx))
    return header, rows, stats


# ---- writers -------------------------------------------------------------

def md_cell(value, is_code: bool) -> str:
    """Escape pipes; wrap code cells in backticks (double if the text has one)."""
    text = str(value).replace("|", "\\|")
    if not (is_code and text):
        return text
    return f"`` {text} ``" if "`" in text else f"`{text}`"


def write_md(header: list[str], rows: list[list], path: Path) -> None:
    code = {header.index(c) for c in CODE_COLS if c in header}
    with open(path, "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "---|" * len(header) + "\n")
        for r in rows:
            f.write("| " + " | ".join(md_cell(c, i in code) for i, c in enumerate(r)) + " |\n")


def write_txt(header: list[str], rows: list[list], path: Path) -> None:
    widths = [TXT_WIDTHS.get(h, TXT_DEFAULT_WIDTH) for h in header]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells) -> str:
        wrapped = [wrap(str(c), w, break_long_words=True, break_on_hyphens=False) or [""]
                   for c, w in zip(cells, widths)]
        out = []
        for parts in zip_longest(*wrapped, fillvalue=""):
            out.append("| " + " | ".join(p.ljust(w) for p, w in zip(parts, widths)) + " |")
        return "\n".join(out)

    with open(path, "w", encoding="utf-8") as f:
        f.write(sep + "\n" + line(header) + "\n" + sep + "\n")
        for r in rows:
            f.write(line(r) + "\n" + sep + "\n")


def write_csv(header: list[str], rows: list[list], path: Path) -> None:
    # utf-8-sig so Excel opens accents/symbols correctly
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def build_outputs(raw: str, stem: Path) -> int:
    """Parse the raw reply and write .md / .txt / .csv. Returns the row count."""
    header, rows, stats = parse(raw)
    if stats["bad_tier"]:
        print(f"Note: {stats['bad_tier']} row(s) had a non-numeric tier "
              f"(defaulted to {DEFAULT_TIER}).")
    if stats["malformed"]:
        print(f"Note: {stats['malformed']} line(s) had too few delimiters and were skipped.")
    if stats["duplicates"]:
        print(f"Note: {stats['duplicates']} duplicate row(s) merged "
              f"(key: {KEY_COL or 'whole row'}).")
    if not rows:
        print("No rows found -- no tables written.")
        return 0

    write_md(header, rows, stem.with_suffix(".md"))
    write_txt(header, rows, stem.with_suffix(".txt"))
    write_csv(header, rows, stem.with_suffix(".csv"))
    print(f"{len(rows)} rows ({stats['added']} added by Claude) written to "
          f"{stem}.md / .txt / .csv")
    return len(rows)


# =========================================================================
#  SECTION 4 -- MAIN
# =========================================================================

def main() -> int:
    args = parse_args()
    check_config()

    stem = resolve_path(args.out_stem, args.dir)
    if args.timestamp:
        stem = stem.with_name(f"{stem.name}_{datetime.now():%Y%m%d_%H%M%S}")
    raw_path = resolve_path(args.raw, args.dir)

    # ---- rebuild tables from a saved reply, no API call ------------------
    if args.parse_only is not None:
        src = resolve_path(args.parse_only, args.dir) if args.parse_only else raw_path
        if not src.is_file():
            sys.exit(f"ERROR: raw file not found: {src}")
        build_outputs(src.read_text(encoding="utf-8"), stem)
        return 0

    # ---- assemble the prompt --------------------------------------------
    text, partial = read_sources(args)
    prompt = build_prompt(text, partial)
    if args.show_prompt:
        print(prompt)
        return 0

    client = make_client()
    exit_code = 0
    stop_reason: str | None = None

    try:
        with open(raw_path, "w", encoding="utf-8") as fh:
            log = RawLog(fh)
            log.write(
                f"[Run: {datetime.now():%Y-%m-%d %H:%M:%S} | Model: {args.model} | "
                f"Source: {args.src}"
                + (f" | Partial: {args.partial}" if partial else "")
                + "]\n"
            )
            t0 = time.perf_counter()                  # times the streaming call only
            try:
                stop_reason = run_query(
                    client, prompt, log,
                    model=args.model,
                    max_tokens=args.max_tokens,
                    max_continuations=args.max_continuations,
                    system=args.system,
                )
            finally:
                # runs on success, API error, dropped connection and Ctrl+C
                elapsed = fmt_elapsed(time.perf_counter() - t0)
                if not log.text().endswith("\n"):
                    log.write("\n")
                log.write(f"[Runtime: {elapsed}]\n")
                print(f"Runtime: {elapsed}")
        print(f"Raw reply written to {raw_path}")

    except anthropic.APIError as e:
        print(f"API ERROR: {e}", file=sys.stderr)
        exit_code = 1
    except KeyboardInterrupt:
        print("\nInterrupted -- building tables from the partial reply.", file=sys.stderr)
        exit_code = 130

    if stop_reason == "refusal":
        return EXIT_REFUSED                           # nothing to tabulate

    if raw_path.is_file():
        build_outputs(raw_path.read_text(encoding="utf-8"), stem)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

