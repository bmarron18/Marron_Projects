#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 11:20:22 2025
updated: 11 Sept 2026
@author: bmarron

"""


# %%

'''
This script will:
1.  Read an English (or any other language) .pdf file.
2.  Construct a clear translator request (prompt + config) for the 
    Gemini 2.5 Flash model.
3.  Send the request to the Gemini 2.5 Flash model.
4.  Write the Spanish (or any other language) translation to 
    a new file type.

Document MIME types available for Gemini output:
    text/plain   ==> .txt
    text/html    ==> .html
    text/json    ==> ,json
    text/x-tex   ==> .tex
    
'''
# %%

'''
Simple Test Run

'''
from google import genai
from google.genai import types
import os


#--- API Key ---------------------
    # API_KEY is saved as an ENV VARIABLE on home compu
    # (See "Info_Gemini_API.txt for procedure)
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)



#--- The API call to the AI
    # ==> modify "prompt" (user level) as needed
    # ==> modify "system instruction" (behavior) as needed

prompt = "Write a one-sentence bedtime story about a unicorn."

response = client.models.generate_content(
    model = "gemini-3.7-flash",
    config = types.GenerateContentConfig(
               system_instruction="Talk like a pirate."),
    contents = [prompt]
    )

#--- Output from AI (response.text) ---

   # Send to IPython window
print(response.text)


'''
"The grand unicorn, her horn glintin' like a mast in the moonlight, \
snuggled deep into her cloud-hammock, dreamin' of sailin' across seas of \
stardust 'til the mornin' tide."

'''




# %%

'''
Translate content of .pdf files
    * returns UTF-8 output
    * output may be requested as any accepted MIME type file

'''


from google import genai
from google.genai import types
from pathlib import Path
import os


#--- API Key ---------------------
    # API_KEY is saved as an ENV VARIABLE on home compu
    # (See "Info_Gemini_API.txt for procedure)
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

    # API_KEY also can be inserted directly
#client = genai.Client(api_key=ACTUAL_API_KEY)



# --- Prep Files, and Define Files and File Paths -------
    # INPUT_FILE
       #==> this is the .pdf file (T)o (B)e (T)ranslated
       #==> Move .pdf file (T)o (B)e (T)ranslated to the Desktop
 
    # OUTPUT_FILE 
        #==> will hold the (T)ranslated text from the AI
        #==> this file will be generated automatically by Python after \
        # the translation is complete
   
    
    # Name the INPUT_FILE and OUTPUT_FILE
    # Change names of files as needed
        # ==> INPUT_FILE must stay as .pdf
        # ==> OUTPUT_FILE can be any of the Document types available for \
        # Gemini output (see header of this script)
    
INPUT_FILE = "Gemini_Doc-English_TBT.pdf"  
OUTPUT_FILE = "Gemini_Doc-Spanish_T.txt"


    # Set up the file paths for the INPUT_FILE and the OUTPUT_FILE
    # Set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_translate = INPUT_FILE
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"


    # create paths to files
    # Retrieve files as PosixPaths

input_filepath = os.path.join(doc_dir, doc_to_translate)
input_f = Path(input_filepath)

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)

 


#--- Read and process file to be translated ---
     # File NOT UPLOADED to Google
 
processedfile = types.Part.from_bytes(
        data=input_f.read_bytes(),
        mime_type='application/pdf'
        )


#--- The API call to the AI
    # ==> modify "prompt" (user level) as needed
    # ==> modify "system instruction" (behavior) as needed

prompt = "Translate the document, processedfile (a .pdf file in English) to \
    standard, natural, fluent Spanish. Maintain all specific formatting \
    (line breaks, indents, spaces, paragraphs, and quotations). Generate the \
    output as MIME type= text/plain. That is, generate the output as a \
    plain text file (.txt)."

response = client.models.generate_content(
    model = "gemini-3.1-pro-preview",
    config = types.GenerateContentConfig(
               system_instruction="You are an expert liguist \
                   specializing in translation. Maintain the original \
                   meaning, and tone of the original. Provide ONLY the \
                   requested translation without any additional commentary, \
                   introductory phrases, other language translations, or \
                   conversational remarks."),
    contents = [processedfile, prompt]
    )

#--- Output from AI (response.text) ---

   # Send to IPython window
#print(response.text)

    # Send to OUTPUT_FILE
GeminiOutput = response.text



with open(output_f, "w", encoding="utf-8") as f:
     f.write(GeminiOutput)
     
print(f"Translation complete! Translated text saved to '{output_f}'.")



# %%
'''
File Management: Files uploaded via client.files.upload are temporarily stored on Google's servers 
and are automatically deleted after 48 hours.

'''

from google import genai

# Initialize the client. It automatically picks up the GEMINI_API_KEY environment variable.
client = genai.Client()

# 1. Upload the PDF file to the Gemini File API
# Uploaded files are securely stored for 48 hours before automatic deletion
document = client.files.upload(file='path/to/your_document.pdf')

# 2. Call the Gemini 3.1 Pro model
response = client.models.generate_content(
    model='gemini-3.1-pro-preview', #
    contents=[
        "Translate this document to French. Maintain the original layout and section headers.", 
        document
    ]
)

# 3. Output the translated text
print(response.text)