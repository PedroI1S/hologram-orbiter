"""Compare independently exported KiCad schematic and PCB nets to pin table."""
from pathlib import Path
import json,xml.etree.ElementTree as ET,sexpdata as sx
ROOT=Path(__file__).resolve().parents[1]
def ch(a,k):return [i for i in a if isinstance(i,list) and i and str(i[0])==k]
def one(a,k):return ch(a,k)[0]
c=json.loads((ROOT/'circuito.json').read_text());expected={(r,p):n for r,item in c.items() for p,n in item['pins'].items()}
board=sx.load(open(ROOT/'cad/interface.kicad_pcb'));actual={}
for f in ch(board,'footprint'):
 refs=ch(f,'property');refs=[r[2] for r in refs if r[1]=='Reference']
 if not refs:refs=[r[2] for r in ch(f,'fp_text') if str(r[1])=='reference']
 if not refs:continue
 ref=str(refs[0])
 if ref not in c:continue
 for p in ch(f,'pad'):
  if not str(p[1]):continue
  actual[(ref,str(p[1]))]=str(one(p,'net')[-1]).removeprefix('/')
assert actual==expected,{'pcb_missing':list(expected.keys()-actual.keys()),'pcb_different':[(k,n,actual.get(k)) for k,n in expected.items() if actual.get(k)!=n]}
sch=ET.parse(ROOT/'reports/schematic.net');schmap={}
for net in sch.findall('./nets/net'):
 for node in net.findall('node'):schmap[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name'].removeprefix('/')
assert schmap==expected,{'schematic_missing':list(expected.keys()-schmap.keys()),'schematic_different':[(k,n,schmap.get(k)) for k,n in expected.items() if schmap.get(k)!=n]}
r={'pin_net_pairs_checked':len(expected),'pcb_matches':True,'schematic_matches':True}
(ROOT/'reports/pinmap.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
