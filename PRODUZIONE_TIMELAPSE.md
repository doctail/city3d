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
- Piano deciso con Fabio (14 ott 2026): 2 video a settimana per 8 settimane + 3 Shorts per video (li taglio io dal video finale; dalla seconda città clip verticali renderizzate sul pod). Città raggruppate per fonte dati (Spagna = catasto, Olanda = BAG). Verifica alla settimana 8: almeno un video sopra 10.000 visualizzazioni oppure 300 iscritti, altrimenti si ripensa il formato.
- Seconda città: **Madrid** (catasto spagnolo). "(No AI)" nel titolo.

## Concorrenza (aggiornare prima di ogni città)
- Già fatte da altri (ott 2026): Roma, Berlino, Londra (CityEons); Parigi (virale gen 2026); Manhattan 1600–2026 (CITY 3D TIMELAPSE, virale ago 2026); Las Vegas (Cornerstone); Budapest (Urbis Anno); Firenze (Tree The City); Gerusalemme (Urbavision); Praga (Latos Charts).
- Formato copertina della nicchia: anni in alto con freccia, nome città enorme e spaziato in basso, bandiera, immagine piena. Script: `thumb_city.py`. Titoli senza "No AI" (decisione di Fabio, 14 ott 2026).
- Verifica del 14 ott 2026 (ricerche YouTube di Fabio): Chicago 4+ video nelle ultime 2 settimane (Cornerstone 60K, gli altri 2–8K); Barcellona Latos Charts 342K + 3 canali piccoli; Amsterdam Latos 502K e una decina di canali nuovi da 20 a 2.000 visualizzazioni, tra cui UrbanRewind con lo stesso nostro angolo ("35,455 Real Buildings", 22 visualizzazioni). Conclusione: la nicchia è già affollata di canali nuovi; le visualizzazioni vanno quasi tutte ai canali affermati (Latos Charts, CITY 3D TIMELAPSE, CityEons, Cornerstone). "(No AI)" è usato dai canali grandi.
- Regola: prima di ogni città, cercare su YouTube "<città> 3D timelapse"; precedenza alle città libere.

## Città candidate e dati (anno di costruzione per edificio)
- Barcellona: Catasto spagnolo INSPIRE (anno e piani di ogni edificio, tutta la Spagna) — da verificare.
- Chicago: footprints comunali con year_built; evento forte (incendio 1871); pubblico USA — da verificare.
- Amsterdam / Rotterdam: registro BAG (bouwjaar) + 3DBAG (altezze); Rotterdam ha il bombardamento del 1940 — da verificare.
