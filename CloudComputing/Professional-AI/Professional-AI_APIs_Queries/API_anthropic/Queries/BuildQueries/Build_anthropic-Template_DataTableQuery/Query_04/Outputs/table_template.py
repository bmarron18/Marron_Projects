#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template: source text -> Claude -> delimited rows -> .md / .txt / .csv

Usage:
    python table_template.py                    # call the API, then build outputs
    python table_template.py --parse-only raw_response.txt   # rebuild outputs, no API call

To reuse for another project, edit only the CONFIG block.
"""

import argparse
import csv
import sys
from itertools import zip_longest
from pathlib import Path
from textwrap import wrap

# ============================== CONFIG ==============================
MODEL = "claude-opus-5-5"            # API model string uses hyphens, not dots
MAX_TOKENS = 64000
SRC = "gcloud-cli_Commands.txt"
OUT_STEM = "gcloud_commands_table"   # -> .md, .txt, .csv
RAW_FILE = "raw_response.txt"

# Columns Claude must return, in order. Last column may safely contain DELIM-free text only.
COLUMNS = ["Category", "Command", "Tier", "Explanation", "Example"]
DELIM = "¦"                          # unlikely to appear in shell commands (unlike "|")

# Post-processing
TIER_COL = "Tier"                    # column holding a rank; a "+" prefix = added by Claude
SORT_BY = ["Tier", "Category", "Command"]
CODE_COLS = {"Command", "Example"}   # wrapped in backticks in .md
TXT_WIDTHS = {"Category": 12, "Command": 34, "Tier": 4, "Added": 5,
              "Explanation": 44, "Example": 52}

SYSTEM = (
    "You are an expert in the Google Cloud gcloud CLI. "
    "Output only the requested delimited rows, with no preamble, header, or commentary."
)

USER_TMPL = (
    "Below is a partial, semi-organized list of gcloud CLI commands.\n\n"
    "<commands>\n{text}\n</commands>\n\n"
    "Produce one row per command, one per line, in exactly this format, "
    "using the character " + DELIM + " as the separator:\n"
    + f" {DELIM} ".join(COLUMNS) + "\n"
    "- Category: a functional category (e.g. Compute, IAM, Storage, Networking).\n"
    "- Tier: 1 = used daily/very common, 2 = common, 3 = occasional/rare.\n"
    "- Explanation: one sentence. Example: one realistic invocation.\n"
    "Cover every command in the list. Then add common, useful commands that are "
    "missing from the list, marking their Tier with a '+' prefix (e.g. +1)."
)
# ====================================================================


def call_api(text: str) -> str:
    """Single streamed request. Streaming is required for large max_tokens and
    means partial output is saved even if the connection dies midway."""
    import anthropic

    client = anthropic.Anthropic(timeout=1800.0)
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=[{"role": "user", "content": USER_TMPL.format(text=text)}],
    ) as stream, open(RAW_FILE, "w", encoding="utf-8") as raw_out:
        for chunk in stream.text_stream:
            raw_out.write(chunk)
            raw_out.flush()
        final = stream.get_final_message()
    print("stop_reason:", final.stop_reason, "| usage:", final.usage)
    if final.stop_reason == "max_tokens":
        print("WARNING: output was truncated; last row may be incomplete.", file=sys.stderr)
    return Path(RAW_FILE).read_text(encoding="utf-8")


def parse(raw: str):
    """Return (header, rows). Splits on the first len(COLUMNS)-1 delimiters only."""
    # insert 'Added' flag column right after the tier column
    t = COLUMNS.index(TIER_COL)
    header = COLUMNS[: t + 1] + ["Added"] + COLUMNS[t + 1:]

    rows, skipped = [], 0
    for line in raw.splitlines():
        if line.count(DELIM) < len(COLUMNS) - 1:
            continue
        cells = [c.strip() for c in line.split(DELIM, len(COLUMNS) - 1)]
        if cells[0].lower() == COLUMNS[0].lower() or set(cells[0]) <= set("-: "):
            continue  # header or separator line
        tier_raw = cells[t]
        added = "yes" if tier_raw.startswith("+") else ""
        tier_raw = tier_raw.lstrip("+").strip()
        cells[t] = int(tier_raw) if tier_raw.isdigit() else 3
        if not tier_raw.isdigit():
            skipped += 1
        rows.append(cells[: t + 1] + [added] + cells[t + 1:])
    if skipped:
        print(f"Note: {skipped} rows had a non-numeric tier (defaulted to 3).")

    idx = [header.index(c) for c in SORT_BY]
    rows.sort(key=lambda r: tuple(r[i] for i in idx))
    return header, rows


def write_md(header, rows, path):
    code = {header.index(c) for c in CODE_COLS if c in header}
    with open(path, "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "---|" * len(header) + "\n")
        for r in rows:
            cells = []
            for i, c in enumerate(r):
                c = str(c).replace("|", "\\|")
                cells.append(f"`{c}`" if i in code and c else c)
            f.write("| " + " | ".join(cells) + " |\n")


def write_txt(header, rows, path):
    widths = [TXT_WIDTHS.get(h, 20) for h in header]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells):
        wrapped = [wrap(str(c), w, break_long_words=True) or [""] for c, w in zip(cells, widths)]
        out = []
        for parts in zip_longest(*wrapped, fillvalue=""):
            out.append("| " + " | ".join(p.ljust(w) for p, w in zip(parts, widths)) + " |")
        return "\n".join(out)

    with open(path, "w", encoding="utf-8") as f:
        f.write(sep + "\n" + line(header) + "\n" + sep + "\n")
        for r in rows:
            f.write(line(r) + "\n" + sep + "\n")


def write_csv(header, rows, path):
    # utf-8-sig so Excel opens accents/symbols correctly
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parse-only", metavar="RAW_FILE",
                    help="skip the API call and rebuild outputs from a saved response")
    args = ap.parse_args()

    if args.parse_only:
        raw = Path(args.parse_only).read_text(encoding="utf-8")
    else:
        raw = call_api(Path(SRC).read_text(encoding="utf-8"))

    header, rows = parse(raw)
    write_md(header, rows, f"{OUT_STEM}.md")
    write_txt(header, rows, f"{OUT_STEM}.txt")
    write_csv(header, rows, f"{OUT_STEM}.csv")
    print(f"{len(rows)} rows written to {OUT_STEM}.md / .txt / .csv")


if __name__ == "__main__":
    main()
