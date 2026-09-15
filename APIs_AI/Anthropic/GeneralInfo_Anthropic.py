#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 12:12:12 2026

@author: bruce-vdb
"""

# %%

#########      Anthropic General        #####################

# %%

'''
Install SDK 

'''

# SDK
	pip install anthropic

# LATER.......For improved async performance with aiohttp
	pip install "anthropic[aiohttp]"

    # Install / Update anthropic SDK
cd ~/spyder-6/envs &&
source ./ai-apis/bin/activate
(ai-apis):$ pip install --upgrade anthropic &&
deactivate

    # as of 13 Sept 2026
Successfully installed anthropic-1.5.0 docstring-parser-0.18.0


# %%

'''
Max Tokens
'''

USE THIS!!
    max_tokens=16384

A max_tokens=4096 setting allows an AI model to generate a response of up to 4,096 output tokens 
(roughly 3,000 words or 12,000 characters) in a single reply.

Length: It is long enough to write a 6-to-10 page essay, a long programming script, or a detailed 
summary.

# %%



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

# Extract and print the response text
print(response.content[0].text)


# %%

When thinking is active, the Anthropic Messages API doesn't just return a 
single text block. Instead, response.content becomes an array of multiple blocks. 
The first block (content[0]) is frequently a ThinkingBlock, which has a .thinking 
attribute instead of .text

Instead of grabbing the first element indiscriminately, loop through the content 
block array or use a list comprehension to extract only the actual TextBlock 
components:
    
    # Extract and concatenate all text blocks from the response
text_content = "".join([block.text for block in response.content if block.type == "text"])

print(text_content)



Alternatively

for block in response.content:
    if block.type == "thinking":
        # Note: Depending on your 'display' config, block.thinking might contain a summary
        print(f"--- Claude's Thinking ---\n{block.thinking}\n")
    elif block.type == "text":
        print(f"--- Final Response ---\n{block.text}")



# %%



'''
Basic Usage.........NO GO!
'''

import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

message = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    system="You are a helpful and concise assistant.",  # Optional system prompt
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
)

for block in message.content:
    if block.type == "text":
        print(block.text)
        

# %%

'''
Async Usage
https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#async-usage

'''

import os
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


async def main() -> None:
    message = await client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude",
            }
        ],
        model="claude-opus-5",
    )
    print(message.content)


asyncio.run(main())


# %%

'''
Using aiohttp for better concurrency
https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python#using-aiohttp-for-better-concurrency

For improved async performance, you can use the aiohttp HTTP backend instead of the default httpx2:

'''


import os
import asyncio
from anthropic import AsyncAnthropic, DefaultAioHttpClient


async def main() -> None:
    async with AsyncAnthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        http_client=DefaultAioHttpClient(),
    ) as client:
        message = await client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, Claude",
                }
            ],
            model="claude-opus-5",
        )
        print(message.content)


asyncio.run(main())


# %%

'''
Multiple conversational turns
https://platform.claude.com/docs/en/build-with-claude/working-with-messages#multiple-conversational-turns

'''


message = anthropic.Anthropic().messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Can you describe LLMs to me?"},
    ],
)
print(message)

    # OUTPUT
{
  "id": "msg_018gCsTGsXkYJVqYPxTgDHBU",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Sure, I'd be happy to provide..."
    }
  ],
  "model": "claude-opus-5",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 30,
    "output_tokens": 309
  }
}

# %%

'''
Streaming responses (Messages API)

The SDK provides support for streaming responses using Server-Sent Events (SSE).
'''

import os
import asyncio
from anthropic import AsyncAnthropic, DefaultAioHttpClient


client = Anthropic()

stream = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-opus-5",
    stream=True,
)
for event in stream:
    print(event.type)

# %%

'''
File uploads
'''

from pathlib import Path
from anthropic import Anthropic

client = Anthropic()

# Upload using a file path
client.files.upload(
    file=Path("/path/to/file"),
)

# Upload using bytes
client.files.upload(
    file=("file.txt", b"my bytes", "text/plain"),
)


# %%

