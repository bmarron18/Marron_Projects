#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created: 06 Jan 2025
Modified: 20 Mar 2025
@author: bmarron

sources: 
*translate_v3beta1_translate_document.py
*https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient
*https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_batch_translate_document
*https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_translate_document
"""


# %%

#====    Windows Preliminaries and Background Info    ==========================

# %%

'''
    Navigating the Windows file system
    Use regular terminal (NOT Power Shell terminal)
    (look for "Simbolo del sistema" terminal)
'''

    # To open (regular) terminal
Click the Start menu and type "cmd" in the search bar to 
find the Command Prompt. 


NB. To open a terminal in a specific folder on Windows 10, navigate to the 
desired folder in File Explorer, then hold down the Shift key, right-click
 within the folder, and select "Open in terminal" from the context menu. 

    # General navigation:
    # open terminal
    # change the directory to the top of the file system
    # NB. use forward slash for Windows (DOS) file system
    # in all commands, REPLACE <you> with your user name

C:\Users\<you>\> cd\
C:\>
    
    # check the contents of the current directory

C:\> dir 


    # change to home directory
C:\> cd %homedrive%%homepath%



# %%

'''
    Handy Windows command line syntax for searching the Windows filesystem
    (ONLY works for regular terminal, NOT PowerShell)
   
'''
https://stackoverflow.com/questions/8066679/how-to-do-a-simple-file-search-in-cmd

 
'''
/b flag 
    treats files as binary (i.e., a raw stream of meaningless bytes), 

/a flag
    treats files as lines of text (with end-of-line characters, 
    end-of-files, etc.)
/s flag
    Lists every occurrence of the specified file name within 
    the specified directory and all subdirectories.
    
* symbol
    wildcards (like Linux)
'''

   # searches in current folder and sub folders.
   # finds directories as well as files
   # print to text file

> dir /b/s *foo* 


    # -d excludes directories C:\>
    # /a: 
> dir /a:-d /b/s *foo* >> file.txt



    #List all Hidden Files w/o directories
> dir /a:h-d /b/s

    #List all System Files w/o directories
> dir /a:s-d /b/s

    List all ReadOnly Files w/o directories
> dir /a:r-d /b/s

    # List all Non Indexed Files w/o directories
> dir /a:i-d /b/s



 #%%
'''
    Install Notepad++ (if not already installed)
    Google "install notepad++ Windows" (automatic download)
'''

    # NB. Notepad++ installs here
C:\Program Files\Notepad++

# %%

'''
    Create a top-level folder for easy access to translation docs
    (Windows 11 has \OneDrive\Desktop w/ complicated access)
'''

C:\> mkdir API_translate


# %%

'''
    Search ALL Windows directories for Pyhton
'''
    # go to the top of the filesystem
C:\Users\<you>\> cd\
C:\> 


   # search for ALL python-named files and directories
   # send the output to text file to Desktop OR to newly-created directory (folder)
C:\> dir /b/s *python* >>C:\Users\<you>\Desktop\python.txt   # Windows 10


C:\> dir /b/s *python* >> C:\API_translate\python.txt        # Windows 11

# %%

'''
    Search ALL Windows directories for pyhton.exe
    Output to text file
'''
C:\Users\<you>\> cd\
C:\> 

    # Output to a text file on Desktop OR "API_translate" directory (folder)
C:\> dir /b/s python.exe >> C:\Users\<you>\Desktop\python_exe_files.txt  # Windows 10

C:\> dir /b/s python.exe >> C:\API_translate\python_exe_files.txt  # Windows 11


'''
    on my compu...
'''

    # google-cloud-sdk bundled python 
    #    ==> Python 3.12.8 (tags/v3.12.8:2dc476b, Dec  3 2024, 19:30:04) [MSC v.1942 64 bit (AMD64)] on win32
C:\Users\bmarr\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe

    # installed Python 2.7.18
C:\Users\bmarr\AppData\Local\Python2.7\python.exe

    # Spyder python
    #  ==> Python 3.11.11 | packaged by conda-forge | (main, Dec  5 2024, 14:06:23) [MSC v.1942 64 bit (AMD64)]
    #  ==> IPython 8.32.0 -- An enhanced Interactive Python.
C:\Users\bmarr\AppData\Local\spyder-6\python.exe
C:\Users\bmarr\AppData\Local\spyder-6\envs\spyder-runtime\python.exe



# %%

'''
    Search ALL Windows directories for pip
    (pip.exe is a Python module installer)
 '''
C:\>dir /b/s pip.exe



'''
    on my compu...
'''
    # python 2.7 has pip
C:\Users\bmarr\AppData\Local\Python2.7\Scripts\pip.exe

    # spyder has pip
C:\Users\bmarr\AppData\Local\spyder-6\envs\spyder-runtime\Scripts\pip.exe
C:\Users\bmarr\AppData\Local\spyder-6\Scripts\pip.exe   #<== this one!!



# %%

'''
    Search ALL Windows directories forPython module, "virtualenv"
    (virtualenv.exe is a program that creates virtual env.s in Python)
 '''
 
    # virtualenv folder should have virtualenv.exe
    # find it

C:\> dir /b/s virtualenv.exe 
File Not Found   #<== this is ok

 
'''
    on my compu
'''
    
   # google-cloud-sdk bundled python has venv folder
C:\Users\bmarr\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\Lib\venv\scripts\nt\python.exe


    # spyder python has venv folder
C:\Users\bmarr\AppData\Local\spyder-6\envs\spyder-runtime\Lib\venv\scripts\nt\python.exe
C:\Users\bmarr\AppData\Local\spyder-6\Lib\venv\scripts\nt\python.exe




# %%

'''
    Install virtualenv into Spyder directories using pip
'''

    # install virtualenv in specific location in Spyder
    # verify installation 

C:\Users\<you>\AppData\Local\spyder-6\Scripts> pip install virtualenv


      # virtualenv.exe should be found in spyder-6 under the Scripts subdirectory.
      # verify installation and locate
C:\>dir /b/s virtualenv.exe
C:\Users\<you>\AppData\Local\spyder-6\Scripts\virtualenv.exe


# %%

'''
  Install Python 2.7 (just for me)
'''


     # install pyhton 2.7 Windows
     # at Setup, select "Install just for me"
Python 2.7.18 is the last release of Python 2.
https://www.python.org/downloads/release/python-2718/


    # Python 2 should be here
C:\Python27\

    
    # NB. Now have Python 2 AND Python 3 (need both)
    # Python3 is here (in spyder) as python.exe and/or python3
C:\Users\<you>\AppData\Local\spyder-6>


# NB.DO NOT mess with PYTHONPATH environmental variable!!
  

'''
    Note on global environmental variables
    in Windows search, Advanced System Settings to find env variables
   
'''
https://stackoverflow.com/questions/13596505/python-command-not-working-in-command-prompt
https://stackoverflow.com/questions/3701646/how-to-add-to-the-pythonpath-in-windows-so-it-finds-my-modules-packages

 
    
  
 


# %%



# =======   Google Preliminaries   ===========================

# %%

'''
Create a Google Cloud Platform acct (need RFC)
Login to Google Cloud account (non-school email)
Activate Cloud Shell
Create a new project
Check account status and exit Cloud Shell
'''
https://console.cloud.google.com/


    #  Google Cloud Console shell looks like this (ie computer terminal)
marron_bruce_mx@cloudshell:~ (my-project-uteca1)$ 




'''
my Google Cloud acct...

'''
Project name
    My Project-UTECA1
Project number           
    735387290281          # <== IMPORTANT!! 
Project ID                
    my-project-uteca1     # <== IMPORTANT!!


Welcome to Cloud Shell! Type "help" to get started.
Your Cloud Platform project in this session is set to my-project-uteca1.
Use “gcloud config set project [PROJECT_ID]” to change to a different project.


# %%

'''
Notes/Info on gcloud SDK (gcloud CLI) 

'''

    # gcloud SDK 'bundled with Python 3" means that the scripts are in python3
    # 'run a supported version of Python' means having python installed
   
By default, the Windows version of Google Cloud CLI comes bundled with 
Python 3. To use Google Cloud CLI your operating system must be able to 
run a supported version of Python.

While Google Cloud CLI installs and manages Python 3 by default, you can use 
an existing Python installation if necessary by unchecking the option
to Install Bundled Python.

   # gcloud SDK contains
    * CLI libraries
    * Cloud Tools for PowerShell
    * Google Cloud Version 513.0.0
    * Python 3
    * CLOUDSDK_PYTHON     <== env variable

 # more info
 https://cloud.google.com/sdk/gcloud


# %%

'''
Install gcloud SDK (gcloud CLI) on home compu 

'''

    # Download installer (GoogleCloudSDKInstaller.exe)
    # accept all defaults on last page of installer

https://cloud.google.com/sdk/docs/install
==> GoogleCloudSDKInstaller.exe



   # installer places SDK here
   # ALL google-cloud-sdk files here
C:\Users\<you>\AppData\Local\Google\Cloud SDK>


       
    # Once installed you get a (PowerShell) terminal to sign in
> You must sign in to continue. Would you like to sign in (Y/n)?

    * asks for Google Cloud acct emai
    * phone verification (TFA)
    * 'Google Cloud wants access your Google acct'
    
You are now authenticated with the gcloud CLI!
    https://cloud.google.com/sdk/auth_success
    

    
'''
on my compu...
'''

> You are signed in as: [marron.bruce.mx@gmail.com].

> Pick cloud project to use:
 [1] my-project-uteca1
 [2] Enter a project ID
 [3] Create a new project
Please enter numeric choice or text value (must exactly match list item):
    
    
This gcloud configuration is called [default]. You can create additional configurations if you work with multiple accounts and/or projects.
Run `gcloud topic configurations` to learn more.


Some things to try next:
* Run `gcloud --help` to see the Cloud Platform services you can interact with. And run `gcloud help COMMAND` to get help on any gcloud command.
* Run `gcloud topic --help` to learn about advanced features of the CLI like arg files and output formatting
* Run `gcloud cheat-sheet` to see a roster of go-to `gcloud` commands.





# %%
'''
Check for google-cloud-sdk updates
Revert google-cloud-sdk to previous version (if needed)
'''
https://stackoverflow.com/questions/71949010/google-cloud-sdk-python-was-not-found


    # check for updates
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud components update

All components are up to date.

    # To revert your CLI to the previously installed version:
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud components update --version 505.0.0
  
  
  # helpful (about Python)
> gcloud topic startup 
 
> gcloud cheat-sheet






  
  

# %%
 
 '''
    Obtain Application Default Credentials (ADC)
    (Only once; stored as .json file)
 '''
 
 
    # Initial get of ADC credentials (stored locally as .json file)
    # ADC authentication is thru google-cloud-sdk 
    # Browser sent to Google Auth Library; follow browser prompts
    # NOT setting up a Service Account; ADC stored locally
    # once have credentials will be used by any library that requests ADCs

C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud auth application-default login
 
   * select Google acct
   * Sign in to Google Auth Library
   * 'Google Auth Library wants to access your Google Account'

   # set the authentication account (if needed)
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud config set account `ACCOUNT`   #<== re-type 'ACCOUNT' w/ apostrophes!!



        # check for credentialed accounts OR
        # get ADC credentials
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud auth list


   # ADC credentials Credentials saved to file: 
C:\Users\<you>\AppData\Roaming\gcloud\application_default_credentials.json


 


'''
my acct
'''

ADC credentials will be used by any library that requests 
Application Default Credentials (ADC).
Quota project "my-project-uteca1" was added to ADC which can be used by Google client 
libraries for billing and quota. Note that some services may still bill the project 
owning the resource.

      Credentialed Accounts
ACTIVE  ACCOUNT
*       marron.bruce.mx@gmail.com



# %%


'''
    Set quota and billing in ADC
'''


C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud auth application-default set-quota-project my-project-uteca1


# %%

==============Workflow_gcloudAPI_NMT_GenTrans_WINDOWS-1_docs-pdf.py  ============

# %%
'''
Check for google-cloud-sdk updates
Revert google-cloud-sdk to previous version (if needed)
'''
https://stackoverflow.com/questions/71949010/google-cloud-sdk-python-was-not-found


    # check for updates
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud components update

All components are up to date.

    # To revert your CLI to the previously installed version:
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud components update --version 505.0.0
  
  
  # helpful (about Python)
> gcloud topic startup 
 
> gcloud cheat-sheet


# %%

'''
Document translations thru API with the Standard NMT model
  Account and Project Configuration
  (Re-set every session)
'''

  # sign in and follow prompts for account and project config
  #  ==> follow prompts
  
C:\Users\<you>\AppData\Local\Google\Cloud SDK> gcloud init



'''
    on my compu ...
'''

Welcome! This command will take you through the configuration of gcloud.....

Settings from your current configuration [default] are:
accessibility:
  screen_reader: 'False'
core:
  account: marron.bruce.mx@gmail.com
  disable_usage_reporting: 'False'
  project: my-project-uteca1

Pick configuration to use:
 [1] Re-initialize this configuration [default] with new settings
 [2] Create a new configuration
Please enter your numeric choice:


Select an account:
 [1] marron.bruce.mx@gmail.com
 [2] Sign in with a new Google Account
 [3] Skip this step
Please enter your numeric choice:



Pick cloud project to use:
 [1] my-project-uteca1
 [2] Enter a project ID
 [3] Create a new project
Please enter numeric choice or text value (must exactly match list item):
    

The Google Cloud CLI is configured and ready to use!


# %%
'''
    Create a virtual Python environment on local machine (home computer)
      ==> Install IPython
      ==> Install the SDK for Google language translation (google-cloud-translate)
      (aka the Google Translation API client library)
      
      

      
# Spyder ISSUES w. virtualenv!! NEED TO FIX!!
    ==> DONT (install spyder kernels yet)
# installed spyder kernels separately
[spyder](base) C:\Users\bmarr\AppData\Local\spyder-6\Scripts> conda install spyder-kernels=3.0
    #check contents
C:\Users\bmarr\AppData\Local\spyder-6\Scripts> dir /b/s venv-translate >> C:\Users\bmarr\Desktop\venv.txt
    # found python.exe but spyder won't accept this
C:\Users\bmarr\AppData\Local\spyder-6\Scripts\venv-translate\Scripts\python.exe                   
 # NOT spyder-kernels==3.0.*
'''


    # cd to the directory with virtualenv.exe
C:\Users\<you>> cd C:\Users\<you>\AppData\Local\spyder-6\Scripts

   # Initialize conda for final clean-up
   # must re-start shell (terminal)
C:\Users\<you>\AppData\Local\spyder-6\Scripts> conda init

 
     # create virtual env, 'venv-translate'
C:\Users\<you>\AppData\Local\spyder-6\Scripts> virtualenv venv-translate


    # activate
C:\Users\<you>\AppData\Local\spyder-6\Scripts> activate


    # activated if see [spyder](base)
[spyder](base) C:\Users\<you>\AppData\Local\spyder-6\Scripts>



    # install ipython google-cloud-translate
[spyder](base) C:\Users\<you>\AppData\Local\spyder-6\Scripts> pip install ipython google-cloud-translate




# %%


   #RUN ipython in virtual env (going thru terminal NOT thru spyder)
[spyder](base) C:\Users\<you>\AppData\Local\spyder-6\Scripts>ipython




'''
on my compu...
'''
Python 3.11.9 | packaged by conda-forge | (main, Apr 19 2024, 18:27:10) [MSC v.1938 64 bit (AMD64)]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.33.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:




# %%

    # Now in Python!! (ipython interpreter in your terminal)
    
'''
    Import modules
      ==> os
    Import methods (fxns)
      ==> google.cloud.translate_v3.services.translation_service.TranslationServiceAsyncClient.translate_text
      ==> google.cloud.translate_v3.services.translation_service.TranslationServiceClient
      ==> method "translate_v3" from google.cloud.translate (SDK)

    COPY/PASTE the python code exactly as is into your terminal
'''
    # this is what your terminal looks like running python
In [1]:

    

    # this is the python code to copy/paste       
import os
from google.cloud import translate_v3 as translate


# %%

'''
  Set Google API variables (Google Cloud project used for translation work)
  Set Google credentials for billing and quots
  
'''
 

 
In [2]:
    
PROJECT_ID = "<your project ID>";
assert PROJECT_ID ;
project_id = PROJECT_ID


  # set ADC from Google as a Python env variable 
  
In [3]:
    
credential_path = "C:\\Users\\<you>\\AppData\\Roaming\\gcloud\\application_default_credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path



# %%

    # WINDOWS 10 ONLY!! (skip if running Windows 11)
'''
    Define the Python translation fxn, "translate_document" Windows 10
'''

    # Indents REMOVED from All original code lines o/w "indent errors" IPython
    # Path separators (forward slashes) must be DOUBLED (escape the fist slash )
    # Windows adds a HIDDEN .pdf extension to pdf files!!
    # CHANGE name of output file 
    
    
    # Cut/paste the ENTIRE translation fxn into IPython
    
    
    # the translation fxn: single doc to single language
    #     Source:
    https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_batch_translate_document

In [4]:
    
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
f = open('C:\\Users\\<you>\\Desktop\\gcTranslate_output.pdf', 'wb')
f.write(response.document_translation.byte_stream_outputs[0])
f.close()
print(f"Response: Detected Language Code - {response.document_translation.detected_language_code}")
return response


# %%

    # WINDOWS 10 ONLY!! (skip if running Windows 11)
'''
    Set name and path of doc to be translated Windows 10
    Set target language (code) for translation
'''

     # document to be translated Windows 10
     # path to the document (with DOUBLE SLASHES)
     
In [5]:

doc_to_translate = "Semiconductores-Tecnológico-Nacional-México.pdf" ;
doc_dir = "C:\\Users\\<you>\\Desktop\\Translate" ;
file_path = os.path.join(doc_dir, doc_to_translate)


# %%

    # WINDOWS 11 ONLY
'''
    Define the Python translation fxn, "translate_document" Windows 11
'''

    # NB path separators (forward slashes) must be DOUBLED (escape the fist slash)
    # NB Windows adds a HIDDEN .pdf extension to pdf files!!
    # NB cut/paste the ENTIRE translation fxn into IPython
    # CHANGE name of output file if desired
    
    
    # Cut/paste the ENTIRE translation fxn into IPython


  # the translation fxn: single doc to single language
  # Source:
https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v3.services.translation_service.TranslationServiceClient#google_cloud_translate_v3_services_translation_service_TranslationServiceClient_batch_translate_document

  
In [4]:
    
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

    # Output the translated document
    # Name of output file is currently set to, "gcTranslate_output.pdf"
    f = open('C:\\API_translate\\gcTranslate_output.pdf', 'wb')
    f.write(response.document_translation.byte_stream_outputs[0])
    f.close()

    # If not provided in the TranslationRequest, the translated file will only be returned through a byte-stream
    # and its output mime type will be the same as the input file's mime type
    print(
        f"Response: Detected Language Code - {response.document_translation.detected_language_code}"
    )

    return response




# %%

    # WINDOWS 11 Only
'''
    Set name and path of document to be translated
    Set target language (code) for translation
'''

     # document to be translated is currently,"Semiconductores-Tecnológico-Nacional-México.pdf"
     # path to the document (with DOUBLE SLASHES!!)
     
In [5]:
    # input the name of the doc to be translated (a .pdf file)
doc_to_translate = "Semiconductores-Tecnológico-Nacional-México.pdf" ;
doc_dir = "C:\\API_translate" ;
file_path = os.path.join(doc_dir, doc_to_translate)

# %%

    # Get language code(s) if needed

'''
Define "print_supported_languages Fxn" 
List all supported language codes
Output to text file

'''

In [6]: 

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

    # togglehashtag to select
# print_supported_languages("en") >> C:\Users\<you>\Desktop\language_codes.txt  # Windows 10

print_supported_languages("en") >> C:\API_translate\language_codes.txt  # Windows 11

# %%

'''
Set target language for translation
Need target language code
'''

In [7]:

target = "zh"




# %%

'''
    Translate !!!!
'''
 
In [8]: 

translate_document(project_id, file_path)


# %%

'''
Sample Ouput 
'''
  # Model used by Google to do the translation
  # Neural Machine Translation (NMT)
  
model: "projects/735387290281/locations/us-central1/models/general/nmt"


# %%

'''
  Clean up

'''
    # EXIT Cloud Shell IPython session
    # return to normal shell (terminal)
In [12]: 
    
    exit

      

    # DEACTIVATE the Python virtual environment with "conda deactivate"
 C:\Users\<you>\AppData\Local\spyder-6\Scripts> conda deactivate 
    

    
   # DELETE virtual environment folder and all files
   #    ==>  /q disables Yes/No prompting
   #    ==> /s means delete the file(s) from all subdirectories.
 C:\Users\<you>\AppData\Local\spyder-6\Scripts> rmdir /s /q venv-translate


    # check the removal
C:\Users\<you>\AppData\Local\spyder-6\Scripts> dir /b/s venv-translate


# %%

# THE END 
[Workflow_gcloudAPI_StndNMT_GenTranslation_WINDOWS_docs]

