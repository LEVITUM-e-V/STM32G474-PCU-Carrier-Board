# refill, DRC, zone/fill-piece summary
from common import *
b=load()
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
out=os.path.join(W,'drc.txt')
pcbnew.WriteDRCReport(b,out,pcbnew.EDA_UNITS_MILLIMETRES,True)
from collections import Counter
txt=open(out).read()
print(Counter(re.findall(r'^\[(\w+)\]',txt,re.M)))
print(re.findall(r'\*\* Found .*',txt))
segs,vias=tracks(b)
for z in b.Zones():
    for L in z.GetLayerSet().Seq():
        ps=z.GetFilledPolysList(L)
        pcs=[]
        for i in range(ps.OutlineCount()):
            o=ps.Outline(i); a=abs(o.Area())/1e12
            bb=o.BBox()
            pcs.append((round(a,1),P(pcbnew.VECTOR2I(bb.GetLeft(),bb.GetTop())),P(pcbnew.VECTOR2I(bb.GetRight(),bb.GetBottom()))))
        pcs.sort(reverse=True)
        print(z.GetNetname(),b.GetLayerName(L),'prio',z.GetAssignedPriority(),'pieces',len(pcs),'minwidth',mm(z.GetMinThickness()),'clr',mm(z.GetLocalClearance()),'islandmode',z.GetIslandRemovalMode(),'thermal gap/spoke',mm(z.GetThermalReliefGap()),mm(z.GetThermalReliefSpokeWidth()),'conn',z.GetPadConnection())
        print('   ',pcs[:12])
