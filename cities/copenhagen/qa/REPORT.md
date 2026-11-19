# QA copenhagen

Generato da `python -m kit.qa` il 2026-11-19 16:16. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| e) Costo e schedule | WARN |

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 198, cambi in tutto il video 3397, max in un fotogramma 33 (~0 s), costo dei soli cambi ~0.01 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 225 m/s (limite 250), mediana 7
- **PASS** drone: accelerazione massima
  - 102 m/s2 (limite 120), 99% 57
- **PASS** drone: jerk massimo
  - 90 m/s3 (limite 200), 99% 45
- **PASS** drone: distanza minima da terreno e tetti
  - 480 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **WARN** drone: soste tolte per tempo
  - 1 tolte, 16 tenute, 0 solo sorvolate; hover 126 s, volo 321 s; The Øresund Bridge (2000) (1996)
- **PASS** drone: hover quasi fermo
  - v max in hover 8.6 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1567 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **PASS** drone: grafico del percorso
  - qa/drone_path.png
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 27.3 s (282-310 s); 2 oltre 15 s: 282-310, 326-352
- **PASS** ritmo: anni/s per minuto
  - 0:00  9.11 | 1:00  3.41 | 2:00  1.86 | 3:00  1.42 | 4:00  0.72 | 5:00  0.79 | 6:00  0.84 | 7:00  0.06 | 8:00  0.00 | 9:00  0.00 | 10:00  0.00
- **PASS** 17 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 12.9 s
- **PASS** notte
  - night_t=460.5, schedule_copenhagen_night.json ok
