# %%
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 19 2025
Modified  18 May 2026
@author: bmarron
"""

This script must be run in a virtual envirnment:
    /home/bruce-mx/spyder-6/envs/ai-apis/bin/python3.12

    $ cd ~/spyder-6/envs
	$ python3 -m venv ai-apis
	$ source ./ai-apis/bin/activate


the following packages have been installed into (ai-apis:

    (ai-apis)$ pip install spyder-kernels google-genai openai
    (ai-apis)$ pip install pandas NumPy python-dateutil pytz tzdata
    (ai-apis)$ pip install "pandas[performance]"
    (ai-apis)$ pip install "pandas[computation]"
    (ai-apis)$ pip install plotnine
    (ai-apis):~$ deactivate

"pandas[performance]" contains:
    numexpr
    bottleneck
    numba
    
"pandas[computation]" contains:
    SciPy
    xarray


Successfully installed NumPy-2.4.6 pandas-3.0.3 pytz-2026.2 tzdata-2026.2
Successfully installed bottleneck-1.6.0 llvmlite-0.47.0 numba-0.65.1 numexpr-2.14.1
Successfully installed scipy-1.17.1 xarray-2026.4.0
Successfully installed contourpy-1.3.3 cycler-0.12.1 fonttools-4.63.0 kiwisolver-1.5.0 matplotlib-3.10.9 \
mizani-0.14.4 patsy-1.0.2 pillow-12.2.0 plotnine-0.15.4 pyparsing-3.3.2 statsmodels-0.14.6

# %%

### Mime-type files ####

'''
Document MIME types available for OpenAI output:
    text/plain   ==> .txt
    text/html    ==> .html
    text/json    ==> ,json
    text/x-tex   ==> .tex
    text/csv    ==> .csv
    
'''

# %%


'''
Load pkgs
'''

from openai import OpenAI

from pathlib import Path
import os

import math
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from scipy.stats import beta

from plotnine import (ggplot, aes, labs, geom_col, facet_grid,
                      geom_bar, ggsave, position_dodge2, geom_hline,
                      geom_vline, geom_text,
                      scale_fill_grey, scale_colour_grey,
                      theme_bw, theme_grey, scale_fill_manual, scale_color_brewer)



# %%

'''
API Query 01
Model ==> gpt-5.5

'''

    # API_KEY is saved as an ENV VARIABLE on home compu
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

    # API_KEY can be inserted directly
#client = OpenAI(api_key="ACTUAL_API_KEY")


    # label of output file
OUTPUT_FILE = "SusCurrQuery01_gpt-5.5.txt"
    
    
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-mx/Desktop"   #<== Old HP


    # create paths to files
    # Retrieve files as PosixPaths
output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)



	# User level message
user_prompt= "Search the internet and extract data for wheat yields from the USA for the years \
2000 - 2025. Organize this data and output the data in a .csv format"


	# Developer level message 
sys_prompt = "You are an expert agricultural researcher."



response = client.responses.create(
  model = "gpt-5.5",
  instructions = sys_prompt,
  input = user_prompt
)

with open(output_f, "w", encoding="utf-8") as f:
     f.write(response.output_text)
     
print(f"Query complete! Outputsaved to '{output_f}'.")




 
# %%


'''
Import clean data .csv 
'''

    # find INPUT FILE
doc_dir = "/home/bruce-mx/Desktop"
INPUT_FILE = "API-Output_Query01_clean.csv"
input_filepath = os.path.join(doc_dir, INPUT_FILE)
input_f = Path(input_filepath)


    # Read in Original Data 
    # cols:  "year", "yield"
df_OD = pd.read_csv(input_f)

    #Rename column in df_OD
df_OD = df1.rename(columns={"yield": "Actual"})

# %%

'''
Model the effects on crop yields from an increasingly severe El Niño

Create a stat distribution (beta dist) that runs from 5.1 to 20.1 and is skewed toward 20.1 over a 25-year 
interval. The stat distro provides subsequent crop loss as percentages

'''


    # Parameters for the distribution
    # 5% - 20% crop loss from El Niño
    # 26 years of wheat yield data from the US
low = 5.1
high = 20.1
years = 26


    # In a beta distribution, alpha (v) > beta (w) skews it toward the upper bound (1).
    # v=10 and w=2 for a moderate skew.
v, w = 5, 2


    # pull two sets of rvs from beta dist for a 26-year interval
samples1 = beta.rvs(v, w, size=years)
samples2 = beta.rvs(v, w, size=years)

    # Scale rvs to 5.1 - 20.1 interval
scaled_samples1 = low + (samples1 * (high - low))
scaled_samples2 = low + (samples2 * (high - low))

    #  sort rvs to create a trend.
print("Yearly Values1:")
for i, val in enumerate(np.sort(scaled_samples1), 1):
    print(f"Year {i}: {val:.2f}")
    
print("Yearly Values2:")
for i, val in enumerate(np.sort(scaled_samples2), 1):
    print(f"Year {i}: {val:.2f}")
    
# %%

'''
OPTION 1

Crop-drop trend increases over time (df1)
'''

    # Assuming scaled_samples exists as an array/list
sorted_samples1 = np.sort(scaled_samples1)

    # Create a df directly using col 'year' from df1 and crop-drop percentages
df1 = pd.DataFrame({
    "year":df_OD['year'],
    "Actual": df_OD['Actual'],
    "crop-drop": sorted_samples1
})

    
    # Create a new col "EnvStress' in df1
    # Multiply columns and store back in df1
df1['EnvStress'] = (df_OD['Actual'].values) - (df_OD['Actual'].values * df1['crop-drop'].values * 0.01)

    # clean up df1
    # remove column
df1 = df1.drop(columns=['crop-drop'])


# %%
'''
OPTION 2

Random hit of crop-drop (df2)
'''

    # DO NOT sort
    # Create a df directly using col 'year' from df_OD and crop-drop percentages
df2 = pd.DataFrame({
    "year": df_OD['year'],
    "Actual": df_OD['Actual'],
    "crop-drop": scaled_samples2
})

    
    # Create a new col "EnvStress' in df2
    # Multiply columns and store back in df2
df2['EnvStress'] = (df2['Actual'].values) - (df2['Actual'].values * df2['crop-drop'].values * 0.01)

    # clean up df2
    # remove column
df2 = df2.drop(columns=['crop-drop'])

 # %%

 '''
 ggplot Style1

 '''

     # plot_df1.jpeg
     # increasing crop-drop effect from El Niño (df1)
 df_long = df1.melt(id_vars=['year'], value_vars= ['Actual', 'EnvStress'])

 plot_df1 = (ggplot(df_long, aes(x = 'year', y = 'value', fill = 'variable'))
     + geom_bar(stat="identity", 
                position = position_dodge2(preserve = "single"),
                width=1.0)
     #+ scale_fill_grey()
     + scale_fill_manual(values={'Actual':'green', 'EnvStress':'red'})
     + theme_grey()
     + geom_hline(yintercept=40, linetype="dotted", colour= "black")
     + labs(title = "US Wheat Yield under El Niño",
            x = "Year",
            y = "Bushel/Acre (27.2 kg/bushel)")
     )

 doc_dir = "/home/bruce-mx/Desktop"
 OUTPUT_FILE = "plot_df1.jpeg"
 output_filepath = os.path.join(doc_dir, OUTPUT_FILE)
 output_f = Path(output_filepath)
 ggsave(plot_df1, output_f)


    # "plot_df2.jpeg
     # random crop-drop effect from El Niño (df2)
 df_long = df2.melt(id_vars=['year'], value_vars= ['Actual', 'EnvStress'])

 plot_df2 = (ggplot(df_long, aes(x = 'year', y = 'value', fill = 'variable'))
     + geom_bar(stat="identity", 
                position = position_dodge2(preserve = "single"),
                width=1.0)
     #+ scale_fill_grey()
     + scale_fill_manual(values={'Actual':'green', 'EnvStress':'red'})
     + theme_grey()
     + geom_hline(yintercept=40, linetype="dotted", colour= "black")
     + labs(title = "US Wheat Yield under El Niño",
            x = "Year",
            y = "Bushel/Acre (27.2 kg/bushel)")
     )

    
 doc_dir = "/home/bruce-mx/Desktop"
 OUTPUT_FILE = "plot_df2.jpeg"
 output_filepath = os.path.join(doc_dir, OUTPUT_FILE)
 output_f = Path(output_filepath)
 ggsave(plot_df2, output_f)






# %%

'''
ggplot Style 2

'''
         # increasing crop-drop effect from El Niño (df1a)
df_long = df1.melt(id_vars=['year'], value_vars= ['Actual', 'EnvStress'])

plot_df1 = (ggplot()
    + geom_col(df_long, aes(x='year', y='value', color="factor(variable)"), width=0.25)
    + facet_grid(". ~ variable") # . means no rows; variable means columns
    + labs(
        x="Year",
        y="Yield"
    )
)


doc_dir = "/home/bruce-mx/Desktop"
OUTPUT_FILE = "plot_df1.jpeg"
output_filepath = os.path.join(doc_dir, OUTPUT_FILE)
output_f = Path(output_filepath)
ggsave(plot_df1, output_f)


    # random crop-drop effect from El Niño (df1b)
df_long = df2.melt(id_vars=['year'], value_vars= ['Actual', 'EnvStress'])

plot_df2 = (ggplot()
    + geom_col(df_long, aes(x='year', y='value', color="factor(variable)"), width=0.25)
    + facet_grid(". ~ variable") # . means no rows; variable means columns
    + labs(
        x="Year",
        y="Yield"
    )
)


doc_dir = "/home/bruce-mx/Desktop"
OUTPUT_FILE = "plot_df2.jpeg"
output_filepath = os.path.join(doc_dir, OUTPUT_FILE)
output_f = Path(output_filepath)
ggsave(plot_df2, output_f)


# %%

'''
     Misc snippets
'''

range(1, len(sorted_samples) + 1)
    
# generate 26 evenly spaced values sampled from this distribution.
x = np.linspace(0, 1, years)

    # remove col from df
df1 = df1.drop(columns=['EnvStressYield'])


       # round new column to one decimal
df2['yield'] = df2['yield'].round(1)



    # plot a single dataset 
data1 = (ggplot()
    + geom_col(df1, aes(x="year", y="yield"), width=0.25)    
    + labs(
        x="Year",
        y="Yield"
    )
)

    # see plot in "Plots" window Spyder
data1



