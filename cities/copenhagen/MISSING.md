# MISSING — Copenhagen (importato dal legacy da `python -m kit legacy copenhagen`)

Campi richiesti dal formato kit che il legacy non poteva dare. Niente e' stato inventato: i campi sono `TODO`/vuoti/`conf: "low"` e sono elencati in `story._legacy_gaps`.

## Importato
- soste: 26 (con bersaglio risolto: 26, con fonte: 0)
- cartelli: 41 (con fonte: 0); minimo richiesto 45: MANCANO 4
- monumenti: 17 (con fonte: 0); tutti `kind: TODO`
- fonti: 0 · popolazione: 0 punti · acqua: 0 · mura: 0 · ponti: 0 · zone: 0
- eventi: 0 · camera drone (pitch_max 30, alt_max 500, d_min 1400, drift_vmax 8, rho_max 1400, lens 32)

## Da compilare (storico)

### Fonti
- `sources` · sources: nessuna scheda di validazione per copenhagen: 0 fonti; tutti gli elementi importati sono conf "low" (deroga regola 1) e vanno risalvati con una fonte reale

### Regimi/polities, ere, popolazione
- `city` · country: non nei file legacy (TODO)
- `city` · style_preset: default 'mediterranean' (il legacy ha lo stile in city_<slug>.json, non e' un preset): scegliere
- `city` · eras: nessuna periodizzazione nel legacy
- `city` · polities: nessun regime/chip bandiera nel legacy: ogni regime da compilare (regola R2)
- `city` · data_reliable_from: non nel legacy
- `city` · population: nessuna serie di popolazione nel legacy (la scheda non c'e'): HUD senza popolazione

### Zone, mura, acqua, ponti
- `history.bridges` · bridges: nessun bridges_copenhagen.py leggibile (vedi anche bridges.json di radice, non per citta')
- `history.zones` · zones: nessuna zona pre-catasto con anello e anni di nascita nel legacy (le zone sono codice in hist_<slug>.py: nuclei/villaggi con parametri a mano): anelli, born, era_height da compilare
- `history` · walls/gutting/lost/fires: mura/sventramenti/edifici perduti/incendi sono generati da codice o da dati esterni (ALPAGE ecc.) nel legacy: non importabili in modo letterale

### Monumenti
- `landmarks` · kind: 17 monumenti con geometria bespoke in landmarks_copenhagen.py: scegliere un preset di kit/landmarks_kit.py o tenere il modulo legacy; phases con solo il primo anno

### Soste (bersaglio, peso, fx)
- `regia.soste[6]` · target: 'GREAT FIRE OF 1728': punto FIRE_PTS 'fire1728' di regia_copenhagen.py
- `regia.soste[11]` · target: 'FIRE OF 1795': punto FIRE_PTS 'fire1795' di regia_copenhagen.py
- `regia.soste[12]` · target: 'BRITISH BOMBARDMENT (1807)': punto FIRE_PTS 'fire1807' di regia_copenhagen.py
- `regia.soste` · target: 13 bersagli dedotti per vicinanza/nome approssimato (vedi _legacy_target di ogni sosta): verificare che il monumento sia quello giusto
- `regia.soste` · weight: 26 soste senza peso (0-10 o "max"): default = forza dell'fx; scegliere almeno la piu' forte come "max"
- `regia.soste` · fx: nessun fx del montaggio nel legacy (campo omesso)

### Cartelli e capitoli
- `montaggio.cards` · cards_src: schede lette da montaggio/copenhagen_overlay.jsx (CARDS); anno = anno della curva schedule al t_in, `legacy_date` = data scritta nella scheda
- `montaggio.cards` · cards: 41 cartelli importati (da eventi_<slug>.json); SOTTO IL MINIMO di 45: ne mancano 4
- `montaggio.cards` · target/shot: il legacy non ha bersaglio per i cartelli (volano durante i tratti)
- `montaggio` · chapters: nessun capitolo storico nel legacy (capitoli_<slug>.txt e metadata sono per orari di video, non per anni): tracciare dalle ere

### Montaggio e consegna
- `montaggio` · open: solo il titolo base ('<CITY> TODAY'): aggiungere la popolazione di oggi con fonte
- `metadata` · chapters/description/tags: capitoli con orari (legacy: orari del vecchio render, non validi per il drone), descrizione, tag, commento fisso, Reddit: da rifare nel formato kit (cities/<slug>/METADATA.md)

### Pacchetto dati
- `data` · data_src: data_copenhagen_src incompleto per kit data/pack: mancano dem.npz

## Pacchetto dati per `kit pack`/`kit data`
- cartella: `data_copenhagen_src`; presenti: bridges.json, buildings.json, fires.json, land.json, landmarks.json, parks.json, reclaim.json, roads.json
- INCOMPLETO, mancano: dem.npz
