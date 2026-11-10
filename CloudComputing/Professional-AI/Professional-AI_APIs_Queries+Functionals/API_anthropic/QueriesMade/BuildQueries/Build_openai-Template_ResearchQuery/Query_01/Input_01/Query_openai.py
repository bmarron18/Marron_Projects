# %%
# -*- coding: utf-8 -*-

"""
Created on 24 Sept 2026
@author: bmarron

==================================
Query: Ecosanitation
Model ==> gpt-6-astra
==================================


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
    * *Run* (f5)


RUN SCRIPT FROM DESKTOP
------------------
On Desktop
    * copy of this script

<<<bash
    cd ~/spyder-6/envs && 
    source ./ai-apis/bin/activate

        # run script
    python3  ~/Desktop/A_translate_docs_gemini_v2.0.py --dry-run
>>>

"""


from openai import OpenAI
from pathlib import Path
import os


    # API_KEY is saved as an ENV VARIABLE on home compu
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    # label of output file
OUTPUT_FILE = "EcosanQuery_OpenAI.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths
output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)



	# User level message
user_prompt= "Write the complete Python code for using OpenAI model, 'gpt-live-transcribe' \
    to take real-time English spoken audio (input), translate the spoken audio to Spanish, and \
    send the translated text to both the Python interpreter screen and to a simple \
    text file on my desktop (/home/bruce-vdb/Desktop). My computer's operating system \
    is Linux Mint 22.3 and I will be running the Python script in a virtual environment \
    in Spyder 6.1.7. "


	# Developer level message 
sys_prompt = "You are an expert Python code writer and debugger."



response = client.responses.create(
  model = "gpt-6-astra",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")






