# manufacturability: acute angles, tiny segments, via-in-pad, via-edge, via-hole, dangling ends, +5V chains
from common import *
from collections import defaultdict
b=filled(); pats,_=netclass_map(); segs,vias=tracks(b)
print('segments <0.05mm:',[(t.GetNetname(),P(t.GetStart()),round(mm(t.GetLength()),3)) for t in segs if mm(t.GetLength())<0.05])
print('segments <0.15mm:',sum(1 for t in segs if mm(t.GetLength())<0.15))
ends=defaultdict(list)
for t in segs:
    for a,c in((t.GetStart(),t.GetEnd()),(t.GetEnd(),t.GetStart())):
        ends[(a.x,a.y,t.GetLayer(),t.GetNetname())].append((c.x-a.x,c.y-a.y,t))
ac=[]
for k,l in ends.items():
    for i in range(len(l)):
        for j in range(i+1,len(l)):
            u,v=l[i],l[j];nu=math.hypot(u[0],u[1]);nv=math.hypot(v[0],v[1])
            if nu==0 or nv==0: continue
            ang=math.degrees(math.acos(max(-1,min(1,(u[0]*v[0]+u[1]*v[1])/(nu*nv)))))
            if ang<89: ac.append((round(ang),k[3],b.GetLayerName(k[2]),P(pcbnew.VECTOR2I(k[0],k[1])),round(mm(min(nu,nv)),2)))
print('acute joints (<89deg):',len(ac))
for a in sorted(ac)[:25]: print('  ',a)
# via in pad
vip=[]
for v in vias:
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: continue
            if p.HitTest(v.GetPosition()) or (math.hypot(*(mm(v.GetPosition().x-p.GetPosition().x),mm(v.GetPosition().y-p.GetPosition().y)))<mm(v.GetWidth())/2+min(mm(p.GetSizeX()),mm(p.GetSizeY()))/2-0.05 and p.GetNetname()==v.GetNetname()):
                bb=p.GetBoundingBox(); bb.Inflate(int(v.GetWidth()/2))
                if bb.Contains(v.GetPosition()):
                    # true overlap test: distance from via centre to pad bbox < via radius
                    q=v.GetPosition(); b0=p.GetBoundingBox()
                    dx=max(b0.GetLeft()-q.x,0,q.x-b0.GetRight());dy=max(b0.GetTop()-q.y,0,q.y-b0.GetBottom())
                    ov=mm(v.GetWidth())/2-mm(math.hypot(dx,dy))
                    hole=mm(v.GetDrill())/2-mm(math.hypot(dx,dy))
                    if ov>0.0 and not fp.GetReference().startswith('TP'): vip.append((fp.GetReference()+'.'+p.GetNumber(),v.GetNetname(),P(q),round(ov,2),'HOLE-IN-PAD' if hole>0 else 'annulus overlaps pad'))
print('vias overlapping non-TP SMD pads:',len(vip),' hole in pad:',sum(1 for x in vip if x[4].startswith('HOLE')))
for x in vip:
    if x[4].startswith('HOLE'): print('  ',x)
from collections import Counter
print('  annulus-overlap by net:',Counter(x[1] for x in vip if not x[4].startswith('HOLE')))
# edge + holes
bb=b.GetBoardEdgesBoundingBox(); x0,y0=P(pcbnew.VECTOR2I(bb.GetLeft(),bb.GetTop()));x1,y1=P(pcbnew.VECTOR2I(bb.GetRight(),bb.GetBottom()))
print('edge bbox',x0,y0,x1,y1)
e=[]
for v in vias:
    p=P(v.GetPosition()); d=min(p[0]-x0,x1-p[0],p[1]-y0,y1-p[1])-mm(v.GetWidth())/2
    if d<0.5: e.append((v.GetNetname(),p,round(d,2)))
print('via copper <0.5mm from edge:',e)
h=[]
holes=[(P(p.GetPosition()),mm(max(p.GetDrillSizeX(),p.GetDrillSizeY()))/2,fp.GetReference()+'.'+p.GetNumber()) for fp in b.GetFootprints() for p in fp.Pads() if p.GetDrillSizeX()>0]
for v in vias:
    p=P(v.GetPosition())
    for q,r,ref in holes:
        d=math.hypot(p[0]-q[0],p[1]-q[1])-r-mm(v.GetDrill())/2
        if d<0.5: h.append((v.GetNetname(),ref,p,round(d,2)))
print('via hole <0.5mm from THT/NPTH hole wall:',h)
vv=[]
for i in range(len(vias)):
    for j in range(i+1,len(vias)):
        a,c=P(vias[i].GetPosition()),P(vias[j].GetPosition());d=math.hypot(a[0]-c[0],a[1]-c[1])-(mm(vias[i].GetDrill())+mm(vias[j].GetDrill()))/2
        if d<0.3: vv.append((vias[i].GetNetname(),vias[j].GetNetname(),a,round(d,2)))
print('via-via hole wall <0.3mm:',vv)
# dangling
pts=defaultdict(int)
for t in segs:
    for a in(t.GetStart(),t.GetEnd()): pts[(a.x,a.y,t.GetNetname())]+=1
dang=[]
for (x,y,n),c in pts.items():
    if c>1: continue
    q=pcbnew.VECTOR2I(x,y)
    if any(v.GetNetname()==n and v.HitTest(q) for v in vias): continue
    if any(p.GetNetname()==n and p.HitTest(q) for fp in b.GetFootprints() for p in fp.Pads()): continue
    hit=[t for t in segs if t.GetNetname()==n and t.HitTest(q)]
    if len(hit)>1: continue
    dang.append((n,P(q)))
print('dangling track ends:',dang)
