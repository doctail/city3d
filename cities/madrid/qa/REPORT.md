# QA madrid

Generato da `python -m kit.qa` il 2026-11-19 16:21. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| e) Costo e schedule | WARN |

## e) Costo e schedule

- **PASS** costo dei cambi (7 s)
  - oggetti citta' 1702, cambi in tutto il video 50537, max in un fotogramma 667 (~8 s), costo dei soli cambi ~0.17 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 169 m/s (limite 250), mediana 16
- **PASS** drone: accelerazione massima
  - 111 m/s2 (limite 120), 99% 44
- **PASS** drone: jerk massimo
  - 103 m/s3 (limite 200), 99% 33
- **PASS** drone: distanza minima da terreno e tetti
  - 432 m (soglia 24); dal solo terreno 500 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 16 tenute, 0 solo sorvolate; hover 156 s, volo 476 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.2 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **WARN** drone: voli con gli anni quasi fermi
  - 139-155 s (16 s, 0.31 anni/s) verso 'Philip IV rings the city w'; 298-310 s (12 s, 0.08 anni/s) verso 'Castro's Ensanche grid tak'; 395-422 s (27 s, 0.25 anni/s) verso 'The Bernabéu stadium opens'; 432-456 s (25 s, 0.22 anni/s) verso 'The Torre de Madrid tops S'; 499-558 s (59 s, 0.22 anni/s) verso 'Four towers redraw the sky'  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1573 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **PASS** drone: grafico del percorso
  - qa/drone_path.png
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 53.4 s (505-558 s); 7 oltre 15 s: 62-81, 133-155, 174-190, 293-310, 386-422, 427-456
- **PASS** ritmo: anni/s per minuto
  - 0:00 14.43 | 1:00  6.82 | 2:00  2.23 | 3:00  1.82 | 4:00  0.96 | 5:00  0.91 | 6:00  0.35 | 7:00  0.51 | 8:00  0.50 | 9:00  0.31 | 10:00  0.02
- **PASS** 16 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 15.7 s
