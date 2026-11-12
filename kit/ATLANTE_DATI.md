# ATLANTE DEI DATI — scelta delle prossime città (Year Built)

Data ricerca: 2026-11-11/12. Nessuno strumento vidIQ usato. Nessun file del repo modificato oltre a questo.

## 0. Limiti di questa ricerca (leggere prima)

- WebFetch NON funziona in questa sessione: `hri.fi` e `wiki.openstreetmap.org` danno ENOTFOUND (host fuori dalla rete consentita). Ho potuto usare solo WebSearch, che restituisce riassunti, non le pagine dei dataset.
- Test di rete (curl, CONNECT): rifiutati con 403 ~50 host governativi/open data (elenco in sezione 6). Unico raggiungibile: `api.dataforsyningen.dk` (Danimarca, già in uso).
- Quindi NESSUN nome di campo, URL di download o licenza è stato verificato a mano su una pagina. Dove il campo "anno" è confermato dai risultati di ricerca lo dico; altrimenti è conoscenza di fondo e il tag è [Likely] o [Guessing].
- Appena gli host della sezione 6 sono sbloccati, il primo passo è un controllo di 10 minuti per fonte (GetCapabilities / prime 100 righe / elenco campi) prima di costruire pipeline. Le righe [Guessing] vanno trattate come ipotesi da verificare, non come fonti.
- Colonna "già fatta da concorrenti?": lasciata vuota ovunque (verifica vidIQ dopo).

Legenda granularità: A = anno/periodo stretto per singolo edificio; B = aggregato (isolato, sezione censuaria, lotto con più edifici, fasce larghe); C = niente.
Tag affidabilità: [Certain] confermato da ricerca o da uso già fatto dal proprietario; [Likely] ricordo solido ma non riverificato; [Guessing] ipotesi.

---

## 1. Tabella paesi

| Paese | Fonte | Gran. | Formato | Licenza | Host da sbloccare | Note | Tag |
|---|---|---|---|---|---|---|---|
| Spagna | Catastro INSPIRE Buildings | A | ATOM/WFS GML | CC BY 4.0 | già usato (`ovc.catastro.meh.es`) | Tutto il paese tranne Paesi Baschi/Navarra (catasti forali propri) | [Certain] (riferimento del proprietario) |
| Danimarca | BBR (Datafordeler / Dataforsyningen) | A | API/WFS | aperta (DK) | già usato (`api.dataforsyningen.dk` raggiungibile) | Anno edificio + impronte | [Certain] |
| Paesi Bassi | BAG (bouwjaar) + 3DBAG | A | WFS, GPKG | CC0/CC BY | già usato (PDOK, 3dbag) | BAG importato anche in OSM con start_date | [Certain] |
| Francia | BDNB (+ BD TOPO per impronte) | A (con buchi) | GPKG/CSV | Licence Ouverte (Etalab) | già usato (bdnb.io / data.gouv) | Anno spesso nullo fuori dai grandi centri; qualità variabile | [Certain] uso; [Likely] copertura |
| USA - NYC | PLUTO + Building Footprints (construction_year) | A | SHP/CSV | NYC Open Data | già usato | Riferimento | [Certain] |
| Finlandia | Helsingin rakennukset (WFS `Rakennukset_alue`, campo `c_valmpvm` data completamento) + HSY "Pääkaupunkiseudun rakennukset" (Helsinki/Espoo/Vantaa/Kauniainen) | A | WFS, SHP/GPKG | CC BY 4.0 [Likely] | `kartta.hel.fi`, `hri.fi`, `kartta.hsy.fi` | Prima del 1981 date meno affidabili (da indagini proprietari/costruttori); WFS: `kartta.hel.fi/ws/geoserver/avoindata/wfs` | [Certain] esistenza campo; [Likely] licenza |
| Finlandia (nazionale) | Ryhti (SYKE) building API INSPIRE | A? | API/GML | aperta | `ryhti.syke.fi` | Edifici + indirizzi INSPIRE; anno da verificare | [Guessing] |
| Estonia | Ehitisregister (EHR) open data + impronte Maa-amet | A | CSV/API, join su impronte | aperta | `livekluster.ehr.ee`, `geoportaal.maaamet.ee` | Aggiornato ogni giorno, storico dal 1994; il campo anno nel dataset aperto non confermato (il portale lo mostra) | [Likely] |
| Svizzera | GWR federale (GBAUJ anno, GBAUP periodo, coord. edificio) + impronte swisstopo/AV | A (punti + join impronte) | CSV, GeoJSON | open (OGD) | `public.madd.bfs.admin.ch`, `www.housing-stat.ch`, `data.geo.admin.ch`, `opendata.swiss`, `data.stadt-zuerich.ch`, `data.bs.ch` | GWR è a punti: poligoni da swisstopo (swissTLM3D/swissBUILDINGS3D) o misura ufficiale, join via EGID. Zurigo città e Basilea hanno GWR aperto (confermato da ricerca) | [Likely] |
| Svezia | Lantmäteriet "Byggnad" (poligoni aperti da feb 2025, CC BY 4.0) | ? | API | CC BY 4.0 | `api.lantmateriet.se`, `geotorget.lantmateriet.se` | Anno di costruzione non confermato nei dati aperti | [Guessing] per anno; [Certain] per poligoni aperti |
| Norvegia | Matrikkelen Bygningspunkt (aperto, GML/SQL/GDB) + FKB-Bygning (poligoni) | B/C? | GML, GDB | NLOD | `nedlasting.geonorge.no`, `kartkatalog.geonorge.no`, `wfs.geonorge.no`, `data.norge.no` | Punti con n. edificio/tipo; edifici pre-1983 con pochi attributi. FKB: accesso contraddittorio (aperto vs soli "Norge digitalt"). Esistono snapshot annuali "historiske data" 2022-2025 (utili per aggiunte, non per anno di costruzione) | [Guessing] |
| Germania | Nessun registro federale con anno (ALKIS/LoD2-DE: attributi senza Baujahr nelle specifiche viste). Zensus 2022 griglia 100 m con classi di età | C (federale) / B (Zensus) | GPKG/CSV | dl-de | `www.destatis.de`, `opengeodata.nrw.de`, `gdi.berlin.de`, `fbinter.stadt-berlin.de` | Land per Land: ALKIS può avere Baujahr ma di rado distribuito. NRW dichiara descrittori con anno (verifica) | [Likely] C; [Guessing] NRW |
| Austria | Nessun dato aperto con anno confermato. Vienna: titolo "Baujahr Stadt Wien" citato da TU Wien. Baualtersplan Wehdorn = protetto da copyright, non aperto | C / ? | - | - | `www.data.gv.at`, `data.wien.gv.at` | Dal 1/9/2025 legge Informationsfreiheit obbliga a più OGD: ricontrollare tra 6-12 mesi | [Guessing] |
| Belgio | Fiandre: GRB (impronte) senza anno [Likely]. Bruxelles: UrbIS Buildings (licenza open; anno non confermato). Catasto federale: statistiche per settore | C/B | WFS/SHP | open | `urbisdownload.datastore.brussels`, `opendata.brussels.be`, `geo.api.vlaanderen.be`, `finance.belgium.be` | UrbIS P&B "su richiesta" per l'accesso completo | [Guessing] |
| Polonia | BDOT10k budynki (OT_BUBD_A): campo anno costruzione indicato da una fonte non ufficiale | A? (spesso vuoto) | GML/SHP | open | `opendata.geoportal.gov.pl`, `integracja.gugik.gov.pl`, `www.geoportal.gov.pl` | Verificare quanto è popolato; modelli LoD1 solo come stato per anno | [Guessing] |
| Rep. Ceca | RÚIAN (VFR) stavební objekt: data di completamento presente ma popolata soprattutto per i nuovi | B/A parziale | VFR XML, WFS | CC BY 4.0 [Likely] | `vdp.cuzk.gov.cz`, `vdp.cuzk.cz`, `services.cuzk.gov.cz`, `ags.cuzk.cz` | Dal 2017 (talk-cz): campo esiste ma incompleto; poligoni da ZABAGED/RÚIAN punti | [Likely] campo; [Guessing] stato attuale |
| Lettonia | Cadastre (VZD): anno di messa in servizio nel catalogo immobili | ? | - | accesso in parte limitato | `www.kadastrs.lv`, `data.gov.lv` | Accesso a molti record a richiesta | [Guessing] |
| Lituania | Registrų centras: "anno di costruzione" nel registro | ? | - | n/d | `www.registrucentras.lt`, `data.gov.lt` | Bulk aperto non confermato | [Guessing] |
| Regno Unito | Nessun registro nazionale aperto con anno per edificio (blog 2020). Colouring London / Colouring Britain = crowd + dati estratti scaricabili | A (Londra, a bande/anno) | CSV/estratti (attributi); geometrie da OS | ODbL (attributi); OS OGL per OpenMap Local | `colouring.london`, `api.os.uk`, `osdatahub.os.uk` | Geometria OS non ridistribuibile: join su TOID con OS OpenMap Local. CDRC: età abitazioni E&W (B) | [Likely] |
| Irlanda | Nessun registro aperto trovato | C | - | - | - | Eurostat censimento solo aggregati | [Guessing] |
| Italia | Nessun catasto aperto con anno; ISTAT sezioni censuarie epoca costruzione (B) | B/C | CSV+SHP | CC BY | `www.istat.it` | Alcune regioni/comuni pubblicano edifici (DBT) senza anno | [Guessing] |
| Portogallo | BGRI (Censos 2021) epoca per subsezione | B | SHP/GPKG | open | `mapas.ine.pt` | Già noto: B | [Certain] (info proprietario) |
| Grecia | Nessun dato aperto trovato (JRC: modelli stimati) | C | - | - | - | Solo stime GHS-OBAT / DBSM | [Guessing] |
| Russia / ex URSS | dom.gosuslugi.ru (GIS ZhKH) e reformagkh.ru: anno per case plurifamiliari (MKD) con indirizzo; Mosca data.mos.ru | A solo MKD, senza impronte | CSV/API + geocoding su OSM | variabile | `dom.gosuslugi.ru`, `www.reformagkh.ru`, `data.mos.ru` | Solo condomini; Rosreestr PKK non aperto | [Guessing] |
| Turchia | Nessun dato aperto con anno (TKGM non aperto) | C | - | - | `data.ibb.gov.tr` (Istanbul, da verificare) | Ripiego OSM/GHSL | [Guessing] |
| Medio Oriente | Nessuna fonte aperta nota (Israele: strati comunali da verificare) | C | - | - | - | | [Guessing] |
| Giappone | PLATEAU (CityGML/3D Tiles/GeoJSON): `yearOfConstruction` previsto dallo schema, mappato a start_date in OSM wiki; popolamento non uniforme | A/B parziale | CityGML, GeoJSON, MVT | CC BY 4.0 | `www.geospatial.jp`, `front.geospatial.jp`, `www.mlit.go.jp` | Valori mancanti spesso segnati con date segnaposto; stime età da 3D molto imprecise (ISPRS RMSE ~26 anni) | [Likely] campo; [Guessing] copertura |
| Corea del Sud | GIS건물통합정보 (MOLIT): impronte + registro edilizio (사용승인일 = data approvazione uso), a livello edificio, nazionale | A | API (data.go.kr), SHP via V-World | uso libero (KOGL) | `www.data.go.kr`, `apis.data.go.kr`, `www.vworld.kr`, `api.vworld.kr`, `data.seoul.go.kr` | Offerto come API; verificare se esiste download bulk. Dataset Seoul registro con date in CSV | [Likely] |
| Taiwan | Nessuna fonte confermata (età edifici in dati prezzi reali, aggregati) | B? | - | - | - | | [Guessing] |
| Singapore | HDB Property Information (anno completamento per blocco, con coordinate) | A (solo HDB) | CSV/API | SG Open Data Licence | `data.gov.sg` | Poco "storico" per un video; HDB = edilizia pubblica | [Likely] |
| Canada | Montreal: unità di valutazione foncière (anno costruzione); Vancouver: Property Tax Report (YEAR_BUILT) + parcelle; Calgary, Edmonton: assessment con anno; Toronto: nessun anno (massing 3D con altezze) | A (lotto/edificio) | SHP/CSV/GeoJSON | open | `donnees.montreal.ca`, `opendata.vancouver.ca`, `data.calgary.ca`, `data.edmonton.ca`, `open.toronto.ca` | StatCan ODB (impronte aperte) senza anno; Toronto solo periodi censuari per sezione | [Likely] (Toronto C: [Certain-ish] da ricerca) |
| USA (tipico) | Footprints comunali + parcelle/assessor di contea con YEAR_BUILT, join per ID particella o spaziale | A (lotto; edificio se 1 edificio per lotto) | SHP/GeoJSON/CSV | in genere PD/CC0 | vedi sezione 2 e 6 | Frammentato: ogni città/contea è un caso. Microsoft/Overture footprints senza anno | [Certain] schema generale |
| Australia | Geoscape Buildings (commerciale, solo date di cattura). Melbourne: City of Melbourne dataset edifici CLUE con anno costruzione (area CBD/municipio) | C nazionale; A Melbourne | CSV/GeoJSON | CC BY (Melbourne) | `data.melbourne.vic.gov.au` | Geoscape "National Buildings" dal 2026, non aperto | [Likely] Melbourne; [Certain-ish] Geoscape senza anno |
| Nuova Zelanda | LINZ NZ Building Outlines (CC BY, senza anno) | C | GPKG/WFS | CC BY 4.0 | `data.linz.govt.nz` | Valutazioni comunali (rating) possono avere anno, non unificate | [Likely] |
| Brasile | San Paolo: lotti + IPTU/TPCL con "ano da construção corrigido" a livello di lotto; resto C | B/A (lotto) | SHP + CSV | aperta | `dados.prefeitura.sp.gov.br`, `geosampa.prefeitura.sp.gov.br` | Join su SQL (setor-quadra-lote) | [Guessing] |
| Messico | Nessun dato aperto con anno | C | - | - | - | | [Guessing] |
| Argentina | Buenos Aires: dati catastali aperti, anno non confermato | C/? | - | - | `data.buenosaires.gob.ar` | | [Guessing] |
| Cile / Colombia | Cile SII catasto beni immobili (anno, senza geometrie aperte); Bogotà (UAECD) lotti/costruzioni | B? | CSV | open | `www.sii.cl`, `datosabiertos.bogota.gov.co` | | [Guessing] |
| Asia (Cina, India ecc.) | Nessun registro aperto | C | - | - | - | Ripiego GHSL | [Likely] |
| Mondo (ripiego) | OSM start_date; GHS-OBAT; GHS-AGE; EUBUCCO; JRC DBSM | vedi sez. 4 | - | ODbL/CC BY | sezione 6 | | [Certain] esistenza |

---

## 2. Tabella città candidate (fonte A), ordinate per "valore da video"

Valore (1-5) = storia lunga/riconoscibilità/dimensione, mio giudizio, non dato di mercato. "Già fatta?" vuota (da verificare con vidIQ). Esclusi i casi già prodotti (Parigi, Copenaghen, Rotterdam, Madrid, Siviglia, Valencia, Porto, Roma) salvo dove il dato nuovo apre un'altra scala.

| # | Città | Paese | Fonte A | Valore | Già fatta? | Rischi / note | Tag |
|---|---|---|---|---|---|---|---|
| 1 | Barcellona | ES | Catastro INSPIRE | 5 | | Pipeline già pronta (Spagna) | [Certain] |
| 2 | Amsterdam | NL | BAG + 3DBAG | 5 | | Pipeline NL già pronta; centro medievale/canali | [Certain] |
| 3 | Chicago | US | Footprints (year_built [Likely]) + Cook County Assessor | 5 | | Grande incendio 1871: storia perfetta per il timelapse; verificare campo year_built | [Likely] |
| 4 | Filadelfia | US | Footprints + OPA year_built (join) | 5 | | Impronte e particelle non si uniscono per ID, serve join per indirizzo/spaziale; molti year_built = 0 | [Likely] |
| 5 | Boston | US | Property Assessment (YR_BUILT) + footprints | 5 | | Join per parcella; molti edifici per lotto | [Likely] |
| 6 | San Francisco | US | Assessor roll (year built) + footprints 3D | 5 | | Terremoto 1906; join per blocco/lotto | [Likely] |
| 7 | Washington DC | US | CAMA (AYB/EYB) + Building Footprints (CC BY 4.0, confermato) | 4 | | Join per SSL/spaziale; footprints per anno 1999-2023 danno ulteriore verifica | [Likely] |
| 8 | Seul | KR | GIS건물통합정보 (사용승인일) | 5 | | Ritmo di crescita spettacolare; accesso via API, bulk da verificare | [Likely] |
| 9 | Zurigo | CH | GWR (aperto, confermato) + impronte | 4 | | GWR è a punti, join EGID | [Likely] |
| 10 | Helsinki | FI | WFS Rakennukset_alue (c_valmpvm) + HSY | 4 | | Dati ante-1981 meno affidabili; WFS diretto, facile | [Certain] |
| 11 | Montreal | CA | Unità di valutazione (anno) | 4 | | Lotto non edificio; verificare lat/lon e poligoni | [Likely] |
| 12 | Utrecht / L'Aia | NL | BAG | 4 | | Stessa pipeline di Amsterdam | [Certain] |
| 13 | Londra | UK | Colouring London (attributi) + OS OpenMap Local | 5 | | Licenza geometrie OS; età spesso a bande/stima crowd | [Likely] |
| 14 | Melbourne (CBD) | AU | CLUE edifici con anno | 3 | | Solo area del municipio, non l'intera metropoli | [Likely] |
| 15 | Tallinn | EE | EHR open + impronte Maa-amet | 3 | | Città medievale; verificare campo anno nel dataset aperto | [Likely] |
| 16 | Pittsburgh | US | Assessor Allegheny (YEARBLT, WPRDC) + footprints | 3 | | Join per parcella | [Likely] |
| 17 | Baltimora | US | SDAT/Maryland Property View (YEAR_BUILD) | 3 | | | [Likely] |
| 18 | Los Angeles | US | LA County Assessor (YearBuilt) + footprints LARIAC | 4 | | Dataset enorme; join per APN | [Likely] |
| 19 | Seattle | US | King County Assessor (YrBuilt) + footprints | 3 | | | [Likely] |
| 20 | Vancouver | CA | Property Tax Report (YEAR_BUILT) + parcelle | 3 | | Condomini per lotto | [Likely] |
| 21 | Zaragoza, Malaga, Granada, Cordoba, Palma, Bilbao* | ES | Catastro | 3-4 | | *Bilbao NON coperta (Paesi Baschi) | [Certain] (Bilbao esclusa) |
| 22 | Aarhus, Odense, Aalborg | DK | BBR | 2-3 | | Pipeline pronta | [Certain] |
| 23 | Edmonton, Calgary | CA | Assessment con anno + footprints | 2 | | | [Likely] |
| 24 | Detroit | US | Parcels con year_built | 3 | | Storia (declino/demolizioni); footprints storici da verificare | [Guessing] |
| 25 | Denver, Minneapolis | US | Assessor/Hennepin (YEAR_BUILT) | 2 | | | [Guessing] |
| 26 | Cincinnati, St. Louis, New Orleans, Portland | US | Assessor di contea (anno) | 2-3 | | Fonti non verificate affatto | [Guessing] |
| 27 | Berlino | DE | solo Umweltatlas Gebäudealter (B, censimento 2014, solo residenziale) | 5 | | NON è A: utile solo come ripiego per blocco | [Certain] (B) |
| 28 | Vienna | AT | "Baujahr Stadt Wien" da verificare | 5 | | Fonte non confermata | [Guessing] |
| 29 | Praga | CZ | RÚIAN data completamento | 4 | | Popolamento solo per edifici recenti | [Guessing] |
| 30 | Tokyo / Osaka / Kyoto | JP | PLATEAU yearOfConstruction | 5 | | Valori spesso vuoti; verificare per comune | [Guessing] |
| 31 | Singapore | SG | HDB year_completed | 3 | | Solo edilizia pubblica | [Likely] |
| 32 | San Paolo | BR | Lotti + IPTU anno | 4 | | Granularità lotto | [Guessing] |
| 33 | Mosca / S. Pietroburgo | RU | reformagkh / dom.gosuslugi (solo MKD) | 5 | | Impronte da OSM; copre solo condomini | [Guessing] |

Non candidati per mancanza di A: Germania (salvo verifiche Land), Austria, Belgio, Italia, Irlanda, Grecia, Turchia, Medio Oriente, Cina/India, Toronto, Oceania (salvo Melbourne), America Latina (salvo San Paolo).

---

## 3. Numero di città "da video" coperte per fonte A (>100K abitanti, storia lunga)

Stime mie, non conteggi verificati.

| Fonte | Stima città >100K | Di cui "da video" | Tag |
|---|---|---|---|
| Spagna (Catastro) | ~60 (senza Paesi Baschi/Navarra) | ~35-40 | [Likely] |
| Francia (BDNB) | ~40 comuni >100K | ~15-20 (qualità anno variabile) | [Guessing] |
| Corea (GIS건물통합) | ~40 | ~10 | [Guessing] |
| USA (parcella+footprint) | ~30-60 con pipeline fattibile su ~330 | ~20 | [Guessing] |
| Paesi Bassi (BAG) | ~25 | ~12 | [Likely] |
| Svizzera (GWR) | 5 (Zurigo, Ginevra, Basilea, Losanna, Berna) | 5 | [Likely] |
| Danimarca (BBR) | 4-5 | 3-4 (1 già fatta) | [Certain] |
| Finlandia | 3 (Helsinki, Espoo, Vantaa) + Tampere/Turku (da verificare) | 1-2 | [Certain] / [Guessing] |
| Canada | ~5-8 | ~4 | [Guessing] |
| Estonia | 1 (Tallinn) | 1 | [Certain] |
| Regno Unito (Colouring) | Londra (altre da verificare) | 1 | [Likely] |
| Giappone (PLATEAU) | decine di comuni, anno incerto | ? | [Guessing] |

Paesi A più ricchi di città: Spagna, Francia (con riserva), Corea, USA, Paesi Bassi.

---

## 4. Ripiego mondiale

| Fonte | Cosa offre | Gran. | Per quali parti di città basta | Licenza | Tag |
|---|---|---|---|---|---|
| OSM `start_date` | Anno per edificio dove mappato (molto denso dove importato da registri: Paesi Bassi via BAG; sporadico altrove) | A, copertura a macchia | Centri storici mappati a mano o quartieri importati; MAI copertura uniforme. Non ho cifre di copertura verificate | ODbL | [Certain] esistenza; [Guessing] densità |
| OpenHistoricalMap | Progetti storici (es. Danimarca/BBR) | A ma rado | Solo progetti specifici | CC0 | [Certain] esistenza |
| GHS-OBAT | Oltre 2,3 miliardi di impronte con epoca di costruzione (anno 2020), altezza, uso | A come epoca, derivata da raster | Aree di espansione recente (post-1975): periferie, città asiatiche/africane/latinoamericane. Il centro storico finisce nella classe unica "prima del 1975" | CC BY 4.0 [Likely] | [Certain] esistenza |
| GHS-AGE | Griglia 100 m / 1 km: epoca dominante dell'edificato (1975-2020), passi di 5-10 anni | B (raster) | Mappe di crescita per decennio dal 1975 | CC BY 4.0 | [Certain] |
| GHS-BUILT-S | Superficie edificata per epoca (1975-2030) | B (raster) | Come sopra | CC BY 4.0 | [Likely] |
| JRC EU DBSM (R2025) | Stime per edificio: altezza, epoca, uso, su impronte ufficiali, UE | A come epoca stimata | Europa dove manca il registro (es. Grecia, Irlanda, Austria) | aperta | [Certain] esistenza; [Guessing] dettagli |
| EUBUCCO | 200+ milioni di edifici da ~50 dataset ufficiali + OSM; anno presente solo ~24% | A parziale | Dove la fonte ufficiale porta l'anno | ODbL | [Certain] |

Regola pratica: GHSL/GHS-OBAT bastano per mostrare l'espansione 1975-2020 ma non per un timelapse storico di un centro antico; per quello serve una fonte A o OSM curato. Sono "ripiego" per città senza registro (Istanbul, Il Cairo, Mumbai...) ma il video sarebbe solo "dal 1975".

---

## 5. Priorità di verifica quando la rete è sbloccata

1. Helsinki WFS (GetCapabilities + 100 edifici con c_valmpvm): conferma immediata, rischio basso.
2. GWR svizzero: scaricare CSV, controllare GBAUJ/GKODE/GKODN, join EGID con swisstopo.
3. Chicago: elenco campi del dataset footprints + Cook County Assessor.
4. Corea: capire se GIS건물통합정보 ha download bulk o solo API (quota).
5. Filadelfia/Boston/SF: provare il join anno↔impronta e misurare quanti year_built sono 0.
6. EHR Estonia: verificare presenza anno nel CSV aperto.
7. Sweden Byggnad, BDOT10k, RÚIAN: percentuale di record con anno popolato.
8. Berlino/Amburgo/NRW/Vienna: cercare Baujahr nel dataset ALKIS/INSPIRE.

---

## 6. Elenco unico degli host da aggiungere alla rete (senza jolly)

Tutti i seguenti hanno dato CONNECT 403 in questa sessione (testati) o non sono stati testati; l'elenco è esatto per nome ma alcuni sottodomini sono [Likely]/[Guessing] (quando non si apre, controllare il link reale dalla pagina del dataset).

PRIORITA 1 - fonti A più promettenti
- `kartta.hel.fi` (WFS Helsinki)  [Certain]
- `hri.fi` (catalogo Helsinki)  [Certain]
- `kartta.hsy.fi` (HSY area metropolitana)  [Likely]
- `public.madd.bfs.admin.ch` (download GWR)  [Likely]
- `www.housing-stat.ch`  [Likely]
- `data.geo.admin.ch` (swisstopo)  [Likely]
- `opendata.swiss`  [Certain]
- `ckan.opendata.swiss`  [Certain]
- `data.stadt-zuerich.ch`  [Likely]
- `data.bs.ch` (Basilea, GWR)  [Certain]
- `data.cityofnewyork.us` (NYC; già usato)  [Certain]
- `data.cityofchicago.org`  [Certain]
- `datacatalog.cookcountyil.gov`  [Likely]
- `opendataphilly.org`  [Certain]
- `phl.carto.com`  [Likely]
- `opendata.dc.gov`  [Certain]
- `data.boston.gov`  [Likely]
- `data.sfgov.org`  [Likely]
- `www.data.go.kr`  [Certain]
- `apis.data.go.kr`  [Likely]
- `www.vworld.kr`  [Likely]
- `api.vworld.kr`  [Likely]
- `data.seoul.go.kr`  [Certain]
- `donnees.montreal.ca`  [Likely]
- `opendata.vancouver.ca`  [Likely]
- `colouring.london`  [Certain]
- `api.os.uk`  [Likely]
- `osdatahub.os.uk`  [Likely]
- `data.melbourne.vic.gov.au`  [Likely]
- `livekluster.ehr.ee`  [Guessing]
- `geoportaal.maaamet.ee`  [Likely]
- `imo.ut.ee` (documentazione EHR open data)  [Certain]

Hub ArcGIS (molte città USA/Canada ospitano i layer qui)  [Likely]
- `hub.arcgis.com`
- `opendata.arcgis.com`
- `services.arcgis.com`
- `services1.arcgis.com`
- `services2.arcgis.com`
- `services3.arcgis.com`
- `services5.arcgis.com`
- `services7.arcgis.com`
- `maps2.dcgis.dc.gov`

PRIORITA 2 - da verificare prima di costruire una pipeline (campo anno non confermato)
- `data.pdok.nl`, `service.pdok.nl`, `api.pdok.nl`, `data.3dbag.nl` (NL, già usati in produzione; se non già in lista)
- `bdnb.io`, `files.data.gouv.fr`, `www.data.gouv.fr`, `data.geopf.fr` (FR, già usati)
- `ovc.catastro.meh.es` (ES, già usato)
- `api.lantmateriet.se`, `geotorget.lantmateriet.se` (SE)
- `nedlasting.geonorge.no`, `kartkatalog.geonorge.no`, `wfs.geonorge.no`, `data.norge.no` (NO)
- `opendata.geoportal.gov.pl`, `integracja.gugik.gov.pl`, `www.geoportal.gov.pl` (PL)
- `vdp.cuzk.gov.cz`, `services.cuzk.gov.cz`, `ags.cuzk.cz` (CZ)
- `www.data.gv.at`, `data.wien.gv.at` (AT)
- `gdi.berlin.de`, `fbinter.stadt-berlin.de`, `daten.berlin.de` (DE Berlino)
- `geodienste.hamburg.de`, `daten.transparenz.hamburg.de`, `suche.transparenz.hamburg.de` (DE Amburgo)
- `www.opengeodata.nrw.de` (DE NRW)
- `urbisdownload.datastore.brussels`, `opendata.brussels.be`, `geo.api.vlaanderen.be` (BE)
- `www.geospatial.jp`, `front.geospatial.jp`, `www.mlit.go.jp` (JP PLATEAU)
- `data.gov.sg` (SG)
- `data.calgary.ca`, `data.edmonton.ca`, `open.toronto.ca` (CA)
- `data.wprdc.org` (Pittsburgh/Allegheny), `data.baltimorecity.gov`, `opendata.maryland.gov`, `mdgeodata.md.gov` (Baltimore)
- `data.seattle.gov`, `gisdata.kingcounty.gov` (Seattle)
- `data.detroitmi.gov` (Detroit), `opendata.minneapolismn.gov` (Minneapolis), `www.denvergov.org` (Denver), `data-cagis.hub.arcgis.com` (Cincinnati), `data.nola.gov` (New Orleans), `www.portlandmaps.com` (Portland)
- `dom.gosuslugi.ru`, `www.reformagkh.ru`, `data.mos.ru` (RU)
- `dados.prefeitura.sp.gov.br`, `geosampa.prefeitura.sp.gov.br` (San Paolo)
- `data.linz.govt.nz` (NZ, solo impronte senza anno)

RIPIEGO MONDIALE
- `overpass-api.de`  [Certain]
- `download.geofabrik.de`  [Certain]
- `planet.openstreetmap.org`  [Certain]
- `human-settlement.emergency.copernicus.eu` (GHS-OBAT)  [Certain]
- `jeodpp.jrc.ec.europa.eu` (download GHSL)  [Likely]
- `ghsl.jrc.ec.europa.eu`  [Certain]
- `zenodo.org` (EUBUCCO, DBSM)  [Likely]
- `eubucco.com`  [Likely]
- `wiki.openstreetmap.org` (documentazione; WebFetch ha dato ENOTFOUND)  [Certain]
- `overturemaps-us-west-2.s3.amazonaws.com` (Overture buildings)  [Likely]

Host testati in questa sessione e risultati BLOCCATI (CONNECT 403): kartta.hel.fi, opendata.dc.gov, data.cityofnewyork.us, opendataphilly.org, data.cityofchicago.org, data.bs.ch, data.gv.at, geonorge.no, data.norge.no, www.geoportal.gov.pl, ags.cuzk.cz, services.arcgis.com, geodienste.hamburg.de, overpass-api.de, jeodpp.jrc.ec.europa.eu, human-settlement.emergency.copernicus.eu, ghsl.jrc.ec.europa.eu, data.stadt-zuerich.ch, ovc.catastro.meh.es, colouring.london, open.toronto.ca, donnees.montreal.ca, opendata.vancouver.ca, opendata.brussels.be, urbisdownload.datastore.brussels, geo.api.vlaanderen.be, api.pdok.nl, data.sfgov.org, data.lacity.org, hub.arcgis.com, opendata.arcgis.com, data.london.gov.uk, www.data.gouv.fr, files.data.gouv.fr, data.linz.govt.nz, www.mlit.go.jp, rosreestr.gov.ru e altri. Unico raggiungibile: `api.dataforsyningen.dk`.

(Nota: ovc.catastro.meh.es, api.pdok.nl, data.cityofnewyork.us e i dati FR risultano bloccati dal mio test anche se il proprietario li ha già usati: probabilmente in altre sessioni/ambienti la rete era diversa. Da riconfermare.)
