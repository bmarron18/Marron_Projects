#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Searchable_PDF_ocr.py

Convert images (PNG, JPG, TIFF, ...) or scanned PDFs into searchable PDFs
using Tesseract OCR.

Created on Wed Oct 14 17:47:24 2026
@author: bruce-vdb, claude sonnet

SETUP
-----
System dependencies (not installable with pip):
    - Tesseract OCR
sudo aptitude install tesseract-ocr
    
    - Poppler
sudo aptitude install poppler-utils

Python environment:
<<< bash
    cd ~/spyder-6/envs &&
    source ./ai-apis/bin/activate
    
    python3 -m pip install --upgrade pip
    pip install --upgrade pytesseract pypdf pdf2image pillow
    deactivate
>>>

USAGE
-----
    python3 Searchable_PDF_ocr.py scan.pdf
    python3 Searchable_PDF_ocr.py scan.pdf -o out.pdf --lang eng+spa --dpi 300
    python3 Searchable_PDF_ocr.py photo.png

If no output path is given, "<input name>_searchable.pdf" is written next
to the input file.

Running with no arguments (e.g. from Spyder) uses the INPUT_PATH and
OUTPUT_PATH values below.
"""

import argparse
import io
import shutil
import sys
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image, ImageSequence
from pypdf import PdfReader, PdfWriter

# --- Defaults for interactive use (Spyder etc.); command-line args override ---
INPUT_PATH = "/home/bruce-vdb/Desktop/Brundtland_P14.pdf"          # image or PDF
OUTPUT_PATH = "/home/bruce-vdb/Desktop/Brundtland_ocr_P14.pdf"
LANGUAGE = "eng"                          # e.g. "eng", "spa", "eng+spa"
DPI = 300

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif", ".webp"}


def check_dependencies():
    """Fail early with a clear message if Tesseract or Poppler is missing."""
    if shutil.which("tesseract") is None:
        sys.exit("Error: Tesseract OCR is not installed or not on your PATH.")
    if shutil.which("pdftoppm") is None:
        sys.exit("Error: Poppler (pdftoppm) is not installed or not on your PATH.")


def ocr_to_pdf_page(image, lang):
    """OCR one PIL image and return a single-page PDF as a PdfReader page."""
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, extension="pdf", lang=lang)
    return PdfReader(io.BytesIO(pdf_bytes)).pages[0]


def image_to_searchable_pdf(image_path, output_pdf_path, lang=LANGUAGE):
    """Convert an image (including multi-frame TIFFs) into a searchable PDF."""
    print(f"Processing image: {image_path}")
    writer = PdfWriter()

    with Image.open(image_path) as img:
        frames = list(ImageSequence.Iterator(img))
        for i, frame in enumerate(frames, start=1):
            print(f"OCR-ing frame {i}/{len(frames)}...")
            # Tesseract's PDF output needs a standard colour mode
            writer.add_page(ocr_to_pdf_page(frame.convert("RGB"), lang))

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"Saved searchable PDF to {output_pdf_path}")


def scanned_pdf_to_searchable_pdf(input_pdf_path, output_pdf_path,
                                  lang=LANGUAGE, dpi=DPI):
    """Convert a scanned (non-searchable) PDF into a searchable PDF.

    Pages are rasterized and OCR'd one at a time so memory use stays flat
    even for very large documents.
    """
    print(f"Processing scanned PDF: {input_pdf_path}")
    total_pages = pdfinfo_from_path(str(input_pdf_path))["Pages"]
    writer = PdfWriter()

    for page_num in range(1, total_pages + 1):
        print(f"OCR-ing page {page_num}/{total_pages}...")
        page_image = convert_from_path(
            str(input_pdf_path), dpi=dpi,
            first_page=page_num, last_page=page_num,
        )[0]
        writer.add_page(ocr_to_pdf_page(page_image, lang))

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
    print(f"Successfully created searchable PDF: {output_pdf_path}")


def make_searchable(input_path, output_path=None, lang=LANGUAGE, dpi=DPI):
    """Detect the input type and dispatch to the right converter."""
    input_path = Path(input_path)
    if not input_path.is_file():
        sys.exit(f"Error: input file not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_searchable.pdf")
    output_path = Path(output_path)

    if output_path.resolve() == input_path.resolve():
        sys.exit("Error: output path must differ from the input path.")

    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        scanned_pdf_to_searchable_pdf(input_path, output_path, lang, dpi)
    elif suffix in IMAGE_EXTENSIONS:
        image_to_searchable_pdf(input_path, output_path, lang)
    else:
        sys.exit(f"Error: unsupported file type '{suffix}'.")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a searchable PDF from an image or scanned PDF using OCR.")
    parser.add_argument("input", nargs="?", default=INPUT_PATH,
                        help="Input image or PDF")
    parser.add_argument("-o", "--output", default=None,
                        help="Output PDF path (default: <input>_searchable.pdf)")
    parser.add_argument("-l", "--lang", default=LANGUAGE,
                        help="Tesseract language code(s), e.g. eng or eng+spa")
    parser.add_argument("--dpi", type=int, default=DPI,
                        help="Rasterization DPI for PDF input (default: 300)")
    args = parser.parse_args()

    # With no CLI arguments at all, fall back to the OUTPUT_PATH default
    output = args.output
    if output is None and len(sys.argv) == 1:
        output = OUTPUT_PATH

    check_dependencies()
    make_searchable(args.input, output, args.lang, args.dpi)


if __name__ == "__main__":
    main()
