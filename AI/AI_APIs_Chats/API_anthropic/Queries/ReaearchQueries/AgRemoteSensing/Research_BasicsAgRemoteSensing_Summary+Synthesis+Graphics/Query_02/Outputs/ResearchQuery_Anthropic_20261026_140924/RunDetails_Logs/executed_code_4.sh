cd /tmp/deliverables && python3 - <<'EOF'
import re
s=open('make_infographic.py').read()
s=s.replace('"USGS EarthExplorer / NASA Earthdata (Landsat, MODIS, HLS, SMAP, ECOSTRESS)"',
            '"USGS EarthExplorer / NASA Earthdata (Landsat, MODIS, HLS, SMAP)"')
s=s.replace('"Satellite SOC/pH/CEC models: typically R2 ~0.4-0.7; validation RPD >1.4 = fair"',
            '"Satellite SOC/pH/CEC models: typically R2 ~0.4-0.7; RPD >1.4 = fair"')
s=s.replace('"Microbial biomass / F:B ratio is NOT directly observed - inferred via covariates"',
            '"Microbial biomass / F:B ratio is NOT directly observed - only inferred"')
s=s.replace('"SoilGrids (ISRIC); LUCAS topsoil (ESDAC); SSURGO / POLARIS (USA)"',
            '"SoilGrids (ISRIC); LUCAS topsoil (ESDAC); SSURGO (USA)"')
s=s.replace('''         "Sources: Weiss, Jacob & Duveiller (2020) Remote Sens. Environ. 236:111402; "
         "Angelopoulou et al. (2019) Remote Sens. 11:676; Lima et al. (2025) Remote Sens. 17:882; "
         "Poggio et al. (2021) SOIL 7:217; Gorelick et al. (2017) Remote Sens. Environ. 202:18; "
         "Cardille et al. (eds., 2024) Cloud-Based Remote Sensing with Google Earth Engine (open access).",
         size=7.5, color=C_MUTED, va="bottom")''',
'''         "Sources: Weiss, Jacob & Duveiller (2020) Remote Sens. Environ. 236:111402; "
         "Angelopoulou et al. (2019) Remote Sens. 11:676; Lima et al. (2025) Remote Sens. 17:882; "
         "Poggio et al. (2021) SOIL 7:217;\\n"
         "Gorelick et al. (2017) Remote Sens. Environ. 202:18; "
         "Cardille et al. (eds., 2024) Cloud-Based Remote Sensing with Google Earth Engine (open access, Springer).",
         size=7.5, color=C_MUTED, va="bottom", linespacing=1.4)''')
open('make_infographic.py','w').write(s)
EOF
python3 - <<'EOF'
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, sys
sys.path.insert(0,'/tmp/deliverables')
import make_infographic as mi
captured={}
plt.Figure.savefig=lambda self,*a,**k: captured.setdefault('fig',self)
plt.close=lambda *a,**k: None
mi.build("/dev/null",dpi=110)
fig=captured['fig']; fig.canvas.draw(); r=fig.canvas.get_renderer()
ax=fig.axes[0]; W,H=fig.get_size_inches()*fig.dpi
# panel bounds
x_left,w=0.06,0.88; panel_w=(w-0.03)/3
bounds=[(x_left+j*(panel_w+0.015), x_left+j*(panel_w+0.015)+panel_w) for j in range(3)]
bad=[]
for t in ax.texts:
    bb=t.get_window_extent(r); x0,x1,y0=bb.x0/W,bb.x1/W,bb.y0/H
    if y0<0.14 and y0>0.02:
        for lo,hi in bounds:
            if lo-0.001<=x0<=hi and x1>hi: bad.append((t.get_text()[:40],round(x1-hi,3)))
    if x1>0.945: bad.append(('GLOBAL',t.get_text()[:40],round(x1,3)))
print(bad)
EOF