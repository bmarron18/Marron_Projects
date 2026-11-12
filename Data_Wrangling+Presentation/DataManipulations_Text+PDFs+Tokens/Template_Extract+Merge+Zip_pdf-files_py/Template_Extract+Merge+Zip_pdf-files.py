#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 09:33:46 2025
Updated: 30 Jun 2026

@author: bmarron
"""


# %%

import os
os.getcwd()

print (os.getcwd())

# %%

'''
<<< bash
    cd ~/spyder-6/envs && 
    source ./ai-apis/bin/activate
    
    pip install --upgrade pypdf
    pip list
>>>
'''

# %%
'''
=======================
Merge pdf files
=======================

NOTE: To shrink the size of a .pdf, can use GIMP OR SEE BELOW
    * import the .pdf as image (not layers) and reduce resolution (try setting at 200)
    * select "Export as..." to export the file as a new .pdf smaller in size
'''



from pypdf import PdfWriter
from pathlib import Path
import os

    # label of output file
OUTPUT_FILE = "Combined_Output.pdf"
      
    # set up the file paths for the OUTPUT_FILE
    # set the file path to your Desktop
    # Path() represents file+directory paths in a platform-independent manner.
doc_to_print = OUTPUT_FILE
doc_dir = "/home/bruce-vdb/Desktop"

    # create paths to files
    # Retrieve files as PosixPaths
output_filepath = os.path.join(doc_dir, doc_to_print)
output_f = Path(output_filepath)

#==================================
# EDIT
#=====================================
    # set input files to be merged
INPUT_FILE_01 =  Path(os.path.join(doc_dir,"M01.pdf"))
INPUT_FILE_02 =  Path(os.path.join(doc_dir,"M02.pdf"))
INPUT_FILE_03 =  Path(os.path.join(doc_dir,"M03.pdf"))
INPUT_FILE_04 =  Path(os.path.join(doc_dir,"M04.pdf"))
INPUT_FILE_05 =  Path(os.path.join(doc_dir,"M05.pdf"))
#INPUT_FILE_03 =  Path(os.path.join(doc_dir,"03_BusinessCards.pdf"))
#INPUT_FILE_04 =  Path(os.path.join(doc_dir,"04_Marron_recommendation_ltr_DEQ.pdf"))
#INPUT_FILE_05 =  Path(os.path.join(doc_dir,"05_Permaculture_small.pdf"))

# call PdfWriter
writer = PdfWriter()

#==================================
# EDIT
#=================================
    # Add your PDFs to merge
writer.append(INPUT_FILE_01)
writer.append(INPUT_FILE_02)
writer.append(INPUT_FILE_03)
writer.append(INPUT_FILE_04)
writer.append(INPUT_FILE_05)


# Save the combined file
writer.write(output_f)
writer.close()


# %%
'''
==================================================
Compress size of merged (multiple-page) pdf file
====================================================

    <<< bash
        sudo aptitude install ghostscript
    >>>
'''

import subprocess
import sys

def compress_pdf(input_file, output_file, power=2):
    """
    Compresses a PDF using Ghostscript.
    power: 0 = default, 1 = screen (lowest quality, 72 dpi), 
           2 = ebook (medium quality, 150 dpi), 3 = printer (300 dpi)
    """
    quality_settings = {
        0: '/default',
        1: '/screen',
        2: '/ebook',
        3: '/printer'
    }
    
    gs_setting = quality_settings.get(power, '/ebook')
    
    cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_setting}", "-dNOPAUSE", "-dQUIET", 
        "-dBATCH", f"-sOutputFile={output_file}", input_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully compressed! Saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}", file=sys.stderr)

    #  Usage:
compress_pdf("/home/bruce-vdb/Desktop/M01.pdf", "/home/bruce-vdb/Desktop/Compressed_Output.pdf", power=3)


# %%

'''
===============================
Create (compressed) .zip file
==================================

Example usage:
    compress_to_zip('my_folder_or_file', 'output.zip')
'''


import os
import zipfile

def compress_to_zip(source_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        if os.path.isfile(source_path):
            zipf.write(source_path, os.path.basename(source_path))
        elif os.path.isdir(source_path):
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=source_path)
                    zipf.write(file_path, arcname)

    size_mb = os.path.getsize(output_zip_path) / (1024 * 1024)
    print(f"Archive created: {output_zip_path} ({size_mb:.2f} MB)")

compress_to_zip('/home/bruce-vdb/Desktop/MAXB590319HNERXR03', '/home/bruce-vdb/Desktop/output.zip')


# %%





    

