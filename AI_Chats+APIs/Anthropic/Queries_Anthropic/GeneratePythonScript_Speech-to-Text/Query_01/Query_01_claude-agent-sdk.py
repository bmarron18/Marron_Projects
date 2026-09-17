#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 12:59:50 2026

@author: bruce-vdb
"""

# %%
'''
Query ==  Create speech-to-text interpretor script
Model ==> claude-opus-5
'''

import os
from pathlib import Path
import anthropic
from anthropic import Anthropic


   # label of output file
OUTPUT_FILE = "Query_01_Anthropic.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"   


    # create paths to files
    # Retrieve files as PosixPaths

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)



    # pick up the ANTHROPIC_API_KEY environment variable
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


content = "Write a complete Python script for using the newest OpenAI models \
    to do the following real-time tasks: 1. listen to real-time English spoken audio from my computer's microphone \
    (input 1); 2. transcribe the English audio to English text (outut 1);  3. translate the English text to \
    Spanish text; and 4. transcribe the Spanish text (output 2). The transcribed texts, both  output 1 and output 2 \
    should go to to a simple text file on my desktop (/home/bruce-vdb/Desktop). \
    The transcribed Spanish text (output 2)  also should go to the Python screen. I plan to run the script in a \
    virtual environment. My computer's operating system is Linux Mint 22.3. "

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=16384,   # if go over this script crashes bc need streaming to API
    system="You are a helpful and concise Python coding assistant.",  # Optional system prompt
    messages=[
        {
            "role": "user",
            "content": content,
        }
    ],
)


'''
for block in response.content:
    if block.type == "thinking":
        # Note: Depending on your 'display' config, block.thinking might contain a summary
        print(f"--- Claude's Thinking ---\n{block.thinking}\n")
    elif block.type == "text":
        print(f"--- Final Response ---\n{block.text}")
'''


    # Extract and concatenate all text blocks from the response
text_content = "".join([block.text for block in response.content if block.type == "text"])


    # Extract and print the response text
with open(output_f, "a", encoding="utf-8") as f:
    f.write(text_content)


print(f"Query complete! Outputsaved to '{output_f}'.")

# %%


