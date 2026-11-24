# -*- coding: utf-8 -*-
"""Writes the eight question-specific procedure files (.txt)."""
import os, textwrap
OUT = "/tmp/deliv/out"
os.makedirs(OUT, exist_ok=True)

COMMON = """
================================================================================
PART A. COMMON SENTINEL-2 -> GOOGLE EARTH ENGINE (GEE) -> PYTHON PIPELINE
(identical for every question; question-specific steps follow in Part B)
================================================================================

A1. Define the area of interest (AOI)
  - Digitise each field / management unit as a polygon (GeoJSON or shapefile,
    EPSG:4326). Keep a unique field_id attribute. For small-scale operations
    (0.5-20 ha) also record crop, sowing date, expected harvest date, and any
    sub-field treatments (these become the "ground truth" table later).
  - Buffer each polygon INWARD by 10-20 m before extracting statistics, so that
    mixed boundary pixels (hedges, tracks, neighbouring fields) are excluded.
  - Upload to GEE as an Asset (FeatureCollection) or load with geemap/ee from
    a local GeoJSON.

A2. Load the Sentinel-2 Level-2A surface-reflectance collection
  - Collection: ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    (bottom-of-atmosphere reflectance, scale factor 0.0001, harmonised so that
    the Jan-2022 processing-baseline offset is removed).
  - Filter: .filterBounds(AOI) and .filterDate(start, end). For a full season
    use ~1 month before sowing to ~1 month after harvest; for multi-year
    analyses (resilience, yield forecasting) load all years since 2017.
  - Useful bands (native resolution): B2 blue 10 m, B3 green 10 m, B4 red 10 m,
    B5 red-edge-1 705 nm 20 m, B6 red-edge-2 740 nm 20 m, B7 red-edge-3 783 nm
    20 m, B8 NIR 842 nm 10 m, B8A narrow NIR 865 nm 20 m, B11 SWIR-1 1610 nm
    20 m, B12 SWIR-2 2190 nm 20 m, SCL scene classification 20 m.

A3. Cloud, shadow and edge masking
  - Preferred: join the Cloud Score+ collection
    ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED') with
    .linkCollection(csPlus, ['cs','cs_cdf']) and keep pixels where
    cs_cdf >= 0.60 (0.50-0.65 is the usual working range; lower = more
    observations but more residual haze; higher = cleaner but fewer dates).
  - Alternative/legacy: SCL band - drop classes 3 (shadow), 8, 9, 10 (cloud,
    cirrus), 11 (snow), 1 (saturated), 0 (no data). Optionally s2cloudless
    ('COPERNICUS/S2_CLOUD_PROBABILITY', probability < 40).
  - Mask pixels where B8A, B11 or B12 are masked (tile-edge artefacts).
  - Record per image the fraction of unmasked AOI pixels; discard images with
    < 70-80 % valid pixels inside the field.

A4. Compute spectral indices (map a function over the collection)
  - Scale reflectance: img.multiply(0.0001).
  - Core indices (band maths with ee.Image.normalizedDifference or .expression):
      NDVI  = (B8 - B4) / (B8 + B4)                      greenness / biomass
      kNDVI = tanh(NDVI^2)                               saturation-resistant
      EVI2  = 2.5 (B8 - B4) / (B8 + 2.4 B4 + 1)          less saturation than NDVI
      SAVI  = 1.5 (B8 - B4) / (B8 + B4 + 0.5)            sparse canopies / early season
      NDRE  = (B8A - B5) / (B8A + B5)                    chlorophyll / N status
      CIre  = (B8A / B5) - 1                             canopy chlorophyll content
      MTCI  = (B6 - B5) / (B5 - B4)                      chlorophyll, late season
      NDMI  = (B8A - B11) / (B8A + B11)                  canopy water content
      MSI   = B11 / B8A                                  moisture stress (inverse)
      NDWI  = (B3 - B8) / (B3 + B8)                      surface water / waterlogging
      PSRI  = (B4 - B2) / B6                             senescence / carotenoid:chl
      REDSI = (605.86 (B7 - B4) - 783.07 (B5 - B4)) / (2 B4)  yellow-rust disease index
      NIRv  = NDVI * B8                                  proxy for photosynthetic capacity
      BSI   = ((B11 + B4) - (B8 + B2)) / ((B11 + B4) + (B8 + B2))  bare soil
  - Biophysical variables (LAI, fAPAR, fCover, canopy chlorophyll content CCC)
    can be retrieved with the Sentinel-2 biophysical neural network (SNAP
    "Biophysical Processor" coefficients ported to GEE) when physically
    interpretable units are needed (e.g., for crop-model assimilation).
  - Resample 20 m bands to 10 m (bilinear) ONLY for visual products; for
    statistics compute red-edge/SWIR indices at native 20 m.

A5. Temporal compositing / time-series construction
  - Field-level time series: for each image, reduceRegion(mean, median, stdDev,
    percentiles 10/50/90, count) over the inward-buffered polygon -> export a
    CSV (date, field_id, index statistics, valid-pixel count).
  - Pixel-level stacks: build composites per 10-day or 16-day window
    (median or maximum-NDVI), or per phenological stage. Fill gaps by linear
    interpolation in time, then smooth with Savitzky-Golay or Whittaker
    (Python: scipy.signal.savgol_filter; or GEE harmonic regression).
  - Baseline/reference layer: multi-year (>= 3 seasons) per-pixel median
    and standard deviation of each index for the same calendar window.

A6. Export GeoTIFFs
  - ee.batch.Export.image.toDrive (or toCloudStorage/toAsset) at 10 m, CRS =
    the local UTM zone (EPSG:326xx / 327xx), region = AOI bounding box,
    maxPixels large, one band per date or one multi-band stack per index.
  - Keep a sidecar JSON with dates, cloud threshold, scale and CRS.

A7. Python post-processing (local)
  - Read with rasterio (or rioxarray/xarray for date stacks); clip to the
    polygon with rasterio.mask; convert nodata to NaN.
  - Descriptive statistics per field and date: mean, median, SD,
    CV = SD / mean (x100 %), P10, P90, skewness, % pixels below a threshold.
  - Spatial autocorrelation (PySAL: libpysal + esda):
      * Build a spatial-weights object for the raster grid: queen contiguity
        (8 neighbours) with libpysal.weights.lat2W(nrows, ncols, rook=False),
        then drop NaN cells (or use a k-nearest-neighbour weight on pixel
        centroids if the field is irregular). Row-standardise (w.transform='r').
      * Global Moran's I  : esda.Moran(values, w)        -> I, p_sim
      * Local Moran's I   : esda.Moran_Local(values, w, permutations=999)
        -> Is (local statistic per pixel), p_sim, q (quadrant: 1 HH, 2 LH,
        3 LL, 4 HL). Pixels with p_sim < 0.05 are significant.
      * LISA cluster map  : raster of HH / LL / HL / LH / not-significant.
      * Summary metrics   : % of field area in each LISA class; mean of Ii;
        SD of Ii; CV of local Moran's I = SD(Ii) / mean(Ii).
      * NOTE on CV(Ii): because Ii can be negative (outliers) and its mean can
        approach zero, always report the mean, the SD and the % of significant
        pixels alongside the CV; when mean(Ii) < 0.05 the CV becomes unstable
        and the SD of Ii (or CV of |Ii|) should be used instead.
  - Spectral heterogeneity / diversity (for Questions 2, 7, 8): Rao's Q over a
    moving window (e.g., 3x3 to 9x9 pixels) on NDVI or on several bands.
  - Temporal metrics (Questions 3, 6): anomalies z = (x - baseline_mean) /
    baseline_sd; lag-1 autocorrelation (AR(1)) of de-seasonalised residuals;
    seasonal integrals (sum / trapezoid of NDVI between SOS and EOS).
  - Clustering for management zones (Question 5): sklearn KMeans / fuzzy
    c-means on standardised multi-date index stacks.
  - Write outputs as GeoTIFF (rasterio) and CSV; make maps with matplotlib.

A8. Interpretation conventions used in Part B
  - "Field mean NDVI" = mean of valid pixels in the inward-buffered polygon.
  - "CV of NDVI" = within-field heterogeneity of crop vigour (%). Typical
    well-managed uniform fields: < 10-15 % at full canopy; > 20-25 % signals
    patchiness worth scouting.
  - "Global Moran's I" of NDVI: ~0 random, > 0 clustered (patches), values
    > 0.3-0.4 commonly reported for yield / NDVI maps with strip-like or
    soil-driven patterns.
  - "Local Moran's I (LISA)": HH = high-vigour cluster, LL = low-vigour cluster
    (stress patch), HL / LH = spatial outliers (single-pixel anomalies, often
    noise, weeds, equipment skips or incipient disease foci).
  - "CV of local Moran's I": low CV = spatial structure is homogeneous (the
    whole field is either uniformly clustered or uniformly random); high CV =
    mixed structure, i.e., a few strong clusters/outliers embedded in a
    random background - typical of localised stress, pest foci, drainage
    problems or patchy emergence. Track its change through the season: a
    rising CV(Ii) before any fall in mean NDVI is an early-warning signal
    that stress is developing locally.
  - Always interpret satellite metrics relative to (i) the crop's phenological
    stage, (ii) the same field in previous seasons, and (iii) neighbouring
    fields of the same crop in the same window.
"""

HEADER = """{title}
{underline}
Prepared: November 2026. Scope: Sentinel-2 (10-20 m, 5-day revisit) processed in
Google Earth Engine (GEE) with Python post-processing; UAV/drone imagery is
treated as an optional high-resolution complement. No executable code is
given; each step states the data, the metric(s), the processing, and how the
result is interpreted for small-scale (0.5-20 ha) crop operations.
"""

def write(fname, title, body):
    under = "=" * len(title)
    txt = HEADER.format(title=title, underline=under) + COMMON + body
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(txt.strip() + "\n")

# ----------------------------------------------------------------------------
Q1 = """
================================================================================
PART B. QUESTION 1 - ABIOTIC AND BIOTIC STRESS DETECTION IN CROPS (FIELD LEVEL)
================================================================================

Principle. Stress changes leaf pigments (chlorophyll, carotenoids), canopy
water content, canopy structure/LAI and - for drones with thermal cameras -
canopy temperature. Satellite indices cannot name the cause directly; the
procedure therefore (1) detects a deviation from the expected canopy state,
(2) characterises WHICH spectral domain deviates (pigment, water, structure),
(3) uses spatial pattern (LISA) and temporal behaviour to separate abiotic
(usually field-wide or soil/topography-shaped) from biotic (usually focal,
expanding patches) causes, and (4) triggers targeted scouting.

B1.1  Data extraction (GEE)
  - Run A1-A6 for the current season and for >= 2 reference seasons.
  - Export per date: NDVI, kNDVI, NDRE, CIre, NDMI, MSI, PSRI, REDSI, NDWI at
    10 m (red-edge/SWIR indices natively 20 m).
  - Export field-level CSV time series (mean, SD, P10, P90, count) for the same
    indices.
  - Optional complementary layers: Sentinel-1 GRD VV/VH backscatter (lodging,
    waterlogging, structure), Landsat-8/9 LST (COLLECTION 2 L2 ST_B10, 100 m,
    coarse canopy temperature proxy), ERA5-Land or CHIRPS rainfall and
    temperature for stress attribution.
  - Drone (if available): multispectral (R, G, RE, NIR) at 2-10 cm plus
    thermal; compute the same indices and, for thermal, CWSI (see below).

B1.2  Metrics and how they are computed
  (a) Field mean NDVI (and kNDVI/EVI2 for dense canopies)
      -> general vigour / biomass; compare to phenology-matched baseline.
  (b) NDVI anomaly: z = (NDVI_t - median_baseline_t) / SD_baseline_t
      where baseline is same-crop same-calendar-window previous seasons.
  (c) Chlorophyll/N domain: NDRE, CIre, MTCI. Ratio NDRE/NDVI falls when
      chlorophyll drops faster than canopy cover (N deficiency, chlorosis,
      early disease).
  (d) Water domain: NDMI (B8A,B11) and MSI. NDMI decreasing while NDVI is
      still stable = incipient water stress (SWIR responds before greenness).
  (e) Senescence/disease domain: PSRI rising prematurely; REDSI (wheat
      yellow rust index built on B4, B5, B7) rising; in general red-edge bands
      (705-783 nm) and SWIR separate healthy from infested canopies better
      than red/NIR alone.
  (f) Waterlogging/flooding: NDWI > 0 or sudden NDVI drop + Sentinel-1 VV drop.
  (g) Drone thermal: CWSI = (Tc - Twet) / (Tdry - Twet), where Tc is canopy
      temperature, Twet a well-watered reference (or lowest 1-5 % of canopy
      pixels), Tdry = Tair + 5 degC (or a non-transpiring reference);
      0 = unstressed, 1 = fully stressed; > 0.3-0.4 usually triggers irrigation.
  (h) Spatial structure per date: CV of NDVI; Global Moran's I of NDVI; LISA
      cluster map; % area LL; CV of local Moran's I.
  (i) Temporal structure: slope of field-mean NDVI over the last 3 dates;
      first date at which the LL cluster area exceeds 5 % of the field.

B1.3  Processing / analysis sequence (Python)
  Step 1  Build the phenology-matched baseline (A5) per pixel and per field.
  Step 2  For each new cloud-free date compute anomalies (b) for NDVI, NDRE,
          NDMI; flag pixels with z < -1.5 (moderate) and z < -2 (severe).
  Step 3  Compute LISA on the anomaly raster (not the raw index), so that
          clusters represent anomalous behaviour rather than permanent soil
          patterns. Keep LL pixels with p < 0.05.
  Step 4  Summarise per field and date: mean NDVI, CV NDVI, % LL area, mean
          and CV of Ii, dominant anomalous spectral domain (pigment / water /
          structure) determined by which index has the most negative z.
  Step 5  Decision rules (adjust thresholds locally after one season of
          calibration against scouting records):
          - Field-wide stress (abiotic likely): mean-NDVI z < -1.5 AND % LL
            area < 10 % AND CV(Ii) low/unchanged -> check weather, irrigation,
            nutrition; compare with neighbouring same-crop fields (if they
            drop too -> weather/regional driver).
          - Patchy stress (biotic or local abiotic): mean NDVI z near 0 but
            % LL area rising on consecutive dates and CV(Ii) rising -> scout
            LL polygons; export LL polygons as GeoJSON/KML for the phone.
          - Pigment-first signature (NDRE/CIre z strongly negative, NDMI z
            near 0) -> nitrogen deficiency, chlorosis, foliar disease.
          - Water-first signature (NDMI/MSI z negative, NDRE z near 0) ->
            drought or root problems; confirm with CWSI if a drone is
            available; check Sentinel-1 for waterlogging (low VV).
          - Senescence-first signature (PSRI up, REDSI up, NDVI only slightly
            down) at an abnormal stage -> fungal disease or heat stress.
          - Structure-first (NDVI/LAI down sharply, Sentinel-1 VH/VV changed,
            pigment indices lag) -> lodging, hail, mechanical/animal damage.
          - Expanding LL patch from a point source (area increases >= 50 %
            between two dates, centroid stable) -> biotic (pest/disease
            focus) until proven otherwise.
  Step 6  Validate with ground scouting: for each flagged LL polygon record
          cause, severity (0-100 %) and date; after one season compute
          confusion matrix / precision-recall of the thresholds and retune.

B1.4  Interpretation guide
  - A healthy, unstressed small field at full canopy typically shows NDVI
    0.7-0.9, CV NDVI < 15 %, NDRE 0.3-0.6, NDMI > 0.2, PSRI near 0, Global
    Moran's I moderate (soil-driven) and a stable LISA map between dates.
  - Stress onset is best detected by CHANGE in (i) index anomalies, (ii) the
    % LL area, and (iii) CV of local Moran's I, rather than by absolute values.
  - Biotic vs abiotic: biotic stress tends to produce significant LL clusters
    and HL/LH outliers that enlarge over time from foci; abiotic stress tends
    to produce field-wide shifts or patterns aligned with soil/topography
    (compare with a DEM or a soil-brightness BSI image from a bare-soil date).
  - Sentinel-2 cannot see individual plants; detection lags visual symptoms
    by days to weeks for small foci (< 2-3 pixels). Drones close this gap.
  - Always report the number of valid pixels; statistics from < 30 pixels
    (~0.3 ha) are unreliable.
"""

Q2 = """
================================================================================
PART B. QUESTION 2 - ABIOTIC AND BIOTIC STRESS AT THE AGROECOSYSTEM LEVEL
================================================================================

Principle. At the agroecosystem (farm-to-landscape, 1-100 km2) scale the
unit of analysis is no longer the pixel but the field (parcel) or a regular
grid cell. Stress is evaluated as (i) the fraction and spatial arrangement of
stressed fields, (ii) departures of the landscape-level vegetation signal
from its climatology, and (iii) the co-location of stress with landscape
features (water bodies, slopes, semi-natural habitats, cropping systems).
The LISA tools shift from pixel neighbourhoods to parcel neighbourhoods.

B2.1  Data extraction (GEE)
  - Parcel layer: farm field boundaries (cadastre / LPIS where available,
    otherwise delineate from a mid-season NDVI image using edge detection or
    SAM-type segmentation, or use a 100-250 m grid).
  - Crop type per parcel: from farm records, a national crop map, or a
    supervised classification of the Sentinel-2 time series (Random Forest on
    monthly NDVI/NDRE/NDMI composites).
  - Per parcel and per 10-16-day composite: mean, SD and P10 of NDVI, NDRE,
    NDMI, PSRI (reduceRegions). Export as a long-format CSV.
  - Baseline: same statistics for >= 3 previous seasons.
  - Contextual layers: SRTM/Copernicus DEM (slope, topographic wetness
    index), ESA WorldCover or Dynamic World (land cover), CHIRPS / ERA5-Land
    (rain, temperature), Sentinel-1 (waterlogging), MODIS/VIIRS active fire.

B2.2  Metrics
  (a) Landscape mean and median NDVI, area-weighted across cropland, per
      composite; its anomaly z versus the multi-year climatology.
  (b) Stressed-parcel fraction: % of parcels (or area) whose own NDVI anomaly
      is < -1.5 SD (or whose NDMI anomaly < -1.5 SD for water stress).
  (c) Vegetation Condition Index VCI = 100 (NDVI - NDVI_min) /
      (NDVI_max - NDVI_min) per pixel using the multi-year record;
      VCI < 40 = drought-stressed vegetation (agricultural drought
      monitoring convention). Temperature Condition Index (from LST) and the
      combined Vegetation Health Index VHI = 0.5 VCI + 0.5 TCI if LST is used.
  (d) Spatial structure among parcels: Global Moran's I of parcel-level NDVI
      anomaly (weights = queen contiguity between parcels or distance band
      ~500 m); Local Moran's I per parcel -> LISA map of HH / LL / HL / LH
      parcels; CV of local Moran's I across parcels.
  (e) Within-parcel heterogeneity distribution: the median and the
      inter-parcel spread (CV) of within-field CV(NDVI).
  (f) Spectral heterogeneity: Rao's Q of NDVI in moving windows (e.g.,
      90 x 90 m) over the whole landscape; sudden increases in Rao's Q within
      cropland between dates indicate patchy stress.
  (g) Biotic-outbreak indicator: count and total area of LL clusters that
      (i) are significant, (ii) span several adjacent parcels of the SAME
      crop, and (iii) grow between consecutive dates. Co-occurrence across
      fields of one host crop but not others points to a host-specific pest
      or disease.
  (h) Abiotic-driver indicators: correlation (Spearman) of parcel NDVI
      anomaly with slope, TWI, elevation, distance to water, soil map units,
      rainfall deficit (SPI/SPEI) - a strong correlation indicates an abiotic
      control.

B2.3  Processing / analysis sequence (Python)
  Step 1  Assemble the parcel x date table; attach crop type, area and
          contextual covariates.
  Step 2  Compute per-parcel anomalies against the crop-specific,
          phenology-matched climatology; compute (a), (b), (c).
  Step 3  Build parcel adjacency weights (libpysal.weights.Queen.from_dataframe
          or DistanceBand); compute Global and Local Moran's I of the NDVI
          anomaly per date; produce the parcel-LISA map; compute CV(Ii).
  Step 4  Track the LL parcel clusters through time (overlay consecutive
          dates; a cluster is "persistent" if it overlaps on >= 2 dates and
          "expanding" if its area grows).
  Step 5  Attribution: (i) if the stressed-parcel fraction rises across ALL
          crops simultaneously and correlates with rainfall deficit or heat
          days -> abiotic, climatic; (ii) if it concentrates on low-lying /
          high-TWI parcels after heavy rain -> waterlogging; (iii) if it
          concentrates on one crop with expanding LL clusters -> biotic;
          (iv) if it follows field boundaries exactly -> management
          (sowing date, variety, input level), not a stress per se.
  Step 6  Report an agroecosystem stress dashboard per composite date:
          landscape NDVI anomaly, VCI distribution, % stressed parcels by
          crop, LISA map, CV(Ii), list of expanding LL clusters with centroid
          coordinates and host crop.

B2.4  Interpretation guide
  - Landscape mean NDVI anomaly < -1 SD with a low Global Moran's I of
    anomalies (stress spread evenly) = regional abiotic driver (drought, heat
    wave, late frost). Confirm with weather data.
  - Low landscape anomaly but high Global Moran's I of anomalies with a few
    significant LL parcel clusters = local drivers (pest/disease focus,
    irrigation failure, local flooding).
  - High CV of local Moran's I among parcels = a heterogeneous landscape
    response: some neighbourhoods strongly coherent, others random. Rising
    CV(Ii) through the season while mean NDVI is stable is an early sign of
    emerging localised stress somewhere in the landscape.
  - VCI < 40 over > 30 % of cropland for two consecutive composites is a
    commonly used agricultural-drought alert.
  - Landscapes with more semi-natural habitat and crop diversity often show
    smaller biotic LL clusters (natural pest regulation); this links to
    Questions 7 and 8.
"""

Q3 = """
================================================================================
PART B. QUESTION 3 - AGROECOSYSTEM RESILIENCE
================================================================================

Principle. Resilience is operationalised from vegetation-index time series in
two complementary ways: (1) "engineering" resilience = how fast and how
completely the system returns to its reference state after a disturbance
(resistance, recovery rate, recovery time); (2) "critical slowing down"
indicators = the lag-1 temporal autocorrelation (TAC or AR(1)) and the
variance of the de-trended, de-seasonalised residuals: a rising TAC means a
slower return to equilibrium, i.e., declining resilience. Both require
multi-year data (>= 4-5 years of Sentinel-2, i.e., 2017 onwards, or longer
with Landsat/MODIS for context).

B3.1  Data extraction (GEE)
  - Run A1-A6 for the complete Sentinel-2 archive over the AOI (fields and,
    for agroecosystem level, the surrounding landscape incl. semi-natural
    vegetation).
  - Build a regular time series of kNDVI (or NDVI/EVI2/NIRv) per pixel or
    per parcel: 10-16-day maximum-value composites, gap-filled and smoothed.
    kNDVI and NIRv are preferred over NDVI because of lower saturation.
  - Covariates: precipitation and temperature (CHIRPS, ERA5-Land), drought
    index (SPEI) to identify disturbance events and to remove climate-driven
    autocorrelation.
  - Optional: Landsat 5-9 NDVI (1984-) to extend the baseline for long-term
    trend and recovery analyses at 30 m.

B3.2  Metrics
  (a) Disturbance magnitude (resistance): minimum anomaly during an event,
      expressed in SD units of the baseline; events are usually defined as
      anomalies beyond +/- 2 SD ("two-sigma events").
  (b) Recovery time: number of days/composites from the anomaly minimum until
      the anomaly returns to 0 (or to within 0.5 SD).
  (c) Recovery rate: slope of the anomaly between the minimum and the return
      point (SD units per composite); or the exponential return rate fitted
      to the recovery segment.
  (d) Degree of recovery after a fixed period (e.g., one season): anomaly at
      time t / anomaly at the minimum, in %.
  (e) Lag-1 temporal autocorrelation TAC (AR(1)) of the residuals after
      removing trend and seasonality (STL decomposition or harmonic
      regression), computed in rolling windows (e.g., 3-5 years of
      composites). Resilience proxy = 1 - TAC. Increasing TAC over time =
      resilience loss. The window length and compositing interval matter:
      very frequent sampling inflates TAC, very sparse sampling hides it;
      report the window and interval used.
  (f) Residual variance / CV of the residuals over the same windows (a second
      critical-slowing-down indicator).
  (g) Temporal stability of productivity (Question 4 metric reused):
      inter-annual CV of the seasonal NDVI integral.
  (h) Spatial component: Global Moran's I and LISA of the recovery-rate map
      and of the TAC map; CV of local Moran's I of TAC. Clusters of high TAC
      (LL in the 1-TAC map) are low-resilience zones.
  (i) Landscape buffers: proportion of semi-natural habitat and Shannon
      diversity of crops within 250-1000 m (from the crop/land-cover map),
      tested as explanatory variables for resilience metrics.

B3.3  Processing / analysis sequence (Python)
  Step 1  Build the smoothed, gap-filled time series (A5); check that the
          number of valid observations per year is similar across years to
          avoid sampling artefacts in TAC.
  Step 2  Decompose each series (statsmodels STL with the seasonal period =
          composites per year); keep the residual component.
  Step 3  Regress residuals on climate anomalies (rain, temperature) and keep
          the climate-adjusted residuals; compute TAC and variance in rolling
          windows; fit a Kendall tau trend of TAC through time.
  Step 4  Detect disturbance events (anomaly < -2 SD, or management-known
          events: drought year, flood, hail, pest outbreak) and compute
          resistance, recovery time, recovery rate, degree of recovery.
  Step 5  Map all metrics as GeoTIFFs; compute Global/Local Moran's I and
          CV(Ii) on the TAC and recovery-rate rasters (or parcel values).
  Step 6  Explain the spatial pattern: relate low-resilience clusters to soil,
          slope, irrigation, crop rotation diversity, distance to
          semi-natural habitat, field size.
  Step 7  Report per field / per landscape: current TAC and its trend,
          mean recovery time of past events, inter-annual CV of productivity,
          and a resilience class (high / medium / low) from tertiles of a
          composite index (z-scored 1-TAC, recovery rate, -CV).

B3.4  Interpretation guide
  - Recovery time < 1 season and recovery rate high, TAC stable or falling,
    inter-annual CV low -> resilient system.
  - Rising TAC (positive Kendall trend over 5+ years) with rising residual
    variance -> loss of resilience / approaching a transition (e.g., soil
    degradation, salinisation, chronic water deficit) even if mean NDVI is
    unchanged. A rising TAC does not uniquely prove proximity to a tipping
    point; confirm with field evidence and climate forcing analysis.
  - Low TAC caused by very noisy data (poor cloud masking) is an artefact;
    check the valid-observation count first.
  - Spatially: low-resilience LL clusters in the (1-TAC) map that coincide
    with specific soils or with monoculture blocks indicate where management
    (cover crops, organic matter, rotation, drainage) should be prioritised.
  - Agroecosystem-level conclusions should compare crop parcels with nearby
    semi-natural vegetation processed identically; higher TAC in cropland
    relative to its surroundings signals management-driven fragility.
"""

Q4 = """
================================================================================
PART B. QUESTION 4 - CROP PRODUCTIVITY
================================================================================

Principle. Productivity is estimated from Sentinel-2 by (1) seasonal
integrals of greenness indices as a proxy of accumulated biomass, (2)
biophysical variables (LAI, fAPAR) that feed light-use-efficiency (LUE) or
crop-growth models, and (3) water productivity (biomass per unit of water
consumed) when evapotranspiration is available (e.g., FAO WaPOR). Outputs
are relative productivity maps and absolute biomass / yield estimates once
calibrated with field data.

B4.1  Data extraction (GEE)
  - Run A1-A6 over the full season; export 10-day composites of NDVI, EVI2,
    kNDVI, NIRv and LAI/fAPAR (Sentinel-2 biophysical NN) at 10 m.
  - Phenology dates: derive SOS (start), POS (peak), EOS (end) per pixel from
    the smoothed NDVI curve (threshold of 20-50 % of seasonal amplitude, or
    the derivative method). Also export the date of maximum NDVI.
  - Meteorological drivers: incoming solar radiation and temperature
    (ERA5-Land) for LUE modelling.
  - Water: FAO WaPOR layers (actual evapotranspiration and interception AETI,
    net primary productivity NPP, total biomass production TBP, gross biomass
    water productivity GBWP) at 100-300 m (Africa/Near East at 100 m and
    higher where available; WaPOR v3 expands coverage).
  - Drone (optional): RGB structure-from-motion canopy height model (CHM)
    and plant counts for emergence/establishment productivity.

B4.2  Metrics
  (a) Seasonal integral of NDVI/EVI2/kNDVI (area under the curve between SOS
      and EOS; trapezoid rule) -> relative biomass proxy. Within one crop
      and region this correlates well with final biomass and yield.
  (b) Peak index (max NDVI / max LAI) and date of peak; length of season
      (EOS - SOS); senescence rate (slope from POS to EOS).
  (c) fAPAR-based LUE model: GPP or biomass = sum over days of
      (fAPAR x PAR x epsilon_max x f(temperature) x f(water)), with crop-
      specific epsilon_max; grain yield = biomass x harvest index.
  (d) NPP / TBP from WaPOR (kg DM / ha / dekad) and GBWP (kg / m3) =
      TBP / AETI -> land and water productivity.
  (e) Canopy chlorophyll content (CCC = LAI x Cab) from CIre / NDRE at
      flowering -> nitrogen-limited productivity.
  (f) Within-field productivity statistics: mean, CV, P10/P90 of the seasonal
      integral; Global Moran's I; LISA map (HH = consistently productive
      zones, LL = chronically poor zones); CV of local Moran's I.
  (g) Multi-year temporal stability (Blackmore-type analysis): per pixel,
      mean of normalised integral across years (relative productivity) and
      its inter-annual CV -> classes: stable-high, stable-low, unstable.

B4.3  Processing / analysis sequence (Python)
  Step 1  Smooth and gap-fill the per-pixel series; derive SOS/POS/EOS.
  Step 2  Integrate indices between SOS and EOS; compute peak metrics.
  Step 3  If LAI/fAPAR available, run the daily LUE model (A3 driver data);
          otherwise use the integral as a relative productivity index (RPI)
          = pixel integral / field (or landscape) median integral.
  Step 4  Calibrate: regress farmer yields (yield monitor, weighed plots,
          field totals) on the integral / LUE biomass; report R2, RMSE and
          relative RMSE; use leave-one-field-out cross validation.
  Step 5  Spatial analysis on the productivity map: CV, Global Moran's I,
          LISA, CV(Ii); export HH/LL polygons.
  Step 6  Multi-year stability classes (g) when >= 3 seasons are available.
  Step 7  Water productivity (if WaPOR or an ET product is available):
          biomass or yield / AETI per field; compare to the regional 95th
          percentile ("productivity gap" approach).

B4.4  Interpretation guide
  - RPI < 0.8 in a persistent LL cluster = chronically low-yielding zone;
    investigate soil depth, compaction, drainage, pH, salinity. RPI > 1.2 in
    HH clusters = high-potential zones where inputs give the best return.
  - A high peak NDVI with a short season (early EOS) indicates terminal
    stress (heat/drought) that curtails grain filling - productivity is lower
    than the peak suggests; the integral captures this, the peak does not.
  - Saturation: NDVI plateaus above LAI ~3-4; use kNDVI, EVI2 or LAI for
    dense cereals, maize and sugarcane.
  - Water productivity (kg / m3) well below the regional top performers
    with similar AETI indicates management (nutrition, variety, timing)
    rather than water as the limiting factor.
  - Stable-low zones justify permanent changes (drainage, liming, zone
    retirement or conversion to habitat - see Question 7); unstable zones
    justify in-season variable management (Question 5).
  - A high CV of local Moran's I of the productivity map indicates that the
    field contains both strongly coherent zones and random patches; zoning
    (Question 5) will be effective for the coherent part only.
"""

Q5 = """
================================================================================
PART B. QUESTION 5 - MANAGEMENT OF CROP VARIABILITY (MANAGEMENT ZONES AND
VARIABLE-RATE DECISIONS)
================================================================================

Principle. Within-field variability is quantified, separated into stable
(soil-driven) and transient (season-driven) components, and converted into
management zones (MZ) and prescription maps for variable-rate seeding,
fertilisation, irrigation and targeted scouting. The key statistics are the
CV of NDVI, Global and Local Moran's I (is the variability structured enough
to be managed?), and the temporal stability of the spatial pattern.

B5.1  Data extraction (GEE)
  - Run A1-A6 for >= 3 seasons; export (i) per-season peak-stage composites
    of NDVI, NDRE, EVI2, (ii) seasonal integrals (Question 4), (iii) a
    bare-soil composite (BSI / brightness from dates with NDVI < 0.25) as a
    proxy of soil texture/organic matter patterns, (iv) in-season 10-day
    composites of NDRE / CIre for nitrogen decisions.
  - Ancillary: DEM derivatives (slope, TWI), soil ECa or soil sampling if
    available, yield-monitor maps if available.
  - Drone: high-resolution NDVI/NDRE for small fields (< 2 ha) where 10 m
    pixels give too few samples (< 200 pixels).

B5.2  Metrics
  (a) CV of NDVI (and of NDRE) per date -> magnitude of variability.
  (b) Global Moran's I of NDVI per date -> spatial structure (manageability).
      Rule of thumb: I < 0.2 = weak structure (variability is noise-like,
      uniform management preferred); I > 0.4 = strong structure (zoning
      worthwhile).
  (c) LISA map per date; % area in HH and LL; CV of local Moran's I.
  (d) Temporal stability of the pattern: Pearson/Spearman correlation of the
      normalised index between seasons; pixel-wise inter-annual CV of the
      normalised integral; stability classes (stable-high, stable-low,
      unstable) as in Question 4.
  (e) Zone compactness and size: number of zones, mean zone area, fraction
      of zone area in patches smaller than the implement width (should be
      small).
  (f) Nitrogen decision metrics: NDRE or CIre sufficiency index SI =
      NDRE_zone / NDRE_reference (reference = well-fertilised strip or the
      95th percentile of the field); N-rate adjustment proportional to
      (1 - SI).
  (g) Irrigation decision metrics: NDMI / MSI anomaly per zone; CWSI from
      drone thermal when available.

B5.3  Processing / analysis sequence (Python)
  Step 1  Normalise each season's index map (divide by field median) to make
          seasons comparable; stack the normalised maps, the integrals, BSI
          and DEM derivatives.
  Step 2  Compute per-season CV, Global Moran's I, LISA, CV(Ii). Decide
          whether zoning is justified (I > 0.3 in most seasons AND CV > 10 %).
  Step 3  Temporal stability: compute between-season correlations and the
          pixel-wise inter-annual CV; map stability classes.
  Step 4  Delineate zones: standardise inputs (z-scores), apply k-means or
          fuzzy c-means for k = 2..5; choose k by the fuzziness performance
          index / normalised classification entropy or by the elbow of
          within-cluster variance; smooth with a majority filter (3x3 or
          5x5) and remove patches smaller than 2-3 implement widths.
  Step 5  Characterise zones: mean and SD of each input per zone, soil
          samples per zone (stratified), yield per zone if available.
  Step 6  In-season prescription: per zone compute the current NDRE/CIre
          sufficiency index (f) and NDMI anomaly (g); convert to rates with
          an agronomic response function; export the prescription map as
          GeoTIFF / shapefile in the controller format.
  Step 7  Evaluate: after harvest compare yield (or seasonal integral) by
          zone and by treatment; update zones every 2-3 seasons.

B5.4  Interpretation guide
  - High CV + high Moran's I + stable pattern between seasons -> variability
    is real, structured and persistent -> soil-based management zones and
    fixed differentiated rates (seed, P, K, lime, drainage).
  - High CV + high Moran's I but unstable between seasons -> the pattern is
    weather- or management-driven -> use in-season, sensor-based variable
    rates (N, irrigation) rather than fixed zones.
  - High CV + low Moran's I -> fine-grained noise or sub-pixel variability
    (weeds, emergence gaps, stones): satellite zoning is not useful; use
    drones or uniform management with targeted scouting of HL/LH outliers.
  - Low CV (< 10 %) -> uniform management is appropriate; focus on
    whole-field timing decisions.
  - CV of local Moran's I: a low CV(Ii) with high Global I means the field
    is composed of a few large coherent zones (easy to manage); a high CV(Ii)
    means a mixture of strong clusters and random background - manage the
    coherent zones and scout the rest.
  - Always ground-truth zones with a few stratified soil samples before
    prescribing inputs; satellite indices describe the crop's response, not
    the cause.
"""

Q6 = """
================================================================================
PART B. QUESTION 6 - MAINTAINING, IMPROVING AND FORECASTING CROP YIELDS
================================================================================

Principle. Yield is forecast by (1) empirical models relating in-season
index features to historical yields, (2) data assimilation of Sentinel-2
LAI/fAPAR into crop-growth models (e.g., WOFOST, SAFY, DSSAT/AquaCrop), or
(3) hybrid machine-learning models that combine indices, weather and soil.
Yield maintenance/improvement uses the same pipeline in monitoring mode:
yield-gap maps, early-warning flags and post-harvest diagnostics.

B6.1  Data extraction (GEE)
  - Run A1-A6 for all available seasons; export 10-day composites of NDVI,
    kNDVI, EVI2, NDRE, CIre, NDMI and LAI/fAPAR; derive phenology (SOS, POS,
    EOS) and the seasonal integral (Question 4).
  - Sentinel-1 VV/VH 12-day composites (fills cloudy periods; sensitive to
    canopy structure and moisture).
  - Weather (ERA5-Land / CHIRPS): growing-degree days, rainfall totals,
    number of heat-stress days (Tmax above the crop threshold), water
    balance by phenological phase.
  - Soil (SoilGrids 250 m) and DEM derivatives.
  - Yield data: farm totals per field per season (minimum), yield monitor or
    hand-harvest plots (better). Minimum useful training set: ~30 field-
    seasons for a regional empirical model; for a single farm use relative
    yield within-field ranking instead of absolute prediction.

B6.2  Metrics / features
  (a) Index features by phenological phase: mean NDVI/kNDVI at tillering,
      stem elongation, flowering, grain filling; peak value and date;
      integral to date; NDRE/CIre at flowering (N status); NDMI at grain
      filling (water); senescence slope.
  (b) Accumulated weather features by phase; stress-day counts.
  (c) Assimilated LAI trajectory -> simulated biomass and yield from the
      crop model (ensemble Kalman filter or recalibration of sowing date,
      emergence and LUE parameters).
  (d) Model skill: R2, RMSE, relative RMSE (% of mean yield), bias, by
      leave-one-year-out cross-validation; forecast lead time (days before
      harvest at which skill stabilises; typically flowering to early grain
      filling).
  (e) Yield-gap metrics: attainable yield = 90-95th percentile of predicted
      pixel yields in the field/landscape; gap = attainable - actual; gap
      map and its LISA clusters.
  (f) Early-warning flags (from Questions 1-2): anomaly in NDVI/NDRE/NDMI
      at critical phases; probability of yield below the farm's 5-year mean.
  (g) Spatial statistics of the predicted yield map: CV, Global Moran's I,
      LISA, CV(Ii).

B6.3  Processing / analysis sequence (Python)
  Step 1  Build the feature table (field-season rows; index, weather and
          soil features as columns).
  Step 2  Fit models of increasing complexity: (i) linear regression on the
          seasonal integral or peak kNDVI (robust baseline), (ii) Random
          Forest / gradient boosting on all features, (iii) crop-model
          assimilation if LAI and crop parameters are available. Evaluate
          with leave-one-year-out CV; retain the simplest model within 10 %
          of the best RMSE.
  Step 3  In-season forecasting: re-run the chosen model at each new
          composite with features available "to date"; report the forecast,
          its prediction interval and the historical skill at that lead
          time; stop updating when skill plateaus (usually early grain fill).
  Step 4  Map pixel-level predicted yield for the current season; compute
          yield gap (e); compute CV, Moran's I, LISA, CV(Ii).
  Step 5  Diagnostics after harvest: compare prediction with actual yield;
          identify which phase/feature explained the shortfall (e.g., low
          NDRE at flowering -> N; low NDMI in grain fill -> water; short
          season -> heat); feed into next season's management plan.
  Step 6  Maintain/improve yield: use stable LL yield-gap clusters to target
          soil amendments and drainage (Questions 4-5); use in-season flags
          to trigger N top-dressing, irrigation or pest control; use the
          multi-year record to evaluate whether changes closed the gap
          (difference-in-differences between treated and untreated zones).

B6.4  Interpretation guide
  - Forecast skill: relative RMSE < 15 % at flowering is good for
    field-scale cereals; < 10 % is excellent. Forecasts made before canopy
    closure are mostly a function of sowing date and emergence and are
    unreliable.
  - A forecast below the 5-year mean with a negative NDRE anomaly and a
    normal NDMI indicates a nutrition-limited season that is still
    correctable if before flowering; the same forecast with a negative NDMI
    anomaly indicates a water-limited season (irrigate if possible).
  - Yield-gap LL clusters that are stable across years = structural limits
    (soil); those that move = seasonal limits (pests, weather, operations).
  - Saturation of NDVI above LAI ~3-4 compresses yield differences in dense
    crops; prefer kNDVI, EVI2, red-edge indices or LAI.
  - Model transfer across regions/crops is unreliable; always recalibrate
    locally and report the uncertainty.
  - For very small fields (< 1 ha) with < 100 pixels, forecast at the field
    level only, not pixel level; a drone survey can provide the within-field
    pattern.
"""

Q7 = """
================================================================================
PART B. QUESTION 7 - ECOSYSTEM SERVICES IN AGROECOSYSTEMS
================================================================================

Principle. Remote sensing provides proxies for ecosystem-service (ES)
SUPPLY indicators; it cannot measure services directly. Sentinel-2 indices
and land-cover maps feed indicator models for: provisioning (biomass/yield,
forage), regulating (carbon sequestration proxy, soil-erosion protection,
water regulation, pollination/pest-control habitat), and supporting
(habitat extent, connectivity). Each indicator is mapped, aggregated per
field and landscape, and tracked over time; trade-offs between services are
assessed by correlation among indicator maps.

B7.1  Data extraction (GEE)
  - Land cover / habitat map at 10 m: ESA WorldCover, Dynamic World, or a
    supervised classification of Sentinel-2 seasonal composites that
    separates crops, grassland, hedgerows/tree lines, woodland, wetlands,
    water, bare soil. Field margins and hedgerows are often < 10 m; use
    seasonal NDVI contrast (woody vegetation stays green after crop
    harvest) and, where possible, drone or very-high-resolution imagery.
  - Seasonal composites and integrals of NDVI/kNDVI/NIRv (Question 4), bare
    soil frequency (fraction of dates with NDVI < 0.25 during the year),
    cover-crop presence (winter NDVI > 0.4 on cropland).
  - Terrain: DEM, slope, flow accumulation; rainfall erosivity (CHIRPS).
  - FAO WaPOR: NPP, AETI, GBWP for carbon/water indicators.
  - Phenology of flowering resources: spring/summer NDVI and visible-band
    indices of grasslands/hedges as proxy for floral resource timing.

B7.2  Metrics (indicator per service)
  (a) Provisioning - crop/forage production: seasonal NDVI integral or WaPOR
      NPP/TBP (kg DM/ha); relative productivity index (Question 4).
  (b) Carbon regulation: annual integral of NIRv or kNDVI as a GPP proxy;
      NPP from WaPOR; woody-vegetation cover fraction (above-ground carbon
      proxy); soil-carbon proxy via bare-soil reflectance (lower
      brightness, higher SWIR absorption = higher SOC) calibrated with soil
      samples.
  (c) Soil-erosion protection: fractional vegetation cover FVC =
      (NDVI - NDVI_soil)/(NDVI_veg - NDVI_soil) over the year, especially in
      the erosive season; cover-management factor C (RUSLE) estimated from
      NDVI, combined with slope-length (LS) and rainfall erosivity (R) ->
      relative soil-loss map; number of bare-soil days per year.
  (d) Water regulation: wetland and riparian vegetation extent (NDWI,
      NDMI), fraction of permanent vegetation along streams (buffer
      analysis), AETI/precipitation ratio.
  (e) Pollination and pest-control habitat: proportion of semi-natural
      habitat (SNH) within 250, 500 and 1000 m of each field; edge density
      of SNH; distance from field centroid to nearest SNH patch; flowering
      resource index (NDVI/greenness of SNH during crop flowering window).
  (f) Habitat and connectivity (supporting): landscape metrics from the
      10 m map - patch number, mean patch size, edge density, Shannon
      diversity of land cover, effective mesh size; computed with pylandstats.
  (g) Spatial diagnostics of each indicator map: CV, Global Moran's I, LISA,
      CV of local Moran's I; a bivariate LISA between two indicators (e.g.,
      productivity vs. SNH proportion) identifies synergy (HH) and trade-off
      (HL/LH) zones.
  (h) Composite ES index: z-score each indicator, average with weights set
      by stakeholders; report both the composite and the individual layers.

B7.3  Processing / analysis sequence (Python)
  Step 1  Produce and validate the land-cover/habitat map (accuracy >= 80 %
          overall with a confusion matrix from reference points).
  Step 2  Compute each indicator raster (a)-(f) for the reference year and,
          if possible, for a baseline year (e.g., 2017-2018) to measure
          change.
  Step 3  Aggregate per field, per farm and per landscape grid (e.g., 500 m);
          compute spatial statistics (g).
  Step 4  Trade-off analysis: Spearman correlation matrix among indicators
          across grid cells; bivariate LISA of pairs of interest.
  Step 5  Scenario assessment (optional): recompute indicators after
          hypothetically converting stable-low productivity zones
          (Question 4) to SNH; quantify production lost vs. regulating
          services gained.
  Step 6  Report a per-farm ES dashboard: indicator values, their change
          since baseline, their rank versus the surrounding landscape, maps
          of synergy/trade-off zones.

B7.4  Interpretation guide
  - ES that depend directly on green cover (production, erosion control,
    forage, carbon proxy) are the ones most reliably assessed from
    Sentinel-2; services depending on soil or hydrology are inferred through
    models and need calibration.
  - SNH proportion within 500 m below ~10-20 % generally indicates poor
    support for pollinators and natural enemies; increasing hedgerow/margin
    cover shows up as rising woody fraction and edge density.
  - Bare-soil days > 120 per year on slopes > 5 % flags high erosion risk;
    cover crops reduce this and increase winter NDVI integral.
  - HH clusters in a bivariate LISA of production vs. SNH indicate
    multifunctional areas; HL (high production, low SNH) marks intensive
    zones where habitat measures could be targeted; LH (low production,
    high SNH) are candidates for extensification/agri-environment schemes.
  - Trends: compare 3-year moving averages, not single years, because
    weather dominates inter-annual variation in all greenness-based
    indicators.
"""

Q8 = """
================================================================================
PART B. QUESTION 8 - NON-CROP PLANT DIVERSITY IN AGROECOSYSTEMS
================================================================================

Principle. Non-crop plant diversity (field margins, hedgerows, grasslands,
fallows, weeds within fields) is assessed through (1) mapping the extent and
configuration of non-crop habitats and (2) the Spectral Variation Hypothesis
(SVH): spectral heterogeneity within a habitat patch correlates with
environmental heterogeneity and species diversity. The main metric is Rao's
quadratic entropy (Rao's Q) computed on Sentinel-2 NDVI or multi-band
reflectance; it combines pixel abundance and pairwise spectral distance.
Validation with field plots is essential because the SVH is not universally
reliable and depends on habitat type, season and spatial scale.

B8.1  Data extraction (GEE)
  - Non-crop habitat mask: from the land-cover/habitat map (Question 7);
    exclude cropped pixels (NDVI phenology typical of crops) and buffer
    crop boundaries by 10 m to avoid mixed pixels.
  - Multi-temporal Sentinel-2 composites across the season (e.g., monthly
    from spring to autumn) of NDVI, NIRv, and the 10 bands B2-B8A, B11, B12.
    Multi-date stacks capture phenological asynchrony among species and
    generally improve the spectral-diversity / species-diversity relation.
  - Drone (strongly recommended for margins and small patches): RGB or
    multispectral at 1-5 cm for fine-scale spectral diversity, flowering
    cover (visible-band indices, e.g., excess green/red), and woody vs.
    herbaceous structure (SfM canopy height).
  - Field data: species lists / Shannon H' / richness in 10 x 10 m or
    20 x 20 m plots aligned with Sentinel-2 pixels (at least 20-30 plots
    per habitat type).

B8.2  Metrics
  (a) Habitat extent and configuration: area and % of non-crop habitat per
      farm/landscape; hedgerow length density (km/km2); mean margin width
      (drone); patch size distribution; edge density; connectivity.
  (b) Spectral diversity (alpha):
      - Rao's Q in a moving window (3x3 = 30 m, 5x5 = 50 m) on NDVI or on
        the PCA-reduced multi-band stack: Q = sum over pixel pairs i,j of
        d_ij x p_i x p_j, where d_ij is the spectral distance and p_i the
        relative abundance of spectral value i. Higher Q = higher spectral
        heterogeneity.
      - Coefficient of variation of NDVI / SD of NDVI in the window (simpler
        SVH metric).
      - Spectral species richness: k-means clustering of the multi-band
        stack into "spectral species"; richness and Shannon entropy of
        spectral species per window/patch.
      - Multi-temporal Rao's Q: Q computed on the stacked monthly NDVI
        (temporal spectral dissimilarity) - captures species with different
        phenology.
  (c) Spectral beta diversity: dissimilarity (Bray-Curtis on spectral-species
      composition, or Rao's Q between patches) among habitat patches ->
      landscape-level turnover.
  (d) Within-crop weed indicator: early-season (pre-canopy) NDVI
      heterogeneity and HL outliers in the LISA map of the crop field;
      drone-based weed cover fraction.
  (e) Spatial statistics: Global and Local Moran's I of the Rao's Q map
      (HH = diversity hotspots), CV of local Moran's I.
  (f) Validation statistics: Spearman rho / R2 between Rao's Q (or other
      SD metrics) and field Shannon H' or richness, per habitat type and per
      month; choose the month and window size that maximise the relation.

B8.3  Processing / analysis sequence (Python)
  Step 1  Build the non-crop habitat mask; stratify by habitat type
          (grassland, hedgerow/woody, fallow, wetland margin).
  Step 2  For each monthly composite compute Rao's Q (e.g., with the
          rasterdiv-style algorithm re-implemented in numpy: discretise NDVI
          into 8-bit classes, compute pairwise distances and relative
          abundances in each window) and the SD/CV of NDVI; compute spectral
          species via k-means (k ~ 10-30) on the PCA components and their
          richness/Shannon per window.
  Step 3  Compute the multi-temporal Rao's Q on the stacked monthly NDVI.
  Step 4  Extract metrics at field plots; fit the SVH relation (f) per habitat
          type and month; retain the best configuration; document R2 and
          sign. If no significant relation (rho < 0.3), do NOT map diversity
          from spectra for that habitat - report extent/configuration only.
  Step 5  Map predicted diversity (or Rao's Q as a relative index) across
          non-crop habitats; compute LISA and CV(Ii); identify hotspots and
          low-diversity patches.
  Step 6  Trend analysis: repeat for several years; a declining Rao's Q in
          grassland/margins may indicate homogenisation (e.g., eutrophication
          or dominance by a few grasses) - verify in the field.
  Step 7  Report per farm: non-crop habitat area and configuration, mean and
          hotspots of spectral diversity, validated relationship (or its
          absence), and recommendations (e.g., widen margins, diversify
          seed mixes, reduce mowing frequency in low-Q patches).

B8.4  Interpretation guide
  - Rao's Q is a RELATIVE heterogeneity index: compare within one habitat
    type, sensor, season and window size; absolute values are not
    transferable between studies.
  - Dense, closed canopies (e.g., mature hedgerows at full leaf) give low
    Rao's Q regardless of species richness (saturation); use spring or
    autumn dates when phenological differences among species are expressed.
  - High Rao's Q may also arise from bare-soil gaps, shadows or mixed
    pixels; inspect HL/LH outliers and mask soil/water before interpreting.
  - At 10-20 m the SVH mostly reflects environmental heterogeneity (soil
    moisture, management, structure) rather than species identity; drone
    imagery at cm resolution approaches the direct species-trait relation.
  - Habitat extent and configuration metrics (a) are the most robust
    non-crop diversity indicators from satellites; spectral diversity adds
    information on condition/heterogeneity once validated locally.
  - A rising CV of local Moran's I of the Rao's Q map indicates increasingly
    patchy diversity (a few hotspots in a homogenised matrix) - a trigger for
    conservation measures on the homogeneous parts.
"""

files = [
 ("Q1_crop_level_stress_detection.txt",
  "QUESTION 1 - Abiotic and biotic stress detection and evaluation in crops (field level) with Sentinel-2 / drone data", Q1),
 ("Q2_agroecosystem_level_stress_detection.txt",
  "QUESTION 2 - Abiotic and biotic stress detection and evaluation at the agroecosystem level with Sentinel-2 / drone data", Q2),
 ("Q3_agroecosystem_resilience.txt",
  "QUESTION 3 - Measuring and evaluating agroecosystem resilience with Sentinel-2 / drone data", Q3),
 ("Q4_crop_productivity.txt",
  "QUESTION 4 - Measuring and evaluating crop productivity with Sentinel-2 / drone data", Q4),
 ("Q5_management_of_crop_variability.txt",
  "QUESTION 5 - Using Sentinel-2 / drone data for the management of crop variability", Q5),
 ("Q6_yield_maintenance_improvement_forecasting.txt",
  "QUESTION 6 - Using Sentinel-2 / drone data for maintaining, improving and forecasting crop yields", Q6),
 ("Q7_ecosystem_services.txt",
  "QUESTION 7 - Measuring and evaluating ecosystem services in agroecosystems with Sentinel-2 / drone data", Q7),
 ("Q8_noncrop_plant_diversity.txt",
  "QUESTION 8 - Measuring and evaluating non-crop plant diversity in agroecosystems with Sentinel-2 / drone data", Q8),
]
for fn, title, body in files:
    write(fn, title, body)
print("written", len(files), "files to", OUT)
