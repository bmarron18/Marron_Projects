#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 10 Nov 2026
Revised : 10 Nov 2026 (v1.1 - Spyder / venv friendly)
Authors : bruce-vdb, claude

---------------------------------------------------
A_Template_ExtractData_Single-asc-File_data_v1.1.py
---------------------------------------------------
    Reads an ESRI ASCII grid (.asc) -- or any raster format GDAL supports --
    using rasterio, and produces:

      1. <name>_xyz.csv      one row per valid cell: x, y, value
                             (x/y are cell CENTRES in the raster's own CRS)
      2. <name>_summary.txt  size, CRS, cell size, extent, nodata value,
                             and basic statistics of the valid cells

    It is the open-source replacement for the old ArcPy + NumPy snippet:
    no ArcGIS licence needed.

-----------
HOW TO USE
-----------
    IN SPYDER (recommended)
        1. Edit INPUT_FILE (and, if you like, OUTPUT_DIR) in the
           CONFIGURATION cell below.
        2. Press F5 to run the whole file, or run the cells one at a time
           with Ctrl+Enter (cells are marked with "#%%").
        3. The result array is left in the console as `xyz`, so you can
           inspect it in the Variable Explorer.

    FROM A TERMINAL (venv activated)
        python A_Template_ExtractData_Single-asc-File_data_v1.1.py your_file.asc
        python A_Template_ExtractData_Single-asc-File_data_v1.1.py your_file.asc /other/output_dir

    FROM ANOTHER SCRIPT
        import importlib
        mod = importlib.import_module("A_Template_ExtractData_Single-asc-File_data_v1.1")
        xyz = mod.grid_to_xyz("path/to/your_file.asc")

    If no path is given on the command line, INPUT_FILE is used.

-------------------------------
SETTING UP THE VENV FOR SPYDER
-------------------------------
    Spyder runs your code in a separate "kernel" using whichever Python
    interpreter you point it at, so the venv needs a few packages:

        # create + activate (Linux/macOS)
        python3 -m venv ~/venvs/gis
        source ~/venvs/gis/bin/activate

        pip install numpy rasterio spyder-kernels

    Then in Spyder:
        Tools > Preferences > Python interpreter
            > "Use the following Python interpreter"
            > ~/venvs/gis/bin/python
        Restart the console (Consoles > Restart kernel).

    Spyder is picky about the spyder-kernels version; if it complains,
    the Preferences page tells you which version to install:
        pip install "spyder-kernels==<version it asks for>"

------
NOTES
------
    - ASCII grids MUST have the usual header (ncols, nrows, xllcorner,
      yllcorner, cellsize, NODATA_value). Cells equal to NODATA_value are
      skipped in the CSV.
    - ASCII grids carry no CRS. If you have a .prj file next to the .asc,
      rasterio will pick it up; otherwise the CRS is reported as None.
    - Large rasters produce very large CSVs (one line per cell). For big
      grids, work on the array directly instead of writing a CSV.
"""

#%% ---------------------------------------------------------------------
# CONFIGURATION  (edit these)
# ------------------------------------------------------------------------
from pathlib import Path

# Raster to read. Used when no path is given on the command line.
INPUT_FILE = Path("/home/bruce-vdb/Desktop/elevation.asc")

# Where the outputs are written
OUTPUT_DIR = Path("/home/bruce-vdb/Desktop")


#%% ---------------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------------------
import sys

import numpy as np

try:
    import rasterio
except ImportError:
    raise ImportError(
        "rasterio is not installed in the interpreter Spyder is using.\n"
        "Activate your venv and run:  pip install rasterio spyder-kernels\n"
        "then point Spyder at that venv (Tools > Preferences > "
        "Python interpreter) and restart the kernel."
    )


#%% ---------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------
def grid_to_xyz(in_path, out_dir=OUTPUT_DIR):
    """Write <name>_xyz.csv and <name>_summary.txt; return the xyz array."""
    in_path = Path(in_path).expanduser()
    out_dir = Path(out_dir).expanduser()

    if not in_path.is_file():
        raise FileNotFoundError(
            f"Input raster not found: {in_path}\n"
            "Check INPUT_FILE in the CONFIGURATION cell."
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(in_path) as src:
        # masked=True hides NODATA cells so they don't pollute stats/output
        arr = src.read(1, masked=True)
        transform = src.transform
        info = {
            "file": str(in_path),
            "driver": src.driver,
            "columns": src.width,
            "rows": src.height,
            "bands": src.count,
            "crs": src.crs,
            "cell size (x, y)": (transform.a, abs(transform.e)),
            "bounds (left, bottom, right, top)": tuple(src.bounds),
            "nodata": src.nodata,
        }

    # Cell-centre coordinates: the affine transform maps (col, row) -> (x, y).
    # Adding 0.5 moves from the cell's top-left corner to its centre.
    rows, cols = np.indices(arr.shape)
    xs, ys = transform * (cols + 0.5, rows + 0.5)

    # Keep only valid (non-nodata) cells
    valid = ~np.ma.getmaskarray(arr)
    xyz = np.column_stack((xs[valid], ys[valid], arr.data[valid]))

    stem = in_path.stem
    csv_path = out_dir / f"{stem}_xyz.csv"
    np.savetxt(csv_path, xyz, delimiter=",", header="x,y,value",
               comments="", fmt="%.6f")

    summary_path = out_dir / f"{stem}_summary.txt"
    with open(summary_path, "w") as f:
        for k, v in info.items():
            f.write(f"{k}: {v}\n")
        f.write(f"valid cells: {valid.sum()} of {arr.size}\n")
        if valid.any():
            f.write(f"min: {arr.min()}\nmax: {arr.max()}\n"
                    f"mean: {arr.mean():.4f}\n")

    print(f"Wrote {csv_path}")
    print(f"Wrote {summary_path}")
    return xyz


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

    xyz = grid_to_xyz(in_file, out_dir)   # `xyz` stays in the Spyder console
    print(f"xyz array shape: {xyz.shape}  (columns: x, y, value)")
