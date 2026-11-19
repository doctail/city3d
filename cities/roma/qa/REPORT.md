# QA roma

Generato da `python -m kit.qa` il 2026-11-19 16:10. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| e) Costo e schedule | WARN |

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 2023, cambi in tutto il video 61269, max in un fotogramma 383 (~5 s), costo dei soli cambi ~0.20 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 122 m/s (limite 250), mediana 24
- **PASS** drone: accelerazione massima
  - 116 m/s2 (limite 120), 99% 41
- **PASS** drone: jerk massimo
  - 120 m/s3 (limite 200), 99% 57
- **PASS** drone: distanza minima da terreno e tetti
  - 460 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 16 tenute, 0 solo sorvolate; hover 81 s, volo 508 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.2 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1594 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **PASS** drone: grafico del percorso
  - qa/drone_path.png
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 30.4 s (232-262 s); 6 oltre 15 s: 16-32, 57-74, 74-97, 204-232, 232-262, 440-455
- **PASS** ritmo: anni/s per minuto
  - 0:00 38.97 | 1:00  5.64 | 2:00  3.13 | 3:00  2.62 | 4:00  3.01 | 5:00 13.29 | 6:00  7.89 | 7:00  1.82 | 8:00  0.60 | 9:00  0.90 | 10:00  0.25
- **PASS** 16 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
