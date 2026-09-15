# -*- coding: utf-8 -*-
"""
Title:			DataProcessing3
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		06 Mar 2016

"""

#%% Import packages
import random
import numpy as np
import cPickle

from sklearn.utils.fixes import bincount
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.utils.extmath import row_norms, squared_norm

from sklearn.metrics import confusion_matrix


#%% Iterate k-means with EACH random cluster center (run this 5x)

#outputs from rcc1, first iteration
best_labels = labels.copy()
best_sse = sse.copy()
best_centers = centers.copy()

#%%
for i in range(1):
    centers_old = centers.copy()
        
"""
E step of the K-means EM algorithm computes:
    1) the labels (case-to-cluster assignment) and 
    2) the SSE (or 'inertia') for the given samples and centroids
"""
all_distances = euclidean_distances(centers_old, tr_d_X, x_squared_norms, squared=True)

for center_id in range(k):
    dist = all_distances[center_id]
    labels[dist <= distances] = center_id
    distances = np.minimum(dist, distances)

sse = distances.sum()
    

"""
M step of the K-means EM algorithm computes:
    1) the new (raw) cluster centers (centroids) 
    2) the new cluster centers (as means)
"""

#compute the new cluster centers (raw)
for i in range(n_samples):
    for j in range(n_features):
        centers[labels[i], j] += tr_d_X[i, j]

n_samples_in_cluster = bincount(labels, minlength=n_clusters)
centers /= n_samples_in_cluster[:, np.newaxis]
   
if sse < best_sse:
    best_labels = labels.copy()
    best_centers = centers.copy()
    best_sse = sse

shift = squared_norm(centers_old - centers)

if shift <= 1e-2:
    print("Converged at iteration %d" % i)


#%% Sum-squared separation

ss_sep = euclidean_distances(best_centers, best_centers, squared=True)
ss_sep.sum()

#%% Entropy of label distribution

def entropy2(labels):
    n_labels = len(labels)
    probs = n_samples_in_cluster.astype(float)/(n_labels)

    ent = 0
    
    for i in probs:
        if i != 0:
            ent -= i * np.log2(i)
    return ent

#%%  Example of convergence from Experiment 1, rcc3
# tracking the shift per run

shifters.append(shift)
shifters
#Out[30]: [9323, 274, 58, 24, 10, 10, 11, 9, 3, 1, 0]    