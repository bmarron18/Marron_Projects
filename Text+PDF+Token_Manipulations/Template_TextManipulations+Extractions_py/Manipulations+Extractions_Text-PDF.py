#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 09:33:46 2025
Updated: 30 Jun 2026

@author: bmarron
"""

# %%

    # freq of words in a text
https://stackoverflow.com/questions/20510768/count-frequency-of-words-in-a-list-and-sort-by-frequency
 

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

=========== pdf Manipulations ========================

# %%

"""
pypdf module
Successfully installed pypdf-6.14.2
"""
https://pypdf.readthedocs.io/en/stable/user/installation.html
https://pypdf.readthedocs.io/en/stable/user/adding-pdf-annotations.html

Hence I would distinguish three types of PDF documents:
#Digitally-born PDF files: The file was created digitally on the computer. It can contain images, texts, links, outline items (a.k.a., bookmarks), JavaScript, … If you Zoom in a lot, the text still looks sharp.
#Scanned PDF files: Any number of pages was scanned. The images were then stored in a PDF file. Hence the file is just a container for those images. You cannot copy the text, you don’t have links, outline items, JavaScript.
#OCRed PDF files: The scanner ran OCR software and put the recognized text in the background of the image. Hence you can copy the text, but it still looks like a scan. If you zoom in enough, you can recognize pixels.

If you have activated a virtual environment (like venv or virtualenv), 
pip completely bypasses your global system folders. It isolates your installations here

Install pypdf into a virtual envirnment:
    /home/bruce-vdb/spyder-6/envs/ai-apis/bin/python3.12

<<< bash
    cd ~/spyder-6/envs && 
    source ./ai-apis/bin/activate
    
    pip install --upgrade pypdf
    pip list
>>>


the following packages have been installed into (ai-apis):

    (ai-apis)$ pip install spyder-kernels google-genai openai
    (ai-apis)$ pip install pandas NumPy python-dateutil pytz tzdata
    (ai-apis)$ pip install "pandas[performance]"
    (ai-apis)$ pip install "pandas[computation]"
    (ai-apis)$ pip install plotnine
    (ai-apis)$ pip install pypdf[full]

(ai-apis):~$ deactivate




# %%
'''
.txt to .pdf for translation purposes

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
Merge pdf files
'''

'''
NOTE: To shrink the size of a .pdf, use GIMP
    * import the .pdf as image (not layers) and reduce resolution (try setting at 200)
    * select "Export as..." to export the file as a new .pdf smaller in size
'''



from pypdf import PdfWriter
from pathlib import Path
import os

    # label of output file
OUTPUT_FILE = "combined_output.pdf"
      
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"

    # create paths to files
    # Retrieve files as PosixPaths
output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)


# set input files to be merged
INPUT_FILE_01 =  Path(os.path.join(doc_dir,"01GE.pdf"))
INPUT_FILE_02 =  Path(os.path.join(doc_dir,"02GE.pdf"))
#INPUT_FILE_03 =  Path(os.path.join(doc_dir,"03_BusinessCards.pdf"))
#INPUT_FILE_04 =  Path(os.path.join(doc_dir,"04_Marron_recommendation_ltr_DEQ.pdf"))
#INPUT_FILE_05 =  Path(os.path.join(doc_dir,"05_Permaculture_small.pdf"))


# call PdfWriter
writer = PdfWriter()

# Add your PDFs to merge
writer.append(INPUT_FILE_01)
writer.append(INPUT_FILE_02)
#writer.append(INPUT_FILE_03)
#writer.append(INPUT_FILE_04)
#writer.append(INPUT_FILE_05)


# Save the combined file
writer.write(output_f)
writer.close()







# %%

"""
Add text box comment
font color hex codes
"""

import os
import pypdf
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText


# path to the document
doc_to_comment = "terminologia 6.1_Leslie.pdf" ;
doc_dir = "/home/bmarron/Desktop" ;
pdf_path = os.path.join(doc_dir, doc_to_comment)


# Fill the writer with the pages you want
reader = PdfReader(pdf_path)
page = reader.pages[0]
writer = PdfWriter()
writer.add_page(page)

# Create the annotation and add it
annotation = FreeText(
    text="LATE\n \n 8.0",
    rect=(200, 700, 150, 650), # a square! why???
    #font="New Times Roman",
    #bold=True,
    #italic=True,
    #font_size="20pt",
    #font_color="000000",
    border_color="d70029",
    background_color="ffffff",
)

# Set annotation flags to 4 for printable annotations.
# See "AnnotationFlag" for other options, e.g. hidden etc.
annotation.flags = 4

writer.add_annotation(page_number=0, annotation=annotation)

# Write the annotated file to disk
with open("/home/bmarron/Desktop/annotated.pdf", "wb") as fp:
    writer.write(fp)
    
    
# %%

========== Optical Character Reader for Scanned pdf Files ===============


# %%
'''    OCR for optical pdf files
        *create text files for Extraction of Vocab
'''
    # STEP 1 ==> pdf to png
    # if a multipage pdf, will out individual ,pngs; one per pdf page
$ pdftoppm -png Webdoc.pdf Webdoc

    # STEP 2a ==> one png file to txt 
$ tesseract Webdoc-1.png Webdoc-1 --dpi 250^C

    # STEP 2b ==> multiple ,png
    # loop thru Webdoc-xx.png files
    # create a text file from each image
$ for i in Webdoc-??.png; 
do tesseract "$i" "text-$i" -l eng; 
done

    # STEP 3 ==> compile/concatentae text files (if needed)
$ cat text-Webdoc* > complete.txt

# %%
'''
    Merge pdf files into one
'''


$ pdfunite in-1.pdf in-2.pdf in-n.pdf ouput.pdf

$ pdfunite W*01.pdf W*02.pdf W*03.pdf W*04.pdf W*05.pdf W*06.pdf W*07.pdf W*08.pdf W*09.pdf W*10.pdf W*11.pdf W*12.pdf ouput.pdf



# %%


# %%
'''
Optical Character Recognition (OCR)
'''

https://builtin.com/data-science/python-ocr



    # Install Tesseract in Linux and Python
    # Successfully installed pytesseract-0.3.13 in /usr/lib/python3/dist-packages
    # pytesseract in ./.local/lib/python3.10/site-packages (0.3.13)

    # for use in terminal
$ sudo aptitude install tesseract-ocr-all

    # for use in Python
$ pip3 install tesseract


# %%

'''
Tesseract   ==> image files only
            ==> unable to read PDFs. rom a PDF, you can 
            ===> use another utility first to generate a set of images
            ==> A single image will represent a single page of the PDF
            ==> pdftppm utility
'''

https://www.howtogeek.com/682389/how-to-do-ocr-from-the-linux-command-line-using-tesseract/

-r number
Specifies the X and Y resolution, in DPI.  The default is 150 DPI.


    # pdf to images is turing-01.png" "turing-02.png" etc
$  pdftoppm -png Web.pdf Web

    # JPEG option
    <opt>=<val>[,<opt>=<val>]"
-jpegopt 
$ pdftoppm -jpegopt=90[,-jpegopt=n] PDF-file PPM-root


    # general tesseract
    # creates "recital.txt" at 150 dpi
$ tesseract recital-63.png recital --dpi 150


    # loop thru turing-xx.png files
    # create a text file from each image
$ for i in turing-??.png; do tesseract "$i" "text-$i" -l eng; done;

    # concatenate text files into one file
$ cat text-turing* > complete.txt




# %%

'''
build an OCR engine in Python
'''

import pytesseract
from PIL import Image
import pytesseract
import numpy as np

    # clean image OCR
filename = "image_01.png" 
img1 = np.array(Image.open(filename))
text = pytesseract.image_to_string(img1)



    # image cleaning then OCR
import numpy as np
import cv2norm_img = np.zeros((img.shape[0], img.shape[1]))
from contextlib import chdir


with chdir('/home/bmarron/Desktop'):

    filename = 'image_02.png'
    img2 = np.array(Image.open(filename))
    img2 = cv2.normalize(img2, norm_img, 0, 255, cv2.NORM_MINMAX)
    img2 = cv2.threshold(img2, 100, 255, cv2.THRESH_BINARY)[1]
    img2 = cv2.GaussianBlur(img2, (1, 1), 0)

    text = pytesseract.image_to_string(img2)
    print(text)


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



