# precise via-in-pad: via centre inside SMD pad polygon (F.Cu pads; TP footprints excluded), and is there a TP under it
from common import *
from collections import Counter
b=filled(); pats,_=netclass_map(); segs,vias=tracks(b)
tp={}
for fp in b.GetFootprints():
    if fp.GetReference().startswith('TP'):
        for p in fp.Pads(): tp[fp.GetReference()]=(P(p.GetPosition()),p.GetNetname(),mm(p.GetSizeX()),fp.IsFlipped())
print('TPs',len(tp),'flipped',sum(1 for t in tp.values() if t[3]),'sizes',Counter(t[2] for t in tp.values()))
rows=[]
for v in vias:
    q=v.GetPosition()
    for fp in b.GetFootprints():
        if fp.GetReference().startswith('TP'): continue
        for p in fp.Pads():
            if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: continue
            if p.GetEffectivePolygon().Contains(q):
                t=[k for k,x in tp.items() if math.hypot(x[0][0]-P(q)[0],x[0][1]-P(q)[1])<0.05]
                rows.append((fp.GetReference()+'.'+p.GetNumber(),fp.GetFPID().GetLibItemName().wxString() if hasattr(fp.GetFPID().GetLibItemName(),'wxString') else str(fp.GetFPID().GetLibItemName()),v.GetNetname(),t[0] if t else '-',v.IsLocked(),(mm(p.GetSizeX()),mm(p.GetSizeY()))))
print('via centre inside SMD pad:',len(rows),'of which TP via:',sum(1 for r in rows if r[3]!='-'))
print(Counter((r[1][:28],r[5]) for r in rows))
print('non-TP vias in pad:',[(r[0],r[2]) for r in rows if r[3]=='-'])
tpv=set(r[3] for r in rows)
print('TPs whose via is NOT in an SMD pad:',len([k for k in tp if k not in tpv]))
# tenting: via mask
print('via tented front/back sample:', Counter((v.IsTented() if hasattr(v,'IsTented') else None) for v in vias))
print('solder mask min width / tent settings:', b.GetDesignSettings().m_SolderMaskExpansion, b.GetPlotOptions().GetPlotViaOnMaskLayer())
