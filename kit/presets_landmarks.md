# Catalogo dei preset di monumenti (`kit/landmarks_kit.py`)

Un monumento della story (`story.json` → `landmarks[]`) diventa parti 3D di `DATA/landmarks.json`:

```jsonc
{"name": "Cathedral", "kind": "cathedral", "at": [39.4757, -0.3752], "footprint": "auto",
 "params": {"nave_h": 26, "facade_towers": 0, "tower_ref": "Micalet"},
 "phases": [{"y": 1262, "y1": 1300}, {"y": 1350, "y1": 1380}, {"y": 1430, "y1": 1440, "groups": ["crossing"]}],
 "demolished": null, "label": true, "src": ["S9"], "conf": "high"}
```

Comandi (dalla radice del repo, Python con shapely: `/home/user/bl/bin/python`):

| Comando | Effetto |
|---|---|
| `python -m kit.landmarks_kit build <slug> [DATA]` | `DATA/landmarks.json` (parti dei preset + `DATA/landmarks_walls.json` di `kit/hist_kit.py` + `labels` + `clear`) e `montaggio/landmarks_<slug>.json` (`{nome: [x, y, h, anno]}` per `montaggio/labels_cam.py`). Idempotente. Il primo `landmarks.json` non scritto dal kit viene copiato in `DATA/landmarks_legacy.json`. |
| `python -m kit.landmarks_kit list` | elenco dei preset con alias |
| `python -m kit.tests.test_landmarks_kit` | test (forme valide, supporti prima delle parti sopra, fasi, demolizione, impronte, CLI idempotente) |
| `python -m kit.tests.landmarks_gallery [OUT] [--shots a,b]` | galleria di controllo: una scena con tutti i preset, 18 inquadrature 480x270 CPU in ~40 s → `kit/tests/gallery/*.jpg` |

## Campi comuni di un monumento

| Campo | Significato |
|---|---|
| `kind` | preset (tabella sotto; alias ammessi) |
| `at` | `[lat, lon]` del centro (oppure `xy: [x, y]` in metri locali) |
| `line` / `ring` | `[[lat, lon], …]` per mura e ponti (`line_xy` in metri locali) |
| `footprint` | `"auto"`: edificio di `DATA/buildings.json` che contiene `at` (o il più vicino entro 30 m, `params.fp_search`); orientamento dal rettangolo minimo (u = asse lungo, verso est); l'impronta va in `clear` e l'edificio del catasto sparisce. `params.fp_merge: m` unisce le particelle catastali adiacenti (entro `fp_radius`, 80 m). Oppure una lista `[[lat, lon], …]`. Senza impronta valgono le misure dei `params`. |
| `phases` | `[{y, y1?, groups?, d?}]`. Senza `groups` le fasi si dividono in ordine la sequenza di cantiere (fondazioni → corpo → tetto → guglia). Con `groups` prendono solo quei gruppi (es. `["spire"]` costruita secoli dopo). `d` in una fase con groups: quei gruppi spariscono (guglia crollata). Senza `y1` il cantiere dura 0,6 anni (le parti compaiono comunque in sequenza). |
| `demolished` | anno o `[y, y1]`: tutte le parti spariscono dall'alto verso il basso. Un monumento demolito non toglie edifici (`clear` vuoto) salvo `"clear": true`. |
| `clear` | `true/false` per forzare; default: sì, tranne mura, ponti e demoliti |
| `label`, `label_name`, `icon` | etichetta (`labels`: name, x, y, z = cima, from = primo anno, to = fine demolizione) |
| `params.ang`, `params.flip` | asse u in gradi da est (antiorario) / inverte l'asse (es. abside a ovest) |
| `params.scale` | scala le misure di default (non quelle dell'impronta) |
| `params.c`, `roof_c`, `dome_c` | colori: nome di palette o `#rrggbb` |

Palette (`PAL`): stone, stone2, limestone, sand, granite, brick, brick2, plaster, ochre, cream, white, calatrava, concrete,
tile, terracotta, slate, lead, copper, gold, bluetile, greentile, glass, glass2, steel, iron, dark, green, grass, arena, red, wood, water, seat.
Alfa: 0.05 pietra/rame senza finestre, 1 pareti con finestre, 0.5 vetro. Tetti/cupole di default da `city.style_preset`:
mediterranean (coppi, cupole di maiolica blu), nordic (rame), central (ardesia, piombo), atlantic.

## Preset

Gruppi = nomi utilizzabili in `phases[].groups`. Misure in metri.

| Preset (alias) | Forma | Parametri principali (default) | Gruppi |
|---|---|---|---|
| `tower_square` (`tower`) | zoccolo, fusto in 3 rocchi, cella campanaria finestrata, copertura | `w` 10 (o impronta), `h` 40, `roof` pyramid\|spire\|dome\|onion\|flat\|crenel\|lantern\|cage, `belfry` true, `c` brick | found, body, belfry, roof, spire, dome, lantern, merlons |
| `tower_round` | cilindro a rocchi | `rad` 6, `h` 30, `top` cone\|dome\|crenel\|flat\|lantern, `belfry` false, `seg` 16, `cone_k` 1.8 | found, body, belfry, roof |
| `lighthouse` | faro a fasce bianche/rosse, ballatoio, lanterna vetrata | `rad` 4.5, `h` 32, `c`, `band_c` | found, body, top |
| `bell_tower` (`campanile`) | campanile | `style` gothic (cornici, cella, guglia ottagonale + pinnacoli) \| baroque (piani rastremati, vasi, cupolino a cipolla) \| romanesque (piramide) \| flat (terrazza merlata + celletta in ferro, tipo Micalet); `plan` square\|octagon; `w`, `h` | found, body, belfry, roof, spire, dome, lantern, top, merlons |
| `cathedral` | croce latina, u → abside | `nave_h` 26, `aisle_h` 15, `nave_w` 0.4·W, `apse` true, `transept` true, `crossing` lantern\|dome\|spire\|none, `facade_towers` 0/1/2, `tower_h`, `tower_top`, `slices` 4, `tower_ref` (nome del campanile separato: la sua area esce dall'impronta, raggio `tower_cut_r` 9) | found, apse, transept, nave, roof, crossing, facade, towers, spire |
| `church` | navata unica + una torre in facciata (cattedrale ridotta) | come cathedral; default l 45, w 18, nave_h 16, tower_h 30 | come cathedral |
| `church_dome` (`central_church`) | pianta centrale: croce greca con timpani e cappelle d'angolo, tamburo finestrato, cupola, lanterna, palla d'oro | `plan` cross\|octagon\|round, `size` 40, `base_h` 16, `drum_r`, `drum_h`, `dome_hz`, `dome_c` | found, body, roof, drum, dome, lantern |
| `gate_towers` (`gate`) | porta a due torri + corpo con arco, merli. u = direzione delle mura, +v = fuori città | `tower_plan` polygon (esagoni tipo Serranos)\|D (semicircolari tipo Quart)\|round\|square, `tower_r` 8, `h` 30, `body_h` h−4, `gap` 14, `depth` 16, `arch_w` 6, `arch_h` 11, `merlons` true | found, towers, body, top, merlons |
| `wall_segment` (`walls`) | cortina a tratti lungo la linea (costruzione progressiva), parapetto, torri | `line`, `h` 10, `w` 3.5, `towers_every_m` 45, `tower` square\|round, `tower_w` 8, `tower_h` h+5, `tower_top` crenel\|pyramid\|flat, `chunk_m` 40 | wall, towers, merlons |
| `bridge_arches` (`bridge`) | spalle, pile con rostri dal fondo (z −2), archi a conci, impalcato, parapetti | `line`, `w` 12, `deck_z` 9, `n` (lunghezza/`span_m` 22), `pier_w` 4, `rise`, `voussoirs` 7, `z_water` −2 | piers, arches, deck |
| `palace_courtyard` (`palace`) | quattro ali a corte con tetti a padiglione, portale, fontana | `l` 70, `w` 50 (o impronta), `wing_w` 14, `h` 16, `corner_towers` false, `tower_top`, `fountain` true | found, body, roof, portal, towers, court |
| `hall_market` (`market`) | corpo finestrato, falde vetrate in serie, cupola centrale con lanterna, cupolette d'angolo | `l` 90, `w` 60, `h` 11, `n_vaults` 5, `dome_k` 0.16, `domes` true | found, body, roof, dome, domes |
| `station` (`train_station`) | facciata con padiglione centrale e torrette con cupolini; tettoia a botte vetrata | `l` 110 (fronte), `w` 120 (profondità), `facade_d` 16, `h` 17, `accent_c` brick, `shed` true | found, body, towers, shed, roof |
| `bullring` (`arena`, `amphitheatre`) | anello ad arcate, 3 gradoni, barriera rossa, ruedo | `r_out` 52 o `plan` ellipse con `a_out`/`b_out`, `h` 17, `arena_k` 0.5, `tiers` 3, `n` 32; `style` roman (anfiteatro alto 48 m in pietra) | found, ring, tiers, barrier |
| `stadium` | tribune inclinate a settori (wedge radiali), anello, pensilina, campo | `a_out` 115, `b_out` 88, `h` 26, `a_field`, `b_field`, `seat_c`, `roof` true, `roof_d` | found, stands, ring, roof |
| `skyscraper` (`tower_glass`) | basamento, fusto di vetro a tronchi con arretramenti, coronamento | `l`/`w` 32 (o impronta), `h` 150, `podium_h` 12, `setbacks` [[0.72, 0.82]], `plan` rect\|round, `crown` flat\|spire\|mast\|pyramid | podium, shaft, crown |
| `modern_shell` (`calatrava`) | architettura organica bianca: `shape` eye (Hemisfèric: lente vetrata con costole e pupilla su vasca) \| ribs (Museu de les Ciències) \| helmet (Palau de les Arts: lente + lama) \| arches (Umbracle) \| dome | `l`, `w`, `h`, `ribs`, `ang` | found, shell, ribs, body, blade, dome |
| `park_structure` (`park`) | arredo: `kind` kiosk \| greenhouse \| fountain \| obelisk \| statue \| wheel (ruota panoramica) \| pagoda \| pergola | `r`, `h`, `l`, `w`, `c` | found, body, roof, legs, rim, cabins |
| `generic_footprint` (`footprint`, `building`) | estrusione dell'impronta (catasto o l×w) | `h` (default: altezza del catasto), `roof` flat\|parapet\|gable\|hip\|dome, `roof_h`, `c` plaster, `a` 1 | found, body, roof |
| `castle` | recinto merlato, torri tonde d'angolo, mastio | `l` 60, `w` 50, `h` 11, `keep_h`, `keep_top`, `cones` | found, walls, towers, keep, merlons |

## Note di modellazione
- Le parti sono primitive di `build_render.py` (`_lmesh`): `prism` non ha buchi (anelli e cortili sono fatti a settori/ali),
  i tetti a due falde sono due `wedge` (timpani chiusi), le piramidi su pianta quadrata sono `hip` (allineate al riferimento),
  i coni a 4/8 lati sono allineati agli assi del mondo (per questo torri ottagonali e guglie usano poligoni non ruotati).
- Ogni parte ha `name` = nome del monumento (la regia trova le parti con `startswith`).
- Costo: con `merge_parts: true` nel city json le parti con lo stesso anno si fondono; i preset con merli/settori
  (castle, gate, bullring, stadium) hanno 80–150 parti, gli altri 5–60.
- La galleria (`kit/tests/gallery/`) è il riferimento visivo: rigenerarla dopo ogni modifica ai preset.
