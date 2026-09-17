# %%
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 19 2025
Modified  12 Sept 2026
@author: bmarron
"""

This script must be run in a virtual envirnment:
    /home/bruce-mx/spyder-6/envs/ai-apis/bin/python3.12

    $ cd ~/spyder-6/envs
	$ python3 -m venv ai-apis
	$ source ./ai-apis/bin/activate


the following packages have been installed into (ai-apis:

    (ai-apis)$ pip install spyder-kernels google-genai openai
    (ai-apis)$ pip install pandas NumPy python-dateutil pytz tzdata
    (ai-apis)$ pip install "pandas[performance]"
    (ai-apis)$ pip install "pandas[computation]"
    (ai-apis)$ pip install plotnine
    (ai-apis)$ pip install pypdf[full]

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
General Query Type I : Python Code Production
Model ==> gpt-5.6

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
OUTPUT_FILE = "GeneralQuery_OpenAI.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)

    # Select/Unselect as needed


	# User level message
user_prompt= "Write the complete Python code for using OpenAI model gpt-live-transcribe \
    to translate real-time English spoken audio (input) to Spanish text (output) \
    with the ouput going to both the Python interpreter screen and to a simple \
    text file on my desktop (/home/bruce-vdb/Desktop). My computer's operating system \
    is Linux Mint 22.3 and I will be running the Python script in Spyder 6.1.7. "



	# Developer level message 
sys_prompt = "You are an expert Python code writer"



response = client.responses.create(
  model = "gpt-5.6",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")






# %%

'''
General Query Type I : Literature Analysis
Model ==> gpt-5.6

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
OUTPUT_FILE = "GeneralQuery.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)

    # Select/Unselect as needed


	# User level message
user_prompt= "Provide i) a brief summary, and ii) comprehension questions for Chapter 1\
    and Chapter 2 of Viet Thanh Nguyen's novel, 'The Sympathizer'. Chapter summaries as well as \
    comprehension questions should be at a college level. Summaries should not exceed one \
    paragraph per chapter. Comprehension questions should cover the important topics introduced \
    in each chapter plus detailed questions regarding the events that happen in each chapter. \
    The output response of summaries and questions should be organized by chapter."



	# Developer level message 
sys_prompt = "You are an expert literary scholar \
    specializing in  intrigue and spy novels. Provide ONLY the requested \
    summaries and questions without any additional commentary, introductory phrases, \
    or conversational remarks."




response = client.responses.create(
  model = "gpt-5.6",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")


