# GND pour: pieces with <=1 anchor to L2 (GND via or THT GND pad); lobes hanging on necks <0.6 mm (erode 0.3) without own anchor
from common import *
b=filled(); segs,vias=tracks(b)
anc=[(v.GetPosition(),0.35) for v in vias if v.GetNetname()=='GND']+[(p.GetPosition(),mm(max(p.GetSizeX(),p.GetSizeY()))/2+0.65) for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname()=='GND' and p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH]
def bbx(o):
    bb=o.BBox(); a=P(pcbnew.VECTOR2I(bb.GetLeft(),bb.GetTop())); c=P(pcbnew.VECTOR2I(bb.GetRight(),bb.GetBottom())); return (round(a[0],1),round(a[1],1),round(c[0],1),round(c[1],1))
for z in b.Zones():
    if z.GetNetname()!='GND': continue
    for L in z.GetLayerSet().Seq():
        ln=b.GetLayerName(L)
        if ln not in('F.Cu','B.Cu'): continue
        ps=z.GetFilledPolysList(L); one=[]
        for i in range(ps.OutlineCount()):
            n=sum(1 for a,t in anc if ps.Contains(a,i,pcbnew.FromMM(t)))
            if n<=1: one.append((round(abs(ps.Outline(i).Area())/1e12,1),n,bbx(ps.Outline(i))))
        print(ln,'pieces',ps.OutlineCount(),'with <=1 anchor:',len(one)); 
        for o in sorted(one,reverse=True)[:8]: print('    ',o)
        e=pcbnew.SHAPE_POLY_SET(ps); e.Inflate(-pcbnew.FromMM(0.3),16); lob=[]
        for i in range(e.OutlineCount()):
            a=abs(e.Outline(i).Area())/1e12
            n=sum(1 for q,t in anc if e.Contains(q,i,pcbnew.FromMM(0.3+t)))
            if n==0 and a>5: lob.append((round(a,1),bbx(e.Outline(i))))
        print('  lobes >5mm2 behind necks <0.6mm, no own anchor:',len(lob))
        for o in sorted(lob,reverse=True)[:10]: print('    ',o)
