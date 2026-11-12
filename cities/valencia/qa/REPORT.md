# QA valencia

Generato da `python -m kit.qa` il 2026-11-12 06:50. Esito complessivo: **FAIL**

| Sezione | Esito |
|---|---|
| a) Story e fonti | WARN |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| d) Corridoi vuoti | FAIL |
| e) Costo e schedule | PASS |
| f) Fotogrammi locali | PASS |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 45 fonti
- **PASS** date con fonte
- **WARN** date fuori dall'intervallo del video
  - history.water[3] Jardi del Turia 1: 99999; history.water[5] Jardi del Turia 2: 99999; history.water[7] Jardi del Turia 3: 99999; history.water[9] Jardi del Turia 4: 99999; history.water[11] Jardi del Turia 5: 99999; history.water[13] Jardi del Turia 6: 99999; history.water[15] 1957 flood (low centre, slab back): 99999

## b) DATA

- **PASS** cartella DATA
  - data_valencia
- **PASS** buildings.json
  - 38241 voci
- **PASS** roads.json
  - 13838 voci
- **PASS** hist.json
  - 17247 voci
- **PASS** land.json
  - 4 voci
- **PASS** landmarks.json
  - 1664 voci
- **PASS** dem.npz
- **PASS** anni edifici (38241)
  - senza anno 0, dopo 2026: 0, prima di 1238 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (17247 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (13838 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 333, nel 1800 837

## c) Densita' storica

- **PASS** Muslim walled city nel 1238
  - 1788 edifici vivi (49/ha, copertura 61%) contro 1054 (29/ha, copertura 76%) nel 2026: rapporto 1.70
- **PASS** Muslim walled city nel 1500
  - 1861 edifici vivi (51/ha, copertura 71%) contro 1054 (29/ha, copertura 76%) nel 2026: rapporto 1.77
- **PASS** Muslim walled city nel 1800
  - 1714 edifici vivi (47/ha, copertura 75%) contro 1054 (29/ha, copertura 76%) nel 2026: rapporto 1.63
- **PASS** Boatella quarter (inside 1356 wall) nel 1500
  - 1868 edifici vivi (46/ha, copertura 58%) contro 668 (17/ha, copertura 62%) nel 2026: rapporto 2.80
- **PASS** Boatella quarter (inside 1356 wall) nel 1800
  - 1868 edifici vivi (46/ha, copertura 58%) contro 668 (17/ha, copertura 62%) nel 2026: rapporto 2.80
- **PASS** Christian expansion within the 1356 wall nel 1500
  - 6977 edifici vivi (43/ha, copertura 56%) contro 3281 (20/ha, copertura 60%) nel 2026: rapporto 2.13
- **PASS** Christian expansion within the 1356 wall nel 1800
  - 6670 edifici vivi (41/ha, copertura 64%) contro 3281 (20/ha, copertura 60%) nel 2026: rapporto 2.03
- **PASS** Quart suburb (arrabal de Quart) nel 1800
  - 367 edifici vivi (38/ha, copertura 55%) contro 242 (25/ha, copertura 56%) nel 2026: rapporto 1.52
- **PASS** Morvedre suburb (north of the Turia) nel 1800
  - 428 edifici vivi (28/ha, copertura 36%) contro 186 (12/ha, copertura 54%) nel 2026: rapporto 2.30
- **PASS** Russafa village nel 1800
  - 223 edifici vivi (26/ha, copertura 39%) contro 142 (17/ha, copertura 58%) nel 2026: rapporto 1.57
- **PASS** El Grau (Vilanova del Grau) nel 1800
  - 22 edifici vivi (2/ha, copertura 3%) contro 7 (1/ha, copertura 1%) nel 2026: rapporto 3.14

## d) Corridoi vuoti

- **FAIL** 1238: nastri stradali prima dell'apertura
  - Calle de la Paz: 64 m² di nastro visibile prima del 1872
- **WARN** 1338: 3 aree vuote allungate
  - #1 1212x126 m a (39.48675,-0.37460); #2 1632x331 m a (39.47047,-0.37378); #3 660x118 m a (39.47502,-0.38863) — corridoi_1338.png
- **WARN** 1338: 1 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #4 302x46 m a (39.47177,-0.37353)
- **FAIL** 1338: nastri stradali prima dell'apertura
  - Calle de la Paz: 64 m² di nastro visibile prima del 1872
- **FAIL** 1800: 6 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 674x71 m a (39.48935,-0.37460); #2 392x28 m a (39.48275,-0.37495); #3 265x51 m a (39.47537,-0.38738); #4 185x16 m a (39.47481,-0.39054); #5 1580x105 m a (39.46895,-0.32926); #6 162x29 m a (39.46265,-0.37143) — corridoi_1800.png
- **WARN** 1800: 4 aree vuote allungate
  - #7 216x47 m a (39.48078,-0.38205); #8 398x83 m a (39.47734,-0.37097); #9 354x79 m a (39.47461,-0.36783); #10 169x33 m a (39.46813,-0.37793) — corridoi_1800.png
- **WARN** 1800: 1 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #11 255x22 m a (39.47484,-0.36990)
- **FAIL** 1900: 2 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 669x70 m a (39.48937,-0.37460); #2 1638x81 m a (39.46895,-0.32926) — corridoi_1900.png
- **WARN** 1900: 6 aree vuote allungate
  - #3 402x80 m a (39.47745,-0.37097); #4 363x84 m a (39.47461,-0.36778); #5 173x28 m a (39.47562,-0.38691); #6 169x33 m a (39.46813,-0.37793); #7 127x32 m a (39.46672,-0.37437); #8 224x52 m a (39.46614,-0.37488) — corridoi_1900.png
- **WARN** 1900: 3 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #9 552x24 m a (39.47602,-0.37122); #10 519x36 m a (39.46904,-0.37832); #11 381x27 m a (39.46598,-0.37430)
- **WARN** 1950: 6 aree vuote allungate
  - #1 402x80 m a (39.47745,-0.37097); #2 404x86 m a (39.47450,-0.36766); #3 120x30 m a (39.47378,-0.32765); #4 225x53 m a (39.47048,-0.37648); #5 169x33 m a (39.46813,-0.37793); #6 122x21 m a (39.46672,-0.37432) — corridoi_1950.png

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 2182, cambi in tutto il video 82577, max in un fotogramma 601 (~7 s), costo dei soli cambi ~0.28 h (budget 1.0 h)
- **PASS** 26 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** evento forte entro 45 s
  - primo a 9.5 s
- **PASS** notte
  - night_t=460.5, schedule_valencia_night.json ok

## f) Fotogrammi locali

- **PASS** render locale: 8 fotogrammi in 218 s
  - cities/valencia/qa/render.log
- **PASS** foglio contatti
  - cities/valencia/qa/contact.jpg: guardalo prima del pod (strade come nastri chiari, centro pieno)

## Immagini

![corridoi_1238.png](corridoi_1238.png)
![corridoi_1338.png](corridoi_1338.png)
![corridoi_1800.png](corridoi_1800.png)
![corridoi_1900.png](corridoi_1900.png)
![corridoi_1950.png](corridoi_1950.png)
![contact.jpg](contact.jpg)
