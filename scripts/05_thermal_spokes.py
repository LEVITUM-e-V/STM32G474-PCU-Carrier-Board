# for every THT pad on a plane net: per zone layer, number of spokes and which fill piece they reach
from common import *
b=filled()
Z=[]
for z in b.Zones():
    for L in z.GetLayerSet().Seq():
        ps=z.GetFilledPolysList(L); areas=[abs(ps.Outline(i).Area()) for i in range(ps.OutlineCount())]
        Z.append((z.GetNetname(),L,ps,areas.index(max(areas))))
def ring(pad,L,off):
    poly=pad.GetEffectivePolygon(); o=poly.Outline(0); c0=pad.GetPosition(); pts=[]
    for i in range(o.PointCount()):
        q=o.CPoint(i); dx=q.x-c0.x; dy=q.y-c0.y; d=math.hypot(dx,dy) or 1; f=(d+pcbnew.FromMM(off))/d
        pts.append((c0.x+dx*f,c0.y+dy*f))
    out=[]
    for i in range(len(pts)):
        a=pts[i];c=pts[(i+1)%len(pts)];d=math.hypot(c[0]-a[0],c[1]-a[1]);k=max(1,int(d/pcbnew.FromMM(0.05)))
        for j in range(k): out.append(pcbnew.VECTOR2I(int(a[0]+(c[0]-a[0])*j/k),int(a[1]+(c[1]-a[1])*j/k)))
    return out
rows=[]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute()!=pcbnew.PAD_ATTRIB_PTH: continue
        n=p.GetNetname()
        for zn,L,ps,main in Z:
            if zn!=n: continue
            pts=ring(p,L,0.2)
            ins=[]
            for q in pts:
                idx=-1
                for i in range(ps.OutlineCount()):
                    if ps.Contains(q,i): idx=i;break
                ins.append(idx)
            frac=sum(1 for i in ins if i>=0)/len(ins)
            arcs=sum(1 for i in range(len(ins)) if ins[i]>=0 and ins[i-1]<0)
            pcs=set(i for i in ins if i>=0)
            st='SOLID' if frac>0.95 else f'{arcs} spokes'
            rows.append((fp.GetReference()+'.'+p.GetNumber(),n,b.GetLayerName(L),st,'main' if main in pcs else ('NONE' if not pcs else 'ISOLATED-PIECE')))
from collections import Counter
print(Counter((r[1],r[2],r[3],r[4]) for r in rows))
for r in rows:
    if r[4]!='main' or r[3] in('1 spokes','0 spokes'): print(r)
