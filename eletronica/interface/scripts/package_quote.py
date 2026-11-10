from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'fabricacao'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted(p for p in (out/'gerbers').iterdir() if p.is_file())
assert len(files)==11
with zipfile.ZipFile(out/'Gerbers_Orbiter_r02.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.name)
# Full quote package includes editable CAD plus review artifacts, without intermediates/logs.
allfiles=[ROOT/'README.md']
allfiles+=sorted(p for p in out.rglob('*') if p.is_file() and p.suffix not in ['.zip'])
allfiles+=sorted(p for p in (ROOT/'cad').rglob('*') if p.is_file() and (p.name in ['interface.kicad_pro','interface.kicad_sch','interface.kicad_pcb','Orbiter.kicad_sym','fp-lib-table','sym-lib-table','wire_positions.json'] or p.suffix=='.kicad_mod'))
allfiles+=sorted(p for p in (ROOT/'reports').rglob('*') if p.is_file() and p.suffix in ['.md','.json','.svg','.png','.net','.txt'])
allfiles=list(dict.fromkeys(allfiles))
manifest=''.join(f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in allfiles)
with zipfile.ZipFile(out/'Pacote_Orbiter_r02.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in allfiles:z.write(p,str(p.relative_to(ROOT)))
 z.writestr('SHA256SUMS.txt',manifest)
for name in ['Gerbers_Orbiter_r02.zip','Pacote_Orbiter_r02.zip']:
 p=out/name
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 print(name, p.stat().st_size,'bytes',digest(p))
(out/'SHA256SUMS-ZIP.txt').write_text(''.join(f'{digest(out/name)}  {name}\n' for name in ['Gerbers_Orbiter_r02.zip','Pacote_Orbiter_r02.zip']))
