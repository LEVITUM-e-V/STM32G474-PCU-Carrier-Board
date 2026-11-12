# +5V / +3V3_MCU track chains (connected groups of segments): length, pads on the chain
from common import *
from collections import defaultdict
b=filled(); segs,vias=tracks(b)
for net in('+5V','+3V3_MCU'):
    S_=[t for t in segs if t.GetNetname()==net]; par=list(range(len(S_)))
    def f(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    for i in range(len(S_)):
        for j in range(i+1,len(S_)):
            if any(S_[j].HitTest(q) for q in(S_[i].GetStart(),S_[i].GetEnd())) or any(S_[i].HitTest(q) for q in(S_[j].GetStart(),S_[j].GetEnd())):
                if S_[i].GetLayer()==S_[j].GetLayer() or any(v.HitTest(S_[i].GetStart()) or v.HitTest(S_[i].GetEnd()) for v in vias if v.GetNetname()==net): par[f(i)]=f(j)
    g=defaultdict(list)
    for i in range(len(S_)): g[f(i)].append(S_[i])
    res=[]
    for k,l in g.items():
        pads=[fp.GetReference()+'.'+p.GetNumber() for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname()==net and any(p.HitTest(q) for t in l for q in(t.GetStart(),t.GetEnd()))]
        nv=sum(1 for v in vias if v.GetNetname()==net and any(v.HitTest(q) for t in l for q in(t.GetStart(),t.GetEnd())))
        res.append((round(sum(mm(t.GetLength()) for t in l),1),pads,nv))
    print(net,'chains',len(res)); [print('  ',r) for r in sorted(res,reverse=True)[:6]]
