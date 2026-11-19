# QA rotterdam

Generato da `python -m kit.qa` il 2026-11-19 16:25. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| e) Costo e schedule | WARN |

## e) Costo e schedule

- **PASS** costo dei cambi (7 s)
  - oggetti citta' 1490, cambi in tutto il video 52109, max in un fotogramma 439 (~5 s), costo dei soli cambi ~0.17 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 170 m/s (limite 250), mediana 8
- **PASS** drone: accelerazione massima
  - 111 m/s2 (limite 120), 99% 61
- **PASS** drone: jerk massimo
  - 99 m/s3 (limite 200), 99% 47
- **PASS** drone: distanza minima da terreno e tetti
  - 464 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 17 tenute, 0 solo sorvolate; hover 169 s, volo 408 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.2 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **WARN** drone: voli con gli anni quasi fermi
  - 276-293 s (17 s, 0.33 anni/s) verso 'City Hall opens on the Coo'; 354-383 s (28 s, 0.20 anni/s) verso 'The center is redesigned ('  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1687 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **PASS** drone: grafico del percorso
  - qa/drone_path.png
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 21.6 s (63-84 s); 2 oltre 15 s: 63-84, 499-517
- **PASS** ritmo: anni/s per minuto
  - 0:00 10.86 | 1:00  3.31 | 2:00  3.05 | 3:00  2.05 | 4:00  0.71 | 5:00  0.35 | 6:00  0.29 | 7:00  0.37 | 8:00  0.54 | 9:00  0.19 | 10:00  0.00
- **PASS** 17 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
