#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 18:48:06 2026

@author: bruce-vdb, claude-opus-5.5

Brundtland Report infographic: The concept of sustainable development
Source: Report of the World Commission on Environment and Development:
        Our Common Future (United Nations, 1987), Chairman's Foreword & Overview.

Requirements: matplotlib (>= 3.3) and Pillow (needed for JPEG output)
    pip install matplotlib pillow
Run:
    python brundtland_infographic.py
Output:
    brundtland_sustainable_development_infographic.jpg
"""

import textwrap
import matplotlib
matplotlib.use("Agg")  # render without a display
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, FancyArrowPatch

# ----------------------------------------------------------------------------
# Canvas: 12 x 20 inches at 150 dpi -> 1800 x 3000 px.
# Data coordinates are 120 x 200 units, so 1 unit = 0.1 inch in both axes.
# ----------------------------------------------------------------------------
W, H = 120, 200
OUTFILE = "brundtland_sustainable_development_infographic.jpg"

# Palette
BG     = "#F5F7F2"
NAVY   = "#12355B"
GREEN  = "#2E8B57"
BLUE   = "#1F6FB2"
ORANGE = "#E07A1F"
TEAL   = "#178F8F"
DARK   = "#1E2A36"
GREY   = "#5B6670"
LIGHTG = "#E3F1E7"

fig = plt.figure(figsize=(12, 20), dpi=150, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
ax.set_facecolor(BG)


# ----------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------
def wrap(s, width):
    """Wrap each paragraph separately so blank lines are preserved."""
    return "\n".join(textwrap.fill(p, width) if p else "" for p in s.split("\n"))


def T(x, y, s, size=12, color=DARK, weight="normal", ha="center", va="center",
      style="normal", width=None, ls=1.3, z=5):
    if width:
        s = wrap(s, width)
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            fontstyle=style, linespacing=ls, zorder=z)


def rbox(x, y, w, h, fc, ec="none", lw=0, r=1.5, alpha=1.0, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z))


def heading(y, text, color=NAVY):
    ax.add_patch(Rectangle((4.5, y - 1.3), 0.9, 2.6, fc=color, ec="none", zorder=3))
    T(6.6, y, text, size=15, color=color, weight="bold", ha="left")


# ----------------------------------------------------------------------------
# 1. Header
# ----------------------------------------------------------------------------
ax.add_patch(Rectangle((0, 186), W, 14, fc=NAVY, ec="none", zorder=1))
T(60, 195.3, "SUSTAINABLE DEVELOPMENT", size=36, color="white", weight="bold")
T(60, 189.6, "The central concept of the Brundtland Report, Our Common Future "
             "(World Commission on Environment and Development, 1987)",
  size=13, color="#CFE3F5")

# ----------------------------------------------------------------------------
# 2. Core definition (para. 27)
# ----------------------------------------------------------------------------
rbox(6, 167, 108, 16, fc=LIGHTG, ec=GREEN, lw=2.5, r=2)
T(10.5, 179.5, "\u201C", size=70, color=GREEN, weight="bold")
T(61, 176.3,
  "Humanity has the ability to make development sustainable \u2014 to ensure that "
  "it meets the needs of the present without compromising the ability of "
  "future generations to meet their own needs.",
  size=16.5, color=DARK, weight="bold", style="italic", width=68)
T(110, 169.3, "\u2014 Our Common Future, Overview, para. 27",
  size=10.5, color=GREY, ha="right")

# ----------------------------------------------------------------------------
# 3. Present <-> future generations bridge
# ----------------------------------------------------------------------------
rbox(6, 150, 38, 14, fc="white", ec=BLUE, lw=2.5, r=1.5)
T(25, 160.6, "THE PRESENT", size=15, color=BLUE, weight="bold")
T(25, 155, "Meet the needs of today\u2019s people \u2014 beginning with the basic "
           "needs of all", size=11.5, width=32)

rbox(76, 150, 38, 14, fc="white", ec=GREEN, lw=2.5, r=1.5)
T(95, 160.6, "FUTURE GENERATIONS", size=15, color=GREEN, weight="bold")
T(95, 155, "Preserve their ability to meet their own needs",
  size=11.5, width=30)

ax.add_patch(FancyArrowPatch((45.5, 154.5), (74.5, 154.5), arrowstyle="<|-|>",
                             mutation_scale=28, lw=3.5, color=ORANGE, zorder=4))
T(60, 159.3, "WITHOUT\nCOMPROMISING", size=12, color=ORANGE, weight="bold")

T(60, 146.6, "\u201CWe borrow environmental capital from future generations with "
             "no intention or prospect of repaying.\u201D \u2014 para. 25",
  size=11, color=GREY, style="italic")

# ----------------------------------------------------------------------------
# 4. Environment + development: inseparable (Venn)
# ----------------------------------------------------------------------------
heading(141.5, "ENVIRONMENT + DEVELOPMENT \u2014 \u201CTHE TWO ARE INSEPARABLE\u201D")

ax.add_patch(Circle((50, 120), 18, fc=GREEN, ec="white", lw=3, alpha=0.75, zorder=2))
ax.add_patch(Circle((70, 120), 18, fc=BLUE, ec="white", lw=3, alpha=0.70, zorder=2))

T(41.5, 124, "ENVIRONMENT", size=13, color="white", weight="bold")
T(41.5, 117.5, "\u201Cwhere we all live\u201D", size=10.5, color="white",
  style="italic", width=14)
T(78.5, 124, "DEVELOPMENT", size=13, color="white", weight="bold")
T(78.5, 116.8, "\u201Cwhat we all do in attempting to improve our lot\u201D",
  size=10, color="white", style="italic", width=16)
T(60, 120, "SUSTAINABLE\nDEVELOPMENT", size=10.5, color="white", weight="bold")

# side notes
T(16, 120, "\u201CPoverty is a major cause and effect of global environmental "
           "problems.\u201D\n\u2014 para. 8",
  size=11, color=DARK, style="italic", width=24)
T(104, 120, "Environmental, development and energy crises:\n\u201CThese are not "
            "separate crises\u2026 They are all one.\u201D\n\u2014 para. 11",
  size=11, color=DARK, style="italic", width=24)
T(60, 99.8, "Source of heading quote: Chairman\u2019s Foreword",
  size=9, color=GREY)

# ----------------------------------------------------------------------------
# 5. Three key ideas: Needs, Limits, Equity (paras. 27-29)
# ----------------------------------------------------------------------------
heading(96, "THREE KEY IDEAS INSIDE THE CONCEPT")

cards = [
    ("NEEDS", ORANGE,
     "Meet the basic needs of all, and extend to all the opportunity to fulfil "
     "their aspirations for a better life.\n\n"
     "Poverty is an evil in itself, and \u201Ca world in which poverty is endemic "
     "will always be prone to ecological and other catastrophes.\u201D"),
    ("LIMITS", TEAL,
     "Not absolute limits, but limits imposed by the present state of technology "
     "and social organization, and by the biosphere\u2019s ability to absorb the "
     "effects of human activities.\n\n"
     "Population size and growth must be in harmony with the ecosystem\u2019s "
     "changing productive potential."),
    ("EQUITY", BLUE,
     "The poor must get their fair share of the resources required to sustain "
     "growth.\n\n"
     "The affluent must adopt life-styles within the planet\u2019s ecological "
     "means, for example in their use of energy.\n\n"
     "Aided by effective citizen participation and greater democracy in "
     "international decision making."),
]
card_w, card_y, card_h = 34, 65, 28
for i, (title, col, body) in enumerate(cards):
    x = 4 + i * (card_w + 5)
    rbox(x, card_y, card_w, card_h, fc="white", ec=col, lw=2.2, r=1.2, z=2)
    rbox(x, card_y + card_h - 6, card_w, 6, fc=col, r=1.2, z=3)
    ax.add_patch(Rectangle((x, card_y + card_h - 6), card_w, 2.5, fc=col,
                           ec="none", zorder=3))
    T(x + card_w / 2, card_y + card_h - 3, title, size=15, color="white",
      weight="bold", z=4)
    T(x + 1.8, card_y + card_h - 7.6, body, size=10.4, ha="left", va="top",
      width=40, ls=1.3)

# ----------------------------------------------------------------------------
# 6. A process of change, not a fixed state (para. 30)
# ----------------------------------------------------------------------------
heading(61.5, "A PROCESS OF CHANGE \u2014 NOT A FIXED STATE OF HARMONY")

steps = ["Exploitation of resources", "Direction of investments",
         "Orientation of technological development", "Institutional change"]
step_cols = [GREEN, TEAL, BLUE, NAVY]
cx, cy, cw, ch, notch = 6, 46.5, 27, 11, 3.2
for i, (label, col) in enumerate(zip(steps, step_cols)):
    x = cx + i * cw
    pts = [(x, cy), (x + cw - notch, cy), (x + cw, cy + ch / 2),
           (x + cw - notch, cy + ch), (x, cy + ch)]
    if i > 0:  # notch on the left for all but the first chevron
        pts.append((x + notch, cy + ch / 2))
    ax.add_patch(Polygon(pts, closed=True, fc=col, ec=BG, lw=2, zorder=2))
    T(x + cw / 2 + (notch / 2 if i > 0 else 0) - 0.8, cy + ch / 2, label,
      size=11, color="white", weight="bold", width=15)

T(60, 42.6, "\u2026all made consistent with FUTURE as well as PRESENT needs. "
            "\u201CPainful choices have to be made.\u201D \u2014 para. 30",
  size=12, color=DARK, style="italic")

# ----------------------------------------------------------------------------
# 7. Why it matters: the interlocking crises (1987 figures)
# ----------------------------------------------------------------------------
heading(37.5, "WHY IT MATTERS: THE INTERLOCKING CRISES (figures as reported in 1987)",
        color=ORANGE)

stats = [
    ("6M ha", "of productive dryland turns into desert every year", ORANGE),
    ("11M ha", "of forest destroyed every year", GREEN),
    ("80\u00D7", "more energy used per person in industrial market economies "
                 "than in sub-Saharan Africa", BLUE),
    ("5 \u2192 8\u201314 bn", "world population today vs. projected "
                             "stabilization next century", TEAL),
    ("$1 tn", "global military spending per year", NAVY),
]
tw, gap = 19.6, 2.1
start = (W - (5 * tw + 4 * gap)) / 2
for i, (big, small, col) in enumerate(stats):
    x = start + i * (tw + gap)
    rbox(x, 19.5, tw, 14, fc="white", ec=col, lw=2, r=1.2)
    T(x + tw / 2, 29.8, big, size=19 if len(big) < 8 else 15.5,
      color=col, weight="bold")
    T(x + tw / 2, 23.9, small, size=9.3, color=DARK, width=23)

T(60, 16.6, "Meanwhile, the gap between rich and poor nations is widening, not "
            "shrinking (para. 6).", size=11, color=GREY, style="italic")

# ----------------------------------------------------------------------------
# 8. Footer: political will and who must act
# ----------------------------------------------------------------------------
ax.add_patch(Rectangle((0, 0), W, 14.5, fc=NAVY, ec="none", zorder=1))
T(60, 10.8, "\u201CIn the final analysis, sustainable development must rest on "
            "political will.\u201D", size=15.5, color="white", weight="bold")
T(60, 6.6, "Who must act: Governments \u00B7 Private enterprise \u00B7 NGOs, "
           "educators & scientists \u00B7 People everywhere, especially the young",
  size=11, color="#CFE3F5")
T(60, 2.6, "Source: Report of the World Commission on Environment and Development: "
           "Our Common Future (United Nations, 1987, A/42/427), Chairman\u2019s "
           "Foreword & Overview.", size=8.5, color="#9FB6CC")

# ----------------------------------------------------------------------------
# Save as JPEG
# ----------------------------------------------------------------------------
fig.savefig(OUTFILE, format="jpeg", dpi=150, facecolor=BG,
            pil_kwargs={"quality": 95, "optimize": True})
plt.close(fig)
print(f"Infographic saved to: {OUTFILE}")


