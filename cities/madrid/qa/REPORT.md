# QA madrid

Generato da `python -m kit.qa` il 2026-11-19 17:04. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| e) Costo e schedule | WARN |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 49 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_madrid
- **PASS** buildings.json
  - 120964 voci
- **PASS** roads.json
  - 434159 voci
- **PASS** hist.json
  - 62139 voci
- **PASS** land.json
  - 45 voci
- **PASS** landmarks.json
  - 903 voci
- **PASS** dem.npz
- **PASS** anni edifici (120964)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di 860 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (62139 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (434159 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 0, nel 1800 25249

## c) Densita' storica

- **PASS** Mayrit: Muslim citadel and town nel 1500
  - 86 edifici vivi (22/ha, copertura 22%) contro 24 (6/ha, copertura 40%) nel 2026: rapporto 3.58
- **PASS** Mayrit: Muslim citadel and town nel 1800
  - 42 edifici vivi (11/ha, copertura 37%) contro 24 (6/ha, copertura 40%) nel 2026: rapporto 1.75
- **PASS** Christian walled town nel 1500
  - 974 edifici vivi (29/ha, copertura 37%) contro 364 (11/ha, copertura 50%) nel 2026: rapporto 2.68
- **PASS** Christian walled town nel 1800
  - 855 edifici vivi (26/ha, copertura 38%) contro 364 (11/ha, copertura 50%) nel 2026: rapporto 2.35
- **PASS** Medieval suburbs (arrabales) and the 15th-century wall nel 1800
  - 3462 edifici vivi (34/ha, copertura 53%) contro 1422 (14/ha, copertura 60%) nel 2026: rapporto 2.43
- **PASS** Habsburg Madrid inside Philip IV's wall (western part) nel 1800
  - 19317 edifici vivi (35/ha, copertura 49%) contro 7350 (13/ha, copertura 54%) nel 2026: rapporto 2.63

## e) Costo e schedule

- **PASS** costo dei cambi (7 s)
  - oggetti citta' 1732, cambi in tutto il video 54953, max in un fotogramma 673 (~8 s), costo dei soli cambi ~0.18 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 202 m/s (limite 250), mediana 16
- **PASS** drone: accelerazione massima
  - 95 m/s2 (limite 120), 99% 44
- **PASS** drone: jerk massimo
  - 86 m/s3 (limite 200), 99% 36
- **PASS** drone: distanza minima da terreno e tetti
  - 424 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 12 tenute, 0 solo sorvolate; hover 105 s, volo 468 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.2 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1556 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **WARN** drone: grafico non fatto
  - No module named 'matplotlib'
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 19.5 s (138-157 s); 5 oltre 15 s: 138-157, 364-380, 401-418, 437-455, 505-520
- **PASS** ritmo: anni/s per minuto
  - 0:00 13.65 | 1:00  6.84 | 2:00  2.28 | 3:00  1.73 | 4:00  0.69 | 5:00  0.61 | 6:00  0.55 | 7:00  0.54 | 8:00  0.37 | 9:00  0.03 | 10:00  0.00
- **PASS** 12 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
