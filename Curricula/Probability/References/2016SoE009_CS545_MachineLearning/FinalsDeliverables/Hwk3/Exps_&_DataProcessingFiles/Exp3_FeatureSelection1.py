# -*- coding: utf-8 -*-
"""
Title:			Experiment3 -- Feature Selection 1
Project Descriptor:	HW3 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		09 Feb 2016

"""
#%% Import packages 

import numpy as np
import cPickle
import pandas as pd

from sklearn import svm
from sklearn.metrics import accuracy_score


#%% Create random oder of features
random_order=np.random.permutation(np.arange(57))

len(random_order)
Out[126]: 57

random_order
Out[5]: 
array([ 6, 42, 31, 38,  1, 17, 23, 46,  2, 27, 21, 44, 16, 48, 52, 28,  4,
        0, 10, 18, 55, 19, 47, 51, 34, 33,  3, 53, 56, 40, 29, 11, 22, 49,
       13, 24, 37, 50, 45, 26,  9, 32, 20, 43, 25, 30, 12,  5, 15, 35,  8,
       39,  7, 14, 54, 41, 36])
       

#%% Reload test data
    
te_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/te_d.pkl","rb"))

# Extract (unzip)
te_d_features_scaled, te_d_classification=zip(*te_d)

# Make 'em lists
te_d_features_scaled = list(te_d_features_scaled)
te_d_classification = list(te_d_classification)
       

#%% Random features m=1

# Reload training data
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

# Make 'em lists
tr_d_features_scaled = list(tr_d_features_scaled)
tr_d_classification = list(tr_d_classification)
test = tr_d_features_scaled

# Purge all feature data but for m=1
for i in range(len(test)):
    for j,k in enumerate(test[i]):
        if not (j==6):
            test[i][j]=0


# Train SVM on tr_d w/ C=0.6
# Set probability = False to get accuracy, precision, recall stats
exp2_svm = svm.SVC(kernel='linear', C=0.6, probability=False)
exp2_svm.fit(test, tr_d_classification)


# Set to svm.predict() for stats
y_pred = exp2_svm.predict(te_d_features_scaled)[:]
y_true = te_d_classification

print accuracy_score(y_true, y_pred)

#%% Random features m=1,2

# Reload training data
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

# Make 'em lists
tr_d_features_scaled = list(tr_d_features_scaled)
tr_d_classification = list(tr_d_classification)
test = tr_d_features_scaled

# Purge all feature data but for m=1,2
for i in range(len(test)):
    for j,k in enumerate(test[i]):
        if not (j==42 or j==6):
            test[i][j]=0

# Train SVM on tr_d w/ C=0.6
# Set probability = False to get accuracy, precision, recall stats
exp2_svm = svm.SVC(kernel='linear', C=0.6, probability=False)
exp2_svm.fit(test, tr_d_classification)


# Set to svm.predict() for stats
y_pred = exp2_svm.predict(te_d_features_scaled)[:]
y_true = te_d_classification

print accuracy_score(y_true, y_pred)

#%% Random features m=1,2,3

# Reload training data
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

# Make 'em lists
tr_d_features_scaled = list(tr_d_features_scaled)
tr_d_classification = list(tr_d_classification)
test = tr_d_features_scaled

# Purge all feature data but for m=1,2,3
for i in range(len(test)):
    for j,k in enumerate(test[i]):
        if not (j==31 or j==42 or j==6):
            test[i][j]=0

# Train SVM on tr_d w/ C=0.6
# Set probability = False to get accuracy, precision, recall stats
exp2_svm = svm.SVC(kernel='linear', C=0.6, probability=False)
exp2_svm.fit(test, tr_d_classification)

# Set to svm.predict() for stats
y_pred = exp2_svm.predict(te_d_features_scaled)[:]
y_true = te_d_classification

print accuracy_score(y_true, y_pred)

#%% Cell for rapid processing of the remaining features (a running sequence)
    #Highest wgt features m=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,
    #23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46
    #47,48,49,50,51,52,53,54,55,56,57

# Reload
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

# Make 'em lists
tr_d_features_scaled = list(tr_d_features_scaled)
tr_d_classification = list(tr_d_classification)
test = tr_d_features_scaled

# Purge all but ...
for i in range(len(test)):
    for j,k in enumerate(test[i]):
        if not (j==36 or j==41 or j==54 or j==14 or j==7 or j==39 or j==8 or j==35 or j==15 or j==5 or j==12 or j==30 or j==25 or j==43 or j==20 or j==32 or j==9 or j==26 or j==45 or j==50 or j==37 or j==24 or j==13 or j==49 or j==22 or j==11 or j==29 or j==40 or j==56 or j==53 or j==3 or j==33 or j==34 or j==51 or j==47 or j==19 or j==55 or j==18 or j==10 or j==0 or j==4 or j==28 or j==52 or j==48 or j==16 or j==44 or j==21 or j==27 or j==2 or j==46 or j==23 or j==17 or j==1 or j==38 or j==31 or j==42 or j==6):
            test[i][j]=0

# Train SVM on tr_d w/ C=0.6
# Set probability = False to get accuracy, precision, recall stats
exp2_svm = svm.SVC(kernel='linear', C=0.6, probability=False)
exp2_svm.fit(test, tr_d_classification)


# Set to svm.predict() for stats
y_pred = exp2_svm.predict(te_d_features_scaled)[:]
y_true = te_d_classification

print accuracy_score(y_true, y_pred)