#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 09:33:46 2025
Updated: 11 Nov 2026

@author: bmarron
"""


# %%

import os
os.getcwd()

print (os.getcwd())



# %%
'''
=========  Extraction of Vocab  ==============================
'''

# %%


'''
INFO
    Generating a unique word list from texts
    Gives single words for student vocab lists
    Regex
'''

https://stackoverflow.com/questions/43025188/regular-expression-re-findall-for-set-of-all-alphabetic-words

This will accept words like "don't" and "re-invent" and "cul-de-sac" but will 
reject numbers, underscores, whitespace, quote marks, and other punctuation.

    re.findall(r"[A-Za-z\-\']+", s)
    
The \p{L} matches all Unicode letters regardless of modifiers passed to the regex compile.
    re.findall(r"[p{L}\-\']+", s)

https://docs.python.org/3/library/re.html
In regex, there are 12 characters with special meanings: 
    the backslash \, 
    the caret ^, 
    the dollar sign $, 
    the period or dot ., 
    the vertical bar or pipe symbol |, 
    the question mark ?, 
    the asterisk or star *, 
    the plus sign +, 
    the opening parenthesis (, 
    the closing parenthesis ), 
    the opening square bracket [, and 
    the opening curly brace {, 
These special characters are often called metacharacters and should be escaped with backslash Ab\(123\) if used as literal.
This can be automagically achieved using re.escape()

# %%

"""
INFO
    Use this to find two-word vocab
    Find next word
"""
    # How to find the next word of a specific word in a txt-file
    # https://stackoverflow.com/questions/70730240/q-how-to-find-the-next-word-of-a-specific-word-in-a-txt-file


# %%

'''
STEP 1
    Extract text from pdf
    (see pypdf below)
'''
 # extract text preserving horizontal positioning without excess vertical
 # whitespace (removes blank and "whitespace only" lines)
 # "a" is append

from contextlib import chdir
from pypdf import PdfReader

    # change pdf name
#with chdir('/home/bmarron/Desktop'):
with chdir('/home/bmarron18/Desktop'):
    reader = PdfReader("science.pdf")
    for page_num in range(len(reader.pages)):  # short articles
    #for page_num in range(8):                   # books
        page = reader.pages[page_num]
        with open("VocabDump.txt", "a") as f:
            print(page.extract_text(), file=f)
         #print(page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False), file=f)



# %%
'''
STEP 2
    USE THIS to remove end of line returns from text file
    End of line returns are coded as, /n
    "tr" == truncate (Linux command)

        # delete all newlines
    $ tr --delete '\n' < yourfile.txt
    
        # replace newlines with space
    $ tr '\n' ' ' < input_filename
''' 

    # USE THIS!! STEP2
    # Linux terminal @ Desktop
$ tr '\n' ' ' < VocabDump.txt > Test2.txt



# %%
 '''
 STEP 3
     *Generating a unique word list from texts
     *Gives single words for student vocab lists
 '''


    # USE THIS!! STEP 3
import re
from contextlib import chdir

#with chdir('/home/bmarron/Desktop'):
with chdir('/home/bmarron18/Desktop'):
    M = []
    with open('Test2.txt') as f:
        for line in f.readlines():
            for word in line.split():
                word = re.findall('[A-Za-zñáéíóúüÁÉÍÓÚ\,\-\.\“\\(]+', word)    #words in español and w/ comma, dash, period
                if word:
                    M.append(word[0])

    S = list(set(M))
    S = sorted(S, key=str.lower)

    with open("output.txt", "w") as f:
        for i in S:
            f.write(i + "\n")



# %%
'''
STEP 4 (as needed)
'''

    # USE THIS!! (as needed)
    # Replace search_word
from contextlib import chdir


#with chdir('/home/bmarron/Desktop'):
with chdir('/home/bmarron18/Desktop'):

    with open('Test2.txt','r') as f:
        data = f.read()

    search_word = "galio"
    list_of_words = data.split()
    next_word = list_of_words[list_of_words.index(search_word) + 1]
    prev_word = list_of_words[list_of_words.index(search_word) - 1]

    with open("two-word_terms.txt", "a") as f:
        print(prev_word,"",search_word,"",next_word, file=f)


# %%
'''
STEP 5 (as needed)
  Building a comprehensive vocab list
'''
  


    # 5a. Replace spaces with hyphens
    # Linux
    
$ tr ' ' '-' <AllVocab.txt >Test2.txt


    # 5b. Sort unique words with Step 3 above
    # get "output.txt"
    
    
    # 5c. Revert to spaces in vocab list
$ tr '-' ' ' <output.txt >AllVocab2.txt




# %%
'''
=========  Finding Dups in Text Files  ==============================
'''

# %%

'''
Find and print duplicates in ONE vocab list;
file1
'''

    # Linux
$ sort file1.txt | uniq -cd >> dups.txt


# %%

'''
Find and print duplicates found in TWO vocab lists;
file1 and file2
'''

from contextlib import chdir

with chdir('/home/bmarron/Desktop'):
    with open("file1.txt") as f1,open("file2.txt") as f2:
        words1=set(line.strip() for line in f1)
        words2=set(line.strip() for line in f2)

    dups=list(words1.intersection(words2))
    
    with open("duplicateVocab.txt", "a") as f:
        print(dups, file=f)
        




# %%
'''
.txt to .pdf for translation purposes

<<< bash
    cd ~/spyder-6/envs && 
    source ./ai-apis/bin/activate
    
    pip install --upgrade pypdf
    pip list
    deactivate
>>>

'''

import textwrap
from fpdf import FPDF
from pathlib import Path
import os


   # set up
input_filename = "/home/bmarron18/Desktop/test.txt"
output_filename = "/home/bmarron18/Desktop/output.pdf"
file = open(input_filename)
text = file.read()
file.close()


def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')


    # run
text_to_pdf(text, output_filename)






# %%

'''
=========  Misc Text Options =======================
    Get word frequencies
'''

import pandas as pd
#pd.options.display.max_colwidth = None
pd.options.display.max_rows = None
    
from contextlib import chdir


with chdir('/home/bmarron/Desktop'):
    
    words = open("clean_test.txt", "r").read().split()
    ordered = sorted(words)
    with open("output.txt", "a") as f:
        print(pd.Series(ordered).value_counts().sort_values(ascending=True), file=f)

# %%





'''
    TEXT CLEANING
    Use sed and 'tr' to
	+ remove all non-printable ASCII characters (garbage characters== !(octal 11-15 || 40-176)).
	+ remove all punctuation
    + NB. 'tr' uses backslash to denote an octal number.
'''

    # open terminal that has file to be counted
    # remove all punctuation
    # overwrite original
    
$ tr -cd '\11-\15\40-\176' < NAME_of_FILE.txt > clean_test.txt &&
sed 's/[[:punct:]]//g' < clean_test.txt > TMP_00 &&
mv TMP_00 clean_test.txt

# %%

from contextlib import chdir


with chdir('/home/bmarron/Desktop'):

    # opening and creating new .txt file 
    with open( 
            "CivilLaw_Terms.txt", 'r') as r, open( 
                'output.txt', 'w') as o: 
      
                    for line in r: 
                        #isspace() function 
                        if not line.isspace(): 
                            o.write(line) 
  
    f = open("output.txt", "r") 
    print("New text file:\n",f.read())


  

# %%


# %%

def count_words(line):
    words = line.split()
    return len(words)

f = open("C:/Users/John Green/Desktop/follows.txt", "r")
text = f.read()
#make a list of the file broken into lines
lines = text.split('\n')
max_words = -1
word = ''
for line in lines:
    length = count_words(line)
    if length > max_words:
        max_words = length
        words = line.split()
f.close()
print(words[0])

# %%


    #Total number of words per line in a text file


def count_words(line):
    words = line.split()
    return len(words)

f = open("/home/bmarron/Desktop/TEST.txt", "r")
text = f.read()
#make a list of the file broken into lines
lines = text.split('\n')
max_words = -1
word = ''
for line in lines:
    length = count_words(line)
    if length > max_words:
        max_words = length
        words = line.split()
f.close()
print(words[0])



# %%



# count the occurrences of number of spaces!?

txt = "Just an example here move along" 
count = 1
for i in txt:
    if i == " ":
       count += 1
print(count)





# %%

"""
USE THIS!!
Find next word
"""
    # How to find the next word of a specific word in a txt-file
    # https://stackoverflow.com/questions/70730240/q-how-to-find-the-next-word-of-a-specific-word-in-a-txt-file


with open('/home/bmarron/Desktop/TEST.txt','r') as f:
    data = f.read()

search_word = "ingeniería"
list_of_words = data.split()
next_word = list_of_words[list_of_words.index(search_word) + 1]



