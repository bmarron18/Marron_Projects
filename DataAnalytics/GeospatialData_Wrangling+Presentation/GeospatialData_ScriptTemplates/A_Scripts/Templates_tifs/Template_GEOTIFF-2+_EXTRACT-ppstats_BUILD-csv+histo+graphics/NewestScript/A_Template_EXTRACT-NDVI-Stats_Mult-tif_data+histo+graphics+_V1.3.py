#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 14:55:18 2026
Modified:.22 Nov 2026

@author: bruce-vdb, claude


---------------------------------------------------------------------------
A_Template_EXTRACT-NDVI-Stats_Mult-tif_data+histo+graphics+_V1.3.py
----------------------------------------------------------------------------
GeoTIFF metadata, visualization and analysis.

Changes in V1.3:
  - Two concentric reference circles (100 m and 500 m radius) drawn on both
    maps as thin black dashed lines, centred on the middle of the raster
    (or on CENTER_X / CENTER_Y if set)

Changes in V1.2:
  - Class breaks and labels retuned to this scene (NDVI about 0.15 to 0.85)
  - Continuous map colour scale (vmin/vmax) can adapt to each file using the
    2nd and 98th percentiles (AUTO_SCALE = True)
  - interpolation="nearest" on both maps so pixels are drawn as crisp blocks
  - Axis labels changed to Easting / Northing (m): the file is projected
    (EPSG:32614, WGS 84 / UTM zone 14N), so the units are metres, not degrees

Outputs (saved to OUT_DIR):
  - <tif name>_tags.txt              TIFF tags / GeoTIFF metadata with file name as header
  - <tif name>_map.png               continuous NDVI map + histogram
  - <tif name>_classes.png           classified NDVI map
  - <tif name>.csv                   x, y, ndvi table (valid pixels only)

Cells are marked with "# %%" so they run individually in Spyder.
"""

# %% 

from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
import imagecodecs  # makes sure the LZW codec is available to tifffile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Circle

#=========================
# FILE TO PROCESS AND PARAMETERS (edit)
#==============================)
TIF_PATH = Path(
    "/home/bruce-vdb/Desktop/UMA_NDVI_2022_03.tif"
)
OUT_DIR = Path("/home/bruce-vdb/Desktop")
STEM = TIF_PATH.stem

MAX_LEN = 500   # truncate very long tag values in the .txt (e.g. strip offsets)
BAND = 0        # only used if the file has more than one band
SCALE = 1.0     # set to 10000 if values look like -10000..10000 (scaled integers)

# Continuous map colour scale
AUTO_SCALE = True          # True: vmin/vmax from percentiles of this file's data
PCT_LOW, PCT_HIGH = 2, 98  # percentiles used when AUTO_SCALE is True
VMIN_FIXED, VMAX_FIXED = 0.1, 0.85   # used when AUTO_SCALE is False

# Reference circles (radius in metres, same units as the UTM coordinates)
RING_RADII = [100, 500]
CENTER_X, CENTER_Y = None, None   # None = centre of the raster; or set UTM easting / northing
RING_COLOR = "black"
RING_LW = 0.8                     # thin line
RING_LABELS = True                # print "100 m" / "500 m" next to each circle

# Class breaks tuned to this scene (range about 0.15 to 0.85, median about 0.55)
EDGES = [-1.0, 0.2, 0.4, 0.6, 0.8, 1.0]
LABELS = [
    "< 0.2  (bare / very sparse)",
    "0.2 - 0.4  (sparse veg)",
    "0.4 - 0.6  (moderate veg)",
    "0.6 - 0.8  (dense veg)",
    ">= 0.8  (very dense veg)",
]
COLORS = ["#d73027", "#fee08b", "#a6d96a", "#1a9641", "#00441b"]


# %% 

#=================================================
#  WRITE .tIf TAGS/METADATA TO A .txt FILE
#======================================================
txt_path = OUT_DIR / f"{STEM}_tags.txt"

with tifffile.TiffFile(TIF_PATH) as tif, open(txt_path, "w", encoding="utf-8") as f:
    title = f"TIFF FILE: {TIF_PATH.name}"  #  (file name as header)
    f.write("=" * len(title) + "\n")
    f.write(title + "\n")
    f.write(f"Path: {TIF_PATH}\n")
    f.write(f"Pages: {len(tif.pages)}\n")
    f.write("=" * len(title) + "\n\n")

    for i, page in enumerate(tif.pages):
        f.write(f"--- Page {i} ---\n")
        f.write(
            f"shape: {page.shape}, dtype: {page.dtype}, "
            f"compression: {page.compression.name}\n"
        )

        data = page.asarray().astype("float64")
        f.write(
            f"min: {np.nanmin(data)}, max: {np.nanmax(data)}, "
            f"mean: {np.nanmean(data):.4f}\n"
        )

        for tag in page.tags.values():
            value = str(tag.value)
            if len(value) > MAX_LEN:
                value = value[:MAX_LEN] + " ... [truncated]"
            f.write(f"{tag.name}: {value}\n")
        f.write("\n")

    if tif.is_geotiff:
        f.write("--- GeoTIFF metadata ---\n")
        for k, v in tif.geotiff_metadata.items():
            f.write(f"{k}: {v}\n")

print(f"Saved tags to {txt_path}")


# %% 
#=================================
# LOAD NDVI, MASK NODATA
# GET GEOREFERENCING
#===================================
with tifffile.TiffFile(TIF_PATH) as tif:
    ndvi = tif.asarray().astype("float64")
    meta = tif.geotiff_metadata
    nodata = getattr(tif.pages[0], "nodata", None)

print("raw shape:", ndvi.shape)
ndvi = np.squeeze(ndvi)
if ndvi.ndim == 3:                       # multi-band file: pick one band
    ndvi = ndvi[BAND]

if nodata is not None:
    ndvi[ndvi == nodata] = np.nan
ndvi[~np.isfinite(ndvi)] = np.nan
ndvi = np.ma.masked_invalid(ndvi / SCALE)

# Pixel -> coordinate mapping (top-left origin)
sx, sy = meta["ModelPixelScale"][:2]
x0, y0 = meta["ModelTiepoint"][3:5]
nrows, ncols = ndvi.shape
extent = [x0, x0 + ncols * sx, y0 - nrows * sy, y0]   # left, right, bottom, top

# Colour scale limits for the continuous map
if AUTO_SCALE:
    vmin, vmax = np.percentile(ndvi.compressed(), [PCT_LOW, PCT_HIGH])
else:
    vmin, vmax = VMIN_FIXED, VMAX_FIXED
print(f"continuous colour scale: vmin {vmin:.3f}, vmax {vmax:.3f}")

# Centre for the reference circles
cx = CENTER_X if CENTER_X is not None else (extent[0] + extent[1]) / 2
cy = CENTER_Y if CENTER_Y is not None else (extent[2] + extent[3]) / 2
print(f"ring centre: E {cx:.1f}, N {cy:.1f}")


def draw_rings(axis):
    """Add thin black dashed circles (RING_RADII, metres) around the centre."""
    xlim, ylim = axis.get_xlim(), axis.get_ylim()   # keep the map extent unchanged
    for r in RING_RADII:
        axis.add_patch(Circle(
            (cx, cy), r, fill=False, edgecolor=RING_COLOR,
            linewidth=RING_LW, linestyle=(0, (5, 3)), zorder=5,
        ))
        if RING_LABELS:
            d = r / np.sqrt(2)                       # label at 45 degrees, upper right
            axis.text(
                cx + d, cy + d, f"{r} m", fontsize=7, ha="left", va="bottom",
                zorder=6,
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=1),
            )
    axis.set_xlim(xlim)
    axis.set_ylim(ylim)


# %% 
#============================
# GENERATE CONTINUOUS MAP + HISTOGRAM
#==========================================
fig1, ax = plt.subplots(1, 2, figsize=(14, 6))

cmap_cont = plt.get_cmap("RdYlGn").copy()
cmap_cont.set_bad("lightgrey")           # masked pixels shown grey

im = ax[0].imshow(
    ndvi, cmap=cmap_cont, vmin=vmin, vmax=vmax,
    extent=extent, interpolation="nearest",
)
draw_rings(ax[0])
ax[0].set_title("NDVI - UMA 2022")
ax[0].set_xlabel("Easting (m)")
ax[0].set_ylabel("Northing (m)")
fig1.colorbar(im, ax=ax[0], label="NDVI", shrink=0.8)

ax[1].hist(ndvi.compressed(), bins=60, color="seagreen", edgecolor="k")
ax[1].set_title("NDVI distribution")
ax[1].set_xlabel("NDVI")
ax[1].set_ylabel("Pixel count")

fig1.tight_layout()
fig1.savefig(OUT_DIR / f"{STEM}_map.png", dpi=200, bbox_inches="tight")  # save before show()
plt.show()


# %% 
#======================================
# GENERATE CLASSIFIED MAP W/ TUNED THRESHOLDS
#==============================================
cmap_cls = ListedColormap(COLORS)
cmap_cls.set_bad("white")
norm = BoundaryNorm(EDGES, cmap_cls.N)

fig2, ax2 = plt.subplots(figsize=(9, 7))
ax2.imshow(ndvi, cmap=cmap_cls, norm=norm, extent=extent, interpolation="nearest")
draw_rings(ax2)
ax2.set_title("NDVI classes - UMA 2022")
ax2.set_xlabel("Easting (m)")
ax2.set_ylabel("Northing (m)")
ax2.legend(
    handles=[Patch(facecolor=c, edgecolor="k", label=l) for c, l in zip(COLORS, LABELS)],
    loc="center left", bbox_to_anchor=(1.01, 0.5), title="NDVI class",
)

fig2.tight_layout()
fig2.savefig(OUT_DIR / f"{STEM}_classes.png", dpi=200, bbox_inches="tight")
plt.show()


# %% 
#==================================
# SUMMARY STATS + CLASS PERCENTAGES
#==================================
vals = ndvi.compressed()
print(f"valid pixels: {vals.size:,} of {ndvi.size:,}")
print(
    f"min {vals.min():.3f} | max {vals.max():.3f} | "
    f"mean {vals.mean():.3f} | median {np.median(vals):.3f} | std {vals.std():.3f}"
)

cls = np.digitize(vals, EDGES[1:-1])     # 0..4
for i, lab in enumerate(LABELS):
    print(f"{lab}: {(cls == i).mean() * 100:.1f}%")


# %% 
#============================================
# EXPORT NDVI DATA TO .csv (x, y, ndvi)
#==========================================
cols, rows = np.meshgrid(np.arange(ncols), np.arange(nrows))
df = pd.DataFrame({
    "x": (x0 + (cols + 0.5) * sx).ravel(),      # pixel centres, flattened to 1D
    "y": (y0 - (rows + 0.5) * sy).ravel(),
    "ndvi": np.ma.filled(ndvi, np.nan).ravel(),
}).dropna()

print(df.head())
print(f"rows: {len(df):,}")
csv_path = OUT_DIR / f"{STEM}.csv"
df.to_csv(csv_path, index=False)
print(f"Saved table to {csv_path}")
