#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created: 06 Jan 2025
Modified: 11 Mar 2025
@author: bmarron

sources: 
*translate_v3beta1_translate_document.py
*https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient
*https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_batch_translate_document
*https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_translate_document
"""

# %%

=======   Preliminaries   ===========================

# %%

'''
Login to Google Cloud account (marron,bruce,mx@gmail,com)
    Check account status
    Exit
'''
https://console.cloud.google.com/

Project name
    My Project-UTECA1
Project number
    735387290281
Project ID
    my-project-uteca1


Welcome to Cloud Shell! Type "help" to get started.
Your Cloud Platform project in this session is set to my-project-uteca1.
Use “gcloud config set project [PROJECT_ID]” to change to a different project.

    #  Google Cloud Console shell
marron_bruce_mx@cloudshell:~ (my-project-uteca1)$ 

# %%

'''
Install gcloud SDK on home compu (if not already done)
    [==> /home/bmarron/google-cloud-sdk]
'''
https://cloud.google.com/sdk/docs/install
    google-cloud-cli-linux-x86_64.tar.gz

  # Run `gcloud cheat-sheet` to see a roster of go-to `gcloud` commands.
$ cd ~
$ ./google-cloud-sdk/bin/gcloud cheat-sheet




# %%
'''
Check for google-cloud-sdk updates
    [Last update 11 Mar 2025]
    Current Google CLI version: 514.0.0
    Previous Google CLI : 511.0.0
    


'''
    
$ cd ~
$ ./google-cloud-sdk/bin/gcloud components update


    # Revert to previous version (if needed)
$ gcloud components update --version 511.0.0
 
 



# %%
'''
   Obtain Application Default Credentials (ADC) (if not already done)
   
'''

  # Initial get of ADC credentials 
  # will be stored locally as .json file
  # ADC authentication is thru google-cloud-sdk 
  # Browser sent to Google Auth Library; follow browser prompts
  # NOT setting up a Service Account; ADC stored locally
  # once have credentials will be used by any library that requests ADCs
 
$ cd ~
$ ./google-cloud-sdk/bin/gcloud auth application-default login


    # Obtain only once; stored as .json file
    # ADC credentials are saved here:: 
/home/bmarron/.config/gcloud/application_default_credentials.json



# %%
'''
Check the authentication account used by gcloud
Set the authentication account (if needed)
'''
    #Check current authentication account
$ cd ~
$ ./google-cloud-sdk/bin/gcloud auth list

      Credentialed Accounts
ACTIVE  ACCOUNT
*       marron.bruce.mx@gmail.com


    # set the authentication account (if needed)
$ gcloud config set account `ACCOUNT`   #<== re-type 'ACCOUNT' w/ apostrophes!!



# %%
'''
Set Google Cloud projects for billing and quotas
(Only once per project)
'''

    # quotas are per project
    #  set to "my-project-uteca1"
$ ./google-cloud-sdk/bin/gcloud auth application-default set-quota-project my-project-uteca1

Quota project "my-project-uteca1" was added to ADC which can be used by 
Google client libraries for billing and quota.



# %%

============== Workflow_gcloudAPI_StandardNMT_GeneralTranslation_docs.py  ============

# %%
'''
Check for google-cloud-sdk updates
    [Last update 11 Mar 2025]
    Current Google CLI version: 514.0.0
    Previous Google CLI : 511.0.0
'''
    
$ cd ~
$ ./google-cloud-sdk/bin/gcloud components update


    # Revert to previous version (if needed)
$ gcloud components update --version 511.0.0
 
# %%

'''
Check the authentication account used by gcloud

'''
    #Check current authentication account
$ cd ~
$ ./google-cloud-sdk/bin/gcloud auth list

      Credentialed Accounts
ACTIVE  ACCOUNT
*       marron.bruce.mx@gmail.com


    # set the authentication account (if needed)
$ gcloud config set account `ACCOUNT`   #<== re-type 'ACCOUNT' w/ apostrophes!!


# %%

'''
Doing complete document translations thru API with the Standard NMT model
  Account and Project Configuration
  Re-set every session
'''

  # sign in and follow prompts for account and project config
  #  ==> follow prompts until:
  # The Google Cloud CLI is configured and ready to use!

$ cd ~ 
$ ./google-cloud-sdk/bin/gcloud init



  
# %%

'''
    Create a virtual Python environment on local machine (home computer)
      ==> Install IPython
      ==> Install the SDK for Google language translation (google-cloud-translate)
      ( aka the Google Translation API client library)
      ==> spyder kernels
'''
 
$ cd ~ 
$ virtualenv venv-translate &&
source venv-translate/bin/activate &&
pip install spyder-kernels ipython google-cloud-translate

    # terminal now here
(venv-translate) bmarron@bmarron-HP-Laptop-15t-dy100:~$ 


# %%
'''
    Getting Spyder into venv-translate
'''


$ python -c "import sys; print(sys.executable)"
    /home/bmarron/venv-translate/bin/python  

    
    # Normal Spyder ==> Python 3.11.11 and IPython 8.32.0
    # in spyder
Tools > Preferences > Python Interpreter > Use the following interpreter
    * paste the path ==>  /home/bmarron/venv-translate/bin/
    * paste file name into text box ==> python


    # Start a new IPython console in Spyder
    # Spyder now operating in virtual env ==> (venv-translate)
    # venv-translate Spyder ==> Python 3.10.12 and IPython 8.34.0
    # Can now use Spyder for all subsequent python calls

# %%
'''
    Import modules
      ==> os
    Import methods (fxns)
      ==> google.cloud.translate_v3.services.translation_service.TranslationServiceAsyncClient.translate_text
      ==> google.cloud.translate_v3.services.translation_service.TranslationServiceClient
      ==> method "translate_v3" from google.cloud.translate (SDK)

'''

import os
    #from google.cloud import translate
from google.cloud import translate_v3 as translate


# %%
'''
  Set Google API variables 
  Set Google credentials for billing and quots
'''
  # Google Cloud project used for translation work
PROJECT_ID = "my-project-uteca1";
assert PROJECT_ID ;
project_id = PROJECT_ID


  # set ADC from Google as a Python env variable 
credential_path = "/home/bmarron/.config/gcloud/application_default_credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


# %%
'''
    Set name and path of doc to be translated
    Set target language (code) for translation
'''

     # document to be translated
     # path to the document
doc_to_translate = "new_2.pdf" ;
doc_dir = "/home/bmarron/Desktop/UTECA/UTECA_AI_TranslatorSetup/UTECA1_TranslatorAPIs/gcTranslationAPI_Workflows/ToTranslate_Docs" ;
file_path = os.path.join(doc_dir, doc_to_translate)


    # target language for translation
target = "es"



# %%
'''
    Define the Python translation fxn, "translate_document"
    Source:
        https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_batch_translate_document
'''


  # the translation fxn: single doc to single language
def translate_document(project_id: str,file_path: str,):
    
    client = translate.TranslationServiceClient()
    location = "us-central1"
    parent = f"projects/{project_id}/locations/{location}"
    
   
    with open(file_path, "rb") as document:
        document_content = document.read()
  
    document_input_config = {
        "content": document_content,
        "mime_type": "application/pdf",
    }

    response = client.translate_document(
        request={
            "parent": parent,
            "target_language_code": target,
            "document_input_config": document_input_config,
        }
    )

    # To output the translated document, uncomment the code below.
    f = open('/home/bmarron/Desktop/gcTranslate_output.pdf', 'wb')
    f.write(response.document_translation.byte_stream_outputs[0])
    f.close()

    # If not provided in the TranslationRequest, the translated file will only be returned through a byte-stream
    # and its output mime type will be the same as the input file's mime type
    print(
        f"Response: Detected Language Code - {response.document_translation.detected_language_code}"
    )

    return response

# %%

  # Do the translation
translate_document(project_id, file_path)


# %%

  # Model used by Google to do the translation
  # Neural Machine Translation (NMT)
  
model: "projects/735387290281/locations/us-central1/models/general/nmt"

# %%

'''
  Clean up
'''
    # exit Cloud Shell IPython session (if working in terminal)
In [12]: exit

    # re-set spyder to original python interpreter

   

   # Stop using the Python virtual environment 
$ deactivate
   
   # Delete virtual environment folder (local machine)
$ cd ~ &&
rm -rf ./venv-translate
    


# [END Workflow_GoogleTranslate_v3_docs]

