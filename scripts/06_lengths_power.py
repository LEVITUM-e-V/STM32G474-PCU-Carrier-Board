# AnalogHZ routed length vs pad-to-pad MST; power track widths; decoupling cap via distances
from common import *
from collections import defaultdict
b=filled(); pats,_=netclass_map(); segs,vias=tracks(b)
pads=defaultdict(list)
for fp in b.GetFootprints():
    for p in fp.Pads(): pads[p.GetNetname()].append((P(p.GetPosition()),fp.GetReference()+'.'+p.GetNumber(),p))
ln=defaultdict(float)
for t in segs: ln[t.GetNetname()]+=mm(t.GetLength())
def mst(pts,oct=False):
    if len(pts)<2: return 0
    d=lambda a,c:(max(abs(a[0]-c[0]),abs(a[1]-c[1]))+0.4142*min(abs(a[0]-c[0]),abs(a[1]-c[1]))) if oct else math.hypot(a[0]-c[0],a[1]-c[1])
    inn=[pts[0]];rest=pts[1:];tot=0
    while rest:
        best=min(((d(a,c),c) for a in inn for c in rest));tot+=best[0];inn.append(best[1]);rest.remove(best[1])
    return tot
print('AnalogHZ: net | routed | MST euclid | MST 45deg | pads   (routed>5)')
rows=[]
for n in pads:
    if cls_of(n,pats)!='AnalogHZ': continue
    pts=[p[0] for p in pads[n] if not p[1].startswith('TP')]
    rows.append((ln[n],mst(pts),mst(pts,True),n,[p[1] for p in pads[n]]))
print('n',len(rows),'routed>5:',sum(r[0]>5 for r in rows),'MST>5:',sum(r[1]>5 for r in rows),'routed>5 but MST(no TP)<=5:',sum(r[0]>5 and r[1]<=5 for r in rows))
for r in sorted(rows,reverse=True):
    if r[0]>5: print(f'  {r[3]} | {r[0]:.1f} | {r[1]:.1f} | {r[2]:.1f} | excess {r[0]-r[2]:.1f} | {" ".join(r[4])}')
print('POWER widths: net | layer | width | total len | longest single-width chain not computed')
pw=defaultdict(float)
for t in segs:
    n=t.GetNetname()
    if n in('+5V','+3.3V','+3V3_MCU','Net-(D17-K)'): pw[(n,t.GetLayerName(),mm(t.GetWidth()))]+=mm(t.GetLength())
for k in sorted(pw): print('  ',k,round(pw[k],1))
print('DECOUPLING: caps with GND pad: cap | other net | GND pad->nearest GND via | pwr pad->nearest same-net via/THT (if plane net)')
V=defaultdict(list)
for v in vias: V[v.GetNetname()].append(P(v.GetPosition()))
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: V[p.GetNetname()].append(P(p.GetPosition()))
out=[]
for fp in b.GetFootprints():
    r=fp.GetReference()
    if not r.startswith('C'): continue
    ps=list(fp.Pads()); nets=[p.GetNetname() for p in ps]
    if 'GND' not in nets: continue
    g=[p for p in ps if p.GetNetname()=='GND'][0]; o=[p for p in ps if p.GetNetname()!='GND']
    q=P(g.GetPosition()); dg=min(math.hypot(q[0]-x,q[1]-y) for x,y in V['GND'])
    on=o[0].GetNetname() if o else 'GND'; dp=None
    if on in('+5V','+3V3_MCU'):
        q2=P(o[0].GetPosition()); dp=min(math.hypot(q2[0]-x,q2[1]-y) for x,y in V[on])
    out.append((dg,r,on,dp))
print('  max GND via dist:',[(r,round(d,2),on) for d,r,on,dp in sorted(out,reverse=True)[:8]])
print('  plane-net caps pwr via dist max:',[(r,on,round(dp,2)) for d,r,on,dp in sorted([o for o in out if o[3] is not None],key=lambda x:-x[3])[:8]])
print('  n caps',len(out),'GND via >1.5mm:',sum(o[0]>1.5 for o in out))
