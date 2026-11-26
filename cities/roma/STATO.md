# Roma, inventario (26/11/2026, yb-scout). Roma e' pipeline PRE-KIT (2 nov 2026): nessun cities/roma/, nessun story.json, nessun `kit build/qa`.

## C'e'
- Config/script legacy in root: city_roma.json, data_roma.sh (pod CPU: OSM Geofabrik + ISTAT 2011 + DEM), prep_roma.py (anni = estrazione casuale per sezione ISTAT 2011 E8-E16, "pre-1919" per zona storica), hist_roma.py (mura Serviane/Aureliane, zone, citta' antica procedurale), landmarks_roma.py, regia_roma.py (schedule_roma.json, ~272 s, camera "cuts" stile Latos, niente drone), eventi_roma.py, labs_roma.py, sfx_roma.py, roma_overlay.jsx, monta_roma*.bat.
- Dati: data_roma_src/ (11 MB: buildings, roads, land, parks, dem, landmarks) + prove prova_regia.jpg, prova_v2.jpg.
- Packaging: metadata_roma.md (titolo A/B, descrizione, capitoli), traduzioni_roma.md, copertina_roma_A/B.jpg (in data_roma_src).
- Atlante: ISTAT 2011 sezioni scaricabile [Certain]; ISTAT 2021 solo E3, nessuna epoca (italia_francia.md). Voto dati Italia = C.
- Saturazione: CityEons "Rome" 1,26M views [Certain, da PRODUZIONE_TIMELAPSE/TABELLA] = domanda provata, ma concorrente fortissimo.

## Manca (per GO pod secondo il kit)
1. Dato per edificio: NON esiste (anno stimato per sezione, casuale). Gate 1 per-building non soddisfatto: va dichiarato come metodo storico (come Roma/Latos) o integrato (OSM start_date, Catasto storico). Decisione gia' presa dal proprietario: si procede.
2. cities/roma/story.json (STORY_SCHEMA.md): fonti, zone, mura, gutting, acqua/Tevere, monumenti, ~45 schede, 25 soste, capitoli, polities. Oggi la storia vive in script Python.
3. Camera drone + regia nuova (regola 26/11): regia_roma.py e' "cuts"; serve `kit regia_check` (tempo morto >10 s, camera ferma con anno che avanza), QA di regia, primi 20 s sulla citta' non sul mare.
4. `python -m kit build roma` + `kit qa roma --render` mai eseguiti: distanza camera mediana >=1.200 m (35 mm), inclinazione <45 gradi, 0 edifici all'anno 0 / sull'acqua (Tevere), monumenti visibili durante l'hover; foglio di 5-6 fotogrammi veri per epoca per il proprietario.
5. Colori nuovi (palette/colour_kit, come Pittsburgh): Roma e' del vecchio look.
6. Packaging check 168 px (gate 2) con copertine rifatte. montaggio/years_roma.json ha 6528 fotogrammi (= 272 s x 24) con anni variabili: un render vecchio stile sembra esistere [Likely], ma e' del look/camera vecchi e va rifatto; video non verificato.
7. Consegna: capitoli con orari finali, tag, commento fissato EN+IT, Reddit, distribuzione, nota stampa, comando cmd di montaggio, light version spezzata. Versione LIGHT dopo il render.
8. GO_POD.md (controllo GPU, git pull, lancio, avanzamento, spegnimento, costo con base misurata) su main.

## Prossimo passo unico
yb-historian: portare Roma nel kit (cities/roma/story.json da hist_roma/regia_roma/landmarks_roma/metadata_roma + city json), poi `kit build roma` e `kit qa roma --render`.
