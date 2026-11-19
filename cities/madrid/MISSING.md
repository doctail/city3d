# MISSING — Madrid (importato dal legacy da `python -m kit legacy madrid`)

Campi richiesti dal formato kit che il legacy non poteva dare. Niente e' stato inventato: i campi sono `TODO`/vuoti/`conf: "low"` e sono elencati in `story._legacy_gaps`.

## Importato
- soste: 0 (con bersaglio risolto: 0, con fonte: 0)
- cartelli: 11 (con fonte: 0); minimo richiesto 45: MANCANO 34
- monumenti: 0 (con fonte: 0); tutti `kind: TODO`
- fonti: 0 · popolazione: 0 punti · acqua: 0 · mura: 0 · ponti: 0 · zone: 0
- eventi: 0 · camera drone (pitch_max 30, alt_max 500, d_min 1400, drift_vmax 8, rho_max 1400, lens 32)

## Da compilare (storico)

### Fonti
- `sources` · sources: nessuna scheda di validazione per madrid: 0 fonti; tutti gli elementi importati sono conf "low" (deroga regola 1) e vanno risalvati con una fonte reale

### Regimi/polities, ere, popolazione
- `city` · country: non nei file legacy (TODO)
- `city` · style_preset: default 'mediterranean' (il legacy ha lo stile in city_<slug>.json, non e' un preset): scegliere
- `city` · eras: nessuna periodizzazione nel legacy
- `city` · polities: nessun regime/chip bandiera nel legacy: ogni regime da compilare (regola R2)
- `city` · data_reliable_from: non nel legacy
- `city` · population: nessuna serie di popolazione nel legacy (la scheda non c'e'): HUD senza popolazione

### Zone, mura, acqua, ponti
- `history.bridges` · bridges: nessun bridges_madrid.py leggibile (vedi anche bridges.json di radice, non per citta')
- `history.zones` · zones: nessuna zona pre-catasto con anello e anni di nascita nel legacy (le zone sono codice in hist_<slug>.py: nuclei/villaggi con parametri a mano): anelli, born, era_height da compilare
- `history` · walls/gutting/lost/fires: mura/sventramenti/edifici perduti/incendi sono generati da codice o da dati esterni (ALPAGE ecc.) nel legacy: non importabili in modo letterale

### Monumenti
- `landmarks` · landmarks: montaggio/landmarks_madrid.json e data_madrid_src/landmarks.json[labels] assenti

### Soste (bersaglio, peso, fx)
- `regia` · soste: nessuna sosta nello schedule legacy
- `regia.soste` · weight: 0 soste senza peso (0-10 o "max"): default = forza dell'fx; scegliere almeno la piu' forte come "max"
- `regia.soste` · fx: nessun fx del montaggio nel legacy (campo omesso)

### Cartelli e capitoli
- `montaggio.cards` · cards_src: 11 cartelli SOLO titolo+anno dai capitoli di metadata_madrid.md (nessun testo, nessuna fonte): sono capitoli di video, non schede storiche; da riscrivere dallo storico
- `montaggio.cards` · cards: 11 cartelli importati (da eventi_<slug>.json); SOTTO IL MINIMO di 45: ne mancano 34
- `montaggio.cards` · hold_s: 11 cartelli senza didascalia in eventi (hold_s 5 s di default, nessuna etichetta monumento)
- `montaggio.cards` · target/shot: il legacy non ha bersaglio per i cartelli (volano durante i tratti)
- `montaggio` · chapters: nessun capitolo storico nel legacy (capitoli_<slug>.txt e metadata sono per orari di video, non per anni): tracciare dalle ere

### Montaggio e consegna
- `montaggio` · open: solo il titolo base ('<CITY> TODAY'): aggiungere la popolazione di oggi con fonte
- `metadata` · chapters/description/tags: capitoli con orari (legacy: orari del vecchio render, non validi per il drone), descrizione, tag, commento fisso, Reddit: da rifare nel formato kit (cities/<slug>/METADATA.md)

### Pacchetto dati
- `data` · data_src: data_madrid_src incompleto per kit data/pack: mancano roads.json, dem.npz

### Altro
- `regia` · SOSTE/CAPS: regia_madrid.py assente o non analizzabile: soste da schedule, cartelli da eventi

## Pacchetto dati per `kit pack`/`kit data`
- cartella: `data_madrid_src`; presenti: buildings.json, land.json, parks.json
- INCOMPLETO, mancano: roads.json, dem.npz

## GAP PRINCIPALE: nessuna sosta (nessun monumento nei file legacy)
Madrid legacy ha solo hist, metadata, schedule, city, overlay: niente regia/landmarks, quindi 0 soste e 0 monumenti. I 11 "cartelli" importati sono SOLO titolo+anno dai capitoli di video di metadata_madrid.md (conf low, senza testo).
Candidati monumenti proposti (conf **low**, nessun anno/fonte/posizione verificati: serve lo storico; Palacio Real non ha impronta entro 40 m nei dati, edifici pre-1850 solo 54 (<1850) / 173 (<=1850), quindi i monumenti vanno modellati con preset, non presi dai dati):
Palacio Real · Puerta del Sol · Plaza Mayor · Cibeles · Museo del Prado · Retiro · Gran Via · Congreso de los Diputados · Cuatro Torres · Almudena · Atocha · Edificio Metropolis (Metropolitan) · Puentes del Manzanares (Segovia/Toledo) · Alcazar (demolito, hist_madrid ALCAZAR) · Puerta de Alcala · Casa de Campo · Torre de Madrid / Edificio Espana · Estacion de Atocha · Basilica di San Francisco el Grande · Teatro Real
