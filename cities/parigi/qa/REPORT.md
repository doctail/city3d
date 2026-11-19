# QA parigi

Generato da `python -m kit.qa` il 2026-11-19 16:55. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | WARN |
| c) Densita' storica | PASS |
| e) Costo e schedule | WARN |

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

## e) Costo e schedule

- **PASS** costo dei cambi (18 s)
  - oggetti citta' 6604, cambi in tutto il video 215547, max in un fotogramma 1954 (~23 s), costo dei soli cambi ~0.72 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 175 m/s (limite 250), mediana 8
- **PASS** drone: accelerazione massima
  - 39 m/s2 (limite 120), 99% 25
- **PASS** drone: jerk massimo
  - 15 m/s3 (limite 200), 99% 9
- **PASS** drone: distanza minima da terreno e tetti
  - 395 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 10 tenute, 0 solo sorvolate; hover 173 s, volo 520 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.3 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1535 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **WARN** drone: grafico non fatto
  - No module named 'matplotlib'
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 18.0 s (244-262 s); 3 oltre 15 s: 201-219, 219-235, 244-262
- **PASS** ritmo: anni/s per minuto
  - 0:00 11.35 | 1:00  3.35 | 2:00  2.19 | 3:00  1.29 | 4:00  0.83 | 5:00  0.38 | 6:00  0.53 | 7:00  0.60 | 8:00  0.55 | 9:00  0.81 | 10:00  0.79 | 11:00  0.02 | 12:00  0.00
- **PASS** 10 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
- **PASS** notte
  - night_t=708.237809884089, schedule_parigi_night.json ok
