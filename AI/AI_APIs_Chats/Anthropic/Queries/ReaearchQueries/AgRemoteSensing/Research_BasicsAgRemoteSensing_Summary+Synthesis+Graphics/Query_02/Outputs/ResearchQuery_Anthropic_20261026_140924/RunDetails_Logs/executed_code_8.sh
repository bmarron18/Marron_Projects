cd /tmp/deliverables && cat > README.txt <<'EOF'
Satellite Data for Agriculture and Soil Health - Deliverables (October 2026)

01_High_Level_Summary_Satellite_Data_in_Agriculture.pdf   - Task 1: high-level summary of current uses
02_Detailed_Account_Acquisition_Processing_Evaluation.pdf - Task 2: detailed account (acquisition, processing, modelling, evaluation)
make_infographic.py                                       - Task 3: stand-alone script; run `python make_infographic.py` to regenerate the JPEG
satellite_ag_infographic.jpeg                             - Task 3: infographic output (16 x 20 in @ 200 dpi)
03_Foundational_and_Canonical_References.pdf              - Task 4: foundational/canonical references with DOIs and open-access flags
04_Public_Satellite_Data_Sources.pdf                      - Task 5: public satellite and ancillary soil data sources
build_pdfs.py                                             - script used to generate the four PDFs (reportlab)

Dependencies: Python 3.8+, matplotlib, Pillow (infographic); reportlab (PDFs).
EOF
cp -r /tmp/deliverables/* "$OUTPUT_DIR"/ && ls "$OUTPUT_DIR"