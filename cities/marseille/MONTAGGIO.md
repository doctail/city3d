# Marseille — montaggio finale (Windows, senza .bat) — 16/11/2026 — PROVVISORIO fino al render (schedule 655,3 s)
Nessun cold open, per ordine del proprietario: il video parte dal primo anno (600 BC).
Cartella con: marseille_full.mp4 (render del pod), marseille_overlay.webm, marseille_audio.m4a (nomi come in `montaggio/monta_kit.sh`; `python -m kit montaggio marseille --overlay` + `sfx_kit.py` producono `out/marseille_overlay.webm` e `out/marseille_audio.m4a`). Serve ffmpeg nel PATH. Apri `cmd` nella cartella. Formato copiato da `cities/lyon/MONTAGGIO.md` (identico alla riga di `monta_kit.sh`, solo slug diverso).

## Unione: marseille_finale.mp4
```
ffmpeg -y -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_overlay.webm -i marseille_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart marseille_finale.mp4
```
Controlla (da `schedule_marseille.json`): titolo a 9,5 s; primo capitolo a 0:12; Saint-Jean a 7:27; cambio musicale a metà video (`b_start` non nello schedule: [Likely] circa 5:27, coperto dalla sosta più vicina); carta Sources a 10:47. years.json del render (15.607 fotogrammi, scarto 0 dallo schedule) ricontrollato: capitoli confermati; i 120 fotogrammi finali (notte) mancano in years.json e sono stati completati a 2026,0 dallo schedule.

## Short (28 s, 1080x1920): marseille_short.mp4
Vedi `SHORT.md` (stessa cartella, file `marseille_short_overlay.webm`, `marseille_short_audio.m4a`, `marseille_full.mp4`). Una riga per cmd:
```
ffmpeg -y -ss 10.5 -t 638.8 -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_short_overlay.webm -i marseille_short_audio.m4a -filter_complex "[0:v]setpts=PTS*0.04148,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart marseille_short.mp4
```

## Note tecniche dell'overlay (16/11/2026)
- Overlay e audio prodotti in `out/`: `marseille_overlay.webm`, `marseille_audio.m4a` (655,300 s, -13,9 LUFS, picco -0,85 dBFS), `marseille_short_overlay.webm`, `marseille_short_audio.m4a`.
- Musica: A@0 (Waking to Reality) > B@244 (Monument) > A@476 (chiusura 8 s) = playlist del kit per durata automatica. Effetti: 7 posizionati; gli fx `stone`, `chime`, `train`, `build` della story non esistono nel kit (saltati).
- Mancano le etichette dei monumenti sullo schermo: `montaggio/labels_marseille.json` richiede Blender (`labels_cam.py`, bpy non disponibile qui).
- `montaggio/eventi_marseille.json` e `public/kit_marseille_eventi.json` rigenerati senza `montaggio.chapters` della story: il kit (`kit/eventi_kit.py`, `kit_city.py`) leggeva i capitoli sia da `montaggio.chapters` sia dalle carte con `chapter`, quindi li duplicava (numeri I, III, V... XV). Correzione di una riga consigliata alla story: togliere `montaggio.chapters` (o dedupe nel kit); fino ad allora `kit_city.py marseille` senza `--story` rigenera il difetto.
