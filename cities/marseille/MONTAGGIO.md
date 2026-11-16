# Marseille — montaggio finale (Windows, senza .bat) — 16/11/2026 — PROVVISORIO fino al render (schedule 655,3 s)
Nessun cold open, per ordine del proprietario: il video parte dal primo anno (600 BC).
Cartella con: marseille_full.mp4 (render del pod), marseille_overlay.webm, marseille_audio.m4a (nomi come in `montaggio/monta_kit.sh`; `python -m kit montaggio marseille --overlay` + `sfx_kit.py` producono `out/marseille_overlay.webm` e `out/marseille_audio.m4a`). Serve ffmpeg nel PATH. Apri `cmd` nella cartella. Formato copiato da `cities/lyon/MONTAGGIO.md` (identico alla riga di `monta_kit.sh`, solo slug diverso).

## Unione: marseille_finale.mp4
```
ffmpeg -y -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_overlay.webm -i marseille_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart marseille_finale.mp4
```
Controlla (da `schedule_marseille.json`): titolo a 9,5 s; primo capitolo a 0:12; Saint-Jean a 7:27; cambio musicale a metà video (`b_start` non nello schedule: [Likely] circa 5:27, coperto dalla sosta più vicina); carta Sources a 10:47. PROVVISORIO: ricontrollare con `years.json` dopo il render.
