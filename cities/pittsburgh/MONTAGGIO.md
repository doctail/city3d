# Pittsburgh: montaggio finale (Windows `cmd`, senza .bat), rifatto il 27/11/2026 sul years.json vero del pod
Nessun cold open (R14): il video parte come renderizzato. Render: 14.822 fotogrammi = 617,6 s (10:17). Capitoli con gli orari FINALI: `CONSEGNA_YOUTUBE.md` (eventi rigenerati da `montaggio/years_pittsburgh.json` = file del pod: identici a quelli committati).

## File nella stessa cartella sul PC
`pittsburgh_full.mp4` (render del pod), `pittsburgh_overlay_1.webm` (19,8 MB, fotogrammi 0-7199), `pittsburgh_overlay_2.webm` (22,1 MB, 7200-14821), `pittsburgh_audio.m4a` (15,3 MB). Sorgenti in `out/` (non committati, troppo grandi; li invia la chat). ffmpeg nel PATH. Apri `cmd` in quella cartella.

## 1. Unisci i due pezzi di overlay (una riga, produce pittsburgh_overlay.webm di 617,75 s; provata qui)
```
(echo file pittsburgh_overlay_1.webm)>list.txt && (echo file pittsburgh_overlay_2.webm)>>list.txt && ffmpeg -y -f concat -safe 0 -i list.txt -c copy pittsburgh_overlay.webm
```

## 2. Unione finale: pittsburgh_finale.mp4 (una riga; identica a `monta_kit.sh pittsburgh long`)
```
ffmpeg -y -i pittsburgh_full.mp4 -c:v libvpx-vp9 -i pittsburgh_overlay.webm -i pittsburgh_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart pittsburgh_finale.mp4
```
Provata qui (Linux) con video di prova 1920x1080 + overlay vero (concat) + audio vero, 12 s: h264 1920x1080 yuv420p, AAC. Non provata su Windows ne' sul `pittsburgh_full.mp4` vero (che non ho). Tempo atteso 20-40 min [Guessing]. `-shortest` taglia a 617,5 s se il video e' piu' corto dell'audio: controllare che l'ultimo secondo (carta Sources) ci sia.

## 3. Miniatura FINALE (da fare sul PC col video vero: qui non c'e')
Bozza pronta: `copertina/pittsburgh_thumb_DRAFT_round2.jpg` (1280x720: `1754 > NOW`, due meta' piene, PITTSBURGH enorme, niente bandiera). La finale si estrae dal video (senza overlay):
```
ffmpeg -ss 21.54 -i pittsburgh_full.mp4 -frames:v 1 -q:v 2 pittsburgh_cover_forts.jpg
ffmpeg -ss 616 -i pittsburgh_full.mp4 -frames:v 1 -q:v 2 pittsburgh_cover_now.jpg
```
(21,54 s = fotogramma 517, anno 1754,95, mura di Fort Duquesne complete; 616 s = 2026, ultima inquadratura. Se l'inquadratura non convince, prova -ss 20.5/22.0 e 612-617.) Poi, nella cartella del repo: `python -m kit.thumb_kit cities/pittsburgh/copertina/pittsburgh_thumb_final.jpg --left pittsburgh_cover_forts.jpg --right pittsburgh_cover_now.jpg --title PITTSBURGH --ly 1754 --ry NOW --lbox 464,0,1050 --rbox 800,0,1050 --text-size 104 --lx 225 --rx 1070` (i box sono quelli della bozza: vanno ritoccati sui fotogrammi del video).

## Cosa e' stato fatto e misurato (27/11)
- Musica: A = "Waking to Reality" (Unicorn Heads, 272,6 s), B = "Monument" (TrackTribe, 251,5 s); modello `kit/music/waking_monument.json` invariato. `sfx_kit` ricalcola sul nuovo schedule: playlist A@0 > B@246 s (4:06) > A@477 s (7:57), chiusura a 8 s; 14 effetti sulle soste. Audio 617,6 s, -13,9 LUFS, picco vero -0,8 dBTP, nessun silenzio oltre 1 s, nessun clipping.
- Overlay: 14.822 fotogrammi, 1920x1080 VP9+alfa, 617,75 s (concat dei due pezzi). Brand "LEDGER OF CITIES" (0 occorrenze di "YEAR BUILT" nel kit json), anni, popolazioni, 55 carte, 14 soste, 8 capitoli, etichette monumenti (Fort Pitt Block House 1764, Duquesne Incline 1876, Gulf Tower 1930, Civic Arena 1958, Three Rivers Stadium 1968).
- R13 (27/11, 99 fotogrammi dall'overlay vero composti su sfondo grigio-azzurro, guardati a fogli): primi 11 s secondo per secondo, titolo, 8 capitoli (+1,5 s), tutte le 55 carte, tutte le 14 soste, Subscribe, CTA, Sources, ultimi 15 s. TROVATO E CORRETTO: il clip Subscribe (90 s) copriva il testo della carta "Fort Pitt is torn down" (89,8-96,0 s). Spostato a 63,0 s (`story.json` montaggio.subscribe_t e `eventi_pittsburgh.json`; finestra libera 60,4-69,6 s), rirenderizzati i 2 pezzi toccati, controllato 65,5 / 91 / 93 s: nessuna sovrapposizione. Nessun altro testo sopra testo.
- Cambio di tempi rispetto al 19/11: Subscribe 1:03 (era 1:30); carta Sources 10:09 (609,6-617,6 s), CTA 10:05 (605,1 s), titolo 9,7 s, capitolo I 0:13.
- Limite [Certain]: non ho il video 3D, quindi il montaggio completo e il controllo delle inquadrature sulle versioni light spettano alla chat; ho controllato solo overlay e audio.
