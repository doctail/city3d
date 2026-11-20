# Follower City — piano tecnico (solo analisi, nessun pod, nessun costo)

Etichette: [Certain] = misurato/letto nei file del repo; [Likely] = deduzione solida; [Guessing] = stima da verificare con una prova. Blender NON è installato in questo container (ci sono solo ffmpeg e node 22), quindi NESSUN dato di render di questo progetto è misurato.

## 0. Cosa c'è già e cosa è riusabile
- [Certain] `build_render.py` (1583 righe) costruisce la scena Blender da JSON (edifici estrusi con bmesh, materiali a nodi, camera da `schedule_*.json`), renderizza con Cycles + OptiX, 8 campioni, JPG 95, fotogrammi saltati se già presenti (ripresa).
- [Certain] Regole imparate sul campo (PRODUZIONE_TIMELAPSE.md): nessun keyframe su materiali/datablock (ogni animazione di dati costringe Cycles a risincronizzare tutta la scena: 13-18 s a fotogramma); la crescita si fa con scala/posizione di oggetti; oggetti numerosi = chunk merged per anno; troppi chunk (bin fini) fanno salire il costo da 1,7 a 3,6 s/fotogramma; 1080x1920 ha gli stessi pixel di 1920x1080.
- [Certain] Misure Year Built (RTX 5080 Community 0,39 $/h, scena con 100K+ edifici, foschia, camera mobile): 1,0-1,9 s/fotogramma a 1080p. Pod A40 0,59 $/h. Rischio noto: pod 5080 con `cuInit=999` (controllo ctypes in 2 s prima di clonare).
- [Certain] Stile già sperimentato per Copenaghen: low-poly "giocattolo", colori netti, niente foschia; note dicono di valutare Eevee/stile semplificato per costare meno.
- [Certain] Montaggio: Remotion (`montaggio/hud.jsx`, `cities.js`, overlay `.webm` trasparenti) + `.bat`/ffmpeg; kit CLI in `kit/` (qa, regia, thumb). Il HUD con contatore, cartelli e titoli si riusa quasi uguale (contatore follower al posto degli anni).
- Riusabile: pipeline pod (`run.sh`, ripresa, JPG, gputest), schema `schedule_*.json` per camera a keyframe, overlay Remotion, `kit/atlante/strumenti/nodum_mcp_curl.py` per Nodum. Da NON riusare: dati urbani reali, OSM, DEM, storia: qui la città è sintetica.

## 1. Città persistente che cresce
Principio: la verità è un JSON, non un .blend. [Likely] Ricostruire la scena da JSON ogni giorno è più sicuro (nessuna deriva, diffabile in git, riproducibile) e con instancing costa secondi, non minuti.
- `city_state.json` (versionato nel repo, un commit al giorno): `followers_total`, `day`, `seed`, `plate` (raggio/anello attuale), `lots[]` (id, cella, anello, tier, archetipo, variante, colore, rotazione, `born_day`, `source`: "follower" | "comment" | "milestone", `label` opzionale per i palazzi da commento), `tier_counter` (follower accumulati verso il prossimo tier), `thresholds_done[]`.
- Allocatore deterministico: celle di una griglia esagonale/radiale che si riempie dal centro verso fuori (spirale), strade e parchi riservati in un piano regolatore fissato dal seed. Il giorno N aggiunge solo lotti nuovi; i vecchi non si spostano mai (continuità visiva tra video).
- Regola di conversione: N nuovi follower -> N unità di crescita, convertite in lotti via tabella soglie (es. 1 follower = casetta 2 piani, 10 = palazzo, 100 = isolato, 1.000 = parco/piazza, 10.000 = monumento). Le unità si accumulano nel `tier_counter`, così nessun follower va perso e i blocchi grandi appaiono alla soglia vera. I tier sono dati in `tiers.json`, non nel codice.
- Script giornaliero `grow.py` (Python puro, senza bpy, testabile in questo container): legge stato + `followers_today` (+ commenti approvati), scrive il nuovo stato e un `day_plan.json` (lotti nuovi con ordine e tempi di comparsa). Poi `render_day.py` (bpy, headless) costruisce la scena da stato + piano e renderizza.
- Parte vecchia = un solo mesh merged per zona (cotto una volta, mai ricalcolato per fotogramma); parte nuova = oggetti separati animati. Opzionale [Likely]: cache `base_dayN.blend` solo come ottimizzazione, mai come fonte di verità.
- Geometry Nodes: utile per UNA cosa, istanziare gli archetipi su punti (Instance on Points con attributi scala/colore/variante). Per l'animazione di comparsa preferisco NON usarli (vedi sotto: ricalcolo per fotogramma).

## 2. Stile visivo e camera
- Clay/low-poly su fondale monocromo (tinta unita scelta dal canale, non il giallo del popcorn per non essere un clone; palette Ledger of Cities). Materiali: un solo shader diffuso con colore per istanza (attributo), nessuna texture; ombra morbida a contatto + luce direzionale unica; piatto/isola come base con bordo spesso.
- Il "contenitore" è la piastra-isola: a ogni soglia l'isola si allarga di un anello (come piatto -> ciotola nel popcorn) e la camera si allontana in una mossa dedicata (ease, 1-2 s) con un hit sonoro.
- Camera: schedule a keyframe come in `schedule_*.json` (riuso), raggio di inquadratura = bounding della città x margine, inclinazione fissa 35-45°, orbita lenta. Formato 9:16: città compatta e tondeggiante, non allungata.
- Il fondale monocromo è un gran vantaggio di costo: niente cielo, niente foschia, niente luce ambiente complessa. Eventuale rendering con alpha e fondale nel montaggio [Likely] (permette anche varianti colore per Shorts).

## 3. Animazione di comparsa
Raccomando animazione procedurale "pop-up" con caduta finta, non rigid body.
- Per ogni lotto nuovo: scala Z 0 -> 1 con overshoot elastico + piccolo squash, oppure caduta dall'alto con rimbalzo smorzato calcolato analiticamente (formula, nessuna simulazione). Keyframe solo su trasformazioni dell'oggetto, mai su materiali [Certain: regola già verificata nel repo].
- Perché non rigid body: [Likely] il popcorn ha bisogno di caos fisico, qui palazzi che si impilano a caso rovinerebbero la leggibilità della città e sarebbero non deterministici; il bake costa tempo e il risultato cambia a ogni run, il che rompe la continuità del JSON. Eccezione facoltativa: coriandoli/polvere di contorno al pop (pochi oggetti, bake corto).
- Quando i nuovi sono molti (centinaia/migliaia): si animano a gruppi (onde per anello, N palazzi per "pop"), mai più di ~100-200 oggetti animati per fotogramma; il resto compare in batch con un solo evento sonoro. Il tempo del video resta fisso (regole canale), cambia la densità dei pop.
- Pochi follower nel giorno (es. 3): video breve ma con "ripasso" della città (camera che gira intorno) e contatore; scelta di regia da fissare, non una domanda al proprietario.

## 4. Tempo e costo di render per video giornaliero (1080x1920)
Base: video 25 s a 30 fps = 750 fotogrammi (20-45 s -> 600-1350). Stessi pixel di un 1080p [Certain].
- Cycles + OptiX, 8-16 campioni, scena semplice: [Guessing] 0,3-0,8 s/fotogramma su RTX 5080/4090 (la scena Year Built, molto più pesante, fa 1,0-1,9 s [Certain]). Quindi 750 fotogrammi = 4-10 min di render [Guessing].
- Costo pod per giorno: render + avvio/clone/costruzione scena (10-15 min [Likely]) ≈ 15-25 min a 0,39 $/h ≈ 0,10-0,17 $/video; mese ≈ 3-5 $ [Guessing, da misurare con una sola prova]. Avvio pod domina il costo, non il render: conviene rendere in batch più giorni per accensione solo se il flusso lo permette (decisione del proprietario, non la propongo come scadenza).
- Eevee (Blender 4.2+ "Next"): [Likely] 0,05-0,2 s/fotogramma e look clay più che sufficiente, MA richiede OpenGL/Vulkan, su pod headless è un rischio non verificato (finora il kit usa solo Cycles+OptiX) [Guessing]. Sul PC del proprietario Eevee funzionerebbe sicuramente con GPU e costo zero.
- Locale del proprietario [Likely]: 0 $, ma serve Blender installato e il suo PC acceso; il `.bat`/cmd di montaggio esistente va già sul suo PC. Opzione ibrida: render su pod, montaggio locale (come Year Built).
- Prova decisiva prima di ogni scelta: scena di test locale (CPU, 5 fotogrammi, 640x1138) -> secondi/fotogramma + conteggio oggetti; poi UNA sessione pod di profilo (6 min) con GO scritto, come da kit. Nessuna cifra di questo paragrafo è misurata.
- Audio: pop, hit di soglia, musica: libreria `kit/music`, sound design in ffmpeg/Remotion (costo zero).

## 5. Richieste dai commenti (palazzo speciale)
Costo basso = catalogo, non modellazione su misura.
- Catalogo di 30-60 archetipi speciali pre-modellati (faro, biblioteca, ristorante, stadio, torre radio, castello, serra, ecc.) con varianti di colore. Un commento ("make me a pizza place") viene mappato a un archetipo (parole chiave + classificazione LLM economica, solo a fine giornata, in batch), con lista bianca e filtro di moderazione (niente nomi di persone private, marchi, simboli protetti o d'odio).
- Il nome dell'autore NON è testo 3D (costoso e rischia glitch): va nel montaggio come cartellino overlay Remotion agganciato alla posizione proiettata del palazzo (coordinate calcolate da bpy: `world_to_camera_view`) e salvato in `label` nello stato.
- Eventuali richieste fuori catalogo: archetipo composto (base + tetto + insegna dai pezzi esistenti); modello nuovo solo se se ne ripetono molte richieste e va a finire nel catalogo (costo ammortizzato).
- Limite per video (es. 3-5 speciali) per mantenere leggibile il video; gli altri passano al giorno dopo, registrati nel JSON (`queue`).
- Commenti letti con strumenti esistenti (vidIQ comment_insights/video_comments), costi dichiarati in una riga e registrati nel LEDGER come da regole.

## 6. Scala a 10K e 100K follower
- 10K edifici: [Likely] nessun problema con instancing (12-20 archetipi x attributi di colore/scala) e merge per zona; Year Built regge già oltre 100K edifici con geometria più complessa [Certain].
- 100K: tre leve. (a) LOD per distanza: con la camera lontana i lotti più esterni diventano box/prisma semplici o una mappa di densità sul suolo; (b) culling per inquadratura (non costruire ciò che il frustum non vede) e niente oggetti sotto 1 px; (c) quartieri a "ghost" cotti una volta (un mesh per distretto, rigenerato solo quando cambia). Memoria: [Likely] pochi GB, il Year Built ha misurato 2,9 GB di VRAM max con scena molto più grande.
- La narrazione cambia con la scala: a 10K la città è una metropoli, la camera passa a vista "mappa", i tier salgono (1 palazzo = 100 follower) e le singole comparse diventano ondate; ciò mantiene il tempo di render circa costante (conta il numero di oggetti animati, non il totale) [Likely].
- Il piano regolatore (anelli/distretti) va dimensionato fin dall'inizio per 100K lotti, per non dover mai spostare edifici già visti.

## 7. Differenza da una copia del popcorn
- Persistenza: il popcorn si resetta, la città si accumula tra i video; chi segue vede la "stessa" città crescere (serialità, ragione per iscriversi e tornare).
- Identità del canale: Ledger of Cities, ogni follower è una riga del registro (nome/ID nel libro mastro, visibile nel cartellino); le soglie rimandano a tipi di città/epoche del canale (ponte con Year Built).
- Partecipazione: il commento diventa un luogo con il nome dell'autore nella città, non solo un oggetto casuale.
- Struttura visiva propria: isola-piastra che cresce ad anelli, palette e fondale diversi dal giallo di @popcornbillionproject, soglie e suoni propri. Mantenere solo il meccanismo generico (contatore + crescita), non copiare asset, suoni o titoli.
- Rischio [Likely]: il popcorn vince sul caos fisico "soddisfacente" (ASMR); la città è più ordinata, quindi serve sound design forte per ogni comparsa e momenti di soglia spettacolari. Da verificare con i primi video, non con rendering.

## Prossimi passi tecnici (nessuno richiede pod)
1. Scrivere `tiers.json`, `grow.py` e il test di determinismo (si può fare qui in Python puro).
2. Archetipi base (6-8) + scena di test locale; misurare secondi/fotogramma e oggetti.
3. Solo con GO scritto della chat: una sessione pod di profilo (cuInit, clone, render di 30 fotogrammi, tempo), poi decisione Cycles/Eevee e pod/locale.
