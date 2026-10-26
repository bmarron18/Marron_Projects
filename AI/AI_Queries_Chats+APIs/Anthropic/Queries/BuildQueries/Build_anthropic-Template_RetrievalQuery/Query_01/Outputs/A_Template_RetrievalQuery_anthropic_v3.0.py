#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 18:34:11 2026
@author: bruce-vdb, claude-opus-5.5


--------------------------------------------
A_Template_RetrievalQuery_anthropic_v3.0.py
--------------------------------------------
Safely recover completed work from an Anthropic Message Batch.
Downloading batch results does NOT consume tokens; re-running this is free.


----------
FUNCTIONS
------------
  1. Checks the batch status (and request counts) via the Anthropic API.
  2. Optionally polls until the batch ends (--wait), or cancels a running batch
     so that everything already completed is released immediately (--cancel).
  3. Streams every result to disk, one JSON object per line, flushing after
     each row. Files are written as *.part and renamed only on success, so an
     interrupted run never clobbers a good export and never loses received rows.
  4. Extracts all generated text and code into easy-to-use formats.
  5. Lists exactly which custom_ids still need to be (re)submitted, so you never
     pay twice for work that already succeeded.



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
  
  2. Set your API key as ENV VARAIBLE (once)
  3. Obtain Batch ID 
  4. Select toggle options
    * Use `--wait`** if you want the whole batch to finish. Batches that haven't finished within 
      24 hours expire, and expired items are not billed.
      
    * Use `--cancel`** if you want the completed work right away. Cancelling is irreversible. Requests 
      already in flight may still complete and be billed, but nothing is billed twice.
      
  
  5. Run file (runs in Spyder within virtual environment, ai-apis)
 
      * To run file w/ CLI toggles
          a) place copy of file on Desktop
          b) run file using IPython interpreter

       --list   # find your batch ID
runfile('/home/bruce-vdb/Desktop/A_Template_RetrievalQuery_anthropic_v3.0.py', args='--list')

-----------------------------------------------------------------------
PASTE BATCH ID HERE:      Batch ID: msgbatch_01URBjcz9SGSZKNVYSFFzHat
-------------------------------------------------------------------------

        msgbatch_XXXX    # export (batch already ended)
runfile("/home/bruce-vdb/Desktop/A_Template_RetrievalQuery_anthropic_v3.0.py", "msgbatch_01URBjcz9SGSZKNVYSFFzHat")

        msgbatch_XXXX --wait      # poll until done, then export
runfile('/home/bruce-vdb/Desktop/A_Template_RetrievalQuery_anthropic_v3.0.py','msgbatch_XXXX', args='--wait')

        msgbatch_XXXX --cancel    # stop now and keep completed work
runfile('/home/bruce-vdb/Desktop/A_Template_RetrievalQuery_anthropic_v3.0.py', 'msgbatch_XXXX', args='--cancel')

    6. Exit codes: 0 ok | 1 error | 2 batch not ended yet | 130 interrupted. 
    7. Build a new batch containing only the IDs in `resubmit_custom_ids.txt`.



-----------------------------------------------------------
OUTPUTS 
(default: ./batch_exports/<batch_id>_<UTC timestamp>/)
------------------------------------------------------------
  raw_results.jsonl           every result, full fidelity (one row per item)
  successful_results.jsonl    raw rows for succeeded items
  failed_results.jsonl        raw rows for errored / canceled / expired items
  text_export.jsonl           clean rows: custom_id, model, stop_reason,
                              truncated flag, text, code_blocks, tool_calls, usage
  combined_output.md          human-readable document of all generated output
  code/<custom_id>/block_NN.<ext>   each fenced code block as its own file
  resubmit_custom_ids.txt     items that did not finish (safe to resubmit)
  needs_fix_custom_ids.txt    items that failed due to invalid requests
  truncated_custom_ids.txt    succeeded items cut off by max_tokens
  summary.json                batch metadata and counts

"""




from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    sys.exit("ERROR: The 'anthropic' package is not installed.\n"
             "       Install it with:  pip install --upgrade anthropic")


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
FENCE_RE = re.compile(r"```[ \t]*([^\n`]*)\n(.*?)```", re.DOTALL)

LANG_EXT = {
    "python": "py", "py": "py", "python3": "py",
    "javascript": "js", "js": "js", "typescript": "ts", "ts": "ts",
    "tsx": "tsx", "jsx": "jsx", "json": "json", "yaml": "yaml", "yml": "yml",
    "bash": "sh", "sh": "sh", "shell": "sh", "zsh": "sh", "powershell": "ps1",
    "html": "html", "css": "css", "sql": "sql", "r": "R", "julia": "jl",
    "java": "java", "kotlin": "kt", "scala": "scala", "go": "go", "rust": "rs",
    "c": "c", "cpp": "cpp", "c++": "cpp", "h": "h", "hpp": "hpp",
    "csharp": "cs", "c#": "cs", "cs": "cs", "ruby": "rb", "php": "php",
    "swift": "swift", "matlab": "m", "latex": "tex", "tex": "tex",
    "markdown": "md", "md": "md", "xml": "xml", "toml": "toml",
    "ini": "ini", "dockerfile": "Dockerfile", "makefile": "mk",
}

# Error types that will fail again unless the request itself is fixed.
NON_RETRYABLE_ERRORS = {"invalid_request_error", "authentication_error",
                        "permission_error", "not_found_error"}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def log(msg: str = "") -> None:
    print(msg, flush=True)


def to_jsonable(obj: Any) -> Any:
    """Convert SDK (pydantic) objects to plain JSON-safe Python structures."""
    if obj is None or isinstance(obj, (str, int, float, bool, list, dict)):
        return obj
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(mode="json")
        except TypeError:
            pass
    if hasattr(obj, "to_json"):
        return json.loads(obj.to_json())
    return str(obj)


def safe_name(text: str, max_len: int = 100) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._")
    return (cleaned or "item")[:max_len]


def describe(batch: Any) -> str:
    c = batch.request_counts
    total = c.processing + c.succeeded + c.errored + c.canceled + c.expired
    return (f"status={batch.processing_status} | total={total} "
            f"processing={c.processing} succeeded={c.succeeded} "
            f"errored={c.errored} canceled={c.canceled} expired={c.expired}")


class SafeFile:
    """Streams to '<name>.part', flushing every write; renamed on commit()."""

    def __init__(self, path: Path):
        self.final = path
        self.tmp = path.with_name(path.name + ".part")
        self.fh = open(self.tmp, "w", encoding="utf-8", newline="\n")
        self.rows = 0

    def write_json(self, obj: Any) -> None:
        self.fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self.fh.flush()
        self.rows += 1

    def write(self, text: str) -> None:
        self.fh.write(text)
        self.fh.flush()

    def commit(self) -> None:
        self.fh.flush()
        os.fsync(self.fh.fileno())
        self.fh.close()
        os.replace(self.tmp, self.final)

    def abort(self) -> None:
        # Keep the .part file: it holds every row received before the failure.
        if not self.fh.closed:
            self.fh.flush()
            self.fh.close()


# --------------------------------------------------------------------------- #
# Batch status / polling / cancel
# --------------------------------------------------------------------------- #
def list_batches(client: Anthropic, limit: int = 20) -> None:
    log(f"Most recent batches (up to {limit}):\n")
    for i, b in enumerate(client.messages.batches.list(limit=limit)):
        if i >= limit:
            break
        created = getattr(b, "created_at", "")
        log(f"  {b.id}  created={created}  {describe(b)}")


def wait_until_ended(client: Anthropic, batch_id: str,
                     interval: float, timeout: float) -> Any:
    start = time.monotonic()
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        log(f"  [{datetime.now():%H:%M:%S}] {describe(batch)}")
        if batch.processing_status == "ended":
            return batch
        if timeout and (time.monotonic() - start) > timeout:
            raise TimeoutError(
                f"Batch did not end within {timeout:.0f}s. It is still running "
                "server-side; re-run this script later (nothing is lost).")
        time.sleep(interval)


def confirm(prompt: str) -> bool:
    try:
        return input(f"{prompt} [y/N]: ").strip().lower() in {"y", "yes"}
    except EOFError:
        return False


# --------------------------------------------------------------------------- #
# Content extraction
# --------------------------------------------------------------------------- #
def extract_message(message: Any) -> dict:
    texts, thinking, tool_calls, other = [], [], [], []
    for block in (getattr(message, "content", None) or []):
        btype = getattr(block, "type", None)
        if btype == "text":
            texts.append(block.text)
        elif btype == "thinking":
            thinking.append(getattr(block, "thinking", ""))
        elif btype == "tool_use":
            tool_calls.append({"id": block.id, "name": block.name,
                               "input": to_jsonable(block.input)})
        else:
            other.append(to_jsonable(block))

    text = "\n\n".join(texts)
    code_blocks = [{"language": (lang.strip().split() or ["text"])[0].lower(),
                    "code": code}
                   for lang, code in FENCE_RE.findall(text)]
    return {
        "text": text,
        "code_blocks": code_blocks,
        "tool_calls": tool_calls,
        "thinking": "\n\n".join(thinking),
        "other_blocks": other,
    }


def save_code_blocks(code_dir: Path, custom_id: str,
                     code_blocks: list[dict]) -> list[str]:
    saved = []
    if not code_blocks:
        return saved
    item_dir = code_dir / safe_name(custom_id)
    item_dir.mkdir(parents=True, exist_ok=True)
    for n, blk in enumerate(code_blocks, start=1):
        ext = LANG_EXT.get(blk["language"], "txt")
        path = item_dir / f"block_{n:02d}.{ext}"
        path.write_text(blk["code"], encoding="utf-8")
        saved.append(str(path))
    return saved


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #
def export_results(client: Anthropic, batch: Any, out_dir: Path,
                   write_code_files: bool, md_thinking: bool) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    code_dir = out_dir / "code"

    names = ["raw_results.jsonl", "successful_results.jsonl",
             "failed_results.jsonl", "text_export.jsonl", "combined_output.md"]
    files = {n: SafeFile(out_dir / n) for n in names}
    md = files["combined_output.md"]
    md.write(f"# Batch {batch.id} — recovered output\n\n"
             f"_Exported {datetime.now(timezone.utc).isoformat()}_\n\n")

    stats: Counter = Counter()
    resubmit, needs_fix, truncated = [], [], []
    code_files_written = 0

    try:
        for item in client.messages.batches.results(batch.id):
            raw = to_jsonable(item)
            files["raw_results.jsonl"].write_json(raw)

            cid = item.custom_id
            rtype = item.result.type
            stats[rtype] += 1

            if rtype == "succeeded":
                files["successful_results.jsonl"].write_json(raw)
                msg = item.result.message
                ex = extract_message(msg)
                stop = getattr(msg, "stop_reason", None)
                is_trunc = stop == "max_tokens"
                if is_trunc:
                    truncated.append(cid)

                code_paths = (save_code_blocks(code_dir, cid, ex["code_blocks"])
                              if write_code_files else [])
                code_files_written += len(code_paths)

                files["text_export.jsonl"].write_json({
                    "custom_id": cid,
                    "model": getattr(msg, "model", None),
                    "stop_reason": stop,
                    "truncated": is_trunc,
                    "text": ex["text"],
                    "code_blocks": ex["code_blocks"],
                    "code_files": code_paths,
                    "tool_calls": ex["tool_calls"],
                    "thinking": ex["thinking"],
                    "other_blocks": ex["other_blocks"],
                    "usage": to_jsonable(getattr(msg, "usage", None)),
                })

                md.write(f"\n---\n\n## {cid}\n\n"
                         f"- model: `{getattr(msg, 'model', '?')}`\n"
                         f"- stop_reason: `{stop}`"
                         f"{'  **⚠ TRUNCATED (max_tokens)**' if is_trunc else ''}\n\n")
                if md_thinking and ex["thinking"]:
                    md.write("<details><summary>Thinking</summary>\n\n"
                             f"{ex['thinking']}\n\n</details>\n\n")
                md.write((ex["text"] or "_(no text content)_") + "\n")
                for tc in ex["tool_calls"]:
                    md.write(f"\n**Tool call `{tc['name']}`:**\n\n```json\n"
                             f"{json.dumps(tc['input'], indent=2, ensure_ascii=False)}"
                             "\n```\n")
            else:
                files["failed_results.jsonl"].write_json(raw)
                err_type = None
                if rtype == "errored":
                    err = to_jsonable(getattr(item.result, "error", None)) or {}
                    err_type = (err.get("error") or {}).get("type") or err.get("type")
                if err_type in NON_RETRYABLE_ERRORS:
                    needs_fix.append(f"{cid}\t{err_type}")
                else:
                    resubmit.append(cid)

            total = sum(stats.values())
            if total % 100 == 0:
                log(f"  ... {total} results streamed")

    except BaseException:
        for f in files.values():
            f.abort()
        log(f"\n!! Export interrupted. Everything received so far is preserved "
            f"in the *.part files in:\n   {out_dir}\n"
            "   Re-running this script is free (no tokens are consumed).")
        raise

    for f in files.values():
        f.commit()

    def write_list(name: str, rows: list[str]) -> None:
        (out_dir / name).write_text("\n".join(rows) + ("\n" if rows else ""),
                                    encoding="utf-8")

    write_list("resubmit_custom_ids.txt", resubmit)
    write_list("needs_fix_custom_ids.txt", needs_fix)
    write_list("truncated_custom_ids.txt", truncated)

    summary = {
        "batch_id": batch.id,
        "processing_status": batch.processing_status,
        "created_at": str(getattr(batch, "created_at", "")),
        "ended_at": str(getattr(batch, "ended_at", "")),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "result_counts": dict(stats),
        "total_results": sum(stats.values()),
        "truncated_count": len(truncated),
        "resubmit_count": len(resubmit),
        "needs_fix_count": len(needs_fix),
        "code_files_written": code_files_written,
        "output_dir": str(out_dir.resolve()),
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Recover and export completed results from an Anthropic "
                    "Message Batch without resubmitting (no extra token cost).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: ./recover_batch.py msgbatch_01ABC... --wait")
    p.add_argument("batch_id", nargs="?", default=os.environ.get("ANTHROPIC_BATCH_ID"),
                   help="Batch ID (or set ANTHROPIC_BATCH_ID).")
    p.add_argument("--list", action="store_true",
                   help="List recent batches and exit.")
    p.add_argument("--wait", action="store_true",
                   help="Poll until the batch ends, then export.")
    p.add_argument("--cancel", action="store_true",
                   help="Cancel a running batch so completed work is released "
                        "now (unfinished items are not billed). Irreversible.")
    p.add_argument("-y", "--yes", action="store_true",
                   help="Skip the confirmation prompt for --cancel.")
    p.add_argument("--poll-interval", type=float, default=30.0,
                   help="Seconds between status checks (default: 30).")
    p.add_argument("--timeout", type=float, default=0.0,
                   help="Max seconds to wait (0 = no limit).")
    p.add_argument("-o", "--output-dir", type=Path, default=None,
                   help="Output directory (default: ./batch_exports/<id>_<time>).")
    p.add_argument("--no-code-files", action="store_true",
                   help="Do not write fenced code blocks to separate files.")
    p.add_argument("--md-thinking", action="store_true",
                   help="Include extended-thinking text in combined_output.md.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        log("ERROR: ANTHROPIC_API_KEY is not set.\n"
            "       export ANTHROPIC_API_KEY='sk-ant-...'")
        return 1

    client = Anthropic(max_retries=5)

    try:
        if args.list:
            list_batches(client)
            return 0

        if not args.batch_id:
            log("ERROR: No batch ID given. Pass it as an argument, set "
                "ANTHROPIC_BATCH_ID, or run with --list to find it.")
            return 1

        batch_id = args.batch_id.strip()
        log(f"Checking batch {batch_id} ...")
        batch = client.messages.batches.retrieve(batch_id)
        log(f"  {describe(batch)}")

        if batch.processing_status == "in_progress":
            if args.cancel:
                c = batch.request_counts
                log(f"\nCancelling will keep the {c.succeeded} succeeded result(s) "
                    f"and stop the {c.processing} still-processing request(s).")
                if not (args.yes or confirm("Cancel this batch now?")):
                    log("Aborted; batch left running.")
                    return 2
                client.messages.batches.cancel(batch_id)
                log("Cancel requested. Waiting for the batch to finish ending ...")
                batch = wait_until_ended(client, batch_id,
                                         min(args.poll_interval, 10.0), args.timeout)
            elif args.wait:
                log(f"\nPolling every {args.poll_interval:.0f}s until the batch ends "
                    "(Ctrl-C to stop; the batch keeps running server-side) ...")
                batch = wait_until_ended(client, batch_id,
                                         args.poll_interval, args.timeout)
            else:
                log("\nThe batch is still processing. The API only releases results "
                    "once a batch has ended. Choose one:\n"
                    "  --wait    poll until it finishes, then export everything\n"
                    "  --cancel  stop it now and export the work completed so far")
                return 2
        elif batch.processing_status == "canceling":
            log("Batch is being cancelled; waiting for it to end ...")
            batch = wait_until_ended(client, batch_id,
                                     min(args.poll_interval, 10.0), args.timeout)

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_dir = args.output_dir or Path("batch_exports") / f"{safe_name(batch_id)}_{stamp}"
        log(f"\nBatch has ended. Streaming results to: {out_dir}")

        summary = export_results(client, batch, out_dir,
                                 write_code_files=not args.no_code_files,
                                 md_thinking=args.md_thinking)

    except KeyboardInterrupt:
        log("\nInterrupted by user. The batch itself is unaffected; re-run anytime.")
        return 130
    except anthropic.NotFoundError:
        log("ERROR: Batch not found. Check the ID, and make sure the API key "
            "belongs to the same workspace that created the batch.")
        return 1
    except anthropic.AuthenticationError:
        log("ERROR: Authentication failed. Check ANTHROPIC_API_KEY.")
        return 1
    except anthropic.APIConnectionError as e:
        log(f"ERROR: Could not reach the Anthropic API: {e}")
        return 1
    except anthropic.APIStatusError as e:
        log(f"ERROR: API returned {e.status_code}: {e.message}")
        return 1
    except TimeoutError as e:
        log(f"\n{e}")
        return 2

    rc = summary["result_counts"]
    log("\n================ Export complete ================")
    log(f"  Succeeded : {rc.get('succeeded', 0)}"
        f"  (truncated by max_tokens: {summary['truncated_count']})")
    log(f"  Errored   : {rc.get('errored', 0)}")
    log(f"  Canceled  : {rc.get('canceled', 0)}")
    log(f"  Expired   : {rc.get('expired', 0)}")
    log(f"  Code files: {summary['code_files_written']}")
    log(f"  Output    : {summary['output_dir']}")
    if summary["resubmit_count"]:
        log(f"\n  -> {summary['resubmit_count']} item(s) listed in "
            "resubmit_custom_ids.txt. Resubmit ONLY these to avoid double-spending.")
    if summary["needs_fix_count"]:
        log(f"  -> {summary['needs_fix_count']} item(s) in needs_fix_custom_ids.txt "
            "failed due to invalid requests; fix them before resubmitting.")
    if summary["truncated_count"]:
        log("  -> Some outputs hit max_tokens (see truncated_custom_ids.txt); "
            "consider re-running those with a higher max_tokens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

