#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 12:59:50 2026

@author: bruce-vdb
"""

# %%

'''
Test Run
'''

import os
from pathlib import Path
import anthropic
from anthropic import Anthropic


client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


# Create a message request to Claude Opus 5
response = client.messages.create(
    model="claude-opus-5",
    max_tokens=4096,  # Set an appropriate ceiling for the output tokens
    system="You are a helpful and concise assistant.",  # Optional system prompt
    messages=[
        {
            "role": "user",
            "content": "Explain the concept of quantum computing in one short paragraph."
        }
    ]
)

    # Extract and concatenate all text blocks from the response
text_content = "".join([block.text for block in response.content if block.type == "text"])

# Extract and print the response text
print(text_content)

# %%



        