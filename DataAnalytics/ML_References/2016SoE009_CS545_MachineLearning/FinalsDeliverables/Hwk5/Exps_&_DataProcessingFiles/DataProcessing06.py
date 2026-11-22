# -*- coding: utf-8 -*-
"""
Title:			DataProcessing1
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		06 Mar 2016

"""

#%% From Experiment 1 : rcc4 is the best
# Run rcc4 (use DataProcessing2.py and DataProcessing3.py)
# then follow this script

#zip the results
test = zip(tr_d_y, labels)

#get the unique labels
np.unique(labels)
#Out[190]: array([0, 2, 3, 4, 5, 6, 7, 8, 9])

#%%
""" Class = 0 """
#%% Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 0 and b == 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[193]: 371

# assign cluster center label = 0 ==> class 0

#%%
""" Class = 1 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 1  and b == 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[202]: 237

# assign cluster center label = 7 ==> class 1

#%%
""" Class = 2 """
#%%
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 2 and b == 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[213]: 263
#62 for 0
#5 for 2
#19 for 4

# assign cluster center label = 7 ==> class 2


#%%
""" Class = 3 """
#%% Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 3 and b == 8):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[221]: 352
# assign cluster center label = 8 ==> class 3

#%%
""" Class = 4 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 4 and b == 5):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#3 ==> 106
#Out[227]: 250
# assign cluster center label = 5 ==> class 4


#%%
""" Class = 5 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 5 and b == 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#3 ==> 49
#Out[237]: 253
# assign cluster center label = 9 ==> class 5



#%%
""" Class = 6 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 6  and b == 6):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[239]: 344
# assign cluster center label = 6 ==> class 6


#%%
""" Class = 7 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 7  and b == 4):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[244]: 336
# assign cluster center label = 4 ==> class 7


#%%
""" Class = 8 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 8 and b == 2):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
# 7 ==> 108
#Out[253]: 205
# assign cluster center label = 2 ==> class 8



#%%
""" Class = 9 """
#%%Find the highest by subbing in values for 'b == <value>' 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 9 and b == 8):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
# 7 ==> 108
#Out[19]: 249
# assign cluster center label = 8 ==> class 9

