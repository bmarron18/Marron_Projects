#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 24 Sept 2026
Revised:  20 Oct 2026
Authors : bruce-vdb, claude-opus-5-5

-------------------------------------------------
A_Template_AnalysisQuery_anthropic_v3.4.py
-------------------------------------------------
  * Send one or more files of ANY permitted type for analysis to Claude
  * Stream the reply to a text file that includes a) analytical results, and 
    b) the Python code to generate any requested graphics
  * Save any files Claude generates
  * Clean up (remove from storage) the uploaded files


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
  3. Edit SECTION 1 below (files, prompt)
  
  4. Run file (runs in Spyder within virtual environment, ai-apis)
      * To run file w/o CLI toggles
          a) Clic on the green Run file icon in Toolbar or press F5

      * To run file w/ CLI toggles
          a) place copy of file on Desktop
          b) run file using IPython interpreter
runfile('/home/bruce-vdb/Desktop/A_Template_AnalysisQuery_anthropic_v3.4.py', args='--dry-run')

  Command-line examples (CLI files replace INPUT_FILES for that run):
     ./A_Template_...py report.pdf notes.txt -p "Summarize these files"
     ./A_Template_...py photo.png diagram.webp -p "Describe these images"
     ./A_Template_...py -c sales.xlsx budget.docx -p "Compare the totals"
     ./A_Template_...py data.csv -c data.csv -p "..."   # same file, both routes
     ./A_Template_...py script.py --prompt-file my_prompt.txt --overwrite
     ./A_Template_...py --dry-run            # show routing, upload nothing
     ./A_Template_...py --list-types         # list supported extensions
     ./A_Template_...py --purge-all          # delete ALL workspace files
     ./A_Template_...py --help
     
 

---------------------------------------------------------------------------
HOW FILES ARE SENT TO CLAUDE  (chosen automatically from the extension)
---------------------------------------------------------------------------
  route       content block      file types
  ---------   ----------------   -------------------------------------------
  document    document           .pdf  and plain-text / source-code files
                                 (.txt .md .csv .py .json .html .sql ...)
  image       image              .jpg .jpeg .png .gif .webp
  container   container_upload   ANY other file (.xlsx .docx .pptx .zip
                                 .parquet .sqlite .bmp .tiff ...).  Claude
                                 opens these with Python in a sandbox; the
                                 code-execution tool is enabled automatically.        

-----------
REVISIONS
-----------
Revised : v3.3 -- all permitted file types, per-type examples,
                  reorganized input area, continuation / pause_turn fixes
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    sys.exit("The 'anthropic' package is not installed.  Run:  pip install --upgrade anthropic")


# =========================================================================
#  SECTION 1 -- USER SETTINGS  (edit these)
# =========================================================================

# ---- Directory that holds the input files and receives the output ---------
DOC_DIR = Path.home() / "/home/bruce-vdb/Desktop"          

# ---- Input files (on Desktop) --------------------------------------------------------
#   * One entry per line; add, remove or comment out (#) lines freely.
#   * Names are relative to DOC_DIR, or give an absolute path.
#   * Entry formats:
#         "file.ext"                      -> route chosen from the extension
#         ("file.ext", "container")       -> force a route:
#                                            "document" | "image" | "container"
INPUT_FILES = [
    # ---- PDF documents ----------------------------------------------
 #    "Woods_Resilience.pdf",

    # ---- Plain text / source code -----------------------------------
    "A_Template_AnalysisQuery_anthropic_v3.4.py",
 #   "Errors.txt",

    # ---- Images -----------------------------------------------------
    # "Screenshot.png",

    # ---- Other files (opened with Python in the sandbox) -------------
    # "Sales_2025.xlsx",
]

# ---- EXAMPLES: one or more for every supported file type --------------
#   Copy any line into INPUT_FILES above (and change the name).
#
#   PDF  (route: document) ..............................................
#     "Annual_Report_2025.pdf",
#
#   PLAIN TEXT  (route: document; file must be UTF-8 text) ..............
#     "Notes.txt",              "README.md",            "Manual.rst",
#     "Data.csv",               "Data.tsv",             "Server.log",
#     "Config.json",            "Records.jsonl",        "Settings.yaml",
#     "Settings.yml",           "pyproject.toml",       "Setup.ini",
#     "Feed.xml",               "Page.html",            "Style.css",
#     "Paper.tex",              "Refs.bib",             "Subtitles.srt",
#     "Notebook.ipynb",         "Makefile",             "Dockerfile",
#
#   SOURCE CODE  (route: document) ......................................
#     "Script.py",   "App.js",   "App.ts",    "Main.java",  "Main.c",
#     "Main.cpp",    "Lib.h",    "Prog.cs",   "Main.go",    "Main.rs",
#     "Tool.rb",     "Index.php","Run.sh",    "Run.bat",    "Run.ps1",
#     "Query.sql",   "Model.R",  "Calc.m",    "App.swift",  "App.kt",
#
#   IMAGES  (route: image) ..............................................
#     "Photo.jpg",   "Photo.jpeg",   "Chart.png",   "Anim.gif",   "Pic.webp",
#
#   OTHER FILES  (route: container -- Claude uses Python to open them) ...
#     "Sales_2025.xlsx",        "Legacy.xls",           "Sheet.ods",
#     "Contract.docx",          "Letter.odt",           "Deck.pptx",
#     "Archive.zip",            "Backup.tar.gz",        "Table.parquet",
#     "Inventory.sqlite",       "Arrays.npy",           "Scan.tiff",
#     "Bitmap.bmp",             "Drawing.svg",          "Ebook.epub",
#
#   FORCING A ROUTE  (tuple form) .......................................
#     ("Big_Dataset.csv", "container"),  # analyze with code, not read as text
#     ("Vector.svg", "document"),        # read SVG markup as text
#     ("Photo.png", "container"),        # process the image with Python (PIL)

# ---- The prompt (adjacent string literals = no stray spaces) ----------
PROMPT = (
    "Review and analyze the attached Python script. The script works perfectly and provides high-level analysis \
    of multiple files. The script has multiple features as described in the module docstring. Using the attached \
    script as a template, create an equivalent Python script for using Google gemini-3.8-flash. The new script should \
    maintain all the same features as the attached script. The name of the new script will be, \
    A_Template_AnalysisQuery_google-genai_v3.0.py. Thank you!"
)

# ---- Optional system prompt (None = no system prompt) -----------------
SYSTEM_PROMPT = "You are an expert Python coder."

# ---- Output -------------------------------------------------------------
OUTPUT_FILE = "QueryResponse_Anthropic.txt"
APPEND_MODE = True              # True = append each run; False = overwrite
DOWNLOAD_GENERATED_FILES = True # save files Claude creates in the sandbox
GENERATED_PREFIX = "generated_" # prefix for those saved files

# ---- Unknown extensions -------------------------------------------------
#   "container" = send to the sandbox (any file type allowed)
#   "error"     = refuse unknown extensions
UNKNOWN_TYPE_POLICY = "container"

# ---- Model / output size -----------------------------------------------
MODEL = "claude-opus-5-5"   # or another current model id
MAX_TOKENS = 64000          # lower this if the API rejects it for your model
MAX_CONTINUATIONS = 3       # extra passes if the reply is cut off / paused


# =========================================================================
#  SECTION 2 -- FIXED SETTINGS  (normally no need to edit)
# =========================================================================

FILES_API_BETA = "files-api-2025-04-14"
CODE_EXECUTION_BETA = "code-execution-2025-08-25"
CODE_EXECUTION_TOOL = {"type": "code_execution_20250825", "name": "code_execution"}

MAX_UPLOAD_BYTES = 500 * 1024 * 1024        # Files API per-file limit

ROUTES = ("document", "image", "container")

# Text-like files -> document block with MIME text/plain
TEXT_EXTENSIONS = {
    # prose / markup / data
    ".txt", ".text", ".md", ".markdown", ".rst", ".csv", ".tsv", ".log",
    ".json", ".jsonl", ".ndjson", ".xml", ".html", ".htm", ".css",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".properties",
    ".tex", ".bib", ".srt", ".vtt", ".ipynb", ".svg",
    # source code
    ".py", ".pyw", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".java", ".c",
    ".h", ".cpp", ".cc", ".hpp", ".cs", ".go", ".rs", ".rb", ".php",
    ".pl", ".lua", ".sh", ".bash", ".zsh", ".bat", ".cmd", ".ps1", ".sql",
    ".r", ".m", ".swift", ".kt", ".scala", ".dart", ".vb", ".f90",
}
TEXT_FILENAMES = {"makefile", "dockerfile", "readme", "license", "changelog"}

# Images -> image block
IMAGE_TYPES = {
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".gif":  "image/gif",
    ".webp": "image/webp",
}

# Known binary formats -> container_upload (sandbox + code execution)
CONTAINER_TYPES = {
    ".xlsx":    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls":     "application/vnd.ms-excel",
    ".ods":     "application/vnd.oasis.opendocument.spreadsheet",
    ".docx":    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc":     "application/msword",
    ".odt":     "application/vnd.oasis.opendocument.text",
    ".rtf":     "application/rtf",
    ".pptx":    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".ppt":     "application/vnd.ms-powerpoint",
    ".odp":     "application/vnd.oasis.opendocument.presentation",
    ".epub":    "application/epub+zip",
    ".zip":     "application/zip",
    ".tar":     "application/x-tar",
    ".gz":      "application/gzip",
    ".7z":      "application/x-7z-compressed",
    ".parquet": "application/vnd.apache.parquet",
    ".feather": "application/octet-stream",
    ".npy":     "application/octet-stream",
    ".npz":     "application/octet-stream",
    ".pkl":     "application/octet-stream",
    ".h5":      "application/x-hdf5",
    ".sqlite":  "application/vnd.sqlite3",
    ".db":      "application/vnd.sqlite3",
    ".bmp":     "image/bmp",
    ".tif":     "image/tiff",
    ".tiff":    "image/tiff",
    ".heic":    "image/heic",
    ".ico":     "image/x-icon",
}

CONTINUE_PROMPT = (
    "Your previous reply was cut off by the output-token limit. "
    "Continue exactly where you stopped -- no preamble, no repeated text."
)


# =========================================================================
#  SECTION 3 -- FUNCTIONS
# =========================================================================

@dataclass
class InputFile:
    path: Path
    route: str          # "document" | "image" | "container"
    mime: str
    file_id: str = ""   # filled in after upload


# ---- command line --------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Command-line options; every option defaults to the SECTION 1 value."""
    p = argparse.ArgumentParser(
        description="Send files of any permitted type + a prompt to Claude "
                    "and save the streamed reply.",
    )
    p.add_argument("files", nargs="*",
                   help="input files, route chosen by extension "
                        "(default: INPUT_FILES in the script)")
    p.add_argument("-c", "--container", nargs="+", default=[], metavar="FILE",
                   help="files to force into the code-execution sandbox")
    p.add_argument("-d", "--dir", type=Path, default=DOC_DIR,
                   help=f"folder for input/output files (default: {DOC_DIR})")
    p.add_argument("-p", "--prompt", default=None,
                   help="prompt text (default: PROMPT in the script)")
    p.add_argument("--prompt-file", type=Path, default=None,
                   help="read the prompt from a text file")
    p.add_argument("-s", "--system", default=SYSTEM_PROMPT,
                   help="optional system prompt")
    p.add_argument("-o", "--output", default=OUTPUT_FILE,
                   help=f"output file name (default: {OUTPUT_FILE})")
    p.add_argument("--overwrite", action="store_true",
                   help="overwrite the output file instead of appending")
    p.add_argument("-m", "--model", default=MODEL,
                   help=f"model id (default: {MODEL})")
    p.add_argument("--max-tokens", type=int, default=MAX_TOKENS,
                   help=f"max output tokens per pass (default: {MAX_TOKENS})")
    p.add_argument("--max-continuations", type=int, default=MAX_CONTINUATIONS,
                   help=f"extra passes if cut off/paused (default: {MAX_CONTINUATIONS})")
    p.add_argument("--dry-run", action="store_true",
                   help="show how each file would be sent, then exit (no upload)")
    p.add_argument("--list-types", action="store_true",
                   help="list supported file extensions, then exit")
    p.add_argument("--purge-all", action="store_true",
                   help="delete EVERY file in your Anthropic Files workspace, then exit")
    args = p.parse_args()
    args.dir = args.dir.expanduser()
    return args


def list_types() -> None:
    """Print every supported extension grouped by route."""
    def show(title: str, exts) -> None:
        print(f"\n{title}")
        print("  " + "  ".join(sorted(exts)))
    show("document (PDF):", [".pdf"])
    show("document (plain text, must be UTF-8):", TEXT_EXTENSIONS)
    print("  also extension-less: " + ", ".join(sorted(TEXT_FILENAMES)))
    show("image:", IMAGE_TYPES)
    show("container (opened with Python in the sandbox):", CONTAINER_TYPES)
    if UNKNOWN_TYPE_POLICY == "container":
        print("\n  ...plus ANY other extension (UNKNOWN_TYPE_POLICY = 'container')")
    print()


# ---- client / prompt -----------------------------------------------------

def make_client() -> Anthropic:
    """Create the API client (key read from the ANTHROPIC_API_KEY env var)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: environment variable ANTHROPIC_API_KEY is not set.")
    return Anthropic(api_key=api_key)


def resolve_prompt(args: argparse.Namespace) -> str:
    """Prompt priority: --prompt-file, then --prompt, then PROMPT."""
    if args.prompt_file:
        path = args.prompt_file.expanduser()
        if not path.is_absolute():
            path = args.dir / path
        if not path.is_file():
            sys.exit(f"ERROR: prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    return args.prompt if args.prompt else PROMPT


# ---- input files ---------------------------------------------------------

def container_mime(path: Path) -> str:
    """MIME type for a sandbox upload (any type is allowed)."""
    ext = path.suffix.lower()
    if ext in CONTAINER_TYPES:
        return CONTAINER_TYPES[ext]
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def detect_route(path: Path) -> tuple[str | None, str | None]:
    """(route, mime) from the file extension; (None, None) if unknown."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "document", "application/pdf"
    if ext in TEXT_EXTENSIONS or (not ext and path.name.lower() in TEXT_FILENAMES):
        return "document", "text/plain"
    if ext in IMAGE_TYPES:
        return "image", IMAGE_TYPES[ext]
    if ext in CONTAINER_TYPES:
        return "container", CONTAINER_TYPES[ext]
    return None, None


def check_text_file(path: Path) -> str | None:
    """Return a problem description if the file is not usable as text."""
    data = path.read_bytes()
    if not data.strip():
        return "file is empty"
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return ("not UTF-8 text -- re-save it as UTF-8, or use "
                f'("{path.name}", "container")')
    return None


def normalize_entries(entries) -> list[tuple[str, str]]:
    """Accept "name" or ("name", "route") and return (name, route) pairs."""
    pairs = []
    for entry in entries:
        if isinstance(entry, (tuple, list)):
            if len(entry) != 2:
                sys.exit(f"ERROR: bad INPUT_FILES entry {entry!r}; "
                         'use "name" or ("name", "route")')
            pairs.append((str(entry[0]), str(entry[1]).strip().lower()))
        else:
            pairs.append((str(entry), "auto"))
    return pairs


def resolve_files(entries, doc_dir: Path) -> list[InputFile]:
    """Turn entries into InputFile objects; stop on any problem."""
    files, problems = [], []
    for name, route in normalize_entries(entries):
        path = Path(name).expanduser()
        if not path.is_absolute():
            path = doc_dir / path

        if not path.is_file():
            problems.append(f"  not found:            {path}")
            continue
        if path.stat().st_size > MAX_UPLOAD_BYTES:
            problems.append(f"  larger than 500 MB:   {path}")
            continue
        if route not in ("auto",) + ROUTES:
            problems.append(f"  unknown route '{route}' (use {', '.join(ROUTES)}): {path}")
            continue

        auto_route, auto_mime = detect_route(path)

        if route == "auto":
            if auto_route is None:
                if UNKNOWN_TYPE_POLICY == "container":
                    route, mime = "container", container_mime(path)
                else:
                    problems.append(f"  unsupported type:     {path}")
                    continue
            else:
                route, mime = auto_route, auto_mime
        elif route == "document":
            if auto_mime not in ("application/pdf", "text/plain"):
                problems.append(f"  not PDF/text, cannot be a document: {path}")
                continue
            mime = auto_mime
        elif route == "image":
            if auto_route != "image":
                problems.append(f"  not jpg/png/gif/webp, cannot be an image: {path}")
                continue
            mime = auto_mime
        else:  # container accepts anything
            mime = container_mime(path)

        if route == "document" and mime == "text/plain":
            issue = check_text_file(path)
            if issue:
                problems.append(f"  {issue}: {path}")
                continue

        files.append(InputFile(path, route, mime))

    if problems:
        sys.exit("ERROR: problem(s) with input files:\n" + "\n".join(problems))
    if not files:
        sys.exit("ERROR: no input files given.")
    return files


def show_routing(files: list[InputFile]) -> None:
    """Print a table of how each file will be sent."""
    print(f"\n{'file':40} {'route':10} mime")
    print(f"{'-' * 40} {'-' * 10} {'-' * 28}")
    for f in files:
        print(f"{f.path.name[:40]:40} {f.route:10} {f.mime}")
    if any(f.route == "container" for f in files):
        print("\n(container files enable the code-execution tool for this run)")
    print()


# ---- upload / request ----------------------------------------------------

def upload_files(client: Anthropic, files: list[InputFile],
                 uploaded: list[InputFile]) -> None:
    """Upload each file. Successes are appended to `uploaded` immediately,
    so the caller can clean up even if a later upload fails."""
    for item in files:
        with open(item.path, "rb") as fh:
            # httpx needs a str filename, not a Path -> use path.name
            result = client.beta.files.upload(file=(item.path.name, fh, item.mime))
        item.file_id = result.id
        uploaded.append(item)
        print(f"Uploaded {item.path.name} [{item.route}] -> {result.id}")


def build_content(uploaded: list[InputFile], prompt: str) -> list[dict]:
    """Documents, labeled images and container uploads first; prompt last."""
    blocks: list[dict] = []
    container_names = []
    for item in uploaded:
        if item.route == "document":
            blocks.append({
                "type": "document",
                "source": {"type": "file", "file_id": item.file_id},
                "title": item.path.name,             # must be a str
            })
        elif item.route == "image":
            blocks.append({"type": "text", "text": f"Image: {item.path.name}"})
            blocks.append({
                "type": "image",
                "source": {"type": "file", "file_id": item.file_id},
            })
        else:
            blocks.append({"type": "container_upload", "file_id": item.file_id})
            container_names.append(item.path.name)

    if container_names:
        blocks.append({
            "type": "text",
            "text": ("These files were uploaded to your code-execution "
                     "container; open them with Python as needed: "
                     + ", ".join(container_names)),
        })
    blocks.append({"type": "text", "text": prompt})
    return blocks


def assistant_blocks(message) -> list:
    """Assistant content to send back, minus empty text blocks (API rejects them)."""
    return [b for b in message.content
            if not (b.type == "text" and not b.text.strip())]


def find_generated_file_ids(message) -> list[str]:
    """File ids of files Claude created in the sandbox during this pass."""
    ids = []
    for block in message.content:
        if block.type in ("bash_code_execution_tool_result",
                          "code_execution_tool_result"):
            result = getattr(block, "content", None)
            for item in getattr(result, "content", None) or []:
                fid = getattr(item, "file_id", None)
                if fid:
                    ids.append(fid)
    return ids


def run_query(client: Anthropic, messages: list[dict], out, *, model: str,
              max_tokens: int, max_continuations: int, system: str | None,
              use_code_execution: bool) -> list[str]:
    """Stream the reply to `out`. Continues automatically if the reply is cut
    off (max_tokens) or paused by a long tool run (pause_turn).
    Returns the ids of any files Claude generated."""
    betas = [FILES_API_BETA] + ([CODE_EXECUTION_BETA] if use_code_execution else [])
    container_id = None
    generated: list[str] = []

    for attempt in range(max_continuations + 1):
        request = dict(model=model, max_tokens=max_tokens,
                       messages=messages, betas=betas)
        if system:
            request["system"] = system
        if use_code_execution:
            request["tools"] = [CODE_EXECUTION_TOOL]
        if container_id:
            request["container"] = container_id       # reuse the same sandbox

        with client.beta.messages.stream(**request) as stream:
            for event in stream:
                if event.type == "content_block_start" and \
                        event.content_block.type == "server_tool_use":
                    out.write("\n[... Claude is running code in the sandbox ...]\n")
                    out.flush()
                elif event.type == "content_block_delta" and \
                        event.delta.type == "text_delta":
                    out.write(event.delta.text)
                    out.flush()                       # nothing lost if the run dies
            final = stream.get_final_message()

        print(f"Pass {attempt + 1}: stop_reason = {final.stop_reason}, "
              f"input tokens = {final.usage.input_tokens}, "
              f"output tokens = {final.usage.output_tokens}")

        container = getattr(final, "container", None)
        if container is not None:
            container_id = container.id
        generated.extend(find_generated_file_ids(final))

        if final.stop_reason not in ("max_tokens", "pause_turn"):
            return generated                          # finished normally

        if attempt == max_continuations:              # out of retries
            warning = ("\n\n[WARNING: reply still incomplete "
                       f"(stop_reason = {final.stop_reason}) after all "
                       "continuation passes. Raise MAX_TOKENS or "
                       "MAX_CONTINUATIONS.]\n")
            out.write(warning)
            print(warning)
            return generated

        blocks = assistant_blocks(final)
        if not blocks:
            print("Reply was empty -- cannot continue.")
            return generated
        messages.append({"role": "assistant", "content": blocks})

        if final.stop_reason == "max_tokens":
            messages.append({"role": "user", "content": CONTINUE_PROMPT})
            print("Reply hit max_tokens -- requesting continuation...")
        else:  # pause_turn: resend as-is so Claude resumes its own turn
            print("Long tool run paused -- resuming...")

    return generated


# ---- generated files / cleanup ------------------------------------------

def save_generated_files(client: Anthropic, file_ids: list[str],
                         out_dir: Path) -> None:
    """Download files Claude created, then delete them from the workspace."""
    for fid in dict.fromkeys(file_ids):               # de-duplicate, keep order
        try:
            meta = client.beta.files.retrieve_metadata(fid)
            dest = out_dir / f"{GENERATED_PREFIX}{meta.filename}"
            if dest.exists():
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = dest.with_name(f"{dest.stem}_{stamp}{dest.suffix}")
            client.beta.files.download(fid).write_to_file(dest)
            print(f"Saved generated file -> {dest}")
            client.beta.files.delete(fid)
        except Exception as e:
            print(f"Could not save generated file {fid}: {e}")


def delete_uploads(client: Anthropic, uploaded: list[InputFile]) -> None:
    """Delete just the files uploaded during this run."""
    for item in uploaded:
        try:
            client.beta.files.delete(item.file_id)
            print(f"Deleted {item.path.name} ({item.file_id})")
        except Exception as e:
            print(f"Could not delete {item.path.name} ({item.file_id}): {e}")


def purge_workspace(client: Anthropic) -> None:
    """Delete EVERY file in the Files workspace (asks for confirmation)."""
    files = list(client.beta.files.list())
    if not files:
        print("Workspace is already empty.")
        return
    answer = input(f"Delete ALL {len(files)} file(s) in the workspace? [y/N] ")
    if answer.strip().lower() != "y":
        print("Cancelled.")
        return
    for f in files:
        try:
            client.beta.files.delete(f.id)
            print(f"Deleted {f.filename} ({f.id})")
        except Exception as e:
            print(f"Could not delete {f.filename} ({f.id}): {e}")


# =========================================================================
#  SECTION 4 -- MAIN
# =========================================================================

def main() -> int:
    args = parse_args()

    if args.list_types:
        list_types()
        return 0

    if args.purge_all:
        purge_workspace(make_client())
        return 0

    # CLI files (if any) replace INPUT_FILES for this run
    cli_entries = list(args.files) + [(name, "container") for name in args.container]
    files = resolve_files(cli_entries or INPUT_FILES, args.dir)
    show_routing(files)

    if args.dry_run:
        print("Dry run -- nothing uploaded.")
        return 0

    prompt = resolve_prompt(args)
    client = make_client()
    output_path = args.dir / args.output
    mode = "w" if (args.overwrite or not APPEND_MODE) else "a"
    use_code_execution = any(f.route == "container" for f in files)

    uploaded: list[InputFile] = []
    try:
        upload_files(client, files, uploaded)
        messages = [{"role": "user", "content": build_content(uploaded, prompt)}]

        with open(output_path, mode, encoding="utf-8") as out:
            out.write(
                f"\n\n{'=' * 70}\n"
                f" Run: {datetime.now():%Y-%m-%d %H:%M:%S}  |  Model: {args.model}\n"
                f" Files: {', '.join(f'{f.path.name} [{f.route}]' for f in files)}\n"
                f"{'=' * 70}\n\n"
            )
            generated = run_query(
                client, messages, out,
                model=args.model,
                max_tokens=args.max_tokens,
                max_continuations=args.max_continuations,
                system=args.system,
                use_code_execution=use_code_execution,
            )
        print(f"Response written to {output_path}")

        if generated and DOWNLOAD_GENERATED_FILES:
            save_generated_files(client, generated, args.dir)
        return 0

    except anthropic.APIError as e:
        print(f"API ERROR: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted -- partial output (if any) was saved.", file=sys.stderr)
        return 130
    finally:
        delete_uploads(client, uploaded)              # always clean up


if __name__ == "__main__":
    sys.exit(main())

