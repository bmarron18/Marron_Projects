#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 18:27:38 2026

@author: bruce-vdb, Claude Sonnet 5
"""


# %%


import anthropic
from openai import OpenAI
from pathlib import Path
import os


#======== Location of Input / Output files  ===================
    # Working on the Desktop
doc_dir = "/home/bruce-vdb/Desktop"


#======== Output file  ===================
   # a .txt file on Desktop
OUTPUT_FILE = "Query_Anthropic.txt"
output_f = Path(os.path.join(doc_dir, OUTPUT_FILE))


#======== Input files  ===================
   # Accepts .pdf 
       # ==> MIME "application/pdf"
   # Accepts plain-text files (.txt, .md, .csv) 
       # ==> MIME "text/plain"
   # Accepts image files (.jpeg, .png, .gif, .webp) 
       # ==> MIME "image/jpeg"
       # ==> MIME "image/png"
       # ==> MIME "image/gif"
       # ==> MIME "image/webp"

    # .pdf file type
INPUT_FILE_01 = "report_q3.pdf"
input_f1 = Path(os.path.join(doc_dir, INPUT_FILE_01))

    # plain-text file type
INPUT_FILE_02 = "architecture_notes.txt"
input_f2 = Path(os.path.join(doc_dir, INPUT_FILE_02))

    # image file type
INPUT_FILE_03 = "diagram.png"
input_f3 = Path(os.path.join(doc_dir, INPUT_FILE_03))


#========= Client for billing ===========================
    # API_KEY is saved as an ENV VARIABLE on home computer
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    # 1. Upload each file once — you get back a file_id you can reuse
    #  across as many Messages requests as you like.

#========= Upload files for review ===========================
   # File type must match MIME type in the files_to_review [list]
files_to_review = [
    (input_f1, "application/pdf"),
    (input_f2, "text/plain"),
    (input_f3, "image/png"),
]

uploaded = []
for filename, mime_type in files_to_review:
    with open(filename, "rb") as f:
        result = client.files.upload(file=(filename, f, mime_type))
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
            "title": filename,
        })

#========== User prompt =================================
    # Put the user prompt last (or first) alongside the file blocks
content_blocks.append({
    "type": "text",
    "text": (
        "Please review these files together. Summarize each one, "
        "flag inconsistencies between them, and note anything that "
        "needs follow-up."
    ),
})


#======== Send everything in one query (Messages request) ==================
response = client.messages.create(
    model="claude-sonnet-4-6",  # or another current model id
    max_tokens=2048,
    messages=[{"role": "user", "content": content_blocks}],
)

#================ Output from query =======================
    # Print to screen (if needed)
#for block in response.content:
#    if block.type == "text":
#        print(block.text)
        
        
    # Extract and concatenate all text blocks from the response
text_content = "".join([block.text for block in response.content if block.type == "text"])


    # Extract and print the response text
with open(output_f, "a", encoding="utf-8") as f:
    f.write(text_content)


#============ Handle fate of input files ============================
    # Delete from workspace just the files you uploaded in this run
for filename, file_id, mime_type in uploaded:
    client.files.delete(file_id)
    print(f"Deleted {filename} ({file_id})")
 
# %%

'''
    # Delete every file in the workspace
for file in client.files.list():
    client.files.delete(file.id)
    print(f"Deleted {file.filename} ({file.id})")
'''

