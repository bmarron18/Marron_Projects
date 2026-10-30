#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 19:44:47 2026

@author: Claude Sonnet 5
"""

# %%


import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

# 1. Upload each file once — you get back a file_id you can reuse
#    across as many Messages requests as you like.
files_to_review = [
    ("report_q3.pdf", "application/pdf"),
    ("architecture_notes.txt", "text/plain"),
    ("diagram.png", "image/png"),
]

uploaded = []
for filename, mime_type in files_to_review:
    with open(filename, "rb") as f:
        result = client.files.upload(file=(filename, f, mime_type))
    uploaded.append((filename, result.id, mime_type))
    print(f"Uploaded {filename} -> {result.id}")

# 2. Build the content blocks for the message.
#    - PDFs and .txt/.md/.csv (text/plain) use a "document" block
#    - images use an "image" block
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

# Put the instruction text last (or first) alongside the file blocks
content_blocks.append({
    "type": "text",
    "text": (
        "Please review these files together. Summarize each one, "
        "flag inconsistencies between them, and note anything that "
        "needs follow-up."
    ),
})

# 3. Send everything in one Messages request
response = client.messages.create(
    model="claude-sonnet-4-6",  # or another current model id
    max_tokens=2048,
    messages=[{"role": "user", "content": content_blocks}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
        
