#! /usr/bin/python
#Python API rasters
#ftp://ftp.remotesensing.org/gdal/presentations/OpenSource_Weds_Andre_CUGOS.pdf

from osgeo import gdal
import sys
import numpy
src_file = sys.argv[1]
dst_file = sys.argv[2]
out_bands = 3

# Open source file
src_ds = gdal.Open( src_file )
src_band = src_ds.GetRasterBand(1)

# create destination file
## driver.Create( outfile, outwidth, outheight, numbands, gdaldatatype)
dst_driver = gdal.GetDriverByName('GTiff')
dst_ds = dst_driver.Create(dst_file, src_ds.RasterXSize, src_ds.RasterYSize, out_bands, gdal.GDT_Byte) 

# create output bands
band1 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
band2 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
band3 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])

# set the projection and georeferencing info
dst_ds.SetProjection( src_ds.GetProjection() )
dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )

# read the source file
for ¡Y in range(src_ds.RasterYSize):
    src_data = src_band.ReadAsArray(0,¡Y,src_ds.RasterXSize,1)
    col_values = src_data[0] 	#array of z_values, one per row in source data

for ¡X in range(src_ds.RasterXSize):
    z_value = col_values[¡X]
    [R,G,B] = MakeColor(z_value) 
    band1[¡Y][¡X] = R
    band2[¡Y][¡X] = G
    band3[¡Y][¡X] = B

# write each band out
dst_ds.GetRasterBand(1).WriteArray(band1)
dst_ds.GetRasterBand(2).WriteArray(band2)
dst_ds.GetRasterBand(3).WriteArray(band3)

#close file
dst_ds = None
