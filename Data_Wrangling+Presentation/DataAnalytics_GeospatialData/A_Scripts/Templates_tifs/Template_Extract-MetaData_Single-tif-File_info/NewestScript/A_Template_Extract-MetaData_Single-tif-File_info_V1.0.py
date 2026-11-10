#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:01:37 2026

@author: bruce-vdb

Notes:

NaN values: NDVI exports from Earth Engine often contain NaNs or nodata pixels. If min, 
max and mean print nan, change those to data.nanmin(), data.nanmax() and data.nanmean() 
(and wrap with float(...) if you like).

Pixel data: I kept page.asarray() since it now feeds the summary stats. If you only want 
the tags, delete that line and the stats line, and it will run much faster on big files.

Tag truncation: MAX_LEN shortens very long tag values so the text file stays readable. 
Set it to a large number if you want everything.

Overwriting: The output is overwritten each run. If you want to keep earlier outputs, add a timestamp to the file name.

The LZW error will still occur until imagecodecs is visible to the Spyder kernel, so run the diagnostic from my previous message first if it persists.


"""


      
# %%

import tifffile
import imagecodecs  # makes sure the LZW codec is available to tifffile
from pathlib import Path

tif_path = Path("/home/bruce-vdb/Desktop/MountainView_NDVI_2022.tif")
out_path = Path("/home/bruce-vdb/Desktop") / f"{tif_path.stem}_tags.txt"

MAX_LEN = 500  # truncate very long tag values (e.g. strip offsets)

with tifffile.TiffFile(tif_path) as tif, open(out_path, "w", encoding="utf-8") as f:
    # Header
    title = f"TIFF FILE: {tif_path.name}"
    f.write("=" * len(title) + "\n")
    f.write(title + "\n")
    f.write(f"Path: {tif_path}\n")
    f.write(f"Pages: {len(tif.pages)}\n")
    f.write("=" * len(title) + "\n\n")

    for i, page in enumerate(tif.pages):
        f.write(f"--- Page {i} ---\n")
        f.write(f"shape: {page.shape}, dtype: {page.dtype}, "
                f"compression: {page.compression.name}\n")

        # Decode pixel data only to report summary stats (also tests the LZW codec)
        data = page.asarray()
        f.write(f"min: {data.min()}, max: {data.max()}, mean: {data.mean():.4f}\n")

        for tag in page.tags.values():
            value = str(tag.value)
            if len(value) > MAX_LEN:
                value = value[:MAX_LEN] + " ... [truncated]"
            f.write(f"{tag.name}: {value}\n")
        f.write("\n")

    # GeoTIFF metadata (CRS, tiepoints, etc.) if present
    if tif.is_geotiff:
        f.write("--- GeoTIFF metadata ---\n")
        for k, v in tif.geotiff_metadata.items():
            f.write(f"{k}: {v}\n")

print(f"Saved to {out_path}")

# %%

import numpy as np
import tifffile
import matplotlib.pyplot as plt
import pandas as pd

path = ("/home/bruce-vdb/Desktop/Marron_Projects/CloudComputing/Professional-AI/"
        "Professional-AI_APIs_RemoteSensing/API_earthengine-api/HowTos/Maps/"
        "MountainView_NDVI_2022.tif")

# ---------- 1) Load ----------
with tifffile.TiffFile(path) as tif:
    ndvi = tif.asarray().astype("float64")
    meta = tif.geotiff_metadata
    nodata = getattr(tif.pages[0], "nodata", None)

print("raw shape:", ndvi.shape)
ndvi = np.squeeze(ndvi)          # single band -> 2D. If 3D, pick a band: ndvi = ndvi[0]

# Mask nodata / NaN / out-of-range
if nodata is not None:
    ndvi[ndvi == nodata] = np.nan
ndvi[~np.isfinite(ndvi)] = np.nan
ndvi = np.ma.masked_invalid(ndvi)

# If values look like -10000..10000 (scaled ints), uncomment:
# ndvi = ndvi / 10000

# ---------- 2) Georeferencing (pixel -> coordinates) ----------
sx, sy = meta["ModelPixelScale"][:2]
x0, y0 = meta["ModelTiepoint"][3:5]          # top-left corner
nrows, ncols = ndvi.shape
extent = [x0, x0 + ncols * sx, y0 - nrows * sy, y0]   # left, right, bottom, top

# ---------- 3) Visualize ----------
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

im = ax[0].imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1, extent=extent)
ax[0].set_title("NDVI – Mountain View 2022")
ax[0].set_xlabel("Longitude / X")
ax[0].set_ylabel("Latitude / Y")
fig.colorbar(im, ax=ax[0], label="NDVI", shrink=0.8)

ax[1].hist(ndvi.compressed(), bins=60, color="seagreen", edgecolor="k")
ax[1].set_title("NDVI distribution")
ax[1].set_xlabel("NDVI")
ax[1].set_ylabel("Pixel count")

plt.tight_layout()
plt.show()

# ---------- 4) Analysis ----------
vals = ndvi.compressed()   # 1D array of valid pixels
print(f"valid pixels: {vals.size:,} of {ndvi.size:,}")
print(f"min {vals.min():.3f} | max {vals.max():.3f} | "
      f"mean {vals.mean():.3f} | median {np.median(vals):.3f} | std {vals.std():.3f}")

# Example: rough land-cover classes
bins = {"water/bare (<0.1)": vals < 0.1,
        "sparse (0.1-0.3)": (vals >= 0.1) & (vals < 0.3),
        "moderate (0.3-0.6)": (vals >= 0.3) & (vals < 0.6),
        "dense (>=0.6)": vals >= 0.6}
for name, m in bins.items():
    print(f"{name}: {m.mean() * 100:.1f}%")

# ---------- 5) Export to a table (x, y, ndvi) ----------
cols, rows = np.meshgrid(np.arange(ncols), np.arange(nrows))
df = pd.DataFrame({
    "x": (x0 + (cols + 0.5) * sx).ravel(),     # pixel centres, flattened to 1D
    "y": (y0 - (rows + 0.5) * sy).ravel(),
    "ndvi": np.ma.filled(ndvi, np.nan).ravel(),
}).dropna()
print(df.head())
print(f"rows: {len(df):,}")
df.to_csv("/home/bruce-vdb/Desktop/MountainView_NDVI_2022.csv", index=False)



