# QA copenhagen

Generato da `python -m kit.qa` il 2026-11-28 01:28. Esito complessivo: **WARN**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| d) Corridoi vuoti | WARN |
| e) Costo e schedule | WARN |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 55 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_copenhagen
- **PASS** buildings.json
  - 131817 voci
- **PASS** roads.json
  - 128234 voci
- **PASS** hist.json
  - 135580 voci
- **PASS** land.json
  - 179 voci
- **PASS** landmarks.json
  - 657 voci
- **PASS** dem.npz
- **PASS** anni edifici (131817)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di 1167 (compaiono all'inizio): 4, d<=y: 0, ring<3: 0
- **PASS** hist (135580 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (128234 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 99, nel 1800 10117

## c) Densita' storica

- **PASS** Medieval city, band to 250 m nel 1500
  - 730 edifici vivi (38/ha, copertura 48%) contro 364 (19/ha, copertura 53%) nel 2026: rapporto 2.01
- **PASS** Medieval city, band to 250 m nel 1800
  - 426 edifici vivi (22/ha, copertura 34%) contro 364 (19/ha, copertura 53%) nel 2026: rapporto 1.17
- **PASS** Medieval city, band to 450 m nel 1500
  - 2381 edifici vivi (39/ha, copertura 47%) contro 814 (13/ha, copertura 67%) nel 2026: rapporto 2.93
- **PASS** Medieval city, band to 450 m nel 1800
  - 1654 edifici vivi (27/ha, copertura 42%) contro 814 (13/ha, copertura 67%) nel 2026: rapporto 2.03
- **PASS** Medieval city, band to 650 m nel 1500
  - 3698 edifici vivi (37/ha, copertura 43%) contro 1117 (11/ha, copertura 57%) nel 2026: rapporto 3.31
- **PASS** Medieval city, band to 650 m nel 1800
  - 2637 edifici vivi (26/ha, copertura 41%) contro 1117 (11/ha, copertura 57%) nel 2026: rapporto 2.36
- **PASS** Medieval city, band to 900 m nel 1800
  - 3067 edifici vivi (26/ha, copertura 39%) contro 1212 (10/ha, copertura 53%) nel 2026: rapporto 2.53
- **PASS** Medieval city, band to 1200 m nel 1800
  - 3263 edifici vivi (25/ha, copertura 37%) contro 1274 (10/ha, copertura 50%) nel 2026: rapporto 2.56
- **PASS** Medieval city, outer part (to 1620) nel 1800
  - 3520 edifici vivi (25/ha, copertura 37%) contro 1329 (9/ha, copertura 49%) nel 2026: rapporto 2.65
- **PASS** Ny-Kobenhavn (Christian IV extension: Rosenborg, Nyboder) nel 1800
  - 1440 edifici vivi (23/ha, copertura 25%) contro 567 (9/ha, copertura 28%) nel 2026: rapporto 2.54
- **PASS** Nyhavn quarter nel 1800
  - 561 edifici vivi (17/ha, copertura 23%) contro 242 (7/ha, copertura 27%) nel 2026: rapporto 2.32
- **PASS** Frederiksstaden nel 1800
  - 1638 edifici vivi (16/ha, copertura 26%) contro 680 (7/ha, copertura 27%) nel 2026: rapporto 2.41
- **PASS** Christianshavn nel 1800
  - 2185 edifici vivi (20/ha, copertura 20%) contro 854 (8/ha, copertura 22%) nel 2026: rapporto 2.56
- **PASS** Holmen naval base nel 1800
  - 1162 edifici vivi (11/ha, copertura 12%) contro 262 (2/ha, copertura 14%) nel 2026: rapporto 4.44

## d) Corridoi vuoti

- **WARN** centro storico molto grande: raster limitato a 10 km
- **PASS** 1267: nessun corridoio vuoto
  - corridoi_1267.png
- **WARN** 1800: 7 aree vuote allungate
  - #1 729x148 m a (55.66989,12.53704); #2 358x70 m a (55.66587,12.51429); #3 531x129 m a (55.66442,12.51919); #4 575x118 m a (55.66231,12.51113); #5 483x101 m a (55.66026,12.52168); #6 176x36 m a (55.66021,12.51155) — corridoi_1800.png
- **WARN** 1800: 1 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #8 709x67 m a (55.66091,12.51664)
- **WARN** 1900: 20 aree vuote allungate
  - #1 213x46 m a (55.66904,12.54328); #2 235x29 m a (55.66659,12.55568); #3 160x25 m a (55.66652,12.55488); #4 145x26 m a (55.66571,12.51827); #5 297x48 m a (55.66446,12.52060); #6 258x26 m a (55.66345,12.52136) — corridoi_1900.png
- **WARN** 1900: 5 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #21 846x56 m a (55.65789,12.54797); #22 738x87 m a (55.66113,12.51613); #23 623x46 m a (55.65420,12.54679); #24 295x30 m a (55.66384,12.51161); #25 264x44 m a (55.66822,12.54574)
- **WARN** 1950: 195 aree vuote allungate
  - #1 256x54 m a (55.66991,12.45977); #2 223x49 m a (55.66994,12.46426); #3 157x28 m a (55.67072,12.48281); #4 255x38 m a (55.66953,12.47624); #5 157x28 m a (55.67029,12.51304); #6 182x28 m a (55.66953,12.45735) — corridoi_1950.png

## e) Costo e schedule

- **PASS** costo dei cambi (10 s)
  - oggetti citta' 3415, cambi in tutto il video 121066, max in un fotogramma 1083 (~13 s), costo dei soli cambi ~0.40 h (budget 1.0 h)
- **PASS** drone: velocita' massima
  - 222 m/s (limite 250), mediana 8
- **PASS** drone: accelerazione massima
  - 121 m/s2 (limite 120), 99% 67
- **PASS** drone: jerk massimo
  - 80 m/s3 (limite 200), 99% 52
- **PASS** drone: distanza minima da terreno e tetti
  - 220 m (soglia 24); dal solo terreno 220 m
- **PASS** drone: discontinuita' (target 0, tagli dichiarati: 0)
  - 0 salti
- **PASS** drone: soste tolte per tempo
  - 0 tolte, 17 tenute, 0 solo sorvolate; hover 141 s, volo 491 s; 
- **PASS** drone: hover quasi fermo
  - v max in hover 8.1 m/s (soglia 12; esclusi 30% o 1,5 s a ogni estremo)
- **PASS** drone: voli con gli anni quasi fermi
  - nessun volo >= 12 s sotto 0,4 anni/s (fuori da apertura e finale)  [uniscili: trasforma una delle due soste vicine in cartello]
- **PASS** drone: monumenti visibili durante il loro hover
  - ogni monumento bersaglio ha il corpo costruito a meta' hover  [Confluences: il corpo compariva a fine hover]
- **PASS** drone: distanza della camera
  - mediana 1541 m equivalenti a 35 mm (obiettivo 32 mm); riferimenti: Copenaghen 1397, Parigi 1427, Madrid 2538, Lione 930 (giudicata troppo vicina); soglia 1200
- **PASS** drone: esattezza anni
  - soste: y0 e y1 esatti sulla finestra di hover; cartelli fuori hover esatti; cartelli durante un hover e voli: anni flessibili (il contatore scorre fra le voci)
- **PASS** drone: grafico del percorso
  - qa/drone_path.png
- **WARN** ritmo: nessun vuoto > 15 s senza stimolo nuovo
  - vuoto massimo 18.0 s (185-203 s); 2 oltre 15 s: 92-109, 185-203
- **PASS** ritmo: anni/s per minuto
  - 0:00 12.03 | 1:00  3.41 | 2:00  1.89 | 3:00  1.12 | 4:00  0.98 | 5:00  0.90 | 6:00  1.13 | 7:00  0.60 | 8:00  0.78 | 9:00  1.08 | 10:00  0.12
- **PASS** 17 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** soste e cartelli sugli anni della story (0,01)
- **PASS** evento forte entro 45 s
  - primo a 12.9 s
- **PASS** notte
  - night_t=645.0, schedule_copenhagen_night.json ok

## Immagini

![corridoi_1267.png](corridoi_1267.png)
![corridoi_1800.png](corridoi_1800.png)
![corridoi_1900.png](corridoi_1900.png)
![corridoi_1950.png](corridoi_1950.png)
