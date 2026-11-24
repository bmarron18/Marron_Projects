# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)

OUT = "/tmp/deliv/out/Item1_Literature_Review_Sentinel2_Agriculture_Metrics.pdf"
ss = getSampleStyleSheet()
H1 = ParagraphStyle('H1', parent=ss['Heading1'], fontSize=15, spaceAfter=6, spaceBefore=10)
H2 = ParagraphStyle('H2', parent=ss['Heading2'], fontSize=12, spaceAfter=4, spaceBefore=8)
B = ParagraphStyle('B', parent=ss['BodyText'], fontSize=9.5, leading=12.5, spaceAfter=5)
BL = ParagraphStyle('BL', parent=B, leftIndent=12, bulletIndent=2)
SM = ParagraphStyle('SM', parent=B, fontSize=8.3, leading=10.3)
REF = ParagraphStyle('REF', parent=B, fontSize=8.5, leading=11, leftIndent=14, firstLineIndent=-14, spaceAfter=3)
TT = ParagraphStyle('TT', parent=ss['Title'], fontSize=17, leading=21)

def P(t, s=B): return Paragraph(t, s)
def bullets(items): return [Paragraph(f"&bull; {t}", BL) for t in items]

def table(data, widths, fs=8):
    cell = ParagraphStyle('cell', parent=B, fontSize=fs, leading=fs+2, spaceAfter=0)
    rows = [[Paragraph(str(c), cell) for c in r] for r in data]
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dce6f0')),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3), ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    return t

story = []
story += [P("Remote Sensing Metrics and Procedures for Small-Scale Crop Management: "
            "A Review of Open-Access Literature, Textbooks and FAO Resources with Emphasis on "
            "Sentinel-2, Mean NDVI and the Coefficient of Variation of Local Moran's I", TT),
          P("Item 1 deliverable. Prepared November 2026. Companion to eight step-by-step procedure files (Item 2).", SM),
          Spacer(1, 8)]

story += [P("1. Purpose and scope", H1),
  P("This document summarises what peer-reviewed open-access literature, standard remote-sensing textbooks and "
    "FAO technical resources say about turning satellite (Sentinel-2) and drone imagery into agronomic information "
    "for small-scale crop operations. It focuses on (i) which metrics are used, (ii) how they are computed from "
    "surface-reflectance GeoTIFFs or Google Earth Engine (GEE) image collections, and (iii) how they are interpreted. "
    "Two metrics requested by the user are treated in depth: the field mean NDVI and the coefficient of variation (CV) "
    "of the local Moran's I statistic. The reference list is deliberately short and restricted to sources that were "
    "located and checked during this review; a few standard textbooks are listed separately as background reading."),
  P("Search strategy. Targeted queries were run for: Sentinel-2 precision-agriculture reviews; Sentinel-2 yield "
    "estimation; local Moran's I / LISA applied to NDVI and yield maps; FAO WaPOR; the Spectral Variation Hypothesis "
    "and Rao's Q; satellite resilience indicators (temporal autocorrelation, recovery metrics); Sentinel-2 pest and "
    "disease detection; remote sensing of ecosystem services in agricultural landscapes; and GEE cloud masking "
    "(Cloud Score+). Only open-access or openly documented sources were retained for the reference list.")]

story += [P("2. Key findings", H1),
  P("2.1 Why Sentinel-2 is the reference sensor for small farms", H2),
  P("Reviews agree that Sentinel-2's combination of 10 m visible/NIR bands, 20 m red-edge (705, 740, 783 nm) and SWIR "
    "(1610, 2190 nm) bands, a 5-day revisit with two satellites, and free access makes it the most practical satellite "
    "source for field and sub-field monitoring (Segarra et al. 2020; Narimani et al. 2026). The red-edge bands are "
    "repeatedly identified as the key advantage: red-edge indices (NDRE, CIred-edge, MTCI) track chlorophyll and nitrogen "
    "and saturate less than NDVI in dense canopies; SWIR bands provide canopy-water information (NDMI, MSI). The "
    "practical limits for small-scale operations are field size (statistics from fewer than ~30 valid 10 m pixels are "
    "unreliable), mixed boundary pixels (hence inward buffering), and cloud cover (hence compositing and the optional "
    "fusion with Sentinel-1 radar). Drones complement Sentinel-2 where centimetre resolution, thermal data (CWSI) or "
    "sub-weekly timing are needed; a 2024 validation study showed that the agreement between drone and Sentinel-2 "
    "indices degrades with surface heterogeneity and depends more on crop structure than on planting pattern."),
  P("2.2 Processing chain recommended by the literature", H2),
  P("The de facto standard chain in GEE is: COPERNICUS/S2_SR_HARMONIZED (Level-2A surface reflectance, harmonised "
    "across processing baselines) -> per-pixel cloud/shadow masking with Cloud Score+ "
    "(GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED, linked by system:index; a cs_cdf threshold of 0.50-0.65 is recommended, "
    "0.60 being common) or, as a fallback, the SCL band / s2cloudless -> index computation -> temporal compositing "
    "(10-16-day median or maximum-value composites; harmonic or Savitzky-Golay smoothing) -> zonal statistics per field "
    "-> export of GeoTIFFs to Drive/Cloud Storage -> Python post-processing with rasterio/xarray, numpy/scipy, "
    "scikit-learn and PySAL (libpysal/esda) for spatial statistics. Biophysical variables (LAI, fAPAR, canopy "
    "chlorophyll) are obtained with the Sentinel-2 biophysical neural network (SNAP processor) when model assimilation "
    "or absolute units are needed."),
  P("2.3 Metrics for crop condition and stress", H2),
  P("The literature converges on a small set of broad-band indices (Table 1). Stress detection is a matter of "
    "detecting anomalies relative to a phenology-matched baseline and reading which spectral domain deviates first: "
    "pigment (red-edge indices), water (SWIR indices), structure (NDVI/LAI, radar) or senescence (PSRI). For biotic "
    "stress, Sentinel-2 studies have proposed dedicated red-edge indices such as the Red Edge Disease Stress Index "
    "(REDSI, built from bands 4, 5 and 7) for wheat yellow rust (Zheng et al. 2018), and recent work on fall armyworm in "
    "maize found the red-edge (740-783 nm), narrow-NIR and SWIR bands most discriminating, with Sentinel-1 adding "
    "structural information. Reviews caution that multispectral indices cannot identify the causal agent; they "
    "localise and time anomalies for targeted scouting, and that discrimination between, e.g., disease and nitrogen "
    "deficiency requires time-series features or hyperspectral data.")]

t1 = table([
 ["Metric", "Sentinel-2 formula (bands)", "What it tracks", "Interpretation notes"],
 ["NDVI", "(B8-B4)/(B8+B4)", "Green biomass, canopy cover", "Saturates at LAI > 3-4; most used; baseline for anomalies"],
 ["kNDVI", "tanh(NDVI^2)", "Greenness, less saturation", "Preferred for resilience/TAC and dense crops"],
 ["EVI2 / SAVI", "2.5(B8-B4)/(B8+2.4B4+1); 1.5(B8-B4)/(B8+B4+0.5)", "Biomass with soil/atmos. correction", "Use early season or sparse canopies"],
 ["NDRE / CIre / MTCI", "(B8A-B5)/(B8A+B5); B8A/B5-1; (B6-B5)/(B5-B4)", "Chlorophyll, N status", "Falls before NDVI under N deficiency or early disease"],
 ["NDMI / MSI", "(B8A-B11)/(B8A+B11); B11/B8A", "Canopy water content", "Water stress signal precedes greenness loss"],
 ["PSRI", "(B4-B2)/B6", "Senescence, carotenoid:chlorophyll", "Premature rise = disease/heat/terminal drought"],
 ["REDSI", "[605.86(B7-B4) - 783.07(B5-B4)]/(2B4)", "Yellow-rust stress (wheat)", "Disease-specific; recalibrate for other crops"],
 ["NDWI / BSI", "(B3-B8)/(B3+B8); SWIR-red vs NIR-blue", "Surface water; bare soil", "Waterlogging; soil-pattern proxies for zoning"],
 ["LAI, fAPAR, CCC", "Biophysical NN (SNAP)", "Canopy structure, light absorption", "Inputs for LUE and crop-model assimilation"],
 ["CWSI (drone thermal)", "(Tc-Twet)/(Tdry-Twet)", "Transpiration / water stress", "0 unstressed - 1 fully stressed; > 0.3-0.4 irrigate"],
 ["VCI / VHI", "100(NDVI-min)/(max-min); 0.5VCI+0.5TCI", "Drought condition vs record", "VCI < 40 = agricultural drought alert"],
 ["Seasonal integral", "Trapezoid of NDVI/kNDVI SOS->EOS", "Accumulated productivity", "Best single proxy of biomass/yield within a crop"],
 ["Rao's Q", "Sum d_ij p_i p_j in a window", "Spectral heterogeneity / diversity", "Relative index; validate against plots"],
 ["TAC (AR(1))", "Lag-1 autocorrelation of residuals", "Recovery speed (resilience)", "Rising TAC = resilience loss; window matters"],
], [2.6*cm, 5.0*cm, 3.9*cm, 5.5*cm])
story += [P("Table 1. Core metrics identified in the reviewed sources.", SM), t1, Spacer(1, 6)]

story += [P("2.4 Mean NDVI, CV of NDVI and spatial autocorrelation (Moran's I, LISA, CV of local Moran's I)", H2),
  P("Field mean NDVI is the universal summary of crop state, but the reviewed precision-agriculture studies stress "
    "that it must be interpreted together with its within-field dispersion (standard deviation, CV) and with the "
    "spatial structure of the pixels. Spatial autocorrelation statistics answer the question 'is the variability "
    "organised into patches that can be managed, or is it noise?'. Global Moran's I summarises overall clustering "
    "(approximately 0 = random; positive = clustered); values around 0.4-0.55 are reported for within-field yield maps "
    "with strip-like or soil-driven patterns. Local Moran's I (Anselin 1995), the Local Indicator of Spatial Association "
    "(LISA), decomposes the global statistic into one value per pixel or parcel, so that significant High-High and "
    "Low-Low clusters and High-Low / Low-High spatial outliers can be mapped. In agriculture LISA maps are used to "
    "delineate management zones, to identify drought-vulnerability clusters, to detect spatial outliers before "
    "variogram modelling, and (as a bivariate LISA) to relate NDVI to soil properties such as bulk density."),
  P("The coefficient of variation of local Moran's I (CV(Ii) = SD of Ii / mean of Ii over the pixels of a field) is "
    "not a standard named statistic in the located literature but follows directly from the LISA framework: it "
    "quantifies how heterogeneous the spatial structure itself is. A low CV(Ii) indicates that pixels share a similar "
    "degree of local association (a field made of a few large coherent zones, or uniformly random); a high CV(Ii) "
    "indicates a mixture of strong clusters/outliers embedded in a random background, which is the signature of "
    "localised stress foci, patchy emergence, drainage problems or weed patches. Because Ii can be negative and its "
    "mean can approach zero, this review recommends reporting CV(Ii) together with the mean and SD of Ii, the "
    "percentage of significant pixels (p < 0.05, 999 permutations) and Global Moran's I, and using SD(Ii) or CV(|Ii|) "
    "when mean(Ii) < 0.05. The most useful way to use CV(Ii) is as a time series: an increase between dates, before "
    "mean NDVI falls, is an early-warning indicator of developing local stress. Scale sensitivity is a documented "
    "limitation of local Moran's I (results depend on the neighbourhood definition), so the weights (queen 8-neighbour "
    "contiguity at 10 m, or parcel contiguity at landscape level) must be fixed and reported."),
  P("2.5 Productivity, yield and water productivity", H2),
  P("The 2026 systematic review of Sentinel-2 yield estimation identifies three families of approaches: empirical "
    "models (vegetation indices with machine learning), assimilation of Sentinel-2 LAI into crop growth models "
    "(WOFOST, SAFY) and fusion with Sentinel-1 to overcome cloud cover. Red-edge indices and multi-temporal features "
    "around flowering generally give the best in-season skill; model transferability across regions remains the main "
    "bottleneck, so local calibration with farm yields is always required. FAO's WaPOR database provides, free of charge, "
    "dekadal evapotranspiration, net primary productivity, total biomass production and gross biomass water "
    "productivity (kg per m3) derived from satellite data, computed in GEE, originally over Africa and the Near East at "
    "100-250 m and now being extended globally; it allows small farms to benchmark land and water productivity against "
    "regional top performers (the 'productivity gap' approach)."),
  P("2.6 Resilience", H2),
  P("Resilience is quantified from vegetation-index time series either as recovery metrics after disturbances "
    "(magnitude of two-sigma anomalies, recovery time, recovery rate; White et al. 2020) or as critical-slowing-down "
    "indicators, chiefly the lag-1 temporal autocorrelation (TAC or AR(1)) of de-trended, de-seasonalised residuals, "
    "computed in rolling windows. Recent work confirms the physiological basis of TAC but shows that results depend on "
    "the vegetation index, the compositing interval and the window length, and warns that rising TAC alone does not "
    "prove proximity to a tipping point. A 2025 study applied these metrics (STL decomposition, anomaly frequency, "
    "recovery time, AR(1)) to agricultural heritage landscapes, demonstrating transfer to agroecosystems."),
  P("2.7 Ecosystem services and non-crop plant diversity", H2),
  P("Remote sensing delivers indicators of ecosystem-service supply rather than the services themselves. Ecosystem "
    "services that depend directly on green cover (production, forage, erosion protection) are assessed most "
    "accurately with Sentinel-2 indices and terrain data, whereas soil- and hydrology-related services need models and "
    "calibration. Reviews of agroforestry and grassland indicators list biochemical, structural, spatial and temporal "
    "indices and landscape-configuration metrics (habitat proportion, edge density, diversity) as the usual proxies. "
    "For plant diversity, the Spectral Variation Hypothesis links spectral heterogeneity to species diversity; Rao's Q "
    "computed on Sentinel-2 or Landsat NDVI (or multi-band data) is the most widely tested metric, outperforming the "
    "simple SD of NDVI in several studies and improving when multi-temporal data are used. However, the relationship is "
    "habitat- and season-dependent and has been criticised as unstable, so local validation with field plots is "
    "mandatory before diversity is mapped from spectra."),
  P("2.8 Gaps identified", H2)]
story += bullets([
  "Few open-access papers give end-to-end, reproducible GEE-to-Python procedures for smallholder-scale fields; most report results, not workflows. The Item 2 files fill this gap.",
  "No located source formally defines or validates the CV of local Moran's I as an agronomic indicator; it is proposed here as a derived LISA summary and should be calibrated against scouting records.",
  "Sentinel-2 lacks thermal bands; water-stress detection relies on SWIR indices or on drone/Landsat thermal data.",
  "Discrimination between biotic and abiotic stress from multispectral data remains indirect (pattern, timing and spectral-domain logic) and needs ground truth.",
  "Spectral-diversity to species-diversity relationships are context dependent; satellite metrics are most robust for habitat extent and configuration."])

story += [PageBreak(), P("3. Notable references (located and checked during this review)", H1),
  P("Peer-reviewed and institutional sources", H2)]
refs = [
 "Anselin, L. (1995). Local Indicators of Spatial Association - LISA. Geographical Analysis 27(2), 93-115. https://doi.org/10.1111/j.1538-4632.1995.tb00338.x",
 "Segarra, J., Buchaillot, M.L., Araus, J.L., Kefauver, S.C. (2020). Remote Sensing for Precision Agriculture: Sentinel-2 Improved Features and Applications. Agronomy 10(5), 641 (open access). https://www.mdpi.com/2073-4395/10/5/641",
 "Narimani, M., Pourreza, A., Moghimi, A., Farajpoor, P. (2026). Sentinel-2 for crop yield estimation: A systematic review. Smart Agricultural Technology (open access, CC BY). https://doi.org/10.1016/j.atech.2026.102405 (preprint: arXiv:2603.23779)",
 "Weiss, M., Jacob, F., Duveiller, G. (2020). Remote sensing for agricultural applications: A meta-review. Remote Sensing of Environment 236, 111402.",
 "Zheng, Q., Huang, W., Cui, X., Shi, Y., Liu, L. (2018). New Spectral Index for Detecting Wheat Yellow Rust Using Sentinel-2 Multispectral Imagery. Sensors 18(3), 868 (open access). https://doi.org/10.3390/s18030868",
 "International Journal of Remote Sensing (2025). Synergistic use of Sentinel-1 and Sentinel-2 data for Fall Armyworm infestation detection and mapping in maize croplands. https://doi.org/10.1080/01431161.2025.2546155",
 "Discover Agriculture (2025). Improving agricultural management zoning involving Sentinel-2 timeseries, crop's phenology stages and proximal soil sensing data. https://doi.org/10.1007/s44279-025-00283-8",
 "AgriEngineering 8(4), 154 (2026). Geostatistical Integration of Soil Attributes and NDVI for Localized Management of Black Pepper in Eastern Amazon (bivariate local Moran's I of NDVI and soil bulk density). https://doi.org/10.3390/agriengineering8040154",
 "Korean Journal of Remote Sensing 40(5) (2024). Evaluation of Surface Reflectance and Vegetation Indices Measured by Sentinel-2 Satellite Using Drone Considering Crop Type and Surface Heterogeneity. https://doi.org/10.7780/kjrs.2024.40.5.1.19",
 "White, H.J., et al. (2020). Quantifying large-scale ecosystem stability with remote sensing data. Remote Sensing in Ecology and Conservation 6(3). https://doi.org/10.1002/rse2.148",
 "Nature Ecology & Evolution (2026). Physiological fidelity of a satellite-derived forest resilience indicator in the Amazon (lag-1 temporal autocorrelation). https://www.nature.com/articles/s41559-026-03116-z",
 "npj Heritage Science (2025). Remote sensing diagnosis of ecosystem resilience dynamics in agricultural heritage landscapes. https://www.nature.com/articles/s40494-025-02222-8",
 "Remote Sensing 18(6), 889 (2026). Detecting and Predicting Vegetation Transitions Based on Resilience Dynamics and Land-Cover Changes (kNDVI, AC1). https://www.mdpi.com/2072-4292/18/6/889",
 "Torresani, M., Rocchini, D., et al. (2019). Estimating tree species diversity from space in an alpine conifer forest: The Rao's Q diversity index meets the spectral variation hypothesis. Ecological Informatics 52, 26-34.",
 "Perrone, M., et al. (2023). The relationship between spectral and plant diversity: Disentangling the influence of metrics and habitat types at the landscape scale. Remote Sensing of Environment 293, 113591 (preprint open access: bioRxiv 10.1101/2022.09.05.506583).",
 "Ecological Indicators (2020). A 15-year spatio-temporal analysis of plant beta-diversity using Landsat time series derived Rao's Q index. https://www.sciencedirect.com/science/article/pii/S1470160X2031044X",
 "Ecological Indicators (2020). Remote sensing for mapping ecosystem services to support evaluation of ecological restoration interventions in an arid landscape. https://www.sciencedirect.com/science/article/abs/pii/S1470160X20301199",
 "Ecological Indicators (2023). Could spaceborne multispectral data be used as SMART proxies' indicators for agroforestry ecosystem services? A systematic review. https://www.sciencedirect.com/science/article/pii/S1470160X23013043",
 "FAO. WaPOR - Remote sensing for water productivity: portal, database and methodology documents (WaPOR database methodology v2, 2020; quality assessment reports). https://www.fao.org/in-action/remote-sensing-for-water-productivity/ and https://openknowledge.fao.org/handle/20.500.14283/cd5978en",
 "Google Earth Engine Data Catalog. Cloud Score+ S2_HARMONIZED V1 (GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED) and Pasquarella, V. 'All Clear with Cloud Score+' (Google Earth blog, 2023). https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED",
 "Remote Sensing 16(15), 2695 (2024). Harmonized Landsat and Sentinel-2 Data with Google Earth Engine (documents the Cloud Score+ 0.60 threshold and processing chain). https://www.mdpi.com/2072-4292/16/15/2695",
]
story += [P(f"[{i+1}] {r}", REF) for i, r in enumerate(refs)]
story += [P("Textbooks (standard background reading; not retrieved online during this review)", H2)]
for r in [
 "Jones, H.G., Vaughan, R.A. (2010). Remote Sensing of Vegetation: Principles, Techniques, and Applications. Oxford University Press.",
 "Jensen, J.R. Remote Sensing of the Environment: An Earth Resource Perspective (2nd ed.). Pearson.",
 "Oliver, M.A. (ed.) (2010). Geostatistical Applications for Precision Agriculture. Springer.",
 "Anselin, L., Rey, S.J. (2014). Modern Spatial Econometrics in Practice: A Guide to GeoDa, GeoDaSpace and PySAL. GeoDa Press."]:
    story += [P(r, REF)]
story += [Spacer(1, 6), P("Note. Where an author list could not be verified from the located record, the reference is given by journal, year, title and persistent link so that it can be retrieved unambiguously.", SM)]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="Item 1 - Literature review: Sentinel-2 metrics for small-scale crop management")
doc.build(story)
print("PDF written:", OUT)
