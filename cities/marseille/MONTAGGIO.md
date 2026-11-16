# Marseille — montaggio finale (Windows, senza .bat) — 16/11/2026 — PROVVISORIO fino al render
Cartella con: marseille_full.mp4 (render del pod), marseille_overlay.webm, marseille_audio.m4a (nomi come in `montaggio/monta_kit.sh`; `python -m kit montaggio marseille --overlay` + `sfx_kit.py` producono overlay e audio, `out/marseille_overlay.webm`, `out/marseille_audio.m4a`). Serve ffmpeg nel PATH. Apri `cmd` nella cartella. Formato copiato da `cities/lyon/MONTAGGIO.md` (identico alla riga di `monta_kit.sh`, solo slug diverso). Nessun file inventato.

## 1. Unione: marseille_finale.mp4
```
ffmpeg -y -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_overlay.webm -i marseille_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart marseille_finale.mp4
```
Controlla (da `schedule_marseille.json`): titolo a 9,5 s; primo capitolo a 0:12; hover 1943 a 7:26-7:40 (446,1-460,1 s); cambio musicale a metà video (`b_start` non nello schedule: [Likely] circa 5:27, coperto dalla sosta più vicina); finale: carta Sources a 10:47.

## 2. Cold open di 9 s (il Saint-Jean dinamitato, 1943) davanti al video: marseille_finale_cold.mp4
Prende i secondi 451-460 di marseille_finale.mp4, li mette in testa con dissolvenza finale e poi il video intero. I capitoli diventano quelli "con cold open di 9 s" di `CONSEGNA_YOUTUBE.md` (+9 s).
```
ffmpeg -y -ss 451 -t 9 -i marseille_finale.mp4 -i marseille_finale.mp4 -filter_complex "[0:v]fade=t=out:st=8.4:d=0.6[v0];[0:a]afade=t=out:st=8.4:d=0.6[a0];[v0][a0][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 256k -movflags +faststart marseille_finale_cold.mp4
```
**PROVVISORIO, motivo (calcolo dallo schedule, non dal render):** l'hover del 1943 è 446,12-460,12 s; il contatore va da 1943,04 a 1943,14 in modo lineare, quindi l'onda di distruzione (1943,088-1943,132 della story) cade circa tra 452,8 e 459,0 s: la finestra 451-460 mostra circa 2 s di quartiere in piedi, poi il dinamitaggio, poi le macerie. Rileggi i secondi esatti da `years.json` dopo il render e cambia `-ss`.
**Problema da risolvere PRIMA del render (storia/regia, non mio):** nello schedule le carte 1943,22 "The Saint-Jean quarter is gone" (446,1-454,1) e 1944,66 "Liberation" (454,1-460,1) sono entrambe `on_hover` dentro lo stesso hover. La finestra del cold open prenderebbe per 6 s su 9 la carta "Liberation 1944" sopra l'esplosione, con l'anno 1943 nel contatore. Soluzione consigliata: spostare "Liberation" fuori dall'hover (dopo 460,1 s) o dargli un hold che non la sovrapponga all'onda. Se non si cambia, il cold open va fatto dal video senza overlay.
Se non vuoi il cold open, pubblica marseille_finale.mp4 con i capitoli senza cold open.
