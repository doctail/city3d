# Parigi — audit tecnico degli archivi e stato di produzione

Data dell'audit: 27 ottobre 2026  
Repository: https://github.com/doctail/city3d  
Perimetro dell'audit: quattro archivi caricati in chat, scheda di validazione e file del branch main. Nessun pod o credito utilizzato.

## 1. Stato sintetico

- Fase 0 — scheda storica: **già completata nel repository**. La GitHub Action "Controllo schede di validazione" è verde sul commit `c79d6649d6f13e7a4713a19f072ba61ec08ea187`: [esecuzione verificata](https://github.com/doctail/city3d/actions/runs/40357651977).
- Fase 1 — acquisizione: archivi ricevuti e ispezionati. Copertura BDNB sufficiente secondo la soglia del 70% in tutti i 20 arrondissement.
- Fase 1 — conversione: **non completata**. Il file `roads.json` previsto dal renderer non è presente negli archivi grezzi; va generato e verificato.
- Fase 2 — layer storico: **non completata**. Nel branch main non esistono ancora `hist_parigi.py` né `bridges_parigi.py`.
- Fase 3 — prove visive, controlli di prestazione e regia: non eseguiti in questo audit. Nessun rendering è stato avviato.

## 2. Inventario verificato degli archivi

### `dati_parigi.tgz` — dati base

Contiene il DEM `Copernicus_DSM_COG_10_N48_00_E002_00_DEM.tif`, configurazione `city_parigi.json`, log e dati compressi OSM/BDNB.

| Layer | Conteggio / risultato verificato | Nota |
|---|---:|---|
| Edifici OSM | 680.548 feature grezze | Include geometrie multipoligono e tag variabili; `prep_parigi.py` filtra gli oggetti da usare come footprint. |
| Strade OSM | 131.306 feature | Le proprietà osservate sono `highway`, `name`, `osm`; non risultano inclusi i tag ponte/ferrovia necessari per replicare integralmente la logica di Copenhagen. |
| Ambiente OSM | 30.953 feature | Contiene acqua e altre geometrie ambientali. |
| BDNB | 338.210 edifici nel riepilogo | 268.959 con anno valido secondo `anni.txt`. |
| Arrondissement | 20/20 riconosciuti | Tabella in `copertura.csv`. |

La copertura degli anni per arrondissement varia dall'87,3% (12º) al 95,1% (3º). Nessun arrondissement è sotto il limite configurato del 70%. Questi valori descrivono la presenza di un anno valido, non garantiscono che ogni data sia storicamente esatta.

### `dati2_parigi.tgz` — Vasserot, vie, monumenti e mappe

- Catalogo di metadati Stanford relativo a cinque layer Vasserot; i link ai singoli file risultano in errore 404 nei log.
- Layer vettoriale delle vie correnti: 6.624 feature in `paris_voies.geojson`, con campi quali `ouverture`, `historique`, `classement`, `siecle`, `debut` e `fin`.
- Il download CSV alternativo `denominations-des-voies-actuelles` fallisce con 404. Il GeoJSON delle vie è invece disponibile e contiene descrizioni utili per ricavare date di apertura.
- Dati Merimée per Parigi e dipartimenti limitrofi.
- Risultati Wikidata: 15.547 righe per costruzione, 805 per demolizione e 1.973 per apertura. Sono risultati grezzi da filtrare e disambiguare, non 19.000 eventi già validati.
- Mappe storiche ad alta risoluzione: Turgot 1739, Vasserot, Verniquet 1789 e una carta circa 1870.

### `dati3_parigi.tgz` — monumenti storici

Contiene esportazioni CSV, JSON e GeoJSON della base dei monumenti storici e il log di ricerca. Sono dataset di supporto per validare monumenti e coordinate, non sostituiscono la scheda storica.

### `dati4_parigi.tgz` — archivio completo ALPAGE

L'archivio contiene il pacchetto ALPAGE e diversi GeoPackage. Sono stati aperti e interrogati direttamente i layer principali; i conteggi verificati sono:

| Layer | Feature | CRS / geometria |
|---|---:|---|
| `Vasserot_1_Bati` | 40.356 | EPSG:2154, MultiPolygon |
| `Vasserot_1_Ilots` | 1.277 | EPSG:2154, MultiPolygon |
| `Vasserot_1_Parcelles` | 26.572 | EPSG:2154, MultiPolygon |
| `Vasserot_1_Voies` | 4.378 | EPSG:2154, MultiLineString |
| `Vasserot_2_Hydro` | 87 | EPSG:2154, MultiPolygon |
| `1380_ilots` | 628 | EPSG:2154, MultiPolygon |
| `1380_hydro` | 123 | EPSG:2154, MultiPolygon |
| `1380_voies` | 1.618 | EPSG:2154, MultiLineString |
| `Ilots_1300` | 440 | EPSG:2154, MultiPolygon |
| `Ilots_1380` | 381 | EPSG:2154, MultiPolygon |
| `Ilots_1553` | 502 | EPSG:2154, MultiPolygon |
| `Ilots_1652` | 836 | EPSG:2154, MultiPolygon |
| `Ilots_1741` | 1.049 | EPSG:2154, MultiPolygon |
| `Ilots_1791` | 1.294 | EPSG:2154, MultiPolygon |
| `Rues_1300` | 1.208 | EPSG:2154, MultiLineString |
| `Rues_1380` | 1.065 | EPSG:2154, MultiLineString |
| `Rues_1553` | 1.139 | Lambert-93, MultiLineString |
| `Rues_1791` | 1.539 | Lambert-93, MultiLineString |
| `Enceintes` | 289 | EPSG:2154, MultiPolygon |
| `Tours_portes` | 179 | EPSG:2154, Point |
| `Quais_1312_1789` | 48 | EPSG:2154, MultiLineString |
| `Hydro_1791` | 81 | EPSG:2154, MultiPolygon |
| `Bati_Cite_1754` | 2.190 | WKT RGF93 / Lambert-93, MultiPolygon |
| `Ilots_Cite_1754` | 48 | EPSG:2154, MultiPolygon |

Il layer `Bati_Cite_1754` ha un CRS descritto tramite WKT anziché un semplice codice EPSG, ma la definizione dichiara RGF93 / Lambert-93: va normalizzato e verificato durante la conversione, non trattato automaticamente come CRS errato.

I file descrittivi ALPAGE indicano licenza ODbL 1.0 e richiedono attribuzione; le mappe derivate hanno inoltre condizioni di attribuzione/condivisione da verificare per ogni fonte.

## 3. Problemi tecnici da risolvere prima della regia

1. **Strade:** `run.sh` si ferma se `DATA/roads.json` manca. Il file OSM è compresso e deve essere adattato al formato atteso dal renderer. Inoltre, l'esportazione corrente non conserva i tag ponte e ferrovia; la logica dei ponti deve usare una fonte separata o una nuova estrazione.
2. **Vie aperte per sventramento:** `paris_voies.geojson` fornisce geometrie poligonali e descrizioni testuali di apertura. La data va estratta con regole esplicite e verifica manuale per gli assi haussmanniani; non si deve applicare un'unica data all'intera via se la fonte descrive tratti distinti.
3. **Predecessori edilizi:** il catasto moderno non contiene le impronte delle case demolite per aprire i boulevard. Servono edifici generici temporanei dentro i corridoi storici, con data di scomparsa legata all'apertura della strada, senza lasciare vuoti a forma di strade moderne.
4. **Layer storico:** il repository non contiene ancora `hist_parigi.py`. Le geometrie ALPAGE sono presenti solo nell'archivio caricato e non sono nel repository; gli script dovranno ricevere un percorso dati esplicito, senza presumere che il pod abbia accesso agli allegati della chat.
5. **Ponti:** il renderer consuma `bridges.json`; lo script specifico per Parigi deve rispettare la sezione G della scheda e separare attraversamento originario, sostituzioni e ponte attuale.
6. **DEM:** il nome del raster contiene `DSM` (Digital Surface Model). Prima di usarlo come solo terreno occorre controllare se include edifici/vegetazione, per evitare di duplicare l'altezza degli edifici nel renderer.
7. **Documentazione di regia:** nel branch main sono presenti `REGIA.md`, `PRODUZIONE_TIMELAPSE.md` e `PROSSIMA_COPENAGHEN.md`; non sono stati trovati `STILE_VISIVO.md`, `SPEC_CAMERA_DRONE.md`, `PROSSIMA_SIVIGLIA.md` o `claude/STATO.md` ai percorsi indicati nel brief. Non dichiarare di averli letti.

## 4. Prossimi passi a costo zero

1. Scrivere e testare un convertitore OSM → `roads.json`, usando le vie storiche come fonte di date di apertura e un fallback documentato per la data di urbanizzazione.
2. Preparare un convertitore ALPAGE che generi layer storici normalizzati e controlli CRS, geometrie e conteggi.
3. Implementare `hist_parigi.py` e `bridges_parigi.py` usando gli ID della scheda come riferimenti nei commenti.
4. Generare quattro frame CPU ritagliati a 640×360 e confrontarli con mappe storiche; non dichiarare superata questa fase finché il confronto non è stato eseguito.
5. Solo dopo la verifica di Fabio, valutare qualunque pod o rendering a pagamento.

Questo audit non certifica ancora il renderer, la copertura visiva dei layer, i ponti in 3D o la correttezza finale delle cronologie. Questi punti richiedono la conversione e i test successivi.
