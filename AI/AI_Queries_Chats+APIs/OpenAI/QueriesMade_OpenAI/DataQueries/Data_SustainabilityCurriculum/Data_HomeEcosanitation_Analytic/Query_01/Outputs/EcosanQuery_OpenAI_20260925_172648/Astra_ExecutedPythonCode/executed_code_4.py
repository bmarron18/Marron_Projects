from pathlib import Path
print(list(Path("/mnt/data").glob("*")))
import fitz
d=fitz.open("/mnt/data/ecosan_design_brief.pdf")
len(d), [(i+1,len(p.get_text()), p.get_text()[:55]) for i,p in enumerate(d)]
