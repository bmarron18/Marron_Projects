# -*- coding: utf-8 -*-
"""
Title:			DataProcessing
Project Descriptor:	HW3 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		03 Feb 2016

"""

#%% Import packages

import numpy as np
import cPickle
import urllib
from sklearn.preprocessing import scale
from sklearn.preprocessing import StandardScaler


#%% Download UCI spambase data
# https://goo.gl/ to shorten
# https://archive.ics.uci.edu/ml/machine-learning-databases/spambase/spambase.data

url = "https://goo.gl/3DSdcJ"

# Download the file
raw_data = urllib.urlopen(url)
spambase = np.loadtxt(raw_data, delimiter=",")

# Save raw data
with open("spambase.pkl", 'wb') as f:
    cPickle.dump(spambase, f, protocol=2)


#%% Find indices in spambase for spam (=1) and not spam (=0)

spambase_id1=np.where(spambase[:, 57] == 1)
spambase_id1
#Out[39]: (array([   0,    1,    2, ..., 1810, 1811, 1812]),)


spambase_id0=np.where(spambase[:, 57] == 0)
spambase_id0
#Out[40]: (array([1813, 1814, 1815, ..., 4598, 4599, 4600]),)

#%% Count number of cases for each class
np.count_nonzero(spambase_id1)
#Out[29]: 1812

np.count_nonzero(spambase_id0)
#Out[28]: 2788
#%% Permute the not spam (=0) records

spambase0_shuffled = np.random.permutation(spambase[1813:,])
spambase0_shuffled.shape
#Out[42]: (2788, 58)

#%% Permute the spam (=1) records

spambase1_shuffled = np.random.permutation(spambase[0:1812, ])
spambase1_shuffled.shape
#Out[44]: (1812, 58)

#%%Make new subset of spambase with equal number of spam (=1) 
#and not spam (=0) cases

spambase_equal = np.concatenate((spambase1_shuffled, spambase0_shuffled[0:1812]), axis=0)

# Save the processed data
with open("spambase_equal.pkl", 'wb') as f:
    cPickle.dump(spambase_equal, f, protocol=2)

#%%#%%Find indices of cases in spambase_equal where spam (=1) 
#and not spam (=0)

spambase_equal_id1=np.where(spambase_equal[:, 57] == 1)
spambase_equal_id1
#Out[10]: (array([   0,    1,    2, ..., 1809, 1810, 1811]),)


spambase_equal_id0=np.where(spambase_equal[:, 57] == 0)
spambase_equal_id0
#Out[11]: (array([1812, 1813, 1814, ..., 3621, 3622, 3623]),)

#%% Shuffle the spambase_equal data

spambase_equal_shuffled = np.random.permutation(spambase_equal)

#Save the processed data
with open("spambase_equal_shuffled.pkl", 'wb') as f:
    cPickle.dump(spambase_equal_shuffled, f, protocol=2)
    
#Reload the processed data
spambase_equal_shuffled = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/spambase_equal_shuffled.pkl","rb"))



#%% Split spambase_equal_shuffled into training dataset and test dataset

spambase_equal_shuffled_split = np.split(spambase_equal_shuffled, 2)

spambase_equal_shuffled_split[0].shape
#Out[29]: (1812, 58)

spambase_equal_shuffled_split[1].shape
#Out[30]: (1812, 58)

# Save the processed data
with open("spambase_equal_shuffled_split.pkl", 'wb') as f:
    cPickle.dump(spambase_equal_shuffled, f, protocol=2)
    
#Reload the processed data
spambase_equal_shuffled_split = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/spambase_equal_shuffled_split.pkl","rb"))



#%% Create and scale the training dataset
scaler=StandardScaler()
tr_d_features = spambase_equal_shuffled_split[:, 0:56]
tr_d_features_scaled = scaler.fit_transform(tr_d_features)

tr_d_classification = spambase_equal_shuffled_split[:, 57]
tr_d = zip(tr_d_features_scaled, tr_d_classification)

# Save the processed data
with open("tr_d.pkl", 'wb') as f:
    cPickle.dump(tr_d, f, protocol=2)
    
# Reload the processed data
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

#%% Create and scale the test dataset with mean and std from training dataset
scaler=StandardScaler()
te_d_features = spambase_equal_shuffled_split[1][:, 0:57]
te_d_features_scaled = scaler.transform(te_d_features)

te_d_classification = spambase_equal_shuffled_split[1][:, 57]
te_d = zip(te_d_features_scaled, te_d_classification)

# Save the processed data
with open("te_d.pkl", 'wb') as f:
    cPickle.dump(te_d, f, protocol=2)
    
# Reload the processed data
te_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/te_d.pkl","rb"))

# Extract (unzip)
te_d_features_scaled, te_d_classification=zip(*te_d)

