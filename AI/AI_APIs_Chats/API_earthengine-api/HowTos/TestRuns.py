#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 14:55:18 2026

@author: bruce-vdb

------------
TestRuns.py
-------------

    * test of various snippets for GEE use
    
    
---------------------------------------------------------------------------
QUICK START
---------------------------------------------------------------------------
1. Check packages installed in venv (ai-apis) and perform updates

<<< bash
    cd ~/spyder-6/envs && source ./ai-apis/bin/activate && 
    pip list &&
    
    python3 -m pip install --upgrade pip &&
    pip install --upgrade pip earthengine-api geemap && 
    earthengine authenticate --project agremotesensing &&
    deactivate
>>>

  2.  Permanently set the environment variable GOOGLE_APPLICATION_CREDENTIALS in ~/.bashrc and check
  
<<< bash
    echo 'export GOOGLE_APPLICATION_CREDENTIALS="/home/bruce-vdb/Desktop/Marron_Projects/AI/AI_APIs_Chats/API_earthengine-api/Credentials/agremotesensing-a0e16021eb39.json"' >> ~/.bashrc &&
    source ~/.bashrc &&
    subl  ~/.bashrc
>>>

NB
Must use name GOOGLE_APPLICATION_CREDENTIALS

When you call ee.Initialize(), the Earth Engine library asks the core Google Authentication system for credentials. 
Because the environment variable points directly to this file, the system handles the configuration for you:
    • It reads the client_email to know who is connecting.
    • It reads the private_key to cryptographically sign the connection request.
    • It reads the project_id to associate your billing and API quotas.


Much cleaner to let Google Cloud handle the credentials globally. 

sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
curl https://google.com | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

sudo rm -f /etc/apt/sources.list.d/google-cloud-sdk.list &&
sudo rm -f /etc/apt/sources.list.d/google-cloud-sdk.list.save
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://google.com cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install -y google-cloud-cli





    
=========
SOURCES
=========
Google Earth Engine Python API: A Beginner's Tutorial
https://rsandgis.me/articles/google-earth-engine-python-api-tutorial.html


"""




# %%


import os
import ee
import google.auth

    # 1. Fetch the credentials file path from your environment variable
gac_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


    # 2. Load the credentials directly from the file path and apply Earth Engine scopes
    # the comma and underscore credentials, _ = ... are used because google.auth.load_credentials_from_file() 
    # returns a tuple containing exactly two items, but your code only needs the first one.
    
    # Think of your Service Account JSON key as a physical passport, and these Scopes as the visa applications you submit
    # before traveling:
credentials, _ = google.auth.load_credentials_from_file(
    gac_path,
    scopes=[
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/earthengine",
    ],
)

# 3. Initialize using the loaded credentials
ee.Initialize(credentials=credentials, project="your-project-id")

print("Earth Engine initialized successfully using Application Default Credentials!")



# %%

# Alternative A: Grab the project ID too, instead of throwing it away
credentials, default_project = google.auth.load_credentials_from_file(...)

# Alternative B: Standard indexing (grab just the first item at index 0)
response = google.auth.load_credentials_from_file(...)
credentials = response[0]














