# QA roma

Generato da `python -m kit.qa` il 2026-11-19 16:57. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| e) Costo e schedule | WARN |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 53 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_roma
- **PASS** buildings.json
  - 92572 voci
- **PASS** roads.json
  - 44335 voci
- **PASS** hist.json
  - 39833 voci
- **PASS** land.json
  - 16 voci
- **PASS** landmarks.json
  - 1706 voci
- **PASS** dem.npz
- **PASS** anni edifici (92572)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di -753 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (39833 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (44335 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 0, nel 1800 6028

## c) Densita' storica

- **PASS** First settlements: Palatine, Capitoline and Forum valley nel 1500
  - 1549 edifici vivi (18/ha, copertura 38%) contro 711 (8/ha, copertura 39%) nel 2026: rapporto 2.18
- **PASS** First settlements: Palatine, Capitoline and Forum valley nel 1800
  - 1337 edifici vivi (16/ha, copertura 38%) contro 711 (8/ha, copertura 39%) nel 2026: rapporto 1.88
- **PASS** Servian Rome (walled area, 246 ha) nel 1500
  - 5843 edifici vivi (24/ha, copertura 36%) contro 2136 (9/ha, copertura 38%) nel 2026: rapporto 2.74
- **PASS** Servian Rome (walled area, 246 ha) nel 1800
  - 5085 edifici vivi (21/ha, copertura 37%) contro 2136 (9/ha, copertura 38%) nel 2026: rapporto 2.38
- **PASS** Republican and Imperial Rome within the Aurelian Walls nel 1500
  - 34181 edifici vivi (26/ha, copertura 35%) contro 10113 (8/ha, copertura 38%) nel 2026: rapporto 3.38
- **PASS** Republican and Imperial Rome within the Aurelian Walls nel 1800
  - 30181 edifici vivi (23/ha, copertura 35%) contro 10113 (8/ha, copertura 38%) nel 2026: rapporto 2.98
- **PASS** Vatican and Leonine City nel 1500
  - 1599 edifici vivi (28/ha, copertura 40%) contro 403 (7/ha, copertura 51%) nel 2026: rapporto 3.97
- **PASS** Vatican and Leonine City nel 1800
  - 1273 edifici vivi (23/ha, copertura 53%) contro 403 (7/ha, copertura 51%) nel 2026: rapporto 3.16

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 2083, cambi in tutto il video 63252, max in un fotogramma 388 (~5 s), costo dei soli cambi ~0.21 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 122 m/s (limite 250), mediana 23
- **PASS** drone: accelerazione massima
  - 115 m/s2 (limite 120), 99% 43
- **PASS** drone: jerk massimo
  - 113 m/s3 (limite 200), 99% 56
- **PASS** drone: distanza minima da terreno e tetti
  - 460 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 16 tenute, 0 solo sorvolate; hover 81 s, volo 502 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.1 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1586 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **WARN** drone: grafico non fatto
  - No module named 'matplotlib'
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 30.4 s (226-256 s); 7 oltre 15 s: 16-33, 60-76, 76-99, 114-130, 198-226, 226-256
- **PASS** ritmo: anni/s per minuto
  - 0:00 38.97 | 1:00  5.08 | 2:00  4.05 | 3:00  2.44 | 4:00  3.47 | 5:00 13.12 | 6:00  7.87 | 7:00  1.48 | 8:00  0.55 | 9:00  0.92 | 10:00  0.00
- **PASS** 16 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
