# schematic netlist vs board pad nets: mismatches only
from common import *
net=os.path.join(W,'net.net')
subprocess.run([KICAD_CLI,'sch','export','netlist','-o',net,SCH],check=True,capture_output=True)
txt=open(net).read()
sch={}  # (ref,pin)->net
for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "((?:[^"\\]|\\.)*)"\)(.*?)(?=\n    \(net |\n  \)\n)',txt,re.S):
    name=m.group(1).replace('\\"','"')
    for r,p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)',m.group(2)): sch[(r,p)]=name
comps=dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)',txt))
b=load(); brd={}; bval={}
for fp in b.GetFootprints():
    bval[fp.GetReference()]=fp.GetValue()
    for p in fp.Pads():
        if p.GetNumber(): brd.setdefault((fp.GetReference(),p.GetNumber()),set()).add(p.GetNetname())
print('sch comps',len(comps),'board fps',len(bval),'sch pins',len(sch),'board pads',len(brd))
print('only in sch:',sorted(set(comps)-set(bval)))
print('only on board:',sorted(set(bval)-set(comps)), {r:bval[r] for r in set(bval)-set(comps)})
print('value diffs:',[(r,comps[r],bval[r]) for r in comps if r in bval and comps[r]!=bval[r]])
norm=lambda n:n.lstrip('/')
mm_=[]
for k,nets in brd.items():
    s=sch.get(k)
    if k[0] not in comps: continue
    if s is None:
        if any(n and not n.startswith('unconnected') for n in nets): mm_.append((k,None,nets))
    elif len(nets)>1 or norm(s) not in {norm(n) for n in nets}:
        if not(s.startswith('unconnected') and all(n=='' or n.startswith('unconnected') for n in nets)): mm_.append((k,s,nets))
print('pad net mismatches',len(mm_)); 
for x in mm_[:40]: print(' ',x)
print('sch pins missing on board:',[k for k in sch if k not in brd and k[0] in bval][:20])
for r in ('R109','D1'):
    print(r,'board nets',{k[1]:v for k,v in brd.items() if k[0]==r},'sch',{k[1]:v for k,v in sch.items() if k[0]==r})
