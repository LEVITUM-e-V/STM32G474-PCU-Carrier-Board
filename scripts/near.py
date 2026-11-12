# list pads/vias near given board-relative points: s5_near.py x y r [x y r ...]
from common import *
b=filled(); segs,vias=tracks(b)
a=list(map(float,sys.argv[1:]))
for i in range(0,len(a),3):
    x,y,r=a[i:i+3]; print('--',x,y,r)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            q=P(p.GetPosition())
            if math.hypot(q[0]-x,q[1]-y)<r: print(' pad',fp.GetReference(),p.GetNumber(),p.GetNetname(),q,'size',mm(p.GetSizeX()),mm(p.GetSizeY()),'drill',mm(p.GetDrillSizeX()),'zc',p.GetZoneConnection())
    for v in vias:
        q=P(v.GetPosition())
        if math.hypot(q[0]-x,q[1]-y)<r: print(' via',v.GetNetname(),q,mm(v.GetWidth()),'locked' if v.IsLocked() else '')
