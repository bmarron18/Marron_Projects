#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 11:35:19 2025
Updated 13 Oct 2026
@author: bmarron

-----------------------------------
UPDATE AND LIST INSTALLED PACKAGES
-----------------------------------
<<< bash
    cd ~/spyder-6/envs && source ./ai-apis/bin/activate  &&
    pip list &&
    python3 -m pip install --upgrade pip &&
    pip install --upgrade tiktoken tokenizers && 
    deactivate
>>>

"""

# %%

'''
TRIAL RUN
Tokenizing for Anthropic Claude Fable 5.1

'''

from tokenizers import Tokenizer

    # Use the verified open-source mirror of Anthropic's Claude tokenizer
try:
    tokenizer = Tokenizer.from_pretrained("Xenova/claude-tokenizer")
except Exception:
    # Alternate mirror repository
    tokenizer = Tokenizer.from_pretrained("Quivr/claude-tokenizer")

def count_fable_tokens_locally(text: str) -> int:
    encoded = tokenizer.encode(text)
    return len(encoded.ids)

# Test the setup
prompt = "Testing API limits for Claude Fable 5.1."
print(f"Claude Fable 5.1 Tokens (Local): {count_fable_tokens_locally(prompt)}")


# %%

'''
RUN
Tokenizing for Anthropic Claude Fable 5.1

'''

from tokenizers import Tokenizer

    # Use the verified open-source mirror of Anthropic's Claude tokenizer
try:
    tokenizer = Tokenizer.from_pretrained("Xenova/claude-tokenizer")
except Exception:
    # Alternate mirror repository
    tokenizer = Tokenizer.from_pretrained("Quivr/claude-tokenizer")

def count_fable_tokens_locally(text: str) -> int:
    encoded = tokenizer.encode(text)
    return len(encoded.ids)

# Test the setup
prompt = "Satellite data has been used to evaluate agricultural production for some time. Satellite data has also been used \
    to infer soil fecundity and bacterial-fungal ratios as well as other metrics of soil health and composition such \
    as soil organic carbon (SOC), pH, nitrogen, and Cation Exchange Capacity. More recently, drone data has also been used \
    evaluate soil health and crop vitality. Review peer-reviewed journals, textbooks, seminar and conference publications, \
    and all relevant source materials for the use and processing of satellite data as well as for the use and processing of drone \
    data in agriculture. With this information at hand, do the following:  1) Provide a high level summary of how each type of data \
    source (satellite data, drone data) are currently being used in agriculture. 2) Provide a detailed account of how satellite data \
    is obtained, processed, and evaluated for agricultural use. 3) Provide an infographic explaining how satellite data is obtained,\
    processed, and evaluated for agricultural use. The infographic should be developed in a Python script that can be run independently \
    to generate the infographic as a .jpeg file. 4) Provide a detailed account of how drone data is obtained, processed, and evaluated \
    for agricultural use. 5) Provide an infographic explaining how drone data is obtained, processed, and evaluated for agricultural use. \
    The infographic should be developed in a Python script that can be run independently to generate the infographic as a .jpeg file. 6) Provide \
    a list of foundational and canonical references that explain the process and theory for obtaining, processing, and evaluating satellite data \
    for agricultural use. 7) Provide a list of foundational and canonical references that explain the process and theory for obtaining,\
    processing, and evaluating satellite data for agricultural use. 8) Provide a list of sources for satellite data for agricultural use"




print(f"Claude Fable 5.1 Tokens (Local): {count_fable_tokens_locally(prompt)}")




