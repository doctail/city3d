# Altre grandi citta' europee + Mosca e San Pietroburgo: anno di costruzione per edificio (13/11/2026)

Metodo: WebSearch (max 2 per paese, modo standard) + test host con `curl -m 15`. Overpass e Geofabrik NON usati (indicati come morti). Nessun dato scaricato: tutti gli host testati sono bloccati dal proxy.

## 0. Esito test di rete (leggere prima)

- Tutti gli host testati (circa 110) danno `000`: il proxy risponde `CONNECT tunnel failed, response 403` (policy di rete, non errore del sito). Nessun host dell'area risulta raggiungibile.
- Quindi non e' stato verificato nessun campo, nessun URL di download e nessuna licenza su pagina viva. Le informazioni sotto vengono solo dai risultati di ricerca: tag [Likely] o [Guessing] dove non confermate.
- Nessun host risulta "200" ne' "403 HTTP" (il proxy blocca prima del TLS): il codice reale e' 000 per tutti.

## 1. Tabella citta'

Voto: A = anno per edificio, copertura >=70% centro, scaricabile. B = per edificio ma parziale, o solo aggregati/lotti/host da sbloccare. C = niente o solo classi di eta'.
Evento storico: il fatto spettacolare piu' citato per la citta'.

| Citta' | Paese | Fonte ufficiale (anno per edificio?) | Host / test | Copertura anno | Voto | Evento spettacolare | Note |
|---|---|---|---|---|---|---|---|
| Varsavia | PL | BDOT10k (OT_BUBD_A), "rok budowy" [Likely] nel modello, nome attributo non confermato | opendata.geoportal.gov.pl 000, integracja.gugik.gov.pl 000, www.geoportal.gov.pl 000 | non misurata [Guessing] | C/B | Insurrezione di Varsavia 1944 e distruzione ~85% del centro (storia certa) | Dati BDOT10k aperti per powiat; fonte "vademecum" 2024 da leggere per il nome del campo |
| Cracovia | PL | BDOT10k, stesso schema di Varsavia | come sopra, 000 | non misurata | C/B | Assedio/occupazione tedesca 1939-45; centro storico quasi intatto (Likely) | Centro UNESCO, pochi cambi: l'anno servirebbe per il contrasto medievale/moderno |
| Praga | CZ | RUIAN: data di completamento dello stavební objekt, campo nel VFR; per la quasi totalita' degli edifici storici popolato in modo incompleto (Likely) | vdp.cuzk.gov.cz 000, vdp.cuzk.cz 000, services.cuzk.gov.cz 000 | non misurata | B (satura: solo nota) | Alluvione Moldava/Vltava 2002 (Likely) | Citta' satura da 1,49M: solo nota, non produrre |
| Budapest | HU | Nessun registro aperto per edificio trovato; KSH tabelle aggregate per epoca; censimento solo come microdato | www.ksh.hu 000, data.gov.hu 000, opendata.budapest.hu 000, www.geoportal.hu 000 | aggregata (C per edificio) | C | Assedio di Budapest 1944-45 (~50 giorni), ponti distrutti (Certain) | Catasto Budapest brownfield: non e' eta' edifici |
| Bratislava | SK | Nessun dataset aperto con rok výstavby confermato; Bratislava ha uno strato edifici 2018 (geodetic documentation) senza anno confermato | zbgis.skgeodesy.sk 000, data.bratislava.sk 000, data.gov.sk 000, kataster.vugk.sk non testato | non misurata | C | Bombardamenti 1944 (Likely) | Kataster ha dati registrati ma non confermati aperti |
| Bruxelles | BE | UrbIS Buildings: anno non confermato; Fiandre GRB senza anno [Likely] | urbisdownload.datastore.brussels 000, opendata.brussels.be 000, geo.api.vlaanderen.be 000 | non misurata | C/B | Bombardamento di Bruxelles 1695 (Grand-Place, Certain) | Gia' citato nel protocollo come "su richiesta" per UrbIS completo |
| Anversa | BE | Nessun dato trovato in ricerca; opendata.antwerpen.be non verificato | opendata.antwerpen.be 000 | non misurata | C | Sacco di Anversa 1576 (Spanish Fury, Certain) | Ricerca non ha trovato il dataset |
| Gand | BE | Nessun dato trovato; data.gent.be non verificato | data.gent.be 000 | non misurata | C | Rivolta contro Carlo V 1539-40 (Likely) | Idem Anversa |
| Zurigo | CH | GWR cantonale/cittadino: `gbauj` (Baujahr) con `gwr_egid` in geolion.zh.ch (Likely); citta' con dataset GWR tagesaktuell (ricerca, schema non verificato) | data.geo.admin.ch 000, public.madd.bfs.admin.ch 000, opendata.swiss 000, data.stadt-zuerich.ch 000 | non misurata (GWR e' per punto, join EGID) | B/A (da verificare) | Nessun evento certo trovato (Guessing) | Migliore candidato dell'area dopo Helsinki; il campo gbauj e' la chiave |
| Basilea | CH | GWR (data.bs.ch citato, confermato da ricerca precedente) | data.bs.ch 000, data.geo.admin.ch 000 | non misurata | B | Terremoto di Basilea 1356 (Certain) | Stesso pattern di Zurigo |
| Oslo | NO | Matrikkelen Bygningspunkt (CC BY 4.0): nei campi trovati non appare anno di costruzione; utilizzata versione "utvidet" come alternativa | nedlasting.geonorge.no 000, kartkatalog.geonorge.no 000, wfs.geonorge.no 000, data.norge.no 000, oslo.kommune.no 000, api.kartverket.no 000 | non misurata | C/B (Guessing) | Grande incendio di Christiania 1624 (Certain) | Verificare il GetCapabilities prima di decidere; API Matrikkel non aperta |
| Stoccolma | SE | Lantmateriet Byggnad: poligoni aperti da feb 2025 (CC BY 4.0, da fonte secondaria); campo "tillbyggnadsår" esiste nello schema, byggnadsår non confermato | api.lantmateriet.se 000, geotorget.lantmateriet.se 000, opendata-download-geodata.lantmateriet.se 000, dataportal.stockholm.se 000 | non misurata | C (gia' scartata) | Nessun evento certo (Guessing) | Confermata scartata dal proprietario, tenuta solo come riferimento |
| Helsinki | FI | Rakennukset_alue / rekisteritiedot WFS, campo `c_valmpvm` (data di completamento) confermato da hri.fi/avoindata.fi | kartta.hel.fi 000 (gia' noto), hri.fi 000, kartta.hsy.fi 000, www.avoindata.fi 000 | non misurata; avviso: prima del 1981 dati meno affidabili | A/B (campo esiste, copertura da misurare) | Bombardamenti sovietici 1944 (Guessing); assedio no | Candidato piu' facile quando la rete c'e' |
| Dublino | IE | Nessun registro open con anno; GeoDirectory (commerciale) ha il build year | data.gov.ie 000, data.geohive.ie 000, www.osi.ie 000 | nessuna | C | Rivolta di Pasqua 1916: bombardamento GPO (Certain) | Licenza GeoDirectory non aperta |
| Lisbona | PT | BGRI Censos 2021: epoca per subsezione (aggregato); Lisbona ha 8.322 edifici pre-1919 nel 2021 (dato ricerca) | mapas.ine.pt 000, dados.gov.pt 000, dados.cm-lisboa.pt 000 | aggregata | B (satura: solo nota) | Terremoto e tsunami 1755 (Certain) | Gia' nota; non produrre |
| Atene | GR | Cadastro/Ktimatologio: portale data.ktimatologio.gr con sezione edifici, campo anno non confermato | data.gov.gr 000, geodata.gov.gr 000, ktimatologio.gr 000 | non misurata | C/B | Esplosione del Partenone 1687 durante assedio veneziano (Certain) | Gia' nota come satura; nota |
| Zagabria | HR | Nessun dato trovato | data.gov.hr 000, geoportal.dgu.hr 000, data.zagreb.hr 000 | nessuna | C | Terremoto di Zagabria 1880 (Certain) | |
| Lubiana | SI | Dato commerciale (Targomo) per periodo di costruzione; nessun aperto trovato | egp.gu.gov.si 000, podatki.gov.si 000, www.ljubljana.si 000 | nessuna | C | Terremoto di Lubiana 1895 (Certain) | |
| Riga | LV | Cadastre VZD: anno di messa in servizio, accesso limitato; nessun bulk aperto confermato | data.gov.lv 000, kadastrs.lv 000, data.riga.lv 000 | non misurata | C | Non trovato evento certo (Guessing) | |
| Tallinn | EE | Ehitisregister EHR: CSV giornaliero, dati dal 1994; campo anno "impresso nel portale" ma non confermato nel CSV (Likely) | livekluster.ehr.ee 000, ehr.ee 000, geoportaal.maaamet.ee 000, avaandmed.eesti.ee 000 | non misurata | B (da verificare) | Bombardamento sovietico di Tallinn 9 marzo 1944 (Likely) | Impronte da Maa-amet; join necessario |
| Vilnius | LT | Registrucentras: "anno di costruzione" nel registro, bulk aperto non confermato | registrucentras.lt 000, data.gov.lt 000, www.geoportal.lt 000, data.vilnius.lt 000 | nessuna | C | Distruzione di parte del centro nel 1944 alla ritirata tedesca (Likely) | |
| Bucarest | RO | Nessun dato trovato | data.gov.ro 000, geoportal.ancpi.ro 000, www.pmb.ro 000 | nessuna | C | Bombardamento alleato 4 aprile 1944 (Certain); terremoto 1940 (Certain) | |
| Sofia | BG | Nessun dato aperto con anno trovato (solo export OSM senza anno) | data.egov.bg 000, kais.cadastre.bg 000, www.sofia.bg 000 | nessuna | C | Bombardamenti alleati 1944 (Likely) | |
| Belgrado | RS | RGZ Building Register (record of changes, a3.geosrbija.rs): anno non confermato; RZS censimento solo aggregato | data.gov.rs 000, katastar.rgz.gov.rs 000, geosrbija.rgz.gov.rs 000 | aggregata | C/B | Bombardamento aereo 6 aprile 1941 e 1944 (Certain) | |
| Mosca | RU | data.mos.ru: footprint con 19 attributi via API (anno non confermato); GIS ZhKH / reformagkh: anno solo per condomini (MKD). Rosreestr PKK: non aperto | dom.gosuslugi.ru 000, www.reformagkh.ru 000, data.mos.ru 000, pkk.rosreestr.ru 000, nspd.gov.ru 000 | solo condomini (B/C) | C/B | Incendio di Mosca 1812 durante l'occupazione napoleonica (Certain) | Vedi sezione 3 (rischio) |
| San Pietroburgo | RU | GISOGD (open data) non trovato in ricerca; "How old is this house" = visualizzazione, non dataset; 2GIS = commerciale | data.gov.spb.ru 000, gisogd.gov.spb.ru 000 | non misurata | C | Assedio di Leningrado 1941-44, ~872 giorni (Certain) | Vedi sezione 3 |

Riepilogo voti: A/B da verificare: Helsinki, Zurigo, Basilea, Tallinn, Oslo (C/B). Tutte le altre C o B aggregate.

## 2. Ripiego OSM (non usato)

Il protocollo chiede conteggio via Overpass, ma Overpass e' dichiarato morto dal proprietario e risulta comunque 403 nei test precedenti: nessuna misura di copertura OSM fatta in questa ricerca. Da fare appena la rete c'e' (con altra fonte, es. dump OSM in altro modo).

## 3. Mosca e San Pietroburgo: rischio e fattibilita' (valutazione onesta)

- Dati: il dato per edificio aperto e' limitato ai condomini (MKD, GIS ZhKH/reformagkh). Il footprint Mosca (data.mos.ru, 145.000+ edifici) e' via API e il campo anno non e' confermato. San Pietroburgo: GISOGD non trovato, nessun bulk aperto confermato.
- Sanzioni e sensibilita': dal 2022 l'accesso dall'estero a portali russi e' spesso bloccato o condizionato; i dati di Rosreestr non sono aperti; contenuti su Mosca/San Pietroburgo possono essere politicamente sensibili per il pubblico e per la piattaforma. Il rischio di blocco (rete, verifica, reputazione) e' alto.
- Valutazione: fattibilita' BASSA nel breve periodo. Se si fa, conviene partire da San Pietroburgo solo se si trova un bulk GISOGD con anno; altrimenti scartare. Non raccomandato come prossima citta'.

## 4. DA SBLOCCARE (host esatti, tutti 403/000 al test)

Priorita' alta (fonti A/B candidate):
- `kartta.hel.fi` (WFS Helsinki, c_valmpvm) [Certain esistenza campo]
- `hri.fi` (catalogo Helsinki) [Certain]
- `kartta.hsy.fi` (HSY, area metropolitana) [Likely]
- `www.avoindata.fi` (catalogo Finlandia) [Likely]
- `geolion.zh.ch` (Zurigo/Canton, gbauj) [Likely]
- `data.geo.admin.ch` (swisstopo, GWR) [Likely]
- `public.madd.bfs.admin.ch` (download GWR) [Likely]
- `opendata.swiss` (catalogo CH) [Certain]
- `data.stadt-zuerich.ch` (Zurigo GWR) [Likely]
- `data.bs.ch` (Basilea) [Certain]
- `data.gov.ie` / `data.geohive.ie` (Dublino, da verificare) [Guessing]

Priorita' media (campo da verificare):
- `opendata.geoportal.gov.pl`, `integracja.gugik.gov.pl`, `www.geoportal.gov.pl` (BDOT10k, Varsavia/Cracovia)
- `vdp.cuzk.gov.cz`, `vdp.cuzk.cz`, `services.cuzk.gov.cz` (RUIAN, Praga)
- `urbisdownload.datastore.brussels`, `opendata.brussels.be`, `geo.api.vlaanderen.be` (Bruxelles/Fiandre)
- `opendata.antwerpen.be`, `data.gent.be` (Anversa, Gand)
- `nedlasting.geonorge.no`, `kartkatalog.geonorge.no`, `wfs.geonorge.no`, `data.norge.no`, `oslo.kommune.no` (Oslo)
- `api.lantmateriet.se`, `geotorget.lantmateriet.se`, `opendata-download-geodata.lantmateriet.se` (Stoccolma, poligoni Byggnad)
- `livekluster.ehr.ee`, `ehr.ee`, `avaandmed.eesti.ee`, `geoportaal.maaamet.ee` (Tallinn, EHR)
- `data.gov.hu`, `www.ksh.hu` (Budapest, da verificare)
- `data.gov.sk`, `zbgis.skgeodesy.sk`, `kataster.vugk.sk`, `data.bratislava.sk` (Bratislava)
- `dados.gov.pt`, `dados.cm-lisboa.pt` (Lisbona, BGRI/edifici)
- `data.ktimatologio.gr`, `data.gov.gr` (Atene)
- `registrucentras.lt`, `data.gov.lt`, `www.geoportal.lt` (Vilnius)
- `data.gov.lv`, `kadastrs.lv`, `data.riga.lv` (Riga)
- `a3.geosrbija.rs`, `data.gov.rs` (Belgrado, Building Register)
- `dom.gosuslugi.ru`, `www.reformagkh.ru`, `data.mos.ru` (Mosca, MKD + footprint)
- `data.gov.spb.ru`, `gisogd.gov.spb.ru` (San Pietroburgo)

Non prioritari: `data.gov.hr`, `data.zagreb.hr`, `egp.gu.gov.si`, `podatki.gov.si`, `data.gov.ro`, `data.egov.bg`, `kais.cadastre.bg`, `wikimapia.org` (non testato a fondo, nessun dato di anno atteso).

Non da sbloccare (fuori scopo o bloccati per scelta): `overpass-api.de`, `download.geofabrik.de` (dichiarati morti dal proprietario).

Nota: per tutti questi host il codice e' 000, cioe' CONNECT 403 dal proxy. Lo sblocco e' una modifica della policy di rete, non un problema del sito.

## 5. Tabella sintetica (per citta')

| Citta' | Voto | Tag |
|---|---|---|
| Helsinki | A/B | [Certain] campo; [Likely] copertura |
| Zurigo | B/A | [Likely] |
| Basilea | B | [Likely] |
| Tallinn | B | [Likely] |
| Oslo | C/B | [Guessing] |
| Stoccolma | C | [Guessing] (gia' scartata) |
| Varsavia, Cracovia | C/B | [Guessing] |
| Praga | B (satura) | [Guessing] stato attuale |
| Bruxelles, Anversa, Gand | C/B | [Guessing] |
| Budapest, Bratislava, Dublino, Riga, Vilnius, Bucarest, Sofia, Zagabria, Lubiana | C | [Guessing] |
| Belgrado | C/B | [Guessing] |
| Lisbona, Atene | B/C (sature) | [Certain] aggregato |
| Mosca, San Pietroburgo | C/B (rischio alto) | [Guessing] |
