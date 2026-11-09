from pathlib import Path
from xml.sax.saxutils import escape
import math

out = Path("/mnt/data")
out.mkdir(exist_ok=True)

# Original process-flow drawing; dimensions and performance are conceptual.
W, H = 1500, 1130
parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
<path d="M0,0 L8,3 L0,6 Z" fill="#526777"/></marker></defs>
<rect width="1500" height="1130" fill="#f7faf9"/>
<style>text{{font-family:Arial,sans-serif;fill:#17332f}}
.title{{font-size:34px;font-weight:700}} .sub{{font-size:19px;fill:#526777}}
.head{{font-size:22px;font-weight:700}} .body{{font-size:19px}}
.small{{font-size:17px;fill:#526777}}</style>''']

def text(x, y, content, css="body"):
    parts.append(f'<text x="{x}" y="{y}" class="{css}">{escape(content)}</text>')

def box(x, y, w, h, title, lines, fill="#ffffff", stroke="#b4c6bf"):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    text(x+20, y+34, title, "head")
    for i, line in enumerate(lines):
        text(x+20, y+65+i*27, line)

def arrow(coords, dashed=False):
    d = "M " + " L ".join(f"{x},{y}" for x,y in coords)
    dash = ' stroke-dasharray="8 6"' if dashed else ""
    parts.append(f'<path d="{d}" fill="none" stroke="#526777" stroke-width="3"{dash} marker-end="url(#arrow)"/>')

text(45, 55, "THREE-ADULT ECOSAN • CONCEPTUAL TREATMENT TRAIN", "title")
text(45, 87, "Separate nutrients at source. Treat closed batches. Release only after verification.", "sub")

box(530,115,440,125,"WATERLESS DIVERTING TOILET",
    ["Gravity separation; dedicated vent", "Urine: design 6 L/day | feces: 0.6 kg/day"], "#e3eee9")
arrow([(600,240),(600,273),(290,273),(290,305)])
arrow([(900,240),(900,273),(1110,273),(1110,305)])
text(115,288,"URINE LINE", "small")
text(870,288,"FECES + PAPER LINE", "small")

box(45,305,560,155,"ISOLATED URINE BATCH TANKS",
    ["6 × 500 L nominal; 450 L working each",
     "Date, level and temperature records",
     "No top-ups after a batch is closed"], "#fff3d5", "#ccb77f")
box(790,305,665,155,"COVERED COLLECTION + CO-COMPOST FEED",
    ["Local straw / shavings + wet kitchen / garden residues",
     "Plan 4–8 L/day total mix; confirm with household data",
     "Three 700 L bins: filling / active / spare-turning"], "#e8eee0")
arrow([(325,460),(325,500)])
arrow([(1110,460),(1110,500)])
box(45,500,560,175,"URINE HYGIENIZATION GATE  [3,11]",
    ["Storage: ≥6 months at ≥20°C after closure",
     "Cold climate: validated solar/waste-heat pasteurizer",
     "80°C for ≥90 seconds at the coldest point",
     "Cold storage alone does not meet the warm criterion"], "#fff3d5", "#ccb77f")
box(790,500,665,175,"INSULATED AEROBIC BATCH TREATMENT  [4,5]",
    ["Target 50–60% moisture; controlled low-power air",
     "Bacterial starter: screened compost strains (trial)",
     "Validate ≥55°C for ≥72 h throughout the batch",
     "Cold spots or missing records → HOLD / REPROCESS"], "#e8eee0")
arrow([(325,675),(325,755)])
arrow([(1110,675),(1110,715)])
box(790,715,665,155,"COOLING + FUNGAL CURING  [7–10]",
    ["Only after verified heat treatment; no fresh feces",
     "Screened fungal starter below its temperature limit",
     "4 × 600 L curing bins; allow ~6 months initially"], "#e8eee0")
box(45,755,560,115,"PRODUCT A • LIQUID FERTILIZER",
    ["Release only after treatment gate passes",
     "Soil-test-based dose; incorporate, do not spray"], "#d7e9df")
arrow([(1110,870),(1110,910)])
box(790,910,665,115,"PRODUCT B • MATURE SOIL AMENDMENT",
    ["Process records + stability + accredited-lab testing",
     "Food-garden use only if locally permitted and verified"], "#d7e9df")
box(45,910,560,115,"CONTAIN ALL SIDE STREAMS",
    ["Leachate / dirty rinse → untreated batch before heat",
     "Exhaust → odor biofilter → outdoor vent"], "#e7edf0")
arrow([(735,565),(680,565),(680,950),(605,950)], dashed=True)
arrow([(790,565),(735,565)], dashed=True)

text(45,1070,"Design allowances, not validated performance: ~50–150 Wh/day electricity (no heating); ~12–18 m² service area.", "small")
text(45,1097,"No flush water. Handwashing still needs safe water. References [1–12] and limitations are in the accompanying brief.", "small")
parts.append("</svg>")
svg_path = out / "ecosan_concept.svg"
svg_path.write_text("\n".join(parts))

import cairosvg
png_path = out / "ecosan_concept.png"
cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))

# A compact, paginated PDF brief with explicit source identifiers.
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="BriefTitle", fontName="Helvetica-Bold", fontSize=23,
                         leading=27, textColor=colors.HexColor("#17332f"), spaceAfter=15))
styles.add(ParagraphStyle(name="BriefH", fontName="Helvetica-Bold", fontSize=13,
                         leading=17, textColor=colors.HexColor("#245749"), spaceBefore=12, spaceAfter=7))
styles.add(ParagraphStyle(name="BriefBody", fontSize=10, leading=14, spaceAfter=8))
styles.add(ParagraphStyle(name="BriefSmall", fontSize=8.5, leading=11, spaceAfter=7))
story = []
def p(t, style="BriefBody"):
    story.append(Paragraph(t, styles[style]))
def h(t): p(t,"BriefH")
def page(): story.append(PageBreak())

p("Home-scale ecosanitation<br/>Three-adult conceptual design", "BriefTitle")
p("Research/design brief • 25 September 2026 • Concept only, not construction approval", "BriefSmall")
p("<b>Recommendation:</b> use a waterless urine-diverting toilet, isolated urine-treatment batches, insulated aerobic co-composting, and a separate fungal-curing stage. Recover two products: a nitrogen-rich liquid fertilizer and a stabilized organic soil amendment. [1–5]")
p("<b>Important limitation:</b> no located study validates this complete home-scale combination as a rapid, year-round, low-energy sanitizer. Specialized inoculants are a potentially useful enhancement, not the pathogen-control barrier. Soil-like appearance and odor are not proof of safety. [5,7–10]")
story.append(Image(str(png_path), width=490, height=490*H/W))
h("System boundary")
p("Includes the toilet, contained collection, urine storage or pasteurization, solids treatment, curing, exhaust control, contaminated-liquid capture, and nutrient-use planning. It excludes whole-house greywater treatment. Safe handwashing water remains essential. Carbon-rich residues, some co-feed, maintenance, and external laboratory verification are required; this is not a sealed or maintenance-free ecosystem. [1,2]")
page()

p("1 | Design basis and equipment", "BriefTitle")
p("All sizes below are engineering allowances for an initial prototype, not published performance specifications. Measure actual household inputs for at least two weeks before final sizing. Excretion varies substantially with diet and fluid intake. [6]")
rows = [
["Item", "Concept allowance"],
["Urine design flow", "6 L/day total; 2,190 L/year"],
["Wet feces design flow", "0.6 kg/day total; 219 kg/year; allow peaks"],
["Total solids co-compost feed", "4–8 L/day including paper, cover and co-feed"],
["Primary batch vessels", "3 × 700 L nominal; ~450 L working each"],
["Batch filling interval", "Up to 56 days; 8 × 56 = 448 L maximum"],
["Curing capacity", "4 × 600 L nominal; ~500 L working each"],
["Urine storage", "6 × 500 L nominal; 450 L usable each = 2,700 L"],
["Routine electrical allowance", "50–150 Wh/day = 18–55 kWh/year; no heating"],
["Service-area allowance", "Approximately 12–18 m², excluding garden and toilet"],
]
table_data = [[Paragraph(escape(c), styles["BriefSmall"]) for c in row] for row in rows]
tab = Table(table_data, colWidths=[185,305])
tab.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e3eee9")),
    ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#c7d3cd")),
    ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),6),
    ("BOTTOMPADDING",(0,0),(-1,-1),5)
]))
story.append(tab)
h("Physical arrangement")
p("Use a roofed, flood-protected service enclosure with an impermeable, curbed work surface and spill capture. Separate dirty collection tools and raw-material access from cured-product handling. Fit pest-proof lids, screened vents, accessible cleanouts, and temperature-compatible vessel liners. Use sound reclaimed materials only when their former contents are known to be nonhazardous. [1,2]")
p("Route urine by gravity through accessible, continuously sloped plumbing into individually valved tanks. Keep tanks covered, compatible with urine, and equipped with engineered pressure equalization and overflow containment; never use a pressure-tight improvised heated vessel. Put each batch's closing date and treatment status on its valve.")
p("For feces, use a direct chute into the filling bin where layout permits, or small reusable transfer containers. Use local chopped straw, leaves and untreated shavings rather than peat or imported coir. Include wet kitchen/green residues as needed; do not assume feces alone will sustain the heat requirement. The 4–8 L/day allowance must include all co-feeds. [1,2,7]")
h("Capacity check")
p("An eight-week, 448 L maximum batch fits a 450 L working volume. One vessel fills while another completes active treatment; the third permits turning or quarantining a failed batch. At one batch every eight weeks, four 500 L working curing bins accommodate roughly six months without relying on volume shrinkage. If treatment stalls or input exceeds design, stop transfer and use reserved containment or an authorized backup service.")
page()

p("2 | Treatment and microbial strategy", "BriefTitle")
h("A. Insulated aerobic co-composting")
p("At batch closure, adjust porosity and moisture; use 50–60% moisture and initial C:N around 25–30:1 as commissioning targets, not a fixed scoop recipe. Use a perforated aeration floor, condensate/leachate capture, insulated walls and lid, and low-power controlled airflow. Record multiple temperatures, including the center, wall zones and base. [2,5]")
p("Plan 4–8 weeks of active treatment after closure as a trial target, not a guaranteed completion time. Refill the next vessel, never the closed treatment batch. Collection time must not be counted as a validated closed-batch hygiene hold.")
h("B. Bacterial and fungal inoculation: separate roles")
p("<b>Early phase:</b> trial a documented, screened compost inoculant containing cellulolytic/proteolytic bacteria such as suitable <i>Bacillus subtilis</i> strains. A verified mature compost starter is the lower-input baseline. Organism names alone do not establish strain safety or efficacy; do not culture raw feces or copy unscreened research consortia. [7,8]")
p("<b>Cooling phase:</b> after verified heat treatment, trial a screened lignocellulose-degrading fungal inoculant. <i>Phanerochaete chrysosporium</i> is a research candidate, not a proven off-the-shelf home-sanitation product. Introduce only below the supplier's strain-specific temperature limit; a conservative trial ceiling is 35–40°C. Its primary target is the plant-fiber fraction. [9]")
p("<b>Evidence:</b> a 2020 cattle-manure experiment improved decomposition and maturity but did not significantly shorten composting time. A 2026 experiment supports phase-specific consortia. A 2015 drum experiment found post-thermophilic fungal addition more effective than initial addition, but used agricultural waste rather than household feces. [7–9]")
p("Do not apply a universal inoculum dose or promise a percentage acceleration: the substrates, strains and test conditions differ. Compare sequential matched batches against a no-specialized-inoculant baseline, measuring temperature, stabilization time and handling effort. Keep all batches under the same sanitation requirements.")
h("C. Pathogen-control gate")
p("As a process benchmark, U.S. Part 503 specifies at least 55°C for three days for in-vessel/aerated-static composting; the windrow benchmark is at least 55°C for 15 days with five turnings. These are not automatic authorization or Class A certification for a DIY toilet. [4]")
p("Validate the entire batch, not just a hot center: use cold-spot mapping, calibrated logging and a demonstrated mixing/aeration method. If any zone fails, retain and reprocess the batch; extending calendar age alone is not equivalent. Keep dirty rinse water and leachate upstream of the validated heat step. [5]")
h("D. Curing")
p("Initially allow approximately six months of separate, covered curing after successful active treatment. This is a design reserve, not a pathogen guarantee. Maintain aeration and enough moisture for maturation; prevent recontamination. Require process verification, stability/maturity assessment and accredited-laboratory testing before release. [2,5,10]")
page()

p("3 | Urine, energy and garden use", "BriefTitle")
h("Urine: choose a climate-appropriate treatment route")
p("<b>Warm-storage route:</b> hold each closed batch for at least six months at 20°C or warmer, consistent with WHO's larger-system guidance. Its stated urine-mixture conditions include pH at least 8.8 and nitrogen at least 1 g/L; heavy fecal contamination invalidates the simple assumption. Do not acidify this treatment stream. The clock starts after the last addition. [3]")
p("Six tanks with 450 L working capacity hold 2,700 L. At 6 L/day, a tank fills in 75 days. A conservative capacity allowance for 182 days of treatment, 180 days without application, and a 75-day fill interval is 6 × (182 + 180 + 75) = 2,622 L. Verify the actual climate and agricultural calendar; calendar capacity is not proof of adequate temperature.")
p("<b>Cold-climate alternative:</b> use an engineered, validated solar-thermal or waste-heat pasteurization module. Rich Earth reports 80°C for 90 seconds for its urine process. Verify the coldest liquid location and prevent contamination afterward. This concept does not prescribe building a pressure vessel. [11]")
p("The ideal heat to raise 6 L/day from 20°C to 80°C is 6 × 4.18 × 60 / 3,600 = <b>0.418 kWh thermal/day</b>, before losses and without heat recovery. Electric resistance heating would add about 153 kWh/year before losses. Thus low-electricity cold-climate operation requires a reliable non-electric heat source, heat recovery, or a revised operating plan.")
h("Resource budget")
p("A sample electrical budget is 2 W continuous ventilation + a 10 W blower for four hours/day + 0.5 W logging = 100 Wh/day, or 36.5 kWh/year. This is only a preliminary load budget: verify airflow and pressure against the compost and biofilter, and include winter ventilation heat loss. Solar PV and storage must be sized for local winter conditions.")
p("Use zero flush water. Rainwater can supply process-moisture adjustments and suitable equipment washing, with contaminated rinse captured upstream of treatment. Do not use untreated rainwater as a substitute for safe handwashing water. Count any cleaning, supplemental heat and irrigation demand explicitly. [1,2]")
h("Fertilizer release and use")
p("Compost release requires successful process records plus stability/maturity checks and locally required pathogen testing. A germination test is a phytotoxicity check, not a pathogen test. During commissioning, do not use feces-derived compost on edible crops. Obtain local approval before any food-garden use. [2,5]")
p("Apply qualified urine to soil at a nutrient-based rate, not a disposal rate; avoid foliage and promptly incorporate it. Use soil testing and crop nutrient demand. For raw-eaten crops, WHO advises at least a month between urine application and harvest. Watch salt accumulation, especially under arid or greenhouse conditions. [3,11]")
p("Illustration only: at an assumed measured urine concentration of 6 g N/L, 1,640 L/year contains 9.84 kg N. At 10 g N/m²/year that corresponds to about 984 m² before other fertilizers and losses. A small vegetable bed may therefore be unable to absorb all three adults' nutrients. Secure sufficient planted area or an authorized outlet.")
p("Do not claim removal of all pharmaceuticals, PFAS or other persistent chemicals. Nutrient recovery and pathogen reduction are not complete chemical purification. Advanced urine systems exist, but their energy, consumable and maintenance demands need separate evaluation. [11,12]")
page()

p("4 | Evidence, limits and next steps", "BriefTitle")
h("Why this configuration")
p("Source separation avoids mixing the main liquid nutrient stream into the solids process. Batch operation makes treatment age traceable. Insulation and co-feeds address heat loss and low fecal loading. A distinct cooling/curing stage allows fungal activity without relying on fungi for sanitation. These are design inferences assembled from sanitation guidance and manure studies, not a tested integrated product. [1–10]")
h("Alternatives not selected as the baseline")
p("<b>Dehydration vaults:</b> useful for low-water containment but not synonymous with rapid composting. <b>Anaerobic digestion:</b> adds gas handling and still requires a hygienization plan. <b>Worms or fermentation alone:</b> do not replace a validated pathogen barrier. <b>Urine concentration:</b> alkaline dehydration and nitrification-based recovery are promising, but add process control or consumables beyond simple storage. [1,2,12]")
h("Operational fail-safes")
p("Keep children and animals out; use dedicated gloves/tools and avoid dusty handling. Cover each new fecal deposit, inspect tank levels and drainage, and review logged temperatures. Service air passages and odor media before restriction becomes severe. A biofilter controls odor; it is not a validated sterilizer. [1,2]")
p("A failed temperature hold, overflow, uncertain batch identity, severe fecal contamination of urine, pest ingress, or laboratory failure triggers HOLD. Retain material in protected containment and follow an approved retreatment or disposal route. Never drain untreated leachate or overflow to the garden.")
h("Commissioning decisions")
p("1. Obtain local sanitation and land-application requirements.<br/>"
  "2. Measure inputs and confirm all co-feed availability year-round.<br/>"
  "3. Establish winter heat balance and urine-treatment route.<br/>"
  "4. Have an experienced sanitation engineer validate containment, air delivery and cold spots.<br/>"
  "5. Agree on sampling and release criteria with an accredited laboratory.<br/>"
  "6. Run baseline batches before evaluating specialized inoculants.<br/>"
  "7. Confirm enough land and crop demand for both liquid and solid products.")
h("What the design can and cannot promise")
p("It provides a coherent low-water, low-electricity process architecture for three adults, with preliminary capacity allowances. It cannot honestly promise garden-ready fertilizer in days, complete chemical removal, zero outside inputs, or year-round hygienization in every climate. If local biomass, heat or land are insufficient, change those constraints or use a shared/authorized treatment service.")
page()

p("5 | Located references", "BriefTitle")
refs = [
("1", "Tilley, E. et al. (2014). <i>Compendium of Sanitation Systems and Technologies</i>, 2nd revised ed. Eawag/Sandec. Free official manual; separation, collection and treatment-chain options.",
 "https://www.eawag.ch/en/department/sandec/publications/compendium/"),
("2", "Strande, L., Ronteltap, M. &amp; Brdjanovic, D., eds. (2014). <i>Faecal Sludge Management: Systems Approach for Implementation and Operation.</i> IWA/Eawag. Free textbook, especially treatment mechanisms, end use and operations.",
 "https://www.eawag.ch/en/department/sandec/publications/fsm-book/"),
("3", "WHO (2006). <i>Guidelines for the Safe Use of Wastewater, Excreta and Greywater</i>, Vol. 4, <i>Excreta and Greywater Use in Agriculture.</i> Tables 5.2–5.3; storage conditions and exposure barriers.",
 "https://iris.who.int/bitstream/handle/10665/78265/9241546824_eng.pdf"),
("4", "U.S. eCFR. <i>40 CFR Part 503, Appendix B: Pathogen Treatment Processes.</i> Official regulatory process benchmarks; not a DIY approval.",
 "https://www.ecfr.gov/current/title-40/chapter-I/subchapter-O/part-503/appendix-Appendix%20B%20to%20Part%20503"),
("5", "U.S. EPA. <i>Pathogens and Vector Attraction in Sewage Sludge.</i> Official guidance; whole-mass temperature monitoring, cold spots and release verification.",
 "https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P1017HWO.TXT"),
("6", "Rose, C., Parker, A., Jefferson, B. &amp; Cartmell, E. (2015). <i>The Characterization of Feces and Urine: A Review of the Literature to Inform Advanced Treatment Technology.</i> 45:1827–1879. DOI: 10.1080/10643389.2014.1000761. Open-access characterization review.",
 "https://pubmed.ncbi.nlm.nih.gov/26246784/"),
("7", "Li, J. et al. (2020). <i>Inoculation of cattle manure with microbial agents increases efficiency and promotes maturity in composting.</i> 3 Biotech 10:128. DOI: 10.1007/s13205-020-2127-4. Open-access primary experiment.",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC7035406/"),
("8", "Li, H., Zeng, W., Huang, J. &amp; Tan, S. (2026). <i>Enhancing cow manure composting via staged inoculation of functional microbial consortia.</i> Frontiers in Microbiomes 5:1855343. Published 11 August 2026. DOI: 10.3389/frmbi.2026.1855343. Open-access primary experiment.",
 "https://www.frontiersin.org/journals/microbiomes/articles/10.3389/frmbi.2026.1855343/full"),
("9", "Varma, V. S., Ramu, K. &amp; Kalamdhad, A. S. (2015). <i>Carbon decomposition by inoculating Phanerochaete chrysosporium during drum composting of agricultural waste.</i> Environmental Science and Pollution Research 22:7851–7858. DOI: 10.1007/s11356-014-3989-y. Public abstract reviewed; open full text not verified.",
 "https://pubmed.ncbi.nlm.nih.gov/25567055/"),
("10", "Piceno, Y. M. et al. (2017). <i>Bacterial community structure transformed after thermophilically composting human waste in Haiti.</i> PLOS ONE 12:e0177626. DOI: 10.1371/journal.pone.0177626. Open-access primary human-excreta study.",
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC5453478/"),
("11", "Rich Earth Institute (2026). <i>Urine My Garden: Gardener Guide to Fertilizing with Urine.</i> Open practitioner guidance; collection, treatment, application and salts.",
 "https://richearthinstitute.org/wp-content/uploads/2026/02/Urine-My-Garden-2026-Plain-Text-1.pdf"),
("12", "Eawag. <i>Blue Diversion Autarky – Wastewater Treatment off the Grid.</i> Official research project and linked publications, including <i>On-site urine treatment combining Ca(OH)2 dissolution and dehydration with ambient air</i> (2021), Water Research X 13:100124, DOI: 10.1016/j.wroa.2021.100124.",
 "https://www.eawag.ch/en/research/humanwelfare/wastewater/projects/autarky/")
]
for num, citation, url in refs:
    p(f'<b>[{num}]</b> {citation} <link href="{escape(url, {chr(34): "&quot;"})}" color="#245749">Source</link>', "BriefSmall")

pdf_path = out / "ecosan_design_brief.pdf"
def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor("#c7d3cd"))
    canvas.line(45,40,A4[0]-45,40)
    canvas.setFont("Helvetica",8)
    canvas.setFillColor(colors.HexColor("#526777"))
    canvas.drawString(45,27,"Three-adult ecosan | Conceptual design — validation required")
    canvas.drawRightString(A4[0]-45,27,str(doc.page))

doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=45, rightMargin=45,
                        topMargin=42, bottomMargin=54)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print("Created: ecosan_design_brief.pdf, ecosan_concept.svg, ecosan_concept.png")
