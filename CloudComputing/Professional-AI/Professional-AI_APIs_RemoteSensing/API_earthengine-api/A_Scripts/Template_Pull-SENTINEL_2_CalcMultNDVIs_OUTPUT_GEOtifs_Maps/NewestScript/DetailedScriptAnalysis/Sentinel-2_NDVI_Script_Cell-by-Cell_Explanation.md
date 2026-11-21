# Sentinel-2 NDVI Script: Cell-by-Cell Explanation

2026-11-20

## Overview

The script pulls a year of Sentinel-2 imagery for one point, builds NDVI statistics and a true-colour image, exports them as GeoTIFFs, and downloads everything into one Desktop folder. Spyder splits a file into cells at each `# %%` line, so each block can be run on its own. Line numbers refer to the v1_3 Sentinel-2 script, and Cell 0 is the code before the first `# %%`.

Run order matters: Cell 5 creates `OUTPUT_DIR`, which Cells 8, 9 and 11 need.

## Cell 0: header and docstring (lines 1-103)

Nothing in this cell runs. It holds the shebang and encoding lines, then a long docstring.

- The docstring records authorship and dates, the five outputs (RGB reflectance GeoTIFF, 8-bit GeoTIFF, PNG, four NDVI statistics), the differences from the Landsat script, and the setup steps.
- Step 5 (lines 87-100) gives the `gcloud storage` commands to list and clean the bucket. The `rm gs://ag-remote-bucket01/UMA_S2*.tif` line deletes every matching file permanently, so run `ls` first.

## Cell 1: imports and configuration (lines 104-144)

Spyder treats the imports and the configuration as one cell, because there is no `# %%` between them.

- **Imports:** `json`, `os`, `sys`, `time` and `Path` are standard library. `urllib.request` fetches the PNG. `ee` is the Earth Engine API and `storage` is the Google Cloud Storage client.
- **Location and area:** `ROI_LON_LAT` is a [lon, lat] list (Earth Engine uses lon first) and `BUFFER_M = 3000` is the radius in metres.
- **Dates:** `END_DATE` is exclusive, so 2022-01-01 to 2023-01-01 covers all of 2022.
- **Cloud filter:** `CLOUD_COVER_MAX = 30` is applied later to the scene property `CLOUDY_PIXEL_PERCENTAGE`.
- **Export settings:** `EXPORT_CRS` is UTM zone 14N, `EXPORT_SCALE = 10` is the pixel size in metres, and `BUCKET_NAME` and `EXPORT_PREFIX` name the bucket and the file-name prefix.
- **Output switches:** `STATS` lists the NDVI statistics. `EXPORT_RGB` and `RGB_VIS` control the true-colour export and its stretch. `RGB_PNG_PIXELS` is the PNG's longest side.
- **Local output:** `DESKTOP_DIR` and `FOLDER_PREFIX` set where the local folder goes. The folder itself is built in Cell 5.
- **Run controls:** `MAKE_MAP`, `RUN_EXPORT` and `RUN_DOWNLOAD` switch whole stages on or off. `EXPORT_TIMEOUT_S` and `POLL_EVERY_S` control how long and how often the export wait loop checks.

## Cell 2: credentials and initialise (lines 146-160)

This cell authenticates to Earth Engine with the service account.

- It reads the path from the `GOOGLE_APPLICATION_CREDENTIALS` environment variable and exits with a clear message if it is unset or the file is missing.
- It loads the service-account JSON to get `client_email` and `project_id`.
- `ee.ServiceAccountCredentials(...)` and `ee.Initialize(...)` authenticate. The Python API is stateless, so this just stores the credentials in memory.
- `assert ee.Number(1).add(1).getInfo() == 2` is a quick check that a server-side round trip works.

## Cell 3: region of interest (lines 162-168)

This cell defines two shapes around the centre point.

- `ee.Geometry.Point(ROI_LON_LAT)` is the centre point.
- `roi.buffer(BUFFER_M)` makes a circle, `area_of_interest`, which is used to clip the NDVI products.
- `.bounds()` makes the bounding rectangle, `aoi_box`, which is used for the RGB outputs so the picture has no empty corners.

## Cell 4: collection, cloud mask and scaling (lines 170-212)

This cell selects the images and cleans them.

- **`mask_and_scale(img)`** runs on every image.
  - It selects the Scene Classification Layer (SCL) and builds a boolean `clear` image by chaining `.neq()` and `.And()`. It rejects classes 0 (no data), 1 (saturated), 3 (cloud shadow), 8 and 9 (cloud), 10 (cirrus) and 11 (snow/ice). Classes 2 (dark area) and 4 to 7 (vegetation, soil, water, unclassified) stay.
  - `img.select("B.*")` is a regex that matches the reflectance bands (B1 to B12, B8A) but not SCL, AOT or the other auxiliary bands. Multiplying by 0.0001 converts digital numbers to reflectance from 0 to 1.
  - `addBands(optical, None, True)` overwrites the original bands in place. `updateMask(clear)` then hides the unwanted pixels in every band.
- **Collection and filters:** `COPERNICUS/S2_SR_HARMONIZED` is filtered by location, dates and the scene-level cloud percentage, then mapped through the function.
- **`count`:** `.size().getInfo()` is the first call that pulls a value to your machine. If it is zero, the script exits.
- **`dates`:** `aggregate_array("system:time_start")` pulls the timestamps, the lambda formats them server-side as `YYYY-MM-dd` in UTC, and `getInfo()` returns a Python list. This counts images, not unique dates: adjacent Sentinel-2 tiles overlap, so the same date can appear twice.

## Cell 5: output folder (lines 214-223)

This cell builds the single folder that receives every local output.

- `min(dates)` and `max(dates)` give the first and last acquisition. Plain string comparison works because the format is ISO.
- `folder_name` joins the prefix, `lon,lat` and the two dates. `DESKTOP_DIR / folder_name` builds the path, and `mkdir(parents=True, exist_ok=True)` creates it without failing if it already exists.
- `MAP_HTML` is defined here because it depends on `OUTPUT_DIR`.
- The dates are those of the images that survived the cloud filter, not `START_DATE` and `END_DATE`.
- Run this cell before Cells 8, 9 and 11 in Spyder, since they need `OUTPUT_DIR`.

## Cell 6: true-colour composite (lines 225-230)

This cell builds the visible-spectrum image from the median of the clear observations.

- `.select(["B4","B3","B2"])` takes red, green and blue from every image. `.median()` then reduces the stack to one image, taking each pixel's median over time from its unmasked observations only.
- `.visualize(bands=..., **RGB_VIS)` applies the min/max/gamma stretch. The result is an 8-bit, 3-band image, ready for display, while `rgb_median` keeps the true reflectance values.

## Cell 7: NDVI per image, then statistics (lines 232-253)

This cell defines the four NDVI products. Nothing is computed yet: these are lazy server-side recipes, and the work happens at export or display time.

- `ndvi_collection` computes NDVI = (B8 - B4)/(B8 + B4) for each image with `normalizedDifference`, then renames the band to `NDVI`. NDVI is taken before the statistics, because the median of NDVI is not the same as the NDVI of a median composite.
- `REDUCERS` maps each name to the matching collection method (`.median()`, `.min()`, `.max()`, `.mean()`).
- A guard exits if `STATS` contains an unknown name.
- The dictionary comprehension builds one image per statistic, renames the band (for example `NDVI_max`) and clips it to the circle. Pixels outside the circle become masked.

## Cell 8: interactive map (lines 255-273)

This cell writes one self-contained HTML map to the output folder.

- `geemap` is imported inside the `try` block, so a missing package skips the map instead of stopping the script.
- It creates a map centred on the ROI at zoom 13 and defines two visualisations: a reflectance stretch for RGB and a blue-white-green palette for NDVI.
- It adds the RGB layer first, then all four NDVI layers with `shown=(s == "median")`. Only the median layer is visible by default, and the others are available in the layer control.
- `m.to_html(...)` writes the file.

## Cell 9: local PNG (lines 275-290)

This cell saves a quick-look PNG without involving the bucket.

- `getThumbURL` asks Earth Engine to render the 8-bit image over `aoi_box`, at up to `RGB_PNG_PIXELS` on the longest side, as a PNG, and returns a temporary URL.
- `urlretrieve` downloads it straight to the output folder.
- The `try`/`except` makes the step non-fatal.

## Cell 10: exports to the bucket (lines 292-344)

This cell starts up to six export tasks at once and waits for them. All tasks run on Google's servers, and your script only polls them.

- **`start_export`** builds the file prefix (`UMA_S2_2022_04_<product>`) and creates an `Export.image.toCloudStorage` task with scale, CRS, region and `GeoTIFF` format. It starts the task and returns the prefix and the task.
- **Which exports:** the four NDVI statistics are cast with `.toFloat()` and use the circle as their region. `RGB_reflectance` uses the box. `RGB_8bit` uses `.toByte()`.
- **The wait loop:**
  - Every `POLL_EVERY_S` seconds it checks each pending task's status.
  - Completed tasks are removed. `FAILED` or `CANCELLED` stops the script with Earth Engine's error message.
  - The loop also exits after `EXPORT_TIMEOUT_S`.

## Cell 11: download (lines 346-366)

This cell copies the exported GeoTIFFs from the bucket into the output folder.

- It creates a Storage client and bucket handle using the same service account.
- It uses `export_prefixes` from Cell 10. If `RUN_EXPORT` is False, it falls back to the base prefix, so it can fetch files from an earlier run.
- For each prefix it lists the matching objects and downloads those ending in `.tif`. Prefix matching also catches tiled outputs, which Earth Engine splits into several files if an image is large.
- Leftover files from an older run with the same prefix would also be downloaded. That is why `EXPORT_PREFIX` is incremented (`_04`) and why the bucket-cleanup step exists.

## Cell 12: finish (lines 368-370)

This cell prints the output folder and "Done."

## Observations

- The reducers use only unmasked observations, so a pixel with few clear dates has a noisier min, max or median than its neighbours.
- The circle clip means the NDVI GeoTIFFs have empty (nodata) corners, while the RGB files cover the full square.
- The "dates" list counts images, not unique days, because overlapping tiles repeat dates.
- Cells 8, 9 and 11 depend on `OUTPUT_DIR` from Cell 5, so run Cell 5 first when working cell by cell.
