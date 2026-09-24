# %%
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 19 2025
Modified  29 Jan 2026
@author: bmarron
"""

This script must be run in a virtual envirnment:
    /home/bmarron18/spyder-6/envs/ai-apis/bin/python3.11


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
Model ==> gpt-5.2
The Sympathizer:
    Major Themes Ch1 - Ch 12
    Major Themes Ch 13 - Ch 23
    Summaries and Questions Ch 1 - Ch 12
    Summaries and Questions Ch 13 - Ch 23

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
OUTPUT_FILE = "GeneralQuery_gpt-5.2.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
    
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bmarron18/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths

output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)

    # Select/Unselect as needed

'''
	# User level message 1
user_prompt= "Provide a list of major themes in Viet Thanh Nguyen's novel, 'The Sympathizer'. The \
    analysis of the themes should be quite detailed and at a college level. The output response of \
    of the themes should be organized by chapter for Chapter 13 through Chapter 23."
'''

	# User level message 2
user_prompt= "Provide i) a brief summary, and ii) comprehension questions for Chapter 13 through \
    Chapter 23 of Viet Thanh Nguyen's novel, 'The Sympathizer'. Chapter summaries as well as \
    comprehension questions should be at a college level. Summaries should not exceed one \
    paragraph per chapter. Comprehension questions should cover the important topics introduced \
    in each chapter plus detailed questions regarding the events that happen in each chapter. \
    The output response of summaries and questions should be organized by chapter."



'''
	# Developer level message 1
sys_prompt = "You are an expert literary scholar \
    specializing in intrigue and spy novels. Provide ONLY the requested \
    list of major themes without any additional commentary, introductory phrases, \
    or conversational remarks."
'''

	# Developer level message 2
sys_prompt = "You are an expert literary scholar \
    specializing in  intrigue and spy novels. Provide ONLY the requested \
    summaries and questions without any additional commentary, introductory phrases, \
    or conversational remarks."




response = client.responses.create(
  model = "gpt-5.2",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")


# %%

'''
General Query Type II
Model ==> gpt-5
 Probability:
         

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

'''
	# User level message 1
user_prompt= "Provide a list of major themes in Aldous Huxley's novel, 'Brave New World'. The \
    analysis of the themes should be quite detailed and at a college level. The output response of \
    of the themes should be organized by chapter."


	# User level message 2
user_prompt= "Provide i) a brief summary, and ii) comprehension questions for chapters \
    one through nine of Aldous Huxley's novel, 'Brave New World'. Chapter summaries as well as \
    comprehension questions should be at a 9th grade level. Summaries should not exceed one \
    paragraph per chapter. Comprehension questions should cover the important topics introduced \
    in each chapter plus detailed questions regarding the events that happen in each chapter. \
    The output response of summaries and questions should be organized by chapter."
'''

	# User level message 3
user_prompt= "Provide i) a brief summary, and ii) comprehension questions for chapters \
    ten through eighteen of Aldous Huxley's novel, 'Brave New World'. Chapter summaries as well as \
    comprehension questions should be at a 9th grade level. Summaries should not exceed one \
    paragraph per chapter. Comprehension questions should cover the important topics introduced \
    in each chapter plus detailed questions regarding the events that happen in each chapter. \
    The output response of summaries and questions should be organized by chapter."


'''
	# Developer level message 1
sys_prompt = "You are an expert literary scholar \
    specializing in science fiction and dystopian futures. Provide ONLY the requested \
    list of major themes without any additional commentary, introductory phrases, \
    or conversational remarks."
'''

	# Developer level message 2
sys_prompt = "You are an expert literary scholar \
    specializing in science fiction and dystopian futures. Provide ONLY the requested \
    summaries and questions without any additional commentary, introductory phrases, \
    or conversational remarks."



response = client.responses.create(
  model = "gpt-5",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")