# -*- coding: utf-8 -*-
"""
Title:			DataProcessing08
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		06 Mar 2016

"""
#%% from the OptDigits info sheet
"""
	Class: No of examples in testing set
	0:  178
	1:  182
	2:  177
	3:  183
	4:  181
	5:  182
	6:  181
	7:  179
	8:  174
	9:  180
 
 """


#%% From Experiment 1 : rcc4 is the best
# Run rcc4 (use DataProcessing2.py and DataProcessing3.py)
# Run a single E step to assign te_d_X to 'best_center' clusters (use
# DataProcessing7.py )
#now follow this script

#zip the results
test = zip(te_d_y, labels)

#get the unique labels
np.unique(labels)
#Out[190]: array([0, 2, 3, 4, 5, 6, 7, 8, 9])
#%%
#%%
""" Class 0 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 0 and b == 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]: 176

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 0 and b != 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 2

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 0 and b == 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 10

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 0 and b != 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1609

#%%
#%%
""" Class 1 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 1 and b == 1):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:0

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 1 and b != 1):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 182

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 1 and b == 1):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 0

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 1 and b != 1):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1615



#%%
#%%
""" Class 2 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 2 and b == 2):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:3

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 2 and b != 2):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 174

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 2 and b == 2):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 128

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 2 and b != 2):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1492



#%%
#%%
""" Class 3 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 3 and b == 3):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:2

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 3 and b != 3):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 181

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 3 and b == 3):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 131

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 3 and b != 3):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1483

#%%
#%%
""" Class 4 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 4 and b == 4):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:1

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 4 and b != 4):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 180

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 4 and b == 4):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 152

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 4 and b != 4):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1464


#%%
#%%
""" Class 5 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 5 and b == 5):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:0

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 5 and b != 5):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 182

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 5 and b == 5):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 187

#%% False Negatives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 5 and b != 5):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1428

#%%
#%%
""" Class 6 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 6 and b == 6):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:173

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 6 and b != 6):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 8

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 6 and b == 6):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 8

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 6 and b != 6):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1608


#%%
#%%
""" Class 7 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 7 and b == 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:2

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 7 and b != 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 177

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 7 and b == 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 336

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 7 and b != 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1282

#%%
#%%
""" Class 8 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 8 and b == 8):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:5

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 8 and b != 8):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 169

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 8 and b == 8):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 382

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 8 and b != 8):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1295


#%%
#%%
""" Class 9 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 9 and b == 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:0

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 9 and b != 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 180

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 9 and b == 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 155

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 9 and b != 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1462