# Kit Year Built

Una città = `cities/<slug>/story.json` (schema: `kit/STORY_SCHEMA.md`). Tutto il resto lo genera il kit.
Python: quello con shapely/numpy/scipy/PIL (`/home/user/bl/bin/python`, sul pod `/workspace/bl/bin/python`); `bpy` serve solo a `qa --render`.

```bash
PY=/home/user/bl/bin/python
$PY -m kit init valencia          # cities/valencia/story.json dal modello (non sovrascrive)
$PY -m kit data valencia          # controlla DATA, dice quale script di acquisizione usare
$PY -m kit build valencia         # hist -> landmarks -> city_valencia.json -> regia -> eventi/labs
$PY -m kit qa valencia --render   # controlli + fotogrammi locali -> cities/valencia/qa/REPORT.md, contact.jpg
$PY -m kit pack valencia          # DATA -> data_valencia_src/*.gz (da committare)
$PY -m kit montaggio valencia --A waking.mp3 --B monument.mp3 [--overlay]
$PY -m kit all valencia           # data, build, qa, pack
```
Ogni passo stampa tempo ed esito; il comando si ferma al primo FAIL (uscita 1). Opzione comune: `--data DIR` (altrimenti `city.data_dir` della story o `data_<slug>`).

## Passi e file
| Passo | Modulo | Scrive |
|---|---|---|
| data | `kit/cli.py` (stub) | niente: per `data_source` indica `fetch_es.py` (catastro), `fetch_dk.py`+`fetch_dk_roads.py` (bbr), `fetch_nl.py` (bag), `osm_dk_raw.py` (osm). Se DATA manca ma c'è `data_<slug>_src/`, la scompatta |
| build 1 | `kit/hist_kit.py` | `hist_<slug>.py` (stub per build_render/run.sh), `DATA/hist.json`, `landphases.json`, `fires.json`, `bridges.json`, strade dei gutting in `roads.json` |
| build 2 | `kit/landmarks_kit.py` | `DATA/landmarks.json`, `montaggio/landmarks_<slug>.json` |
| build 3 | `kit/city_json.py` + `kit/presets.py` | `city_<slug>.json` completo (nessun default NYC), marcato `_generated_by` |
| build 4 | `kit/regia_kit.py` | `schedule_<slug>.json`, `schedule_<slug>_night.json`, `cities/<slug>/regia.txt/png` |
| build 5 | `kit/eventi_kit.py`, `kit/labs_kit.py` (se presenti) | `montaggio/eventi_<slug>.json`, `labs_<slug>.json` |
| qa | `kit/qa.py` | `cities/<slug>/qa/REPORT.md`, `corridoi_<anno>.png`, `contact.jpg`, `frames/`, `render.log` |
| pack | `kit/cli.py` | `data_<slug>_src/*.json.gz` (escluso ciò che il pod rigenera: hist, urban_kit, landmarks_walls, *_stats, raw) |
| montaggio | `montaggio/kit_city.py`, `sfx_kit.py`, `ov_kit.sh` | file in `montaggio/public`, `out/<slug>_audio.m4a`, overlay |

Sul pod: `CITY=<slug> bash run.sh preview|full|...`. Per una città con `cities/<slug>/story.json` run.sh scompatta `data_<slug>_src`, crea lo stub `hist_<slug>.py` e il city json se mancano, poi lancia `hist_<slug>.py DATA` come per le altre città.

## city json (`kit/city_json.py`)
Preset `style_preset`: `mediterranean` (Roma + calce di Siviglia), `nordic` (Copenaghen), `central` (Parigi in resa Standard), `atlantic` (Siviglia/Porto). Tutti: `view_transform Standard`, `look None` (resa satura di Roma/Copenaghen), stile con tutte le chiavi lette da build_render. Sempre scritte: `lat0, lon0, radius_m, hist, story, core_box (±radius), forest_box [0,0,1,1], grid_deg 0, parks [], roads [], outer` neutro, `bin/dbin` (4/8; 6/16 oltre 900 anni; 10/50 oltre 1500), `cover` (obliqua da sud sul centro delle zone, anni inizio/fine, notte sull'ultimo se `regia.night`), `shorts` (regia propria se esiste `schedule_<slug>_shortA.json`, altrimenti il lungo accelerato a ~30 s).
Override nella story: `city.style` (si fonde sullo stile), `city.city_overrides` (chiavi top-level), `city.cover`, `city.shorts`. Validazione: `python -m kit.city_json <slug> --check-only`. Non sovrascrive un city json scritto a mano (senza `_generated_by`) salvo `--force`.

## Controlli (`kit/qa.py`)
- **a** story: chiavi city, preset, fonti; ogni data in `history.*` e `landmarks` con `src` esistente salvo `conf: "low"` (FAIL); soste senza fonte né bersaglio con fonte (WARN); coordinate oltre 1,5×radius (lat/lon invertiti: FAIL).
- **b** DATA: `buildings`, `roads` (obbligatorio), `hist`, `landmarks` (FAIL se mancano), `land`, `dem` (WARN); anni mancanti/futuri, `d<y`.
- **c** densità: per ogni zona, all'anno di partenza, 1500 e 1800 (se ≥ `born[1]`): edifici vivi e copertura contro il 2026. PASS se rapporto ≥ 0,6 e copertura ≥ 25 %; FAIL sotto 0,3 o 12 %.
- **d** corridoi: raster 4 m del centro (zone) negli anni start, +100, 1800, 1900, 1950. Vuoto = terra non coperta da edifici vivi, nastri visibili o parchi; si tolgono i vicoli < ~12 m; componenti lunghe ≥ 120 m e allungate (L/W ≥ 4): ROSSO/FAIL se ≥ 30 % è una strada futura (forma di strada moderna), GIALLO/WARN altrimenti. FAIL anche per nastri visibili in un `gutting` prima di `until` e gutting vuoti > 35 %. BLU/WARN: viali larghi già visibili fino al 1900 (se aperti sventrando, dichiarare un gutting). PNG `qa/corridoi_<anno>.png`.
- **e** `tools/costo_cambi.py` (FAIL oltre budget) e schedule: years ordinati e fino all'anno di partenza, camera, soste ben formate/ordinate/non sovrapposte, didascalie `Titolo (data)`, anni della sosta coerenti con la regia (WARN), primo evento forte (sosta, incendio, evento non sobrio) entro 45 s (WARN), notte.
- **f** `--render`: una sola costruzione della scena. Il kit scrive `qa/schedule_qa.json` con un blocco fermo di 16 fotogrammi per inquadratura (anno costante: edifici cresciuti; chiave camera esatta sul fotogramma centrale) e lancia `build_render.py --frames 1 N --only <centrali> --res 480 270 --samples 4 --denoiser none --device CPU`. Inquadrature: dall'alto del centro in start, +100, 1800, 1900, fine (max 5) + metà delle 3 soste più lunghe (camera interpolata linearmente tra le chiavi dello schedule). Foglio contatti `qa/contact.jpg`. Python con bpy: `KIT_BPY` o `/home/user/bl/bin/python`.

Opzioni di prova: `--story PATH --city JSON --schedule JSON --only abcde`.

## Test
```bash
/home/user/bl/bin/python -m unittest kit.tests.test_qa -v
```
Mini città sintetica: fonti, densità con/senza predecessori, viale moderno vuoto (FAIL) e riempito (PASS), nastro prima del gutting, roads obbligatorio, schedule/didascalie/45 s, city json completo, `costo_cambi` che legge `bin`.

## Correzioni fatte al codice esistente (11 nov 2026)
- `tools/costo_cambi.py`: `bin` letto dal city json (prima 4 fisso: per Roma, bin 10, contava troppi oggetti).
- `build_render.py`: `sky_grad` usa `sun_rot` (prima 230 fisso: a Parigi, sun_rot 140, il bagliore del cielo non era dove sta il sole); `style.night_off` vale come alias di `night_bld_off`. **Effetto sulle città vecchie se rifatte di notte**: Roma/Copenaghen (0,82) e Siviglia/Parigi (0,72) avranno più palazzi spenti del 35 % usato finora.
- `run.sh`: ramo kit per le città con `cities/<slug>/story.json` (le altre invariate).
