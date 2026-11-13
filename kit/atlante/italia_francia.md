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
