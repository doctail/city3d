# QA valencia

Generato da `python -m kit.qa` il 2026-11-12 06:44. Esito complessivo: **FAIL**

| Sezione | Esito |
|---|---|
| a) Story e fonti | WARN |
| b) DATA | PASS |
| c) Densita' storica | PASS |
| d) Corridoi vuoti | FAIL |
| e) Costo e schedule | PASS |
| f) Fotogrammi locali | PASS |

## a) Story e fonti

- **PASS** chiavi city
- **PASS** 45 fonti
- **PASS** date con fonte
- **WARN** date fuori dall'intervallo del video
  - history.water[3] Jardi del Turia 1: 99999; history.water[5] Jardi del Turia 2: 99999; history.water[7] Jardi del Turia 3: 99999; history.water[9] Jardi del Turia 4: 99999; history.water[11] Jardi del Turia 5: 99999; history.water[13] Jardi del Turia 6: 99999; history.water[15] 1957 flood (low centre, slab back): 99999

## b) DATA

- **PASS** cartella DATA
  - data_valencia
- **PASS** buildings.json
  - 38241 voci
- **PASS** roads.json
  - 13838 voci
- **PASS** hist.json
  - 17247 voci
- **PASS** land.json
  - 4 voci
- **PASS** landmarks.json
  - 1571 voci
- **PASS** dem.npz
- **PASS** anni edifici (38241)
  - senza anno 0, dopo 2026: 0, prima di 1238 (compaiono all'inizio): 0, d<=y: 0, ring<3: 0
- **PASS** hist (17247 predecessori)
  - senza y/d 0, d<y 0, nati dopo 2026: 0
- **PASS** anni strade (13838 nastri)
  - senza anno 0, dopo 2026: 0; visibili all'inizio 333, nel 1800 837

## c) Densita' storica

- **PASS** Muslim walled city nel 1238
  - 1788 edifici vivi (49/ha, copertura 61%) contro 968 (27/ha, copertura 76%) nel 2026: rapporto 1.85
- **PASS** Muslim walled city nel 1500
  - 1791 edifici vivi (49/ha, copertura 71%) contro 968 (27/ha, copertura 76%) nel 2026: rapporto 1.85
- **PASS** Muslim walled city nel 1800
  - 1628 edifici vivi (45/ha, copertura 75%) contro 968 (27/ha, copertura 76%) nel 2026: rapporto 1.68
- **PASS** Boatella quarter (inside 1356 wall) nel 1500
  - 1868 edifici vivi (46/ha, copertura 58%) contro 668 (17/ha, copertura 62%) nel 2026: rapporto 2.80
- **PASS** Boatella quarter (inside 1356 wall) nel 1800
  - 1868 edifici vivi (46/ha, copertura 58%) contro 668 (17/ha, copertura 62%) nel 2026: rapporto 2.80
- **PASS** Christian expansion within the 1356 wall nel 1500
  - 6903 edifici vivi (43/ha, copertura 56%) contro 3191 (20/ha, copertura 60%) nel 2026: rapporto 2.16
- **PASS** Christian expansion within the 1356 wall nel 1800
  - 6580 edifici vivi (41/ha, copertura 64%) contro 3191 (20/ha, copertura 60%) nel 2026: rapporto 2.06
- **PASS** Quart suburb (arrabal de Quart) nel 1800
  - 1737 edifici vivi (24/ha, copertura 35%) contro 725 (10/ha, copertura 37%) nel 2026: rapporto 2.40
- **PASS** Morvedre suburb (north of the Turia) nel 1800
  - 3470 edifici vivi (27/ha, copertura 35%) contro 1184 (9/ha, copertura 38%) nel 2026: rapporto 2.93
- **PASS** Russafa village nel 1800
  - 1863 edifici vivi (38/ha, copertura 59%) contro 906 (19/ha, copertura 62%) nel 2026: rapporto 2.06
- **PASS** El Grau (Vilanova del Grau) nel 1800
  - 227 edifici vivi (7/ha, copertura 7%) contro 35 (1/ha, copertura 9%) nel 2026: rapporto 6.49

## d) Corridoi vuoti

- **PASS** 1238: nessun corridoio vuoto
  - corridoi_1238.png
- **FAIL** 1338: 1 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 508x107 m a (39.47902,-0.39031) — corridoi_1338.png
- **WARN** 1338: 1 aree vuote allungate
  - #2 1487x311 m a (39.47318,-0.37379) — corridoi_1338.png
- **WARN** 1338: 1 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #3 293x46 m a (39.47177,-0.37351)
- **FAIL** 1800: 12 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 1381x297 m a (39.48536,-0.37963); #2 214x18 m a (39.48858,-0.37942); #3 134x20 m a (39.48136,-0.38733); #4 497x90 m a (39.47902,-0.39031); #5 888x179 m a (39.47560,-0.38896); #6 157x28 m a (39.47562,-0.39129) — corridoi_1800.png
- **WARN** 1800: 4 aree vuote allungate
  - #13 505x81 m a (39.48154,-0.37956); #14 218x47 m a (39.48078,-0.38205); #15 400x84 m a (39.47734,-0.37099); #16 354x79 m a (39.47461,-0.36780) — corridoi_1800.png
- **WARN** 1800: 1 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #17 255x23 m a (39.47484,-0.36990)
- **FAIL** 1900: 5 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 1185x265 m a (39.48536,-0.37977); #2 214x18 m a (39.48858,-0.37942); #3 134x20 m a (39.48136,-0.38733); #4 385x91 m a (39.47893,-0.39110); #5 592x142 m a (39.46829,-0.32793) — corridoi_1900.png
- **WARN** 1900: 2 aree vuote allungate
  - #6 401x81 m a (39.47743,-0.37095); #7 361x83 m a (39.47461,-0.36771) — corridoi_1900.png
- **WARN** 1900: 6 viali larghi gia' visibili (se aperti sventrando: gutting)
  - #8 662x35 m a (39.46451,-0.37216); #9 546x23 m a (39.47604,-0.37123); #10 529x36 m a (39.46904,-0.37832); #11 423x23 m a (39.48268,-0.38112); #12 405x21 m a (39.47618,-0.38964)
- **FAIL** 1950: 3 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 679x128 m a (39.48765,-0.38289); #2 135x18 m a (39.48805,-0.37223); #3 134x20 m a (39.48136,-0.38733) — corridoi_1950.png
- **WARN** 1950: 8 aree vuote allungate
  - #4 334x73 m a (39.48156,-0.37821); #5 401x81 m a (39.47743,-0.37095); #6 204x14 m a (39.47591,-0.38901); #7 406x85 m a (39.47448,-0.36766); #8 226x52 m a (39.47047,-0.37646); #9 187x39 m a (39.47003,-0.33443) — corridoi_1950.png

## e) Costo e schedule

- **PASS** costo dei cambi (3 s)
  - oggetti citta' 2182, cambi in tutto il video 82577, max in un fotogramma 601 (~7 s), costo dei soli cambi ~0.28 h (budget 1.0 h)
- **PASS** 26 soste ben formate
- **PASS** soste ordinate e non sovrapposte
- **PASS** didascalie "Titolo (data)"
- **PASS** evento forte entro 45 s
  - primo a 9.5 s
- **PASS** notte
  - night_t=460.5, schedule_valencia_night.json ok

## f) Fotogrammi locali

- **PASS** render locale: 8 fotogrammi in 214 s
  - cities/valencia/qa/render.log
- **PASS** foglio contatti
  - cities/valencia/qa/contact.jpg: guardalo prima del pod (strade come nastri chiari, centro pieno)

## Immagini

![corridoi_1238.png](corridoi_1238.png)
![corridoi_1338.png](corridoi_1338.png)
![corridoi_1800.png](corridoi_1800.png)
![corridoi_1900.png](corridoi_1900.png)
![corridoi_1950.png](corridoi_1950.png)
![contact.jpg](contact.jpg)
