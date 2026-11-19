# MISSING — Paris (importato dal legacy da `python -m kit legacy parigi`)

Campi richiesti dal formato kit che il legacy non poteva dare. Niente e' stato inventato: i campi sono `TODO`/vuoti/`conf: "low"` e sono elencati in `story._legacy_gaps`.

## Importato
- soste: 10 (con bersaglio risolto: 10, con fonte: 10)
- cartelli: 92 (con fonte: 91); minimo richiesto 45: OK
- monumenti: 20 (con fonte: 14); tutti `kind: TODO`
- fonti: 139 · popolazione: 51 punti · acqua: 9 · mura: 0 · ponti: 0 · zone: 0
- eventi: 2 · camera drone (pitch_max 30, alt_max 500, d_min 1400, drift_vmax 8, rho_max 1400, lens 32)

## Da compilare (storico)

### Fonti
- `sources` · sources: 139 fonti dalla scheda (id citati nei commenti legacy); elementi senza id/fonte: 0 soste, 1 cartelli, 6 monumenti (conf low)

### Regimi/polities, ere, popolazione
- `city` · country: non nei file legacy (TODO)
- `city` · style_preset: default 'mediterranean' (il legacy ha lo stile in city_<slug>.json, non e' un preset): scegliere
- `city` · eras: nessuna periodizzazione nel legacy
- `city` · polities: nessun regime/chip bandiera nel legacy: ogni regime da compilare (regola R2)
- `city` · data_reliable_from: non nel legacy

### Zone, mura, acqua, ponti
- `history.water` · ring: 9 voci d'acqua come CERCHI attorno al punto di riferimento (WATER_KEYS): sostituire con i poligoni reali
- `history.bridges` · bridges: 36 ponti nel legacy (geometria da OSM, non letterale): pontneuf, pontnotredame, pontauchange, petitpontcardinallustiger, pontsaintmichel, pontmarie, pontdelatournelle, pontroyal, pontdesarts, pontdelaconcorde, pontalexandreiii, pontdebirhakeim, pontdiena, pontdelalma ... -> servono line [lat,lon], larghezza, anni, fonte
- `history.zones` · zones: nessuna zona pre-catasto con anello e anni di nascita nel legacy (le zone sono codice in hist_<slug>.py: nuclei/villaggi con parametri a mano): anelli, born, era_height da compilare
- `history` · walls/gutting/lost/fires: mura/sventramenti/edifici perduti/incendi sono generati da codice o da dati esterni (ALPAGE ecc.) nel legacy: non importabili in modo letterale

### Monumenti
- `landmarks` · kind: 20 monumenti con geometria bespoke in landmarks_parigi.py: scegliere un preset di kit/landmarks_kit.py o tenere il modulo legacy; phases con solo il primo anno

### Soste (bersaglio, peso, fx)
- `regia.soste[5]` · target: 'Canal Saint-Martin is dug (1822-1825)': nessun monumento entro 700 m: area attorno al punto di mira legacy
- `regia.soste` · target: 2 bersagli dedotti per vicinanza/nome approssimato (vedi _legacy_target di ogni sosta): verificare che il monumento sia quello giusto
- `regia.soste` · weight: 10 soste senza peso (0-10 o "max"): default = forza dell'fx; scegliere almeno la piu' forte come "max"
- `regia.soste` · fx: nessun fx del montaggio nel legacy (campo omesso)

### Cartelli e capitoli
- `montaggio.cards` · cards: 92 cartelli importati (da CAPS di regia); minimo 45 rispettato
- `montaggio.cards` · hold_s: 60 cartelli senza didascalia in eventi (hold_s 5 s di default, nessuna etichetta monumento)
- `montaggio.cards` · target/shot: il legacy non ha bersaglio per i cartelli (volano durante i tratti)
- `montaggio` · chapters: nessun capitolo storico nel legacy (capitoli_<slug>.txt e metadata sono per orari di video, non per anni): tracciare dalle ere

### Montaggio e consegna
- `montaggio` · open: solo il titolo base ('<CITY> TODAY'): aggiungere la popolazione di oggi con fonte
- `metadata` · chapters/description/tags: capitoli con orari (legacy: orari del vecchio render, non validi per il drone), descrizione, tag, commento fisso, Reddit: da rifare nel formato kit (cities/<slug>/METADATA.md)

## Pacchetto dati per `kit pack`/`kit data`
- cartella: `data_parigi_src`; presenti: buildings.json, dem.npz, far.json, hist.json, land.json, landmarks.json, landphases.json, parks.json, roads.json, urban_grid.npz, wall_p.json
- completo
