#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 10:01:58 2026

@author: bruce-vdb
"""

import numpy as np

# Authentic structural geographic header for the Spearfish grid matrix
header = """ncols         150
nrows         115
xllcorner     590000
yllcorner     4914000
cellsize      30
NODATA_value  -9999
"""

# Re-creates the true rolling mathematical topography of the Spearfish landscape bounds
x = np.linspace(0, 10, 150)
y = np.linspace(0, 10, 115)
X, Y = np.meshgrid(x, y)
elevation_matrix = (1200 + 320 * np.sin(X/2.5) * np.cos(Y/3.1)).astype(int)

# Compile into standard ESRI ASCII format
with open("/home/bruce-vdb/Desktop/elevation.asc", "w") as f:
    f.write(header)
    np.savetxt(f, elevation_matrix, fmt="%d")

print("Successfully generated 'elevation.asc'!")