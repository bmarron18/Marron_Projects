# -*- coding: utf-8 -*-
"""
Title:			DataProcessing2
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		05 Mar 2016

"""

#%% Import packages
import random
import numpy as np
import cPickle

from sklearn.utils.fixes import bincount
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.utils.extmath import row_norms, squared_norm

from sklearn.metrics import confusion_matrix

#%%Reload the processed data
 
tr_d_X = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/tr_d_X.pkl","rb"))
 
tr_d_y = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/tr_d_y.pkl","rb"))

te_d_X = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/te_d_X.pkl","rb"))

te_d_y = cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk5/DataFiles/InputData/Processed/te_d_y.pkl","rb"))

#%%
#Check the shape of tr_d and te_d
tr_d_X.shape
# (3823, 64)
te_d_X.shape
#(1797, 64)


#%%Generate 4 sets of k=10 random cluster centers
# shape of the centers ==> shape(k, n_features)

np.random.seed(47)
rcc1=np.random.randint(0, 16, (10, 64))

np.random.seed(147)
rcc2=np.random.randint(0, 16, (10, 64))

np.random.seed(247)
rcc3=np.random.randint(0, 16, (10, 64))

np.random.seed(347)
rcc4=np.random.randint(0, 16, (10, 64))

np.random.seed(447)
rcc5=np.random.randint(0, 16, (10, 64))

#%% check; good  for all rccs
k = rcc1.shape[0]
#Out[66]: 10
n_features = rcc1.shape[1]
#Out[137]: 64

#%% First iteration of run (<fill-in> of 5) of k-means for k=10
#for this run <fill-in> = 1

""" 
Step1: enter the rcc<value>
Step2: change rcc<value> as needed in this script
Step3: run this script
Step4: go to DataProcessing3.py
Step5: run 'best_, best_, ...' subscript
Step6: run convergence subscript until convergence
Step7: grab best_sse, ss_sep, and entropy
Step8: at the start of each new clear all EXCEPT data!!

"""


"""
E step of the K-means EM algorithm computes:
    1) the labels (case-to-cluster assignment) and 
    2) the SSE (or 'inertia') for the given samples and centroids
"""


""" change this as needed!!! """
centers=rcc4

k = 10
n_clusters = 10    
n_samples = tr_d_X.shape[0]
#Out[65]: 3823
n_features = tr_d_X.shape[1]
#Out[105]: 64


#Row-wise (squared) Euclidean norm of X; that is, 
#the pre-computed dot-products of vectors in X 
x_squared_norms = row_norms(tr_d_X, squared=True)
x_squared_norms.shape
#Out[79]: (3823,)


#Considering the rows of rcc1 and tr_d_X as vectors, compute
#the distance matrix between each pair of vectors (pairwise distances) as
#squared distances; has shape (n_samples_1, n_samples_2)
#
"""change rcc<value>, as needed!!"""
all_distances = euclidean_distances(rcc4, tr_d_X, x_squared_norms, squared=True)
all_distances.shape
#Out[78]: (10, 3823)

#set an empty array for labels. A label is the code or index of the centroid 
#that the ith observation is closest to; that is, the case-to-centroid assignment
labels = np.empty(n_samples, dtype=np.int32)
labels.fill(-1)

#set an initial array for minimum distances
#w/ distances set to infinity so that 
#computed distances on the first run will be less 
mindist = np.empty(n_samples)
mindist.fill(np.infty)

#set an empty array for distances
distances = np.zeros(shape=(n_samples,), dtype=np.float64)


for center_id in range(k):
    dist = all_distances[center_id]
    labels[dist < mindist] = center_id
    mindist = np.minimum(dist, mindist)

#sum of squared distances to the closest centroid 
#for all observations in the training set
sse = mindist.sum()

#update distances to the minimums
distances[:] = mindist


"""
M step of the K-means EM algorithm computes:
    1) the new (raw) cluster centers (centroids) 
    2) the new cluster centers (as means)
"""

#compute the new cluster centers (raw)
for i in range(n_samples):
    for j in range(n_features):
        centers[labels[i], j] += tr_d_X[i, j]


# Count the number of occurrences of each value in labels; 
#minlength is specified so there will be at least this number of bins 
#Each bin gives the number of occurrences of its index value in x.

n_samples_in_cluster = bincount(labels, minlength=n_clusters)

#compute the new cluster centers (as means)
centers /= n_samples_in_cluster[:, np.newaxis]



#%%
#check shape of new clusters
#should be shape ==> (n_clusters, n_features)
centers.shape
#Out[4]: (10, 64)