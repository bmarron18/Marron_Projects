#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 24 Sept 2026
Revised:  22 Nov 2026  (v1.4: outputs go to one dated folder on the Desktop)
Authors : bruce-vdb, claude

-------------------------------------------------------
A_Template_PULL-Landsat8_DATE-timestack_CALC-NDVI-stat_BUILD_geotif+map_v1.4.py
----------------------------------------------------------

        * Pulls Landsat 8 (+9) Collection 2 Level 2 surface reflectance for a point of interest,
        * builds a cloud-masked, scale-corrected MEDIAN composite,
        * computes NDVI,
        * saves an interactive map (.html),
        * exports the NDVI as a GeoTIFF to a Google Cloud Storage bucket,
        * waits for the export to finish, and downloads the .tif.

        OUTPUT FOLDER (new in v1.4): the .html and the .tif are both saved in

            /home/bruce-vdb/Desktop/LANDSAT_<lon>,<lat>_<first-image-date>,<last-image-date>

        e.g. LANDSAT_-100.088829,19.190335_2022-01-09,2022-12-29
        The dates are the first and last acquisition dates of the scenes that
        survive the filters (so the folder name is built after the collection
        has been queried).

Based on: https://rsandgis.me/articles/google-earth-engine-python-api-tutorial.html

---------------------------------------------------------------------------
QUICK START
---------------------------------------------------------------------------
1. Packages (in the ai-apis venv):
 <<< bash
        cd ~/spyder-6/envs && source ./ai-apis/bin/activate

        python3 -m pip install --upgrade pip &&
        pip install --upgrade earthengine-api geemap google-cloud-storage &&
        pip list &&
        deactivate
 >>>


2. Service Account credentials: set GOOGLE_APPLICATION_CREDENTIALS in
   ~/.bashrc to the path of the service-account .json file.
<<< bash
      echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"' >> ~/.bashrc
      subl ~/.bashrc
      source ~/.bashrc
>>>


3. Run:  python3 this_script.py   (or run cell by cell in Spyder)

NB
  * The Earth Engine Python API is stateless: ee.Initialize() stores the
    credentials/project in memory; each .getInfo() or export is an
    independent HTTPS request. Nothing needs to be closed at the end.
  * The map (.html) is optional; set MAKE_MAP = False to skip it.


4. Generate Geospatial Analytics
      Run "A_Template_EXTRACT-NDVI-PPstat_1-geotif_BUILD-csv+histo+graphics_V1.3.py"
      (point it at the LANDSAT_<lon>,<lat>_<dates> folder created by this script)


5. Clean GCP bucket
<<< bash
        # list buckets
    gcloud storage ls --project=agremotesensing

        # list files in a bucket
    gcloud storage ls -l --recursive gs://ag-remote-bucket01/

        # delete file(s) from bucket
    gcloud storage rm gs://ag-remote-bucket01/*.tif

        # check
    gcloud storage ls -l --recursive gs://ag-remote-bucket01/

"""
# %%
# =============================================================================
# IMPORTS
# =============================================================================
import json
import os
import sys
import time
from pathlib import Path

import ee
from google.cloud import storage

# =============================================================================
# CONFIGURATION  (edit here)
# =============================================================================
ROI_LON_LAT = [-100.088829, 19.190335]   # Longitude, Latitude (UMA, VdB Mexico)
BUFFER_M = 3000                          # buffer around ROI, metres

START_DATE = "2022-01-01"
END_DATE = "2023-01-01"                  # filterDate end is EXCLUSIVE -> covers all of 2022

# Scene-level pre-filter. Pixel-level masking (QA_PIXEL) is applied below, so
# this can be looser than 10% and keeps more (rainy-season) scenes.
CLOUD_COVER_MAX = 30
INCLUDE_LANDSAT9 = True                 # True = merge Landsat 8 + 9 (more revisits)

EXPORT_CRS = "EPSG:32614"                # UTM 14N, correct for lon -100
EXPORT_SCALE = 30                        # metres (Landsat native)
BUCKET_NAME = "ag-remote-bucket01"
EXPORT_PREFIX = "-100.088829,19.190335_medianNDVI_2022"       # becomes <prefix>.tif in the bucket
EXPORT_DESCRIPTION = "UMA_Landsat8_medianNDVI_Export"

# Output location: one folder per run, created under OUTPUT_ROOT once the
# first/last image dates are known (see section 2-3). Holds the .html and .tif.
OUTPUT_ROOT = Path("/home/bruce-vdb/Desktop")
ROI_TAG = f"{ROI_LON_LAT[0]},{ROI_LON_LAT[1]}"   # "-100.088829,19.190335"
OUTPUT_DIR = None                        # set below -> OUTPUT_ROOT/LANDSAT_<ROI_TAG>_<first>,<last>
MAP_HTML = None                          # set below, inside OUTPUT_DIR

MAKE_MAP = True
RUN_EXPORT = True
RUN_DOWNLOAD = True
EXPORT_TIMEOUT_S = 30 * 60               # give up waiting after 30 min
POLL_EVERY_S = 15

# %%
# =============================================================================
# CREDENTIALS & INITIALISE
# =============================================================================
gac_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if not gac_path or not os.path.isfile(gac_path):
    sys.exit("GOOGLE_APPLICATION_CREDENTIALS is not set or points to a missing file.")

with open(gac_path) as f:
    gac = json.load(f)

email = gac["client_email"]
project_id = gac["project_id"]

credentials = ee.ServiceAccountCredentials(email, gac_path)
ee.Initialize(credentials, project=project_id)

# Small server-side calls to confirm Earth Engine works
assert ee.Number(1).add(1).getInfo() == 2, "Earth Engine basic call failed"
print("SRTM bands:", ee.Image("USGS/SRTMGL1_003").bandNames().getInfo())  # ['elevation']

# %%
# =============================================================================
# 1. Region of Interest (ROI)
# =============================================================================
roi = ee.Geometry.Point(ROI_LON_LAT)
area_of_interest = roi.buffer(BUFFER_M)

# %%
# =============================================================================
# 2-3. COLLECTION, FILTERS, CLOUD MASK + SCALE FACTORS
# =============================================================================
def mask_and_scale(img):
    """Mask fill/cloud/shadow pixels via QA_PIXEL and apply Collection 2 L2 scale factors."""
    qa = img.select("QA_PIXEL")
    clear = (
        qa.bitwiseAnd(1 << 0).eq(0)      # fill
        .And(qa.bitwiseAnd(1 << 1).eq(0))  # dilated cloud
        .And(qa.bitwiseAnd(1 << 2).eq(0))  # cirrus
        .And(qa.bitwiseAnd(1 << 3).eq(0))  # cloud
        .And(qa.bitwiseAnd(1 << 4).eq(0))  # cloud shadow
    )
    optical = img.select("SR_B.").multiply(0.0000275).add(-0.2)   # reflectance 0-1
    thermal = img.select("ST_B10").multiply(0.00341802).add(149.0)  # Kelvin
    return (
        img.addBands(optical, None, True)
        .addBands(thermal, None, True)
        .updateMask(clear)
    )


collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
if INCLUDE_LANDSAT9:
    collection = collection.merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2"))

filtered_collection = (
    collection
    .filterBounds(roi)
    .filterDate(START_DATE, END_DATE)
    .filter(ee.Filter.lt("CLOUD_COVER", CLOUD_COVER_MAX))
    .map(mask_and_scale)
)

count = filtered_collection.size().getInfo()
print(f"Number of images in filtered collection: {count}")
if count == 0:
    sys.exit("No images matched the filters; widen the dates or CLOUD_COVER_MAX.")

dates = (
    filtered_collection.aggregate_array("system:time_start")
    .map(lambda t: ee.Date(t).format("YYYY-MM-dd"))
    .getInfo()
)
dates = sorted(dates)                    # merged L8+L9 list is not guaranteed chronological
print("Acquisition dates:", dates)

# ---- Output folder: LANDSAT_<lon>,<lat>_<first-date>,<last-date> -----------
first_date, last_date = dates[0], dates[-1]
OUTPUT_DIR = OUTPUT_ROOT / f"LANDSAT_{ROI_TAG}_{first_date},{last_date}"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MAP_HTML = OUTPUT_DIR / f"{ROI_TAG}_UMA_map.html"
print("Output folder:", OUTPUT_DIR)

# %%
# =============================================================================
# 4-5.CREATE (stat = median) COMPOSITE, CLIP
# =============================================================================
median_composite = filtered_collection.median()
clipped_image = median_composite.clip(area_of_interest)

# %%
# =============================================================================
# NDVI  (Landsat 8/9: SR_B5 = NIR, SR_B4 = Red; reflectance already scaled)
# =============================================================================
ndvi_only = clipped_image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")

# %%
# =============================================================================
# INTERACTIVE MAP  (true colour + NDVI) -> .html  (saved in OUTPUT_DIR)
# =============================================================================
if MAKE_MAP:
    try:
        import geemap

        m = geemap.Map(center=[ROI_LON_LAT[1], ROI_LON_LAT[0]], zoom=11)

        vis_rgb = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 0.0, "max": 0.3, "gamma": 1.4}
        vis_ndvi = {"min": 0.0, "max": 1.0, "palette": ["blue", "white", "green"]}

        m.addLayer(clipped_image, vis_rgb, "Landsat True Color")
        m.addLayer(ndvi_only, vis_ndvi, "NDVI Layer")
        m.to_html(str(MAP_HTML))
        print("Map saved:", MAP_HTML)
    except Exception as exc:  # map is optional; don't kill the export
        print("Map step skipped:", exc)

# %%
# =============================================================================
# EXPORT NDVI GeoTIFF -> GCS bucket, then WAIT for it to finish
# =============================================================================
if RUN_EXPORT:
    task = ee.batch.Export.image.toCloudStorage(
        image=ndvi_only.toFloat(),
        description=EXPORT_DESCRIPTION,
        bucket=BUCKET_NAME,
        fileNamePrefix=EXPORT_PREFIX,
        scale=EXPORT_SCALE,
        region=area_of_interest,
        crs=EXPORT_CRS,
        maxPixels=1e13,
    )
    task.start()
    print("Export started. Task id:", task.id)

    t0 = time.time()
    while True:
        status = task.status()
        state = status["state"]
        print(f"  [{int(time.time() - t0):>4}s] export state: {state}")
        if state == "COMPLETED":
            break
        if state in ("FAILED", "CANCELLED", "CANCEL_REQUESTED"):
            sys.exit(f"Export ended with state {state}: {status.get('error_message')}")
        if time.time() - t0 > EXPORT_TIMEOUT_S:
            sys.exit(f"Timed out waiting for export (task id {task.id}). "
                     "Check later with ee.data.getTaskStatus(task_id).")
        time.sleep(POLL_EVERY_S)

# %%
# =============================================================================
# DOWNLOAD FROM BUCKET  -> OUTPUT_DIR (same folder as the .html)
# =============================================================================
if RUN_DOWNLOAD:
    client = storage.Client(project=project_id)   # picks up GOOGLE_APPLICATION_CREDENTIALS
    bucket = client.bucket(BUCKET_NAME)

    downloaded = []
    for blob in client.list_blobs(bucket, prefix=EXPORT_PREFIX):
        if blob.name.endswith(".tif"):
            dest = OUTPUT_DIR / Path(blob.name).name
            blob.download_to_filename(str(dest))
            downloaded.append(dest)
            print("Downloaded", blob.name, "->", dest)

    if not downloaded:
        print(f"No .tif found in gs://{BUCKET_NAME}/ with prefix '{EXPORT_PREFIX}'.")

# %%
print("Done. Outputs in:", OUTPUT_DIR)
