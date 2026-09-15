# -*- coding: utf-8 -*-
"""
Title:			Experiment3 -- Feature Selection 2 (ggplot)
Project Descriptor:	HW3 -- MachineLearning
Project ID:		CS 545 (2016SoE009)
Record:		
Author:			bmarron
Origin Date:		10 Feb 2016

"""
#%% Use ggplot_anaconda2 ==> numpy 1.9!!
# Import packages

import numpy as np
import cPickle
import pandas as pd
from ggplot import *


#%% Load accuracy data and make count list

# Use spyder import (green arrow)
# File ==> exp3_accuracies.txt

# Data should be in single line; comma separated .txt file
Accs = list(exp3_accuraciestxt)
count = np.arange(57)
 

#%% Use pandas and make dataframe; plot
df = pd.DataFrame(dict(A=Accs, c=count))

gg = ggplot(df, aes(x='c', y='A')) +\
    geom_line() +\
    labs(x="Features (random)", y="Accuracy")
    
#%% Export the graphic (full size)
    
ggsave(filename="exp3_accuracies.png", plot=gg)
ggsave(filename="exp3_accuracies.pdf", plot=gg)
