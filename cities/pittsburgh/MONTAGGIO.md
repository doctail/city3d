# Pittsburgh: montaggio finale (Windows `cmd`, senza .bat) — 19/11/2026
Nessun cold open (R14): il video parte dal primo anno (1754). Durata del render: 588,5 s (9:48), 14.124 fotogrammi (`years.json` del pod).
Cartella con tre file: `pittsburgh_full.mp4` (render del pod), `pittsburgh_overlay.webm` (livello grafico trasparente, canale "Ledger of Cities") e `pittsburgh_audio.m4a` (musica Waking to Reality + Monument con effetti, -14 LUFS). Serve ffmpeg nel PATH. Apri `cmd` nella cartella e incolla UNA riga (identica a `montaggio/monta_kit.sh`, slug diverso; stessa riga di Lyon/Marseille):

## Unione: pittsburgh_finale.mp4
```
ffmpeg -y -i pittsburgh_full.mp4 -c:v libvpx-vp9 -i pittsburgh_overlay.webm -i pittsburgh_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart pittsburgh_finale.mp4
```
Provata su questa macchina (Linux, ffmpeg 5/6) con un video di prova 1920x1080 da 10 s + i primi 10 s dell'overlay reale + i primi 10 s dell'audio reale: uscita h264 1920x1080 yuv420p, audio AAC, durata 10,0 s, ~23 s di CPU. La riga non e' stata provata su Windows (stesso comando delle citta' precedenti, provate dal proprietario).
Tempo atteso sul PC con il file vero: da 20 a 40 minuti (preset slow, 588 s a 1080p) [Guessing, non misurato].

## Controlli (da `montaggio/eventi_pittsburgh.json`)
Titolo a 9,7 s (dopo il riavvolgimento 3,2-9,5 s); capitolo I a 0:12; carta 1754 a 0:15; Subscribe a 1:43; musica A>B a 4:06, ritorno ad A a 7:47 (chiusura 8 s); CTA "Which city should grow next?" a 9:36; carta Sources a 9:40 fino a 9:48.

## R13 (controllo overlay a occhio, 19/11)
Fotogrammi controllati (94, un foglio di contatto + 2 ingrandimenti): primi 12 s secondo per secondo (0-11 s: riavvolgimento, "PITTSBURGH TODAY", "272 YEARS", titolo a 10-11 s), meta' di ognuno degli 8 capitoli, inizio+1,5 s di tutte le 50 carte e delle 14 soste, ultimi 15 s (573,5-588 s: CTA 9:36, carta Sources, "LEDGER OF CITIES"). Trovato e corretto: etichetta "Heinz Field (now Acrisure Stadium)" tagliata al bordo destro (466-472 s), accorciata a "Heinz Field" in `labs`/`labels` e rirenderizzati i 2 pezzi interessati. Nessuna sovrapposizione titolo/capitolo I. Limite: capitolo VIII (7:50) compare mentre svaniscono le etichette PNC Park/Heinz e la didascalia della sosta e' ancora in basso a destra: affollato ma senza testo sopra testo. Capitoli doppi (I, II... per ogni capitolo) corretti in `kit/eventi_kit.py`.
Overlay: `out/pittsburgh_overlay.webm` (40,7 MB, 14.124 fotogrammi), audio: `out/pittsburgh_audio.m4a` (14,5 MB, AAC 588,5 s, -14 LUFS); non committati.
