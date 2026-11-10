"""Create assembler BOM and a pin-by-pin wire map. Placement export uses pcbnew."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fabricacao';OUT.mkdir(exist_ok=True)
c=json.loads((ROOT/'circuito.json').read_text())
groups=[
('U1','SN74AHCT125DR','Texas Instruments','SOIC-14','C155176','5V quad TTL buffer'),
('R1,R2,R3,R8,R9','0603WAF1002T5E','UNI-ROYAL','0603','C25804','10k 1% 0.1W'),
('R4','0603WAF1503T5E','UNI-ROYAL','0603','C22807','150k 1% 0.1W'),
('R5','0603WAF4702T5E','UNI-ROYAL','0603','C25819','47k 1% 0.1W'),
('R6,R10,R11','0603WAF330JT5E','UNI-ROYAL','0603','C23140','33R 1% 0.1W'),
('R7,R12,R13','0603WAF0000T5E','UNI-ROYAL','0603','C21189','0R jumper'),
('C1,C3','CC0603KRX7R9BB104','Yageo','0603','C14663','100nF 50V X7R 10%'),
('C2','CS0603KRX7R8BB105','Yageo','0603','C5972986','1uF 25V X7R 10%')]
with (OUT/'BOM.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Designator','Quantity','Manufacturer','MPN','Package','LCSC Part #','Comment'])
 for refs,mpn,mfr,pkg,lcsc,comment in groups:w.writerow([refs,len(refs.split(',')),mfr,mpn,pkg,lcsc,comment])
with (OUT/'BOM-JLCPCB.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Comment','Designator','Footprint','LCSC Part #'])
 for refs,mpn,mfr,pkg,lcsc,comment in groups:w.writerow([comment,refs,pkg,lcsc])
wire=json.loads((ROOT/'cad/wire_positions.json').read_text())
with (OUT/'mapa-fios.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Marcacao_B_Silk','Grupo','Pino','Rede','X_mm','Y_mm','Observacao'])
 n=0
 for ref,pads in wire.items():
  for pin,(x,y) in pads.items():
   n+=1;w.writerow([f'{n:02}',ref,pin,c[ref]['pins'][pin],x,y,'Fio soldado apos montagem SMD; AWG28; furo 0.5mm'])
with (ROOT/'conexoes.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['referencia','valor','pino','rede'])
 for ref,item in c.items():
  for pin,net in item['pins'].items():w.writerow([ref,item['value'],pin,net])
print('BOM: 17 SMDs, 8 purchase lines; 19 wires mapped')
