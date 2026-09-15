# -*- coding: utf-8 -*-
"""
Title:			DataProcessing11
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


#%% From Experiment 2 : rcc4 is the best
# Run rcc4 (use DataProcessing4.py and DataProcessing5.py)
# Run a single E step to assign te_d_X to 'best_center' clusters (use
# DataProcessing9.py )
#now follow this script

#zip the results
test = zip(te_d_y, labels)

#get the unique labels
np.unique(labels)
#array([ 0,  1,  2,  4,  5,  6,  7,  8,  9, 10, 11, 13, 14, 19, 20, 21, 22,
#       23, 24, 25, 26, 27, 28])
#%%
#%%
""" Class 0 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 0 and b == 13):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]: 84

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 0 and b != 13):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 94

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 0 and b == 13):
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
    if (a != 0 and b != 13):
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
    if (a == 1 and b == 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:100

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 1 and b != 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 82

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 1 and b == 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 23

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 1 and b != 9):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1592



#%%
#%%
""" Class 2 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 2 and b == 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:59

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 2 and b != 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 118

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 2 and b == 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 20

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 2 and b != 7):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1600



#%%
#%%
""" Class 3 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 3 and b == 27):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:112

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 3 and b != 27):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 71

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 3 and b == 27):
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
    if (a != 3 and b != 27):
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
    if (a == 4 and b == 19):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:76

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 4 and b != 19):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 105

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 4 and b == 19):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 2

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 4 and b != 19):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1614


#%%
#%%
""" Class 5 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 5 and b == 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:100

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 5 and b != 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 82

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 5 and b == 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 3

#%% False Negatives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 5 and b != 0):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1612

#%%
#%%
""" Class 6 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 6 and b == 26):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:92

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 6 and b != 26):
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
    if (a != 6 and b == 26):
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
    if (a != 6 and b != 26):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1616


#%%
#%%
""" Class 7 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 7 and b == 23):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:108

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 7 and b != 23):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 71

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 7 and b == 23):
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
    if (a != 7 and b != 23):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1606

#%%
#%%
""" Class 8 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 8 and b == 10):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:116

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 8 and b != 10):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 58

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 8 and b == 10):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 14

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 8 and b != 10):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1609


#%%
#%%
""" Class 9 """
#%% True Positives 
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 9 and b == 20):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[25]:79

#%%True Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a == 9 and b != 20):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[26]: 101

#%% False Positives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 9 and b == 20):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[28]: 21

#%% False Negatives
assign =[]
for i, (a, b) in enumerate(test):
    if (a != 9 and b != 20):
        c = 1
        assign.append(c)
    else:
        c = 0
        assign.append(c)
        
sum(assign)
#Out[31]: 1596

#%%