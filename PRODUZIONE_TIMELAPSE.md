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
