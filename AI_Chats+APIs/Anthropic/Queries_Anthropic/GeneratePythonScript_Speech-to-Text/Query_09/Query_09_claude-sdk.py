#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 18:27:38 2026
Revised  17 Sep 2026 09:39 PM CST
Revised  18 Sep 2026 -- streaming + full-output capture (fixes truncated output)
@author: bruce-vdb, Claude Sonnet 5
"""


# %%


from anthropic import Anthropic
from datetime import datetime
from pathlib import Path
import os


#======== Location of Input / Output files  ===================
    # Working on the Desktop
doc_dir = "/home/bruce-vdb/Desktop"


#======== Output file  ===================
   # a .txt file on Desktop
OUTPUT_FILE = "Response_Anthropic.txt"
output_f = Path(os.path.join(doc_dir, OUTPUT_FILE))

    # True  = append each run to the file (a dated separator marks each run)
    # False = overwrite the file on every run
APPEND_MODE = True


#======== Model / output-size settings  ===================
MODEL = "claude-opus-5"   # or another current model id

    # The reply is cut off when it hits max_tokens (stop_reason == "max_tokens").
    # A complete script can easily exceed 16,384 tokens, so this is set higher.
    # If the API rejects the value, lower it to your model's maximum output limit.
MAX_TOKENS = 64000

    # If the reply is STILL cut off, ask Claude to continue, up to this many times
MAX_CONTINUATIONS = 3


#======== Input files  ===================
   # Accepts .pdf 
       # ==> MIME "application/pdf"
   # Accepts plain-text files (.txt, .md, .csv, .py) 
       # ==> MIME "text/plain"
   # Accepts plain-text files (.csv) 
       # ==> MIME "text/csv"
   # Accepts image files (.jpeg, .png, .gif, .webp) 
       # ==> MIME "image/jpeg"
       # ==> MIME "image/png"
       # ==> MIME "image/gif"
       # ==> MIME "image/webp"
    # Replace name(s)
    # Comment out uneeded file types


'''
    # .pdf file
INPUT_FILE_01 = "report_q3.pdf"
input_f1 = Path(os.path.join(doc_dir, INPUT_FILE_01))

    # plain-text file
INPUT_FILE_02 = "architecture_notes.txt"
input_f2 = Path(os.path.join(doc_dir, INPUT_FILE_02))

    # image file
INPUT_FILE_03 = "diagram.png"
input_f3 = Path(os.path.join(doc_dir, INPUT_FILE_03))
'''


    # plain-text file
INPUT_FILE_01 = "X_Speech-to-text_Gemini-API_Live_v1.6.py"
input_f1 = Path(os.path.join(doc_dir, INPUT_FILE_01))

    # plain-text file
INPUT_FILE_02 = "RunLog.txt"
input_f2 = Path(os.path.join(doc_dir, INPUT_FILE_02))






#========= Client for billing ===========================
    # API_KEY is saved as an ENV VARIABLE on home computer
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


    # 1. Upload each file once — you get back a file_id you can reuse
    #  across as many Messages requests as you like.

#========= Upload files for review ===========================
   # File type must match MIME type in the files_to_review [list]
files_to_review = [
    (input_f1, "text/plain"),
    (input_f2, "text/plain"),
]

uploaded = []
for filename, mime_type in files_to_review:
    with open(filename, "rb") as f:
        # NOTE: the httpx multipart encoder requires a plain str filename,
        # not a pathlib.Path -- passing `filename` directly raises
        # "TypeError: expected string or bytes-like object, got 'PosixPath'".
        # `filename.name` gives the basename as a str (e.g. "script.py").
        result = client.files.upload(file=(filename.name, f, mime_type))
    uploaded.append((filename, result.id, mime_type))
    print(f"Uploaded {filename} -> {result.id}")


#========= Build the content blocks for the message ===============
    # PDFs and .txt/.md/.csv (text/plain) use a "document" block
    # images use an "image" block
content_blocks = []
for filename, file_id, mime_type in uploaded:
    if mime_type.startswith("image/"):
        content_blocks.append({
            "type": "image",
            "source": {"type": "file", "file_id": file_id},
        })
    else:
        content_blocks.append({
            "type": "document",
            "source": {"type": "file", "file_id": file_id},
            # same fix: title must be a str, not a Path
            "title": filename.name,
        })

#========== User prompt =================================
    # Put the user prompt last (or first) alongside the file blocks
    # (adjacent string literals -- no stray indentation inside the prompt)
content_blocks.append({
    "type": "text",
    "text": (
        "The attached Python script (input_f1) passes initial checks but throws errors. \
        The output from the checks and the attempted run are given in the RunLog.txt file \
        (input_f2).  Please review the RunLog.txt file, double-check the code in the Python script,\
        analyze the problem, and rewrite the script with the recommended changes. \
        Provide a copy of the entire revised script."
    ),
})



#======== Send the query, stream the reply, write it to the file ==========
    # Why streaming?
    #  - Large max_tokens values require streaming in the Anthropic SDK
    #    (long non-streaming requests can time out).
    #  - Every text chunk is written and flushed to disk as it arrives, so
    #    nothing is lost even if the connection drops part-way through.
    #  - stop_reason tells us WHY the reply ended. "max_tokens" means the
    #    reply was cut off -- that is what truncated the original output.

messages = [{"role": "user", "content": content_blocks}]

try:
    with open(output_f, "a" if APPEND_MODE else "w", encoding="utf-8") as out:
        out.write(
            f"\n\n{'=' * 70}\n"
            f" Run: {datetime.now():%Y-%m-%d %H:%M:%S}  |  Model: {MODEL}\n"
            f"{'=' * 70}\n\n"
        )

        for attempt in range(MAX_CONTINUATIONS + 1):
            collected = []

            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:      # only text deltas
                    collected.append(text)
                    out.write(text)
                    out.flush()
                final = stream.get_final_message()

            print(
                f"Pass {attempt + 1}: stop_reason = {final.stop_reason}, "
                f"output tokens = {final.usage.output_tokens}"
            )

            # Finished normally ("end_turn", "stop_sequence", etc.)
            if final.stop_reason != "max_tokens":
                break

            # Cut off by the token limit
            if attempt == MAX_CONTINUATIONS:
                warning = (
                    "\n\n[WARNING: output was still cut off at the token limit "
                    "after all continuation attempts. Raise MAX_TOKENS or "
                    "MAX_CONTINUATIONS.]\n"
                )
                out.write(warning)
                print(warning)
                break

            # Ask Claude to pick up exactly where it stopped
            messages.append({"role": "assistant", "content": "".join(collected)})
            messages.append({
                "role": "user",
                "content": (
                    "Your previous reply was cut off by the output-token limit. "
                    "Continue exactly where you stopped -- no preamble, no "
                    "repeated text."
                ),
            })
            print("Reply hit max_tokens -- requesting continuation...")

    print(f"Response written to {output_f}")

#============ Handle fate of input files ============================
    # Delete from workspace just the files you uploaded in this run
    # (in `finally`, so uploads are cleaned up even if the query fails)
finally:
    for filename, file_id, mime_type in uploaded:
        try:
            client.files.delete(file_id)
            print(f"Deleted {filename} ({file_id})")
        except Exception as e:
            print(f"Could not delete {filename} ({file_id}): {e}")

# %%

'''
    # Delete every file in the workspace
for file in client.files.list():
    client.files.delete(file.id)
    print(f"Deleted {file.filename} ({file.id})")
'''
