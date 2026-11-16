# QA marseille

Generato da `python -m kit.qa` il 2026-11-16 09:00. Esito complessivo: **FAIL**

| Sezione | Esito |
|---|---|
| a) Story e fonti | PASS |
| b) DATA | FAIL |
| c) Densita' storica | FAIL |
| d) Corridoi vuoti | FAIL |
| e) Costo e schedule | FAIL |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 30 fonti
- **PASS** date con fonte

## b) DATA

- **PASS** cartella DATA
  - data_marseille
- **PASS** buildings.json
  - 154128 voci
- **PASS** roads.json
  - 177736 voci
- **FAIL** hist.json mancante
  - lancia python -m kit build
- **PASS** land.json
  - 134 voci
- **PASS** landmarks.json
  - 0 voci
- **PASS** dem.npz
- **PASS** anni edifici (154128)
  - senza anno 0, anno 0 (segnaposto): 0, dopo 2026: 0, prima di -600 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** anni strade (177736 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 0, nel 1800 966

## c) Densita' storica

- **FAIL** Archaic Massalia (Saint-Laurent and Moulins hills) nel 1500
  - 3 edifici vivi (0/ha, copertura 0%) contro 842 (37/ha, copertura 49%) nel 2026: rapporto 0.00
- **FAIL** Archaic Massalia (Saint-Laurent and Moulins hills) nel 1800
  - 170 edifici vivi (7/ha, copertura 6%) contro 842 (37/ha, copertura 49%) nel 2026: rapporto 0.20
- **FAIL** Hellenistic Massalia (Saint-Laurent, Moulins and Carmes hills) nel 1500
  - 3 edifici vivi (0/ha, copertura 0%) contro 1189 (21/ha, copertura 46%) nel 2026: rapporto 0.00
- **FAIL** Hellenistic Massalia (Saint-Laurent, Moulins and Carmes hills) nel 1800
  - 196 edifici vivi (3/ha, copertura 3%) contro 1189 (21/ha, copertura 46%) nel 2026: rapporto 0.16
- **FAIL** Saint-Victor and the south shore nel 1500
  - 0 edifici vivi (0/ha, copertura 0%) contro 432 (12/ha, copertura 37%) nel 2026: rapporto 0.00
- **FAIL** Saint-Victor and the south shore nel 1800
  - 28 edifici vivi (1/ha, copertura 3%) contro 432 (12/ha, copertura 37%) nel 2026: rapporto 0.06
- **FAIL** Medieval Marseille (Ville haute and Ville basse) nel 1500
  - 3 edifici vivi (0/ha, copertura 0%) contro 1604 (18/ha, copertura 40%) nel 2026: rapporto 0.00
- **FAIL** Medieval Marseille (Ville haute and Ville basse) nel 1800
  - 232 edifici vivi (3/ha, copertura 2%) contro 1604 (18/ha, copertura 40%) nel 2026: rapporto 0.14
- **FAIL** Louis XIV extension (1666-1700) nel 1800
  - 218 edifici vivi (3/ha, copertura 5%) contro 2679 (33/ha, copertura 56%) nel 2026: rapporto 0.08

## d) Corridoi vuoti

- **PASS** -600: nessun corridoio vuoto
  - corridoi_-600.png
- **FAIL** -500: gutting non riempiti
  - Rue Imperiale (Rue de la Republique): 100% vuoto (case predecessore mancanti)
- **WARN** 1800: 3 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #1 474x50 m a (43.29717,5.36727); #2 316x19 m a (43.30022,5.36650); #3 220x25 m a (43.29353,5.37319)
- **FAIL** 1800: nastri stradali prima dell'apertura
  - Rue Imperiale (Rue de la Republique): 1856 m² di nastro visibile prima del 1864
- **FAIL** 1800: gutting non riempiti
  - Rue Imperiale (Rue de la Republique): 71% vuoto (case predecessore mancanti)
- **WARN** 1900: 6 aree vuote allungate
  - #1 133x16 m a (43.29860,5.37660); #2 207x25 m a (43.29820,5.38235); #3 219x34 m a (43.29597,5.38262); #4 329x18 m a (43.29603,5.37157); #5 179x39 m a (43.29518,5.37396); #6 281x57 m a (43.28991,5.36818) — corridoi_1900.png
- **WARN** 1900: 7 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #7 1471x136 m a (43.29720,5.37356); #8 564x87 m a (43.30393,5.36702); #9 541x36 m a (43.29000,5.36685); #10 429x65 m a (43.29147,5.36628); #11 300x21 m a (43.29943,5.36374)
- **WARN** 1950: 6 aree vuote allungate
  - #1 660x151 m a (43.30444,5.36399); #2 173x32 m a (43.30068,5.37512); #3 133x16 m a (43.29860,5.37660); #4 206x25 m a (43.29820,5.38235); #5 329x18 m a (43.29603,5.37157); #6 179x39 m a (43.29518,5.37396) — corridoi_1950.png

## e) Costo e schedule

- **FAIL** city_marseille.json mancante
  - python -m kit.city_json <slug>
- **FAIL** schedule_marseille.json mancante
  - lancia la regia (python -m kit build)

## Immagini

![corridoi_-600.png](corridoi_-600.png)
![corridoi_-500.png](corridoi_-500.png)
![corridoi_1800.png](corridoi_1800.png)
![corridoi_1900.png](corridoi_1900.png)
![corridoi_1950.png](corridoi_1950.png)
