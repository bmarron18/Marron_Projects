#!/usr/bin/env python3
"""
make_infographic.py
-------------------
Stand-alone script that draws an infographic explaining how satellite data are
obtained, processed, and evaluated for agricultural and soil-health applications,
and saves it as a JPEG.

Requirements: Python 3.8+, matplotlib (>=3.3), Pillow (for JPEG writing).
Usage:
    python make_infographic.py                    # writes satellite_ag_infographic.jpeg
    python make_infographic.py -o my_file.jpeg    # custom output name
    python make_infographic.py --dpi 300          # higher resolution
"""
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon, Rectangle
import numpy as np

# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #
C_BG      = "#F6F8F4"
C_TITLE   = "#1F3B2C"
C_TEXT    = "#2B2B2B"
C_MUTED   = "#5F6B63"
STAGE_COLORS = ["#2E6F95", "#3C8D5A", "#C98B2B", "#8B4A9C", "#B8433E"]  # 5 stages
C_LINE    = "#9AA69E"


def rounded_box(ax, x, y, w, h, color, alpha=1.0, lw=1.2, ec=None, radius=0.02):
    """Draw a rounded rectangle in axes coordinates (0-1)."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0,rounding_size={radius}",
                         linewidth=lw, edgecolor=ec or color, facecolor=color,
                         alpha=alpha, transform=ax.transAxes, zorder=2)
    ax.add_patch(box)
    return box


def arrow(ax, x0, y0, x1, y1, color=C_LINE, lw=2.2):
    a = FancyArrowPatch((x0, y0), (x1, y1), transform=ax.transAxes,
                        arrowstyle="-|>", mutation_scale=18, lw=lw,
                        color=color, zorder=3)
    ax.add_patch(a)


def text(ax, x, y, s, size=10, color=C_TEXT, weight="normal", ha="left",
         va="top", wrap_width=None, **kw):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=size, color=color,
            fontweight=weight, ha=ha, va=va, zorder=5, **kw)


# --------------------------------------------------------------------------- #
# Small decorative glyphs (drawn with primitives so no image files are needed)
# --------------------------------------------------------------------------- #
def draw_satellite(ax, cx, cy, s=0.03, color="white"):
    # body
    ax.add_patch(Rectangle((cx - s * 0.35, cy - s * 0.35), s * 0.7, s * 0.7,
                           transform=ax.transAxes, color=color, zorder=6))
    # solar panels
    for sign in (-1, 1):
        ax.add_patch(Rectangle((cx + sign * s * 0.45 - (s * 0.5 if sign < 0 else 0),
                                cy - s * 0.18), s * 0.5, s * 0.36,
                               transform=ax.transAxes, color=color, alpha=0.85, zorder=6))
    # signal arcs
    for r, a in ((0.6, 0.9), (0.9, 0.6), (1.2, 0.35)):
        th = np.linspace(-np.pi / 4 - np.pi / 2, np.pi / 4 - np.pi / 2, 30)
        ax.plot(cx + r * s * np.cos(th), cy - s * 0.4 + r * s * np.sin(th) * 0.75,
                transform=ax.transAxes, color=color, alpha=a, lw=1.4, zorder=6)


def draw_grid(ax, cx, cy, s=0.03, color="white"):
    n = 4
    for i in range(n):
        for j in range(n):
            a = 0.35 + 0.65 * ((i + j) % 3) / 2
            ax.add_patch(Rectangle((cx - s / 2 + i * s / n, cy - s / 2 + j * s / n),
                                   s / n * 0.9, s / n * 0.9, transform=ax.transAxes,
                                   color=color, alpha=a, zorder=6))


def draw_curve(ax, cx, cy, s=0.03, color="white"):
    x = np.linspace(0, 1, 50)
    y = np.exp(-((x - 0.55) ** 2) / 0.05)
    ax.plot(cx - s / 2 + x * s, cy - s / 2 + y * s * 0.9, transform=ax.transAxes,
            color=color, lw=2, zorder=6)
    ax.plot([cx - s / 2, cx + s / 2], [cy - s / 2, cy - s / 2], transform=ax.transAxes,
            color=color, lw=1, zorder=6)


def draw_brain(ax, cx, cy, s=0.03, color="white"):
    # simple "network" glyph
    pts = [(-0.4, 0.3), (-0.4, -0.3), (0.0, 0.0), (0.4, 0.35), (0.4, -0.35), (0.0, 0.45)]
    for (x0, y0) in pts:
        ax.add_patch(Circle((cx + x0 * s, cy + y0 * s), s * 0.09, transform=ax.transAxes,
                            color=color, zorder=7))
    for i, (x0, y0) in enumerate(pts):
        for (x1, y1) in pts[i + 1:]:
            ax.plot([cx + x0 * s, cx + x1 * s], [cy + y0 * s, cy + y1 * s],
                    transform=ax.transAxes, color=color, lw=0.9, alpha=0.7, zorder=6)


def draw_check(ax, cx, cy, s=0.03, color="white"):
    ax.add_patch(Circle((cx, cy), s * 0.5, transform=ax.transAxes, fill=False,
                        ec=color, lw=2, zorder=6))
    ax.plot([cx - s * 0.22, cx - s * 0.05, cx + s * 0.25],
            [cy, cy - s * 0.2, cy + s * 0.22], transform=ax.transAxes,
            color=color, lw=2.4, zorder=7)


# --------------------------------------------------------------------------- #
# Main drawing routine
# --------------------------------------------------------------------------- #
def build(output="satellite_ag_infographic.jpeg", dpi=200):
    fig = plt.figure(figsize=(16, 20), facecolor=C_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ------------------------------------------------------------------ Title
    text(ax, 0.5, 0.975, "FROM ORBIT TO FIELD", size=30, color=C_TITLE,
         weight="bold", ha="center")
    text(ax, 0.5, 0.952, "How satellite data are obtained, processed and evaluated "
         "for agriculture and soil health", size=15, color=C_MUTED, ha="center")
    ax.plot([0.06, 0.94], [0.935, 0.935], transform=ax.transAxes, color=C_LINE, lw=1)

    # ------------------------------------------------------------- Stage flow
    stages = [
        ("1  ACQUIRE",
         "Sensors in orbit record energy\nreflected or emitted by the land surface.",
         ["Optical multispectral: Sentinel-2 (10-20 m, 5-day), Landsat 8/9 (30 m, 8-day), MODIS (250 m, daily)",
          "Hyperspectral: EnMAP, PRISMA, EMIT (hundreds of narrow bands)",
          "Radar (SAR): Sentinel-1 C-band; works through cloud, sensitive to moisture & structure",
          "Thermal: Landsat TIRS, ECOSTRESS for crop water stress / ET",
          "Passive microwave: SMAP, SMOS for coarse soil moisture"],
         draw_satellite),
        ("2  PRE-PROCESS",
         "Turn raw digital numbers into physically\nmeaningful, co-registered surface data.",
         ["Radiometric calibration -> top-of-atmosphere radiance / reflectance",
          "Atmospheric correction (Sen2Cor, LaSRC, 6S) -> surface reflectance (Level-2A)",
          "Cloud, shadow and snow masking (s2cloudless, Fmask, SCL)",
          "Orthorectification and co-registration to a map grid; harmonisation across sensors (e.g., HLS)",
          "Temporal compositing, gap-filling and smoothing of time series"],
         draw_grid),
        ("3  DERIVE FEATURES",
         "Compress spectra into indices and\nbiophysical variables that track crops and soil.",
         ["Vegetation indices: NDVI, EVI, NDRE, SAVI, GNDVI; red-edge chlorophyll / nitrogen proxies",
          "Biophysical retrieval: LAI, fAPAR, canopy chlorophyll via PROSAIL inversion or ML",
          "Bare-soil composites (multi-year, NDVI < ~0.25) expose topsoil spectra for SOC, clay, CaCO3, pH, CEC",
          "Soil & water indices: NDWI, NDMI, brightness, SWIR ratios; SAR backscatter and coherence",
          "Phenology metrics: green-up, peak, senescence dates, integrated NDVI"],
         draw_curve),
        ("4  MODEL",
         "Link features to ground truth with\nstatistical, ML or process-based models.",
         ["Crop type & cropland mapping: random forest, gradient boosting, CNN / transformer on time series",
          "Yield & biomass: regression, LightGBM, LSTM, crop-model data assimilation (WOFOST, DSSAT, APSIM)",
          "Soil properties: PLSR / Cubist / RF on bare-soil spectra + terrain, climate & parent-material covariates",
          "Microbial proxies (emerging): NDVI/hyperspectral linked to eDNA & PLFA fungal:bacterial data via GPR / RF",
          "Digital soil mapping at scale: SoilGrids (250 m) from ~240k profiles and 400+ covariates"],
         draw_brain),
        ("5  EVALUATE & DELIVER",
         "Quantify accuracy and uncertainty,\nthen translate maps into decisions.",
         ["Spatial / blocked cross-validation; independent hold-out fields",
          "Regression metrics: R2, RMSE, bias, RPD / RPIQ, prediction intervals (e.g., 5-95% quantiles)",
          "Classification metrics: overall accuracy, F1, kappa, confusion matrix; area estimation with design-based sampling",
          "Transferability checks across years, regions and sensors; sensitivity to cloud gaps",
          "Outputs: variable-rate prescription maps, yield forecasts, SOC baselines & MRV, drought early warning"],
         draw_check),
    ]

    top = 0.905
    box_h = 0.138
    gap = 0.016
    x_left, w = 0.06, 0.88
    for i, (title, tagline, bullets, glyph) in enumerate(stages):
        y = top - i * (box_h + gap) - box_h
        col = STAGE_COLORS[i]
        # left colour band
        rounded_box(ax, x_left, y, 0.20, box_h, col, radius=0.012)
        # right content pane
        rounded_box(ax, x_left + 0.20, y, w - 0.20, box_h, "white", ec=col, lw=1.6, radius=0.012)
        glyph(ax, x_left + 0.10, y + box_h - 0.035, s=0.035)
        text(ax, x_left + 0.10, y + box_h - 0.066, title, size=16, color="white",
             weight="bold", ha="center")
        text(ax, x_left + 0.10, y + box_h - 0.088, tagline, size=9.5, color="white",
             ha="center", linespacing=1.35)
        # bullets
        by = y + box_h - 0.016
        for b in bullets:
            text(ax, x_left + 0.215, by, "\u25B8 " + b, size=10.3, color=C_TEXT)
            by -= 0.0235
        # connector arrow
        if i < len(stages) - 1:
            arrow(ax, x_left + 0.10, y - 0.001, x_left + 0.10, y - gap + 0.001, color=col)

    # ------------------------------------------------------ Bottom panels
    yb = 0.03
    hb = 0.105
    panel_w = (w - 0.03) / 3
    panels = [
        ("WHAT CAN BE SEEN FROM SPACE",
         ["Crop type, extent and field boundaries",
          "Canopy greenness, LAI, chlorophyll, N status",
          "Phenology, growth anomalies, lodging, flooding",
          "Crop water stress (thermal) and ET",
          "Soil moisture (SAR / passive microwave)",
          "Topsoil SOC, clay, CaCO3, pH & CEC on bare soil",
          "Tillage, residue cover, cover-crop adoption"]),
        ("KEY LIMITS & CAVEATS",
         ["Optical sensors are blind under cloud; SAR fills gaps",
          "Soil signal only from exposed, dry, smooth bare soil",
          "Satellite SOC/pH/CEC models: typically R2 ~0.4-0.7; RPD >1.4 = fair",
          "Microbial biomass / F:B ratio is NOT directly observed - only inferred",
          "Spatial resolution vs field size; mixed pixels",
          "Models rarely transfer across regions without recalibration",
          "Ground truth remains essential"]),
        ("OPEN DATA & TOOLS",
         ["Copernicus Data Space (Sentinel-1/2/3)",
          "USGS EarthExplorer / NASA Earthdata (Landsat, MODIS, HLS, SMAP)",
          "Google Earth Engine; Microsoft Planetary Computer",
          "SoilGrids (ISRIC); LUCAS topsoil (ESDAC); SSURGO (USA)",
          "USDA NASS Cropland Data Layer; ESA WorldCereal",
          "FAO WaPOR, GEOGLAM Crop Monitor",
          "Open software: SNAP, QGIS, GDAL, rasterio, scikit-learn"]),
    ]
    for j, (ptitle, items) in enumerate(panels):
        px = x_left + j * (panel_w + 0.015)
        rounded_box(ax, px, yb, panel_w, hb, "white", ec=C_LINE, lw=1.2, radius=0.01)
        rounded_box(ax, px, yb + hb - 0.022, panel_w, 0.022, C_TITLE, radius=0.01)
        text(ax, px + panel_w / 2, yb + hb - 0.004, ptitle, size=10.5, color="white",
             weight="bold", ha="center")
        iy = yb + hb - 0.030
        for it in items:
            text(ax, px + 0.008, iy, "\u2022 " + it, size=8.6, color=C_TEXT)
            iy -= 0.0115

    # ------------------------------------------------------------- Footer
    text(ax, 0.06, 0.012,
         "Sources: Weiss, Jacob & Duveiller (2020) Remote Sens. Environ. 236:111402; "
         "Angelopoulou et al. (2019) Remote Sens. 11:676; Lima et al. (2025) Remote Sens. 17:882; "
         "Poggio et al. (2021) SOIL 7:217;\n"
         "Gorelick et al. (2017) Remote Sens. Environ. 202:18; "
         "Cardille et al. (eds., 2024) Cloud-Based Remote Sensing with Google Earth Engine (open access, Springer).",
         size=7.5, color=C_MUTED, va="bottom", linespacing=1.4)

    fig.savefig(output, dpi=dpi, format="jpeg", facecolor=C_BG,
                pil_kwargs={"quality": 92, "optimize": True})
    plt.close(fig)
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate the satellite-agriculture infographic (JPEG).")
    p.add_argument("-o", "--output", default="satellite_ag_infographic.jpeg")
    p.add_argument("--dpi", type=int, default=200)
    args = p.parse_args()
    out = build(args.output, args.dpi)
    print(f"Wrote {out}")
