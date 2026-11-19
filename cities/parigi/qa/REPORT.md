# QA parigi

Generato da `python -m kit.qa` il 2026-11-19 16:01. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | WARN |
| c) Densita' storica | PASS |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 215 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_parigi
- **PASS** buildings.json
  - 239538 voci
- **PASS** roads.json
  - 293856 voci
- **PASS** hist.json
  - 402130 voci
- **PASS** land.json
  - 63 voci
- **PASS** landmarks.json
  - 794 voci
- **PASS** dem.npz
- **PASS** anni edifici (239538)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di 1190 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (402130 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **WARN** anni strade (293856 nastri)
  - senza anno 0, dopo 2026: 113; visibili all'inizio 4021, nel 1800 82857

## c) Densita' storica

- **PASS** Paris core of 1190: Cite (Île de la Cité) nel 1190
  - 1546 edifici vivi (25/ha, copertura 34%) contro 797 (13/ha, copertura 50%) nel 2026: rapporto 1.94
- **PASS** Paris core of 1190: Cite (Île de la Cité) nel 1500
  - 1493 edifici vivi (24/ha, copertura 49%) contro 797 (13/ha, copertura 50%) nel 2026: rapporto 1.87
- **PASS** Paris core of 1190: Cite (Île de la Cité) nel 1800
  - 1314 edifici vivi (21/ha, copertura 49%) contro 797 (13/ha, copertura 50%) nel 2026: rapporto 1.65
- **PASS** Paris core of 1190: Grève / Saint-Gervais nel 1190
  - 1388 edifici vivi (31/ha, copertura 39%) contro 551 (12/ha, copertura 47%) nel 2026: rapporto 2.52
- **PASS** Paris core of 1190: Grève / Saint-Gervais nel 1500
  - 1487 edifici vivi (33/ha, copertura 40%) contro 551 (12/ha, copertura 47%) nel 2026: rapporto 2.70
- **PASS** Paris core of 1190: Grève / Saint-Gervais nel 1800
  - 1339 edifici vivi (30/ha, copertura 45%) contro 551 (12/ha, copertura 47%) nel 2026: rapporto 2.43
- **PASS** Paris core of 1190: Saint-Germain-des-Prés nel 1190
  - 628 edifici vivi (42/ha, copertura 53%) contro 324 (22/ha, copertura 61%) nel 2026: rapporto 1.94
- **PASS** Paris core of 1190: Saint-Germain-des-Prés nel 1500
  - 628 edifici vivi (42/ha, copertura 53%) contro 324 (22/ha, copertura 61%) nel 2026: rapporto 1.94
- **PASS** Paris core of 1190: Saint-Germain-des-Prés nel 1800
  - 562 edifici vivi (38/ha, copertura 54%) contro 324 (22/ha, copertura 61%) nel 2026: rapporto 1.73
- **PASS** Paris core of 1190: Sainte-Geneviève nel 1190
  - 435 edifici vivi (35/ha, copertura 39%) contro 170 (14/ha, copertura 58%) nel 2026: rapporto 2.56
- **PASS** Paris core of 1190: Sainte-Geneviève nel 1500
  - 450 edifici vivi (36/ha, copertura 40%) contro 170 (14/ha, copertura 58%) nel 2026: rapporto 2.65
- **PASS** Paris core of 1190: Sainte-Geneviève nel 1800
  - 418 edifici vivi (34/ha, copertura 56%) contro 170 (14/ha, copertura 58%) nel 2026: rapporto 2.46
- **PASS** Paris core of 1190: Saint-Marcel nel 1190
  - 462 edifici vivi (31/ha, copertura 39%) contro 190 (13/ha, copertura 45%) nel 2026: rapporto 2.43
- **PASS** Paris core of 1190: Saint-Marcel nel 1500
  - 462 edifici vivi (31/ha, copertura 39%) contro 190 (13/ha, copertura 45%) nel 2026: rapporto 2.43
- **PASS** Paris core of 1190: Saint-Marcel nel 1800
  - 491 edifici vivi (33/ha, copertura 41%) contro 190 (13/ha, copertura 45%) nel 2026: rapporto 2.58
- **PASS** Paris core of 1190: Saint-Martin-des-Champs nel 1190
  - 258 edifici vivi (33/ha, copertura 48%) contro 80 (10/ha, copertura 62%) nel 2026: rapporto 3.23
- **PASS** Paris core of 1190: Saint-Martin-des-Champs nel 1500
  - 259 edifici vivi (33/ha, copertura 49%) contro 80 (10/ha, copertura 62%) nel 2026: rapporto 3.24
- **PASS** Paris core of 1190: Saint-Martin-des-Champs nel 1800
  - 259 edifici vivi (33/ha, copertura 49%) contro 80 (10/ha, copertura 62%) nel 2026: rapporto 3.24
- **PASS** Inside the Philip Augustus wall (1190-1213) nel 1500
  - 7894 edifici vivi (33/ha, copertura 47%) contro 3585 (15/ha, copertura 52%) nel 2026: rapporto 2.20
- **PASS** Inside the Philip Augustus wall (1190-1213) nel 1800
  - 6939 edifici vivi (29/ha, copertura 49%) contro 3585 (15/ha, copertura 52%) nel 2026: rapporto 1.94
- **PASS** Inside the Charles V wall (1356-1383), right bank nel 1500
  - 19356 edifici vivi (36/ha, copertura 52%) contro 8122 (15/ha, copertura 58%) nel 2026: rapporto 2.38
- **PASS** Inside the Charles V wall (1356-1383), right bank nel 1800
  - 17065 edifici vivi (32/ha, copertura 59%) contro 8122 (15/ha, copertura 58%) nel 2026: rapporto 2.10
- **PASS** Louis XIII wall quarters (1633-1636), west right bank nel 1800
  - 2581 edifici vivi (39/ha, copertura 52%) contro 769 (12/ha, copertura 57%) nel 2026: rapporto 3.36
- **PASS** Inside the Farmers-General wall (1784-1791) nel 1800
  - 120657 edifici vivi (33/ha, copertura 44%) contro 42401 (12/ha, copertura 47%) nel 2026: rapporto 2.85
