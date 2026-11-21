# -*- coding: utf-8 -*-
"""
Title:			DataProcessing09
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		06 Mar 2016

"""

#%% From Experiment 2 : rcc4 is the best
# Run rcc4 (use DataProcessing4.py and DataProcessing5.py)
# then follow this script

#zip the results
test = zip(tr_d_y, labels)

#get the unique labels
np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])

#%%
""" Class = 0 """
#%% Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 0 and b == 13):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[36]: 191

# assign cluster center label = 13 ==> class 0

#%%
""" Class = 1 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 1  and b == 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[54]: 233

# assign cluster center label = 9 ==> class 1

#%%
""" Class = 2 """
#%%
np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 2 and b == 28
    ):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[63]: 138

# assign cluster center label = 7 ==> class 2


#%%
""" Class = 3 """
#%% Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 3 and b == 27):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[100]: 213
# assign cluster center label = 27 ==> class 3

#%%
""" Class = 4 """
#%%Find the highest by subbing in values for 'b == <value>' 

np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 4 and b == 19):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)

#Out[115]: 183
# assign cluster center label = 19 ==> class 4


#%%
""" Class = 5 """
#%%Find the highest by subbing in values for 'b == <value>' 

np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 5 and b == 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)

#Out[116]: 213
# assign cluster center label = 0 ==> class 5



#%%
""" Class = 6 """
#%%Find the highest by subbing in values for 'b == <value>' 

np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 6  and b == 26):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[137]: 162
# assign cluster center label = 26 ==> class 6


#%%
""" Class = 7 """
#%%Find the highest by subbing in values for 'b == <value>' 
np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])

assign =[]
for i, (a, b) in enumerate(test):
    if (a == 7  and b == 23):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[155]: 274
# assign cluster center label = 23 ==> class 7


#%%
""" Class = 8 """
#%%Find the highest by subbing in values for 'b == <value>' 
np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 8 and b == 10):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)

#Out[165]: 222
# assign cluster center label = 10 ==> class 8



#%%
""" Class = 9 """
#%%Find the highest by subbing in values for 'b == <value>' 
np.unique(labels)
#Out[24]: array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21,
#    22, 23, 24, 25, 26, 27, 28])
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 9 and b == 28):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)

#Out[180]: 114
# assign cluster center label = 20 ==> class 9

