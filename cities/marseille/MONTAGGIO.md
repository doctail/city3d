# Marseille — montaggio finale (Windows, senza .bat) — 16/11/2026 — PROVVISORIO fino al render (aggiornato sullo schedule round 4: 655,3 s)
Cartella con: marseille_full.mp4 (render del pod), marseille_overlay.webm, marseille_audio.m4a (nomi come in `montaggio/monta_kit.sh`; `python -m kit montaggio marseille --overlay` + `sfx_kit.py` producono overlay e audio, `out/marseille_overlay.webm`, `out/marseille_audio.m4a`). Serve ffmpeg nel PATH. Apri `cmd` nella cartella. Formato copiato da `cities/lyon/MONTAGGIO.md` (identico alla riga di `monta_kit.sh`, solo slug diverso). Nessun file inventato.

## 1. Unione: marseille_finale.mp4
```
ffmpeg -y -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_overlay.webm -i marseille_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart marseille_finale.mp4
```
Controlla (da `schedule_marseille.json`): titolo a 9,5 s; primo capitolo a 0:12 (invariato); hover 1943 a 7:27-7:36 (447,92-456,92 s); cambio musicale a metà video (`b_start` non nello schedule: [Likely] circa 5:27, coperto dalla sosta più vicina); finale: carta Sources a 10:47.

## 2. Cold open di 9 s (il Saint-Jean dinamitato, 1943) davanti al video: marseille_finale_cold.mp4
Prende i secondi 447,9-456,9 di marseille_finale.mp4, li mette in testa con dissolvenza finale e poi il video intero. I capitoli diventano quelli "con cold open di 9 s" di `CONSEGNA_YOUTUBE.md` (+9 s).
```
ffmpeg -y -ss 447.9 -t 9 -i marseille_finale.mp4 -i marseille_finale.mp4 -filter_complex "[0:v]fade=t=out:st=8.4:d=0.6[v0];[0:a]afade=t=out:st=8.4:d=0.6[a0];[v0][a0][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 256k -movflags +faststart marseille_finale_cold.mp4
```
**PROVVISORIO, motivo (calcolo dallo schedule round 4, non dal render):** hover del 1943 = 447,92-456,92 s (9 s; contatore 1943,04 → 1943,14, lineare; la carta 'condemned' finisce a 447,86, 'Liberation and a fallen bridge' parte a 458,85: nessuna carta sovrapposta). Dinamitaggio (1943,088-1943,132) ≈ 452,2-456,2 s. Finestra scelta: 447,9-456,9 (9 s: ~4 s di quartiere in piedi, ~4 s di esplosioni, macerie) → capitoli 'con cold open' = +9 s. Taglio più stretto consigliato dal coordinatore: 451,2-456,9 (5,7 s) con `-t 5.7` e `fade st=5.1`; in quel caso i capitoli con cold open sono +5,7 (da ricalcolare: dimmelo e rigenero). Rileggi i secondi esatti da `years.json` dopo il render.
Se non vuoi il cold open, pubblica marseille_finale.mp4 con i capitoli senza cold open.
