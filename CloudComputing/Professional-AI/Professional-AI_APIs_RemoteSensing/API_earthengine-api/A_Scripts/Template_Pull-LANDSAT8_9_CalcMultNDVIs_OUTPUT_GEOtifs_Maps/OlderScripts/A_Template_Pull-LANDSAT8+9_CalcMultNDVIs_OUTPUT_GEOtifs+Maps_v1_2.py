#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 18 Nov 2026
Revised:  20 Nov 2026
Authors : bruce-vdb, claude


--------------------------------------------------------
A_Template_Pull-LANDSAT8+9_CalcMultNDVIs_OUTPUT_GEOtifs+Maps_v1_2
--------------------------------------------------------
Revision of v1_1 (claude, Nov 2026). Changes:

  1. Visible-spectrum (true colour) composite is now EXPORTED:
       - <prefix>_RGB_reflectance.tif : 3-band float, reflectance 0-1 (analysis)
       - <prefix>_RGB_8bit.tif        : 8-bit stretched image (viewing)
       - <prefix>_RGB.png             : local PNG via getThumbURL (no bucket)
  2. NDVI statistics over time: median, min, max, mean (STATS list), each
     exported as its own GeoTIFF: <prefix>_NDVI_<stat>.tif
     NDVI is computed PER IMAGE first, then reduced across time (this is
     not the same as NDVI of a median composite).

Notes
  * RGB uses the median composite only. Per-band min/max across dates mixes
    different days in each band, so it is not a real picture.
  * Landsat is 30 m/pixel; it will not match Google Maps resolution.
    Increase BUFFER_M for a larger visual, or use Sentinel-2 for 10 m.
  * Setup (packages, GOOGLE_APPLICATION_CREDENTIALS) as in v1_1.
  
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
  
    4. NEXT STEP
       Run "A_Template_Extract-NDVI-Data_Mult-GEOtif-Files_data+graphics+stats_V1.2.py"
  
"""
# %%
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import ee
from google.cloud import storage

# =============================================================================
# CONFIGURATION
# =============================================================================
ROI_LON_LAT = [-100.088829, 19.190335]   # Longitude, Latitude (UMA, VdB Mexico)
BUFFER_M = 3000                          # buffer around ROI, metres

START_DATE = "2022-01-01"
END_DATE = "2023-01-01"                  # end exclusive

CLOUD_COVER_MAX = 30
INCLUDE_LANDSAT9 = True

EXPORT_CRS = "EPSG:32614"
EXPORT_SCALE = 30
BUCKET_NAME = "ag-remote-bucket01"
EXPORT_PREFIX = "UMA_2022_04"            # files become <prefix>_<product>.tif

STATS = ["median", "min", "max", "mean"]  # NDVI statistics to export
EXPORT_RGB = True
RGB_VIS = {"min": 0.0, "max": 0.3, "gamma": 1.4}   # stretch for 8-bit/PNG
RGB_PNG_PIXELS = 1024                    # longest side of local PNG

OUTPUT_DIR = Path.home() / "Desktop"
MAP_HTML = OUTPUT_DIR / "UMA_map.html"

MAKE_MAP = True
RUN_EXPORT = True
RUN_DOWNLOAD = True
EXPORT_TIMEOUT_S = 30 * 60
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

project_id = gac["project_id"]
credentials = ee.ServiceAccountCredentials(gac["client_email"], gac_path)
ee.Initialize(credentials, project=project_id)
assert ee.Number(1).add(1).getInfo() == 2, "Earth Engine basic call failed"

# %%
# =============================================================================
# Region of Interest (ROI)
# =============================================================================
roi = ee.Geometry.Point(ROI_LON_LAT)
area_of_interest = roi.buffer(BUFFER_M)      # circle (used to clip NDVI)
aoi_box = area_of_interest.bounds()          # square (used for RGB export)

# %%
# =============================================================================
# COLLECTION, CLOUD MASK + SCALE FACTORS
# =============================================================================
def mask_and_scale(img):
    qa = img.select("QA_PIXEL")
    clear = (
        qa.bitwiseAnd(1 << 0).eq(0)
        .And(qa.bitwiseAnd(1 << 1).eq(0))
        .And(qa.bitwiseAnd(1 << 2).eq(0))
        .And(qa.bitwiseAnd(1 << 3).eq(0))
        .And(qa.bitwiseAnd(1 << 4).eq(0))
    )
    optical = img.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal = img.select("ST_B10").multiply(0.00341802).add(149.0)
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
print("Acquisition dates:", dates)

# %%
# =============================================================================
# VISIBLE (TRUE-COLOUR) COMPOSITE  -> median of the RGB bands
# =============================================================================
rgb_median = filtered_collection.select(["SR_B4", "SR_B3", "SR_B2"]).median()
rgb_8bit = rgb_median.visualize(bands=["SR_B4", "SR_B3", "SR_B2"], **RGB_VIS)

# %%
# =============================================================================
# NDVI PER IMAGE, THEN STATISTICS OVER TIME
# =============================================================================
ndvi_collection = filtered_collection.map(
    lambda img: img.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
)

REDUCERS = {
    "median": lambda c: c.median(),
    "min": lambda c: c.min(),
    "max": lambda c: c.max(),
    "mean": lambda c: c.mean(),
}
unknown = [s for s in STATS if s not in REDUCERS]
if unknown:
    sys.exit(f"Unknown STATS entries: {unknown}. Choose from {list(REDUCERS)}.")

ndvi_images = {
    s: REDUCERS[s](ndvi_collection).rename(f"NDVI_{s}").clip(area_of_interest)
    for s in STATS
}

# %%
# =============================================================================
# INTERACTIVE MAP -> .html
# =============================================================================
if MAKE_MAP:
    try:
        import geemap

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        m = geemap.Map(center=[ROI_LON_LAT[1], ROI_LON_LAT[0]], zoom=13)
        vis_rgb = {"bands": ["SR_B4", "SR_B3", "SR_B2"], "min": 0.0, "max": 0.3, "gamma": 1.4}
        vis_ndvi = {"min": 0.0, "max": 1.0, "palette": ["blue", "white", "green"]}

        m.addLayer(rgb_median.clip(aoi_box), vis_rgb, "Landsat True Color (median)")
        for s, im in ndvi_images.items():
            m.addLayer(im, vis_ndvi, f"NDVI {s}", shown=(s == "median"))
        m.to_html(str(MAP_HTML))
        print("Map saved:", MAP_HTML)
    except Exception as exc:
        print("Map step skipped:", exc)

# %%
# =============================================================================
# LOCAL PNG OF THE TRUE-COLOUR IMAGE (no bucket needed)
# =============================================================================
if EXPORT_RGB:
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        url = rgb_8bit.getThumbURL({
            "region": aoi_box,
            "dimensions": RGB_PNG_PIXELS,
            "format": "png",
        })
        png_path = OUTPUT_DIR / f"{EXPORT_PREFIX}_RGB.png"
        urllib.request.urlretrieve(url, str(png_path))
        print("RGB PNG saved:", png_path)
    except Exception as exc:
        print("RGB PNG step skipped:", exc)

# %%
# =============================================================================
# EXPORTS -> GCS (all started together, then polled together)
# =============================================================================
def start_export(image, product, region):
    prefix = f"{EXPORT_PREFIX}_{product}"
    task = ee.batch.Export.image.toCloudStorage(
        image=image,
        description=prefix[:100],
        bucket=BUCKET_NAME,
        fileNamePrefix=prefix,
        scale=EXPORT_SCALE,
        region=region,
        crs=EXPORT_CRS,
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
    task.start()
    print(f"Export started: {prefix}  (task id {task.id})")
    return prefix, task


export_prefixes = []
if RUN_EXPORT:
    tasks = {}
    for s, im in ndvi_images.items():
        p, t = start_export(im.toFloat(), f"NDVI_{s}", area_of_interest)
        tasks[p] = t
    if EXPORT_RGB:
        p, t = start_export(rgb_median.toFloat(), "RGB_reflectance", aoi_box)
        tasks[p] = t
        p, t = start_export(rgb_8bit.toByte(), "RGB_8bit", aoi_box)
        tasks[p] = t

    export_prefixes = list(tasks)
    t0 = time.time()
    pending = dict(tasks)
    while pending:
        for p, t in list(pending.items()):
            status = t.status()
            state = status["state"]
            if state == "COMPLETED":
                print(f"  [{int(time.time() - t0):>4}s] {p}: COMPLETED")
                del pending[p]
            elif state in ("FAILED", "CANCELLED", "CANCEL_REQUESTED"):
                sys.exit(f"{p} ended with state {state}: {status.get('error_message')}")
        if not pending:
            break
        if time.time() - t0 > EXPORT_TIMEOUT_S:
            sys.exit(f"Timed out; still pending: {list(pending)}. "
                     "Check later with ee.data.getTaskStatus(task_id).")
        print(f"  [{int(time.time() - t0):>4}s] waiting on {len(pending)} export(s)...")
        time.sleep(POLL_EVERY_S)

# %%
# =============================================================================
# DOWNLOAD FROM BUCKET
# =============================================================================
if RUN_DOWNLOAD:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = storage.Client(project=project_id)
    bucket = client.bucket(BUCKET_NAME)

    # If RUN_EXPORT was False, fall back to everything with the base prefix.
    prefixes = export_prefixes or [EXPORT_PREFIX]
    downloaded = []
    for pfx in prefixes:
        for blob in client.list_blobs(bucket, prefix=pfx):
            if blob.name.endswith(".tif"):
                dest = OUTPUT_DIR / Path(blob.name).name
                blob.download_to_filename(str(dest))
                downloaded.append(dest)
                print("Downloaded", blob.name, "->", dest)

    if not downloaded:
        print(f"No .tif found in gs://{BUCKET_NAME}/ for prefixes {prefixes}.")

# %%
print("Done.")
