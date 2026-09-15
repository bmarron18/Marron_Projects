# -*- coding: utf-8 -*-
"""
Title:			DataProcessing2
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		05 Mar 2016

"""

#%% 

#%% After running rcc4 (best run for Experiment 1), use the 'best_centers'
#to assign each test case to the closest cluster class
# classification here is a single k-means run; no iteration;
# a single E step

#clusters from rcc4
centers=best_centers

k = 10
n_clusters = 10    
n_samples = te_d_X.shape[0]
#Out[21]: (1797,)
n_features = te_d_X.shape[1]
#Out[105]: 64


#Row-wise (squared) Euclidean norm of X; that is, 
#the pre-computed dot-products of vectors in X 
x_squared_norms = row_norms(te_d_X, squared=True)
x_squared_norms.shape
#Out[21]: (1797,)

#%%

#Considering the rows of rcc1 and tr_d_X as vectors, compute
#the distance matrix between each pair of vectors (pairwise distances) as
#squared distances; has shape (n_samples_1, n_samples_2)

all_distances = euclidean_distances(centers, te_d_X, x_squared_norms, squared=True)
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



#%%
