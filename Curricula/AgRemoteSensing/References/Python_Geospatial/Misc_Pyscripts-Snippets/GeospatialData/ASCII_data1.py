# -*- coding: utf-8 -*-
"""

Title:			Using Python on ASCII files
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
ArcPy is part of ArcGIS, which is not free software. You need to obtain a license for ArcGIS to use ArcPy.

There's not really any "raw string"; there are raw string literals, 
which are exactly the string literals marked by a 'r' before the opening quote.

A "raw string literal" is a slightly different syntax for a string literal, 
in which a backslash, \, is taken as meaning "just a backslash" 
(except when it comes right before a quote that would otherwise terminate 
the literal) -- no "escape sequences" to represent newlines, tabs, backspaces, 
form-feeds, and so on. In normal string literals, each backslash must be 
doubled up to avoid being taken as the start of an escape sequence.

"""
#%%
import arcpy, numpy

inRaster = r"C:\tmp\RastersArray.gdb\InRaster"
inRaster2 = r"C:\tmp\RastersArray.gdb\InRaster2"

##Get properties of the input raster
inRasterDesc = arcpy.Describe(inRaster)

#coordinates of the lower left corner
rasXmin = inRasterDesc.Extent.Xmin
rasYmin = inRasterDesc.Extent.Ymin

# Cell size, raster size
rasMeanCellHeight = inRasterDesc.MeanCellHeight
rasMeanCellWidth = inRasterDesc.MeanCellWidth
rasHeight = inRasterDesc.Height
rasWidth = inRasterDesc.Width

##Calculate coordinates basing on raster properties
#create numpy array of coordinates of cell centroids
def rasCentrX(rasHeight, rasWidth):
    coordX = rasXmin + (0.5*rasMeanCellWidth + rasWidth)
    return coordX
inRasterCoordX = numpy.fromfunction(rasCentrX, (rasHeight,rasWidth)) #numpy array of X coord

def rasCentrY(rasHeight, rasWidth):
    coordY = rasYmin + (0.5*rasMeanCellHeight + rasHeight)
    return coordY
inRasterCoordY = numpy.fromfunction(rasCentrY, (rasHeight,rasWidth)) #numpy array of Y coord

#combine arrays of coordinates (although array for Y is before X, dstack produces [X, Y] pairs)
inRasterCoordinates = numpy.dstack((inRasterCoordY,inRasterCoordX))


##Raster conversion to NumPy Array
#create NumPy array from input rasters 
inRasterArrayTopLeft = arcpy.RasterToNumPyArray(inRaster)
inRasterArrayTopLeft2 = arcpy.RasterToNumPyArray(inRaster2)

#flip array upside down - then lower left corner cells has the same index as cells in coordinates array
inRasterArray = numpy.flipud(inRasterArrayTopLeft)
inRasterArray2 = numpy.flipud(inRasterArrayTopLeft2)


# combine coordinates and value
inRasterFullArray = numpy.dstack((inRasterCoordinates, inRasterArray.T))

#add values from second raster
rasterValuesArray = numpy.dstack((inRasterFullArray, inRasterArray2.T))
