# Lyon — montaggio finale (Windows, senza il .bat) — 16/11/2026
Cartella con: lyon_full.mp4 (render del pod), lyon_overlay.webm, lyon_audio.m4a. Serve ffmpeg nel PATH. Apri `cmd` nella cartella.

## 1. Unione: lyon_finale.mp4
```
ffmpeg -y -i lyon_full.mp4 -c:v libvpx-vp9 -i lyon_overlay.webm -i lyon_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart lyon_finale.mp4
```
Controlla: apertura 0:00-0:14, cambio musicale a 4:06, soste di Saint-Jean (1:35-1:42) e Confluences (7:59), finale.

## 2. Cold open di 6 s (il fuoco dell'assedio del 1793) davanti al video: lyon_finale_cold.mp4
Prende i secondi 156-162 di lyon_finale.mp4 (hover dell'assedio, fiamme e fumo), li mette in testa con dissolvenza finale e poi il video intero. I capitoli diventano quelli "con cold open di 6 s" di CONSEGNA_YOUTUBE.md.
```
ffmpeg -y -ss 156 -t 6 -i lyon_finale.mp4 -i lyon_finale.mp4 -filter_complex "[0:v]fade=t=out:st=5.4:d=0.6[v0];[0:a]afade=t=out:st=5.4:d=0.6[a0];[v0][a0][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 256k -movflags +faststart lyon_finale_cold.mp4
```
Se il fuoco non è nel punto migliore, cambia `-ss 156` (l'hover dell'assedio va da circa 152 a 170 s). Se non vuoi il cold open, pubblica lyon_finale.mp4 con i capitoli senza cold open.
