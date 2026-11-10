"""
Mountain View NDVI 2022 - GeoTIFF metadata, visualization and analysis.

Outputs (saved to OUT_DIR):
  - <tif name>_tags.txt              TIFF tags / GeoTIFF metadata with file name as header
  - <tif name>_map.png               continuous NDVI map + histogram
  - <tif name>_classes.png           classified NDVI map (thresholds tuned to this scene)
  - <tif name>.csv                   x, y, ndvi table (valid pixels only)

Cells are marked with "# %%" so they run individually in Spyder.
"""

# %% 0) Imports and settings
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
import imagecodecs  # makes sure the LZW codec is available to tifffile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

TIF_PATH = Path(
    "/home/bruce-vdb/Desktop/Marron_Projects/CloudComputing/Professional-AI/"
    "Professional-AI_APIs_RemoteSensing/API_earthengine-api/HowTos/Maps/"
    "MountainView_NDVI_2022.tif"
)
OUT_DIR = Path("/home/bruce-vdb/Desktop")
STEM = TIF_PATH.stem

MAX_LEN = 500   # truncate very long tag values in the .txt (e.g. strip offsets)
BAND = 0        # only used if the file has more than one band
SCALE = 1.0     # set to 10000 if values look like -10000..10000 (scaled integers)

# Class breaks tuned to this scene (range about -0.28 to 0.52, median about 0.12)
EDGES = [-1.0, 0.0, 0.1, 0.2, 0.3, 1.0]
LABELS = [
    "< 0  (water / shadow)",
    "0 - 0.1  (bare / impervious)",
    "0.1 - 0.2  (very sparse veg)",
    "0.2 - 0.3  (sparse veg)",
    ">= 0.3  (moderate veg)",
]
COLORS = ["#2b83ba", "#bdbdbd", "#fee08b", "#a6d96a", "#1a9641"]


# %% 1) Write TIFF tags / metadata to a .txt file (file name as header)
txt_path = OUT_DIR / f"{STEM}_tags.txt"

with tifffile.TiffFile(TIF_PATH) as tif, open(txt_path, "w", encoding="utf-8") as f:
    title = f"TIFF FILE: {TIF_PATH.name}"
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


# %% 2) Load NDVI, mask nodata, get georeferencing
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


# %% 3) Continuous map + histogram
fig1, ax = plt.subplots(1, 2, figsize=(14, 6))

cmap_cont = plt.get_cmap("RdYlGn").copy()
cmap_cont.set_bad("lightgrey")           # masked pixels shown grey

im = ax[0].imshow(ndvi, cmap=cmap_cont, vmin=-0.3, vmax=0.55, extent=extent)
ax[0].set_title("NDVI - Mountain View 2022")
ax[0].set_xlabel("Longitude / X")
ax[0].set_ylabel("Latitude / Y")
fig1.colorbar(im, ax=ax[0], label="NDVI", shrink=0.8)

ax[1].hist(ndvi.compressed(), bins=60, color="seagreen", edgecolor="k")
ax[1].set_title("NDVI distribution")
ax[1].set_xlabel("NDVI")
ax[1].set_ylabel("Pixel count")

fig1.tight_layout()
fig1.savefig(OUT_DIR / f"{STEM}_map.png", dpi=200, bbox_inches="tight")  # save before show()
plt.show()


# %% 4) Classified map with tuned thresholds
cmap_cls = ListedColormap(COLORS)
cmap_cls.set_bad("white")
norm = BoundaryNorm(EDGES, cmap_cls.N)

fig2, ax2 = plt.subplots(figsize=(9, 7))
ax2.imshow(ndvi, cmap=cmap_cls, norm=norm, extent=extent)
ax2.set_title("NDVI classes - Mountain View 2022")
ax2.set_xlabel("Longitude / X")
ax2.set_ylabel("Latitude / Y")
ax2.legend(
    handles=[Patch(facecolor=c, edgecolor="k", label=l) for c, l in zip(COLORS, LABELS)],
    loc="center left", bbox_to_anchor=(1.01, 0.5), title="NDVI class",
)

fig2.tight_layout()
fig2.savefig(OUT_DIR / f"{STEM}_classes.png", dpi=200, bbox_inches="tight")
plt.show()


# %% 5) Summary statistics and class percentages
vals = ndvi.compressed()
print(f"valid pixels: {vals.size:,} of {ndvi.size:,}")
print(
    f"min {vals.min():.3f} | max {vals.max():.3f} | "
    f"mean {vals.mean():.3f} | median {np.median(vals):.3f} | std {vals.std():.3f}"
)

cls = np.digitize(vals, EDGES[1:-1])     # 0..4
for i, lab in enumerate(LABELS):
    print(f"{lab}: {(cls == i).mean() * 100:.1f}%")


# %% 6) Export to a table (x, y, ndvi)
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
