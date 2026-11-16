# Marseille — montaggio finale (Windows, senza .bat) — 16/11/2026 — render verificato con years.json (655,3 s)
Nessun cold open, per ordine del proprietario: il video parte dal primo anno (600 BC).
Cartella con: marseille_full.mp4 (render del pod), marseille_overlay.webm, marseille_audio.m4a (nomi come in `montaggio/monta_kit.sh`; `python -m kit montaggio marseille --overlay` + `sfx_kit.py` producono `out/marseille_overlay.webm` e `out/marseille_audio.m4a`). Serve ffmpeg nel PATH. Apri `cmd` nella cartella. Formato copiato da `cities/lyon/MONTAGGIO.md` (identico alla riga di `monta_kit.sh`, solo slug diverso).

## Unione: marseille_finale.mp4
```
ffmpeg -y -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_overlay.webm -i marseille_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart marseille_finale.mp4
```
Controlla (da `schedule_marseille.json`): titolo a 9,5 s; primo capitolo a 0:12; Saint-Jean a 7:27; cambio musicale A→B a 4:04 (244 s, misurato; coperto dalla sosta La Vieille Charité, 244,2-249,2 s) e ritorno B→A a 7:56 (476 s: NON coperto da una sosta, la più vicina è Pouillon a 8:06); carta Sources a 10:47. years.json del render (15.607 fotogrammi, scarto 0 dallo schedule) ricontrollato: capitoli confermati; i 120 fotogrammi finali (notte) mancano in years.json e sono stati completati a 2026,0 dallo schedule.

## Short (28 s, 1080x1920): marseille_short.mp4
Vedi `SHORT.md` (stessa cartella, file `marseille_short_overlay.webm`, `marseille_short_audio.m4a`, `marseille_full.mp4`). Una riga per cmd:
```
ffmpeg -y -ss 10.5 -t 638.8 -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_short_overlay.webm -i marseille_short_audio.m4a -filter_complex "[0:v]setpts=PTS*0.04148,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart marseille_short.mp4
```

## Note tecniche dell'overlay (16/11/2026)
- Overlay e audio prodotti in `out/`: `marseille_overlay.webm`, `marseille_audio.m4a` (655,300 s, -13,9 LUFS, picco -0,85 dBFS), `marseille_short_overlay.webm`, `marseille_short_audio.m4a`.
- Musica: A@0 (Waking to Reality) > B@244 (Monument) > A@476 (chiusura 8 s) = playlist del kit per durata automatica. Effetti: 7 posizionati; gli fx `stone`, `chime`, `train`, `build` della story non esistono nel kit (saltati).
- Etichette dei monumenti presenti (`montaggio/labels_marseille.json` da `labels_cam.py` con bpy 5.2.2; nomi inglesi della story; `montaggio.label_area` [230,1690,230,900] perché nessuna etichetta venga tagliata ai bordi).
- Capitoli: `montaggio.chapters` tolto dalla story (le carte con `chapter` bastano): numeri I-VIII senza doppioni, anche rilanciando `kit_city.py marseille`.
- Sottotitolo del titolo a schermo: 'Open data, reconstruction before 1800' (`montaggio.open[3]`). Chip dei regimi accorciati (`city.polities[*].name`, solo testo).
- Short: `kit_overlay.jsx` (una modifica): la CTA 'FULL VIDEO' compare quando l'anno è già sparito (nessuna sovrapposizione a 27-28 s).

## Overlay lungo: 45,3 MB, diviso in due file da scaricare (sotto 30 MB)
`out/marseille_overlay_1.webm` (25,6 MB, fotogrammi 0-7999) + `out/marseille_overlay_2.webm` (19,7 MB, 8000-15726). Verificato: riunendoli con il comando sotto si ottiene un file identico (stessa dimensione, 15.727 fotogrammi, 1920x1080, 24 fps). Una riga per cmd, nella cartella con i due file:
```
(echo file marseille_overlay_1.webm)>list.txt && (echo file marseille_overlay_2.webm)>>list.txt && ffmpeg -y -f concat -safe 0 -i list.txt -c copy marseille_overlay.webm
```
Poi il comando di unione del video lungo (sopra). Lo Short usa `marseille_short_overlay.webm` (1,9 MB) e `marseille_short_audio.m4a` (0,7 MB).
