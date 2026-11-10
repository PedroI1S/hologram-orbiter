"""Independent preflight of routed copper (KiCad DRC is also required)."""
from pathlib import Path
import json,math,itertools,sexpdata as sx
from shapely.geometry import Point,LineString,box
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
def ch(a,k):return [i for i in a if isinstance(i,list) and i and str(i[0])==k]
def one(a,k):return ch(a,k)[0]
a=sx.load(open(ROOT/'cad/interface.kicad_pcb'));copper={};items=[];pads={}
def add(layer,net,geom,desc):
 copper.setdefault((layer,net),[]).append(geom);items.append((layer,net,geom,desc))
for f in ch(a,'footprint'):
 ref=next((str(i[2]) for i in ch(f,'property') if str(i[1])=='Reference'),None) or next(str(i[2]) for i in ch(f,'fp_text') if str(i[1])=='reference');at=one(f,'at');x,y=at[1:3];ang=at[3] if len(at)>3 else 0
 for pad in ch(f,'pad'):
  ns=ch(pad,'net')
  if not ns:continue
  net=str(ns[0][-1]);p=one(pad,'at');s=one(pad,'size');px,py=p[1:3]
  if str(pad[3])=='circle':poly=Point(0,0).buffer(s[1]/2)
  else:
   rr=ch(pad,'roundrect_rratio');r=min(s[1],s[2])*(rr[0][1] if rr else 0)
   poly=box(-s[1]/2+r,-s[2]/2+r,s[1]/2-r,s[2]/2-r).buffer(r) if r else box(-s[1]/2,-s[2]/2,s[1]/2,s[2]/2)
  poly=translate(poly,px,py);poly=translate(rotate(poly,-ang,origin=(0,0)),x,y)
  layers=[str(i) for i in one(pad,'layers')[1:]];layers=['F.Cu','B.Cu'] if '*.Cu' in layers else [l for l in layers if l.endswith('.Cu')]
  for layer in layers:add(layer,net,poly,f'{ref}.{pad[1]}')
  pads[(ref,str(pad[1]))]=(net,poly)
for i,s in enumerate(ch(a,'segment')):
 start=one(s,'start')[1:];end=one(s,'end')[1:];net=str(one(s,'net')[-1]);layer=str(one(s,'layer')[1]);width=one(s,'width')[1]
 add(layer,net,LineString([start,end]).buffer(width/2),f'track{i}')
for i,v in enumerate(ch(a,'via')):
 p=one(v,'at')[1:];size=one(v,'size')[1];net=str(one(v,'net')[-1]);poly=Point(*p).buffer(size/2)
 for layer in ['F.Cu','B.Cu']:add(layer,net,poly,f'via{i}')
issues=[];minclear=99
unions={k:unary_union(v) for k,v in copper.items()}
for (layer,n),p in unions.items():
 for (l,m),q in unions.items():
  if layer!=l or n>=m:continue
  d=p.distance(q);minclear=min(minclear,d)
  if d<.153-1e-4:issues.append({'layer':layer,'net1':n,'net2':m,'gap_mm':d})
bounds=box(100,100,115,120);edges=[]
for layer,n,p,desc in items:
 d=bounds.boundary.distance(p)
 if d<.25-1e-4:edges.append((desc,layer,d))
# Connectivity across layers: each segment/through pad/via must join a net component.
# DRC performs the final topology check; here ensure each pad touches routed copper.
untouched=[]
for (ref,pin),(net,p) in pads.items():
 touching=[desc for l,n,g,desc in items if n==net and desc!=f'{ref}.{pin}' and desc.startswith(('track','via')) and p.distance(g)<1e-4]
 if not touching:untouched.append(f'{ref}.{pin}')
# Independently prove connectivity, including layer bridges at vias and through pads.
parents=list(range(len(items)))
def find(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
def join(i,j):parents[find(i)]=find(j)
for i,(l,n,p,d) in enumerate(items):
 for j in range(i):
  ll,nn,pp,dd=items[j]
  if nn!=n:continue
  if (l==ll and p.distance(pp)<1e-4) or (d==dd and (d.startswith('via') or d.startswith('J'))):join(i,j)
open_nets=[]
for net in {n for _,n,_,_ in items}:
 roots={find(i) for i,(_,n,_,d) in enumerate(items) if n==net}
 if len(roots)>1:open_nets.append({'net_id':net,'islands':len(roots)})
r={'open_nets':open_nets,'minimum_inter_net_clearance_mm':minclear,'clearance_issues':issues,'edge_clearance_issues':edges,'pads_without_track_contact':untouched,'filled_zones_included':False}
(ROOT/'reports/copper-preflight.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not issues and not edges and not untouched and not open_nets
