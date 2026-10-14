# PRODUZIONE TIMELAPSE — canale "Year Built"

Secondo progetto dentro "carta animata": timelapse 3D di città che crescono, senza voce. Canale YouTube separato (kit del canale in `city3d/canale_yearbuilt.md`). Questo file è la memoria tra una chat e l'altra per i timelapse; per i video storici valgono `claude/PRODUZIONE.md` e `claude/STATO.md`.

## Regole di Fabio (sempre)
- Rispondere in italiano. Nessun credito (vsub o altro) e nessun pod RunPod senza il suo OK esplicito, ogni volta.
- Chiamate brevi: interrompe quelle lunghe. Tenerlo aggiornato mentre si lavora.
- Testo a schermo, titoli, descrizioni in inglese americano (pubblico USA).
- 11 settembre / Torri Gemelle: tema delicatissimo per il pubblico USA, solo un cartello sobrio.

## Dove sta il codice
- Repository GitHub: `github.com/doctail/city3d` (pubblico). Il pod lo clona da lì. Ogni modifica va committata e pushata.
- File principali: `build_render.py` (scena Blender e render), `fetch_nyc.py` (dati NYC Open Data + terra NJ dal Census), `hist_nyc.py` (edifici storici demoliti), `schedule_nyc.json` (anni e camera sincronizzati alla musica), `run.sh` (tutto il flusso sul pod), `gputest.py`, `pack.sh`, `PROSSIMO_VIDEO.md` (note tecniche e numeri).
- Grafiche del montaggio (HUD anni, cartelli, titolo): Remotion, `city3d/hud.jsx` nel progetto.

## Flusso di un video
1. **Dati e regia (in chat, gratis)**: scaricare/derivare i dati della città, scrivere `schedule_<città>.json` (anni per secondo e chiavi camera `[t, [pos], [target], mm]`) sulla traccia musicale scelta.
2. **Prove locali (gratis)**: render CPU ritagliati (`--crop`, densità basse, 640x360) di 4–6 fotogrammi chiave; foglio di prova a Fabio. Correggere qui, non sul pod.
3. **Pod RunPod (con OK di Fabio)**: template PyTorch 2.8.0, 30 GB disco. GPU consigliata: RTX 5080 Community (0,39 $/h) o 4090 Community; L40 se servono più di 16 GB.
   - `cd /workspace && git clone https://github.com/doctail/city3d && cd city3d && bash run.sh profile` (6 minuti: misura i secondi/fotogramma di 5 configurazioni).
   - poi `bash run.sh full` (riprende da dove si è fermato; i fotogrammi fatti si saltano).
   - Download da Jupyter: `out/nyc_full.mp4` e `out/years.json`. Poi TERMINARE il pod.
4. **Montaggio (in chat)**: Fabio carica l'mp4 nella chat (GitHub non riceve il video). Aggiungo HUD con anno e popolazione, cartelli degli eventi, titolo, musica, finale; poi copertina e metadati.

## Impostazioni che funzionano (New York, ottobre 2026)
- 1920x1080, 8 campioni, denoiser **OptiX** (OIDN costava 2,5 s in più a fotogramma), rimbalzi ridotti, JPG 95 (i PNG erano 8 MB l'uno e riempivano il disco).
- RTX 5080: **1,0 s/fotogramma**, 7.839 fotogrammi ≈ 2,3 ore ≈ 0,9 $. Riavvolgimento iniziale più lento (~7 s/fotogramma per ~90 fotogrammi).
- Nessun keyframe su materiali o datablock: qualsiasi animazione costringe Cycles a risincronizzare tutta la scena (13–18 s). Crescita solo con scala degli oggetti, sparizione spostandoli a z −5000, alberi "cotti" in mesh.
- La foschia è un'emissione: va esclusa dal campionamento delle luci (`emission_sampling = NONE`), altrimenti picchi da 12 s.
- Camera bassa (400–450 m, 40 mm) dal 1929 in poi per far leggere l'altezza dei grattacieli; cielo sfumato con nuvole.

## Stato
- **New York** (primo video): render completo lanciato il 14 ott 2026 su RTX 5080. In attesa dell'mp4 per il montaggio. Musica: "The Shining in Dubai" — Unicorn Heads (YouTube Audio Library), 5:27.
- Difetti noti accettati: New Jersey senza edifici (solo tessuto urbano disegnato); leggera macchiatura del denoiser sulle facciate a vetri; edifici pre-1900 ricostruiti in modo illustrativo.
- Prossima città candidata: Amsterdam (registro BAG con anno di costruzione di ogni edificio, altezze da 3DBAG) — da verificare.
