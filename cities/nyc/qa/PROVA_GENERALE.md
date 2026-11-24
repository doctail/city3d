# NYC prova generale (24/11/2026, clone pulito di origin/main 9636c44, branch yb/nyc-rehearsal)
Clone nuovo `/home/user/city3d-rehearsal`, nessun symlink. Render CPU 8 spp 1920x1080 (niente GPU qui). Script: `qa/prova_generale_years.py`, `qa/rehearsal/cmp.py`.

## 1. GO_POD sul clone (tutto tranne il render): PASS con 2 note
- `merge-base --is-ancestor 77d9576 HEAD` OK. `git diff --quiet 77d9576 HEAD -- <file di render>` OK (HEAD cambia solo GO_POD.md). Tutti i path del diff-check esistono.
- Dati come run.sh (gunzip data_nyc_src -> `kit.hist_kit build nyc` -> `restore_after_build.sh`): 5 min 26 s su questa CPU (il GO dice 2 min 9 s solo per hist). md5 di hist, landphases, landmarks, roads, bridges, fires, floods, dem, buildings = IDENTICI a quelli di /home/user/city3d/data_nyc (rebuild di oggi): pipeline riproducibile.
- Banner: `fotogrammi 13305, notte dal fotogramma 12946` OK; schedule 554 s lens 32.0 OK; `[restore] landphases 1227 pier entries 331 dem D max 202 m` OK; `changed 1799 delayed 1773 dropped 26` OK; `[build] navi: 83 istanze, 0 scartate (terra) []` OK.
- DISCREPANZA 1: `[hist_kit] edifici vivi` reale = `1609: 0, 1500: 0, 1800: 12189, 1900: 291472`; il GO dice `1800: 12043, 1900: 291454` (numeri vecchi, pre-riva graduale). Chi confronta il banner a mano vedra' una differenza: correggere il GO.
- DISCREPANZA 2 (lieve): "13306" e' il n. di chiavi camera/overlay, il render fa 13305 (GO lo spiega). 13310 compare solo ricostruendo la regia, che il pod NON fa.
- Non verificabili qui: `uso: OPTIX`, nvidia-smi/cuInit, apt/pip.

## 2. Schedule: FAIL?  No: PASS (il pod usa la COMMITTATA, non rigenera)
- run.sh non chiama mai regia_kit/kit build: usa `schedule_nyc.json`, `city_nyc.json` committati; dati = data_nyc_src + hist_kit + restore. Rigenerare e' solo locale.
- La schedule committata e' quella del 20/11 (60af1f0) con solo 377 chiavi camera cambiate (0-376): years, soste, cards identici [Certain, confronto json].
- Coerenza con i dati attuali: anno monotono dopo il rewind (max 30 anni/s, nessun salto), 15 hover: ogni monumento citato esiste ai suoi anni di hover (Fort Amsterdam 1625,6 <= 1626,9; muro 1653,2; Trinity 1697,3 <= 1698,3; Fraunces 1718,6; St Paul 1764; Federal Hall 1699; Castle Clinton 1808-1811; Empire 1930,3; Twin 1968,4/1969,2 <= 1971; One WTC 2006,7 <= 2014,7). Nessun hover su monumento non nato. Fill graduali (1690-1830) e water_fix sono solo dati, non cambiano gli anni.

## 3. Pixel vs approvati (1920x1080, 8 spp, CPU)
| frame | riferimento | diff media | % pixel diff>8 |
|---|---|---|---|
| f1 pod (schedule vera, `--only 1`) | qa/cam/0001.jpg | 4,78 | 20,5 |
| riva est 1750 | qa/shore/after_east_1750.jpg | 0,41 | 0,09 |
| porto 1850 | qa/water/dopo/port1850.jpg | 5,05 | 22,5 |
| 2014 (cams_full f2014) | qa/fix/frames_full/f2014.jpg | 16,97 | 60,8 |
- Riva 1750: quasi identico, la pipeline e' deterministica e coincide col fotogramma approvato.
- Porto 1850: stessa scena; differiscono la posizione delle navi (dipende dal numero di fotogramma nello schedule di prova) e riferimento del 20/11 pre-modifiche: spiegato, non un difetto.
- 2014: il riferimento e' vecchio (pre acqua scura/alberi 1/3/navi): non e' un'approvazione valida.
- **f1: DISCREPANZA REALE.** Camera e geometria identiche, ma l'illuminazione e' diversa (mio render: sole basso, ombra lunga della torre sull'acqua; qa/cam/0001.jpg: luce piu' alta/diffusa). Un render con schedule corta custom e il render con schedule vera sono identici tra loro (diff 0,00): quindi il pod produrra' l'aspetto di `qa/rehearsal/f1_pod.jpg`, NON quello di `qa/cam/0001.jpg`. Config (city_nyc.json, build_render.py) identica in city3d-cam: l'agente camera deve dire con quali opzioni ha reso i suoi frame. Va deciso (e fatto vedere al proprietario) quale aspetto vale prima del GO.

## 4. Controllo 1609-2026 (`qa/prova_generale_years.json`, 1 anno fino al 1950, poi 5): FAIL
- Edifici con baricentro in acqua: NON 0. 1609-1687: 0; 1688-1904: 1-61 (max 61 nel 1904, di cui >30 m dalla terra: 50); 1905-1911: 173-180 (119 sono `hist` ritardati a YMAX=1905 da water_fix per costruzione, GO: "restano a 1905 come prima"); 1912-1950: 59-119; 1955-2026: <=59 (tutti <30 m dalla riva). La maggior parte sono edifici attuali su Governors Island (-2500,-7500 / -3000,-8000, 27+11 nel 1904) e hist su Brooklyn/Governors; non sono moli storici. Il GO dice "0 edifici in acqua 1609-1900": e' vero solo con criterio footprint<50% e fino al 1900 sui predecessori; col baricentro no.
- Salti di terra (sym. diff.) sulle rive di Manhattan > 60.000 m2/anno: 1811 100.658 (40 fasi), 1850 1.800.302 (254 fasi moli/slips a comparsa simultanea, nota e accettata), 1906 105.174, 1912 443.045 (Governors fill), 1975 306.432 (5 anni: 61.000/anno, al limite). Il fill graduale 1690-1830 sta sotto: max 43.076 (1690), 32-38 mila nel 1800-1801.
- Lembi staccati < 0,05 km2: costanti per anni e quasi tutti slivers da 0-65 m2 (residui del taglio delle fasi: 1609-1829/1905/1911, lungo Pearl/Water St e baia), un lembo vero da 13.307 m2 a (-4511,-6497) (isola, Ellis [Likely]); 8 lembi lontani (Bronx/Queens, 761-23.793 m2) fissi 1609-2026. Nessun lembo nuovo che compare/sparisce fuori da moli o fill noti. Slivers sotto 1 pixel: non visibili.

## Giudizio GO_POD
Usabile con correzioni: (a) banner `edifici vivi` (12189/291472); (b) decidere/spiegare l'aspetto f1 (luce) prima del GO; (c) togliere o precisare "0 edifici in acqua" (misura baricentro: 61 fino al 1904, ~180 nel 1905-11); (d) 1850 = 1,8 km2 di moli in un anno (nota, accettato il 20/11).
