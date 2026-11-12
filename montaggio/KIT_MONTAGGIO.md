# Kit montaggio (Year Built): dal render 3D al video finale

Tutti i comandi si lanciano dalla radice del repo `city3d`. `<slug>` = nome città (es. `valencia`).
File per città richiesti in `montaggio/`: `eventi_<slug>.json`, `labels_<slug>.json`, `labs_<slug>.json`
(`years_<slug>.json` si ricava da `schedule_<slug>.json` se manca; `eventi` si costruisce da `story.montaggio.events` se manca).
Sono comunque necessari `cities/<slug>/story.json` (sezioni `city`, `regia`, `montaggio`) e `schedule_<slug>.json`.

1. **Dipendenze** (una volta): `cd montaggio && npm install` (non committare `node_modules`, `package-lock.json`, `out/`).
2. **Configurazione overlay**: `python3 montaggio/kit_city.py <slug>` genera `montaggio/public/kit_<slug>.json` (+ copie dei 4 json). Tutti i tempi (HUD, titolo, sepia, fine, Short) derivano dallo schedule. Legge gli avvisi finali (sosta senza "(data)", `est_until` assente, ecc.).
   Chiavi opzionali: `city.pop_label|est_until|ticks|popmax`; `montaggio.open` (2 stringhe, o 4 con 2ª schermata), `title`, `end`, `end_sub`, `tok_exclude`, `subscribe_t`, `label_area`, `short_tag`.
3. **Anteprima di un fotogramma**: `cd montaggio && npx remotion still kit_overlay.jsx KitOverlay /tmp/f.png --frame=3000 --props='{"slug":"<slug>"}'` (Short: composizione `KitShort`; con video: `KitPreview`, serve `public/<slug>_light.mp4`). Il PNG è trasparente: guardalo su sfondo scuro.
4. **Render overlay** (a pezzi da 800 fotogrammi, riprende se interrotto): `bash montaggio/ov_kit.sh <slug>` → `out/<slug>_overlay.webm`; Short: `bash montaggio/ov_kit.sh <slug> short` → `out/<slug>_short_overlay.webm`. Chromium trovato da solo (o `BROWSER=...`); prova rapida `FRAMES=0-47`.
5. **Audio** (musica A/B + effetti da `regia.soste[*].fx`, loudnorm -14 LUFS):
   `python3 montaggio/sfx_kit.py <slug> --A waking.mp3 --B monument.mp3` → `out/<slug>_audio.m4a` e `out/<slug>_short_audio.m4a`. Prova veloce: `--test 20`.
   Python con numpy+scipy (`/home/user/bl/bin/python`). Cambio A→B a `schedule.b_start` (altrimenti `regia.music_cuts.b_start_sosta`, altrimenti metà video), coperto dalla sosta più vicina; ritorno ad A con `regia.music_cuts.a_return_sosta` (automatico se B è troppo corta).
   `fx` di una sosta: `"hammer"`, `{"fx":"hammer","dt":0.8,"gain":0.08,"n":6}` o lista. Nomi: hammer crowd fire bell boom water battle quake horn peal crash firework rocket alarm hum. Anche `montaggio.events[*].fx` (per le didascalie).
6. **Montaggio finale**: metti `<slug>_full.mp4` (render del pod) in `out/` e lancia `bash montaggio/monta_kit.sh <slug>` → `out/<slug>_finale.mp4`; Short: `bash montaggio/monta_kit.sh <slug> short`. Colore: `CONTRAST=1.04 SAT=1.10 bash ...`.
   Windows (Fabio): `monta_kit.bat <slug>` nella cartella con i file; Short: `monta_kit.bat <slug> short A B SP` (valori da `public\kit_<slug>.json`, chiave `short`; SP = (28-1.5)/(B-A)).

Prova senza render 3D: `montaggio/test_fixtures/roma_story.json` (story minima di Roma) con `--story montaggio/test_fixtures/roma_story.json` su `kit_city.py` e `sfx_kit.py`.
Differenza da Roma: le didascalie `sober` hanno barra e data grigie (Roma le aveva dorate); per il resto i fotogrammi sono identici pixel per pixel.
