# QA sevilla

Generato da `python -m kit.qa` il 2026-11-19 17:02. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| e) Costo e schedule | WARN |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 55 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_sevilla
- **PASS** buildings.json
  - 58696 voci
- **PASS** roads.json
  - 88841 voci
- **PASS** hist.json
  - 26676 voci
- **PASS** land.json
  - 11 voci
- **PASS** landmarks.json
  - 867 voci
- **PASS** dem.npz
- **PASS** anni edifici (58696)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di 1248 (compaiono all'inizio): 2, d<=y: 0, ring<3: 0
- **PASS** hist (26676 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (88841 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 6003, nel 1800 17715

## c) Densita' storica

- **PASS** Alameda de Hércules: houses around the drained lagoon nel 1800
  - 942 edifici vivi (48/ha, copertura 55%) contro 659 (33/ha, copertura 57%) nel 2026: rapporto 1.43
- **PASS** Northern gardens inside the walls (San Gil, Macarena) nel 1500
  - 3686 edifici vivi (50/ha, copertura 60%) contro 2036 (28/ha, copertura 62%) nel 2026: rapporto 1.81
- **PASS** Northern gardens inside the walls (San Gil, Macarena) nel 1800
  - 3663 edifici vivi (50/ha, copertura 60%) contro 2036 (28/ha, copertura 62%) nel 2026: rapporto 1.80
- **PASS** Arenal and port of the Indies nel 1800
  - 880 edifici vivi (49/ha, copertura 61%) contro 579 (32/ha, copertura 65%) nel 2026: rapporto 1.52
- **PASS** Triana nel 1800
  - 4290 edifici vivi (27/ha, copertura 33%) contro 2069 (13/ha, copertura 35%) nel 2026: rapporto 2.07
- **PASS** Suburb: San Bernardo nel 1800
  - 2960 edifici vivi (23/ha, copertura 26%) contro 634 (5/ha, copertura 29%) nel 2026: rapporto 4.67
- **PASS** Suburb: Macarena nel 1800
  - 1224 edifici vivi (21/ha, copertura 26%) contro 541 (9/ha, copertura 27%) nel 2026: rapporto 2.26
- **PASS** Suburb: San Roque / Puerta de Carmona nel 1800
  - 3042 edifici vivi (28/ha, copertura 33%) contro 697 (6/ha, copertura 36%) nel 2026: rapporto 4.36
- **PASS** Suburb: Extramuros Puerta del Sol / Osario nel 1800
  - 3514 edifici vivi (30/ha, copertura 36%) contro 1586 (14/ha, copertura 38%) nel 2026: rapporto 2.22
- **PASS** Almohad walled city (Ishbiliya) nel 1248
  - 9644 edifici vivi (36/ha, copertura 46%) contro 7253 (27/ha, copertura 64%) nel 2026: rapporto 1.33
- **PASS** Almohad walled city (Ishbiliya) nel 1500
  - 13159 edifici vivi (49/ha, copertura 63%) contro 7253 (27/ha, copertura 64%) nel 2026: rapporto 1.81
- **PASS** Almohad walled city (Ishbiliya) nel 1800
  - 13075 edifici vivi (48/ha, copertura 63%) contro 7253 (27/ha, copertura 64%) nel 2026: rapporto 1.80

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 1907, cambi in tutto il video 64416, max in un fotogramma 751 (~9 s), costo dei soli cambi ~0.21 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 112 m/s (limite 250), mediana 12
- **PASS** drone: accelerazione massima
  - 25 m/s2 (limite 120), 99% 18
- **PASS** drone: jerk massimo
  - 26 m/s3 (limite 200), 99% 13
- **PASS** drone: distanza minima da terreno e tetti
  - 477 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 9 tenute, 0 solo sorvolate; hover 81 s, volo 398 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.2 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1520 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **WARN** drone: grafico non fatto
  - No module named 'matplotlib'
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 15.4 s (413-428 s); 2 oltre 15 s: 299-314, 413-428
- **PASS** ritmo: anni/s per minuto
  - 0:00 10.38 | 1:00  4.10 | 2:00  2.85 | 3:00  1.13 | 4:00  1.03 | 5:00  0.52 | 6:00  0.33 | 7:00  0.41 | 8:00  0.01
- **PASS** 9 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
- **PASS** notte
  - night_t=495.15363282265685, schedule_sevilla_night.json ok
