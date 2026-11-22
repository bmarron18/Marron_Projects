# -*- coding: utf-8 -*-
"""
Title:			DataProcessing12
Project Descriptor:	HW5 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		06 Mar 2016

"""


#%% Processing Exp 1 outputs for visualization
# from 'best_centers' (ouput DataProcessing02.py and DataProcessing03.py)
# grey scale 0 - 255 (black -white)

digits = []
for i in range(10):
    dig = 255 - best_centers[i]
    digits.append(dig)
    
#%% Post-processing to .pmg files needed after this
import csv

with open('Exp1Digits.txt', "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(digits)
    
#%% for assgning cluster centers
    
np.unique(labels)


#%% Processing Exp 2 outputs for visualization
# from 'best_centers (ouput DataProcessing04.py and DataProcessing05.py)
# grey scale 0 - 255 (black -white)

digits = []
for i in range(30):
    dig = 255 - best_centers[i]
    digits.append(dig)
    
#%%Post-processing to .pmg files needed after this
import csv

with open('Exp2Digits.txt', "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerows(digits)
    
#%% for assgning cluster centers
    
np.unique(labels)