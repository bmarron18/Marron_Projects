#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 24 Sept 2026
@author: bmarron, claude-opus-5-5

Revised: v2.0
    * FIX: long-running requests failed with
           "RemoteProtocolError: Server disconnected without sending a response"
           -> APIConnectionError.  The request is now submitted in BACKGROUND
           mode and polled until complete, so no HTTP connection is held open
           for minutes at a time.
    * NEW: --resume <response_id> to collect a background job later
           (e.g. after Ctrl-C, a network drop, or a polling timeout).
    * NEW: web_search tool enabled so the model can actually review
           literature; web sources saved to *_sources.txt.
    * NEW: raw response JSON + response ID saved for debugging.
    * NEW: status handling for failed / incomplete / cancelled responses.
    * FIX: prompt strings no longer contain embedded runs of whitespace;
           typos corrected.

==================================
Data Query Template
Model ==> gpt-6-astra
Multi-file-type output (text, code, images, data files)
==================================

WHAT THIS SCRIPT DOES
---------------------
    1. Submits a query to an OpenAI model via the Responses API in
       BACKGROUND mode, with the Code Interpreter and Web Search tools enabled.
    2. Polls the API until the job completes (robust to network drops).
    3. Saves the model's text answer to a .txt file.
    4. Saves any web sources (URL citations) to a _sources.txt file.
    5. Saves any code that the model executed to .py files.
    6. Saves the execution logs to a .log file.
    7. Downloads every file the model generated inside its sandbox
       (e.g. .png, .csv, .xlsx, .py, .pdf) with its original name and extension.
    8. Saves any inline images (plots) returned by Code Interpreter.
    9. Saves the raw JSON response for debugging.

    All outputs are written to a time-stamped folder on the Desktop:
        ~/Desktop/EcosanQuery_OpenAI_YYYYMMDD_HHMMSS/


UPDATE AND LIST INSTALLED PACKAGES
-------------
<<< bash
    cd ~/spyder-6/envs &&
    source ./ai-apis/bin/activate &&
    python3 -m pip install --upgrade pip &&
    pip install --upgrade openai

    pip list
>>>

RUN IN SPYDER
-------------
    * *Run* (F5)


RUN SCRIPT FROM DESKTOP
------------------
On Desktop
    * copy of this script

<<<bash
    cd ~/spyder-6/envs &&
    source ./ai-apis/bin/activate

        # run script (normal)
    python3 ~/Desktop/A_Template_DataQuery_OpenAI_v2.0.py

        # run script (dry run)
    python3 ~/Desktop/A_Template_DataQuery_OpenAI_v2.0.py --dry-run
>>>
    
    
INTERRUPTED RUN 
-----------------
If the run is interrupted(Ctrl-C, network drop, or polling exceeds 60 minutes), the job keeps running 
server-side. Check the ouput docs for a XXXX_response_id.txt file. Will have data like this:
    resp_0500885f0f7254b2006ab701e618e487d1b2da1e48a6b43be6
    status: completed


Collect the job with:
<<<bash
       # resume / collect an earlier background job
   python3 ~/Desktop/A_Template_DataQuery_OpenAI_v2.0.py --resume resp_XXXXXXXX
>>>

   In Spyder, set this under **Run → Configuration per file → Command line options**.
        Run > Configuration per file > Command line options:  --resume resp_XXXXXXXX
"""


import argparse
import base64
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from openai import OpenAI, APIConnectionError, APIStatusError, APITimeoutError


# =============================================================================
# CONFIGURATION
# =============================================================================

    # model to query
MODEL = "gpt-6-astra"

    # base label for all output files
OUTPUT_LABEL = "EcosanQuery_OpenAI"

    # Desktop directory (falls back to ~/Desktop if the hard-coded path is absent)
DOC_DIR = Path("/home/bruce-vdb/Desktop")
if not DOC_DIR.exists():
    DOC_DIR = Path.home() / "Desktop"

    # memory for the Code Interpreter sandbox ("1g", "4g", "16g", "64g")
    # set to None to use the API default
CONTAINER_MEMORY = "4g"

    # enable the web search tool (needed for real literature review/citations)
USE_WEB_SEARCH = True

    # per-HTTP-request timeout (seconds). Each request is now short
    # (submit / poll), so this does NOT need to cover the whole job.
API_TIMEOUT = 120

    # automatic SDK retries for each individual HTTP request
MAX_RETRIES = 3

    # polling settings for background mode
POLL_INTERVAL = 10          # seconds between status checks
MAX_WAIT = 60 * 60          # give up polling after this many seconds (job keeps running)
MAX_POLL_ERRORS = 10        # consecutive network errors tolerated while polling

    # extra data to return with the response
INCLUDE = ["code_interpreter_call.outputs"]           # logs + images
if USE_WEB_SEARCH:
    INCLUDE.append("web_search_call.action.sources")  # web sources consulted


# =============================================================================
# Prompt
# =============================================================================

    # User level message
user_prompt = (
    "Design a complete, self-contained home-scale ecosanitation system that "
    "effectively and efficiently recycles human waste into garden-ready "
    "fertilizer. The system must be designed so that 1) it can handle human "
    "waste from three adults; 2) it uses very little electricity and virtually "
    "no freshwater; 3) it separates urine and feces; 4) it rapidly decomposes "
    "fecal material using inoculations of specialized bacteria and fungi; and "
    "5) it has a minimal ecological footprint. To begin exploring design options "
    "for such a system, review open-source journals, textbooks, and relevant "
    "source materials for advances in ecosanitation, advances in animal manure "
    "processing, and advances in bacterial-fungal decomposition of waste "
    "streams. Provide 1) a high-level conceptual design in both written and "
    "graphical form; and 2) a list of relevant citations."
)

    # Developer level message
sys_prompt = (
    "You are an expert in bacterial and fungal decomposition techniques and "
    "ecological engineering designs. Use web search to find and verify sources; "
    "cite only sources you have actually located. When a file, chart, table, or "
    "script would be useful, create it with the code interpreter and save it as "
    "a file so the user can download it."
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_output_dir(base_dir: Path, label: str) -> Path:
    """Create a unique, time-stamped output folder."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = base_dir / f"{label}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def safe_filename(name: str, default: str = "file") -> str:
    """Strip path parts and characters that are unsafe in filenames."""
    name = os.path.basename(name or "").strip()
    name = re.sub(r"[^\w.\-]+", "_", name)
    return name or default


def unique_path(directory: Path, filename: str) -> Path:
    """Avoid overwriting files that share the same name."""
    path = directory / filename
    stem, suffix = path.stem, path.suffix
    n = 1
    while path.exists():
        path = directory / f"{stem}_{n}{suffix}"
        n += 1
    return path


def get_attr(obj, key, default=None):
    """Read a field from either an SDK object or a plain dict."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def download_container_file(client: OpenAI, container_id: str,
                            file_id: str, filename: str, out_dir: Path):
    """Download a file created inside the Code Interpreter container."""
    target = unique_path(out_dir, safe_filename(filename, default=file_id))
    content = client.containers.files.content.retrieve(
        file_id,
        container_id=container_id,
    )
    target.write_bytes(content.read())
    return target


def save_image_url(url: str, out_dir: Path, index: int):
    """Save an image returned as a data URL (base64) or as a web URL."""
    if url.startswith("data:"):
        header, b64data = url.split(",", 1)
        ext_match = re.search(r"image/(\w+)", header)
        ext = ext_match.group(1) if ext_match else "png"
        target = unique_path(out_dir, f"image_{index}.{ext}")
        target.write_bytes(base64.b64decode(b64data))
    else:
        target = unique_path(out_dir, f"image_{index}.png")
        with urllib.request.urlopen(url, timeout=60) as resp:
            target.write_bytes(resp.read())
    return target


def resume_hint(response_id: str) -> str:
    """Command the user can run to collect a background job later."""
    script = os.path.basename(__file__) if "__file__" in globals() else "script.py"
    return f"python3 {script} --resume {response_id}"


# =============================================================================
# API: SUBMIT + POLL (BACKGROUND MODE)
# =============================================================================

def build_tools() -> list:
    """Assemble the tool list for the request."""
    container = {"type": "auto"}
    if CONTAINER_MEMORY:
        container["memory_limit"] = CONTAINER_MEMORY

    tools = [{"type": "code_interpreter", "container": container}]
    if USE_WEB_SEARCH:
        tools.append({"type": "web_search"})
    return tools


def submit_query(client: OpenAI) -> str:
    """
    Submit the request in background mode.
    Returns immediately with a response ID; the model works server-side.
    """
    print(f"Submitting prompt to {MODEL} (background mode) ...")

    response = client.responses.create(
        model=MODEL,
        instructions=sys_prompt,
        input=user_prompt,
        tools=build_tools(),
        include=INCLUDE,
        background=True,     # <-- key fix: no long-held HTTP connection
        store=True,          # required for background mode
    )

    print(f"Response ID: {response.id}")
    print(f"(If interrupted, collect later with:  {resume_hint(response.id)})\n")
    return response.id


def wait_for_response(client: OpenAI, response_id: str):
    """
    Poll a background response until it reaches a terminal state.
    Tolerates transient network errors. Returns the final Response object,
    or None if MAX_WAIT is exceeded (the job keeps running on the server).
    """
    terminal = {"completed", "failed", "cancelled", "incomplete"}
    start = time.time()
    last_status = None
    poll_errors = 0

    while True:
        try:
            resp = client.responses.retrieve(response_id, include=INCLUDE)
            poll_errors = 0
        except (APIConnectionError, APITimeoutError) as err:
            poll_errors += 1
            if poll_errors > MAX_POLL_ERRORS:
                print(f"\n[Error] Too many consecutive polling errors: {err}")
                return None
            wait = min(POLL_INTERVAL * poll_errors, 60)
            print(f"[Warning] Polling error ({poll_errors}/{MAX_POLL_ERRORS}): "
                  f"{err}. Retrying in {wait}s ...")
            time.sleep(wait)
            continue

        status = get_attr(resp, "status")
        elapsed = int(time.time() - start)

        if status != last_status:
            print(f"[{elapsed:>5}s] status: {status}")
            last_status = status
        else:
            print(f"[{elapsed:>5}s] still {status} ...", end="\r", flush=True)

        if status in terminal:
            print()
            return resp

        if elapsed > MAX_WAIT:
            print(f"\n[Warning] Stopped polling after {MAX_WAIT}s. "
                  "The job is still running on the server.")
            return None

        time.sleep(POLL_INTERVAL)


# =============================================================================
# OUTPUT HANDLING
# =============================================================================

def process_response(client: OpenAI, response, out_dir: Path) -> None:

    saved_files = []
    status = get_attr(response, "status")

    # ---------------------------------------------------------------
    # 0. RAW JSON + ID (debugging / record keeping)
    # ---------------------------------------------------------------
    try:
        raw_path = out_dir / f"{OUTPUT_LABEL}_raw_response.json"
        raw_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")
        saved_files.append(raw_path)
    except Exception as err:
        print(f"[Warning] Could not save raw JSON: {err}")

    id_path = out_dir / f"{OUTPUT_LABEL}_response_id.txt"
    id_path.write_text(f"{response.id}\nstatus: {status}\n", encoding="utf-8")
    saved_files.append(id_path)

    # ---------------------------------------------------------------
    # 0b. STATUS CHECK
    # ---------------------------------------------------------------
    if status != "completed":
        detail = get_attr(response, "error") or get_attr(response, "incomplete_details")
        print(f"[Warning] Response status is '{status}'. Details: {detail}")
        err_path = out_dir / f"{OUTPUT_LABEL}_status_{status}.txt"
        err_path.write_text(f"status: {status}\ndetails: {detail}\n", encoding="utf-8")
        saved_files.append(err_path)
        # continue anyway: partial output may still be useful

    # ---------------------------------------------------------------
    # 1. TEXT OUTPUT  -> .txt
    # ---------------------------------------------------------------
    output_text = get_attr(response, "output_text") or ""
    text_path = out_dir / f"{OUTPUT_LABEL}.txt"
    text_path.write_text(output_text, encoding="utf-8")
    saved_files.append(text_path)

    print("--- TEXT OUTPUT ---")
    print(output_text if output_text else "(no text output)")
    print()

    # ---------------------------------------------------------------
    # 2. WALK THROUGH EVERY OUTPUT ITEM
    # ---------------------------------------------------------------
    container_files = {}          # file_id -> (container_id, filename)
    container_ids = set()
    log_lines = []
    web_sources = {}              # url -> title
    code_count = 0
    image_count = 0

    for item in get_attr(response, "output") or []:
        item_type = get_attr(item, "type")

        # ---- Code Interpreter calls: code, logs, images ------------
        if item_type == "code_interpreter_call":
            container_id = get_attr(item, "container_id")
            if container_id:
                container_ids.add(container_id)

                # save the code the model executed -> .py
            code = get_attr(item, "code")
            if code:
                code_count += 1
                code_path = unique_path(out_dir, f"executed_code_{code_count}.py")
                code_path.write_text(code, encoding="utf-8")
                saved_files.append(code_path)

                # logs and inline images
            for output in get_attr(item, "outputs") or []:
                out_type = get_attr(output, "type")

                if out_type == "logs":
                    logs = get_attr(output, "logs", "")
                    log_lines.append(f"=== Code block {code_count} ===\n{logs}\n")
                    print("--- CODE INTERPRETER LOGS ---")
                    print(logs)

                elif out_type == "image":
                    url = get_attr(output, "url")
                    if url:
                        image_count += 1
                        try:
                            img_path = save_image_url(url, out_dir, image_count)
                            saved_files.append(img_path)
                            print(f"[Image Output] -> {img_path.name}")
                        except Exception as err:
                            print(f"[Warning] Could not save image {image_count}: {err}")

        # ---- Web search calls: sources consulted -------------------
        elif item_type == "web_search_call":
            action = get_attr(item, "action")
            for src in (get_attr(action, "sources") or []) if action else []:
                url = get_attr(src, "url")
                if url and url not in web_sources:
                    web_sources[url] = get_attr(src, "title") or ""

        # ---- Messages: file citations + URL citations --------------
        elif item_type == "message":
            for part in get_attr(item, "content") or []:
                for ann in get_attr(part, "annotations") or []:
                    ann_type = get_attr(ann, "type")

                    if ann_type == "container_file_citation":
                        file_id = get_attr(ann, "file_id")
                        cid = get_attr(ann, "container_id")
                        fname = get_attr(ann, "filename") or file_id
                        if file_id and cid:
                            container_files[file_id] = (cid, fname)
                            container_ids.add(cid)

                    elif ann_type == "url_citation":
                        url = get_attr(ann, "url")
                        if url:
                            # cited titles take precedence over search-only titles
                            web_sources[url] = get_attr(ann, "title") or web_sources.get(url, "")

    # ---------------------------------------------------------------
    # 3. FALLBACK: list model-created files in each container
    #    (catches files the model saved but did not cite)
    # ---------------------------------------------------------------
    for cid in container_ids:
        try:
            for f in client.containers.files.list(container_id=cid):
                if get_attr(f, "source") == "user":
                    continue            # skip files we uploaded
                fid = get_attr(f, "id")
                if fid and fid not in container_files:
                    fname = os.path.basename(get_attr(f, "path") or fid)
                    container_files[fid] = (cid, fname)
        except Exception as err:
            print(f"[Warning] Could not list files in container {cid}: {err}")
            print("          (Containers expire after ~20 min of inactivity; "
                  "resume promptly after a job completes.)")

    # ---------------------------------------------------------------
    # 4. DOWNLOAD ALL GENERATED FILES (any type)
    # ---------------------------------------------------------------
    for file_id, (cid, fname) in container_files.items():
        try:
            path = download_container_file(client, cid, file_id, fname, out_dir)
            saved_files.append(path)
            print(f"[File Output] -> {path.name}")
        except Exception as err:
            print(f"[Warning] Could not download '{fname}' ({file_id}): {err}")

    # ---------------------------------------------------------------
    # 5. EXECUTION LOGS -> .log
    # ---------------------------------------------------------------
    if log_lines:
        log_path = out_dir / f"{OUTPUT_LABEL}_execution.log"
        log_path.write_text("\n".join(log_lines), encoding="utf-8")
        saved_files.append(log_path)

    # ---------------------------------------------------------------
    # 6. WEB SOURCES -> _sources.txt
    # ---------------------------------------------------------------
    if web_sources:
        src_path = out_dir / f"{OUTPUT_LABEL}_sources.txt"
        lines = [f"{i}. {title}\n   {url}" if title else f"{i}. {url}"
                 for i, (url, title) in enumerate(web_sources.items(), start=1)]
        src_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        saved_files.append(src_path)

    # ---------------------------------------------------------------
    # 7. USAGE + SUMMARY
    # ---------------------------------------------------------------
    usage = get_attr(response, "usage")
    print("\n==================================")
    if usage:
        print(f"Tokens: input={get_attr(usage, 'input_tokens')}  "
              f"output={get_attr(usage, 'output_tokens')}  "
              f"total={get_attr(usage, 'total_tokens')}")
    print(f"Query {status}! {len(saved_files)} file(s) saved to:")
    print(f"  {out_dir}")
    for p in saved_files:
        print(f"    - {p.name}")
    print("==================================")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
        # parse_known_args ignores extra arguments Spyder may pass (e.g. --wdir)
    parser = argparse.ArgumentParser(description="Query OpenAI with multi-file output.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show settings without calling the API.")
    parser.add_argument("--resume", metavar="RESPONSE_ID", default=None,
                        help="Collect results of an existing background response.")
    args, _ = parser.parse_known_args()

    if args.dry_run:
        print("DRY RUN: no API call will be made.\n")
        print(f"Model:          {MODEL}")
        print(f"Output folder:  {DOC_DIR / (OUTPUT_LABEL + '_<timestamp>')}")
        print(f"Container mem:  {CONTAINER_MEMORY}")
        print(f"Web search:     {USE_WEB_SEARCH}")
        print(f"Tools:          {[t['type'] for t in build_tools()]}")
        print(f"Include:        {INCLUDE}")
        print(f"Poll every:     {POLL_INTERVAL}s  (max wait {MAX_WAIT}s)")
        print(f"API key found:  {bool(os.getenv('OPENAI_API_KEY'))}")
        print(f"\nInstructions:\n{sys_prompt}")
        print(f"\nPrompt:\n{user_prompt}")
        return

        # API_KEY is saved as an ENV VARIABLE on home compu
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("ERROR: OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key, timeout=API_TIMEOUT, max_retries=MAX_RETRIES)

    # ---- submit (or resume) ----------------------------------------
    try:
        if args.resume:
            response_id = args.resume
            print(f"Resuming background response {response_id} ...\n")
        else:
            response_id = submit_query(client)
    except APIStatusError as err:
        sys.exit(f"ERROR: API returned status {err.status_code}: {err.message}")
    except APIConnectionError as err:
        sys.exit(f"ERROR: Could not reach the OpenAI API: {err}")

    # ---- poll -------------------------------------------------------
    try:
        response = wait_for_response(client, response_id)
    except KeyboardInterrupt:
        print("\n\nInterrupted. The job is still running on the server.")
        print(f"Collect it later with:\n  {resume_hint(response_id)}")
        return
    except APIStatusError as err:
        sys.exit(f"ERROR: API returned status {err.status_code}: {err.message}")

    if response is None:
        print(f"Collect it later with:\n  {resume_hint(response_id)}")
        return

    # ---- save outputs ----------------------------------------------
    out_dir = make_output_dir(DOC_DIR, OUTPUT_LABEL)
    process_response(client, response, out_dir)


if __name__ == "__main__":
    main()


