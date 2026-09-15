# -*- coding: utf-8 -*-
"""
Title:			Experiment1 -- Classification
Project Descriptor:	HW3 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		05 Feb 2016

"""
#%% Import packages

import numpy as np
import cPickle
import pandas as pd

from sklearn import svm
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.metrics import confusion_matrix, classification_report


#%%Training Data

# Reload
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

#%% Test Data
    
# Reload
te_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/te_d.pkl","rb"))

# Extract (unzip)
te_d_features_scaled, te_d_classification=zip(*te_d)

#%% Train SVM on tr_d w/ C=0.6
# Set probability = False to get accuracy, precision, recall stats
# Set probability = True for ROC curve
exp2_svm = svm.SVC(kernel='linear', C=0.6, probability=True)
exp2_svm.fit(tr_d_features_scaled, tr_d_classification)

# Set to svm.predict() for stats
# Set to svm.predict_proba() for ROC curve
    #w/o [:,1] returns tuples of lower and upper prob
    #w/ [:,1] returns ONLY the upper prob
y_pred = exp2_svm.predict_proba(te_d_features_scaled)[:,1]
y_true = te_d_classification

#%% SVM set to probability = False
print accuracy_score(y_true, y_pred)
print precision_score(y_true, y_pred)
print recall_score(y_true, y_pred)

0.926600441501
0.923925027563
0.929046563193

print confusion_matrix(y_true, y_pred)
[[841  69]
 [ 64 838]]

 
#%% SVM set to probability = True
fpr, tpr, thresholds = roc_curve(y_true, y_pred)
len(thresholds)
#Out[60]: 310

ROC_data = zip(fpr, tpr)

# Save ROC data
# See Exp1_Classification_ROC.py for making ROC curve in ggplot 
with open("ROCcurve_data.pkl", 'wb') as f:
    cPickle.dump(ROC_data, f, protocol=2)

