cd /tmp/deliverables && python3 -c "
import pypdf
r=pypdf.PdfReader('02_Detailed_Account_Acquisition_Processing_Evaluation.pdf')
t=r.pages[0].extract_text()
import re
print([m for m in re.findall(r'.{10}(?:&|8-14).{12}', t)][:5])
r2=pypdf.PdfReader('01_High_Level_Summary_Satellite_Data_in_Agriculture.pdf')
print(re.findall(r'.{8}R2.{8}|.{8}R\n?2 .{8}', r2.pages[1].extract_text())[:2])
"; rm -rf __pycache__; ls