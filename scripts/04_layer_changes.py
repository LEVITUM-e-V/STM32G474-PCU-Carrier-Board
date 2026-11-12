# layer changes: nearest GND via per signal via; B.Cu length per net; island-edge crossings; power vias vs island
from common import *
from collections import defaultdict
b=filled(); pats,_=netclass_map(); segs,vias=tracks(b)
IX0,IX1,IY0,IY1=44.3,70.4,3.0,57.0
ins=lambda p:IX0<p[0]<IX1 and IY0<p[1]<IY1
PL=('GND','+5V','+3V3_MCU')
gv=[P(v.GetPosition()) for v in vias if v.GetNetname()=='GND']
gp=[P(p.GetPosition()) for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname()=='GND' and p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH]
G=gv+gp
print('+5V vias inside island:',[P(v.GetPosition()) for v in vias if v.GetNetname()=='+5V' and ins(P(v.GetPosition()))])
print('+3V3_MCU vias outside island:',[P(v.GetPosition()) for v in vias if v.GetNetname()=='+3V3_MCU' and not ins(P(v.GetPosition()))])
print('+3.3V vias inside island:',[P(v.GetPosition()) for v in vias if v.GetNetname()=='+3.3V' and ins(P(v.GetPosition()))])
bl=defaultdict(float); cross=defaultdict(list); fl=defaultdict(float)
for t in segs:
    n=t.GetNetname(); a,c=P(t.GetStart()),P(t.GetEnd()); L=math.hypot(a[0]-c[0],a[1]-c[1])
    if t.GetLayerName()=='B.Cu':
        bl[n]+=L
        if ins(a)!=ins(c): cross[n].append(((a[0]+c[0])/2,(a[1]+c[1])/2))
    else: fl[n]+=L
print('B.Cu segs crossing island edge (net,class,where):')
for n,v in cross.items(): print('  ',n,cls_of(n,pats),[(round(x,1),round(y,1)) for x,y in v])
print('signal vias: net|class|pos|inIsland|nearest GND via/THT mm   (only >2.0 mm listed; count all)')
sv=[v for v in vias if v.GetNetname() not in PL]
print('n signal vias',len(sv))
far=[]
for v in sv:
    p=P(v.GetPosition()); d=min(math.hypot(p[0]-g[0],p[1]-g[1]) for g in G); far.append((d,v.GetNetname(),p))
import statistics
print('median',round(statistics.median([f[0] for f in far]),2),'>3mm:',sum(1 for f in far if f[0]>3),'>2mm:',sum(1 for f in far if f[0]>2))
for d,n,p in sorted(far,reverse=True):
    if d>2.0: print(f'  {n} [{cls_of(n,pats)}] {p} isl={ins(p)} d={d:.1f} Bcu={bl[n]:.1f}')
print('analog-class nets with B.Cu: net|class|B.Cu len|F.Cu len|vias')
vc=defaultdict(int)
for v in sv: vc[v.GetNetname()]+=1
for n in sorted(bl):
    c=cls_of(n,pats)
    if c in('ADC','AnalogHZ','AnalogIn','HV50','OpOut','RS232L','CAN','VREF','CPump'): print(f'  {n} [{c}] B={bl[n]:.1f} F={fl[n]:.1f} vias={vc[n]}')
