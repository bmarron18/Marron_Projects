#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created : 10 Nov 2026
Revised:  
Authors : bruce-vdb, claude

-------------------------------------------------
A_Template_ExtractData_Single-asc-File_data_v1.0.py
-------------------------------------------------
    Reads an ESRI ASCII grid (.asc) -- or any raster format GDAL supports --
    using rasterio, and produces:

      1. <name>_xyz.csv      one row per valid cell: x, y, value
                             (x/y are cell CENTRES in the raster's own CRS)
      2. <name>_summary.txt  size, CRS, cell size, extent, nodata value,
                             and basic statistics of the valid cells

    It is the open-source replacement for the old ArcPy + NumPy snippet:
    no ArcGIS licence needed.

--------------
HOW TO USE
-----------------
    From a terminal:
       * A_Template_ExtractData_Single-asc-File_data_v1.0.py path/to/your_file.asc
       * A_Template_ExtractData_Single-asc-File_data_v1.0.py path/to/your_file.asc /some/other/output_dir

    Or from another script / IPython:
        from ascii_grid_to_xyz import grid_to_xyz
        grid_to_xyz("path/to/your_file.asc")

    Outputs go to OUTPUT_DIR (below) unless you pass a second argument.

----------------
REQUIREMENTS
-----------------
    Python 3, numpy, rasterio     (pip install rasterio)

NOTES
    - ASCII grids MUST have the usual header (ncols, nrows, xllcorner,
      yllcorner, cellsize, NODATA_value). Cells equal to NODATA_value are
      skipped in the CSV.
    - ASCII grids carry no CRS. If you have a .prj file next to the .asc,
      rasterio will pick it up; otherwise the CRS is reported as None.
    - Large rasters produce very large CSVs (one line per cell). For big
      grids, work on the array directly instead of writing a CSV.
"""

import sys
from pathlib import Path

import numpy as np
import rasterio

# Default destination for outputs (change as needed)
OUTPUT_DIR = Path("/home/bruce-vdb/Desktop")


def grid_to_xyz(in_path, out_dir=OUTPUT_DIR):
    in_path = Path(in_path)
    out_dir = Path(out_dir)
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: A_Template_ExtractData_Single-asc-File_data_v1.0.py input.asc [output_dir]")
    grid_to_xyz(*sys.argv[1:3])
