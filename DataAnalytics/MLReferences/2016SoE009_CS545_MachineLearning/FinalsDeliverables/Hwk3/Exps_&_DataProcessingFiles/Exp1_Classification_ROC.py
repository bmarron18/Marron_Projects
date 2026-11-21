# -*- coding: utf-8 -*-
"""
Title:			Experiment1 -- Classification ROC Curve (ggplot)
Project Descriptor:	HW3 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		06 Feb 2016

"""
#%% Use ggplot_anaconda2 ==> numpy 1.9!!
# Import packages

import numpy as np
import cPickle
import pandas as pd
from ggplot import *

#%% Reload ROC data
ROC_data = cPickle.load(open("/home/bmarron/Desktop/ROCcurve_data.pkl","rb"))
    
# Extract (unzip)
fpr, tpr = zip(*ROC_data)    

#%% Use pandas and make dataframe; plot
df = pd.DataFrame(dict(fpr=fpr, tpr=tpr))

gg = ggplot(df, aes(x='fpr', y='tpr')) +\
    geom_line() +\
    geom_abline(linetype='dashed') +\
    labs(x="False positive rate (fpr)", y="True positive rate (tpr)")
    
#%% Export the graphic (full size)
    
ggsave(filename="roc.png", plot=gg)
ggsave(filename="roc.pdf", plot=gg)

