# QA sevilla

Generato da `python -m kit.qa` il 2026-11-19 16:13. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| e) Costo e schedule | WARN |

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 1906, cambi in tutto il video 66190, max in un fotogramma 751 (~9 s), costo dei soli cambi ~0.22 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 112 m/s (limite 250), mediana 11
- **PASS** drone: accelerazione massima
  - 25 m/s2 (limite 120), 99% 16
- **PASS** drone: jerk massimo
  - 26 m/s3 (limite 200), 99% 13
- **PASS** drone: distanza minima da terreno e tetti
  - 395 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 10 tenute, 0 solo sorvolate; hover 86 s, volo 424 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.2 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **WARN** drone: voli con gli anni quasi fermi
  - 342-375 s (33 s, 0.27 anni/s) verso 'The river is moved west: C'; 380-406 s (26 s, 0.31 anni/s) verso 'Expo 92 (20 April - 12 Oct'  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1445 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **PASS** drone: grafico del percorso
  - qa/drone_path.png
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 15.4 s (445-460 s); 2 oltre 15 s: 299-314, 445-460
- **PASS** ritmo: anni/s per minuto
  - 0:00 10.38 | 1:00  4.09 | 2:00  2.85 | 3:00  1.19 | 4:00  0.98 | 5:00  0.42 | 6:00  0.29 | 7:00  0.54 | 8:00  0.02 | 9:00  0.00
- **PASS** 10 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
- **PASS** notte
  - night_t=526.6922329009448, schedule_sevilla_night.json ok
