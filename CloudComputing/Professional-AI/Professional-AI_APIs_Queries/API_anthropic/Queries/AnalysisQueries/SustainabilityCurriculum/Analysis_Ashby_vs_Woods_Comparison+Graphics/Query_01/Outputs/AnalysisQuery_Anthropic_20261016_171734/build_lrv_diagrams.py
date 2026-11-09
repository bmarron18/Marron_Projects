#!/usr/bin/env python3
"""Rebuild the two Law of Requisite Variety diagrams as JPEG files.

Usage:
    python build_lrv_diagrams.py [output_dir]

Requires: matplotlib, numpy, pillow  (pip install matplotlib numpy pillow)
Output:   LRV_resilience_framing.jpeg, LRV_vs_Woods_four_concepts.jpeg
"""
import os
import sys
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)


def wrap(s, w):
    return "\n".join(textwrap.fill(p, w, break_long_words=False) for p in s.split("\n"))


def box(ax, x, y, w, h, fc, ec, lw=2, r=0.8, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls))


def arrow(ax, p1, p2, color='#222', lw=2.5, ls='-', rad=0.0, ms=22):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=ms, color=color, lw=lw,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}"))


def node(ax, x, y, w, h, title, body, fc, ec, tw=24, bw=30, ts=12.5, bs=10.5, ls='-'):
    box(ax, x, y, w, h, fc, ec, ls=ls)
    ax.text(x + 0.8, y + h - 0.8, wrap(title, tw), ha='left', va='top', fontsize=ts, weight='bold', color=ec)
    nt = wrap(title, tw).count("\n") + 1
    ax.text(x + 0.8, y + h - 0.9 - nt * 1.75, wrap(body, bw), ha='left', va='top', fontsize=bs, color='#222',
            linespacing=1.25)


# =============================== DIAGRAM 1 ===============================
def diagram_1():
    fig = plt.figure(figsize=(20, 13), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 65)
    ax.axis('off')

    ax.text(50, 62.6, "The Law of Requisite Variety as a Theory of Resilience", ha='center', va='center',
            fontsize=25, weight='bold', color='#1f2d3d')
    ax.text(50, 60.2, 'Ashby (1956), An Introduction to Cybernetics, Ch. 11 — "only variety in R can force down the variety due to D; variety can destroy variety"',
            ha='center', va='center', fontsize=13, style='italic', color='#444')

    box(ax, 3, 52.6, 94, 6, '#eef3fb', '#2b5797')
    ax.text(22, 55.6, r"$V_E \;\geq\; V_D \;-\; \log k \;-\; V_R$", fontsize=27, ha='center', va='center', color='#2b5797')
    ax.text(67, 56.8, "Resilience condition: the residual variety must fit inside the viability set η",
            ha='center', va='center', fontsize=13.5, weight='bold', color='#1f2d3d')
    ax.text(67, 54.4, r"$V_D - \log k - V_R \;\leq\; \log|\eta|$      (varieties in bits;  $\log k$ = variety absorbed by the world $T$ alone, §11/9)",
            ha='center', va='center', fontsize=13)

    ax.text(34, 51.4, "The regulatory loop (§11/11, §11/14) read as a resilience system", ha='center', va='center',
            fontsize=13.5, weight='bold', color='#1f2d3d')

    # nodes
    node(ax, 4, 32, 16, 12.5, "D — Disturbances",
         "Variety V_D: shocks, loads, noise in T, unknown initial states — all folded into a vector D (§11/17–19).",
         '#fdecea', '#b03a2e')
    node(ax, 26, 40, 16, 10, "T — The 'Table' (the hard world)",
         "Given dynamics. Buffers, slack and margins absorb log k of D's variety passively (§11/9).",
         '#f4f6f7', '#5d6d7e', tw=22)
    node(ax, 26, 19.5, 16, 12, "R — Regulator",
         "Variety V_R = repertoire of distinct responses = adaptive capacity. Its strategy (a mapping D → R) must exist before D acts.",
         '#e8f1fb', '#2b5797')
    node(ax, 47, 32, 16, 12.5, "E — Essential variables",
         "Must stay inside η, the viability envelope; leaving η = failure. Only E is held constant — R itself may vary greatly (§11/15).",
         '#e9f7ef', '#1e8449')
    node(ax, 4, 19.5, 16, 9, "C — Goals / Controller",
         "Sets the target. Perfect regulation by R gives C complete control over E (§11/14).",
         '#fef9e7', '#9a7d0a')
    node(ax, 47, 19.5, 16, 10, "Variety deficit = brittleness",
         "If V_R is too small, residual variety passes through T to E: essential variables are driven out of η → collapse.",
         '#fdecea', '#b03a2e', ls='--')
    node(ax, 4, 46.2, 16, 4.4, "Model surprise",
         "Disturbances outside the modelled set: new rows of the table.", '#ffffff', '#b03a2e',
         ts=11, bs=9.5, bw=34, ls='--')

    # arrows
    arrow(ax, (12, 46.2), (12, 44.6), color='#b03a2e', ls='--')
    arrow(ax, (20, 41.5), (26, 45))
    ax.text(23, 47.3, "direct path\nD → T → E", ha='center', va='center', fontsize=10, color='#444')
    arrow(ax, (20, 35), (26, 29), color='#2b5797')
    ax.text(22.6, 36.2, "sensing channel D → R\n(its capacity bounds V_R)", ha='left', va='center', fontsize=10, color='#2b5797')
    arrow(ax, (34, 31.5), (34, 40), color='#2b5797', lw=3)
    ax.text(35, 33.6, "action channel R → T\n(counter-variety)", ha='left', va='center', fontsize=10, color='#2b5797')
    arrow(ax, (42, 45), (47, 41.5), color='#1e8449')
    ax.text(44.8, 46.6, "outcome", ha='center', va='center', fontsize=10, color='#1e8449')
    arrow(ax, (20, 24), (26, 24), color='#9a7d0a')
    ax.text(23, 25.2, "target", ha='center', va='center', fontsize=10, color='#9a7d0a')
    arrow(ax, (55, 29.5), (55, 32), color='#b03a2e', ls='--', ms=16)

    # levers panel
    ax.text(81.5, 51.4, "Five resilience levers implied by the law", ha='center', va='center', fontsize=13.5,
            weight='bold', color='#1f2d3d')
    levers = [
        ("Amplify regulator variety (↑ V_R)", "Broader response repertoire, redundancy, reserves, multiple modes of response — 'adaptive capacity'."),
        ("Absorb / attenuate disturbance (↑ log k)", "Buffers, margins and slack in T absorb variety passively — 'robustness by design'."),
        ("Widen the channels (sensing and acting)", "A regulator's capacity cannot exceed its capacity as a communication channel (§11/11; Shannon Th. 10)."),
        ("Redraw the system boundary", "Fold noise, initial states and newly recognised threats into D — which demands a more complex R (§11/18–19)."),
        ("Import variety before it is needed", "Curiosity, play, exploration (§11/13) build the repertoire ahead of the crisis' 'brutal audit'."),
    ]
    cols = ['#2b5797', '#5d6d7e', '#117a65', '#9a7d0a', '#7d3c98']
    for i, ((t, b), c) in enumerate(zip(levers, cols)):
        y = 44.4 - i * 6.4
        box(ax, 66, y, 31, 5.6, '#ffffff', c)
        ax.add_patch(Circle((68.3, y + 2.8), 1.25, color=c))
        ax.text(68.3, y + 2.8, str(i + 1), ha='center', va='center', color='white', fontsize=13, weight='bold')
        ax.text(70.4, y + 4.8, t, ha='left', va='top', fontsize=11.5, weight='bold', color=c)
        ax.text(70.4, y + 3.0, wrap(b, 66), ha='left', va='top', fontsize=10, color='#222', linespacing=1.2)

    # bottom text panel
    box(ax, 46, 2, 51, 15, '#f8f9f9', '#1f2d3d')
    ax.text(47.2, 16.0, "Reading the law through a resilience lens", ha='left', va='top', fontsize=13,
            weight='bold', color='#1f2d3d')
    bul = [
        "Necessity, not engineering: the law is combinatorial (§11/10) — no technology lets a regulator with less variety than its disturbances hold E constant.",
        "Capacity precedes the event: R's strategy is fixed before D plays; resilience is built in advance and then audited by the disturbance.",
        "Brittleness = variety deficit: whatever variety R and T fail to absorb is transmitted to the essential variables.",
        "Constancy of relations, not of states: a resilient regulator may change continuously (searchlight, steering) to hold one invariant.",
    ]
    ax.text(47.2, 13.6, "\n".join(wrap("• " + b, 110) for b in bul), ha='left', va='top', fontsize=11, linespacing=1.4)

    # chart
    ax2 = fig.add_axes([0.05, 0.045, 0.36, 0.195])
    vr = np.linspace(0, 7, 300)
    logk, eta = 1.0, 1.5
    ax2.fill_between(vr, eta, 7, color='#fdecea')
    ax2.fill_between(vr, 0, eta, color='#e9f7ef')
    for VD, col, lab in [(5, '#2b5797', r'routine disturbances ($V_D$ = 5 bits)'),
                         (7.5, '#c0392b', r'after a surprise ($V_D$ = 7.5 bits)')]:
        ax2.plot(vr, np.maximum(0, VD - logk - vr), color=col, lw=2.6, label=lab)
        need = VD - logk - eta
        ax2.axvline(need, color=col, ls=':', lw=1.8)
    ax2.axhline(eta, color='k', ls='--', lw=1.5)
    ax2.text(0.1, eta + 0.15, r"tolerance $\log|\eta|$", fontsize=9.5)
    ax2.text(2.6, 3.2, r"routine needs $V_R \geq 2.5$", fontsize=9.5, color='#2b5797')
    ax2.text(5.1, 3.2, "surprise needs\n" r"$V_R \geq 5$", fontsize=9.5, color='#c0392b')
    ax2.text(3.0, 5.7, "BRITTLE: E driven outside η", fontsize=10, color='#b03a2e', weight='bold')
    ax2.text(4.4, 0.45, "RESILIENT: E kept in η", fontsize=10, color='#1e8449', weight='bold')
    ax2.set_xlim(0, 7)
    ax2.set_ylim(0, 7)
    ax2.set_xlabel(r"Regulator variety $V_R$ (bits)", fontsize=10.5)
    ax2.set_ylabel(r"Minimum outcome variety $V_E$", fontsize=10.5)
    ax2.set_title("Resilience margin: the same regulator fails when surprise raises $V_D$  (log k = 1)",
                  fontsize=11, weight='bold')
    ax2.legend(loc='upper right', fontsize=8.5, bbox_to_anchor=(1.0, 0.86), framealpha=0.95)

    path = os.path.join(OUT_DIR, 'LRV_resilience_framing.jpeg')
    fig.savefig(path, dpi=150, pil_kwargs={'quality': 95})
    plt.close(fig)
    return path


# =============================== DIAGRAM 2 ===============================
def diagram_2():
    fig = plt.figure(figsize=(22, 15), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 75)
    ax.axis('off')

    ax.text(50, 72.6, "Ashby's Law of Requisite Variety vs. Woods' Four Concepts of Resilience", ha='center', va='center',
            fontsize=25, weight='bold', color='#1f2d3d')
    ax.text(50, 70.3, "Where the law explains each concept, where it converges, and where Woods' agenda moves beyond what the law holds fixed",
            ha='center', va='center', fontsize=13, style='italic', color='#444')

    box(ax, 2, 61.6, 96, 6.6, '#eef3fb', '#2b5797')
    ax.text(3.2, 67.4, "Common reference — Law of Requisite Variety (Ashby 1956)", ha='left', va='top',
            fontsize=14, weight='bold', color='#2b5797')
    ax.text(3.2, 65.0, wrap("Only variety can destroy variety:  V_E ≥ V_D − log k − V_R.  A combinatorial hard limit on any regulator R facing a given "
                            "disturbance set D through a fixed world T with target set η. Regulatory capacity cannot exceed channel capacity. "
                            "It is a necessary condition, stated for a known table — it says nothing about cost, time, learning, or how the table changes.", 205),
            ha='left', va='top', fontsize=11.5, linespacing=1.35)

    # spectrum
    ax.text(2, 57.2, "Distance from the\nlaw's explicit scope:", ha='left', va='center', fontsize=11.5,
            weight='bold', color='#1f2d3d')
    arrow(ax, (15, 57.2), (97.5, 57.2), color='#7f8c8d', lw=3)
    ax.text(15, 55.4, "inside: known D, fixed table T, given η", ha='left', va='center', fontsize=10, color='#555')
    ax.text(97.5, 55.4, "beyond: model surprise, changing T, co-evolving layered networks", ha='right', va='center',
            fontsize=10, color='#555')
    rowcol = {'R1': '#e67e22', 'R2': '#2e86c1', 'R3': '#229954', 'R4': '#8e44ad'}
    for x, k, lab in [(27, 'R2', 'R2  Robustness'), (44, 'R1', 'R1  Rebound'), (63, 'R3', 'R3  Graceful extensibility'),
                      (83, 'R4', 'R4  Sustained adaptability')]:
        ax.add_patch(Circle((x, 57.2), 0.75, color=rowcol[k], zorder=5))
        ax.text(x, 59.0, lab, ha='center', va='center', fontsize=11.5, weight='bold', color=rowcol[k])

    # matrix
    xs = [2, 14, 29, 49.5, 70, 90.5, 98]
    headers = ["Woods' concept", "Woods' core question", "Ashby / LRV counterpart", "Convergence",
               "Divergence (what the law does not capture)", "LRV coverage"]
    hy, hh = 50.6, 3.4
    for i, h in enumerate(headers):
        box(ax, xs[i], hy, xs[i + 1] - xs[i] - 0.3, hh, '#1f2d3d', '#1f2d3d', r=0.4)
        ax.text((xs[i] + xs[i + 1] - 0.3) / 2, hy + hh / 2, wrap(h, 26 if i < 5 else 10), ha='center', va='center',
                fontsize=11.5 if i < 5 else 10.5, color='white', weight='bold')

    rows = [
        ('R1', "Rebound", "rebound = resilience [1]",
         "Why do some systems recover from trauma or stressors and return to previous, normal functioning?",
         "Return of E to the acceptable set η. Ashby's compound target (§11/20) literally encodes rebound: 'if displaced by ±10° it shall return to the allowed range within one minute'. R's strategy is a mapping fixed before D acts.",
         "Both put the decisive factor before the event: Lagadec's 'brutal audit' (Woods) = testing whether V_R was already in place. Rebound is simply one component of a vector target η.",
         "Ashby holds a relation invariant, not a prior state (searchlight, §11/15) — consistent with Woods' rejection of 'return to equilibrium'. But the law is silent on how adapting transforms the system and on cumulative strain from repeated stretching.",
         2, "Partial: recasts rebound as a target specification"),
        ('R2', "Robustness", "robustness = resilience [2]",
         "How large is the set of disturbances the system can absorb? Optimise worst-case, not average, performance.",
         "The heart of the law: known disturbance set D, fixed T, regulator as mapping D → R; log k = passive absorption by T. Doyle's 'system X has property Y robust in sense Z to perturbation W' is exactly a table with D and η.",
         "Robust control is applied requisite variety for well-modelled disturbances. Both quantify coverage and are worst-case: every row of D must be answered.",
         "The law is a lower bound with no cost model, so it misses 'robust-yet-fragile': expanding coverage creates new vulnerabilities elsewhere. For Woods, resilience starts exactly where the disturbance set is NOT well modelled.",
         4, "Strong: the law is the theoretical floor of robustness"),
        ('R3', "Graceful extensibility", "opposite of brittleness = resilience [3]",
         "How does a system stretch, bringing extra adaptive capacity to bear, when surprise pushes it to and beyond its boundaries?",
         "The boundary is where V_D − log k − V_R exceeds log|η|; surprise = new rows of the table. Ashby's remedies: redraw boundaries, folding noise and initial states into D (§11/18–19); import surplus variety through curiosity and play (§11/13).",
         "Decompensation = regulator saturation as cascading disturbances outgrow V_R. Channel-capacity limits explain sensing and acting bottlenecks before collapse. Surplus variety = readiness-to-respond.",
         "The law bounds residual variety but not the SHAPE of degradation (cliff vs. slope), anticipation, or timing (critical slowing down). It assumes the table is given; Woods' focus is model surprise, where the table itself is wrong.",
         2, "Partial: the law locates the boundary; Woods studies behaviour at it"),
        ('R4', "Sustained adaptability", "architectures = resilience [4]",
         "What architectures and governance let layered networks keep adapting over many cycles of change, managing fundamental trade-offs?",
         "Regulation enables control: C → R → E (§11/14) is a layered relation. 'Hitler's control … just 1 man-power' (§11/13): a central regulator cannot match a society's variety. Species block variety from the gene-pattern.",
         "The law is precisely the kind of hard limit R4 says architectures must navigate. Distributing regulators across layers (Ostrom's polycentric governance) is the architectural way to reach requisite variety.",
         "The law is static and single-loop: D, T and η are fixed. R4 is reflexive — success triggers adaptation by neighbouring units, reshaping D and T; there are multiple trade-offs and scales. No account of how the regulator itself evolves.",
         1, "Foundational: a constraint, not an architecture"),
    ]
    rh, gap = 10.0, 0.35
    wraps = [None, 37, 53, 53, 53]
    for j, (key, name, tag, q, cp, cv, dv, lvl, covtxt) in enumerate(rows):
        y = hy - (j + 1) * (rh + gap)
        c = rowcol[key]
        light = '#fbfcfc' if j % 2 == 0 else '#f2f4f4'
        for i in range(6):
            fc = c if i == 0 else light
            box(ax, xs[i], y, xs[i + 1] - xs[i] - 0.3, rh, fc, c, lw=1.6 if i else 0, r=0.4)
        ax.text(xs[0] + 0.7, y + rh - 0.8, key, ha='left', va='top', fontsize=20, weight='bold', color='white')
        ax.text(xs[0] + 0.7, y + rh - 3.6, wrap(name, 13), ha='left', va='top', fontsize=13.5, weight='bold', color='white')
        ax.text(xs[0] + 0.7, y + 0.6, wrap(tag, 20), ha='left', va='bottom', fontsize=9.5, style='italic', color='white')
        for i, t in zip([1, 2, 3, 4], [q, cp, cv, dv]):
            ax.text(xs[i] + 0.6, y + rh - 0.7, wrap(t, wraps[i]), ha='left', va='top', fontsize=10.3,
                    linespacing=1.28, color='#1c1c1c')
        # coverage gauge
        gx = xs[5] + 0.8
        for s in range(4):
            ax.add_patch(FancyBboxPatch((gx + s * 1.55, y + rh - 2.6), 1.3, 1.6,
                                        boxstyle="round,pad=0,rounding_size=0.2",
                                        fc=c if s < lvl else '#ffffff', ec=c, lw=1.4))
        ax.text(gx, y + rh - 3.4, wrap(covtxt, 15), ha='left', va='top', fontsize=9.6, color='#1c1c1c', linespacing=1.25)

    # synthesis
    box(ax, 2, 1.2, 96, 7.6, '#fef9e7', '#9a7d0a')
    ax.text(3.2, 8.1, "Synthesis", ha='left', va='top', fontsize=14, weight='bold', color='#9a7d0a')
    syn = ("The Law of Requisite Variety is a NECESSARY condition for all four concepts — no system keeps its essential variables in η without matching variety — "
           "but it is not SUFFICIENT for any of the higher ones. Woods' progression R1 → R4 moves step by step from what the law assumes fixed (the disturbance set D, "
           "the table T, the target η and the regulator's repertoire) to how those assumptions break and are rebuilt over time. Ashby supplies the hard limit and a metric (bits); "
           "Woods supplies the empirical failure patterns (decompensation, brittleness, robust-yet-fragile trade-offs) and the architectural agenda for sustaining requisite variety "
           "in layered, co-evolving networks.")
    ax.text(3.2, 6.0, wrap(syn, 215), ha='left', va='top', fontsize=11.3, linespacing=1.38)

    path = os.path.join(OUT_DIR, 'LRV_vs_Woods_four_concepts.jpeg')
    fig.savefig(path, dpi=150, pil_kwargs={'quality': 95})
    plt.close(fig)
    return path


if __name__ == '__main__':
    for p in (diagram_1(), diagram_2()):
        print(f"{p}  ({os.path.getsize(p):,} bytes)")
