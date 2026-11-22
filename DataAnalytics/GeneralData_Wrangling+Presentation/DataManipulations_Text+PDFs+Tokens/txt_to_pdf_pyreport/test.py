# Define a set of tightly-ranged bounding coordinates to extract precip,
#tempmax, and tempmin daily data from the University of Idaho OPeNDAP 
#server; a massive repository of NetCDF .nc files.
#Coord set is for 31 specific "weather stations" selected by SWAT 
#for use with 31 subbasins in a model of the Clackamas River, OR.
#Daily weather data from HadGEM2 general climate model; 2086-2099

'''
helpful:
http://docs.opendap.org/index.php/QuickStart

repository selection sequence:
http://thredds.northwestknowledge.net:8080/thredds/catalog.html
http://thredds.northwestknowledge.net:8080/thredds/nw.csc.is.catalog.html
http://thredds.northwestknowledge.net:8080/thredds/nw.csc.climate.html
http://thredds.northwestknowledge.net:8080/thredds/catalog/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/catalog.html
http://thredds.northwestknowledge.net:8080/thredds/catalog/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/macav2livneh/catalog.html
http://thredds.northwestknowledge.net:8080/thredds/catalog/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/macav2livneh/HadGEM2-ES365/catalog.html
http://thredds.northwestknowledge.net:8080/thredds/catalog/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/macav2livneh/HadGEM2-ES365/catalog.html?dataset=NWCSC_IS_ALL_SCAN/macav2livneh/HadGEM2-ES365/macav2livneh_pr_HadGEM2-ES365_r1i1p1_rcp85_2086_2099_CONUS_daily.nc
'''

'''
code works when see this output:
opened url for 1x time
/home/bmarron/Desktop/25
lat lon data collected 
coords found
coords df created
wrote ws coords
...
'''


'''
Original code by Madeline Steele, Mike Psaris, GIS Programming 2012
Modified Bruce Marron, Portland State University, May 2016
'''



#%% SWAT-selcted weather stations from the 352 weather stations offered by
# by PRISM; sorted min to max
# 
L=[30,27,25,51,52,77,100,96,122,95,120,164,147,143,166,175,198,171,218,209,
190,214,212,234,237,261,276,281,326,328,301]
L = sorted(L)


#%% the packages required for this script

import csv
import os
import numpy
import pydap    # Import the OPenDAP python library
from pydap.client import open_url
from pydap.client import open_dods
    #import pandas as pd ??
import pydataframe as df
import datetime as dt

#%%
# Have each weather station tightly bounded so that only one 
# "weather station" is pulled from the .nc database (tricky!)
# Save the tightly-bounded coords as .csv, with the following fields:
# ['gage_id', 'lon_max', 'lon_min', 'lat_max', 'lat_min']
# use ==> "Clackamas_ws_360_HadGEM2.csv"

output_path = "/home/bmarron/Desktop"
output_array = numpy.array([])

#%%
# HadGEM2 years in this .nc file are 2086 to 2099
# The .nc file is named with the prefix "pr", 
#but the variables in the dataset use longer names
var_name_list = 'precipitation'

#Some of the variable names are the same.  I've changed them for more clarity when they are written to text files.
col_header_list = 'precipitation'


# Read in the list of XY min and max for each (buffered) polygon from QGIS
xy_bounds = "/home/bmarron/Desktop/Clackamas_ws_360_HadGEM2.csv"
reader = csv.reader(open(xy_bounds))
headers = reader.next() # This skips the headers row


#%%  Run script in one-shot from here
# Loop through each row (watershed bounding box) 
# and get the coordinates from table

#Determine the index values of the weather station 
#coordinates using the the "precipitation" variable.  
#The indices are the same for all variables in this HadGEM2 series.     

url = ("http://thredds.northwestknowledge.net:8080/thredds/dodsC/NWCSC_INTEGRATED_SCENARIOS_ALL_CLIMATE/macav2livneh/HadGEM2-ES365/macav2livneh_pr_HadGEM2-ES365_r1i1p1_rcp85_2086_2099_CONUS_daily.nc") 
dataset = open_url(url)
print "opened url for 1x"

for row in reader:
    gage_id = row[0]
    lon_max = float(row[1]) # They need to be converted from string type
    lon_min = float(row[2])
    lat_max = float(row[3])
    lat_min = float(row[4])
    lat_list = []
    lon_list = []
    id_list = []

    #Unique identifier for each grid point
    dataset_num = 1

    # Create an output folder for each gage
    output_folder = (output_path + "/" + gage_id) 
    print output_folder 
    if not os.path.exists(output_folder):  # Check to see if output folder has been created. If not, make it.
        os.makedirs(output_folder)

    lat = dataset['lat'] # Accesses the latitude array
    lon = dataset['lon'] # Accesses the longitude array
    lat_ind = numpy.arange(0,(len(lat[:])))
    lon_ind = numpy.arange(0,(len(lon[:])))
    sub_lat_ind = lat_ind[(lat > lat_min) & (lat < lat_max)]
    sub_lon_ind = lon_ind[(lon > lon_min) & (lon < lon_max)]
    print "lat lon data collected "

    #For each grid point, a time series of all the variables are written to a tab-delimited text file.  
    for lat_index in sub_lat_ind:
        for lon_index in sub_lon_ind:
            lat_list.append(float(lat[lat_index]))
            lon_list.append(float(lon[lon_index]))
            id_list.append(dataset_num)
            dataset_num += 1
    print "coords found"

    coords = df.DataFrame({"ID": id_list, "LAT": lat_list, "LON": lon_list})
    print "coords df created "
    
    file_name = output_path + "/" + str(gage_id) + "/" + "ws_Coords.txt"
    with open(file_name, 'wb') as f:
        write_data = f.write(str(coords))
    f.closed
    print "wrote ws coords"
    
