"""Import Specctra wires/vias without moving or replacing reviewed footprints."""
from pathlib import Path
import json,uuid,sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
def ch(a,k):return [i for i in a if isinstance(i,list) and i and str(i[0])==k]
def one(a,k):return ch(a,k)[0]
def uid():return str(uuid.uuid4())
file=ROOT/'cad/interface-unrouted.kicad_pcb';text=file.read_text();board=sx.loads(text)
nets={str(n[2]):int(n[1]) for n in ch(board,'net')}
s=sx.load(open(ROOT/'cad/interface-quad.ses'));routes=one(s,'routes');res=one(routes,'resolution');assert str(res[1])=='um';scale=1000*res[2]
# Confirm router retained each component's position/orientation.
for group in ch(one(s,'placement'),'component'):
 p=one(group,'place');ref=str(p[1]);f=next(f for f in ch(board,'footprint') if any(str(t[1])=='reference' and str(t[2])==ref for t in ch(f,'fp_text')));a=one(f,'at')
 assert abs(p[2]/scale-a[1])<1e-5 and abs(-p[3]/scale-a[2])<1e-5
 assert abs(p[5]-(a[3] if len(a)>3 else 0))<1e-5
parts=[];nseg=nv=0
for net in ch(one(routes,'network_out'),'net'):
 netid=nets[str(net[1])]
 for wire in ch(net,'wire'):
  path=one(wire,'path');layer=str(path[1]);width=path[2]/scale;pts=list(zip(path[3::2],path[4::2]))
  for (x,y),(u,v) in zip(pts,pts[1:]):
   if x==u and y==v:continue
   parts.append(f'(segment (start {x/scale:.6f} {-y/scale:.6f}) (end {u/scale:.6f} {-v/scale:.6f}) (width {width}) (layer "{layer}") (net {netid}) (uuid {uid()}))');nseg+=1
 for via in ch(net,'via'):
  assert str(via[1])=='Via_600_300'
  parts.append(f'(via (at {via[2]/scale:.6f} {-via[3]/scale:.6f}) (size .6) (drill .3) (layers "F.Cu" "B.Cu") (net {netid}) (uuid {uid()}))');nv+=1
parts.append(f'''(zone (net {nets['GND']}) (net_name "GND") (layer "B.Cu") (uuid {uid()}) (hatch edge .5)
(connect_pads yes (clearance .18)) (min_thickness .153) (fill yes (thermal_gap .25) (thermal_bridge_width .25))
(polygon (pts (xy 100.3 100.3) (xy 114.7 100.3) (xy 114.7 119.7) (xy 100.3 119.7))))''')
(ROOT/'cad/interface.kicad_pcb').write_text(text.rstrip()[:-1]+'\n'+'\n'.join(parts)+'\n)\n')
(ROOT/'reports/router-summary.json').write_text(json.dumps({'segments':nseg,'vias':nv,'all_placements_preserved':True,'router':'Freerouting 2.1.0','validation':'KiCad DRC must follow'},indent=2)+'\n')
print(nseg,'segments;',nv,'vias')
