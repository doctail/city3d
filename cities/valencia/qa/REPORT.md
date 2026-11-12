# QA valencia

Generato da `python -m kit.qa` il 2026-11-12 11:59. Esito complessivo: **FAIL**

| Sezione | Esito |
|---|---|
| a) Story e fonti | WARN |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| d) Corridoi vuoti | FAIL |
| e) Costo e schedule | PASS |

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
  - 9367 voci
- **PASS** land.json
  - 4 voci
- **PASS** landmarks.json
  - 1664 voci
- **PASS** dem.npz
- **PASS** anni edifici (38241)
  - senza anno 0, dopo 2026: 0, prima di 1238 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (9367 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (13838 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 344, nel 1800 984

## c) Densita' storica

- **PASS** Muslim walled city nel 1238
  - 1920 edifici vivi (53/ha, copertura 65%) contro 1054 (29/ha, copertura 76%) nel 2026: rapporto 1.82
- **PASS** Muslim walled city nel 1500
  - 1904 edifici vivi (53/ha, copertura 72%) contro 1054 (29/ha, copertura 76%) nel 2026: rapporto 1.81
- **PASS** Muslim walled city nel 1800
  - 1744 edifici vivi (48/ha, copertura 76%) contro 1054 (29/ha, copertura 76%) nel 2026: rapporto 1.65
- **PASS** Boatella quarter (inside 1356 wall) nel 1500
  - 1944 edifici vivi (48/ha, copertura 61%) contro 668 (17/ha, copertura 62%) nel 2026: rapporto 2.91
- **PASS** Boatella quarter (inside 1356 wall) nel 1800
  - 1944 edifici vivi (48/ha, copertura 61%) contro 668 (17/ha, copertura 62%) nel 2026: rapporto 2.91
- **PASS** Christian expansion within the 1356 wall nel 1500
  - 7123 edifici vivi (44/ha, copertura 57%) contro 3281 (20/ha, copertura 60%) nel 2026: rapporto 2.17
- **PASS** Christian expansion within the 1356 wall nel 1800
  - 6803 edifici vivi (42/ha, copertura 65%) contro 3281 (20/ha, copertura 60%) nel 2026: rapporto 2.07
- **PASS** Quart suburb (arrabal de Quart) nel 1800
  - 355 edifici vivi (37/ha, copertura 54%) contro 242 (25/ha, copertura 56%) nel 2026: rapporto 1.47
- **PASS** Morvedre suburb (north of the Turia) nel 1800
  - 491 edifici vivi (32/ha, copertura 41%) contro 186 (12/ha, copertura 54%) nel 2026: rapporto 2.64
- **PASS** Russafa village nel 1800
  - 300 edifici vivi (35/ha, copertura 55%) contro 142 (17/ha, copertura 58%) nel 2026: rapporto 2.11
- **PASS** El Grau (Vilanova del Grau) nel 1800
  - 7 edifici vivi (1/ha, copertura 1%) contro 7 (1/ha, copertura 1%) nel 2026: rapporto 1.00

## d) Corridoi vuoti

- **PASS** 1238: nessun corridoio vuoto
  - corridoi_1238.png
- **WARN** 1338: 4 aree vuote allungate
  - #1 1212x126 m a (39.48675,-0.37460); #2 1608x324 m a (39.47061,-0.37378); #3 679x118 m a (39.47504,-0.38856); #4 153x32 m a (39.47104,-0.37339) — corridoi_1338.png
- **WARN** 1338: 1 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #5 304x52 m a (39.47179,-0.37353)
- **FAIL** 1800: 1 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 120x24 m a (39.47144,-0.32993) — corridoi_1800.png
- **WARN** 1800: 3 aree vuote allungate
  - #2 394x82 m a (39.47741,-0.37097); #3 353x79 m a (39.47461,-0.36783); #4 169x33 m a (39.46813,-0.37793) — corridoi_1800.png
- **WARN** 1800: 2 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #5 582x20 m a (39.47602,-0.37122); #6 241x26 m a (39.46464,-0.32928)
- **WARN** 1900: 3 aree vuote allungate
  - #1 402x80 m a (39.47745,-0.37097); #2 363x84 m a (39.47461,-0.36778); #3 169x33 m a (39.46813,-0.37793) — corridoi_1900.png
- **WARN** 1900: 2 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #4 552x24 m a (39.47602,-0.37122); #5 524x31 m a (39.46896,-0.37851)
- **WARN** 1950: 4 aree vuote allungate
  - #1 402x80 m a (39.47745,-0.37097); #2 404x86 m a (39.47450,-0.36766); #3 225x53 m a (39.47048,-0.37648); #4 169x33 m a (39.46813,-0.37793) — corridoi_1950.png

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 1539, cambi in tutto il video 56171, max in un fotogramma 406 (~5 s), costo dei soli cambi ~0.19 h (budget 1.0 h)
- **PASS** 26 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** evento forte entro 45 s
  - primo a 9.5 s
- **PASS** notte
  - night_t=460.5, schedule_valencia_night.json ok

## Immagini

![corridoi_1238.png](corridoi_1238.png)
![corridoi_1338.png](corridoi_1338.png)
![corridoi_1800.png](corridoi_1800.png)
![corridoi_1900.png](corridoi_1900.png)
![corridoi_1950.png](corridoi_1950.png)
