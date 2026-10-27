#!/usr/bin/env python3
"""
Created on Mon Dec 30 21:54:30 2024

@author: bmarron
"""

# %%

#!/Python34/python

num_list = []

with open('temperature.text', 'r') as fh:
    for line in fh:
        num_list.append(int(line))

# %%

import pandas as pd
from contextlib import chdir

with chdir('/home/bmarron/Desktop'):
    
     #read the words into a list.
     #keep duplicate words and sort
     words = open("clean_test.txt", "r").read().split()
     ordered = sorted(words)

     #remove duplicate words and sort
     #uniq = sorted(set(words)) 


with open("output.txt", "a") as f:
    print(pd.Series(ordered).value_counts().sort_values(ascending=True), file=f)




    # freq of words in a text

words = file("test.txt", "r").read().split() #read the words into a list.
uniqWords = sorted(set(words)) #remove duplicate words and sort
for word in uniqWords:
    print words.count(word), word
    
    # freq of words in a text Pandas
import pandas as pd
original_list = ["the", "car", "is", "red", "red", "red", "yes", "it", "is", "is", "is"]
pd.Series(original_list).value_counts()

pd.Series(original_list).value_counts().sort_values(ascending=True)
    

# %%

def print_supported_languages(display_language_code: str):
    client = translate.TranslationServiceClient()

    response = client.get_supported_languages(
        parent=PARENT,
        display_language_code=display_language_code,
    )

    languages = response.languages
    print(f" Languages: {len(languages)} ".center(60, "-"))
    for language in languages:
        language_code = language.language_code
        display_name = language.display_name
        print(f"{language_code:10}{display_name}")


print_supported_languages("en")

# %%

def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )

    return response.translations[0]



text = "Hello World!"
target_languages = ["tr", "de", "es", "it", "el", "zh", "ja", "ko"]
print(f" {text} ".center(50, "-"))


for target_language in target_languages:
      translation = translate_text(text, target_language)
      source_language = translation.detected_language_code
      translated_text = translation.translated_text
      print(f"{source_language} → {target_language} : {translated_text}")


# %%

import os
os.getcwd()

# get the current working directory
current_working_directory = os.getcwd()

# print output to the console
print(current_working_directory)

# %%

    # change working directory for safety
    # USE THIS ==> Work within a new directory then go back to the original current working directory

    # Option 1  <== USE THIS !!
from contextlib import chdir
with chdir(path):
  # do stuff; the code you will be processing
  
  
# %%
   
   # change directory for safety
   # run a ;print to file code'
   # print to file two different ways
   # Changed TABS to 2 spaces

from contextlib import chdir
with chdir('/home/bmarron/Desktop'):
  
  import os
  import pprint
  
  data = {'a': [1, 2, 3], 'b': {'c': 4, 'd': 5}}

  with open('output.txt', 'w') as f:
    pprint.pprint(data, stream=f)
    
  with open('out.txt', 'w') as f:
    print('Data', data, file=f)
        

print(os.getcwd())
  


# %%
  # Sample fxn
  
  
  
def get_even(numbers):
  """Adds two numbers and returns the result as a list."""
  even_nums = [num for num in numbers if not num % 2]
  return even_nums


get_even([1, 2, 3, 4, 5, 6])

# %%
  # Sample fxn
  
  
def greeting(name: str) -> str:
  return 'Hello, {}'.format(name)

greeting('Bruce')

# %%
  # Sample fxn
  
  
def get_even(numbers) -> "a list":
    
  even_nums = [num for num in numbers if not num % 2]
  return even_nums

get_even([1, 2, 3, 4, 5, 6])

# %% 

  # Sample fxn
  # the following two fxns are equal

def my_sum(*args):
    result = 0
    # Iterating over the Python args tuple
    for x in args:
        result += x
    return result

print(my_sum(1, 2, 3))

'''
  To call this function you’ll also need to create a list of arguments to pass to it.
  (ie,  a list of arguments named 'list_of_integers' to pass to 'my_integers')
  '''

def my_sum(my_integers):
    result = 0
    for x in my_integers:
        result += x
    return result

list_of_integers = [1, 2, 3] 
print(my_sum(list_of_integers))

# %%
  # sample fxn
  # need an API key to access 
  
import requests 
from pprint import pprint 

def geocode(address): 
	url = "https://maps.googleapis.com/maps/api/geocode/json"   
	resp = requests.get(url, params = {'address': address}) 
	return resp.json() 

  # calling the geocode function 
data = geocode('India gate') 

  # pretty-printing json response 
pprint(data) 

# %%

'''
TUTORIAL 7 
 '''
   # On home computer terminal (Linux)
 
  '''
   "virtualenv" is a tool to create isolated Python environments. Integrated into the standard library
   under the "venv" module.  

   # The call "$ virtualenv venv-translate" invokes the  'virtualenv' tool in the 'venv' module 
   # 'venv-translate' is the name of the virtual environment..
   
    # Installing 'google-cloud-translate' ==> the Google SDK libraries enable the interface between 
    Google Cloud and home compu in Python
    '''
   
 https://cloud.google.com/translate/docs/reference/libraries/v2/python
    

  
$ cd ~
$ virtualenv venv-translate &&
source venv-translate/bin/activate

$ pip install ipython google-cloud-translate



  # To Stop using the Python virtual environment on home computer
$ deactivate
    
  #  To Delete your virtual environment folder:on home computer
$ cd ~
$ rm -rf ./venv-translate
 
    
# %%

  # On home computer terminal (Python)
'''
Find the list ofenvironmental variables used by Python
'''


  # importing os module  
>>> import os 
>>> import pprint 
  
  # Get the list of user's 
>>> env_var = os.environ 
  
  # Print the list of user's 
>>> print("User's Environment Variables:") 
>>> pprint.pprint(dict(env_var), width = 1)
    
    
    
# %%
  # in Google Cloud Console (w/o IPython)
 


$ export PROJECT_ID=$(gcloud config get-value core/project)
$ echo "PROJECT_ID: $PROJECT_ID"
    
   # in Google Cloud Console (w/ IPython)   
   
from os import environ
from google.cloud import translate

PROJECT_ID = environ.get("PROJECT_ID", "")
assert PROJECT_ID
PARENT = f"projects/{PROJECT_ID}"

# %%
 
 # in Google Cloud Console (w/ IPython)
  
  '''
  Argument formats in calls (eg display_language_code=display_language_code)
  ==> a Keyword (match by name) argument (p. 83, Pocket Reference)
  
  The fxn "print_supported_languages" requires the argument "display_language_code: str"
  which must be a string (ie : str)
  '''
https://stackoverflow.com/questions/54962869/function-parameter-with-colon


def print_supported_languages(display_language_code: str):
    client = translate.TranslationServiceClient()

    response = client.get_supported_languages(
        parent=PARENT,
        display_language_code=display_language_code,
    )

    languages = response.languages
    print(f" Languages: {len(languages)} ".center(60, "-"))
    
    for language in languages:
        language_code = language.language_code
        display_name = language.display_name
        print(f"{language_code:10}{display_name}")



# %%

'''
from Google snippet files
/home/bmarron/Desktop/UTECA/UTECA_AI_TranslatorSetup/Github_PythonSnippets_GoogleCloud/python-docs-samples/translate/samples/snippets

translate_v3beta1_batch_translate_document.py
'''

input_uri = "https://cloud.google.com/translate/docs/supported-formats"

gcs_source = {"input_uri": input_uri}

batch_document_input_configs = {
    "gcs_source": gcs_source,
}

tester = [batch_document_input_configs]
print(tester)

'''
  # a nested dictionary
Out[5]: [{'gcs_source': {'input_uri': 'https://cloud.google.com/translate/docs/supported-formats'}}]
'''

# %%


def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )

    return response.translations[0]



text = "Hello World!"
target_languages = ["tr", "de", "es", "it", "el", "zh", "ja", "ko"]
print(f" {text} ".center(50, "-"))



for target_language in target_languages:
    translation = translate_text(text, target_language)
    source_language = translation.detected_language_code
    translated_text = translation.translated_text
    print(f"{source_language} → {target_language} : {translated_text}")


text = "What the fuck!"

print(f" {text} ".center(50, "-"))
for target_language in target_languages:
    translation = translate_text(text, target_language)
    source_language = translation.detected_language_code
    translated_text = translation.translated_text
    print(f"{source_language} → {target_language} : {translated_text}")
    
----------------- what the fuck! -----------------
en → tr : ne oluyor lan!
en → de : was zur Hölle!
en → es : ¡Qué carajo!
en → it : che cazzo!
en → el : τι στο διάολο!
en → zh : 什么鬼！
en → ja : 何だこれ！
en → ko : 이게 뭐야!



  
# %%



def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result


# %%

       # exit Cloud Shell IPython session to go back to the Cloud Shell
In [12]: exit
 

To delete your Google Cloud project, from Cloud Shell:
    Retrieve your current project ID: PROJECT_ID=$(gcloud config get-value core/project)
    Make sure this is the project you want to delete: echo $PROJECT_ID
    Delete the project: gcloud projects delete $PROJECT_ID

# %%



