# -*- coding: utf-8 -*-
"""

Title:			Using Python on ASCII files: GDAL
Project Descriptor:	
Project ID:		
Record:		
Author:			bmarron
Origin Date:		14 Feb 2016

Created on Sun Feb 14 15:17:10 2016

@author: bmarron
"""

#%%
"""
Info available:
http://gdal.org/python/
http://www.gdal.org/formats_list.html
http://www.gdal.org/gdal_utilities.html
https://pcjericks.github.io/py-gdalogr-cookbook/index.html
http://www.gis.usu.edu/~chrisg/python/2009/
ftp://ftp.remotesensing.org/gdal/presentations/OpenSource_Weds_Andre_CUGOS.pdf


"""

#%%
from astropy.io import ascii
data = ascii.read("/home/bmarron/Desktop/FRAGSTATS/FRAGSTAT_input_files/rck_crk06_rcl.asc")  


#%%
import numpy as np
from osgeo import ogr, osr, gdal
from gdalconst import *

#check the version of the GDAL/OGR on the imported module
gdal_version=int(gdal.VersionInfo('VERSION_NUM'))

# Enable GDAL/OGR exceptions
gdal.UseExceptions()

#%%
# Python GDAL detects what type of file you are opening.
#It loads and registers the correct driver
#ascii grid files MUST have header w/ ncols, nrows, etc

filename= "/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE010_GEOG694_Models/_PWFs_works_inprogress/Lab3/FRAGSTAT_input_files/rck2_crk06_rcl.asc"
dataset = gdal.Open(filename)
dataset

#%%
cols = dataset.RasterXSize
rows = dataset.RasterYSize
bands = dataset.RasterCount
driver = dataset.GetDriver().LongName



#%%
"""
adfGeoTransform[0] /* top left x */
adfGeoTransform[1] /* w-e pixel resolution */
adfGeoTransform[2] /* rotation, 0 if image is "north up" */
adfGeoTransform[3] /* top left y */
adfGeoTransform[4] /* rotation, 0 if image is "north up" */
adfGeoTransform[5] /* n-s pixel resolution */ 

"""

geotransform = dataset.GetGeoTransform()

#%%
print geotransform[0]
print geotransform[1]
print geotransform[2]
print geotransform[3]
print geotransform[4]
print geotransform[5]

#%%


