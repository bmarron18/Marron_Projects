# -*- coding: utf-8 -*-
"""
Title:			Experiment1 -- Cross-Validation
Project Descriptor:	HW3 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		04 Feb 2016

"""
#%% Import packages

import numpy as np
import cPickle
from sklearn import cross_validation
from sklearn import svm

#%% Training Data

# Reload
tr_d = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk3/DataFiles/InputData/Processed/tr_d.pkl","rb"))
    
# Extract (unzip)
tr_d_features_scaled, tr_d_classification=zip(*tr_d)

#%% Peform 10-fold cross-validation on linear SVM, C=0.0
exp1_1 = svm.SVC(kernel='linear', C=0.0)
exp1_1_scores = cross_validation.cross_val_score(exp1_1, tr_d_features_scaled, tr_d_classification, cv=10)


#Note ==> Error for C=0 !
#File "sklearn/svm/libsvm.pyx", line 187, in sklearn.svm.libsvm.fit (sklearn/svm/libsvm.c:2098)
ValueError: C <= 0

#%% Peform 10-fold cross-validation on linear SVM, C=0.1
exp1_2 = svm.SVC(kernel='linear', C=0.1)
exp1_2_scores = cross_validation.cross_val_score(exp1_2, tr_d_features_scaled, tr_d_classification, cv=10)


exp1_2_scores                                              
array([ 0.90659341,  0.91758242,  0.86187845,  0.94475138,  0.91712707,
        0.94475138,  0.96132597,  0.90055249,  0.92265193,  0.93370166])

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_2_scores.mean(), exp1_2_scores.std() * 2))
Accuracy: 0.9211 (+/- 0.05)

#%% Perform 10-fold cross-validation on linear SVM, C=0.2
exp1_3 = svm.SVC(kernel='linear', C=0.2)
exp1_3_scores = cross_validation.cross_val_score(exp1_3, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_3_scores.mean(), exp1_3_scores.std() * 2))
Accuracy: 0.9233 (+/- 0.05)


print exp1_3_scores  
[ 0.90659341  0.91758242  0.87845304  0.95027624  0.91160221  0.94475138
  0.96132597  0.90607735  0.92265193  0.93370166]
  
#%% Perform 10-fold cross-validation on linear SVM, C=0.3
exp1_4 = svm.SVC(kernel='linear', C=0.3)
exp1_4_scores = cross_validation.cross_val_score(exp1_4, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_4_scores.mean(), exp1_4_scores.std() * 2))
Accuracy: 0.9216 (+/- 0.05)

print exp1_4_scores  
[ 0.90659341  0.91758242  0.87845304  0.95027624  0.91160221  0.94475138
  0.96132597  0.90607735  0.92265193  0.93370166]

#%% Perform 10-fold cross-validation on linear SVM, C=0.4
exp1_5 = svm.SVC(kernel='linear', C=0.4)
exp1_5_scores = cross_validation.cross_val_score(exp1_5, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_5_scores.mean(), exp1_5_scores.std() * 2))
print exp1_5_scores

Accuracy: 0.9239 (+/- 0.05)
[ 0.90659341  0.92307692  0.86740331  0.95027624  0.91160221  0.95027624
  0.96685083  0.90055249  0.93370166  0.9281768 ]
  
#%% Perform 10-fold cross-validation on linear SVM, C=0.5
exp1_6 = svm.SVC(kernel='linear', C=0.5)
exp1_6_scores = cross_validation.cross_val_score(exp1_6, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_6_scores.mean(), exp1_6_scores.std() * 2))
print exp1_6_scores

Accuracy: 0.9244 (+/- 0.05)
[ 0.90659341  0.92307692  0.86740331  0.95027624  0.91712707  0.95027624
  0.96685083  0.90055249  0.93370166  0.9281768 ]

#%% Perform 10-fold cross-validation on linear SVM, C=0.6
exp1_7 = svm.SVC(kernel='linear', C=0.6)
exp1_7_scores = cross_validation.cross_val_score(exp1_7, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_7_scores.mean(), exp1_7_scores.std() * 2))
print exp1_7_scores

Accuracy: 0.9261 (+/- 0.05)
[ 0.90659341  0.92307692  0.86740331  0.95027624  0.92265193  0.95027624
  0.96685083  0.91160221  0.93370166  0.9281768 ]  


#%% Perform 10-fold cross-validation on linear SVM, C=0.7
exp1_8 = svm.SVC(kernel='linear', C=0.7)
exp1_8_scores = cross_validation.cross_val_score(exp1_8, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_8_scores.mean(), exp1_8_scores.std() * 2))
print exp1_8_scores

Accuracy: 0.9239 (+/- 0.05)
[ 0.9010989   0.92307692  0.86740331  0.95027624  0.92265193  0.94475138
  0.96685083  0.91160221  0.92265193  0.9281768 ]

#%% Perform 10-fold cross-validation on linear SVM, C=0.8
exp1_9 = svm.SVC(kernel='linear', C=0.8)
exp1_9_scores = cross_validation.cross_val_score(exp1_9, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_9_scores.mean(), exp1_9_scores.std() * 2))
print exp1_9_scores

Accuracy: 0.9227 (+/- 0.05)
[ 0.9010989   0.92307692  0.86740331  0.95027624  0.91160221  0.94475138
  0.96685083  0.90607735  0.9281768   0.9281768 ]

#%% Perform 10-fold cross-validation on linear SVM, C=0.9
exp1_10 = svm.SVC(kernel='linear', C=0.9)
exp1_10_scores = cross_validation.cross_val_score(exp1_10, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_10_scores.mean(), exp1_10_scores.std() * 2))
print exp1_10_scores

Accuracy: 0.9216 (+/- 0.05)
[ 0.9010989   0.92307692  0.86740331  0.95027624  0.90607735  0.94475138
  0.96685083  0.90607735  0.92265193  0.9281768 ]

#%% Perform 10-fold cross-validation on linear SVM, C=1.0
exp1_11 = svm.SVC(kernel='linear', C=1.0)
exp1_11_scores = cross_validation.cross_val_score(exp1_11, tr_d_features_scaled, tr_d_classification, cv=10)

#The mean score and the 95% confidence interval of the score estimate 
print("Accuracy: %0.4f (+/- %0.2f)" % (exp1_11_scores.mean(), exp1_11_scores.std() * 2))
print exp1_11_scores

Accuracy: 0.9211 (+/- 0.05)
[ 0.90659341  0.93406593  0.86740331  0.95027624  0.90607735  0.94475138
  0.96685083  0.90055249  0.92265193  0.91160221]  