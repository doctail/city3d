# QA rotterdam

Generato da `python -m kit.qa` il 2026-11-19 17:08. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| e) Costo e schedule | WARN |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 40 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_rotterdam
- **PASS** buildings.json
  - 268466 voci
- **PASS** roads.json
  - 248402 voci
- **PASS** hist.json
  - 13456 voci
- **PASS** land.json
  - 1004 voci
- **PASS** landmarks.json
  - 200 voci
- **PASS** dem.npz
- **PASS** anni edifici (268466)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di 1270 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (13456 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (248402 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 0, nel 1800 13834

## c) Densita' storica

- **PASS** Dam settlement on the Rotte nel 1500
  - 970 edifici vivi (36/ha, copertura 40%) contro 440 (16/ha, copertura 41%) nel 2026: rapporto 2.20
- **PASS** Dam settlement on the Rotte nel 1800
  - 981 edifici vivi (36/ha, copertura 40%) contro 440 (16/ha, copertura 41%) nel 2026: rapporto 2.23
- **PASS** Walled town between Coolsingel, Goudsesingel and the Hoogstraat nel 1500
  - 605 edifici vivi (36/ha, copertura 44%) contro 270 (16/ha, copertura 58%) nel 2026: rapporto 2.24
- **PASS** Walled town between Coolsingel, Goudsesingel and the Hoogstraat nel 1800
  - 616 edifici vivi (37/ha, copertura 45%) contro 270 (16/ha, copertura 58%) nel 2026: rapporto 2.28
- **PASS** The Water Town nel 1800
  - 2101 edifici vivi (20/ha, copertura 21%) contro 966 (9/ha, copertura 23%) nel 2026: rapporto 2.17
- **PASS** Delfshaven harbor town nel 1800
  - 1672 edifici vivi (39/ha, copertura 32%) contro 1579 (36/ha, copertura 33%) nel 2026: rapporto 1.06
- **PASS** Schiedam nel 1500
  - 5678 edifici vivi (39/ha, copertura 29%) contro 4621 (31/ha, copertura 31%) nel 2026: rapporto 1.23
- **PASS** Schiedam nel 1800
  - 5656 edifici vivi (38/ha, copertura 29%) contro 4621 (31/ha, copertura 31%) nel 2026: rapporto 1.22

## e) Costo e schedule

- **PASS** costo dei cambi (7 s)
  - oggetti citta' 1497, cambi in tutto il video 52344, max in un fotogramma 439 (~5 s), costo dei soli cambi ~0.17 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 172 m/s (limite 250), mediana 8
- **PASS** drone: accelerazione massima
  - 112 m/s2 (limite 120), 99% 60
- **PASS** drone: jerk massimo
  - 100 m/s3 (limite 200), 99% 47
- **PASS** drone: distanza minima da terreno e tetti
  - 460 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 16 tenute, 0 solo sorvolate; hover 158 s, volo 400 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 9.1 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1690 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **WARN** drone: grafico non fatto
  - No module named 'matplotlib'
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 21.7 s (63-84 s); 2 oltre 15 s: 63-84, 476-494
- **PASS** ritmo: anni/s per minuto
  - 0:00 10.86 | 1:00  3.31 | 2:00  3.07 | 3:00  2.03 | 4:00  0.78 | 5:00  0.31 | 6:00  0.36 | 7:00  0.49 | 8:00  0.45 | 9:00  0.06
- **PASS** 16 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
