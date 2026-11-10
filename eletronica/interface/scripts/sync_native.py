from pathlib import Path
import json,pcbnew
ROOT=Path(__file__).resolve().parents[1]
b=pcbnew.LoadBoard(str(ROOT/'cad/interface.kicad_pcb'))
c=json.loads((ROOT/'circuito.json').read_text())
for n in list(b.GetNetsByNetcode().values()):
 if n.GetNetCode() and not n.GetNetname().startswith('/'):n.SetNetname('/'+n.GetNetname())
for f in b.GetFootprints():
 r=f.GetReference()
 if r.startswith('J'):f.SetValue(c[r]['value']);f.SetExcludedFromBOM(True)
pcbnew.ZONE_FILLER(b).Fill(b.Zones());pcbnew.SaveBoard(str(ROOT/'cad/interface.kicad_pcb'),b)
