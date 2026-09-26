# %%
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 19 2025
Modified  06 Nov 2025
@author: bmarron
"""


# %%

### Mime-type files ####

'''

Document MIME types available for OpenAI output:
    text/plain   ==> .txt
    text/html    ==> .html
    text/json    ==> ,json
    text/x-tex   ==> .tex
    
'''

# %%

'''
General Query Type I
Model ==> gpt-5
Shawn
    Multiple sclerosis (MS) 
        Symptoms
        Diagnosis
        Treatments
        Recommendations

'''


from openai import OpenAI
from pathlib import Path
import os


    # API_KEY is saved as an ENV VARIABLE on home compu
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

    # API_KEY can be inserted directly
#client = OpenAI(api_key="ACTUAL_API_KEY")


    # label of output file
OUTPUT_FILE = "GeneralQuery_gpt-5.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bmarron18/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)


	# User level message
user_prompt= "Evaluate the current state of medical knowledge about the autoimmune disease, \
    multiple sclerosis (MS). Specifically, i) highlight and summarize the symptoms of MS; \
    ii) detail the different diagnostic procedures used to confirm MS in an individual; iii) \
    briefly summarize and evaluate the current treatment options for MS; iv) evaluate the possible \
    synergistic effects of black mold exposure with MS; and v) provide a list \
    of recommendations for best practices for individuals with MS. Organize the output by \
    sections i - v above and deliver the output in MIME type text/plain."



	# Developer level message 1
sys_prompt = "You are an expert medical researcher specializing in autoimmune diseases \
    and clinical diagnoses. Provide ONLY the requested set of queries (i-v) above without any \
    additional commentary, or introductory phrases, or conversational remarks.Use medical \
    jargon sparingly and define all medical terms."




response = client.responses.create(
  model = "gpt-5",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")


# %%

