#!/usr/bin/env python3
"""
Created on Mon Dec 30 21:54:30 2024
updated: 11 Sept 2026
@author: bmarron
"""



# %%

Note that it lists all types of names: variables, modules, functions, etc.

dir() does not list the names of built-in functions and variables. 
If you want a list of those, they are defined in the standard module 
builtins:

import builtins

dir(builtins)


# %%


---- $PYTHONPATH
https://askubuntu.com/questions/384996/what-does-my-pythonpath-contain


---- Option 3: pip install spyder-kernels==3.0.* in virtual environment
https://stackoverflow.com/questions/30170468/how-to-run-spyder-in-virtual-environment


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

https://realpython.com/python-kwargs-and-args/

  '''
  *args ==>  allows you to pass a varying number of positional arguments.
  Extended sequence assignments use * (p. 74, 82 in Pocket Reference)
  
  The unpacking operator (*) creates a tuple not a list: A tuple is similar to a list in 
  that they both support slicing and iteration. However, tuples are very different in at least 
  one aspect: lists are mutable, while tuples are not. 
  '''
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


