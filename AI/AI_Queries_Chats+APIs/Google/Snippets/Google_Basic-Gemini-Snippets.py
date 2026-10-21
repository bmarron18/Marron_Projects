#!/usr/bin/env python3
"""
Created on Mon Dec 30 21:54:30 2024
updated: 11 Sept 2026
@author: bmarron
"""

# %%

    # in Linux terminal in virtual environment 
$ pip install google-genai
$ pip install --upgrade google-genai

    # as of 11 Sept 2026
google-genai-2.23.0



# %%
'''
Note options for interaction
'''
https://ai.google.dev/gemini-api/docs/text-generation


# Basic
response = client.models.generate_content(
    model="gemini-3.6-flash"
    )


# Potentially interactive
interaction = client.interactions.create(
    model="gemini-3.7-flash"
    )


# Full scale AI agent
interaction = client.interactions.create(
    agent="antigravity-preview-05-2026"
    )


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

# %%

'''
Analyze Python Code for Using "gemini-3.5-transcribe-live"
'''

    # NB
'''
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. 
Instead, we recommend to use AFC in Chat.send_message. 

Similarly, direct use of AFC in Models.generate_content_stream is not recommended. 
Instead, we recommend to use AFC in Chat.send_message_stream.

'''

from google import genai
from pathlib import Path
import os


#--- API Key ---------------------
    # API_KEY is saved as an ENV VARIABLE on home compu
    # (See "Info_Gemini_API.txt for procedure)
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

INPUT_FILE = "BadPythonCode.py"
OUTPUT_FILE = "Analysis.txt"

doc_to_analyze = INPUT_FILE
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"


input_filepath = os.path.join(doc_dir, doc_to_analyze)
input_f = Path(input_filepath)
output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)

processedfile = types.Part.from_bytes(
        data=input_f.read_bytes(),
        mime_type='text/plain'
        )

prompt = "Analyze the Python code in the attached script. The script uses \
    gemini-3.5-transcribe-live to translate real-time English spoken audio (input) to Spanish text (output) \
    with the ouput going to both the Python interpreter screen and to a simple \
    text file on my desktop (/home/bruce-vdb/Desktop). My computer's operating system \
    is Linux Mint 22.3 and I will be running the Python script in Spyder 6.1.7. The script runs but \
    does not output any translated text. Make any recommend changes to the script and re-wrtte the \
    new, corrected script to the output file"

response = client.models.generate_content(
    model="gemini-3.8-flash", 
    contents=[processedfile, prompt]
    )
        
    # Toggle to send to screen    
#print(response.text)

   # Send to OUTPUT_FILE
GeminiOutput = response.text

with open(output_f, "w", encoding="utf-8") as f:
     f.write(GeminiOutput)
     
print(f"Request complete! Saved to '{output_f}'.")






        
# %%

from googletrans import Translator

def translate_spanish_to_english():
    """
    Prompts the user for Spanish text and translates it to English.
    The translation continues until the user types 'quit'.
    """
    translator = Translator()

    print("--- Spanish to English Translator ---")
    print("Enter Spanish text to translate, or type 'quit' to exit.")
    print("-" * 35)

    while True:
        spanish_text = input("\nSpanish Text: ")

        if spanish_text.lower() == 'quit':
            print("Exiting translator. ¡Hasta luego!")
            break
        elif not spanish_text.strip():
            print("Please enter some text to translate.")
            continue

        try:
            # Translate from Spanish ('es') to English ('en')
            # The 'src' and 'dest' parameters ensure correct language detection,
            # though the library often auto-detects well.
            translation = translator.translate(spanish_text, src='es', dest='en')

            print(f"English Translation: {translation.text}")
        except Exception as e:
            print(f"An error occurred during translation: {e}")
            print("Please check your internet connection or try again later.")
            print("If the issue persists, the unofficial 'googletrans' library might be experiencing temporary issues.")

# --- Run the translator prompt (in terminal as .py script ---
if __name__ == "__main__":
    translate_spanish_to_english()


# %%


### Example Interaction:

```
--- Spanish to English Translator ---
Enter Spanish text to translate, or type 'quit' to exit.
-----------------------------------

Spanish Text: Hola, ¿cómo estás?
English Translation: Hello, how are you?

Spanish Text: El sol brilla hoy.
English Translation: The sun shines today.

Spanish Text: Me gusta aprender Python.
English Translation: I like to learn Python.

Spanish Text: quit
Exiting translator. ¡Hasta luego!
```

# %%

'''
Python Code Prompt: Spanish to English Translator

'''

from google import genai


# Set the API Key
    # Get my Gemini API Key here:
    # /home/bmarron/Desktop/UTECA/GithubToken_UTECALogins.txt
    API_KEY = "MY_KEY_ALPHANUMERIC"
client = genai.Client(api_key=API_KEY)


response = client.models.generate_content(
    model="gemini-3.7-flash", 
    contents="Write a Python code prompt to translate from \
        Spanish into English")
print(response.text)


# %%

from google import genai

    # Set the API Key
 
    
API_KEY = "MY_KEY_ALPHANUMERIC"
client = genai.Client(api_key=API_KEY)


response = client.models.generate_content(
    model="gemini-3.7-flash", 
    contents="Can Gemini 2.5 Flash be used for natural language \
    translation?")
print(response.text)

# %%

from google import genai


    # Set the API Key
API_KEY = "MY_KEY_ALPHANUMERIC"
client = genai.Client(api_key=API_KEY)


response = client.models.generate_content(
    model="gemini-3.7-flash", 
    contents="Give me a sample Python prompt for translating a \
        text file from Englsh to Spanish using Gemini 2.5 Flash \
        for natural language translation")

print(response.text)

# %%

from google import genai

client = genai.Client()

prompt = "You are playing the 20 question game. You know that what you are looking \
    for is an aquatic mammal that doesn't live in the sea, is venomous and that it's \
    smaller than a cat. What could that be and how could you make sure?"


    # Start the generation job
response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents=prompt
)

print(response.text)


# %%

from google import genai

    # Set the API Key
     
API_KEY = "MY_KEY_ALPHANUMERIC"
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-3.7-flash", 
    contents="Explain how AI works in a few words")
print(response.text)


# %%


  

