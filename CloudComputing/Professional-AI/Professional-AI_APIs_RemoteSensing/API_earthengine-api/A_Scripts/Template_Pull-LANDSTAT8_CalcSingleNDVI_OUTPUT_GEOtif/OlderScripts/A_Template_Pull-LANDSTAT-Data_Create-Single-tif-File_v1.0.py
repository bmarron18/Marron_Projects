#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 14:55:18 2026
Modified: 18 Nov 2026

@author: bruce-vdb

------------
UMA_NDVI.py
-------------

    * Based on Google Earth Engine Python API: A Beginner's Tutorial
    https://rsandgis.me/articles/google-earth-engine-python-api-tutorial.html
    
    
---------------------------------------------------------------------------
QUICK START
---------------------------------------------------------------------------
1. Check packages installed in venv (ai-apis) and perform updates

<<< bash
    cd ~/spyder-6/envs && source ./ai-apis/bin/activate && 
    pip list &&
    
    python3 -m pip install --upgrade pip &&
    pip install --upgrade pip earthengine-api geemap jupyterlab ipyleaflet jupytext "ipykernel>=6.29.3,<7" google-cloud-storage && 
    pip check &&
    pip list | grep -i -E "ipykernel|spyder-kernels|jupyterlab"
    
ipykernel                 6.31.0
jupyterlab                4.6.5
jupyterlab_pygments       0.3.0
jupyterlab_server         2.28.1
jupyterlab_widgets        3.0.17
spyder-kernels            3.1.5

    deactivate
>>>

  2.  Permanently set the environment variable GOOGLE_APPLICATION_CREDENTIALS in ~/.bashrc and check
      The env variable is keyed to a .json file used for authetication with Service Accounts
  
<<< bash
    echo 'export GOOGLE_APPLICATION_CREDENTIALS="/home/bruce-vdb/path-to/agremotesensing-a0e16021eb39.json"' >> ~/.bashrc &&
    subl  ~/.bashrc  &&
    source ~/.bashrc 
    
>>>

NB
    * Must use name GOOGLE_APPLICATION_CREDENTIALS for env variable
    * The Earth Engine Python API is stateless: ee.Initialize() just stores your credentials and project in 
      memory and sends independent HTTPS requests to the server whenever you call something like .getInfo() or 
      start an export. There’s no persistent connection, session, or handle to release.

"""
# %%


import os
import json
import ee
import geemap
from google.cloud import storage

#==============
# CREDENTIALS
#==============

    # Path to Service Account credentials .json file
gac_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # open the Service Account credentials .json file
with open(gac_path) as f:
    gac = json.load(f)
    
    if not gac_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set")


    # extract credentials for login
email = gac["client_email"]
project_id = gac["project_id"]

credentials = ee.ServiceAccountCredentials(
    email,
    gac_path,
)

    # GEE API login 
ee.Initialize(credentials, project = project_id)

#======================
#GEE  Functionality Checks
#=======================
    # make small, server-side calls to check GEE functionaslity
print(ee.Number(1).add(1).getInfo())  # should print 2

img = ee.Image("USGS/SRTMGL1_003")
print(img.bandNames().getInfo())  # <== should print ['elevation']






# %%

#====================
# TUTORIAL SNIPPETS
#===================

# %%

'''
 1. Define a Region of Interest (ROI) over time
 2. Use Landsat 8 Surface Reflectance Image Collection
 3. Filter data
 4. Create single, composite image
 5. Clip the composite image with a buffer around ROI

'''

    # define a point of interest and filter the collection to retrieve images for the year 2022.
    # Define a Region of Interest (ROI) using a Point coordinate
roi = ee.Geometry.Point([-100.088829, 19.190335]) # Longitude, Latitude (UMA, VdB Mexico)

    # Load the Landsat 8 Surface Reflectance Image Collection
landsat_collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

    # Apply filters: location, date, and cloud cover
filtered_collection = (landsat_collection
    .filterBounds(roi)
    .filterDate('2022-01-01', '2022-12-31')
    .filter(ee.Filter.lt('CLOUD_COVER', 10))) # Less than 10% cloud cover

    # Get the number of images in our filtered collection
count = filtered_collection.size().getInfo()
print(f"Number of images in filtered collection: {count}")


    # Reduce the collection to a single image by calculating the median
median_composite = filtered_collection.median()

    # Clip the composite to a specific area if desired (optional)
    # buffer around the ROI (in meters)
area_of_interest = roi.buffer(1000)
clipped_image = median_composite.clip(area_of_interest)

# %%

'''
Calculating Vegetation Indices (NDVI)
In Landsat 8, Band 4 is Red and Band 5 is NIR
'''

    # Define a function to calculate NDVI
def calculate_ndvi(image):
    # The Normalized Difference function computes (band1 - band2) / (band1 + band2)
    # Landsat 8: Band 5 is NIR, Band 4 is Red
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    
    # Return the image with the new NDVI band added
    return image.addBands(ndvi)

    # Apply the function to our median composite
image_with_ndvi = calculate_ndvi(clipped_image)

    # Select only the NDVI band for focused analysis
ndvi_only = image_with_ndvi.select('NDVI')


# %%

'''
 Interactive Visualization with Geemap
 Visualize both the true-color composite and the calculated NDVI layer
 
 
 <<< bash
     cd ~/spyder-6/envs && source ./ai-apis/bin/activate && 
     jupytext --to notebook ~/Desktop/Marron_Projects/AI/AI_APIs_Chats/API_earthengine-api/HowTos/TestRuns_Tutorials.py &&
     jupyter lab ~/Desktop/Marron_Projects/AI/AI_APIs_Chats/API_earthengine-api/HowTos/TestRuns_Tutorials.ipynb
     deactivate
 >>>
 
 In Jupyter .ipynb, add a cell to check correct kernel is running (ie, inside venv)
 
 <<< python
import sys
print(sys.executable)
>>>

'''


    # Create an interactive map centered on our ROI
Map = geemap.Map(center=[19.190335, -100.088829], zoom=11)

    # Define visualization parameters for True Color (RGB: Bands 4, 3, 2)
    # Note: Landsat 8 Collection 2 requires scale factors applied for precise reflectance, 
    # but for simple visualization, we can define arbitrary min/max.
vis_params_rgb = {
    'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
    'min': 0,
    'max': 30000,
    'gamma': 1.4
}

    # Define visualization parameters for NDVI (values range from -1 to 1)
vis_params_ndvi = {
    'min': 0.0,
    'max': 1.0,
    'palette': ['blue', 'white', 'green']
}

    # Add the layers to the map
Map.addLayer(clipped_image, vis_params_rgb, 'Landsat 8 True Color')
Map.addLayer(ndvi_only, vis_params_ndvi, 'NDVI Layer')

    # Display the map (only in Jup notebook)
#Map

    # Export as .html
Map.to_html("/home/bruce-vdb/Desktop/UMA_map.html")


# %%

'''
Export NDVI image as a GeoTIFF to GCP Bucket


If task fails
<<< python
	# after ee.Initialize(...)
op = ee.data.getTaskStatus("H2YACZGMB4F5RWRYAMJVRDF7")
print(op)
>>>

'''


    # Define export task parameters
export = ee.batch.Export.image.toCloudStorage(
    image=ndvi_only,
    description='Landsat8_NDVI_Export',
    bucket="ag-remote-bucket01",
    fileNamePrefix='UMA_NDVI_2022_02',
    scale=30,
    region=area_of_interest,
    crs='EPSG:32614',
    maxPixels=1e13,
)

export.start()

print(export.status())

# %%

'''
Download from Bucket using gcloud

<<< bash
    # get list of files in bucket
gcloud storage ls -l --recursive gs://ag-remote-bucket01/

    # download "UMA_NDVI_2022_02.tif" to Desktop
gcloud storage cp gs://ag-remote-bucket01/UMA*.tif ~/Desktop/

'''

# %%
'''
Download from Bucket using Python

'''

client = storage.Client(project="agremotesensing")
bucket = client.bucket("ag-remote-bucket01")

for blob in client.list_blobs(bucket, prefix="UMA_NDVI_2022"):
    if blob.name.endswith(".tif"):
        blob.download_to_filename(f"/home/bruce-vdb/Desktop/{blob.name}")
        print("Downloaded", blob.name)



# %%

'''
Get NDVI Data and Graphics

    run
    A_Template_Extract-NDVI-Data_Single-tif-File_data+graphics+stats_V1.1.py

'''















