#!/usr/bin/env python3
"""Builds the four PDF deliverables with reportlab."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, ListFlowable, ListItem, Image)
from reportlab.lib.enums import TA_JUSTIFY

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=20, leading=24, spaceAfter=6, textColor=colors.HexColor("#1F3B2C"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13.5, leading=17, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#2E6F95"))
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=11.5, leading=14, spaceBefore=6, spaceAfter=2, textColor=colors.HexColor("#3C8D5A"))
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=13.5, alignment=TA_JUSTIFY, spaceAfter=5)
SM = ParagraphStyle("SM", parent=B, fontSize=8.5, leading=11, textColor=colors.HexColor("#5F6B63"))
SUB = ParagraphStyle("SUB", parent=B, fontSize=10.5, leading=14, textColor=colors.HexColor("#5F6B63"), alignment=0)
REF = ParagraphStyle("REF", parent=B, fontSize=9.2, leading=12, alignment=0, leftIndent=14, firstLineIndent=-14, spaceAfter=4)
CELL = ParagraphStyle("CELL", parent=B, fontSize=8.6, leading=10.8, alignment=0, spaceAfter=0)
CELLH = ParagraphStyle("CELLH", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)


def P(t, st=B):
    return Paragraph(t, st)


def bullets(items, st=B):
    return ListFlowable([ListItem(P(i, st), leftIndent=12) for i in items],
                        bulletType="bullet", start="\u2022", leftIndent=12, bulletFontSize=8)


def table(data, widths, header=True):
    rows = [[Paragraph(c, CELLH if (header and r == 0) else CELL) for c in row] for r, row in enumerate(data)]
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA69E")),
             ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E6F95"))]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F1F4F0")))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5F6B63"))
    canvas.drawString(0.8 * inch, 0.5 * inch, doc.title)
    canvas.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_doc(path, title):
    d = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                          topMargin=0.8 * inch, bottomMargin=0.8 * inch, title=title, author="Prepared with verified literature sources")
    return d


DATE = "October 2026"

# =========================================================================== #
# 1. HIGH-LEVEL SUMMARY
# =========================================================================== #
def build_summary(path):
    doc = make_doc(path, "Satellite Data in Agriculture - High-Level Summary")
    s = []
    s.append(P("Satellite Data in Agriculture: A High-Level Summary", H1))
    s.append(P(f"Current uses, soil-health inference, and what the evidence supports &nbsp;|&nbsp; {DATE}", SUB))
    s.append(Spacer(1, 8))

    s.append(P("1. Why satellites matter for agriculture", H2))
    s.append(P("Agriculture must deliver food, fibre and fuel for a growing population while adapting to climate change and "
               "protecting soil, water and biodiversity. Earth-observation (EO) satellites help because they provide "
               "repeated, spatially complete, objective measurements of the land surface at scales from individual fields "
               "to continents. The canonical meta-review of the field (Weiss, Jacob &amp; Duveiller, 2020, <i>Remote Sensing of "
               "Environment</i>) frames the value of remote sensing as supplying repetitive information on crop status throughout "
               "the season, at different scales, for different actors - from breeders and farmers to insurers, governments and "
               "food-security agencies."))
    s.append(P("Three developments over the past decade turned EO from a research tool into operational infrastructure: "
               "(i) free and open data policies (Landsat since 2008; the Copernicus Sentinels since 2014-15), "
               "(ii) sensors with field-relevant resolution and frequent revisit (Sentinel-2's 10-20 m pixels, red-edge "
               "bands and ~5-day revisit), and (iii) cloud platforms such as Google Earth Engine and the Copernicus Data Space "
               "Ecosystem that remove the need to download and store petabytes of imagery."))

    s.append(P("2. What satellites are used for today", H2))
    s.append(table([
        ["Application area", "What is measured / inferred", "Typical data and methods", "Maturity"],
        ["Cropland and crop-type mapping", "Where crops grow, which crop, field boundaries, cropping intensity",
         "Sentinel-2 / Landsat / Sentinel-1 time series; random forest, gradient boosting, deep learning; e.g. USDA Cropland Data Layer, ESA WorldCereal", "Operational"],
        ["Crop condition and phenology", "Greenness (NDVI/EVI), leaf area index, chlorophyll and nitrogen status, emergence, peak, senescence",
         "Vegetation indices and red-edge indices; PROSAIL radiative-transfer inversion; time-series smoothing", "Operational"],
        ["Yield estimation and forecasting", "Field to national yield, biomass, anomalies vs. previous seasons",
         "Index regression, ML/DL on image time series, assimilation into crop models (WOFOST, DSSAT, APSIM) with weather and soil data", "Operational at regional scale; field scale maturing"],
        ["Precision / site-specific management", "Within-field variability for variable-rate N, seeding, irrigation, management zones",
         "High-resolution optical (Sentinel-2, PlanetScope), NDRE / chlorophyll indices, zoning algorithms", "Commercial products widespread"],
        ["Water and drought", "Soil moisture, evapotranspiration (ET), crop water stress, irrigation extent",
         "SMAP / SMOS passive microwave, Sentinel-1 SAR, Landsat / ECOSTRESS thermal, energy-balance ET models (e.g. FAO WaPOR)", "Operational"],
        ["Soil properties", "Topsoil organic carbon, clay, carbonates, pH, cation exchange capacity, bulk density proxies",
         "Bare-soil composites from Sentinel-2 / Landsat; PLSR, Cubist, random forest, deep learning calibrated on soil samples (LUCAS, national surveys); digital soil mapping with hundreds of covariates (SoilGrids)", "Research to early operational; moderate accuracy"],
        ["Soil biology (emerging)", "Microbial biomass, bacterial and fungal diversity, fungal:bacterial balance",
         "Statistical links between NDVI / hyperspectral imagery and eDNA or PLFA ground data; Gaussian-process and random-forest models", "Exploratory; indirect inference only"],
        ["Policy, insurance and compliance", "CAP subsidy checks, cover-crop and tillage practice detection, disaster assessment, carbon MRV",
         "Sentinel-1/2 time series, change detection, practice classifiers", "Operational in EU; growing elsewhere"],
    ], [1.35 * inch, 1.9 * inch, 2.45 * inch, 1.1 * inch]))
    s.append(Spacer(1, 6))

    s.append(P("3. Soil fertility and soil health from orbit: what is - and is not - possible", H2))
    s.append(P("<b>Directly sensed chemistry.</b> Soil organic carbon (SOC), iron oxides, carbonates and clay minerals have "
               "characteristic absorption features in the visible, near-infrared and shortwave-infrared (400-2500 nm). "
               "When soil is bare, dry and relatively smooth, multispectral (Sentinel-2, Landsat) or hyperspectral "
               "(EnMAP, PRISMA, EMIT) reflectance can be regressed against laboratory values. Reviews of the SOC literature "
               "(Angelopoulou et al., 2019; Lima et al., 2025) report that Sentinel-2 and Landsat 8 are now the dominant data "
               "sources, that vegetation and topographic indices are among the most influential predictors, and that the spatial "
               "spread of calibration samples matters more than their total number. Published satellite SOC models typically "
               "reach cross-validated R<sup>2</sup> of about 0.4-0.7; PLSR models from Sentinel-2 bare-soil spectra achieve "
               "intermediate skill (R<sup>2</sup> &ge; 0.5, RPD &ge; 1.4) for SOC, pH, CaCO<sub>3</sub> and CEC in favourable "
               "European settings."))
    s.append(P("<b>Indirectly mapped properties.</b> pH, total nitrogen and CEC have weak or no direct spectral signature; they are "
               "predicted because they co-vary with SOC, clay, carbonates, climate, terrain and parent material. This is the logic of "
               "digital soil mapping: SoilGrids 2.0 (Poggio et al., 2021) uses machine learning on ~240,000 soil profiles and 400+ "
               "environmental covariates (many satellite-derived) to map SOC, total N, pH, CEC, bulk density and texture at 250 m "
               "globally, with spatially explicit 5th-95th percentile uncertainty."))
    s.append(P("<b>Soil biology.</b> Microbial biomass and the fungal:bacterial (F:B) ratio cannot be observed from space. "
               "Recent work shows that satellite data can be <i>statistically associated</i> with soil biology: hyperspectral "
               "imagery from DESIS explained up to about half of the variance in forest soil bacterial alpha diversity and ~40% for "
               "fungi when paired with eDNA data; and Sentinel-2 NDVI, after adjusting for soil and climate confounders, has been "
               "linked to the abundance of beneficial versus pathogenic fungal genera in European cereal fields. These results are "
               "promising but exploratory, and F:B ratios still require field measurement (PLFA, qPCR, microscopy-based kits)."))

    s.append(P("4. How the data get from orbit to a decision", H2))
    s.append(bullets([
        "<b>Acquire:</b> optical multispectral, hyperspectral, thermal, radar (SAR) and passive-microwave sensors each capture a different physical property of crops and soil.",
        "<b>Pre-process:</b> calibration, atmospheric correction to surface reflectance, cloud masking, geometric alignment and temporal compositing produce analysis-ready data.",
        "<b>Derive features:</b> vegetation and soil indices, biophysical variables, phenology metrics and bare-soil composites.",
        "<b>Model:</b> statistical, machine-learning or process-based models link features to ground truth (yields, crop labels, soil analyses).",
        "<b>Evaluate and deliver:</b> spatial cross-validation, independent test sets, uncertainty quantification, and translation into maps, forecasts and prescriptions.",
    ]))

    s.append(P("5. Key take-aways for practitioners", H2))
    s.append(bullets([
        "Satellite data excel at <b>spatial coverage, revisit frequency and consistency</b>; they complement rather than replace ground sampling.",
        "Sentinel-2 plus Sentinel-1 (free, 10-20 m, 5-6 day revisit) is the default starting point for most agricultural work; Landsat gives the long archive; MODIS gives daily regional context.",
        "For <b>soil properties</b>, expect moderate accuracy, strong dependence on bare-soil availability and local calibration, and much better results for SOC/clay/carbonates than for pH, N or CEC.",
        "For <b>soil biology</b>, satellite products are indicators of habitat and plant response, not measurements of microbial communities.",
        "Always report validation metrics and uncertainty, and check whether a model transfers across years, regions and sensors before operational use.",
    ]))
    s.append(Spacer(1, 10))
    s.append(P("Key sources: Weiss, Jacob &amp; Duveiller (2020) Remote Sens. Environ. 236:111402 - Angelopoulou et al. (2019) Remote Sens. 11:676 - "
               "Lima et al. (2025) Remote Sens. 17:882 - Poggio et al. (2021) SOIL 7:217-240 - Gorelick et al. (2017) Remote Sens. Environ. 202:18-27 - "
               "Segarra et al. (2020) Agronomy 10:641 - Cardille et al. (eds., 2024) Cloud-Based Remote Sensing with Google Earth Engine (Springer, open access). "
               "Full reference list with DOIs is provided in the companion document <i>Foundational and Canonical References</i>.", SM))
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


# =========================================================================== #
# 2. DETAILED ACCOUNT
# =========================================================================== #
def build_detailed(path, infographic):
    doc = make_doc(path, "Satellite Data for Agriculture - Acquisition, Processing and Evaluation")
    s = []
    s.append(P("Satellite Data for Agricultural and Soil-Health Evaluation", H1))
    s.append(P(f"A detailed account of how data are obtained, processed, modelled and evaluated &nbsp;|&nbsp; {DATE}", SUB))
    s.append(Spacer(1, 6))

    # ---- Part A
    s.append(P("Part A. Physical basis: what a satellite actually measures", H2))
    s.append(P("A satellite sensor records electromagnetic energy leaving the Earth's surface. For agriculture the useful regions are: "
               "<b>visible (400-700 nm)</b>, where chlorophyll absorbs strongly in blue and red; the <b>red edge (680-750 nm)</b>, where "
               "reflectance rises steeply and whose position shifts with chlorophyll content and nitrogen status; the "
               "<b>near-infrared (750-1300 nm)</b>, where healthy leaf mesophyll scatters strongly so that canopy reflectance "
               "increases with leaf area; the <b>shortwave infrared (1300-2500 nm)</b>, dominated by water absorption in vegetation "
               "and by clay-mineral (~2200 nm), carbonate (~2340 nm) and organic-matter features in soils; the <b>thermal infrared "
               "(8-14 &micro;m)</b>, which gives land-surface temperature and hence evaporative cooling and crop water stress; and the "
               "<b>microwave (1-30 cm)</b>, where active radar backscatter depends on surface roughness, canopy structure and dielectric "
               "constant (i.e. water content), and passive radiometers sense near-surface soil moisture."))
    s.append(P("Soil reflectance in the 400-2500 nm range decreases overall as organic carbon increases (soils darken), shows "
               "iron-oxide features near 500-900 nm, hydroxyl/clay features near 1400, 1900 and 2200 nm, and carbonate features near "
               "2340 nm. These are the physical hooks that allow SOC, clay, CaCO<sub>3</sub> and iron to be estimated from spectra. "
               "pH, CEC, total N and microbial properties lack distinct features and are predicted through covariance with the "
               "directly sensed constituents and with landscape covariates."))

    s.append(P("Part B. Obtaining the data", H2))
    s.append(P("B.1 Sensor families and representative missions", H3))
    s.append(table([
        ["Sensor family", "Representative missions (free data)", "Spatial / temporal resolution", "Agricultural use"],
        ["Optical multispectral", "Sentinel-2A/B/C (ESA); Landsat 8/9 (USGS/NASA); MODIS Terra/Aqua, VIIRS (NASA/NOAA)",
         "S2: 10/20/60 m, ~5 d; Landsat: 30 m (15 m pan, 100 m thermal), 8 d combined; MODIS: 250-1000 m, daily",
         "Vegetation indices, LAI/fAPAR, crop type, phenology, bare-soil spectra"],
        ["Hyperspectral (imaging spectroscopy)", "EnMAP (DLR), PRISMA (ASI), EMIT (NASA, on ISS), DESIS (DLR, on ISS)",
         "30 m, 200+ bands; tasking-based or limited coverage",
         "Soil mineralogy and SOC, pigment and nitrogen retrieval, species / trait mapping"],
        ["Synthetic aperture radar (SAR)", "Sentinel-1A/C (C-band, ESA); NISAR (L/S-band, NASA-ISRO); ALOS-2 (L-band, JAXA)",
         "5-20 m, 6-12 d; cloud-independent, day and night",
         "Crop structure and type, flooding, soil moisture, tillage, phenology under persistent cloud"],
        ["Thermal infrared", "Landsat TIRS; ECOSTRESS (ISS); MODIS/VIIRS; Sentinel-3 SLSTR",
         "70-1000 m",
         "Land-surface temperature, evapotranspiration, water-stress indices"],
        ["Passive microwave", "SMAP (NASA); SMOS (ESA); AMSR2 (JAXA)",
         "9-40 km, 1-3 d",
         "Regional surface soil moisture, drought monitoring, crop-model forcing"],
        ["Commercial very-high-resolution", "PlanetScope (3 m, daily); SkySat; WorldView; Pleiades",
         "0.3-3 m, daily to on-demand",
         "Small-holder fields, within-field zoning, emergence counts (not free; some research programmes provide access)"],
    ], [1.25 * inch, 2.0 * inch, 1.75 * inch, 1.8 * inch]))
    s.append(Spacer(1, 6))
    s.append(P("B.2 Processing levels and what to download", H3))
    s.append(P("Agencies distribute data at standard levels. <b>Level-1</b> products are radiometrically calibrated and "
               "geo-located top-of-atmosphere (TOA) radiance or reflectance (e.g. Sentinel-2 L1C, Landsat L1TP). <b>Level-2</b> "
               "products have been atmospherically corrected to <i>surface reflectance</i> and include per-pixel quality masks "
               "(e.g. Sentinel-2 L2A with its Scene Classification Layer, Landsat Collection 2 Level-2 with the QA_PIXEL band, "
               "Sentinel-1 GRD after terrain correction). <b>Level-3/4</b> products are gridded, composited or modelled variables "
               "(MODIS 16-day NDVI, Copernicus Global Land LAI/fAPAR, SMAP soil moisture, HLS). For most agricultural analysis one "
               "starts from Level-2 surface reflectance; analysis-ready data (ARD) collections on cloud platforms remove most of the "
               "remaining preparation burden."))
    s.append(P("B.3 Access routes", H3))
    s.append(bullets([
        "<b>Agency portals</b> (Copernicus Data Space Ecosystem, USGS EarthExplorer, NASA Earthdata) for scene download and APIs (STAC, OData, openEO).",
        "<b>Cloud platforms</b> that co-locate data and compute: Google Earth Engine (multi-petabyte catalogue, JavaScript/Python API; Gorelick et al., 2017), Microsoft Planetary Computer, AWS Open Data registry, Copernicus Data Space JupyterHub / Sentinel Hub.",
        "<b>Thematic services</b> that deliver finished variables: Copernicus Land Monitoring Service, FAO WaPOR, GEOGLAM Crop Monitor, USDA NASS CropScape.",
    ]))

    # ---- Part C
    s.append(P("Part C. Pre-processing to analysis-ready data", H2))
    s.append(P("C.1 Radiometric calibration", H3))
    s.append(P("Raw digital numbers are converted to at-sensor radiance using gain/offset coefficients, then to TOA reflectance "
               "by normalising for solar irradiance, Earth-Sun distance and solar zenith angle. Modern missions are cross-calibrated "
               "against each other and against vicarious targets so that time series are radiometrically stable to within ~1-3%."))
    s.append(P("C.2 Atmospheric correction", H3))
    s.append(P("Scattering and absorption by aerosols, water vapour and ozone are removed to obtain surface reflectance. Operational "
               "processors include Sen2Cor (Sentinel-2 L2A), LaSRC and LEDAPS (Landsat), MAJA (multi-temporal, Theia/CNES), FORCE, "
               "and physics-based codes such as 6S and MODTRAN. Over dark soils and sparse canopies, residual aerosol errors can bias "
               "soil-property models, so consistent processor choice across dates is important."))
    s.append(P("C.3 Cloud, shadow and snow screening", H3))
    s.append(P("Optical imagery is unusable under cloud. Masks come from the product itself (Sentinel-2 SCL and Cloud Probability, "
               "Landsat Fmask/QA_PIXEL), from machine-learning detectors (s2cloudless), or from multi-temporal consistency tests. "
               "Aggressive masking plus temporal compositing (median, maximum-NDVI or best-available-pixel) yields cloud-free "
               "mosaics for a target window. In cloudy regions Sentinel-1 SAR time series are fused to fill gaps."))
    s.append(P("C.4 Geometric processing and harmonisation", H3))
    s.append(P("Orthorectification with a digital elevation model places pixels on a map grid (UTM/WGS84 tiles for Sentinel-2 and "
               "Landsat). Multi-sensor work requires band-pass adjustment and BRDF normalisation; NASA's Harmonized Landsat "
               "Sentinel-2 (HLS) product does this to produce a 30 m, 2-3 day virtual constellation. SAR data require calibration "
               "to sigma-0 or gamma-0, speckle filtering and radiometric terrain correction."))
    s.append(P("C.5 Time-series preparation", H3))
    s.append(P("Irregularly spaced, gappy observations are regularised by interpolation and smoothing (Savitzky-Golay, Whittaker, "
               "harmonic / Fourier fitting, double-logistic phenology models). Outputs include per-pixel phenological metrics "
               "(start, peak and end of season, length, amplitude, integrated greenness) that are strong predictors of crop type "
               "and yield."))
    s.append(P("C.6 Bare-soil compositing for soil properties", H3))
    s.append(P("Topsoil can only be sensed where it is exposed. Bare-soil composites select, over several years, every pixel-date "
               "where NDVI is low (commonly &lt; 0.25-0.30), a bare-soil or normalised burn index indicates no residue or dry "
               "vegetation, and no cloud/shadow is present, then aggregate the surface reflectance (median or mean) per pixel. "
               "Examples are the Soil Composite Mapping Processor (SCMaP) for Landsat and the Geospatial Soil Sensing System (GEOS3). "
               "Further filters remove moist soils (SWIR-based moisture indices) and rough, freshly tilled surfaces, both of which "
               "distort spectra. The composite is then matched to soil-sample locations for model training."))

    # ---- Part D
    s.append(P("Part D. Feature derivation", H2))
    s.append(table([
        ["Feature", "Formula / method", "Sensitive to", "Comments"],
        ["NDVI", "(NIR - Red) / (NIR + Red)", "Green biomass, fractional cover", "Saturates at high LAI; the workhorse index (Tucker, 1979)"],
        ["EVI", "2.5 (NIR - Red) / (NIR + 6 Red - 7.5 Blue + 1)", "Biomass, with reduced saturation and atmospheric sensitivity", "MODIS standard product"],
        ["NDRE / CIred-edge", "(NIR - RE) / (NIR + RE); NIR/RE - 1", "Canopy chlorophyll, nitrogen", "Requires red-edge bands (Sentinel-2 B5-B7)"],
        ["SAVI / MSAVI", "(1 + L)(NIR - Red) / (NIR + Red + L)", "Vegetation with soil-brightness correction", "Useful at early growth stages"],
        ["NDMI / NDWI", "(NIR - SWIR1) / (NIR + SWIR1)", "Canopy and soil water content", "Also used to filter moist bare soil"],
        ["Bare-soil indices", "BSI, NBR2 = (SWIR1 - SWIR2)/(SWIR1 + SWIR2)", "Soil exposure, residue, moisture", "Thresholds select pixels for soil composites"],
        ["Soil spectral features", "Band reflectances, ratios, continuum removal, derivatives, PCA", "SOC, clay, carbonates, iron", "Basis for PLSR / Cubist soil models; S2 B11/B12 and visible bands most informative"],
        ["LAI, fAPAR, CCC", "PROSAIL inversion (look-up table or neural network) or empirical regression", "Canopy structure and pigments", "ESA SNAP Biophysical Processor; Copernicus Global Land products"],
        ["SAR features", "VV, VH backscatter, VH/VV ratio, coherence, polarimetric decompositions", "Canopy structure, moisture, roughness", "Cloud-independent; strong for rice, flooding, tillage"],
        ["Thermal features", "Land-surface temperature, Ts - Ta, evaporative fraction", "Water stress, ET", "Energy-balance models (SEBAL, METRIC, TSEB)"],
    ], [1.1 * inch, 2.2 * inch, 1.7 * inch, 1.8 * inch]))
    s.append(Spacer(1, 6))

    # ---- Part E
    s.append(P("Part E. Modelling approaches", H2))
    s.append(P("E.1 Empirical / statistical", H3))
    s.append(P("Linear and multiple regression, partial least squares regression (PLSR) and geostatistical models (kriging, "
               "regression-kriging, linear spatial mixed models) remain widely used because they are interpretable and need modest "
               "training data. PLSR is the standard chemometric method for soil spectra, handling many collinear bands."))
    s.append(P("E.2 Machine learning", H3))
    s.append(P("Random forest, Cubist, gradient boosting (XGBoost, LightGBM), support vector regression and Gaussian-process "
               "regression dominate crop classification, yield estimation and digital soil mapping. Deep learning - 1-D/2-D/3-D CNNs, "
               "LSTM/GRU recurrent networks and transformers on image time series - now gives the best crop-type and yield "
               "accuracies where large labelled datasets exist (e.g. CAP parcel declarations, Cropland Data Layer). Systematic "
               "reviews of SOC estimation report that deep models often outperform shallow networks and that the spatial "
               "distribution of samples matters more than their count."))
    s.append(P("E.3 Physically based retrieval and data assimilation", H3))
    s.append(P("Radiative-transfer models (PROSPECT + SAIL = PROSAIL) simulate canopy reflectance from leaf chemistry and canopy "
               "structure; inverting them yields LAI, chlorophyll and water content without site-specific calibration. Crop growth "
               "models (WOFOST, DSSAT, APSIM, STICS) can be constrained by assimilating satellite LAI or soil moisture through "
               "ensemble Kalman filters or variational schemes, improving yield forecasts and making them physically consistent."))
    s.append(P("E.4 Digital soil mapping (DSM)", H3))
    s.append(P("DSM formalises the SCORPAN model - soil as a function of soil, climate, organisms, relief, parent material, age and "
               "position - with machine learning. Covariates include satellite reflectance and indices, bare-soil composites, land-"
               "surface temperature, DEM derivatives (slope, curvature, wetness index), climate grids and geology. SoilGrids 2.0 "
               "applies quantile random forest to ~240,000 profiles and 400+ covariates to map SOC, total N, pH, CEC, bulk density "
               "and texture at six depths and 250 m with 5th/95th-percentile uncertainty maps. National products follow the same "
               "logic at finer resolution (e.g. POLARIS and gSSURGO-based maps in the USA; LUCAS-based maps in the EU)."))
    s.append(P("E.5 Inferring soil biology", H3))
    s.append(P("No satellite measures microbes. Current approaches (i) regress eDNA- or PLFA-derived indicators (alpha diversity, "
               "biomass, F:B ratio) on hyperspectral or multispectral features plus soil and climate covariates - DESIS imaging "
               "spectroscopy with Gaussian-process regression explained roughly 50% of bacterial and 40% of fungal alpha-diversity "
               "variance in forests; (ii) relate crop-health signals (NDVI adjusted for abiotic confounders using LUCAS topsoil and "
               "ERA5 climate) to fungal community composition in cereals; or (iii) use satellite-derived SOC, moisture, temperature "
               "and vegetation as habitat covariates in microbial biogeography models. Global syntheses show microbial biomass and "
               "richness-to-biomass ratios are strongly structured by soil carbon content and pH - both mappable - which is why "
               "such indirect inference has some skill. Treat outputs as hypotheses to be verified with field assays."))

    # ---- Part F
    s.append(P("Part F. Evaluation and quality assurance", H2))
    s.append(P("F.1 Validation design", H3))
    s.append(bullets([
        "<b>Independent reference data</b>: laboratory soil analyses (LUCAS, national soil surveys, project sampling), yield monitors or harvest plots, field crop-type surveys, parcel declarations.",
        "<b>Spatial cross-validation</b> (blocked by field, farm or region) rather than random k-fold, to avoid optimistic bias from spatial autocorrelation; SoilGrids 2.0 explicitly adopts spatial CV.",
        "<b>Temporal transfer tests</b>: train on one or more seasons and test on an unseen season to mimic operational forecasting.",
        "<b>Sensor transfer tests</b>: check whether models calibrated on Sentinel-2 hold for Landsat or MODIS; studies find skill in calibration but limited spatial robustness across sensors.",
    ]))
    s.append(P("F.2 Metrics and benchmarks", H3))
    s.append(table([
        ["Task", "Metrics", "Typical published performance", "Interpretation notes"],
        ["Soil SOC / clay / CaCO3", "R<sup>2</sup>, RMSE, bias, RPD (SD/RMSE), RPIQ (IQR/RMSE), Lin's concordance",
         "Satellite SOC: R<sup>2</sup> 0.4-0.7, RPD 1.3-2.0; hyperspectral and bare-soil composites at the upper end",
         "RPD &lt; 1.4 poor, 1.4-2.0 fair/screening, &gt; 2.0 good; report prediction intervals"],
        ["Soil pH, CEC, total N", "As above", "Usually lower: R<sup>2</sup> 0.3-0.6; CEC/pH reach 'intermediate' skill only where they covary with SOC or carbonates",
         "Largely indirect predictions; strong local calibration needed"],
        ["Crop type classification", "Overall accuracy, F1 per class, kappa, confusion matrix; design-based area estimates with confidence intervals",
         "OA 85-95% for major crops with full-season S1+S2 time series", "Minor crops and early-season maps much weaker"],
        ["Yield estimation", "R<sup>2</sup>, RMSE, MAPE, nRMSE vs. yield monitor / official statistics",
         "Field-scale R<sup>2</sup> 0.5-0.8 for cereals; county/regional R<sup>2</sup> often &gt; 0.8", "Check performance in anomalous (drought) years"],
        ["Biophysical variables (LAI, CCC)", "RMSE vs. in-situ, with uncertainty flags", "LAI RMSE ~0.5-1.0", "Saturation at LAI &gt; 4-5"],
        ["Soil biology indicators", "Explained variance, correlation with eDNA / PLFA, cluster-level significance",
         "Up to ~40-50% variance for alpha diversity; associations rather than predictions for F:B", "Exploratory; not yet suitable for management decisions"],
    ], [1.2 * inch, 1.8 * inch, 2.1 * inch, 1.7 * inch]))
    s.append(Spacer(1, 6))
    s.append(P("F.3 Uncertainty, documentation and delivery", H3))
    s.append(P("Good practice includes per-pixel uncertainty (quantile regression forests, bootstrap ensembles, conformal "
               "prediction), prediction-interval coverage checks, area-of-applicability analysis for ML models, and "
               "metadata that records sensor, processing version, training data and validation design. Deliverables are typically "
               "cloud-optimised GeoTIFFs or vector management zones consumed by farm-management software, variable-rate controllers, "
               "insurers, or carbon-MRV protocols."))

    # ---- Part G
    s.append(P("Part G. Worked example workflow (Sentinel-2 to topsoil SOC and pH map)", H2))
    s.append(bullets([
        "Define area and period (e.g. 5 years of Sentinel-2 L2A over an agricultural region); load from Earth Engine or the Copernicus Data Space.",
        "Mask clouds/shadows with SCL + s2cloudless; compute NDVI, NBR2 and a SWIR moisture index per scene.",
        "Select bare, dry, residue-free pixels (NDVI &lt; 0.25, NBR2 &lt; 0.1, moisture index below threshold); take the per-band median to build the bare-soil composite.",
        "Extract composite spectra, band ratios and DEM/climate covariates at soil-sample points (e.g. LUCAS topsoil); harmonise lab methods and depths.",
        "Fit PLSR and random forest / Cubist models for SOC, clay, CaCO<sub>3</sub>, pH and CEC; tune with spatially blocked cross-validation.",
        "Report R<sup>2</sup>, RMSE, RPD/RPIQ and prediction intervals; map predictions and uncertainty; mask pixels outside the model's area of applicability.",
        "Validate against an independent hold-out set or a new sampling campaign; document limitations (e.g. no predictions under permanent cover).",
    ]))

    s.append(PageBreak())
    s.append(P("Appendix. Process infographic", H2))
    img = Image(infographic)
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = 6.3 * inch
    img.drawHeight = 6.3 * inch * ratio
    s.append(img)
    s.append(P("Generated by the accompanying stand-alone script <i>make_infographic.py</i>.", SM))
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


# =========================================================================== #
# 3. REFERENCES
# =========================================================================== #
REFS = {
    "Foundational theory and textbooks (open access unless noted)": [
        "Cardille, J.A., Crowley, M.A., Saah, D. &amp; Clinton, N.E. (eds.) (2024). <i>Cloud-Based Remote Sensing with Google Earth Engine: Fundamentals and Applications</i>. Springer, 1,247 pp. Open access (CC BY). https://doi.org/10.1007/978-3-031-26588-4 - 55 lab-style chapters from image basics to regression, time-series, classification and agricultural applications.",
        "Canada Centre for Mapping and Earth Observation (Natural Resources Canada). <i>Fundamentals of Remote Sensing</i> tutorial. Free online primer on electromagnetic radiation, sensors, platforms and image analysis. https://natural-resources.canada.ca/maps-tools-and-publications/satellite-imagery-and-air-photos/tutorial-fundamentals-remote-sensing",
        "NASA Applied Remote Sensing Training (ARSET). <i>Fundamentals of Remote Sensing</i> and <i>Agricultural Crop Classification with Synthetic Aperture Radar and Optical Remote Sensing</i>. Free recorded courses and exercises. https://appliedsciences.nasa.gov/get-involved/training",
        "Jensen, J.R. (2015). <i>Introductory Digital Image Processing: A Remote Sensing Perspective</i>, 4th ed. Pearson. (Textbook; not open access.) Standard reference for radiometric/geometric correction and classification.",
        "Lillesand, T., Kiefer, R.W. &amp; Chipman, J. (2015). <i>Remote Sensing and Image Interpretation</i>, 7th ed. Wiley. (Textbook; not open access.)",
        "McBratney, A.B., Mendonca Santos, M.L. &amp; Minasny, B. (2003). On digital soil mapping. <i>Geoderma</i> 117, 3-52. https://doi.org/10.1016/S0016-7061(03)00223-4 - defines the SCORPAN framework used by all satellite-covariate soil mapping.",
        "Mulder, V.L., de Bruin, S., Schaepman, M.E. &amp; Mayr, T.R. (2011). The use of remote sensing in soil and terrain mapping - a review. <i>Geoderma</i> 162, 1-19. https://doi.org/10.1016/j.geoderma.2010.12.018",
    ],
    "Canonical reviews of satellite remote sensing in agriculture": [
        "Weiss, M., Jacob, F. &amp; Duveiller, G. (2020). Remote sensing for agricultural applications: a meta-review. <i>Remote Sensing of Environment</i> 236, 111402. https://doi.org/10.1016/j.rse.2019.111402 - the central synthesis of techniques, retrievable variables and applications (open-access author version available via HAL/IRD).",
        "Sishodia, R.P., Ray, R.L. &amp; Singh, S.K. (2020). Applications of remote sensing in precision agriculture: a review. <i>Remote Sensing</i> 12, 3136. https://doi.org/10.3390/rs12193136 (open access).",
        "Khanal, S., KC, K., Fulton, J.P., Shearer, S. &amp; Ozkan, E. (2020). Remote sensing in agriculture - accomplishments, limitations, and opportunities. <i>Remote Sensing</i> 12, 3783. https://doi.org/10.3390/rs12223783 (open access).",
        "Segarra, J., Buchaillot, M.L., Araus, J.L. &amp; Kefauver, S.C. (2020). Remote sensing for precision agriculture: Sentinel-2 improved features and applications. <i>Agronomy</i> 10, 641. https://doi.org/10.3390/agronomy10050641 (open access).",
        "Wu, B. et al. (2023). Challenges and opportunities in remote sensing-based crop monitoring: a review. <i>National Science Review</i> 10, nwac290. https://doi.org/10.1093/nsr/nwac290 (open access).",
        "Sentinel-2 for crop yield estimation: a systematic review (2026). <i>Smart Agricultural Technology</i>; preprint arXiv:2603.23779 (open access).",
    ],
    "Sensors, indices and physical retrieval": [
        "Tucker, C.J. (1979). Red and photographic infrared linear combinations for monitoring vegetation. <i>Remote Sensing of Environment</i> 8, 127-150. https://doi.org/10.1016/0034-4257(79)90013-0 - origin of NDVI.",
        "Huete, A. et al. (2002). Overview of the radiometric and biophysical performance of the MODIS vegetation indices. <i>Remote Sensing of Environment</i> 83, 195-213. https://doi.org/10.1016/S0034-4257(02)00096-2",
        "Drusch, M. et al. (2012). Sentinel-2: ESA's optical high-resolution mission for GMES operational services. <i>Remote Sensing of Environment</i> 120, 25-36. https://doi.org/10.1016/j.rse.2011.11.026",
        "Torres, R. et al. (2012). GMES Sentinel-1 mission. <i>Remote Sensing of Environment</i> 120, 9-24. https://doi.org/10.1016/j.rse.2011.05.028",
        "Roy, D.P. et al. (2014). Landsat-8: science and product vision for terrestrial global change research. <i>Remote Sensing of Environment</i> 145, 154-172. https://doi.org/10.1016/j.rse.2014.02.001 (open access).",
        "Claverie, M. et al. (2018). The Harmonized Landsat and Sentinel-2 surface reflectance data set. <i>Remote Sensing of Environment</i> 219, 145-161. https://doi.org/10.1016/j.rse.2018.09.002",
        "Entekhabi, D. et al. (2010). The Soil Moisture Active Passive (SMAP) mission. <i>Proceedings of the IEEE</i> 98, 704-716. https://doi.org/10.1109/JPROC.2010.2043918",
        "Jacquemoud, S. et al. (2009). PROSPECT + SAIL models: a review of use for vegetation characterization. <i>Remote Sensing of Environment</i> 113, S56-S66. https://doi.org/10.1016/j.rse.2008.01.026",
        "Main-Knorn, M. et al. (2017). Sen2Cor for Sentinel-2. <i>Proc. SPIE</i> 10427, Image and Signal Processing for Remote Sensing XXIII. https://doi.org/10.1117/12.2278218",
        "Zhu, Z. &amp; Woodcock, C.E. (2012). Object-based cloud and cloud shadow detection in Landsat imagery (Fmask). <i>Remote Sensing of Environment</i> 118, 83-94. https://doi.org/10.1016/j.rse.2011.10.028",
    ],
    "Soil properties from satellite data (SOC, pH, CEC, N, texture)": [
        "Angelopoulou, T., Tziolas, N., Balafoutis, A., Zalidis, G. &amp; Bochtis, D. (2019). Remote sensing techniques for soil organic carbon estimation: a review. <i>Remote Sensing</i> 11, 676. https://doi.org/10.3390/rs11060676 (open access) - includes an introduction to soil spectroscopy.",
        "Lima, A.A.J. et al. (2025). Soil organic carbon assessment using remote-sensing data and machine learning: a systematic literature review. <i>Remote Sensing</i> 17, 882. https://doi.org/10.3390/rs17050882 (open access).",
        "Vaudour, E. et al. (2019). Sentinel-2 image capacities to predict common topsoil properties of temperate and Mediterranean agroecosystems. <i>Remote Sensing of Environment</i> 223, 21-33. https://doi.org/10.1016/j.rse.2019.01.006 - PLSR for SOC, pH, CEC, texture, CaCO3, iron.",
        "Castaldi, F. et al. (2019). Evaluating the capability of the Sentinel 2 data for soil organic carbon prediction in croplands. <i>ISPRS Journal of Photogrammetry and Remote Sensing</i> 147, 267-282. https://doi.org/10.1016/j.isprsjprs.2018.11.026",
        "Rogge, D. et al. (2018). Building an exposed soil composite processor (SCMaP) for mapping spatial and temporal characteristics of soils with Landsat imagery (1984-2014). <i>Remote Sensing of Environment</i> 205, 1-17. https://doi.org/10.1016/j.rse.2017.11.004",
        "Dematte, J.A.M. et al. (2018). Geospatial Soil Sensing System (GEOS3): a powerful data mining procedure to retrieve soil spectral reflectance from satellite images. <i>Remote Sensing of Environment</i> 212, 161-175. https://doi.org/10.1016/j.rse.2018.04.047",
        "Zizala, D., Minarik, R. &amp; Zadorova, T. (2019). Soil organic carbon mapping using multispectral remote sensing data: prediction ability of data with different spatial and spectral resolutions. <i>Remote Sensing</i> 11, 2947. https://doi.org/10.3390/rs11242947 (open access).",
        "Wang, S. et al. (2022). Using soil library hyperspectral reflectance and machine learning to predict soil organic carbon: assessing potential of airborne and spaceborne optical soil sensing. <i>Remote Sensing of Environment</i> 271, 112914. https://doi.org/10.1016/j.rse.2022.112914",
        "Poggio, L., de Sousa, L.M., Batjes, N.H., Heuvelink, G.B.M., Kempen, B., Ribeiro, E. &amp; Rossiter, D. (2021). SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. <i>SOIL</i> 7, 217-240. https://doi.org/10.5194/soil-7-217-2021 (open access).",
        "Orgiazzi, A., Ballabio, C., Panagos, P., Jones, A. &amp; Fernandez-Ugalde, O. (2018). LUCAS Soil, the largest expandable soil dataset for Europe: a review. <i>European Journal of Soil Science</i> 69, 140-153. https://doi.org/10.1111/ejss.12499 (open access).",
        "Satellite remote sensing enables monitoring of soil organic carbon decline in croplands of Jilin, China (2026). Open access via PubMed Central (PMC12917285) - compares PLSR SOC models across MODIS, Landsat OLI and Sentinel-2 MSI and proposes the Ratio Soil Index.",
    ],
    "Soil biology and microbial inference from remote sensing (emerging)": [
        "eDNA biodiversity from space: predicting soil bacteria and fungi alpha diversity in forests using DESIS satellite remote sensing (2025). <i>International Journal of Remote Sensing</i>. https://doi.org/10.1080/01431161.2025.2464958 (open access).",
        "Exploring crop health and its associations with fungal soil microbiome composition using machine learning applied to remote sensing data (2025). <i>Communications Earth &amp; Environment</i>. https://doi.org/10.1038/s43247-025-02330-0 (open access) - NDVI adjusted with LUCAS topsoil and ERA5 covariates, linked to fungal taxa.",
        "Bastida, F. et al. (2021). Soil microbial diversity-biomass relationships are driven by soil carbon content across global biomes. <i>The ISME Journal</i> 15, 2081-2091. https://doi.org/10.1038/s41396-021-00906-0 (open access) - explains why SOC and pH maps carry information about microbial communities.",
        "Joergensen, R.G. (2024). A hitchhiker's guide: estimates of microbial biomass and microbial gene abundance in soil. <i>Biology and Fertility of Soils</i>. https://doi.org/10.1007/s00374-024-01810-3 (open access) - ground-truth methods for biomass and bacteria:fungi ratios.",
        "Frostegard, A., Tunlid, A. &amp; Baath, E. (2011). Use and misuse of PLFA measurements in soils. <i>Soil Biology and Biochemistry</i> 43, 1621-1625. https://doi.org/10.1016/j.soilbio.2010.11.021 - the reference method for fungal:bacterial ratios used to calibrate any remote-sensing proxy.",
    ],
    "Platforms, machine learning and evaluation methodology": [
        "Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D. &amp; Moore, R. (2017). Google Earth Engine: planetary-scale geospatial analysis for everyone. <i>Remote Sensing of Environment</i> 202, 18-27. https://doi.org/10.1016/j.rse.2017.06.031 (open access).",
        "Belgiu, M. &amp; Dragut, L. (2016). Random forest in remote sensing: a review of applications and future directions. <i>ISPRS Journal of Photogrammetry and Remote Sensing</i> 114, 24-31. https://doi.org/10.1016/j.isprsjprs.2016.01.011",
        "Meyer, H., Reudenbach, C., Wollauer, S. &amp; Nauss, T. (2019). Importance of spatial predictor variable selection in machine learning applications - moving from data reproduction to spatial prediction. <i>Ecological Modelling</i> 411, 108815. https://doi.org/10.1016/j.ecolmodel.2019.108815 - spatial cross-validation.",
        "Meyer, H. &amp; Pebesma, E. (2021). Predicting into unknown space? Estimating the area of applicability of spatial prediction models. <i>Methods in Ecology and Evolution</i> 12, 1620-1633. https://doi.org/10.1111/2041-210X.13650 (open access).",
        "Olofsson, P. et al. (2014). Good practices for estimating area and assessing accuracy of land change. <i>Remote Sensing of Environment</i> 148, 42-57. https://doi.org/10.1016/j.rse.2014.02.015 - standard for accuracy assessment of crop/land-cover maps.",
        "Bellon-Maurel, V. et al. (2010). Critical review of chemometric indicators commonly used for assessing the quality of the prediction of soil attributes by NIR spectroscopy. <i>TrAC Trends in Analytical Chemistry</i> 29, 1073-1081. https://doi.org/10.1016/j.trac.2010.05.006 - RPD/RPIQ interpretation.",
    ],
}


def build_refs(path):
    doc = make_doc(path, "Foundational and Canonical References")
    s = [P("Foundational and Canonical References", H1),
         P(f"Theory and practice of obtaining, processing and evaluating satellite data for agriculture and soil health &nbsp;|&nbsp; {DATE}", SUB),
         Spacer(1, 4),
         P("Entries marked <i>open access</i> are free to read at the DOI given; MDPI <i>Remote Sensing</i>, <i>Agronomy</i>, Copernicus <i>SOIL</i>, "
           "Frontiers, Nature Communications-family and arXiv items are fully open. Elsevier titles without the open-access flag usually have free "
           "author manuscripts on institutional repositories (HAL, ResearchGate, NASA/ESA archives). Bibliographic details for the reviews, "
           "SoilGrids, Google Earth Engine and the Earth Engine textbook were verified against publisher or indexing records in October 2026; "
           "the remaining entries are standard works whose details should be confirmed at the DOI before formal citation.", SM)]
    for sec, items in REFS.items():
        s.append(P(sec, H2))
        for i, it in enumerate(items, 1):
            s.append(P(f"[{i}] {it}", REF))
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


# =========================================================================== #
# 4. DATA SOURCES
# =========================================================================== #
SOURCES = [
    ["Source / portal", "Operator", "What you get", "Access"],
    ["Copernicus Data Space Ecosystem (dataspace.copernicus.eu)", "ESA / European Commission",
     "Sentinel-1 SAR (GRD, SLC), Sentinel-2 L1C/L2A, Sentinel-3 OLCI/SLSTR, Sentinel-5P; Copernicus Contributing Missions; Sentinel Hub and openEO APIs, JupyterLab",
     "Free registration; full, open and immediate"],
    ["Copernicus Land Monitoring Service (land.copernicus.eu)", "European Environment Agency / JRC",
     "Global Land products (LAI, fAPAR, NDVI, soil water index, land cover), CORINE, High-Resolution Layers, European crop-type layers",
     "Free"],
    ["USGS EarthExplorer / Landsat Collection 2 (earthexplorer.usgs.gov)", "USGS",
     "Landsat 1-9 archive since 1972 incl. Level-2 surface reflectance and temperature; ARD tiles; also hosts MODIS, ASTER, SRTM and declassified imagery",
     "Free registration"],
    ["NASA Earthdata / LP DAAC / NSIDC (earthdata.nasa.gov)", "NASA",
     "MODIS and VIIRS vegetation indices, LAI/fAPAR, LST, ET (MOD16); Harmonized Landsat Sentinel-2 (HLS); ECOSTRESS; EMIT hyperspectral; SMAP soil moisture; GPM precipitation",
     "Free registration (Earthdata Login)"],
    ["Google Earth Engine (earthengine.google.com)", "Google",
     "Multi-petabyte catalogue (Sentinel-1/2/3/5P, Landsat, MODIS, HLS, SMAP, SoilGrids, ERA5, Cropland Data Layer, WorldCereal, etc.) with server-side processing in JavaScript/Python",
     "Free for research, education and non-profit use; commercial licence otherwise"],
    ["Microsoft Planetary Computer (planetarycomputer.microsoft.com)", "Microsoft",
     "STAC catalogue of Sentinel-1/2, Landsat, MODIS, HLS, NAIP, ESA WorldCover, gNATSGO, Daymet; Python-first Hub",
     "Free; API key for some assets"],
    ["Registry of Open Data on AWS (registry.opendata.aws)", "Amazon / data providers",
     "Cloud-optimised Sentinel-2 (COGs), Sentinel-1, Landsat, NAIP, MODIS, NOAA GOES, NASA HLS",
     "Free (requester-pays for some buckets)"],
    ["EO Browser / Sentinel Hub (apps.sentinel-hub.com/eo-browser)", "Sinergise / Planet",
     "Browser visualisation and index calculation for Sentinel, Landsat, MODIS; custom scripts",
     "Free tier"],
    ["Theia Land Data Centre (theia.cnes.fr)", "CNES / French partners",
     "Sentinel-2 L2A processed with MAJA, SPOT World Heritage, snow and land-cover products",
     "Free registration"],
    ["EnMAP, PRISMA and DESIS hyperspectral portals", "DLR (EnMAP, DESIS), ASI (PRISMA)",
     "30 m hyperspectral imagery (400-2500 nm) for soil mineralogy / SOC and canopy chemistry; tasking requests for new acquisitions",
     "Free for scientific use after registration and proposal"],
    ["Alaska Satellite Facility (asf.alaska.edu)", "NASA / University of Alaska",
     "Sentinel-1 SAR with on-demand RTC and InSAR processing; ALOS PALSAR; NISAR",
     "Free (Earthdata login)"],
    ["JAXA G-Portal", "JAXA", "AMSR2 soil moisture, GCOM-C vegetation products, ALOS-2 (restricted)", "Free registration"],
    ["USDA NASS CropScape / Cropland Data Layer (nassgeodata.gmu.edu/CropScape)", "USDA NASS",
     "Annual 30 m crop-type map for the conterminous USA since 2008; crop frequency layers; VegScape NDVI condition",
     "Free"],
    ["ESA WorldCereal (esa-worldcereal.org)", "ESA / VITO consortium",
     "Global 10 m seasonal cropland, maize and cereal maps plus irrigation layers; open processing system",
     "Free"],
    ["FAO WaPOR (data.apps.fao.org/wapor)", "FAO",
     "Evapotranspiration, biomass production and water productivity for Africa and the Near East at 20-300 m, dekadal",
     "Free"],
    ["GEOGLAM Crop Monitor (cropmonitor.org)", "GEO / NASA Harvest / UMD",
     "Monthly global crop-condition assessments and underlying NDVI, precipitation and soil-moisture anomalies",
     "Free"],
    ["SoilGrids (soilgrids.org)", "ISRIC - World Soil Information",
     "Global 250 m maps of SOC, total N, pH, CEC, bulk density, texture and coarse fragments at six depths with 5th/95th percentile uncertainty; WCS/WMS and REST API",
     "Free (CC BY 4.0)"],
    ["ESDAC - LUCAS Topsoil (esdac.jrc.ec.europa.eu)", "European Commission JRC",
     "Harmonised lab data (SOC, N, P, K, pH, CEC, texture, VNIR spectra) for ~20,000+ EU sites (2009, 2015, 2018); derived European soil-property maps",
     "Free registration"],
    ["USDA NRCS Web Soil Survey / gSSURGO / gNATSGO", "USDA NRCS",
     "Detailed US soil survey polygons and attribute tables (pH, CEC, organic matter, texture, hydrologic group)",
     "Free"],
    ["Copernicus Climate Data Store - ERA5 / ERA5-Land", "ECMWF",
     "Hourly reanalysis weather and soil moisture/temperature grids used as covariates and crop-model forcing",
     "Free registration"],
    ["Open software for processing", "ESA, OSGeo, community",
     "SNAP (Sentinel toolboxes), QGIS, GDAL, rasterio, xarray, scikit-learn, geemap, Orfeo ToolBox, FORCE, Sen2Cor",
     "Free and open source"],
]


def build_sources(path):
    doc = make_doc(path, "Publicly Available Satellite Data Sources for Agriculture")
    s = [P("Publicly Available Satellite and Soil Data Sources for Agricultural Evaluation", H1),
         P(f"Portals, cloud platforms, thematic products and ancillary datasets &nbsp;|&nbsp; {DATE}", SUB),
         Spacer(1, 6),
         P("The table lists free or freely registrable sources suitable for crop monitoring, yield estimation and soil-property "
           "mapping. Cloud platforms (Earth Engine, Planetary Computer, Copernicus Data Space) are the most efficient route for "
           "time-series work because they avoid downloading raw scenes; agency portals remain the authoritative archives. Ancillary "
           "soil and climate datasets are included because they supply the calibration data and covariates that satellite-based "
           "soil-health models require."),
         table(SOURCES, [1.75 * inch, 1.1 * inch, 2.7 * inch, 1.25 * inch]),
         Spacer(1, 8),
         P("Practical notes", H2),
         bullets([
             "Prefer Level-2 surface-reflectance products (Sentinel-2 L2A, Landsat Collection 2 L2, HLS) so that multi-date analyses are physically consistent.",
             "Sentinel-2 revisit is 5 days at the equator (2-3 days at mid-latitudes with overlapping orbits); Landsat 8+9 together give 8 days; combine with Sentinel-1 for cloud-free continuity.",
             "Hyperspectral missions (EnMAP, PRISMA, EMIT) are not wall-to-wall; check archive coverage or submit tasking requests early.",
             "For soil models, pair imagery with LUCAS (EU), NRCS/NCSS (USA) or national soil archives; harmonise depth intervals and laboratory methods before training.",
             "Check licences: Copernicus, Landsat, MODIS, SoilGrids and CDL are fully open; Earth Engine is free only for non-commercial use; PlanetScope requires a licence (education and research programmes exist).",
         ])]
    doc.build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    import os
    out = "/home/bruce-vdb/Desktop/deliverables"
    build_summary(os.path.join(out, "01_High_Level_Summary_Satellite_Data_in_Agriculture.pdf"))
    build_detailed(os.path.join(out, "02_Detailed_Account_Acquisition_Processing_Evaluation.pdf"),
                   os.path.join(out, "satellite_ag_infographic.jpeg"))
    build_refs(os.path.join(out, "03_Foundational_and_Canonical_References.pdf"))
    build_sources(os.path.join(out, "04_Public_Satellite_Data_Sources.pdf"))
    print("done")
