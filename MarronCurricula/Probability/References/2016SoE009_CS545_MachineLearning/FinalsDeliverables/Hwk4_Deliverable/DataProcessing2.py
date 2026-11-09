# -*- coding: utf-8 -*-
"""
Title:			DataProcessing2
Project Descriptor:	HW4 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		21 Feb 2016

"""

#%% Import packages

import numpy as np
import cPickle
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix, classification_report

#%%Reload the processed data

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

#%% mean and std dev of features in the training set

#zip 
tr_d_combo=zip(tr_d_y,tr_d_X)

#select spam(=1) and not spam(=0) feature sets 
tr_d_X_spam = []
for i,j in tr_d_combo:
    if i==1:
        tr_d_X_spam.append(j)
        
tr_d_X_notspam = []
for i,j in tr_d_combo:
    if i==0:
        tr_d_X_notspam.append(j)        
      
#%%compute mean and variance for spam feature set     
tr_d_mu_spam = list(np.mean(tr_d_X_spam, axis=0))
tr_d_var_spam = list(np.var(tr_d_X_spam, axis=0))
tr_d_sigma_spam = list(np.sqrt(tr_d_var_spam))

#look for zero values
tr_d_sigma_spam.index(0.0)
#Out[46]: 31

#correct zero values, if needed
for n,i in enumerate(tr_d_sigma_spam):
    if i==0.0:
        tr_d_sigma_spam[n]=1e-10
#check
tr_d_sigma_spam[31]
#Out[51]: 1e-10



#%%compute mean and variance for not spam feature set  
tr_d_mu_notspam = list(np.mean(tr_d_X_notspam, axis=0))
tr_d_var_notspam = list(np.var(tr_d_X_notspam, axis=0))
tr_d_sigma_notspam = list(np.sqrt(tr_d_var_notspam))


#look for zero values
#correct zero values, not needed
tr_d_sigma_notspam.index(0.0)
#ValueError: 0.0 is not in list


#%%NB for spam class

log_likelihood_spam = []
for i in te_d_X:
    log_p1 = np.log(prob_spam)
    log_p2 = - 0.5 * np.sum(np.log(2. * np.pi * np.asarray(tr_d_sigma_spam)))
    log_p2 -= 0.5 * np.sum(((i - np.asarray(tr_d_mu_spam)) ** 2) / np.asarray(tr_d_sigma_spam))
    log_likelihood_spam.append(log_p1 + log_p2)
    
    
#%%NB for not spam class

log_likelihood_notspam = []
for i in te_d_X:
    log_p1 = np.log(prob_notspam)
    log_p2 = - 0.5 * np.sum(np.log(2. * np.pi * np.asarray(tr_d_sigma_notspam)))
    log_p2 -= 0.5 * np.sum(((i - np.asarray(tr_d_mu_notspam)) ** 2) / np.asarray(tr_d_sigma_notspam))
    log_likelihood_notspam.append(log_p1 + log_p2)
    
#%% Take argmax of NB for spam(=1) and not spam(=0)   
nb = zip(log_likelihood_notspam, log_likelihood_spam)
nb_te_d=np.argmax(nb, axis=1)


#%%Classification metrics

round(accuracy_score(te_d_y, nb_te_d),4)
#Out[22]: 0.7245

round(precision_score(te_d_y, nb_te_d),4)
#Out[23]: 0.7008

round(recall_score(te_d_y, nb_te_d),4)
#Out[24]: 0.4835

confusion_matrix(te_d_y, nb_te_d)
#Out[25]: 
#array([[1243,  181],
#       [ 453,  424]])


