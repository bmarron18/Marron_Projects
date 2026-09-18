# %%
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 19 2025
@author: bmarron

"""
# %%

    # Refs
'''
https://platform.openai.com/docs/quickstart

https://community.openai.com/t/which-api-for-translation/553000/6
https://platform.openai.com/docs/api-reference/responses

https://platform.openai.com/docs/api-reference/responses/create
https://platform.openai.com/docs/guides/migrate-to-responses
https://platform.openai.com/docs/guides/pdf-files?api-mode=responses

https://community.openai.com/t/translation-script-not-working/896719/2
https://platform.openai.com/docs/api-reference/chat/create?lang=python

'''
# %%

    # Use the "Response API" and NOT the "ChatCompletion API" for translation
    # Install OpenAI SDK into conda env, (spyder_env)
    
$ conda activate spyder_env
(spyder_env)$ conda install openai
(spyder_env)$ conda deactivate

# %%

    # Manage API Key
https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety

# NB. shell configuration files ( .bashrc, .zshrc, or .bash_profile)
# I have ~/.bashrc

    # creates a .bash_profile file at /home/bmarron
$ echo "export OPENAI_API_KEY='my-key'" >> ~/.bashrc

    # update shell with new variable
$ source ~/.bashrc

    # check  ~/.bashrc file
    # should have ==> export OPENAI_API_KEY="sk-proj-xxxxxxxxxx" as \ 
    # the last entry
    
$ notepadqq ./.bashrc

    # confirm you have set the API key correctly
$ echo $OPENAI_API_KEY

    # check Python finds the key
    # DONT USE ==> os.environment["OPENAI_API_KEY"]

import os
openai_api_key = os.getenv("OPENAI_API_KEY")


    # call the key in scripts
    
import os
import openai
 
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


# %%

'''
Simple Test Run

'''
import os
from openai import OpenAI

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

    # API_KEY is inserted directly
#client = OpenAI(api_key=ACTUAL_API_KEY)


response = client.responses.create(
  model = "gpt-4o",
  temperature = 1.3,
  instructions = "Talk like a pirate.",
  input = "Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)

'''
Arr matey, once upon a time, atop the moonlit waves o' dreamland, pranced a 
shimmering unicorn, whose horn sparkled with such magic it sent the young 
pirate driftin' to sleep among the stars.
'''

# %%

Path() construcor in Python

represent file and directory paths in a platform-independent manner.

# %%

Error code: 400 - {'error': {'message': "'assistant' is not one of 
    ['fine-tune', 'assistants', 'batch', 'user_data', 'vision', 'evals'] - 
    'purpose'", 'type': 'invalid_request_error', 'param': 'purpose', 'code': None}}
