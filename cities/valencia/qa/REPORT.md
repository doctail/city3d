# QA valencia

Generato da `python -m kit.qa` il 2026-11-12 06:40. Esito complessivo: **FAIL**

| Sezione | Esito |
|---|---|
| c) Densita' storica | PASS |
| d) Corridoi vuoti | FAIL |

## c) Densita' storica

- **PASS** Muslim walled city nel 1238
  - 1788 edifici vivi (49/ha, copertura 61%) contro 960 (26/ha, copertura 76%) nel 2026: rapporto 1.86
- **PASS** Muslim walled city nel 1500
  - 1783 edifici vivi (49/ha, copertura 72%) contro 960 (26/ha, copertura 76%) nel 2026: rapporto 1.86
- **PASS** Muslim walled city nel 1800
  - 1620 edifici vivi (45/ha, copertura 75%) contro 960 (26/ha, copertura 76%) nel 2026: rapporto 1.69
- **PASS** Boatella quarter (inside 1356 wall) nel 1500
  - 1911 edifici vivi (47/ha, copertura 61%) contro 660 (16/ha, copertura 60%) nel 2026: rapporto 2.90
- **PASS** Boatella quarter (inside 1356 wall) nel 1800
  - 1911 edifici vivi (47/ha, copertura 61%) contro 660 (16/ha, copertura 60%) nel 2026: rapporto 2.90
- **PASS** Christian expansion within the 1356 wall nel 1500
  - 6938 edifici vivi (43/ha, copertura 57%) contro 3175 (20/ha, copertura 60%) nel 2026: rapporto 2.19
- **PASS** Christian expansion within the 1356 wall nel 1800
  - 6615 edifici vivi (41/ha, copertura 65%) contro 3175 (20/ha, copertura 60%) nel 2026: rapporto 2.08
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
  - #2 1488x307 m a (39.47318,-0.37379) — corridoi_1338.png
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
  - #8 662x35 m a (39.46451,-0.37216); #9 547x31 m a (39.46896,-0.37832); #10 546x23 m a (39.47604,-0.37123); #11 423x23 m a (39.48268,-0.38112); #12 405x21 m a (39.47618,-0.38964)
- **FAIL** 1950: 3 corridoi con forma di strada moderna (niente case, niente nastro)
  - #1 679x128 m a (39.48765,-0.38289); #2 135x18 m a (39.48805,-0.37223); #3 134x20 m a (39.48136,-0.38733) — corridoi_1950.png
- **WARN** 1950: 7 aree vuote allungate
  - #4 334x73 m a (39.48156,-0.37821); #5 401x81 m a (39.47743,-0.37095); #6 204x14 m a (39.47591,-0.38901); #7 406x85 m a (39.47448,-0.36766); #8 187x39 m a (39.47003,-0.33443); #9 122x21 m a (39.46896,-0.33766) — corridoi_1950.png

## Immagini

![corridoi_1238.png](corridoi_1238.png)
![corridoi_1338.png](corridoi_1338.png)
![corridoi_1800.png](corridoi_1800.png)
![corridoi_1900.png](corridoi_1900.png)
![corridoi_1950.png](corridoi_1950.png)
