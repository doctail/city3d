# MISSING — Seville (importato dal legacy da `python -m kit legacy sevilla`)

Campi richiesti dal formato kit che il legacy non poteva dare. Niente e' stato inventato: i campi sono `TODO`/vuoti/`conf: "low"` e sono elencati in `story._legacy_gaps`.

## Importato
- soste: 11 (con bersaglio risolto: 9, con fonte: 0)
- cartelli: 54 (con fonte: 0); minimo richiesto 45: OK
- monumenti: 21 (con fonte: 0); tutti `kind: TODO`
- fonti: 0 · popolazione: 0 punti · acqua: 0 · mura: 1 · ponti: 0 · zone: 0
- eventi: 1 · camera drone (pitch_max 30, alt_max 500, d_min 1400, drift_vmax 8, rho_max 1400, lens 32)

## Da compilare (storico)

### Fonti
- `sources` · sources: nessuna scheda di validazione per sevilla: 0 fonti; tutti gli elementi importati sono conf "low" (deroga regola 1) e vanno risalvati con una fonte reale

### Regimi/polities, ere, popolazione
- `city` · country: non nei file legacy (TODO)
- `city` · style_preset: default 'mediterranean' (il legacy ha lo stile in city_<slug>.json, non e' un preset): scegliere
- `city` · eras: nessuna periodizzazione nel legacy
- `city` · polities: nessun regime/chip bandiera nel legacy: ogni regime da compilare (regola R2)
- `city` · data_reliable_from: non nel legacy
- `city` · population: nessuna serie di popolazione nel legacy (la scheda non c'e'): HUD senza popolazione

### Zone, mura, acqua, ponti
- `history.walls[0]` · built/demolished/src: walls_1248.json: solo il tracciato; anni e fonte da compilare
- `history.bridges` · bridges: nessun bridges_sevilla.py leggibile (vedi anche bridges.json di radice, non per citta')
- `history.zones` · zones: nessuna zona pre-catasto con anello e anni di nascita nel legacy (le zone sono codice in hist_<slug>.py: nuclei/villaggi con parametri a mano): anelli, born, era_height da compilare
- `history` · walls/gutting/lost/fires: mura/sventramenti/edifici perduti/incendi sono generati da codice o da dati esterni (ALPAGE ecc.) nel legacy: non importabili in modo letterale

### Monumenti
- `landmarks` · kind: 21 monumenti con geometria bespoke in landmarks_sevilla.py: scegliere un preset di kit/landmarks_kit.py o tenere il modulo legacy; phases con solo il primo anno

### Soste (bersaglio, peso, fx)
- `regia.soste[3]` · target: 'The Maestranza bullring rises (1761-1785)': bersaglio legacy assente
- `regia.soste[4]` · target: 'Isabel II Bridge replaces the boat bridge (1845-1852)': bersaglio legacy assente
- `regia.soste` · target: 7 bersagli dedotti per vicinanza/nome approssimato (vedi _legacy_target di ogni sosta): verificare che il monumento sia quello giusto
- `regia.soste` · weight: 11 soste senza peso (0-10 o "max"): default = forza dell'fx; scegliere almeno la piu' forte come "max"
- `regia.soste` · fx: nessun fx del montaggio nel legacy (campo omesso)

### Cartelli e capitoli
- `montaggio.cards` · cards: 54 cartelli importati (da CAPS di regia); minimo 45 rispettato
- `montaggio.cards` · hold_s: 28 cartelli senza didascalia in eventi (hold_s 5 s di default, nessuna etichetta monumento)
- `montaggio.cards` · target/shot: il legacy non ha bersaglio per i cartelli (volano durante i tratti)
- `montaggio` · chapters: nessun capitolo storico nel legacy (capitoli_<slug>.txt e metadata sono per orari di video, non per anni): tracciare dalle ere

### Montaggio e consegna
- `montaggio` · open: solo il titolo base ('<CITY> TODAY'): aggiungere la popolazione di oggi con fonte
- `metadata` · chapters/description/tags: capitoli con orari (legacy: orari del vecchio render, non validi per il drone), descrizione, tag, commento fisso, Reddit: da rifare nel formato kit (cities/<slug>/METADATA.md)

### Pacchetto dati
- `data` · data_src: data_sevilla_src incompleto per kit data/pack: mancano roads.json, land.json, dem.npz

## Pacchetto dati per `kit pack`/`kit data`
- cartella: `data_sevilla_src`; presenti: buildings.json, dem_rel.npz, walls_1248.json, water_src.json
- INCOMPLETO, mancano: roads.json, land.json, dem.npz
