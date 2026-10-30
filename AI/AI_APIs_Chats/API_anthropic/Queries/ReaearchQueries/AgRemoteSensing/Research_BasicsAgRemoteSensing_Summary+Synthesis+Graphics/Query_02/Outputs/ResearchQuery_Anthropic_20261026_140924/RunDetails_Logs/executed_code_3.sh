cd /tmp/deliverables && python3 - <<'EOF'
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import make_infographic as mi
# monkeypatch savefig to capture figure
captured={}
orig=plt.Figure.savefig
def fake(self,*a,**k): captured['fig']=self
plt.Figure.savefig=fake
orig_close=plt.close; plt.close=lambda *a,**k: None
mi.build("/dev/null",dpi=110)
fig=captured['fig']; fig.canvas.draw(); r=fig.canvas.get_renderer()
ax=fig.axes[0]; W,H=fig.get_size_inches()*fig.dpi
over=[]
for t in ax.texts:
    bb=t.get_window_extent(r)
    x1=bb.x1/W; y0=bb.y0/H
    if x1>0.945 or y0<0.0: over.append((t.get_text()[:50], round(x1,3), round(y0,3)))
print("overflow count:",len(over))
for o in over[:10]: print(o)
EOF