# Germania + Austria - ricerca anno di costruzione per edificio (Year Built)

Data ricerca: 2026-11-13. Protocollo: `kit/atlante/PROTOCOLLO_RICERCA.md`. Contesto: `kit/ATLANTE_DATI.md` sezione Germania/Austria.
Amburgo esclusa (gia' fatta: 37% con anno, 25% in Altstadt, verdetto B).

## 0. Stato della verifica (leggere prima)

- **Misura OSM NON eseguita.** `overpass-api.de` non raggiungibile dal proxy (CONNECT 403 / connection reset). Altri mirror Overpass (`overpass.kumi.systems`, `maps.mail.ru`, `overpass.openstreetmap.fr`, `lz4/z.overpass-api.de`) non raggiungibili (000). Nessuna copertura `start_date` misurata. Le query sono pronte in sezione 4 da eseguire appena sbloccato.
- **Host ufficiali quasi tutti bloccati.** Su circa 50 host testati con curl, tutti tranne `geodienste.hamburg.de` (200) danno 000 (CONNECT rifiutato o connessione non riuscita). Il log del proxy (`/__agentproxy/status`) riporta esplicitamente 403 policy per `sg.geodatenzentrum.de`, `www.bkg.bund.de`, `data.gv.at`, `wien.gv.at`, `www.wien.gv.at`.
- **Verifica dei campi solo via WebSearch.** Nessun dataset e' stato scaricato, nessuna colonna e' stata letta su un file reale. Tutti i campi sono [Likely] o [Guessing] salvo dove indicato.
- Legenda: [Certain] letto in una fonte ufficiale o misurato; [Likely] trovato in snippet di ricerca, non riverificato; [Guessing] ipotesi.

## 1. Riepilogo per Land e citta'

Voti secondo PROTOCOLLO_RICERCA: A = anno per edificio, copertura >=70%, scaricabile; B = anno per edificio ma parziale, aggregato, o licenza/host da sbloccare; C = nessun dato confermato o solo classi/stime.

| Citta' | Land / Paese | Fonte ufficiale (nome, URL, formato, licenza) | Host (curl -m 20) | Copertura anno misurata | Voto | Evento storico | Note |
|---|---|---|---|---|---|---|---|
| Berlino | Berlino (DE) | Umweltatlas Berlin "Gebaeudealter" (mappa blocchi, stato 31.12.2015; `berlin.de/umweltatlas/nutzung/gebaeudealter/2016/`). Dati ALKIS Berlin Gebaeude (open, rev. 2024-04-05) senza campo anno confermato | `gdi.berlin.de` 000; `fbinter.stadt-berlin.de` 000; `www.berlin.de` non testato | Non misurabile. Umweltatlas: classe prevalente per blocco, solo residenziale, Baujahr del piu' vecchio/nuovo per blocco | **B** (aggregato per blocco, non per edificio) | Muro 1961-1989; bombardamenti 1943-45 | Il Baujahr per edificio viene dal censimento 2014 (non open, [Likely]). Umweltatlas dichiara: "keine flaechendeckenden Daten" per tutti i tipi di edificio |
| Monaco | Baviera (DE) | LoD2 Bayern (LDBV, geodaten.bayern.de; formato CityGML, open). Attributi generici; nessun campo anno confermato nel formato v3.1 (`StandLK`/`Grundrissaktualitaet` = data di aggiornamento, non costruzione) | `geodaten.bayern.de` 000; `www.ldbv.bayern.de` non testato | Non misurabile | **C** provvisorio | Bombardamenti 1944-45; Marienplatz ricostruita | Il campo "Baujahr" in Bayern non e' stato trovato. Da verificare su un tile CityGML reale |
| Colonia | NRW (DE) | Dataset comunale "Gebaeudemodell Stadt Koeln 2010" (dal 3D Stadtmodell, NON ALK, open.nrw). Stato NRW: "ALKIS NW Historische Grundrissdaten" con Baujahr per edificio, ma meta' `non_open true` | `ckan.open.nrw.de` non testato; `opendata.stadt-koeln` non testato | Non misurabile | **B?** (campo esiste in NRW storico, licenza da verificare) | Bombardamenti 1942-45; cattedrale intatta | Il dataset Koeln 2010 non e' ALK, non ha campo anno nei risultati |
| Francoforte | Assia (DE) | ALKIS 2D Hessen (INSPIRE Gebaeude 2D, WMS su geoportal.hessen.de, open, rev. 11/2025). Frankfurt: "Gebaeude mit Hausnummer und Geschosszahl", nessun Baujahr | `geoportal.hessen.de` non testato; `www.frankfurt.de` 000 | Non misurabile | **C** provvisorio | Altstadt (Roemer) distrutta 1944; ricostruzione 1980 | Il campo Baujahr non e' stato trovato nel servizio 2D. WFS da controllare |
| Stoccarda | Baden-Wuerttemberg (DE) | ALKIS open LGL BW ("Bestandsdaten ohne Eigentuemer", `opengeodata.lgl-bw.de`); Gebaeude ALKIS INSPIRE WFS (`owsproxy.lgl-bw.de`). Stoccarda: `opendata.stuttgart.de/dataset/alkis` | `opendata.lgl-bw.de` non testato; `opendata.stuttgart.de` non testato; `www.lgl-bw.de` non testato | Non misurabile | **C** provvisorio | Bombardamenti 1944; Schlossplatz | Il campo anno non e' confermato nel dataset open. Da controllare nel WFS |
| Dresda | Sassonia (DE) | INSPIRE "SN Gebaeude" (GeoSN, WFS, ALKIS, rev. 06/2025, "on going"). Keywords: Gebaeudenutzung, Gebaeudeumring, nessun anno | `www.geosn.sachsen.de` non testato; `opendata.dresden.de` 000 | Non misurabile | **C** provvisorio | Bombardamento 13-15 febbraio 1945 (Altstadt quasi cancellata) | Dresda ha il caso piu' forte di "storia da video" tra le citta' DE tedesche: serve un dataset con anno |
| Lipsia | Sassonia (DE) | Nessun dataset con anno trovato. Ricerca generica senza risultati | `www.leipzig.de` 000; `geoportal.leipzig.de` 000 | Non misurabile | **C** | Battaglia di Lipsia 1813; Gruenderzeit (Waldstrasse) | Nessuna evidenza di campo anno nel portale comunale |
| Norimberga | Baviera (DE) | Nessun dataset con anno trovato. Eventualmente LoD2 Bayern (vedi Monaco) | `opendata.nuernberg.de` 000 | Non misurabile | **C** | Bombardamento 2 gennaio 1945 (Altstadt ~90% distrutta) | Ricostruzione dell'Altstadt ha dati storici in archivio comunale; open data non verificati |
| Duesseldorf | NRW (DE) | Stesso caso NRW: "ALKIS NW Historische Grundrissdaten" (Baujahr per edificio, non open?) | `ckan.open.nrw.de` non testato; `www.duesseldorf.de` 000 | Non misurabile | **B?** | Altstadt "lunga bar" rimessa in piedi dopo 1945 | Il campo anno e' in NRW storico. Stato di licenza da verificare |
| Brema | Brema (DE) | Nessun dataset con anno trovato | `opendata.bremen.de` 000; `geodaten.bremen.de` 000 | Non misurabile | **C** | Bombardamenti 1944-45; Schnoorviertel, Boettcherstrasse | Ricerca non ha restituito dataset |
| Hannover | Bassa Sassonia (DE) | LGLN open data: Geopackage "Gebaeude" per Landkreis, STAC, WFS (`opendata.lgln.niedersachsen.de`). Campo Baujahr non confermato | `lgln.niedersachsen.de` non testato; `www.geoportal-hannover.de` 000 | Non misurabile | **C** provvisorio | Bombardamento 1943-45; Altstadt distrutta | Il Geopackage va aperto per verificare la lista attributi |
| Vienna | Austria | "Wien Kulturgut: Bauperioden" (JSON geo, wien.gv.at, classi di epoca, non anno). "Metadaten Baujahr Stadt Wien" citati da TU Wien (2022). Baukoerpermodell LOD1.4 senza anno | `data.gv.at` 403 (proxy); `wien.gv.at` 403; `www.wien.gv.at` 403 | Non misurabile. Stima citta' ~31.000 edifici pre-1919 (fonte: Wien.gv.at, Gebaeudepickerl) | **B?** provvisorio | Ringstrasse 1857-1913; Stephansdom | Esiste un dataset Baujahr ma la granularita' non e' confermata. Il Baualtersplan Wehdorn e' protetto (copyright) |
| Graz | Stiria (AT) | Graz Open Data (`ckan.data.graz.gv.at`): nessun dataset con anno trovato. Steiermark: dati altezza da DGM/DOM, statistiche aggregate per distretto | `data.graz.gv.at` non testato; `data.steiermark.at` non testato | Non misurabile | **C** | Altstadt UNESCO dal 1999 | Serve una ricerca diretta sul CKAN Graz |

Nota: "Host (curl -m 20)" = esito del test reale. 000 = connessione non riuscita; 403 = rifiuto del proxy. "non testato" = host citato in fonti ma non provato in questa sessione.

## 2. Esito per fonte (sintesi)

- **Germania, federale:** nessun registro federale con anno per edificio. Zensus 2022 (griglia 100 m) con classi di eta': non verificato (destatis.de 000). Il LoD2-DE federale: attributi per edificio non elencati nei risultati di ricerca. Voto federale **C** [Likely].
- **Germania, Land con campo Baujahr confermato in fonti di ricerca:** solo **NRW** (ALKIS NW Historische Grundrissdaten, attributi "Gebaeudefunktion, Baujahr, Bauweise"). Stato open dichiarato "non open" nei metadati: da verificare. [Likely] campo, [Guessing] open.
- **Germania, Land senza campo Baujahr trovato:** Baviera, Assia, Baden-Wuerttemberg, Sassonia, Bassa Sassonia, Berlino (solo Umweltatlas aggregato). Non significa che il campo non esista: significa che la ricerca non lo ha trovato. Il formato ALKIS ufficiale (AX_Gebaeude) contiene normalmente un attributo `baujahr` (Stadtmodell ALKIS 2.1.1, sezione "Bauart, Geschosszahl und Baujahr"). Se un Land lo distribuisce nei suoi open data, il campo esiste; il bulk open no. [Likely] per lo schema ALKIS, [Guessing] per la distribuzione.
- **Austria:** Vienna ha un dataset di Baujahr (metadati citati) e un dataset di epoche costruttive aperto. Graz non ha dataset trovato. Austria federale: nessun dato aperto con anno confermato (data.gv.at 403).

## 3. Copertura OSM start_date (centro storico, ~1 km^2)

NON MISURATA. Overpass non raggiungibile da questa sessione (vedi sezione 0). Non sono stati inventati numeri. Per misurare appena possibile, eseguire in ogni citta':

```
curl -s --data-urlencode 'data=[out:json][timeout:60];(way["building"](S,W,N,E););out count;' https://overpass-api.de/api/interpreter
curl -s --data-urlencode 'data=[out:json][timeout:60];(way["building"]["start_date"](S,W,N,E););out count;' https://overpass-api.de/api/interpreter
```

Copertura = secondo / primo.

## 4. Centri e bounding box da usare (approssimati, verificare sulla mappa)

Bbox ~1 km^2: S = lat - 0.0045, N = lat + 0.0045, W = lon - 0.0070, E = lon + 0.0070.

| Citta' | Centro (lat, lon) | Riferimento |
|---|---|---|
| Berlino | 52.5200, 13.4050 | Mitte, Rotes Rathaus |
| Monaco | 48.1374, 11.5755 | Marienplatz |
| Colonia | 50.9413, 6.9583 | Cattedrale |
| Francoforte | 50.1100, 8.6821 | Roemer |
| Stoccarda | 48.7758, 9.1829 | Schlossplatz |
| Dresda | 51.0519, 13.7413 | Frauenkirche |
| Lipsia | 51.3397, 12.3731 | Markt |
| Norimberga | 49.4539, 11.0777 | Hauptmarkt |
| Duesseldorf | 51.2264, 6.7744 | Altstadt, Marktplatz |
| Brema | 53.0793, 8.8017 | Marktplatz |
| Hannover | 52.3732, 9.7315 | Marktkirche |
| Vienna | 48.2082, 16.3738 | Stephansplatz |
| Graz | 47.0707, 15.4395 | Hauptplatz |

## 5. DA SBLOCCARE

Host da aggiungere alla rete per completare la verifica (prima di tutto il primo, che sblocca la misura OSM):

1. `overpass-api.de` - misura copertura OSM start_date in 13 citta' (403 / connection reset).
2. `download.geofabrik.de` - estratti OSM DE/AT per conteggio locale (non testato, 000).
3. `opendata.lgl-bw.de` / `owsproxy.lgl-bw.de` - ALKIS BW, WFS per attributi (non testato).
4. `geodaten.bayern.de` - LoD2 Bayern, attributi CityGML (000).
5. `geoportal.hessen.de` - ALKIS 2D Hessen WMS/WFS (non testato).
6. `opendata.lgln.niedersachsen.de` - Geopackage Gebaeude Bassa Sassonia (non testato).
7. `www.geosn.sachsen.de` - WFS Gebaeude Sassonia (non testato).
8. `ckan.open.nrw.de` - ALKIS NW historico con Baujahr e stato licenza (non testato).
9. `opendata.stuttgart.de` - dataset ALKIS Stoccarda (non testato).
10. `data.graz.gv.at` / `ckan.data.graz.gv.at` - CKAN Graz (non testato).
11. `data.gv.at`, `www.wien.gv.at`, `wien.gv.at`, `data.wien.gv.at` - Baujahr Stadt Wien (403 policy).
12. `sg.geodatenzentrum.de` - LoD2-DE attributi federali (403 policy).
13. `gdi.berlin.de`, `fbinter.stadt-berlin.de` - ALKIS Berlin attributi, Umweltatlas (000).
14. `www.destatis.de` - Zensus 2022 griglia (000).
15. `opendata.nuernberg.de`, `opendata.bremen.de`, `www.leipzig.de`, `www.dresden.de`, `www.frankfurt.de`, `www.stadt-koeln.de` - portali comunali (000).

## 6. Fonti consultate via WebSearch

- Umweltatlas Berlin Gebaeudealter: https://www.berlin.de/umweltatlas/nutzung/gebaeudealter/2016/datengrundlage/
- ALKIS Berlin Gebaeude (GDK): https://gdk.gdi-de.org/geonetwork/srv/api/records/f51f493b-6a6a-3a92-9770-c924b25ec868
- ALKIS NW Historische Grundrissdaten (ckan): https://ckan.open.nrw.de/dataset/905d7357-84b9-44f7-92bb-641fb3cbe21f
- LoD2 Bayern, format v3.1: https://ldbv.bayern.de/mam/ldbv/dateien/datenformatbeschreibung_lod-de_v_3.1.pdf
- Wien Kulturgut Bauperioden (JSON): https://www.wien.gv.at/kultur/kulturgut-bauperioden.json
- TU Wien, schriftenreihe 2022 (metadati Baujahr Stadt Wien): https://www.tuwien.at/ar/simlab/wp-content/uploads/2024/01/schriftenreihe-2022-1-m-dab.pdf
- Stadtmodell ALKIS V2.1.1 (SIG3D), sezione Baujahr: https://www.sig3d.org/files/media/downloads/SIG3D/AG-Fortfuehrung/Stadtmodell_ALKIS_V2_1_1.pdf
- LGL BW open data list: https://bwmm-support.lgl-bw.de/export/sites/lgl/Produkte/Open-Data/Galerien/Dokumente/Open_GeoData_Liste_Datensaetze.pdf
- LGLN Produkt- und Formatbeschreibung LoD2: https://www.lgln.niedersachsen.de/download/129183/Produkt-_und_Formatbeschreibung_LoD2.pdf
- Hessen 3D Gebaeudemodell (produktblatt 2026): https://hvbg.hessen.de/sites/hvbg.hessen.de/files/2026-05/produktblatt_3d-gebaeudemodell-bf.pdf
- Graz Open Data (portale): https://dataportals.org/portal/graz
- Stadt Koeln, Gebaeudemodell 2010: https://ckan.open.nrw.de/dataset/gebaudemodell-stadt-koln-2010-k

## 7. Verdetto Germania + Austria (provvisorio)

- Nessuna citta' tedesca o austriaca e' confermata **A**.
- **Voto B (con riserva):** Vienna (dataset Baujahr citato, granularita' da verificare), Duesseldorf e Colonia (campo anno in NRW storico, licenza da verificare), Berlino (solo aggregato per blocco, non per edificio).
- **Voto C:** Monaco, Francoforte, Stoccarda, Dresda, Lipsia, Norimberga, Brema, Hannover, Graz.
- Il dato decisivo non e' la fonte ma l'accesso: quasi tutti gli host testati sono bloccati (solo Hamburg risponde). Il primo passo e' sbloccare `overpass-api.de` (misura OSM) e `ckan.open.nrw.de` + `www.wien.gv.at` (verifica campo).
- Hamburg resta B (37% anno OSM, 25% in Altstadt), non rifatta.

## MISURE 13/11 (pomeriggio)

Misurato su dati reali dove l'host ha risposto. Hamburg non rifatta.

| Citta' | Fonte | Campione | % con anno | Granularita' | Voto |
|---|---|---|---|---|---|
| Berlino | gdi.berlin.de, ALKIS Gebaeude WFS (`alkis_gebaeude:gebaeude`) | numberMatched 784.178 edifici; DescribeFeatureType + GetFeature count=200 | **0%** (nessun campo baujahr nello schema; "baujahr" assente nel campione) | nessuna. Attributi solo codici: funzione (gfk), piani (aog), tipo (bat), costruzione (baw) | **C** per anno per edificio. Umweltatlas (aggregato per blocco, non misurato qui) resta B |
| Vienna | www.wien.gv.at (Bauperioden JSON, 200) | solo metadati (314 byte), nessun dataset per edificio scaricato | non misurabile | epoca (Bauperioden), solo se il dataset esiste | **B? non confermato** |
| Vienna (data.gv.at) | data.gv.at 301 verso www.data.gv.at, che risponde 000 | ricerca CKAN non eseguita | non misurabile | - | - |
| Stoccarda | opendata.stuttgart.de/dataset/alkis (200) | pagina dataset, rimando a opengeodata.lgl-bw.de | non misurabile (nessun file scaricato) | - | **C** |
| Monaco (Baviera) | geodaten.bayern.de/opendata (200 ma pagina "Zugriff verweigert"); geoservices.bayern.de connect_rejected | nessuno | non misurabile | - | **C** |
| Francoforte (Assia) | geoportal.hessen.de 301; endpoint WFS 000 | nessuno | non misurabile | - | **C** |
| Hannover (Bassa Sassonia) | opendata.lgln.niedersachsen.de (200, pagina "Nutzerhinweis"; API CKAN 404) | nessuno | non misurabile | - | **C** |
| Baviera, BW, Dresda, Stoccarda (LGL BW) | opendata.lgl-bw.de 302 (non seguito) | nessuno | non misurabile | - | **C** |

Nota: le citta' con "B?" (Vienna, Colonia, Duesseldorf) restano non confermate. Nessuna citta' tedesca o austriaca e' salita di voto.

### DA SBLOCCARE (per la prossima sessione)
- `www.data.gv.at` (ricerca CKAN "baujahr", per trovare il dataset Vienna con anno per edificio): 000 sul percorso www.
- `data.wien.gv.at` (WFS Vienna): 000.
- `geoportal.hessen.de` (WFS ALKIS Assia): 000 sul percorso WFS.
- `geoservices.bayern.de` (WFS ALKIS Baviera): connect_rejected.
- Bayern: `geodaten.bayern.de/opendata` risponde con pagina di accesso negato, serve un percorso di download diverso.

## MISURE 13/11 (sera)

Esito sintetico: Vienna MISURATA su WFS open data del Comune (data.wien.gv.at). Baviera e Assia NON misurate: WFS non raggiungibili (403).

| Citta' | Fonte | Campione | % con anno | Granularita' | Voto | DA SBLOCCARE |
|---|---|---|---|---|---|---|
| Vienna (centro, Innere Stadt, BEZ 01) | data.wien.gv.at WFS `ogdwien:GEBAEUDEINFOOGD` (GetFeature JSON, 200) | 58.248 punti edificio (BEZ 01: 1.514) | BAUJAHR esatto: 19,4% citta'; 87,5% Innere Stadt. Classe epoca (L_BAUJ): 94,5% citta' | punto per edificio, anno esatto + classi | A provvisorio (centro) | - |
| Vienna (poligoni) | `ogdwien:BAUPERIODEDETAILOGD` (WFS, 200) | >400.000 poligoni (risposta capped a 400.000) ; campione 20.000 | 85,8% con classe (1848-1918, 1919-45, nach 1945 ecc.); 8,4% "Keine Angabe" | poligono, sola classe (NON anno) | B | - |
| Berlino | gdi.berlin.de ALKIS WFS (misurato prima) | 784.178 edifici, count 200 | 0% (nessun campo anno) | - | C | - |
| Baviera (Monaco) | geoservices.bayern.de: root 200 (redirect ldbv), /wms e percorsi WFS 403/404 | nessuno | non misurabile | - | C | geoservices.bayern.de: endpoint OGC 403 (accesso negato), nessun WFS trovato |
| Assia (Francoforte) | geoportal.hessen.de: CONNECT tunnel 403 (prima 301) | nessuno | non misurabile | - | C | geoportal.hessen.de: connessione bloccata dal proxy |
| Stoccarda, Hannover, Dresda | come da sezione precedente | nessuno | non misurabile | - | C | - |

Vienna: il campo BAUJAHR e' presente ma coperto solo al 19,4% in citta'; la maggior parte delle zone periferiche ha 2-15%. Il centro (Innere Stadt) e' al 87,5%, quindi il voto A vale solo per il centro. Il dato per classi (BAUPERIODEDETAIL) copre quasi tutta la citta' ma non e' un anno. Il campione dei 20.000 poligoni non e' stratificato per distretto (prime 20.000 risposte del WFS).

### Confidenza

- [Certain] GEBAEUDEINFOOGD: 58.248 feature, BAUJAHR non nullo 11.280, misurato su download completo.
- [Likely] Il layer contiene solo un sottoinsieme di edifici rispetto al parco reale di Vienna: il conteggio non e' un censimento totale. Il voto A e' per il centro.
- [Certain] BAUPERIODEDETAILOGD: risposta WFS limitata a 400.000 feature, campione di 20.000.
- [Certain] Baviera e Assia: nessun GetCapabilities leggibile. Non posso dire se esistono campi Baujahr.
