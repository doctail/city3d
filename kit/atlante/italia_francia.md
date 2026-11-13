# Italia + Francia: anno di costruzione per edificio (Year Built) - 13/11/2026

Stato: RICERCA PARZIALE. La misura OSM non e' stata completata (Overpass e Geofabrik resettano la connessione) e la maggior parte dei portali ufficiali e' bloccata dal proxy (CONNECT 403). Nessun dato di copertura e' misurato in questo file. Le voci sono tutte [Likely] o [Guessing] salvo dove indicato.

Legenda: [Certain] misurato/letto; [Likely] inferenza forte o ricerca web; [Guessing] ipotesi da verificare.
Voti: A = anno per edificio, copertura >=70% nel centro, scaricabile. B = anno per edificio ma 35-70%, o solo per parti, o host/licenza da sbloccare. C = solo classi di eta' / stime / nessun dato.

---

## 1. Stato della rete (misurato)

| Host | Esito | Note |
|---|---|---|
| overpass-api.de | RESET (ws_closed_mid_exchange) | 5 tentativi, tunnel aperto ma chiuso dopo 2-3 s. Stesso errore per download.geofabrik.de. Non e' un 403: e' un problema di relay. |
| download.geofabrik.de | RESET | idem |
| overpass.kumi.systems, lz4/z.overpass-api.de, overpass.openstreetmap.fr | 403 | mirror Overpass alternativi bloccati |
| www.openstreetmap.org, api.openstreetmap.org | 403 | |
| nominatim.openstreetmap.org | 302 (raggiungibile) | non usato per la misura |
| data.gouv.fr, www.data.gouv.fr, files.data.gouv.fr | 403 | blocca BDNB, BD TOPO, DVF, cadastre |
| api-adresse.data.gouv.fr, cadastre.data.gouv.fr, data.geopf.fr | 403 | Base Adresse, cadastre, WMTS IGN |
| bdnb.io, geoservices.ign.fr | 403 | |
| www.istat.it | 403 | sezioni censuarie |
| dati.comune.milano.it, opendata.comune.torino.it, opendata.comune.bologna.it, dati.comune.bologna.it | 403 | |
| api.dataforsyningen.dk | 404 (raggiungibile) | solo Danimarca, fuori area |

Il proxy registra ancora 7 tunnel aperti e nessun collo di bottiglia: il problema e' la policy (403) e il relay (reset su Overpass).

---

## 2. Fonti Francia (ricerca web, non verificata su pagina)

| Fonte | Campo anno | Stato | Copertura | Voto | Tag |
|---|---|---|---|---|---|
| BDNB (data.gouv.fr, bdnb.io) | annee_construction (nome campo non confermato) | Ricerca conferma che la "carte d'identite" del batiment include l'anno di costruzione, insieme a logements, surfaces, materiaux. Licenza Licence Ouverte. Millesimi trimestrali (es. 2025-07.a) | Non misurata; dipende da FF (vedi sotto). Buchi fuori dai grandi centri | B (provvisorio) | [Likely] campo; [Guessing] copertura |
| BD TOPO IGN | date_d_apparition | Ricerca: e' la data di "nascita" sul terreno, NON l'anno di costruzione. Nessuna evidenza di data di costruzione nella tabella bati | - | C per questo scopo | [Likely] |
| Fichiers fonciers (FF, CEREMA datafoncier) | Annee de construction | Ricerca CEREMA: l'anno di costruzione viene dai FF, non da IGN. Fonte primaria per BDNB | Non misurata. Dati per parcella/locale, accesso via datafoncier.cerema.fr | A/B (da verificare) | [Likely] |
| Base Adresse Nationale | nessun anno | Solo indirizzi/coordinate: serve come join | - | - | [Certain] schema generale |
| DVF | nessun anno | Solo transazioni: non usare per anno costruzione | - | - | [Likely] |
| Cadastre (PCI vecteur) | nessun anno | Parcelle e geometrie | - | - | [Likely] |

Conclusione Francia: la strada credibile e' BDNB (annee_construction, derivata da FF) con join su BD TOPO per le impronte. BD TOPO da sola non serve per l'anno.

---

## 3. Fonti Italia (ricerca web, non verificata su pagina)

| Fonte | Campo | Stato | Voto | Tag |
|---|---|---|---|---|
| ISTAT sezioni di censimento 2021 | epoca di costruzione per sezione (classi) | Basi territoriali e variabili censuarie confermate; geometrie shapefile WGS84 UTM32N (756.259 sezioni). Classi di epoca per edifici a livello sezione NON confermate dalla ricerca: da cercare nelle variabili definitive del Censimento 2021 | C/B (solo classi) | [Likely] esistenza geometrie; [Guessing] classi |
| Milano dati.comune.milano.it | origine/periodo costruzione scuole statali (a.s. 2020/21) | Dataset trovato, solo edifici scolastici | C per il centro | [Likely] |
| Milano CENED / ACE / APE (energia) | non confermato | Possibile anno di costruzione nei campi APE; da controllare | ? | [Guessing] |
| Torino, Bologna, Firenze, Trento, Bolzano | - | Nessun dataset con anno trovato in ricerca | ? | [Guessing] |
| Catasto (Agenzia Entrate) | anno costruzione non nei dati aperti | Accesso non verificato | C | [Guessing] |

Conclusione Italia: nessuna fonte A confermata. Il massimo realistico e' B/C (classi ISTAT a sezione, eventuali campi APE a Milano). Serve verifica di campo su pagina reale.

---

## 4. Tabella per citta'

Copertura OSM start_date nel centro: NON MISURATA (Overpass non raggiungibile). Tutte le citta' sono in attesa di misura.

### Italia

| Citta' | Fonte ufficiale | Host raggiungibile | Copertura OSM centro | Voto | Evento storico | Note |
|---|---|---|---|---|---|---|
| Milano | APE/CENED (campo da verificare); ISTAT sezioni (classi) | No (dati.comune 403) | non misurata | C/B? | Expo 1906/1915, Duomo | Dataset scuole trovato, solo scuole |
| Torino | nessun dataset trovato; ISTAT classi | No | non misurata | C | Barocco sabaudo, Mole | Portale comunale 403 |
| Bologna | nessun dataset trovato; ISTAT classi | No | non misurata | C | portici medievali | Portale 403 |
| Firenze | nessun dataset trovato; ISTAT classi | No | non misurata | C | centro UNESCO 1865-71 (risanamento) | Non cercato su portale |
| Genova | ISTAT classi | No | non misurata | C | caruggi, ricostruzioni post-bombardamento | Non cercato |
| Venezia | ISTAT classi | No | non misurata | C | acqua, palafitte | Non cercato |
| Palermo | ISTAT classi | No | non misurata | C | sismi/ricostruzioni | Non cercato |
| Bari | ISTAT classi | No | non misurata | C | Bari vecchia | Non cercato |
| Trieste | ISTAT classi | No | non misurata | C | asburgica | Non cercato |
| Verona | ISTAT classi | No | non misurata | C | Arena | Non cercato |

### Francia

| Citta' | Fonte ufficiale | Host raggiungibile | Copertura OSM centro | Voto | Evento storico | Note |
|---|---|---|---|---|---|---|
| Lione | BDNB annee_construction (da FF) | No (data.gouv/bdnb 403) | non misurata | B (provv.) | Vieux-Lyon, Croix-Rousse, Presqu'ile haussmanniana | Campo non confermato |
| Marsiglia | BDNB | No | non misurata | B (provv.) | Vieux-Port, distruzione 1943 | |
| Bordeaux | BDNB | No | non misurata | B (provv.) | Port de la Lune, 18 sec. | |
| Tolosa | BDNB | No | non misurata | B (provv.) | brique rosa, dopo 2001 AZF | |
| Nantes | BDNB | No | non misurata | B (provv.) | Ile de Nantes, post-industriale | |
| Strasburgo | BDNB (Alsazia: FF) | No | non misurata | B (provv.) | Petite France, Neustadt tedesca 1871-1918 | Neustadt: interessante per cambio di epoca |
| Lille | BDNB | No | non misurata | B (provv.) | Vieux-Lille, cotone | |
| Nizza | BDNB | No | non misurata | B (provv.) | Belle Epoque, ricostruzioni | |
| Montpellier | BDNB | No | non misurata | B (provv.) | Antigone, espansione recente | |

Parigi: gia' trattata (esclusa).

---

## 5. DA SBLOCCARE

Host da aprire per completare la ricerca (CONNECT 403 o reset, testati oggi):

- `overpass-api.de` - RESET mid-exchange (non 403). Serve verificare dal lato proxy o aggiungere un mirror permesso (`overpass.kumi.systems` e' 403). Blocca la misura OSM di tutte le citta'. [priorita' 1]
- `download.geofabrik.de` - RESET. Alternativa per estratti OSM regionali (italy-latest, france-latest). [priorita' 1]
- `data.gouv.fr`, `files.data.gouv.fr`, `www.data.gouv.fr` - 403. Blocca download BDNB e DVF. [priorita' 1]
- `bdnb.io` - 403. Dizionario dati BDNB e download dipartimentali. [priorita' 1]
- `cadastre.data.gouv.fr`, `api-adresse.data.gouv.fr` - 403. Cadastre e join indirizzi. [priorita' 2]
- `geoservices.ign.fr`, `data.geopf.fr` - 403. Descrittivo BD TOPO (verifica campi bati). [priorita' 2]
- `datafoncier.cerema.fr` - non testato (documentazione FF). [da testare]
- `www.istat.it` - 403. Variabili definitive Censimento 2021 per sezione (classi epoca). [priorita' 1]
- `dati.comune.milano.it` - 403. Verifica APE/CENED e dataset scuole. [priorita' 2]
- `opendata.comune.torino.it`, `opendata.comune.bologna.it`, `dati.comune.bologna.it` - 403. [priorita' 2]
- `opendata.comune.fi.it`, `dati.trentino.it`, `dati.comune.bolzano.it` - non testati. [da testare]

Nota: `overpass.kumi.systems`, `openstreetmap.org` e `api.openstreetmap.org` sono 403 e non sono in lista di sblocco salvo decisione diversa.

---

## 6. Prossimi passi

1. Ritentare Overpass quando il relay si stabilizza, con la query per la finestra centro di ogni citta' (conta way["building"] e con start_date).
2. Verificare nome campo BDNB (`annee_construction`) e campo BD TOPO bati su dizionario reale.
3. Verificare in ISTAT se le variabili 2021 per sezione includono epoca costruzione degli edifici (classi).
4. Solo dopo: scegliere citta' per voto A/B.

---

## MISURE 13/11 (pomeriggio)

Esito sintetico: Italia misurata a livello di sezione di censimento (dato 2011, classi di epoca, non per edificio). Francia NON misurata: il campione BDNB non e' scaricabile dal proxy (S3 403). Overpass/Geofabrik non usati (chiusi).

### Verifiche di rete e licenza (misurate oggi)

| Host / risorsa | Esito | Note |
|---|---|---|
| bdnb.io (pagine, /download/, /schema/latest/) | 200 | pagine di download e dizionario, nessun file dati |
| open-data.s3.fr-par.scw.cloud (file BDNB France/dipartimenti, dizionario xlsx) | 403 | policy: "connect_rejected". Blocca TUTTI i file BDNB |
| api.bdnb.io, api-portail.bdnb.io | 403 / 000 | API BDNB non raggiungibile |
| files.data.gouv.fr, www.data.gouv.fr (API) | 200 | metadati dataset OK, ma i file BDNB sono su S3 |
| gitlab.com (repo BDNB, wiki, api_columns.json) | 200 | documentazione campi e metodo, letta |
| www.istat.it (pagine, nota informativa, nota metodologica, zip 2011) | 200 | scaricato zip 2011 (52 MB) |
| esploradati.istat.it (zip sezioni 2021 e 2023) | 403 | file 2021/2023 per sezione NON scaricabili |
| datafoncier.cerema.fr | 000 | non raggiunto (tunnel non aperto), non verificato oltre |
| portali open data metropolitani (data.grandlyon.com, opendata.bordeaux-metropole.fr, data.nantesmetropole.fr, data.strasbourg.eu, opendata.lillemetropole.fr, data.toulouse-metropole.fr, data.nicecotedazur.org, data.montpellier3m.fr, data.marseille.fr) | 403 / 000 | nessun dataset per citta' raggiungibile |

Licenze verificate: BDNB su data.gouv = "lov2" (Licence Ouverte 2.0) [Certain, da API data.gouv]. Documentazione metodologica BDNB (wiki GitLab) = CC BY-SA 4.0 [Certain]. ISTAT = CC BY 4.0 [Certain, pagina note legali].

Campo BDNB verificato: `annee_construction` = "Annee de construction du batiment", livello open, tiles_open = x [Certain, da api_columns.json del repo GitLab]. Per il metodo: la fonte primaria dell'anno e' CEREMA Fichiers Fonciers (priorita' 1), poi RNC e RPLS, poi DPE [Certain, wiki "fiabilite_periode_construction"]. L'anno e' a livello batiment_groupe (unita' di parcella), non per geometria di edificio: per gruppi multi-edificio vale l'anno con la maggiore somma di superfici [Certain, wiki Changelog]. Quindi anche con dati scaricati la granularita' e' "per gruppo di edifici", non "per edificio".

### Italia: ISTAT Censimento 2011, sezioni di censimento (dati scaricati, misura reale)

Fonte: dati-cpa_2011.zip (www.istat.it/storage/cartografia/variabili-censuarie/), file "R*_indicatori_2011_sezioni.csv" (tutte le regioni), variabili E3 (edifici ad uso residenziale) ed E8-E16 (classi di epoca: prima del 1919 ... dopo il 2005). Somma delle classi = E3 nel 100% dei casi, quindi la partizione e' completa. Conteggio di edifici su comune intero, non sul centro storico.

| Citta' | Fonte | Edifici (E3 residenziali) | % con anno | Voto | Note |
|---|---|---|---|---|---|
| Milano | ISTAT 2011 sezioni, classi E8-E16 | 42.980 (E1 totali 65.516) | 100% in classi, 0% per edificio | C | pre1919 12,4% / 1919-45 23,5% / 1946-60 27,7% / 1961-70 19,9% / 1971-80 8,6% / 1981-90 2,9% / 1991-2000 2,0% / 2001-05 1,5% / post2005 1,5%. Comune intero, centro non filtrato (geometrie sezioni non scaricate). 6.017 sezioni |
| Torino | ISTAT 2011 sezioni | 36.158 (E1 63.764) | 100% in classi | C | pre1919 14,3% / 1919-45 20,8% / 1946-60 28,1% / 1961-70 20,8% / 1971-80 9,3% / 1981-90 3,0% / 1991-2000 1,9% / 2001-05 1,2% / post2005 0,6%. 3.713 sezioni |
| Bologna | ISTAT 2011 sezioni | 22.149 (E1 29.368) | 100% in classi | C | pre1919 20,7% / 1919-45 21,4% / 1946-60 29,0% / 1961-70 14,5% / 1971-80 5,9% / 1981-90 2,7% / 1991-2000 2,9% / 2001-05 1,7% / post2005 1,2%. 2.260 sezioni |
| Firenze | ISTAT 2011 sezioni | 31.070 (E1 46.281) | 100% in classi | C | pre1919 35,5% / 1919-45 28,9% / 1946-60 19,0% / 1961-70 10,2% / 1971-80 3,7% / 1981-90 1,1% / 1991-2000 0,7% / 2001-05 0,4% / post2005 0,5%. 2.070 sezioni |
| Genova | ISTAT 2011 sezioni | 29.668 (E1 37.960) | 100% in classi | C | pre1919 43,4% / 1919-45 20,1% / 1946-60 18,9% / 1961-70 10,8% / 1971-80 4,0% / 1981-90 1,8% / 1991-2000 0,3% / 2001-05 0,2% / post2005 0,3%. 3.458 sezioni |
| Venezia | ISTAT 2011 sezioni | 34.994 (E1 40.914) | 100% in classi | C | pre1919 26,6% / 1919-45 8,0% / 1946-60 23,1% / 1961-70 20,8% / 1971-80 9,2% / 1981-90 5,0% / 1991-2000 3,2% / 2001-05 2,1% / post2005 1,9%. 3.476 sezioni |
| Palermo | ISTAT 2011 sezioni | 46.293 (E1 57.015) | 100% in classi | C | pre1919 11,9% / 1919-45 18,4% / 1946-60 17,1% / 1961-70 18,5% / 1971-80 15,6% / 1981-90 11,6% / 1991-2000 5,0% / 2001-05 1,4% / post2005 0,4%. 2.834 sezioni |
| Bari | ISTAT 2011 sezioni | 23.252 (E1 28.041) | 100% in classi | C | pre1919 12,4% / 1919-45 18,9% / 1946-60 17,5% / 1961-70 22,7% / 1971-80 16,1% / 1981-90 6,6% / 1991-2000 3,7% / 2001-05 1,4% / post2005 0,6%. 1.451 sezioni |
| Trieste | ISTAT 2011 sezioni | 22.638 (E1 27.244) | 100% in classi | C | pre1919 31,7% / 1919-45 14,6% / 1946-60 18,2% / 1961-70 14,9% / 1971-80 7,9% / 1981-90 4,6% / 1991-2000 3,5% / 2001-05 2,1% / post2005 2,4%. 908 sezioni |
| Verona | ISTAT 2011 sezioni | 25.393 (E1 30.312) | 100% in classi | C | pre1919 18,6% / 1919-45 13,8% / 1946-60 19,5% / 1961-70 18,1% / 1971-80 11,1% / 1981-90 6,9% / 1991-2000 4,9% / 2001-05 3,5% / post2005 3,6%. 1.954 sezioni |

ISTAT 2021/2023 per sezione: la nota informativa (9/06/2026) dichiara sezioni di censimento e aree subcomunali per regione e per capoluoghi di Citta' Metropolitana, ma le variabili diffuse sono popolazione, famiglie, automobili e "informazioni sulle abitazioni e gli altri tipi di alloggio". Le classi di epoca degli EDIFICI non sono citate [Likely: assenti]. I file 2021 sono su esploradati.istat.it, 403. Per questo, il dato 2021 per epoca NON e' misurato. Il 2011 e' l'ultimo anno con classi di epoca degli edifici a livello sezione, confermato dal tracciato.

### Francia: BDNB annee_construction (NON misurata)

| Citta' | Fonte | Edifici | % con anno | Voto | Note |
|---|---|---|---|---|---|
| Lione | BDNB annee_construction (da Fichiers Fonciers) | n.d. | n.d. | B (provv., non misurato) | file S3 403, nessun campione. Vieux-Lyon/Croix-Rousse non filtrabili |
| Marsiglia | idem | n.d. | n.d. | B (provv., non misurato) | idem |
| Bordeaux | idem | n.d. | n.d. | B (provv., non misurato) | idem |
| Tolosa | idem | n.d. | n.d. | B (provv., non misurato) | idem |
| Nantes | idem | n.d. | n.d. | B (provv., non misurato) | idem |
| Strasburgo | idem | n.d. | n.d. | B (provv., non misurato) | idem. Neustadt 1871-1918 da verificare |
| Lille | idem | n.d. | n.d. | B (provv., non misurato) | idem |
| Nizza | idem | n.d. | n.d. | B (provv., non misurato) | idem |
| Montpellier | idem | n.d. | n.d. | B (provv., non misurato) | idem |

Il voto B e' provvisorio: il campo esiste ed e' open, ma l'anno e' per gruppo di edifici (non per edificio) e la copertura non e' misurata. Non posso dire se supera il 70%.

### Confidenza

- [Certain] Host S3 BDNB, data.gouv API, GitLab, ISTAT pagine e zip 2011: esiti misurati oggi.
- [Certain] Campo annee_construction, fonte FF prioritaria, granularita' batiment_groupe, licenze lov2 / CC BY 4.0.
- [Certain] Dati ISTAT 2011 per sezione, classi di epoca per comune: somme verificate (classi = E3 al 100%).
- [Likely] ISTAT 2021/2023 senza classi di epoca degli edifici: dalla nota informativa, non dal file.
- [Guessing] Copertura % del campo BDNB annee_construction per citta': non misurabile senza file.

### DA SBLOCCARE

- `open-data.s3.fr-par.scw.cloud` - 403 policy. Blocca TUTTI i file BDNB (csv/gpkg/pgdump France 40-52 GB, dipartimenti da estrarre, dizionario xlsx 243 KB). Sblocco prioritario: senza questo la Francia resta non misurata. [priorita' 1]
- `api.bdnb.io` - 403. Alternativa API per campione (annee_construction per batiment_groupe su un comune). [priorita' 2]
- `esploradati.istat.it` - 403. Zip sezioni 2021 (Dati_regionali_2021.zip) e 2023: serve per verificare se il 2021 ha classi di epoca degli edifici. [priorita' 1]
- `datafoncier.cerema.fr` - 000 (tunnel non aperto). Fichiers Fonciers per parcella, fonte primaria BDNB. [priorita' 2]
- `api-portail.bdnb.io` - 000. Catalogo API BDNB. [priorita' 3]
- Portali open data metropolitani: data.grandlyon.com, opendata.bordeaux-metropole.fr, data.nantesmetropole.fr, data.strasbourg.eu, opendata.lillemetropole.fr, data.toulouse-metropole.fr, data.nicecotedazur.org, data.montpellier3m.fr, data.marseille.fr - 403/000. Possibili dataset annee_construction locali. [priorita' 3]
