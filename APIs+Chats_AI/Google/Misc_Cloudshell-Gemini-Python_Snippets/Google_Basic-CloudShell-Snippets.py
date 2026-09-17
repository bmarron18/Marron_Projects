#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 21:54:30 2024
updated: 11 Sept 2026
@author: bmarron
"""



# %%

=====   Google Cloudshell    ============================


# %%

'''
References
'''

 # Google DeepL
https://transcy.crisp.help/en/article/how-to-translate-target-language-by-deepl-service-1ftwdt4/?bust=1712201846082


  #Google Cloud Translation API
https://cloud.google.com/translate/?hl=en


  # Tutorial--Getting Started with Google Cloud Translation API
  # [This tutorial confuses local and cloud shell machines]
https://codelabs.developers.google.com/codelabs/cloud-translation-python3#0

    # google-cloud-translate documentation
https://pypi.org/project/google-cloud-translate/
https://cloud.google.com/python/docs/reference/translate/latest/summary_overview
https://cloud.google.com/python/docs/reference/translate/latest/summary_method.html

    #This one!!
Class TranslationServiceClient (3.20.1) 
https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_TranslationServiceClient
https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient
https://cloud.google.com/python/docs/reference/translate/latest/summary_method#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_summary

# %%

'''
 References
'''
  # Google Cloud Services Account
https://cloud.google.com/
https://console.cloud.google.com/
https://cloud.google.com/iam/docs/service-accounts-create
https://cloud.google.com/iam/docs/service-account-overview
https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin


  # Installing Google Cloud SDK (includes CLI)
https://cloud.google.com/sdk
https://cloud.google.com/sdk/docs/initializing
https://stackoverflow.com/questions/71086225/how-to-install-or-uninstall-gcloud


  # Google Cloud Shell (available from Google Cloud Console)
  ''' IDE with a command line interface. This virtual machine is loaded with all the 
  development tools needed. It offers a persistent 5 GB home directory and runs in Google Cloud.
  Cloud Shell is a Debian-based virtual machine '''


  # Google Authentication and Application Default Credentials (ADC)
https://cloud.google.com/docs/authentication
https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment
https://cloud.google.com/docs/authentication/application-default-credentials#personal
https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment
https://cloud.google.com/docs/authentication/provide-credentials-adc
https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to
https://cloud.google.com/docs/authentication/application-default-credentials
https://stackoverflow.com/questions/51554341/google-auth-exceptions-defaultcredentialserror
https://stackoverflow.com/questions/40032678/where-are-google-application-default-credentials-stored
https://medium.com/datamindedbe/application-default-credentials-477879e31cb5
https://www.googlecloudcommunity.com/gc/Serverless/Why-i-have-the-error-raise-exceptions-DefaultCredentialsError-in/m-p/726413
https://stackoverflow.com/questions/73451173/google-auth-exceptions-defaultcredentialserror-could-not-automatically-determin
https://stackoverflow.com/questions/74502095/setting-application-default-credentials-adc-on-google-cloud


  # Google Cloud Storage
https://cloud.google.com/storage/docs/gsutil/commands/config] 


  # Google Cloud Client Libraries -- General
https://cloud.google.com/sdk/docs/install
https://cloud.google.com/apis/docs/cloud-client-libraries
https://cloud.google.com/apis/docs/client-libraries-explained
https://developers.google.com/api-client-library/
https://developers.google.com/apis-explorer/
 

  # Google Cloud Client Libraries -- Python
https://cloud.google.com/python
 https://github.com/googleapis/google-cloud-python
https://cloud.google.com/python/docs/getting-started
https://cloud.google.com/python/docs/setup
https://cloud.google.com/python/docs/reference


  # Google Cloud Client Libraries -- Translation / General
https://cloud.google.com/translate/docs
https://cloud.google.com/translate/docs/setup
https://cloud.google.com/translate/docs/reference/rest
https://cloud.google.com/translate/docs/advanced/translate-documents
https://cloud.google.com/translate/docs/supported-formats
https://pypi.org/project/google-cloud-translate/


  # Google Cloud Client Libraries  -- Translation / Python
https://cloud.google.com/python/docs/reference/translate/latest
https://cloud.google.com/translate/docs/advanced/translating-text-v3#translate_v3_translate_text-python
https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/translate/samples/snippets


  # Google Advanced Translation
https://cloud.google.com/translate/docs/intro-to-v3


  # Google Zones and Location of Servers for Cloud Computing
https://cloud.google.com/compute/docs/regions-zones
https://stackoverflow.com/questions/66841594/google-cloud-translate-400-invalid-resource-name-location-even-though-it-is-vali



    #On Set the PROJECT_ID environment variable (to be used in your application)
https://stackoverflow.com/questions/35599414/get-the-default-gcp-project-id-with-a-cloud-sdk-cli-one-liner



---- trying to install google-cloud-translate in Spyder Python
https://stackoverflow.com/questions/59200541/why-does-my-google-translate-api-work-in-the-terminal-but-not-an-executable
https://stackoverflow.com/questions/2915471/install-a-python-package-into-a-different-directory-using-pip
https://stackoverflow.com/questions/44389630/using-spyder-with-virtualenv



 # translaring text
https://cloud.google.com/translate/docs/basic/translating-text#translating_text
https://cloud.google.com/translate/docs/basic/translating-text#translate_translate_text-python


# %%
  # in Google Cloud Console (w/o IPython)
  # f-string
 https://realpython.com/python-f-strings/



$ export PROJECT_ID=$(gcloud config get-value core/project)
$ echo "PROJECT_ID: $PROJECT_ID"
    
   # in Google Cloud Console (w/ IPython)   
   
>>> from os import environ
>>> from google.cloud import translate

>>> PROJECT_ID = environ.get("PROJECT_ID", "")
>>> assert PROJECT_ID
>>> PARENT = f"projects/{PROJECT_ID}"

# %%

List of methods/fxn in Google Cloudschell API

https://stackoverflow.com/questions/69964961/how-can-i-get-a-list-of-google-cloud-functions-using-google-python-client-for-cl

from google.cloud.functions_v1.services.cloud_functions_service import CloudFunctionsServiceClient
from google.cloud.functions_v1.types import ListFunctionsRequest
list_functions_request = ListFunctionsRequest(parent=f"projects/{project}/locations/{region}")
await CloudFunctionsServiceClient().list_functions(list_functions_request)


# %%

'''
     On Google Authentication for Cloudshell ...
'''
    #  in Google Cloud Console (w/o IPython) Neural Machine Translation (NMT)

 $ gcloud auth login
     # to obtain new credentials.
     # follow prompts to obtain new credentials (needed every time)

$ gcloud auth list
    #Cloud Shell needs permission to use your credentials for the gcloud CLI command.
    #Click Authorize to grant permission to this and future calls. 
    # NB --- need to activate Free Trial to authenticate account
    
    #ACTIVE: *
    #ACCOUNT: marron.bruce.mx@gmail.com

# %%

'''
    On Google Account and Project Configuration
'''
    #  in Google Cloud Console (w/o IPython)

$ gcloud config set account 'ACCOUNT'     # <== retype w/ single quotes ''

$ gcloud config list project
 

# %%

'''
    On Google Cloud Translation API
    in Google Cloud Console (w/o IPython)
'''


$ gcloud services enable translate.googleapis.com


# %%

'''
   On Set the PROJECT_ID environment variable (to be used in your application)
'''
https://stackoverflow.com/questions/35599414/get-the-default-gcp-project-id-with-a-cloud-sdk-cli-one-liner

#  in Google Cloud Console (w/o IPython)


$ export PROJECT_ID=$(gcloud config get-value core/project)
    #Your active configuration is: [cloudshell-22175]
$ echo "PROJECT_ID: $PROJECT_ID"
    #PROJECT_ID: my-project-uteca1
    


# %%
'''
    On calling IPython in Cloud Shell
    Import objects 'os.environ' and 'google.cloud.translate'
'''

#  in Google Cloud Console (w/ IPython)
$ ipython

   # OS Environment variables (sometimes called "env vars") are variables you store outside your
   # program that can affect how it runs. For example, you can set environment variables that
   # contain the key and secret for an API. Your program might then use those variables when it 
   # connects to the API. 
   
   # os.environ is a mapping object that maps the user's environmental variables. It returns a 
   # dictionary or table having the user's environmental variable as key and their values as value.
   # os. environ behaves like a common dictionary, so operations like get and set can be performed


#  in Google Cloud Console (w/ IPython)

>>> from os import environ
>>> from google.cloud import translate

>>> PROJECT_ID = environ.get("PROJECT_ID", "")
>>> assert PROJECT_ID
>>> PARENT = f"projects/{PROJECT_ID}"



# %%

List of methods/fxn in Google Cloudshell API

https://stackoverflow.com/questions/69964961/how-can-i-get-a-list-of-google-cloud-functions-using-google-python-client-for-cl

from google.cloud.functions_v1.services.cloud_functions_service import CloudFunctionsServiceClient
from google.cloud.functions_v1.types import ListFunctionsRequest
list_functions_request = ListFunctionsRequest(parent=f"projects/{project}/locations/{region}")
await CloudFunctionsServiceClient().list_functions(list_functions_request)



# %%

Note that it lists all types of names: variables, modules, functions, etc.

dir() does not list the names of built-in functions and variables. 
If you want a list of those, they are defined in the standard module 
builtins:

import builtins

dir(builtins)



# %%

'''
     Exit Python in Cloudshell
     Close virtual environment
    
'''

In [12]: exit
    # exit Cloud Shell IPython session to go back to the Cloud Shell


$ deactivate
    # Stop using the Python virtual environment on home computer
   
$ cd ~
$ rm -rf ./venv-translate
    #  Delete your virtual environment folder:on home computer

To delete your Google Cloud project, from Cloud Shell:
    Retrieve your current project ID: PROJECT_ID=$(gcloud config get-value core/project)
    Make sure this is the project you want to delete: echo $PROJECT_ID
    Delete the project: gcloud projects delete $PROJECT_ID

# %%

'''
TUTORIAL 9
'''

  # in Google Cloud Console (w/ IPython)
  
  '''
  Argument formats in calls (eg display_language_code=display_language_code)
  ==> a Keyword (match by name) argument (p. 83, Pocket Reference)
  
  The fxn "print_supported_languages" requires the argument "display_language_code: str"
  which must be a string (ie : str)
  '''
https://stackoverflow.com/questions/54962869/function-parameter-with-colon

>>>
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
---------------------- Languages: 194 ----------------------
ab        Abkhaz
ace       Acehnese
ach       Acholi
af        Afrikaans
sq        Albanian
alz       Alur
am        Amharic
ar        Arabic
hy        Armenian
as        Assamese
...
yua       Yucatec Maya
zu        Zulu

# %%

'''
TUTORIAL 10

'''


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

------------------ Hello World! ------------------
en → tr : Selam Dünya!
en → de : Hallo Welt!
en → es : ¡Hola Mundo!
en → it : Ciao mondo!
en → el : Γεια σου Κόσμο!
en → zh : 你好世界！
en → ja : 「こんにちは世界」
en → ko : 안녕하세요!


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

 # translaring text
https://cloud.google.com/translate/docs/basic/translating-text#translating_text
https://cloud.google.com/translate/docs/basic/translating-text#translate_translate_text-python




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

'''
TUTORIAL 12
     Clean up
    
'''

In [12]: exit
    # exit Cloud Shell IPython session to go back to the Cloud Shell




To delete your Google Cloud project, from Cloud Shell:
    Retrieve your current project ID: PROJECT_ID=$(gcloud config get-value core/project)
    Make sure this is the project you want to delete: echo $PROJECT_ID
    Delete the project: gcloud projects delete $PROJECT_ID
    
    
