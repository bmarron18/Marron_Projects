#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 17:15:03 2025

@author: bmarron18
"""


# %%

'''
Pandas Internal Tests
'''

import pandas as pd
from pathlib import Path
import os



    # create paths to files
    # Retrieve files as PosixPaths
    
doc_dir = "/home/bmarron18/Desktop"
OUTPUT_FILE = "PandaTests.txt"
output_filepath = os.path.join(doc_dir, OUTPUT_FILE)
output_f = Path(output_filepath)

test = pd.test() 

   # Output
with open(output_f, "w", encoding="utf-8") as f:
     f.write(test)
     
# %%
'''
Greek letters Unicode

'''

    # ctrl+Shift+U 03B8  θ  theta
    
# %%

'''
    NumPy, Pandas, and SciPy for stats

    https://docs.scipy.org/doc/scipy/reference/stats.html


'''
    
# %%


'''
Statistical Distros
'''

import math
import numpy as np
import pandas as pd
from scipy.stats import  hypergeom, binom, beta

# %%

# --- Discrete Statistical functions (scipy.stats) --------------------

    # NB. Inverses of pmf and percentiles
n, p = 20, 0.10
binom.pmf(0, n, p)                      #<== gives np.float64(0.12157665459056918)
binom.ppf(0.12157665459056918, n, p)    #<== gives np.float64(0.0)

binom.pmf(1, n, p)                      #<== gives np.float64(0.2701703435345983)
binom.ppf(0.2701703435345983, n, p)     #<== gives np.float64(1.0)

binom.pmf(2, n, p)                      #<== gives np.float64(0.28517980706429846)
binom.ppf(0.28517980706429846, n, p)    #<== gives np.float64(2.0)



    # NB the discrete distros are binned, thus
binom.ppf(0.28, n, p)                    #<== gives np.float64(1.0)
binom.ppf(0.29, n, p)
binom.ppf(0.39, n, p)
binom.ppf(0.399, n, p)                  #<== gives np.float64(2.0)


# Hypergeometric
    scipy.stats.hypergeom
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.hypergeom.html
    
    # Prob Mass Fxn
    # hypergeom.pmf(k, M, n, N, loc=0)
    * M == ct of all entities in a set; two types
    * N == ct of Type I entities
    * M-N == ct of Type II entities
    * n == ct of draws/trials/slots
    * k == ct of Type I in n draws/trials/slots

    # Cumulative distribution function.
    # hypergeom.cdf(k, M, n, N, loc=0)

    # Random variates.
    # hypergeom.rvs(M, n, N, loc=0, size=1, random_state=None)



# Binomial
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html#scipy.stats.binom
       
    # binom.pmf(k, n, p, loc=0)  <== prob mass fxn
    #   n = ct of slots/trials/draws that result from sampling/observing the output from
    #       a binary entity generator (w/ replacement)
    #   k = ct of type a entities 
    #   n-k = ct of type b entties
    
    #   p = prob of type a entity
    #   1-p = prob of type b entity
    #   loc=0 <== endpoint of distro
    
    # binom.ppf(q, n, p, loc=0)  <== % point fxn, percentiles (inverse pmf)
    #   q = percentile
  
    




# %%

# --- Continuous Statistical functions (scipy.stats) --------------------

# Beta
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html#scipy.stats.beta

    # beta.ppf(q, a, b, loc=0, scale=1) <== % point fxn, percentiles (inverse cdf)
    # beta.pdf(x, a, b, loc=0, scale=1) <== prob density fxn
    # beta.cdf(x, a, b, loc=0, scale=1) <== cumulative density fxn (the integral of the pdf)

     # NB. Inverses of cdf and percentiles (NOT of pdf)
a, b = 2, 20
beta.cdf(0.05, a, b, loc=0, scale=1)                # <== gives 0.2830281551829153
beta.ppf(0.2830281551829153, a, b, loc=0, scale=1)  # <== gives 0.05





# %%















