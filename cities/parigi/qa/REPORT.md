# QA parigi

Generato da `python -m kit.qa` il 2026-11-27 18:01. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | WARN |
| c) Densita' storica | PASS |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 243 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - ../../../tmp/dp
- **PASS** buildings.json
  - 239538 voci
- **PASS** roads.json
  - 293856 voci
- **PASS** hist.json
  - 403441 voci
- **PASS** land.json
  - 63 voci
- **PASS** landmarks.json
  - 2172 voci
- **PASS** dem.npz
- **PASS** anni edifici (239538)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di 1190 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (403441 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **WARN** anni strade (293856 nastri)
  - senza anno 0, dopo 2026: 113; visibili all'inizio 3790, nel 1800 81665

## c) Densita' storica

- **PASS** Paris core of 1190: Cite (Île de la Cité) nel 1190
  - 1730 edifici vivi (28/ha, copertura 38%) contro 797 (13/ha, copertura 50%) nel 2026: rapporto 2.17
- **PASS** Paris core of 1190: Cite (Île de la Cité) nel 1500
  - 1665 edifici vivi (27/ha, copertura 51%) contro 797 (13/ha, copertura 50%) nel 2026: rapporto 2.09
- **PASS** Paris core of 1190: Cite (Île de la Cité) nel 1800
  - 1489 edifici vivi (24/ha, copertura 52%) contro 797 (13/ha, copertura 50%) nel 2026: rapporto 1.87
- **PASS** Paris core of 1190: Grève / Saint-Gervais nel 1190
  - 1467 edifici vivi (33/ha, copertura 41%) contro 551 (12/ha, copertura 47%) nel 2026: rapporto 2.66
- **PASS** Paris core of 1190: Grève / Saint-Gervais nel 1500
  - 1570 edifici vivi (35/ha, copertura 42%) contro 551 (12/ha, copertura 47%) nel 2026: rapporto 2.85
- **PASS** Paris core of 1190: Grève / Saint-Gervais nel 1800
  - 1436 edifici vivi (32/ha, copertura 46%) contro 551 (12/ha, copertura 47%) nel 2026: rapporto 2.61
- **PASS** Paris core of 1190: Saint-Germain-des-Prés nel 1190
  - 658 edifici vivi (44/ha, copertura 54%) contro 324 (22/ha, copertura 61%) nel 2026: rapporto 2.03
- **PASS** Paris core of 1190: Saint-Germain-des-Prés nel 1500
  - 658 edifici vivi (44/ha, copertura 54%) contro 324 (22/ha, copertura 61%) nel 2026: rapporto 2.03
- **PASS** Paris core of 1190: Saint-Germain-des-Prés nel 1800
  - 592 edifici vivi (40/ha, copertura 56%) contro 324 (22/ha, copertura 61%) nel 2026: rapporto 1.83
- **PASS** Paris core of 1190: Sainte-Geneviève nel 1190
  - 430 edifici vivi (35/ha, copertura 40%) contro 170 (14/ha, copertura 58%) nel 2026: rapporto 2.53
- **PASS** Paris core of 1190: Sainte-Geneviève nel 1500
  - 461 edifici vivi (37/ha, copertura 42%) contro 170 (14/ha, copertura 58%) nel 2026: rapporto 2.71
- **PASS** Paris core of 1190: Sainte-Geneviève nel 1800
  - 418 edifici vivi (34/ha, copertura 56%) contro 170 (14/ha, copertura 58%) nel 2026: rapporto 2.46
- **PASS** Paris core of 1190: Saint-Marcel nel 1190
  - 462 edifici vivi (31/ha, copertura 39%) contro 190 (13/ha, copertura 45%) nel 2026: rapporto 2.43
- **PASS** Paris core of 1190: Saint-Marcel nel 1500
  - 462 edifici vivi (31/ha, copertura 39%) contro 190 (13/ha, copertura 45%) nel 2026: rapporto 2.43
- **PASS** Paris core of 1190: Saint-Marcel nel 1800
  - 495 edifici vivi (33/ha, copertura 41%) contro 190 (13/ha, copertura 45%) nel 2026: rapporto 2.61
- **PASS** Paris core of 1190: Saint-Martin-des-Champs nel 1190
  - 279 edifici vivi (35/ha, copertura 50%) contro 80 (10/ha, copertura 62%) nel 2026: rapporto 3.49
- **PASS** Paris core of 1190: Saint-Martin-des-Champs nel 1500
  - 280 edifici vivi (35/ha, copertura 50%) contro 80 (10/ha, copertura 62%) nel 2026: rapporto 3.50
- **PASS** Paris core of 1190: Saint-Martin-des-Champs nel 1800
  - 280 edifici vivi (35/ha, copertura 50%) contro 80 (10/ha, copertura 62%) nel 2026: rapporto 3.50
- **PASS** Inside the Philip Augustus wall (1190-1213) nel 1500
  - 8384 edifici vivi (35/ha, copertura 49%) contro 3585 (15/ha, copertura 52%) nel 2026: rapporto 2.34
- **PASS** Inside the Philip Augustus wall (1190-1213) nel 1800
  - 7403 edifici vivi (31/ha, copertura 51%) contro 3585 (15/ha, copertura 52%) nel 2026: rapporto 2.06
- **PASS** Inside the Charles V wall (1356-1383), right bank nel 1500
  - 20235 edifici vivi (38/ha, copertura 53%) contro 8122 (15/ha, copertura 58%) nel 2026: rapporto 2.49
- **PASS** Inside the Charles V wall (1356-1383), right bank nel 1800
  - 17674 edifici vivi (33/ha, copertura 60%) contro 8122 (15/ha, copertura 58%) nel 2026: rapporto 2.18
- **PASS** Louis XIII wall quarters (1633-1636), west right bank nel 1800
  - 2652 edifici vivi (40/ha, copertura 53%) contro 769 (12/ha, copertura 57%) nel 2026: rapporto 3.45
- **PASS** Inside the Farmers-General wall (1784-1791) nel 1800
  - 122376 edifici vivi (34/ha, copertura 44%) contro 42409 (12/ha, copertura 47%) nel 2026: rapporto 2.89
