# like s2 but 2 mm window and aggressor pads (bbox) included
from common import *
from collections import defaultdict
b=load(); pats,_=netclass_map(); segs,vias=tracks(b)
def agg(n):
    c=cls_of(n,pats)
    if c in('DO','CAN','RS232L','CPump','HV50','DI'): return c
    if re.match(r'MCU_(DO|CAN|RS232|DI)',n) or n.startswith('I2C') or n.startswith('Net-(U4-') or n.startswith('Net-(U6-'): return 'DIG'
VIC=('AnalogHZ','ADC','AnalogIn','VREF')
def d_pt_seg(p,a,c):
    ax,ay=a;cx,cy=c;px,py=p;dx,dy=cx-ax,cy-ay;L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.hypot(px-ax-t*dx,py-ay-t*dy)
A=[];V=[];R=[]
for t in segs:
    n=t.GetNetname();s=(P(t.GetStart()),P(t.GetEnd()),mm(t.GetWidth())/2,t.GetLayerName(),n)
    if agg(n): A.append(s)
    if cls_of(n,pats) in VIC: V.append(s)
for fp in b.GetFootprints():
    for p in fp.Pads():
        n=p.GetNetname()
        if agg(n):
            bb=p.GetBoundingBox();x0,y0=P(pcbnew.VECTOR2I(bb.GetLeft(),bb.GetTop()));x1,y1=P(pcbnew.VECTOR2I(bb.GetRight(),bb.GetBottom()))
            for L in('F.Cu','B.Cu'):
                if p.IsOnLayer(b.GetLayerID(L)): R.append((x0,y0,x1,y1,L,n,fp.GetReference()+'.'+p.GetNumber()))
res=defaultdict(lambda:[0,9,None]); pres=defaultdict(lambda:[0,9,None])
for a,c,hw,L,n in V:
    ln=math.hypot(c[0]-a[0],c[1]-a[1]);k=max(1,int(ln/0.1))
    for i in range(k):
        f=(i+.5)/k;p=(a[0]+f*(c[0]-a[0]),a[1]+f*(c[1]-a[1]))
        best={}
        for a2,c2,hw2,L2,n2 in A:
            if L2!=L: continue
            g=d_pt_seg(p,a2,c2)-hw-hw2
            if g<2.0 and g<best.get(n2,9): best[n2]=g
        for n2,g in best.items():
            r=res[(n,n2,L)];r[0]+=ln/k
            if g<r[1]: r[1]=g;r[2]=p
        for x0,y0,x1,y1,L2,n2,ref in R:
            if L2!=L: continue
            g=math.hypot(max(x0-p[0],0,p[0]-x1),max(y0-p[1],0,p[1]-y1))-hw
            if g<0.6:
                r=pres[(n,ref,n2,L)];r[0]+=ln/k
                if g<r[1]: r[1]=g;r[2]=p
print('TRACK-TRACK within 2mm: victim|aggr|layer|len|min gap|at')
for (n,n2,L),r in sorted(res.items(),key=lambda x:-x[1][0]):
    if r[0]>=1.5: print(f'{n} [{cls_of(n,pats)}] | {n2} [{agg(n2)}] | {L} | {r[0]:.1f} | {r[1]:.2f} | ({r[2][0]:.1f},{r[2][1]:.1f})')
print('TRACK-PAD within 0.6mm: victim|pad|padnet|layer|len|min gap|at')
for (n,ref,n2,L),r in sorted(pres.items(),key=lambda x:x[1][1]):
    print(f'{n} [{cls_of(n,pats)}] | {ref} | {n2} | {L} | {r[0]:.1f} | {r[1]:.2f} | ({r[2][0]:.1f},{r[2][1]:.1f})')
