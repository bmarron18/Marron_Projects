# -*- coding: utf-8 -*-
"""
Title:			DataProcessing1
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		05 Mar 2016

"""

#%% Import packages

import numpy as np
import cPickle


#%% Import OptDigits data

# import the files
optdigits_tr = np.loadtxt("/home/bmarron/Desktop/optdigits.train", delimiter=",")
optdigits_te = np.loadtxt("/home/bmarron/Desktop/optdigits.test", delimiter=",")

# Save raw data
with open("optdigits_tr.pkl", 'wb') as f:
    cPickle.dump(optdigits_tr, f, protocol=2)
    
with open("optdigits_te.pkl", 'wb') as f:
    cPickle.dump(optdigits_te, f, protocol=2)    


#%% Confirm data content with info sheet about data
#0=376, 1=389, 2=380, 9=382 

test0 = np.where(optdigits_tr[:, 64] == 0)
test0 = list(test0[0])

test1 = np.where(optdigits_tr[:, 64] == 1)
test1 = list(test1[0])

test2 = np.where(optdigits_tr[:, 64] == 2)
test2 = list(test2[0])


test9 = np.where(optdigits_tr[:, 64] == 9)
test9 = list(test9[0])



#%% Split training dataset(tr_d) and test dataset(te_d) into features and class

tr_d_X, tr_d_y = optdigits_tr[:,0:64], optdigits_tr[:, 64]
te_d_X, te_d_y = optdigits_te[:,0:64], optdigits_te[:, 64]


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

#%%
#Reload the processed data, if needed    
tr_d_X = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/tr_d_X.pkl","rb"))

#Reload the processed data    
tr_d_y = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/tr_d_y.pkl","rb"))

#Reload the processed data    
te_d_X = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/te_d_X.pkl","rb"))

#Reload the processed data    
te_d_y = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/te_d_y.pkl","rb"))


#%% 
