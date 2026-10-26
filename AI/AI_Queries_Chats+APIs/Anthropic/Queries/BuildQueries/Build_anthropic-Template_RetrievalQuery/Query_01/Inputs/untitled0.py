#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 16:00:13 2026

@author: bruce-vdb
"""

import os
import json
from anthropic import Anthropic

# 1. Initialize the client (Make sure your ANTHROPIC_API_KEY environment variable is set)
client = Anthropic()

# 2. Set your specific Batch ID and output files
BATCH_ID = "YOUR_BATCH_ID_HERE"  # <-- Replace with your actual Batch ID
SUCCESS_FILE = "successful_results.jsonl"
FAILED_FILE = "failed_results.jsonl"

print(f"Fetching results for batch: {BATCH_ID}...")

try:
    # 3. Retrieve the results stream from Anthropic
    # The results endpoint returns an iterable stream of the entire batch execution
    results_stream = client.messages.batches.results(BATCH_ID)
    
    success_count = 0
    failure_count = 0
    
    # 4. Open our output files and process line-by-line
    with open(SUCCESS_FILE, "w", encoding="utf-8") as success_out, \
         open(FAILED_FILE, "w", encoding="utf-8") as failed_out:
         
        for result in results_stream:
            # Convert the result object to a dictionary/JSON structure
            result_dict = result.model_dump()
            
            # Check if this specific item in the batch succeeded
            if result_dict.get("result", {}).get("type") == "succeeded":
                success_out.write(json.dumps(result_dict) + "\n")
                success_count += 1
            else:
                failed_out.write(json.dumps(result_dict) + "\n")
                failure_count += 1

    print("\nProcessing complete!")
    print(f" Saved {success_count} successful items to: {SUCCESS_FILE}")
    print(f" Saved {failure_count} failed/incomplete items to: {FAILED_FILE}")

except Exception as e:
    print(f"\nAn error occurred while fetching the batch: {e}")
    print("Ensure your API key is valid and the Batch ID is correct.")
