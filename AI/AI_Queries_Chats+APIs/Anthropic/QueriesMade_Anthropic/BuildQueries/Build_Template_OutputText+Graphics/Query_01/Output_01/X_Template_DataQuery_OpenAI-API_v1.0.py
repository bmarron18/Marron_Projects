#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Created on 24 Sept 2026
@author: bmarron, claude-opus-5-5

==================================
Data Query Template
Model ==> gpt-6-astra
Multi-file-type output (text, code, images, data files)
==================================

WHAT THIS SCRIPT DOES
---------------------
    1. Sends a query to an OpenAI model via the Responses API, with the
       Code Interpreter tool enabled.
    2. Saves the model's text answer to a .txt file.
    3. Saves any code that the model executed to .py files.
    4. Saves the execution logs to a .log file.
    5. Downloads every file the model generated inside its sandbox
       (e.g. .png, .csv, .xlsx, .py, .pdf) with its original name and extension.
    6. Saves any inline images (plots) returned by Code Interpreter.

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
    python3 ~/Desktop/X_Template_DataQuery_OpenAI-API_v1.0.py
    
        # run script (dry run)
    python3 ~/Desktop/X_Template_DataQuery_OpenAI-API_v1.0.py --dry-run
>>>

"""


import argparse
import base64
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from openai import OpenAI


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

    # seconds to wait for the API (code-interpreter jobs can take a while)
API_TIMEOUT = 600


# =============================================================================
# Prompt
# =============================================================================

    # User level message
user_prompt = (
    "Write the complete Python code for using OpenAI model, 'gpt-live-transcribe' "
    "to take real-time English spoken audio (input), translate the spoken audio to "
    "Spanish, and send the translated text to both the Python interpreter screen and "
    "to a simple text file on my desktop (/home/bruce-vdb/Desktop). My computer's "
    "operating system is Linux Mint 22.3 and I will be running the Python script in "
    "a virtual environment in Spyder 6.1.7. "
    "In addition to your written answer, use the code interpreter to save the "
    "complete script as a downloadable .py file."
)

    # Developer level message
sys_prompt = (
    "You are an expert Python code writer and debugger. "
    "When a file, chart, table, or script would be useful, create it with the "
    "code interpreter and save it as a file so the user can download it."
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
        with urllib.request.urlopen(url) as resp:
            target.write_bytes(resp.read())
    return target


# =============================================================================
# MAIN QUERY + OUTPUT HANDLING
# =============================================================================

def run_query(client: OpenAI, out_dir: Path) -> None:

    print(f"Sending prompt to {MODEL} ...\n")

        # Code Interpreter tool definition
    container = {"type": "auto"}
    if CONTAINER_MEMORY:
        container["memory_limit"] = CONTAINER_MEMORY

    response = client.responses.create(
        model=MODEL,
        instructions=sys_prompt,
        input=user_prompt,
        tools=[{"type": "code_interpreter", "container": container}],
        include=["code_interpreter_call.outputs"],   # return logs + images
    )

    saved_files = []

    # ---------------------------------------------------------------
    # 1. TEXT OUTPUT  -> .txt
    # ---------------------------------------------------------------
    text_path = out_dir / f"{OUTPUT_LABEL}.txt"
    text_path.write_text(response.output_text or "", encoding="utf-8")
    saved_files.append(text_path)

    print("--- TEXT OUTPUT ---")
    print(response.output_text)
    print()

    # ---------------------------------------------------------------
    # 2. WALK THROUGH EVERY OUTPUT ITEM
    # ---------------------------------------------------------------
    container_files = {}          # file_id -> (container_id, filename)
    container_ids = set()
    log_lines = []
    code_count = 0
    image_count = 0

    for item in response.output:
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

        # ---- Messages: look for file citations ---------------------
        elif item_type == "message":
            for part in get_attr(item, "content") or []:
                for ann in get_attr(part, "annotations") or []:
                    if get_attr(ann, "type") == "container_file_citation":
                        file_id = get_attr(ann, "file_id")
                        cid = get_attr(ann, "container_id")
                        fname = get_attr(ann, "filename") or file_id
                        if file_id and cid:
                            container_files[file_id] = (cid, fname)
                            container_ids.add(cid)

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
    # 6. SUMMARY
    # ---------------------------------------------------------------
    print("\n==================================")
    print(f"Query complete! {len(saved_files)} file(s) saved to:")
    print(f"  {out_dir}")
    for p in saved_files:
        print(f"    - {p.name}")
    print("==================================")


def main() -> None:
        # parse_known_args ignores extra arguments Spyder may pass
    parser = argparse.ArgumentParser(description="Query OpenAI with multi-file output.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show settings without calling the API.")
    args, _ = parser.parse_known_args()

    if args.dry_run:
        print("DRY RUN: no API call will be made.\n")
        print(f"Model:          {MODEL}")
        print(f"Output folder:  {DOC_DIR / (OUTPUT_LABEL + '_<timestamp>')}")
        print(f"Container mem:  {CONTAINER_MEMORY}")
        print(f"API key found:  {bool(os.getenv('OPENAI_API_KEY'))}")
        print(f"\nPrompt:\n{user_prompt}")
        return

        # API_KEY is saved as an ENV VARIABLE on home compu
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("ERROR: OPENAI_API_KEY environment variable is not set.")

    client = OpenAI(api_key=api_key, timeout=API_TIMEOUT)

    out_dir = make_output_dir(DOC_DIR, OUTPUT_LABEL)
    run_query(client, out_dir)


if __name__ == "__main__":
    main()