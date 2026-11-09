# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 10:07:49 2016

@author: bmarron
"""


#%%Required pkgs (imports)
import random
import cPickle
import string
import pandas as pd
import numpy as np


#processed training data
tr_d=cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk2/DataFiles/Input_Data/Processed/tr_d/tr_d.pkl","rb"))


#processed test data
te_d=cPickle.load(open("/home/bmarron/Desktop/PSU/PhD_EES/SoE/2016SoE009_CS545_MachineLearning/_PWFs_works_inprogress/Hwk2/DataFiles/Input_Data/Processed/te_d/te_d.pkl","rb"))



#%% The Letter Recognition Neural Network (w/ momentum)
#run this (Marron_NN1a.py) to load Class LtrRecogNN

    #NN layers
NNsize=[16,4,26]
np.random.seed(47)
 


#%% Experiment 1a: tr_d and tr_d


	#initiation from zero state
hwk2_exp1_run1=LtrRecogNN(NNsize)

    #eta =.3, alpha = .3
hwk2_exp1_run1.SGD(tr_d, 100, .3, .3, tr_d)


#%% Experiment 1b: tr_d and tr_d (another 100 epochs better?)

hwk2_exp1_run1.SGD(tr_d, 100, .3, .3, tr_d)

#%% Experiment 1c: tr_d and te_d

	#initiation from zero state
hwk2_exp1_run1=LtrRecogNN(NNsize)

    #eta =.3, alpha = .3
hwk2_exp1_run1.SGD(tr_d, 100, .3, .3, te_d)
#%%

#%% Experiment 2a: tr_d and tr_d

	#initiation from zero state
hwk2_exp2=LtrRecogNN(NNsize)

    #eta =.05, alpha = .3
hwk2_exp2.SGD(tr_d, 100, .05, .3, tr_d)


#%% Experiment 2b: tr_d and te_d

	#initiation from zero state
hwk2_exp2=LtrRecogNN(NNsize)

    #eta =.05, alpha = .3
hwk2_exp2.SGD(tr_d, 100, .05, .3, te_d)

#%% Experiment 2c: tr_d and tr_d

	#initiation from zero state
hwk2_exp2=LtrRecogNN(NNsize)

    #eta =.6, alpha = .3
hwk2_exp2.SGD(tr_d, 100, .6, .3, tr_d)


#%% Experiment 2d: tr_d and te_d

	#initiation from zero state
hwk2_exp2_run1=LtrRecogNN(NNsize)

    #eta =.6, alpha = .3
hwk2_exp2_run1.SGD(tr_d, 100, .6, .3, te_d)


#%%
#%% Experiment 3a: tr_d and tr_d

	#initiation from zero state
hwk2_exp3=LtrRecogNN(NNsize)

    #eta =.3, alpha = .05
hwk2_exp3.SGD(tr_d, 100, .3, .05, tr_d)


#%% Experiment 3b: tr_d and te_d

	#initiation from zero state
hwk2_exp3=LtrRecogNN(NNsize)

    #eta =.3, alpha = .05
hwk2_exp3.SGD(tr_d, 100, .3, .05, te_d)

#%% Experiment 3c: tr_d and tr_d

	#initiation from zero state
hwk2_exp3=LtrRecogNN(NNsize)

    #eta =.3, alpha = .6
hwk2_exp3.SGD(tr_d, 100, .3, .6, tr_d)


#%% Experiment 3d: tr_d and te_d

	#initiation from zero state
hwk2_exp3=LtrRecogNN(NNsize)

    #eta =.3, alpha = .6
hwk2_exp3.SGD(tr_d, 100, .3, .6, te_d)

#%%
#%% Experiment 4a: tr_d and tr_d

	#initiation from zero state
hwk2_exp4=LtrRecogNN(NNsize2)

    #eta =.3, alpha = .05
hwk2_exp4.SGD(tr_d, 100, .3, .3, tr_d)


#%% Experiment 4b: tr_d and te_d

	#initiation from zero state
hwk2_exp4=LtrRecogNN(NNsize2)

    #eta =.3, alpha = .05
hwk2_exp3.SGD(tr_d, 100, .3, .3, te_d)




