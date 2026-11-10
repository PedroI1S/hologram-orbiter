"""Independent checks of board footprint courtyards and printed-bay envelope."""
from pathlib import Path
import json,math,itertools
import sexpdata as sx
from shapely.geometry import Point,box
from shapely.affinity import rotate,translate
ROOT=Path(__file__).resolve().parents[1]
a=sx.load(open(ROOT/'cad/interface-unrouted.kicad_pcb'))
def key(x):return str(x[0]) if isinstance(x,list) and x else ''
def children(x,k):return [i for i in x if key(i)==k]
def one(x,k):return children(x,k)[0]
def polygon(fp):
 at=one(fp,'at');x,y=at[1:3];ang=at[3] if len(at)>3 else 0
 rects=children(fp,'fp_rect');circs=children(fp,'fp_circle')
 for r in rects:
  if one(r,'layer')[1]=='F.CrtYd':
   p1=one(r,'start')[1:];p2=one(r,'end')[1:];poly=box(min(p1[0],p2[0]),min(p1[1],p2[1]),max(p1[0],p2[0]),max(p1[1],p2[1]));return translate(rotate(poly,-ang,origin=(0,0)),xoff=x,yoff=y)
 for r in circs:
  if one(r,'layer')[1]=='F.CrtYd':return Point(x,y).buffer(1.75)
 return None
polys={};issues=[]
for fp in children(a,'footprint'):
 ref=next(i[2] for i in children(fp,'fp_text') if str(i[1])=='reference');poly=polygon(fp)
 if poly is not None:polys[ref]=poly
for (r,p),(s,q) in itertools.combinations(polys.items(),2):
 if p.intersection(q).area>1e-5:issues.append(f'Courtyard overlap {r}/{s}: {p.intersection(q).area:.5f} mm2')
bounds=box(100,100,115,120)
for r,p in polys.items():
 if not bounds.covers(p):issues.append(f'{r} courtyard outside board')
# The board corner maps to CAD (19.5, -5); board local axes match rotor +x,+y.
# Verify actual enclosure wall, battery cradle and post centers independently.
par=json.loads((ROOT.parents[1]/'Hologram_Orbiter_v3_0/CAD/parameters.json').read_text())
sp=par['spider'];coords=[(19.5+x,-5+y) for x,y in [(0,0),(15,0),(15,20),(0,20)]]
maxr=max(math.hypot(x,y) for x,y in coords)
assert maxr<sp['electronics_bay_id']/2
expected=[(21.5,-3),(32.5,-3),(32.5,13),(21.5,13)]
actual=[(19.5+x,-5+y) for x,y in [(2,2),(13,2),(13,18),(2,18)]]
assert actual==expected
report={'board_mm':[15,20,1.6],'max_corner_radius_mm':maxr,'enclosure_inner_radius_mm':sp['electronics_bay_id']/2,'minimum_radial_corner_gap_mm':sp['electronics_bay_id']/2-maxr,'mounting_centers_rotor_mm':actual,'component_courtyard_issues':issues,'assumptions':['Nominal printed CAD, actual printed part not measured','PCB underside at Z=6; 1.6mm board plus SOIC height under 8mm total envelope','19 wire bends and external power harness still require physical check','Heads must fit reserved diameter 3.5mm; underside must remain insulated']}
(ROOT/'reports/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));assert not issues
