#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 10 Nov 2026
Revised :
Authors : bruce-vdb, claude

-------------------------------------------------
A_Template_Raster-to-RGB-GeoTIFF_v1.0.py
-------------------------------------------------
    Reads a single-band raster (e.g. an ESRI ASCII grid, .asc) with rasterio,
    colours every cell using a colour ramp, and writes a georeferenced
    3-band (or 4-band, with transparency) 8-bit RGB GeoTIFF.

    Output:  <name>_rgb.tif

    This is the open-source rewrite of the old GDAL "projection_asciiraster"
    snippet. Fixes vs. the original:
      - loops nested correctly (the original only coloured one row), and the
        per-cell loops are replaced by a fast whole-array numpy.interp
      - the colour ramp (the missing MakeColor function) is defined below
      - NODATA cells get a fixed colour and, optionally, transparency
      - output is a proper uint8 array; CRS can be set/overridden explicitly

-----------
HOW TO USE
-----------
    IN SPYDER (recommended)
        1. Edit the CONFIGURATION cell below (INPUT_FILE, OUTPUT_DIR,
           COLOR_RAMP, etc.).
        2. Press F5 to run the whole file, or run cells with Ctrl+Enter
           (cells are marked with "#%%").
        3. The RGB array is left in the console as `rgb` (rows, cols, 3).

    FROM A TERMINAL (venv activated)
        python A_Template_Raster-to-RGB-GeoTIFF_v1.0.py your_file.asc
        python A_Template_Raster-to-RGB-GeoTIFF_v1.0.py your_file.asc /other/output_dir

    If no path is given on the command line, INPUT_FILE is used.

-------------------------------
SETTING UP THE VENV FOR SPYDER
-------------------------------
 <<< bash
     cd ~/spyder-6/envs && source ./ai-apis/bin/activate && 
     pip list &&
     
     python3 -m pip install --upgrade pip &&
     pip install --upgrade rasterio && 
     deactivate

 >>>

    Then in Spyder: Tools > Preferences > Python interpreter >
    "Use the following Python interpreter" > ~/venvs/gis/bin/python,
    and restart the kernel.

------
NOTES
------
    - ASCII grids carry no CRS. If a .prj file sits next to the .asc,
      rasterio picks it up; otherwise set CRS_OVERRIDE (e.g. "EPSG:32618").
      A GeoTIFF written without a CRS still has correct cell positions but
      GIS software won't know what coordinate system they are in.
    - The colour ramp is defined in FRACTIONS of the value range, so it
      stretches automatically to the data. Set VALUE_MIN / VALUE_MAX to fix
      the stretch (useful when colouring several rasters consistently).
    - For categorical rasters (land cover classes etc.) a continuous ramp is
      the wrong tool; use a class->colour lookup instead.
"""

#%% ---------------------------------------------------------------------
# CONFIGURATION  (edit these)
# ------------------------------------------------------------------------
from pathlib import Path

# Raster to read. Used when no path is given on the command line.
INPUT_FILE = Path("/home/bruce-vdb/Desktop/elevation.asc")

# Where the output GeoTIFF is written
OUTPUT_DIR = Path("/home/bruce-vdb/Desktop")

# CRS to assign if the input has none (or to override it). None = keep input's.
# Examples: "EPSG:4326" (lat/lon WGS84), "EPSG:32614" (UTM 14N)
CRS_OVERRIDE = None

# Value range mapped onto the ramp. None = use the min/max of the data.
VALUE_MIN = None
VALUE_MAX = None

# Colour ramp: (fraction of value range, (R, G, B)); fractions run 0.0 -> 1.0
# This default is a simple low-to-high "elevation" style ramp.
COLOR_RAMP = [
    (0.00, (0, 104, 55)),       # dark green  (lowest)
    (0.25, (120, 198, 121)),    # light green
    (0.50, (255, 255, 191)),    # pale yellow
    (0.75, (200, 140, 80)),     # brown
    (1.00, (255, 255, 255)),    # white       (highest)
]

# NODATA cells: colour used, and whether to make them transparent
# (transparent => output gets a 4th alpha band, RGBA)
NODATA_COLOR = (0, 0, 0)
NODATA_TRANSPARENT = True


#%% ---------------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------------------
import sys

import numpy as np

try:
    import rasterio
    from rasterio.crs import CRS
    from rasterio.enums import ColorInterp
except ImportError:
    raise ImportError(
        "rasterio is not installed in the interpreter Spyder is using.\n"
        "Activate your venv and run:  pip install rasterio spyder-kernels\n"
        "then point Spyder at that venv (Tools > Preferences > "
        "Python interpreter) and restart the kernel."
    )


#%% ---------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------
def apply_color_ramp(arr, vmin, vmax, ramp, nodata_color):
    """Map a masked 2-D array to an (rows, cols, 3) uint8 RGB array."""
    stops = np.array([s[0] for s in ramp], dtype=float)
    colors = np.array([s[1] for s in ramp], dtype=float)      # (n_stops, 3)
    if np.any(np.diff(stops) <= 0):
        raise ValueError("COLOR_RAMP fractions must be strictly increasing.")

    data = arr.filled(vmin).astype(float)                      # nodata placeholder
    span = vmax - vmin
    frac = np.zeros_like(data) if span == 0 else np.clip((data - vmin) / span, 0, 1)

    rgb = np.empty(data.shape + (3,), dtype=np.uint8)
    for ch in range(3):
        rgb[..., ch] = np.rint(np.interp(frac, stops, colors[:, ch])).astype(np.uint8)

    # Overwrite NODATA cells with the fixed nodata colour
    rgb[np.ma.getmaskarray(arr)] = nodata_color
    return rgb


def raster_to_rgb_geotiff(in_path, out_dir=OUTPUT_DIR):
    """Colour a single-band raster and write <name>_rgb.tif; return the RGB array."""
    in_path = Path(in_path).expanduser()
    out_dir = Path(out_dir).expanduser()

    if not in_path.is_file():
        raise FileNotFoundError(
            f"Input raster not found: {in_path}\n"
            "Check INPUT_FILE in the CONFIGURATION cell."
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(in_path) as src:
        arr = src.read(1, masked=True)          # NODATA cells are masked
        transform = src.transform
        crs = CRS.from_string(CRS_OVERRIDE) if CRS_OVERRIDE else src.crs

    if crs is None:
        print("WARNING: no CRS found and CRS_OVERRIDE is None - the output "
              "will have no coordinate system.")

    valid = ~np.ma.getmaskarray(arr)
    if not valid.any():
        raise ValueError("Raster contains only NODATA cells; nothing to colour.")

    vmin = float(arr.min()) if VALUE_MIN is None else VALUE_MIN
    vmax = float(arr.max()) if VALUE_MAX is None else VALUE_MAX
    print(f"Colour stretch: {vmin} -> {vmax}")

    rgb = apply_color_ramp(arr, vmin, vmax, COLOR_RAMP, NODATA_COLOR)

    n_bands = 4 if NODATA_TRANSPARENT else 3
    out_path = out_dir / f"{in_path.stem}_rgb.tif"

    with rasterio.open(
        out_path, "w",
        driver="GTiff",
        height=arr.shape[0], width=arr.shape[1],
        count=n_bands, dtype="uint8",
        crs=crs, transform=transform,
        compress="lzw",
    ) as dst:
        for ch in range(3):
            dst.write(rgb[..., ch], ch + 1)
        if NODATA_TRANSPARENT:
            dst.write(np.where(valid, 255, 0).astype(np.uint8), 4)
            dst.colorinterp = [ColorInterp.red, ColorInterp.green,
                               ColorInterp.blue, ColorInterp.alpha]
        else:
            dst.colorinterp = [ColorInterp.red, ColorInterp.green,
                               ColorInterp.blue]

    print(f"Wrote {out_path}")
    return rgb


#%% ---------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------
def _cli_args():
    """Real command-line arguments only (ignores flags the IDE/kernel adds)."""
    return [a for a in sys.argv[1:] if not a.startswith("-")]


if __name__ == "__main__":
    args = _cli_args()
    in_file = args[0] if args else INPUT_FILE
    out_dir = args[1] if len(args) > 1 else OUTPUT_DIR

    rgb = raster_to_rgb_geotiff(in_file, out_dir)   # `rgb` stays in the Spyder console
    print(f"rgb array shape: {rgb.shape}  (rows, cols, R/G/B)")
