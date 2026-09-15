# %%
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 19 2025
Modified  06 Au 2026
@author: bmarron
"""

# %%

This script must be run in a virtual envirnment (ai-apis). Set Spyder to run in (ai-apis) by
pointing the Python interpreter (found under the Wrench) to:
    /home/bruce-vdb/spyder-6/envs/ai-apis/bin/python3.12

To create the virtual env, ai-apis
    $ cd ~/spyder-6/envs
	$ python3 -m venv ai-apis
	$ source ./ai-apis/bin/activate


the following packages have been installed into (ai-apis):

    (ai-apis)$ pip install spyder-kernels google-genai openai
    (ai-apis)$ pip install pandas NumPy python-dateutil pytz tzdata
    (ai-apis)$ pip install "pandas[performance]"
    (ai-apis)$ pip install "pandas[computation]"
    (ai-apis)$ pip install plotnine
    (ai-apis):~$ deactivate
    


"pandas[performance]" contains:
    numexpr
    bottleneck
    numba
    
"pandas[computation]" contains:
    SciPy
    xarray
    
# %%

    # Update openai SDK
$ cd ~/spyder-6/envs
$ source ./ai-apis/bin/activate
$ (ai-apis):$ pip install --upgrade openai
$ (ai-apis):~$ deactivate


# %%
    # Sending files
To send files to the OpenAI API, you typically perform a two-step process: 
first, you upload the file to the Files API to obtain a unique file_id, and 
then you pass that ID into a specific tool or feature like Assistants, 
Vector Stores, or the Responses API.


# %%

### Translation of mime-type = "application/pdf" files ####

'''
This script will:
1.  Read an English (or any other language) .pdf file.
2.  Construct a clear translator request for an OpenAI model
    (gpt-4o, gpt-5, etc).
3.  Send the request to the OpenAI model.
4.  Write the Spanish (or any other language) translation to 
    a new file type.

Document MIME types available for OpenAI output:
    text/plain   ==> .txt
    text/html    ==> .html
    text/json    ==> ,json
    text/x-tex   ==> .tex
    
'''

# %%

'''
Simple Test Run
Model ==> gpt-5.5

'''

import os
from openai import OpenAI

    # API_KEY is saved as an ENV VARIABLE on home compu
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

    # API_KEY can be inserted directly
#client = OpenAI(api_key=ACTUAL_API_KEY)


response = client.responses.create(
  model = "gpt-5.5",
#  temperature = 1.3,
  instructions = "Talk like a pirate.",
  input = "Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)


# %%

'''
Sample Output
'''

Arr matey, once upon a time, atop the moonlit waves o' dreamland, pranced a 
shimmering unicorn, whose horn sparkled with such magic it sent the young 
pirate driftin' to sleep among the stars.

On a moonlit tide o’ clouds, a wee unicorn with a starry horn sailed soft to Dreamland, sharin’ gentle sparkle-lullabies till every lad an’ lass drifted off t’ sweet sleep, arrr.

Under the silver moon, a gentle unicorn sailed through a sea of stars, whisperin’ sweet dreams to every sleepy critter in the enchanted forest, arrr.


# %%

'''
Translate content of .pdf files
    * returns UTF-8 output
    * output may be requested as any accepted MIME type file
    * Model ==> gpt-5.6

'''


from openai import OpenAI
from pathlib import Path
import os

    # API_KEY is saved as an ENV VARIABLE on home compu
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

    # API_KEY is inserted directly
#client = OpenAI(api_key="ACTUAL_API_KEY")




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
       # OpenAI output (see header of this script)
    
INPUT_FILE = "OpenAI_Doc-English_TBT.pdf"  
OUTPUT_FILE = "OpenAI_Doc-Spanish_T.txt"
    
    
    # set up the file paths for the INPUT_FILE and the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_translate = INPUT_FILE
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bmarron18/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths

input_filepath = os.path.join(doc_dir, doc_to_translate)
input_f = Path(input_filepath)

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)


#--- Read and process file to be translated ---

    # File accessed but NOT UPLOADED to OpenAI
    # creates a file.id value    
file = client.files.create(
    file=open(input_f, "rb"),
    purpose="user_data",
)


	# User level message
user_prompt= "Translate the file (a .pdf file in English) to standard, natural, \
    and fluent Spanish. Maintain all specific formatting (line breaks, \
    indents, spaces, paragraphs, and quotations). Generate the output as \
    MIME type= text/plain. That is, generate the output as a plain text \
    file (.txt)."


	# Developer level message
sys_prompt = "You are an expert linguist \
    specializing in translation. Maintain the original \
    meaning and tone. Provide ONLY the requested translation without \
    any additional commentary, introductory phrases, other language \
    translations or conversational remarks."



	# Response API call
response = client.responses.create(
    model="gpt-5.6",
#    temperature=1.3,
    instructions= sys_prompt,
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": user_prompt,
                },
            ]
        }
    ]
)


#--- Output from AI (response.output_text) ---

	# Send to IPython window
#print(response.output_text)


   # Send to OUTPUT_FILE
#with open(output_f, "w", encoding="latin-1") as f:
with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Translation complete! Translated text saved to '{output_f}'.")


