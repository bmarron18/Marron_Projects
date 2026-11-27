#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Region NDVI from area-weighted mean NIR and Red, with a fractal-growth exponent.

Input : <prefix>_B8B4_stats.csv  (columns: x, y, B8_<stat>, B4_<stat>, ...)
Steps : 1) keep pixels with NDVI > NDVI_MIN
        2) weighted mean NIR (B8) and weighted mean Red (B4), separately
        3) region NDVI = (NIR_bar - Red_bar) / (NIR_bar + Red_bar)
        4) find the bin the region NDVI falls in -> exponent
        5) report region NDVI and region NDVI ** exponent

Usage : python3 region_ndvi_fractal.py [path/to/B8B4_stats.csv]
"""
import sys

import numpy as np
import pandas as pd

# ---------------- User settings ----------------
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "UMA_S2_2022_04_B8B4_stats.csv"
STATS_TO_RUN = ["min", "max", "mean"]   # which band statistics to process
NDVI_MIN = 0.25                         # accept only NDVI > this value
AREA_COL = None                         # per-pixel area column (m2), if you have one
PIXEL_SIZE = 10.0                       # m; Sentinel-2 10 m pixels (used if AREA_COL is None)

# (lower inclusive, upper exclusive, exponent); the last bin also includes its upper edge
BINS = [(0.2, 0.4, 2.0),
        (0.4, 0.6, 2.5),
        (0.6, 1.0, 3.0)]


def find_bin(v):
    """Return ((lo, hi), exponent) for the bin containing v, or (None, None)."""
    for i, (lo, hi, exp) in enumerate(BINS):
        is_last = i == len(BINS) - 1
        if lo <= v < hi or (is_last and v == hi):
            return (lo, hi), exp
    return None, None


def region_ndvi(df, stat):
    nir_col, red_col = f"B8_{stat}", f"B4_{stat}"
    for c in (nir_col, red_col):
        if c not in df.columns:
            raise ValueError(f"Column {c!r} not found. Columns: {list(df.columns)}")

    d = df.dropna(subset=[nir_col, red_col]).copy()
    n_all = len(d)

    # 1) pixel NDVI from this statistic's own bands; keep NDVI > NDVI_MIN
    den = d[nir_col] + d[red_col]
    d = d[den > 0]
    d["ndvi_px"] = (d[nir_col] - d[red_col]) / (d[nir_col] + d[red_col])
    d = d[d["ndvi_px"] > NDVI_MIN]
    if d.empty:
        return None

    # 2) area weights that sum to 1
    area = d[AREA_COL].to_numpy(float) if AREA_COL else np.full(len(d), PIXEL_SIZE ** 2)
    w = area / area.sum()

    # 3) weighted mean bands first, then NDVI once from the aggregated bands
    nir_bar = float(np.sum(w * d[nir_col].to_numpy(float)))
    red_bar = float(np.sum(w * d[red_col].to_numpy(float)))
    ndvi_reg = (nir_bar - red_bar) / (nir_bar + red_bar)

    # 4) bin and exponent
    bin_range, exponent = find_bin(ndvi_reg)

    return dict(stat=stat, n_all=n_all, n_used=len(d), nir_bar=nir_bar, red_bar=red_bar,
                ndvi_reg=ndvi_reg, bin_range=bin_range, exponent=exponent)


def main():
    df = pd.read_csv(CSV_PATH)
    print(f"File: {CSV_PATH}  ({len(df)} rows)\n")

    for stat in STATS_TO_RUN:
        r = region_ndvi(df, stat)
        print(f"=== B8_{stat} / B4_{stat} ===")
        if r is None:
            print(f"No pixels with NDVI > {NDVI_MIN}.\n")
            continue
        print(f"Pixels used (NDVI > {NDVI_MIN}): {r['n_used']} of {r['n_all']}")
        print(f"Weighted mean NIR : {r['nir_bar']:.5f}")
        print(f"Weighted mean Red : {r['red_bar']:.5f}")
        print(f"Region NDVI       : {r['ndvi_reg']:.5f}")
        if r["exponent"] is None:
            print("Region NDVI is outside the defined bins (0.2-1.0); no exponent applied.\n")
        else:
            lo, hi = r["bin_range"]
            print(f"Bin               : {lo} to {hi}  ->  exponent {r['exponent']}")
            print(f"Region NDVI^{r['exponent']}   : {r['ndvi_reg'] ** r['exponent']:.5f}\n")


if __name__ == "__main__":
    main()
