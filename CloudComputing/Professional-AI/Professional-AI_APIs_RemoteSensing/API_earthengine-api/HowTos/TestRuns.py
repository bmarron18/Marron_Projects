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
    * Must use name GOOGLE_APPLICATION_CREDENTIALS for env variable
    * The Earth Engine Python API is stateless: ee.Initialize() just stores your credentials and project in 
      memory and sends independent HTTPS requests to the server whenever you call something like .getInfo() or 
      start an export. There’s no persistent connection, session, or handle to release.



    
=========
SOURCES
=========
Google Earth Engine Python API: A Beginner's Tutorial
https://rsandgis.me/articles/google-earth-engine-python-api-tutorial.html


"""
# %%

'''
Test Credentials
'''

import os, json

p = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
print(p)
d = json.load(open(p))
print(d["client_email"], d["project_id"])



# %%

'''
Test GEE Access
'''

import os
import json
import ee

#==============
# CREDENTIALS
#==============

    # Fetch the credentials file details from your environment variable, "GOOGLE_APPLICATION_CREDENTIALS"
gac_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # open .json file
gac= json.load(open(gac_path))

    # extract credentials for login
email = gac["client_email"]
project_id = gac["project_id"]

credentials = ee.ServiceAccountCredentials(
    email,
    gac_path,
)

    # GEE API login 
ee.Initialize(credentials, project = project_id)

    # check 
print("Earth Engine initialized successfully using Application Default Credentials!")


# %%

  # Cancel a specific task you started
 
task.cancel()

  # Or cancel all active/pending tasks
for t in ee.batch.Task.list():
    if t.state in ("READY", "RUNNING"):
          t.cancel()









