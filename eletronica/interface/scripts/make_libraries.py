"""Provide project-local symbol/footprint libraries, with no global configuration."""
from pathlib import Path
import copy,json,subprocess,sys,sexpdata as sx
ROOT=Path(__file__).resolve().parents[1];CAD=ROOT/'cad'
def ch(a,k):return [i for i in a if isinstance(i,list) and i and str(i[0])==k]
def one(a,k):return ch(a,k)[0]
c=json.loads((ROOT/'circuito.json').read_text())
for ref,item in c.items():item['footprint']='Orbiter:'+ref
(ROOT/'circuito.json').write_text(json.dumps(c,indent=2)+'\n')
subprocess.run([sys.executable,str(ROOT/'scripts/generate_schematic.py')],check=True)
ids=json.loads((CAD/'symbol_ids.json').read_text())
lib=CAD/'Orbiter.pretty';lib.mkdir(exist_ok=True)
for filename in ['interface-unrouted.kicad_pcb','interface.kicad_pcb']:
 b=sx.load(open(CAD/filename))
 for fp in ch(b,'footprint'):
  ref=next(str(t[2]) for t in ch(fp,'fp_text') if str(t[1])=='reference');fp[1]='Orbiter:'+ref
  paths=ch(fp,'path')
  if ref in ids:
   if paths:paths[0][1]='/'+ids[ref]
   else:fp.append([sx.Symbol('path'),'/'+ids[ref]])
  f=copy.deepcopy(fp);f[1]=ref
  # Local pin coordinates stay unchanged; orientation is normalized with the placement removed.
  f[:]=[e for e in f if not (isinstance(e,list) and e and str(e[0]) in ['at','uuid','path','sheetname','sheetfile'])]
  for pad in ch(f,'pad'):
   pad[:]=[e for e in pad if not (isinstance(e,list) and e and str(e[0]) in ['net','uuid'])]
   ats=ch(pad,'at')
   if ats and len(ats[0])>3:ats[0][3]=0
  for t in ch(f,'fp_text'):
   if str(t[1])=='reference':t[2]='REF**'
   ats=ch(t,'at')
   if ats and len(ats[0])>3:ats[0][3]=0
  f.insert(2,[sx.Symbol('version'),20240108]);f.insert(3,[sx.Symbol('generator'),sx.Symbol('pcbnew')])
  (lib/(ref+'.kicad_mod')).write_text(sx.dumps(f)+'\n')
 (CAD/filename).write_text(sx.dumps(b)+'\n')
s=sx.load(open(CAD/'interface.kicad_sch'));symbols=one(s,'lib_symbols')[1:]
for sym in symbols:sym[1]=sym[1].removeprefix('Orbiter:')
sl=[sx.Symbol('kicad_symbol_lib'),[sx.Symbol('version'),20241209],[sx.Symbol('generator'),sx.Symbol('kicad_symbol_editor')]]+symbols
(CAD/'Orbiter.kicad_sym').write_text(sx.dumps(sl)+'\n')
(CAD/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Orbiter") (type "KiCad") (uri "${KIPRJMOD}/Orbiter.pretty") (options "") (descr "Project-local Orbiter footprints")))\n')
(CAD/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Orbiter") (type "KiCad") (uri "${KIPRJMOD}/Orbiter.kicad_sym") (options "") (descr "Project-local Orbiter symbols")))\n')
print('Self-contained local libraries and schematic links written')
