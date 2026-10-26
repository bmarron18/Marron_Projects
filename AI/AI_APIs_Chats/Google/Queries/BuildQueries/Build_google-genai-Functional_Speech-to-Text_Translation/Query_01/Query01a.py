#!/usr/bin/env python3
"""
Created on Mon Dec 30 21:54:30 2024
updated: 11 Sept 2026
@author: bmarron
"""


# %%

'''
Get Python Code for Using "gemini-3.5-transcribe-live"

'''

from google import genai
from pathlib import Path
import os


#--- API Key ---------------------
    # API_KEY is saved as an ENV VARIABLE on home compu
    # (See "Info_Gemini_API.txt for procedure)
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)


OUTPUT_FILE = "PythonCode.txt"
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)


response = client.models.generate_content(
    model="gemini-3.7-flash", 
    contents="Write the complete Python code for using gemini-3.5-transcribe-live \
        to translate real-time English spoken audio (input) to Spanish text (output) \
        with the ouput going to both the Python interpreter screen and to a simple \
        text file on my desktop (/home/bruce-vdb/Desktop). My computer's operating system \
        is Linux Mint 22.3 and I will be running the Python script in Spyder 6.1.7. ")
        
    # Toggle to send to screen    
#print(response.text)

   # Send to OUTPUT_FILE
GeminiOutput = response.text

with open(output_f, "w", encoding="utf-8") as f:
     f.write(GeminiOutput)
     
print(f"Request complete! Saved to '{output_f}'.")


# %%



