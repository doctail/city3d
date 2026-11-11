# Porto / Vila Nova de Gaia: dati anno di costruzione per edificio

Data ricerca: 2026-11-11. Metodo: solo WebSearch. WebFetch NON funziona: host non risolvibili
(da abilitare nella rete di sessione): inspire-geoportal.ec.europa.eu, cascais.pt,
wiki.openstreetmap.org, dados.gov.pt. Quindi nessun file e' stato aperto: tutto da snippet di ricerca.

## Verdetto: B (aggregato per subsezione statistica) [Likely]
Nessuna fonte aperta con anno/epoca per singolo edificio trovata per Porto/Gaia.
Il meglio e' INE BGRI 2021 (poligoni di subsezione con n. edifici per epoca) piu' la BGE (punti edificio, senza epoca confermata).
Va fatta assegnazione sintetica. Non e' come Copenaghen (BBR) o Spagna (Catastro).

## Tabella fonti

| Fonte | URL | Contenuto | Granularita' | Formato | Licenza | Accessibile |
|---|---|---|---|---|---|---|
| INE BGRI Censos 2021 | mapas.ine.pt/download/index2021.phtml | Subsezioni con n. edifici per epoca di costruzione. Campi (da layer Cascais derivato) tipo n_edificios_constr_antes_1945 ... 2011_2021 [Likely] | Poligono di subsezione (isolato/gruppo di isolati), non edificio | GeoPackage | INE, uso libero con citazione (CC BY 4.0 per i dataset INE su dados.gov.pt) [Likely] | Non verificato (WebFetch bloccato); sito INE pubblico [Likely] |
| INE BGE (Base Geografica de Edificios) | inspire-geoportal.ec.europa.eu record ad14e031-a2c1-4673-a85b-3b57b0df3767 | Edifici georeferenziati dai rilevatori nei Censos 2011, aggiornati 2021 (nuovi residenziali, posizioni corrette) | Punto per edificio [Likely]; non poligono | Non chiaro | Metadati INSPIRE: accesso pubblico senza restrizioni [Likely] | Non verificato. NON confermato che contenga epoca per edificio, ne' che sia scaricabile in bulk [Guessing: epoca probabilmente solo a livello statistico, per privacy] |
| INE Edificios por localizacao e epoca (tabelle) | dados.gov.pt/en/datasets/edificios-n-o-34 (e -2, -3) | N. edifici per epoca per unita' geografica | Freguesia/localita'/subsezione secondo dataset | CSV/XLSX | CC BY 4.0 | Host bloccato; esistenza confermata da snippet |
| INE indirizzi (inspire.ine.pt/AD/atom) | inspire.ine.pt/AD/atom | Punti indirizzo GML | Punto indirizzo | GML EPSG:4258 | Libera [Likely] | Non verificato (info da lista OSM 2021) |
| DGT INSPIRE Buildings / cadastro | geoportal DGT, SNIG | Nessun servizio WFS Buildings Portogallo trovato. BUPi/SiNErGIC copre soprattutto rustico/misto, solo pilota urbano | - | - | - | No [Likely]: il Portogallo non ha catasto urbano geometrico aperto con anno |
| CM Porto dati aperti | opendata.porto.digital | Trovato solo "Edificios dispersos de Habitacao Municipal" (edilizia pubblica) e statistiche licenziamento urbanistico dal 2010 (aggregate). Nessun layer edifici con anno | - | - | CC (portale) | Layer edifici con anno: non trovato [Likely]. Catalogo non esplorato a fondo |
| OpenStreetMap | openstreetmap.org | Impronte di Porto molto completate (campagna "Adding missing buildings in Porto" dic 2021-gen 2022, ortofoto DGT 25 cm 2018). Nessuna statistica trovata su start_date | Poligono edificio | PBF/Overpass | ODbL | Si (non provato da qui). Copertura start_date [Guessing]: <5% a Porto; verificare con Overpass/taginfo |
| GHS-AGE (GHSL) | registry.opendata.aws/ghs-age | Epoca mediana del costruito per cella | 100 m / 1 km; classi: <1980, 1980-90, 90-00, 00-10, 10-20 | GeoTIFF Mollweide | CC BY 4.0 [Likely] | Si [Likely]. Troppo grossolano: tutto Porto storico = "<1980" |
| GHS-OBAT (JRC, 2025) | JRC, report EUR 40214 | Attributi per edificio inclusi epoca di costruzione, altezza, uso | Per edificio, ma modellato | - | Da verificare | Copertura Europa/Portogallo non confermata [Guessing]. Epoca stimata, non reale |
| Microsoft / Google Open Buildings | github.com/microsoft/GlobalMLBuildingFootprints | Solo impronte, niente anno | Poligono | GeoJSON/Parquet | ODbL / CC BY | Si [Likely] |
| Cartografia storica Porto | Arquivo Municipal / Historico do Porto | Telles Ferreira 1892 (464 fogli 1:500, riduzione 1:5000 del 1895), Balck 1813 ("Planta Redonda"). Nessuna versione georeferenziata scaricabile trovata. Esiste digitalizzazione accademica (UP) | Raster | - | Da verificare | Georef non trovata; si puo' georeferenziare noi i fogli [Likely] |
| DEM | EEA / Copernicus Data Space | Copernicus DEM GLO-30 (30 m) sul CDSE; EU-DEM 25 m non piu' distribuito ufficialmente | 30 m | GeoTIFF | Libera | Si [Likely]. DGT ha MDT piu' fine (non confermato). Per il Douro: OSM/COS DGT per la sagoma del fiume; livelli acqua non trovati ma non servono [Likely] |

## Confronto

| | Copenaghen (BBR) | Spagna (Catastro INSPIRE) | Porto/Gaia |
|---|---|---|---|
| Impronta per edificio | si | si | si (OSM, MS) |
| Anno per edificio | si | si | no |
| Fallback | - | - | BGRI per subsezione (epoche) + cartografia 1892 |

## Quanto e' fine il fallback B [Guessing sulle cifre]
- Il comune di Porto ha circa 25-30 mila edifici (Censos 2011 ~ 28k) e circa 3-4 mila subsezioni BGRI [Guessing]: media 6-10 edifici per subsezione. Gaia: circa 3x gli edifici.
- Epoche INE: antes 1919 / 1919-45 / 46-60 / 61-70 / 71-80 / 81-90 / 91-00 / 01-10 / 11-21 [Likely, schema Censos 2011; il layer Cascais usa antes 1945 come primo taglio].
- Assegnazione: per ogni subsezione estrarre a sorte le epoche per gli edifici OSM secondo le proporzioni del conteggio, poi anno uniforme dentro l'epoca. Per i primi decenni vincolare con la carta 1892 (edificato gia' presente) e con il GHS-BUILT-S per le fasi dal 1975.
- Errore: epoca esatta a livello di isolato non garantita per l'edificio singolo, ma il totale per subsezione e' rispettato. Accettabile per un timelapse a scala citta'.

## Prossimi passi consigliati
1. Abilitare gli host bloccati (sopra) per verificare campi di BGRI 2021 e la BGE.
2. Scaricare BGRI 2021 via mapas.ine.pt e controllare i campi epoca (conferma o smentisce il verdetto B).
3. Overpass: contare edifici con start_date/building:year a Porto e Gaia.
4. Chiedere alla CM Porto (Arquivo Municipal / urbanismo) l'accesso ai dati di licenziamento georeferenziati (potrebbero dare l'anno per lotto).
