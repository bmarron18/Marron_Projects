# -*- coding: utf-8 -*-
"""
Title:			DataProcessing1
Project Descriptor:	HW4 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		20 Feb 2016

"""

#%% Import packages

import numpy as np
import cPickle
import urllib
from sklearn.cross_validation import train_test_split


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
#Count number of cases for each class
#Check the demarcation line

spambase_id1=np.where(spambase[:, 57] == 1)
spambase_id1 = list(spambase_id1[0])
len(spambase_id1)
#Out[22]: 1813
spambase[1812][57]
#Out[8]: 1.0
spambase[1813][57]
#Out[9]: 0.0


spambase_id0=np.where(spambase[:, 57] == 0)
spambase_id0 = list(spambase_id0[0])
len(spambase_id0)
#Out[25]: 2788

#%% Permute original database, 2x

spambase_shuffled = np.random.permutation(spambase)
spambase_shuffled = np.random.permutation(spambase_shuffled)
spambase_shuffled.shape
#Out[33]: (4601, 58)

#%% Define X, y (features, class)
#Create training dataset(tr_d) and test dataset(te_d); split spambase 50:50

X, y = spambase_shuffled[:,0:57], spambase_shuffled[:, 57]
tr_d_X, te_d_X, tr_d_y, te_d_y = train_test_split(X, y, test_size=0.50, random_state=74)


#%%Save all tr_d and te_d separately

# Save tr_d_X
with open("tr_d_X.pkl", 'wb') as f:
    cPickle.dump(tr_d_X, f, protocol=2)
    
# Save tr_d_y
with open("tr_d_y.pkl", 'wb') as f:
    cPickle.dump(tr_d_y, f, protocol=2)    
    
# Save te_d_X
with open("te_d_X.pkl", 'wb') as f:
    cPickle.dump(te_d_X, f, protocol=2) 

# Save te_d_y
with open("te_d_y.pkl", 'wb') as f:
    cPickle.dump(te_d_y, f, protocol=2)


#Reload the processed data, if needed    
tr_d_X = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk4/DataFiles/InputData/Processed/tr_d_X.pkl","rb"))

#Reload the processed data    
tr_d_y = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk4/DataFiles/InputData/Processed/tr_d_y.pkl","rb"))

#Reload the processed data    
te_d_X = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk4/DataFiles/InputData/Processed/te_d_X.pkl","rb"))

#Reload the processed data    
te_d_y = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk4/DataFiles/InputData/Processed/te_d_y.pkl","rb"))


#%%Compute prior probability for each class in the training data

prob_spam=sum(list(tr_d_y))/len(list(tr_d_y))
round(prob_spam,5)
#Out[11]: 0.40696

prob_notspam = 1-prob_spam
round(prob_notspam,5)
#Out[12]: 0.59304

#%% 
