"""Specctra transport from the generated placement; KiCad DRC remains authoritative."""
from pathlib import Path
import json,sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
def q(s):return json.dumps(str(s))
def ch(a,k):return [i for i in a if isinstance(i,list) and i and str(i[0])==k]
def one(a,k):return ch(a,k)[0]
a=sx.load(open(ROOT/'cad/interface-unrouted.kicad_pcb'));images=[];placement=[];pads={};nets={}
for fp in ch(a,'footprint'):
 ref=next(str(i[2]) for i in ch(fp,'fp_text') if str(i[1])=='reference');at=one(fp,'at');x,y=at[1:3];angle=at[3] if len(at)>3 else 0
 if ref.startswith('H'):continue
 pins=[]
 for pad in ch(fp,'pad'):
  pin=str(pad[1]);p=one(pad,'at');size=one(pad,'size');net=str(one(pad,'net')[2]);n=str(pad[2]);
  ps=f'{n}_{size[1]}_{size[2]}';netpin=f'{ref}-{pin}';nets.setdefault(net,[]).append(netpin)
  if ps not in pads:
   if n=='thru_hole':shape=' '.join(f'(shape (circle {layer} {size[1]*1000}))' for layer in ['F.Cu','B.Cu'])
   else:shape=f'(shape (rect F.Cu {-size[1]*500} {-size[2]*500} {size[1]*500} {size[2]*500}))'
   pads[ps]=f'(padstack {q(ps)} {shape} (attach off))'
  pins.append(f'(pin {q(ps)} {q(pin)} {p[1]*1000} {-p[2]*1000})')
 images.append(f'(image {q(ref)} {" ".join(pins)})')
 placement.append(f'(component {q(ref)} (place {q(ref)} {x*1000} {-y*1000} front {angle}))')
keep=[]
for x,y in [(102,102),(113,102),(113,118),(102,118)]:
 for layer in ['F.Cu','B.Cu']:keep.append(f'(keepout "" (circle {layer} 3560 {x*1000} {-y*1000}))')
netstr=' '.join(f'(net {q(n)} (pins {" ".join(pins)}))' for n,pins in nets.items())
text=f'''(pcb "interface"
(parser (string_quote ") (space_in_quoted_tokens on) (host_cad "KiCad") (host_version "9.0.0"))
(resolution um 10) (unit um)
(structure (layer F.Cu (type signal) (property (index 0))) (layer B.Cu (type signal) (property (index 1)))
(boundary (path pcb 0 100000 -100000 115000 -100000 115000 -120000 100000 -120000 100000 -100000))
(via "Via_600_300") (control (via_at_smd off))
(rule (width 200) (clearance 180) (clearance 180 (type default_smd)) (clearance 180 (type smd_smd))) {' '.join(keep)})
(placement {' '.join(placement)})
(library {' '.join(images)} {' '.join(pads.values())} (padstack "Via_600_300" (shape (circle F.Cu 600)) (shape (circle B.Cu 600)) (attach off)))
(network {netstr} (class "Default" {' '.join(q(n) for n in nets)} (circuit (use_via "Via_600_300")) (rule (width 200) (clearance 180))))
(wiring))'''
(ROOT/'cad/interface.dsn').write_text(text)
print('DSN generated:',len(nets),'nets')
