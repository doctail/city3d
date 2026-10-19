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
- Città basse (Madrid): camera "da drone" che parte stretta e si allarga con la città (raggio = 0,95 × raggio storico + 900 m, inclinazione 20–22°), sempre sul lato SUD: guardando verso sud si va controsole e la città diventa marrone scuro. Poi volo basso lungo l'asse moderno fino ai grattacieli.

## Stato
- **New York** (primo video): render completato il 14 ott 2026 (RTX 5080, 2 h 46 min, ~1,1 $). Montaggio fatto: grafiche trasparenti `nyc_overlay.webm` + `monta_nyc.bat` (Fabio unisce sul suo PC al file a qualità piena). Copertina finale, metadati (`metadata_nyc.md`) e 3 Shorts consegnati. Codice montaggio in `montaggio/` (hud.jsx, nyc_overlay.jsx, nyc_shorts.jsx) su GitHub. Musica: "The Shining in Dubai" — Unicorn Heads (YouTube Audio Library), 5:27.
- Difetti noti accettati: New Jersey senza edifici (solo tessuto urbano disegnato); leggera macchiatura del denoiser sulle facciate a vetri; edifici pre-1900 ricostruiti in modo illustrativo.
- Piano deciso con Fabio (14 ott 2026): 2 video a settimana per 8 settimane + 3 Shorts per video (li taglio io dal video finale; dalla seconda città clip verticali renderizzate sul pod). Città raggruppate per fonte dati (Spagna = catasto, Olanda = BAG). Verifica alla settimana 8: almeno un video sopra 10.000 visualizzazioni oppure 300 iscritti, altrimenti si ripensa il formato.
- Seconda città: **Madrid** (catasto spagnolo). "(No AI)" nel titolo. 15 ott 2026: anteprima ok, render completo lanciato sul pod (1,0–1,1 s/fotogramma). Grafiche pronte (`montaggio/madrid_overlay.jsx`, dati in `montaggio/cities.js`), `monta_madrid.bat`, metadati in `metadata_madrid.md`. Mancano: copertina e Shorts (dopo il render).
- Montaggio per una nuova città: aggiungere l'oggetto della città in `montaggio/cities.js`, copiare `madrid_overlay.jsx`, generare `years_<città>.json` dalla regia, poi `OVC=<file> OVID=<Comp> OVDIR=... OVOUT=... bash montaggio/ov_chunks.sh` (pezzi da 800 fotogrammi, ~4 min l'uno).
- Regola: niente secondi vuoti all'inizio (il riavvolgimento deve arrivare a un anno in cui c'è già qualcosa da vedere).

## Concorrenza (aggiornare prima di ogni città)
- Già fatte da altri (ott 2026): Roma, Berlino, Londra (CityEons); Parigi (virale gen 2026); Manhattan 1600–2026 (CITY 3D TIMELAPSE, virale ago 2026); Las Vegas (Cornerstone); Budapest (Urbis Anno); Firenze (Tree The City); Gerusalemme (Urbavision); Praga (Latos Charts).
- Formato copertina della nicchia: anni in alto con freccia, nome città enorme e spaziato in basso, bandiera, immagine piena. Script: `thumb_city.py`. Titoli senza "No AI" (decisione di Fabio, 14 ott 2026).
- Verifica del 14 ott 2026 (ricerche YouTube di Fabio): Chicago 4+ video nelle ultime 2 settimane (Cornerstone 60K, gli altri 2–8K); Barcellona Latos Charts 342K + 3 canali piccoli; Amsterdam Latos 502K e una decina di canali nuovi da 20 a 2.000 visualizzazioni, tra cui UrbanRewind con lo stesso nostro angolo ("35,455 Real Buildings", 22 visualizzazioni). Conclusione: la nicchia è già affollata di canali nuovi; le visualizzazioni vanno quasi tutte ai canali affermati (Latos Charts, CITY 3D TIMELAPSE, CityEons, Cornerstone). "(No AI)" è usato dai canali grandi.
- Regola: prima di ogni città, cercare su YouTube "<città> 3D timelapse"; precedenza alle città libere.
- Verifica vidIQ del 15 ott 2026 (15 crediti): Rotterdam → Epoch Timelapse (AI, camera fissa a Oude Haven, 4 ott 2026) 39.800 visualizzazioni in 11 giorni con 5.900 iscritti, capitolo forte sul bombardamento del 1940; mappa animata Museum Rotterdam 2012 (26K). Siviglia → Epoch Timelapse AI (ago 2026, 18K). Valencia → nessun video di crescita. Nuovo concorrente con il nostro stile esatto: **Timeline Cities** (Venezia 3D, 400 iscritti, 13.600 visualizzazioni in 2 settimane). Epoch Timelapse sta coprendo le città europee una alla volta (Milano 72K, Barcellona, Siviglia, Rotterdam): ricontrollare il suo canale prima di ogni città.

## Città candidate e dati (anno di costruzione per edificio)
- Barcellona: Catasto spagnolo INSPIRE (anno e piani di ogni edificio, tutta la Spagna) — da verificare.
- Chicago: footprints comunali con year_built; evento forte (incendio 1871); pubblico USA — da verificare.
- Amsterdam / Rotterdam: registro BAG (bouwjaar) + 3DBAG (altezze); Rotterdam ha il bombardamento del 1940 — da verificare.

## Ricerca vidIQ (14 ott 2026) — vale per tutti i video
- Il pubblico cerca **"evolution"**, non "grow": "city evolution 3d" ~28.000 ricerche/mese, concorrenza 24/100, +131% in 30 giorni; "city evolution" 28.700 (+33%); "city evolution timelapse" 12.000; "3d city evolution" 9.700; "evolution of new york city" 10.400; "evolution of madrid" 4.700 con concorrenza 12/100 (bassissima).
- Il formato dominante della nicchia è "Evolution of <Città> | Fixed-Camera Timelapse: N Years in M Minutes", quasi tutto generato con AI. Canali piccoli esplodono: EvolveInTime (1.570 iscritti) 76K, Civilizations in Motion (9K) 2M, Restored Timeline Chicago 3,5M, Timelapse Professor "History Of Rome - 3D Timelapse (NO AI)" 19K con 1.950 iscritti. Quindi NON è vero che le visualizzazioni vanno solo ai canali affermati.
- Differenza nostra da difendere: dati reali, niente AI → "(No AI)" e "Every Real Building" restano nel titolo.
- Punteggi titolo vidIQ: "Watch New York Grow for 400 Years — Every Real Building, 1609–2026 (No AI)" 91; "Evolution of New York City in 3D | 400 Years, Every Real Building (No AI)" 96; Madrid "Evolution of Madrid in 3D | 500 Years, Every Real Building (No AI)" 90.
- Schema titolo da qui in avanti: **Evolution of <City> in 3D | N Years, Every Real Building (No AI)**. Tag di base: city evolution 3d, 3d city evolution, city evolution timelapse, evolution of <city>, <city> history, history of <city>, <city> timelapse, 3d timelapse, historical reconstruction.
- Primi dati New York (circa 4 ore): 1.100 impressioni, CTR 1,3% (basso), 30 visualizzazioni, durata media 1:02 su 5:27 (19%). Campione troppo piccolo per giudicare.

## RIPARTENZA IN UNA NUOVA CHAT (aggiornato 15 ott 2026, 16:00)
Il sandbox di una nuova chat è vuoto: tutto ciò che serve sta su GitHub (`git clone https://github.com/doctail/city3d`) e in questo progetto.
- Montaggio (Remotion): creare una cartella, copiarci `montaggio/package.json`, `npm install`, mettere i .jsx di `montaggio/` in `src/` e i `years_*.json` in `public/`. Browser locale: `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`, `--concurrency=2`. Rendering a pezzi (≤10 min per chiamata).
- Copertine: `thumb_city.py` (font Anton/Oswald: `npm pack @fontsource/anton@5 @fontsource/oswald@5` in /tmp/claude-0/fonts). Bandiere: us, es.
- I video di Fabio (full/light) NON sono su GitHub: se servono, li ricarica lui in chat.

### Stato al 15 ott 2026
- **New York**: pubblicato il 14 ott. Dopo ~22 h: 3.200 impressioni, CTR 2,5%, 161 visualizzazioni, durata media 1:07 su 5:27 (20%). Curva di fidelizzazione non ancora disponibile.
  - **Venerdì 16 ott sera** (48 h): cambiare insieme titolo → "Evolution of New York City in 3D | 400 Years, Every Real Building (No AI)" e copertina → `copertina_nyc_v2.jpg` (prima/dopo 1658|2026). Annotare CTR e impressioni al momento del cambio.
  - **Domenica 18 ott**: confrontare CTR 48 h prima/dopo (miglioramento vero solo se > 3%). Se compare la curva di fidelizzazione e il calo è tra 0:06 e 0:30 (foresta vuota), valutare il taglio con l'editor di YouTube Studio.
  - Descrizione: togliere la vecchia frase "From a forested island…" rimasta, hashtag → #NewYork #Manhattan #Timelapse.
- **Madrid**: render completato (RTX 5080, 1,88 s/fotogramma, ~4,1 h). Consegnati: `madrid_overlay.webm`, `monta_madrid.bat` (con leggero contrasto), `copertina_madrid.jpg`, 3 Shorts con titolo/anno/musica, `metadata_madrid.md`. Fabio deve unire sul PC (bat), controllare 2:30–4:30 (parte un po' piatta) e pubblicare.
  - Costo pod Madrid ≈ 2,4 $ (sopra il tetto di 2 €): gli Shorts verticali nativi costano ~0,7 $. Per le prossime città decidere prima se farli nativi o ritagliati (gratis).
- **Terza città: Rotterdam** (decisione di Fabio, 15 ott 2026). Motivo: il video AI di Epoch dimostra la domanda (~40K in 11 giorni); il nostro è aereo, su tutta la città, con dati reali. Titolo: "Evolution of Rotterdam in 3D | N Years, Every Real Building (No AI)".
  - Dati: 3DBAG lod13 in GeoParquet su source.coop (747 MB, una riga per parte di edificio, `bouwjaar` 9999 = sconosciuto, `height` sul terreno). Dal sandbox è BLOCCATO (anche api.3dbag.nl e PDOK): si scarica dal pod. Script: `fetch_nl.py` (provato su un file finto con lo stesso schema), `data_nl.sh` (pod CPU, niente Blender), `city_rotterdam.json` (centro Laurenskerk, raggio 9 km).
  - Passi: (1) pod CPU con OK di Fabio → `CITY=rotterdam bash city3d/data_nl.sh` → scaricare `dati_rotterdam.tgz` e caricarlo in chat; (2) acqua e parchi: export OSM da overpass-turbo fatto da Fabio → `osm_extra.py` (la Nieuwe Maas taglia la città: senza acqua il video non regge); (3) strato storico `hist_rotterdam.py`: il BAG ha solo gli edifici di oggi, quindi il centro distrutto il 14 maggio 1940 va ricostruito da mappe storiche con anno di demolizione `d=1940` (build_render lo supporta); (4) regia e prove locali.
  - Rischio noto: gli anni BAG degli edifici molto antichi sono spesso approssimati.
  - 15 ott 2026, fatto: dati estratti dal pod (268.466 parti, tolta una "torre" di 316 m su 17 m2) e salvati in `data_rotterdam_src/`; acqua e parchi da Geofabrik (Overpass rispondeva 500 da tutti i server) con `osm_nl.sh` + `osm_pbf.py`; `osm_extra.py` ora legge i multipoligoni (la Nieuwe Maas lo e'). `hist_rotterdam.py`: triangolo medievale, Waterstad 1590-1640, Schiedam (il nucleo antico piu' grande nel raggio: 150 edifici pre-1800), Delfshaven, Overschie, Charlois, riva sud dal 1870, zona distrutta il 14 maggio 1940 (8.617 edifici storici spariscono, contorno approssimato). 353.000 predecessori: con 268.000 edifici reali la scena e' piu' pesante di Madrid, controllare i tempi nel profilo.
  - Shorts: verticali nativi dal pod (decisione di Fabio, 15 ott 2026), pur costando ~0,7 $ in piu'. Tratti in `city_rotterdam.json` -> `shorts`, gia' adattati alla regola di ritmo (24-29 s).
  - 15 ott 2026, regia e prove locali fatte. ORIGINE = Stadhuis sulla Coolsingel, non la Laurenskerk (che sta a ~(536, 22)): i punti storici sono ora calcolati da lat/lon. Riva sud = massa di terra che contiene Charlois (da land.json). Bacini portuali: `harbours_rotterdam.py` (canale = linea OSM della Nieuwe Maas + 320 m; bacini per zona con anno di scavo) -> `harbours.json`: terra verde fino all'anno, poi acqua. `build_render.py`: `--only` (prove su fotogrammi scelti), `haze_k` e `field_colors` per citta', supporto `harbours.json`.
  - Musica: stesso brano (The Shining in Dubai). Misure: calo 3:27-3:31, quasi silenzio 3:32-3:36, ripresa 3:37-3:56, crescendo da 3:57. Regia (`regia_rotterdam.py` -> `schedule_rotterdam.json`): 1340 -> 1938 fino a 3:24, 14 maggio 1940 nel calo, centro vuoto nel silenzio, ricostruzione 1946-1957 nella ripresa, dopoguerra e skyline nel crescendo. Camera a sud, quasi ferma nel 1940, bassa sul fiume alla fine.
  - Prova locale v2 (CPU 640x360, ritaglio): ok. Residui accettati: piccole insenature dove i bacini toccano il fiume; la fascia di riva segue il profilo delle banchine moderne.
  - 16 ott 2026, pod A40 Secure (0,59 $/h, l'unico libero): profilo a 1080p OptiX 1,58 s/fot. (2 campioni 0,98; OIDN 4,75: scartato); anteprima 960x540 media 0,85 s/fot. (il 1941-1960 e' il tratto PIU' veloce, 0,4 s). VRAM massima 2,9 GB: la 5080 da 16 GB basta. 2 contro 8 campioni: identici nel 1938, ma a 2 i grattacieli di vetro del finale sono maculati (rischio sfarfallio): restano 8.
  - Dopo l'anteprima (16 ott, 12:00): `marsh: false` (la fascia di palude sulle rive sembrava lastricato crepato), `land_half_m` 60 km (bordo del mondo all'orizzonte nel finale), camera piu' vicina sul triangolo nei primi 65 s. Provato in locale.
  - Stima render completo a 8 campioni: ~1,8 s/fot. -> ~3,9 h; su 5080 Community (0,39 $/h) video + Shorts ~2,0 $ (~1,75 EUR) se la 5080 e' veloce come l'A40 (probabilmente di piu').
  - 16 ott pomeriggio, corretti in locale prima del render: (1) la campagna diventava citta' fino a 60 km (le curve dei nuclei minori restituivano l'ultimo anno a qualsiasi distanza; ora ogni nucleo vale solo fino alla fine della sua curva): orizzonte verde nel finale; (2) Rotterdam fuori dal triangolo cresceva prima del 1855 (controllo `(cx, cy) == (0, 0)` rimasto dopo lo spostamento del centro): predecessori 357.000 -> 265.000; (3) macchie nere dove la terra chiusa (buffer 45 m) copre i bacini stretti: riempimenti dei bacini 3 cm sopra la terra.
  - `run.sh full` ora fa anche: `<citta>_light.mp4` (960x540, 1,3 Mbit/s, ~55 MB, per la chat) e la copertina (`cover` in city_<citta>.json: camera, obiettivo, anni -> `<citta>_cover_<anno>.jpg` a 32 campioni). `run.sh shorts` fa anche `_short<n>_light.mp4` (~15 MB). Modalita' separata `run.sh cover`. Rotterdam: copertina 1700 | 2026, camera bassa sul fiume verso Kop van Zuid.
  - Prossimo: pod 5080 Community -> `CITY=rotterdam bash run.sh full && CITY=rotterdam bash run.sh shorts`; in chat: light, years.json, copertine, short light -> montaggio (cities.js, cartello 14 maggio 1940), copertina con thumb_city.py (bandiera nl da aggiungere), metadati.
- **Miglioramenti tecnici da fare per la prossima città**: meno foschia nel render (città grigia a metà video); stima tempi realistica = 1,9 s/fotogramma, non 1,1 (la parte centrale è la più lenta); inquadratura dedicata alla copertina con il monumento simbolo in primo piano; niente secondi vuoti all'inizio.
- vidIQ: 20 crediti al giorno; ricerca parole chiave già fatta (sezione sopra).

### Calendario di pubblicazione (deciso da Fabio il 15 ott 2026)
- Video lunghi: mercoledì e domenica alle 16:00 ora italiana (10:00 New York).
- Shorts: i 3 giorni successivi al video lungo, alle 17:00. Nota: gli Shorts del video della domenica cadono lun-mar-mer, quindi il mercoledì escono insieme al video lungo nuovo.
- Madrid: domenica 18 ott 16:00; Shorts lun 19, mar 20, mer 21 alle 17:00.

### Shorts: apertura dal presente (15 ott 2026)
- Primo Short di New York (dal 1609, foresta): 904 visualizzazioni in 4,5 h, ma solo il 40,1% "ha continuato a guardare". Ipotesi: il primo secondo è vuoto.
- Rifatti con 1,5 s di apertura sulla città di oggi ("<CITY> TODAY / NOW WATCH IT GROW FROM <anno>") e poi lo short dal passato: `nyc_short3_v2.mp4`, `madrid_short1_v2.mp4`, `madrid_short3_v2.mp4` (codice `montaggio/hook_shorts.jsx`). Regola per le prossime città: ogni Short che parte dal passato apre con 1,5 s del presente.
- **Regola di ritmo per gli Shorts (Fabio, 15 ott 2026: "quel ritmo è da long video, non da short")**: almeno 5-10 anni al secondo e qualcosa di visibile che cambia ogni 1-2 s; durata sotto i 35 s (meglio 25-30). Le epoche "lente" (villaggio che cresce piano) vanno accelerate di più o tagliate. Rifatti di conseguenza: `nyc_short3_v2.mp4` (5x, 1609→1825, 31 s) e `madrid_short3_v2.mp4` (doppia velocità, 1480→1700, 25 s). `madrid_short1_v2.mp4` (500 anni in 46 s, ~11 anni/s) va bene così. In `run.sh shorts` i passi vanno scelti con questa regola.
- Verifica: confrontare "Ha continuato a guardare" dello Short 2 di New York (parte dal 1929, città già piena) e dei v2 con il 40% del primo.

### New York: dati al cambio titolo/copertina (ven 16 ott 2026, 08:20, ~39 h dalla pubblicazione)
- Base per il confronto: 4.900 impressioni, CTR 2,4%, 268 visualizzazioni, 100 spettatori unici, +1 iscritto, durata media 1:08 (20,9%), mi piace 66,7%. Traffico: home 67%, video consigliati 26% (accanto a "EVOLUTION OF NEW YORK | 3D CITY TIMELAPSE" e "SAN FRANCISCO 3D TIMELAPSE"), ricerca 1,5%. USA 62%. Dispositivi: cellulare 34%, computer 26%, TV 25%, tablet 14%.
- Curva di fidelizzazione: crollo nei primi 30 s (37% a 0:30, "in linea con il tipico" per YouTube), poi quasi PIATTA intorno al 20-25% fino alla fine, piccolo rialzo verso 4:50. Conclusione: il contenuto tiene, l'inizio perde la gente. Conferma la regola "niente secondi vuoti all'inizio" e l'apertura sul presente.
- Cambio fatto alle 08:20 di venerdì (non alle 17): titolo "Evolution of New York City in 3D | 400 Years, Every Real Building (No AI)" + copertina v2. Confronto CTR domenica: Analytics → Copertura, date 14-15 ott contro 16-17 ott.

### Idea titoli da provare (vidIQ, 16 ott 2026)
- vidIQ ha proposto per New York titoli in stile diverso: "Every Building in NYC Appears the Year It Was Built" (97), "I Rebuilt 400 Years of New York City in 3D (No AI)" (96). Lo stile in prima persona / "ogni edificio nel suo anno" potrebbe rendere meglio in home e consigliati; "Evolution of…" aiuta la ricerca. Da provare su UNA città futura come confronto (non su New York, già cambiato il 16 ott).
- Previsione vidIQ per New York: ~750 visualizzazioni a 14 giorni. Il "28,8× il percorso tipico" non ha significato con un solo video sul canale. Il consiglio "pubblica di lunedì" è generico: calendario invariato.

### Ritmo dei video lunghi (17 ott 2026)
- Fabio trova lenti anche i lunghi (New York e, in parte, Madrid: stessa durata 5:27, stessa scansione del tempo). I dati di New York però dicono che il problema dimostrato è l'INIZIO (crollo nei primi 30 s); dopo, la curva è piatta.
- Regola per le prossime città (Rotterdam compresa): a metà video almeno un evento visibile ogni 20-30 s (cartello, cambio di camera, zona che esplode, grattacielo che sale in primo piano); evitare tratti di 1-2 minuti di crescita uniforme e grigia (Madrid 2:30-4:30).
- Verifica: confrontare la curva di Madrid con quella di New York nel tratto 2:30-4:30. Se Madrid scende lì, il ritmo centrale va rivisto anche nella durata.

### Shorts: risultato del confronto (17 ott 2026)
- Short 1 New York (parte dal 1609, foresta): 40,1% "ha continuato a guardare", 1.600 visualizzazioni in 42 h, curva: crollo nei primi 10 s poi piatta ~30-38%.
- Short 2 New York (parte dal 1929, città già piena): 39,3%, 1.100 in 17 h. => L'apertura vuota NON era l'unica causa: l'ipotesi "apertura sul presente" NON è confermata, trattarla come da verificare.
- Ipotesi rimaste: (a) ritaglio dal video orizzontale = immagine morbida e lontana, edifici-puntini sul telefono; (b) nessun soggetto nel primo secondo; (c) 40% come livello base di questo tipo di immagine.
- Prossimi test già in calendario: Short 3 v2 New York (apertura + 5x + 31 s, ancora ritagliato); Shorts Madrid (verticali NATIVI, camera vicina). Se anche Madrid resta ~40%: provare Shorts con inquadratura bassa tra gli edifici / grattacielo che sale in primo piano, renderizzata apposta.

### Analisi di 3 concorrenti (17 ott 2026, video caricati da Fabio, misure con ffmpeg/OCR)
Video: Latos Charts "AMSTERDAM - 3D Timelapse" (11:57, stesso formato nostro), Timelapse Professor "The Entire History Of Rome - 3D Timelapse (NO AI)" (10:56), Restored Timeline "Evolution of CHICAGO | Fixed-Camera" (12:15, AI).

| | Amsterdam | Roma | Chicago (AI) | New York | Madrid |
|---|---|---|---|---|---|
| Durata | 11:57 | 10:56 | 12:15 | 5:27 | 5:27 |
| Movimento visivo (diff. media ogni 0,5 s) | 21,7 | 18,2 | 11,2 | **2,7** | 8,8 |
| Saturazione colori (0-255) | 159 | 175 | 66 | **57** | **49** |
| Schede evento | ~38, una ogni ~19 s, 3 nei primi 20 s | una ogni ~15-20 s | anno grande + barra | 13, una ogni ~25 s | 15 |
| Primi 30 s | battuta scritta a 0:10 ("IT'S A SWAMP"), diga e villaggio entro 0:15, camera bassa | **gancio narrato** (voce umana): "la città più grande del mondo... poi se ne andarono tutti e le mucche entrarono nella piazza" + titolo a 0:16 | scena che cambia ogni ~5 s (stagioni, animali, luce) | foresta vuota fino a 0:30 | villaggio dal secondo 6 |
| Audio | musica + effetti sonori sugli eventi (raffiche a banda larga: fuoco, battaglie, campane) | voce nei primi ~45 s, poi musica | musica + ambienti che cambiano ogni ~10 s | solo musica | solo musica |
| Altro | stemma + nome dell'epoca, contatore abitanti, battaglie animate (navi, soldati, aerei), testi brevi e spiritosi | ritratti dei sovrani, monumenti etichettati (Pantheon, Fontana di Trevi), "Part 1/2..." | barra di avanzamento in alto | HUD anno/epoca/popolazione | idem |

Conclusioni (in ordine di resa/costo):
1. **Colori**: i nostri render sono slavati (saturazione ~1/3 dei concorrenti 3D): erba verde viva, acqua blu, tetti arancio, meno foschia. Costo basso (materiali + grading).
2. **Più eventi e più brevi**: una scheda ogni 15-20 s, titolo di 2-3 parole + una riga spiritosa; 2-3 eventi nei primi 20 s.
3. **Monumenti riconoscibili ed etichettati** quando compaiono (etichetta che punta al monumento). Richiede modelli o almeno sagome dei 5-10 monumenti simbolo della città.
4. **Effetti sonori sugli eventi** (fuoco, battaglia, campane, sirene) sotto la musica. Costo basso (montaggio).
5. **Gancio nei primi 15 s** con un contrasto narrativo (Roma: "la città più grande del mondo... poi le mucche"). Senza voce: in testo grande.
6. Camera più bassa e obliqua sul punto dove succede l'evento (Amsterdam, Roma).
La durata di 10-12 minuti arriva DOPO: loro la riempiono con 38+ eventi; con i nostri 13-15 un video più lungo sarebbe più vuoto.

### Rotterdam: cosa cambia dopo l'analisi dei concorrenti (17 ott 2026, prima del render)
- **Ritmo**: la regia toglie il "tratto lungo e uniforme". Prima: 1340-1870 in 160 s e 1870-1938 in 40 s. Ora: 1340-1650 in 50 s (triangolo, poi Waterstad), **1650-1850 in 15 s** (la citta' resta nelle mura per due secoli), **1850-1938 in 134 s** (Waterproject, porti, la citta' esplode con la camera larga). Il 1940 resta agganciato alla musica (3:27). Shorts ricalcolati (26-30 s).
- **Colori**: misurati sui fotogrammi di prova, saturazione 50-61 (concorrenti 159-175). Provate in locale 3 varianti di render: meno foschia + AgX contrasto molto alto (peggio, slavato) e trasformazione Standard (bruciato, verde fluo). **Si corregge al montaggio, non nel render**: saturazione x1,7 e contrasto x1,06 (ffmpeg `eq=saturation=1.7:contrast=1.06`) -> ~100, piu' vivo senza diventare finto. Vale anche per copertina e Shorts. `build_render.py` ora accetta `view_transform`, `look`, `exposure` nella config citta' (default invariati).
- Eventi ogni 15-20 s, monumenti etichettati, effetti sonori, gancio scritto nei primi 15 s: tutto al montaggio, non serve rifare il render. Candidati Rotterdam: 1340 diritti di citta', 1572 sacco spagnolo, 1602 VOC, Waterstad, 1866-72 Nieuwe Waterweg, 1898 Witte Huis (primo grattacielo d'Europa, e' nei dati BAG), porti 1905-1930, 14 maggio 1940, 1953 Lijnbaan, 1960 Euromast, 1984 case cubiche, 1996 Erasmusbrug, 2013 De Rotterdam, 2014 Markthal, 2022 Zalmhaven.


### Shorts: terzo dato (17 ott 2026, sera)
- Short 3 v2 New York (apertura "NEW YORK TODAY" + skyline 1,5 s, poi foresta 1609, 5x, 31 s): **27,7%** "ha continuato a guardare" dopo ~4,5 h (circa 460 nel feed). Peggio di Short 1 (40,1%) e Short 2 (39,3%).
- Ipotesi: mostrare subito il risultato toglie curiosità + stacco deludente su foresta + blocco di testo grande su immagine ritagliata/morbida. L'apertura sul presente è quindi PEGGIORATIVA su New York; resta in verifica su Madrid (lun Short 1 v2 con apertura, mar Short 2 senza, mer Short 3 v2 con apertura; tutti verticali nativi).
- Per ora gli Shorts portano pochi iscritti (2-3 in tutto); il video lungo ne ha portati 3 con 340 visualizzazioni. Priorità ai video lunghi (colori, eventi), non inseguire gli Shorts.

### PROPOSTA PER LA CHAT DI ROTTERDAM: Shorts "su un evento" (18 ott 2026, OK di Fabio)
Gli Shorts attuali (anche quelli nativi di Madrid) usano la STESSA camera e gli stessi anni del video lungo, solo in verticale e accelerati. I due Shorts di New York stanno a ~40% "ha continuato a guardare" sia partendo dal vuoto sia dalla città piena: il problema probabile è che non succede NIENTE DI PRECISO, non l'anno di partenza.
Test da fare su Rotterdam (stesso costo pod degli Shorts attuali):
- **Short A (controllo)**: il veloce di tutta la città, come Madrid Short 1.
- **Short B (evento)**: SOLO il 14 maggio 1940. Camera bassa e vicina sul centro (Coolsingel / Laurenskerk), ferma o in lenta rotazione, regia propria (NON la camera del lungo). Struttura 20-30 s: scritta-domanda nel primo secondo ("Where did Rotterdam's center go?") → centro intatto 1938 → scompare (1940) → vuoto → rinasce 1946-1960 → rimando al video lungo. Circa 500-700 fotogrammi.
- **Short C (evento)**: "Manhattan on the Maas": Kop van Zuid / Wilhelminapier 1990→2026 (Ponte Erasmus 1996, De Rotterdam 2013 e le altre torri). Camera bassa sul fiume, torri che salgono una dopo l'altra. Domanda iniziale tipo "How did Rotterdam get a skyline?". 20-30 s. (Alternativa se le torri sono poche nei dati: i bacini portuali scavati, terra che diventa acqua, da harbours.json.)
- Ordine di uscita: A, B, C a un giorno di distanza. Con due Shorts "evento" contro uno di controllo il confronto è più solido. Se B e C battono A di 10+ punti su "ha continuato a guardare", gli Shorts "su un evento" diventano la regola per tutte le città.
- NON usare l'apertura sul presente (peggiorativa su New York: 27,7%).
- Regola per scegliere gli eventi: solo momenti in cui gli EDIFICI cambiano davanti alla camera (torri che salgono, quartieri che appaiono o scompaiono). Eventi che il render non mostra (incendi, assedi) non funzionano come Short.

### Rotterdam: Shorts A/B/C pronti (18 ott 2026, chat di Rotterdam)
- `regia_rotterdam_shorts.py` -> `schedule_rotterdam_shortB.json` (26 s, 624 fot.) e `schedule_rotterdam_shortC.json` (27 s, 648 fot.). Provati in locale (CPU, verticale 360x640).
- **B** (14 maggio 1940): camera propria a 1,9 km dal centro, 750 m di quota, rotazione lenta -8/+4 gradi. Anni: 1936-1939,9 (0-6 s, domanda scritta nel primo secondo) -> scompare 7-9,5 s -> vuoto fino a 13 s -> rinasce 1945-1962 (13,5-24 s) -> fermo 2 s. `--bin 2` (i quartieri ricostruiti compaiono ogni ~1,3 s).
- **C** ("Manhattan on the Maas"): camera sull'acqua a ovest di Wilhelminapier, da 1,7 a 1,4 km, obiettivo 50 mm, torri al centro del verticale con i riflessi sotto. 1988-2026 in 22 s (~1,6 anni/s: piu' lento della regola dei 5 anni/s, ma ogni 2-4 s sale una torre). `--bin 1`. Torri nei dati: 1997, 2000 (122 m), 2005 (140 m), 2010 (158 m), 2011 Maastoren (165 m), 2013 De Rotterdam (152 m), 2017. Il ponte Erasmus NON c'e' (niente ponti nel modello): non nominarlo nelle scritte. Zalmhaven (2022, 203 m) resta fuori quadro.
- **A** (controllo): tutta la storia con la camera del lungo, passo 11 (29 s).
- `run.sh shorts` ora legge [nome, primo, ultimo, passo, regia?, bin?]: con la regia propria lo Short usa la sua camera. Uscite: `rotterdam_shortA.mp4`, `_shortB`, `_shortC` (+ `_light`).

### Rotterdam: montaggio preparato durante il render (18 ott 2026)
- `montaggio/rotterdam_overlay.jsx`: titolo nel riavvolgimento (0-5 s), **gancio scritto** 5,8-15 s ("EUROPE'S BIGGEST PORT / started as a dam on a muddy stream." poi "IN 1940 IT LOST ITS HEART / in a single afternoon. Watch what came back."), **22 schede a tempo** (una ogni ~15 s, titolo 2-3 parole + una riga; 14 maggio 1940 sobria), **etichette sui monumenti** calcolate con la stessa camera del render (`labels_cam.py` + `landmarks_rotterdam.json`: Witte Huis, City Hall, Laurenskerk, Euromast, Cube Houses, Delftse Poort, Maastoren, De Rotterdam, Zalmhaven, Van Nelle); nel silenzio dopo il bombardamento: "City Hall · survived", "Laurenskerk · survived". HUD con dati di Rotterdam in `cities.js`. Anni dal `schedule_rotterdam.json` (`years_rotterdam.json` uguale a quello del pod).
- **Effetti sonori sintetici** (`montaggio/sfx_rotterdam.py`): campane 0:16, sirena di nave 1:27, sirena antiaerea 3:19 ed esplosioni lontane nel calo 3:27-3:31, sotto la musica (+0,3/+2,6 dB di media nei tratti). Audio pronto: `rotterdam_audio.m4a` (con effetti) e `rotterdam_audio_solo_musica.m4a`.
- `monta_rotterdam.bat`: full + overlay + audio, saturazione 1,7 e contrasto 1,06. `monta_rotterdam_shorts.bat`: 3 Shorts + loro overlay + musica (A dal 4:00, B dal 3:20 così il silenzio cade sul centro vuoto, C dal 3:57).
- `montaggio/rotterdam_shorts.jsx`: overlay trasparenti 1080x1920 per A/B/C (domanda dal primo fotogramma, anno grande, rimando finale "FULL STORY ON OUR CHANNEL"; in C etichette su Maastoren e De Rotterdam).
- `thumb_city.py`: aggiunta bandiera olandese (`--flag nl`). `metadata_rotterdam.md` pronto (titolo, descrizione con capitoli, tag, Shorts).


## Scansione onde (18 ott 2026, vidIQ ~35 crediti) — scelta della città dopo Rotterdam
- "city evolution" 35.600 ricerche/mese, **+65% in 30 giorni**; invece "city evolution timelapse" -29%, "fixed camera timelapse" -24%, "ai timelapse" -38%. Lettura [Likely]: la domanda per l'argomento cresce, quella per il formato AI a camera fissa cala. Vantaggio per noi (3D, dati veri, No AI).
- Video che sfondano nell'ultimo mese: Kuala Lumpur (Epoch, AI) 162K; Pripyat (EraLapse) 82K; Hong Kong 77K; Wellington 65K; San Pietroburgo 60K; Tenochtitlan (Timelapse Professor, 3D No AI, 3.290 iscritti) 27,6K in ~9 giorni.
- **Attenzione**: "3D Timelapse – New York (1600–2026)" (canale polacco con 1.150 iscritti, 3D, non AI) ha 96K in 3 settimane. Il nostro New York è a ~390. L'argomento funziona, quindi il nostro problema è copertina/titolo/primi secondi, non la città.
- Candidati: **Chicago** — "evolution of chicago" 4.600/mese, "chicago timelapse" 5.100 (concorrenza 16), "history of chicago" 12.400. Unico video di crescita: Restored Timeline (AI) **3,5 milioni**. Nessuna versione 3D con dati veri. Pubblico USA, incendio del 1871 come evento forte. Dati: footprints comunali con year_built (da verificare: molti zero?). **Barcellona** — "barcelona evolution" 5.400 con concorrenza 7, stessa pipeline di Madrid (catasto), ma Epoch l'ha già fatta. **Amsterdam** — 5.100 con concorrenza 10, stessa pipeline di Rotterdam (BAG), ma c'è Latos (3D forte).
- Raccomandazione: **Chicago** dopo Rotterdam (domanda dimostrata da 3,5M e nessun concorrente con dati veri); Barcellona come riserva veloce se i dati di Chicago non reggono.
- Scansione automatica ogni lunedì mattina (attività programmata): outliers del mese + ricerca parole chiave sulle città candidate, rapporto breve.

## Analisi "3D Timelapse – New York (1600–2026)" (canale polacco, 1.150 iscritti, 96K in 3 settimane) — 18 ott 2026
- Misure (stesso metodo della tabella concorrenti): movimento 9,4 (il nostro NYC 2,7), saturazione 90 (nostro 57), contrasto 26,6, audio -23,7 LUFS, 8:01. Sottotitolo: "An illustrative reconstruction · real modern building locations" → NON ha dati veri per edificio: **i dati veri non sono cio' che porta visualizzazioni, lo spettacolo si'**.
- 0:00 camera a terra tra gli alberi con le capanne Lenape; 0:06 arrivano le navi; 0:21 gia' una citta' a griglia; **0:46 Grande Incendio del 1835 con fiamme, di notte**.
- **Monumenti modellati e inquadrati da vicino mentre salgono**, con scheda "UNDER CONSTRUCTION <anni>": Central Park, Statua della Libertà, Flatiron, Williamsburg Bridge, Chrysler, Empire State, George Washington Bridge, Torri Gemelle, One WTC. La camera va da un monumento all'altro (ogni 15-30 s).
- **Finale di notte**: dal 1984 la citta' si spegne e si accendono le finestre; il lato destro della copertina e' la citta' illuminata di notte.
- HUD: PIL che sale (dollari, top sinistra), popolazione (top destra), anno, bandiera + epoca (basso sinistra).
- Copertina: lato sinistro a livello del terreno con capanne (scala umana), lato destro notte con luci, "1600 → 2026" con 2026 giallo, "New York" enorme bianco in basso.
- Da adottare (in ordine di impatto): (1) monumenti simbolo modellati (anche semplici) + camera che ci va vicino quando salgono; (2) finale notturno con finestre accese (emissione nel render, ultimi 30-40 s) e copertina notturna; (3) apertura a terra con oggetti a scala umana ed evento spettacolare entro 45 s; (4) camera sempre in movimento e varia (alto/basso/vicino); (5) contatore che sale veloce (popolazione già c'e'; il PIL e' un'idea).
- 18 ott, deciso con Fabio: il render di Rotterdam era quasi finito → NON si rifà. Per Rotterdam solo ciò che si fa al montaggio: etichette dei monumenti agganciate alla posizione 3D (proiezione con le chiavi camera di schedule_rotterdam.json + mm), bagliore/fumo sovrapposto sulla zona distrutta il 14 maggio 1940, contatori, saturazione x1,7. Il modello completo (monumenti modellati + camera vicina, finale notturno con finestre accese, apertura a terra con evento entro 45 s) parte da **Chicago**: incendio 1871, Water Tower (sopravvissuta all'incendio), Home Insurance Building 1885 (primo grattacielo), Willis/Sears 1973, John Hancock 1969, Trump Tower, St. Regis.

### Rotterdam: migliorie di montaggio dalla chat madre (18 ott 2026, pomeriggio)
- Etichette monumenti: verificate sul light vero (Euromast, De Rotterdam, City Hall, Laurenskerk cadono sulla cima dell'edificio). **Erasmusbrug NON etichettata**: il ponte non e' nel modello, l'etichetta punterebbe sull'acqua.
- **Fuoco e fumo** sul 14 maggio 1940 (`Fire` in rotterdam_overlay.jsx): contorno della zona e 10 focolai proiettati con la camera (`bomb_rotterdam.json` da `labels_cam.py` + `bomb_points.json`); bagliore 206,8-213,6 s, fumo che sale 207,4-219 s.
- **Contatori**: "BUILDINGS STANDING" in alto a destra (reali + ricostruiti per anno, `buildings_rotterdam.json`: 295 nel 1340, 189.365 nel 1939, 268.466 nel 2026); "HOMES DESTROYED" 0 -> 24.978 nella scheda del 14 maggio.
- years.json del pod identico a years_rotterdam.json (calcolato dalla regia).


### Rotterdam: tempi del pod (18 ott 2026, RTX 5080 Community 0,39 $/h)
- Lungo: 7.839 fotogrammi a 1,69 s = 3,75 h (13.518 s con mp4, light e avvio).
- Shorts verticali: **A** (camera del lungo, bin 4) 701 fotogrammi a 1,77 s = 22 min; **B** (camera propria, bin 2) 624 a **3,59 s** = 38 min; **C** (camera propria, bin 1) 648 a circa 4-5 s = circa 50 min (stima).
- Totale circa 5,7-6 h, cioè circa 2,2-2,3 $: **di nuovo sopra il tetto di 2 €**, come per Madrid. Gli Shorts nativi costano circa 0,8 $, cioè il 35% del pod per 75 secondi di video.
- Causa probabile [Likely]: i bin per anno più fini (`--bin 2` per B, `--bin 1` per C) moltiplicano gli oggetti-chunk, e Blender li ricalcola a ogni fotogramma. In più la camera bassa e vicina vede più geometria. Non è la risoluzione: 1080×1920 ha gli stessi pixel di 1920×1080.
- **Regole per la prossima città**:
  1. Shorts con il bin del lungo (4), salvo che servano anni veramente fini: per B il 1940 è un salto secco, quindi bin 4 bastava.
  2. Fare un profilo di 20 fotogrammi di ogni Short prima del lancio completo.
  3. Mettere nel conto 3,5-5 s a fotogramma per gli Shorts con camera propria.
  4. Se il budget è stretto, fare gli Shorts di controllo (tipo A) ritagliati dal lungo, che sono gratis, e nativi solo quelli "su un evento".

## 19 ott 2026 — LA NICCHIA SI STA INTASANDO (verifica vidIQ youtube_search, 15 crediti)
- **Madrid** (nostro: 5 impressioni in 15 h, indicizzato 4° per "evolution of madrid 3d"): Meridian Timelapse "Evolution of Madrid | 3D City Timelapse 852–2026" uscito il **15 ott** (3 giorni prima di noi), 15.161 visualizzazioni, 304/ora, 469 iscritti, 9:37, 19 capitoli. Anche TimeLess History (6 ott, 382) e Historical Algorithm. Causa probabile del blocco: lo spazio "Madrid 3D" era già preso da un video che sta funzionando; non è un problema tecnico.
- **Chicago: SCARTATA.** Nelle ultime 3 settimane almeno 8 video 3D: Cornerstone Timelapse 99K (2 ott), nobodycares 8K, MetroRewind 5K, DataShark, TIME TALES, City Strata, Chronopolis, e "Everything's OK" che usa ESATTAMENTE i nostri dati (Chicago Data Portal year_built) con 10 visualizzazioni. La scansione outliers del 18 ott non li aveva visti: per ogni città candidata serve youtube_search "<città> 3D timelapse" con publishedAfter = ultimi 45 giorni.
- **Rotterdam**: "History Of" (38 iscritti) ha pubblicato il 17 ott un Rotterdam 3D con 3DBAG + brandgrens 1940 (stessi dati nostri), 379 visualizzazioni; TimeLoop ha fatto Delft. Siamo il terzo arrivato (dopo Epoch AI 40K).
- Molti canali nuovi usano lo stesso schema nostro (Blender, dati aperti, "Which city should we build next? Tell us in the comments."): pipeline costruite con assistenti AI, decine di cloni. **I dati veri non distinguono più.** Vincono spettacolo (monumenti, fuoco, notte) e arrivare per primi su una città.
- Modello da studiare: **Cornerstone Timelapse** (3.640 iscritti): Las Vegas 739K in 12 giorni (4.276/ora), Chicago 99K. Las Vegas = demolizioni/implosioni + Strip di notte.
- Regola nuova: (1) la città si sceglie con youtube_search degli ultimi 45 giorni, il giorno prima del render; (2) di nuovo il giorno prima della pubblicazione; (3) se nel frattempo esce un concorrente forte sulla stessa città, si valuta di anticipare o cambiare titolo/copertina per distinguersi.
- **DECISO 19 ott (Fabio)**: Rotterdam esce giovedì 22 come previsto (non slitta). **Quarta città: COPENAGHEN**, libera in 3D, budget pod fino a 4,5 €, uscita obiettivo martedì 27 ott, primo video col modello completo (monumenti, fuoco 1728/1795/1807, notte). Piano completo per la nuova chat: **`PROSSIMA_COPENAGHEN.md`**.

## Ritmo dei concorrenti (19 ott 2026)
- **Cornerstone Timelapse** (canale nato il 2 ott, 3.640 iscritti): Chicago 2 ott (100K), Las Vegas 7 ott (739K), **New York 11 ott (1,03 MILIONI in 8 giorni, 16.390/ora)**, Los Angeles 15 ott (123K). Un video lungo ogni 4-5 giorni, **8-9 minuti**, **ZERO Shorts**. Titoli tutti uguali: "EVOLUTION OF <CITY> | 3D CITY TIMELAPSE (<anno>–NOW)".
- Latos Charts (101K iscritti): Lisbona 29 set, Barcellona 1 ott, Amsterdam 4 ott → ogni 2-3 giorni, 9-12 minuti.
- Epoch Timelapse (AI): ogni 2-3 giorni. Meridian, TIME TALES, Everything's OK: anche uno al giorno, ma con poche visualizzazioni.
- Lezioni: (1) la velocità non è ciò che separa vincitori e perdenti (i cloni giornalieri restano a centinaia); (2) gli Shorts non servono per esplodere; (3) i vincitori durano 8-10 minuti (noi 5:27); (4) "siamo in ritardo" non regge: Cornerstone è nato 12 giorni prima del nostro New York e ha fatto 1 milione sulla stessa città.
