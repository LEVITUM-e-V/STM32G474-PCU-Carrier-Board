# acute joints (<89 deg) between two segments of one net: is the vertex covered by a same-net pad or via?
from common import *
from collections import defaultdict
b=filled(); segs,vias=tracks(b)
ends=defaultdict(list)
for t in segs:
    for a,c in((t.GetStart(),t.GetEnd()),(t.GetEnd(),t.GetStart())): ends[(a.x,a.y,t.GetLayer(),t.GetNetname())].append((c.x-a.x,c.y-a.y))
for k,l in ends.items():
    for i in range(len(l)):
        for j in range(i+1,len(l)):
            u,v=l[i],l[j];nu=math.hypot(*u);nv=math.hypot(*v)
            if not nu or not nv: continue
            ang=math.degrees(math.acos(max(-1,min(1,(u[0]*v[0]+u[1]*v[1])/(nu*nv)))))
            if ang<89:
                q=pcbnew.VECTOR2I(k[0],k[1])
                pad=[fp.GetReference()+'.'+p.GetNumber() for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname()==k[3] and p.IsOnLayer(k[2]) and p.GetEffectivePolygon().Contains(q)]
                via=any(v_.GetNetname()==k[3] and math.hypot(v_.GetPosition().x-q.x,v_.GetPosition().y-q.y)<v_.GetWidth()/2 for v_ in vias)
                if not pad and not via: print('FREE',round(ang),k[3],b.GetLayerName(k[2]),P(q),round(mm(min(nu,nv)),2))
print('done')
