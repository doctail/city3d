# Fonti per la datazione delle strade di Lione

Autore: yb-historian. Tutte le pagine sotto sono state realmente lette il 2026-11-13 (via WebFetch/curl). Gli ID S17+ proseguono la numerazione di `story.json` (S1-S16); S8 (en.wikipedia "Lyon from the First to the Second Empire") e S16 (Nominatim) restano quelli esistenti.

## Fonti usate
| ID | Pagina | URL |
|---|---|---|
| S17 | fr.wikipedia, Rue de la République (Lyon) | https://fr.wikipedia.org/wiki/Rue_de_la_République_(Lyon) |
| S18 | fr.wikipedia, Cours Gambetta | https://fr.wikipedia.org/wiki/Cours_Gambetta |
| S19 | fr.wikipedia, Liste des quais de Lyon | https://fr.wikipedia.org/wiki/Liste_des_quais_de_Lyon |
| S20 | fr.wikipedia, Tunnel de la Croix-Rousse | https://fr.wikipedia.org/wiki/Tunnel_de_la_Croix-Rousse |
| S21 | fr.wikipedia, Rue Édouard-Herriot | https://fr.wikipedia.org/wiki/Rue_Édouard-Herriot |
| S22 | fr.wikipedia, Rue du Président-Carnot | https://fr.wikipedia.org/wiki/Rue_du_Président-Carnot |
| S23 | fr.wikipedia, Cours Lafayette | https://fr.wikipedia.org/wiki/Cours_Lafayette |
| S24 | fr.wikipedia, Cours Vitton | https://fr.wikipedia.org/wiki/Cours_Vitton |
| S25 | fr.wikipedia, Cours Franklin-Roosevelt (Lyon) | https://fr.wikipedia.org/wiki/Cours_Franklin-Roosevelt_(Lyon) |
| S26 | fr.wikipedia, Cours Charlemagne | https://fr.wikipedia.org/wiki/Cours_Charlemagne |
| S27 | fr.wikipedia, Avenue Berthelot (Lyon) | https://fr.wikipedia.org/wiki/Avenue_Berthelot_(Lyon) |
| S28 | fr.wikipedia, Tunnel de Fourvière | https://fr.wikipedia.org/wiki/Tunnel_de_Fourvière |
| S29 | fr.wikipedia, Avenue du Maréchal-de-Saxe | https://fr.wikipedia.org/wiki/Avenue_du_Maréchal-de-Saxe |
| S30 | fr.wikipedia, Rue Garibaldi (Lyon) | https://fr.wikipedia.org/wiki/Rue_Garibaldi_(Lyon) |
| S31 | fr.wikipedia, Cours de la Liberté | https://fr.wikipedia.org/wiki/Cours_de_la_Liberté |
| S32 | fr.wikipedia, Part-Dieu | https://fr.wikipedia.org/wiki/Part-Dieu |
| S33 | fr.wikipedia, Lyon Confluence | https://fr.wikipedia.org/wiki/Lyon_Confluence |
| S34 | fr.wikipedia, Boulevard périphérique de Lyon | https://fr.wikipedia.org/wiki/Boulevard_périphérique_de_Lyon |
| S35 | fr.wikipedia, Liste des ponts de Lyon (letta solo fino a char 100000 di 115173) | https://fr.wikipedia.org/wiki/Liste_des_ponts_de_Lyon |
| S36 | fr.wikipedia, Pont Lafayette (Lyon) | https://fr.wikipedia.org/wiki/Pont_Lafayette_(Lyon) |
| S37 | fr.wikipedia, Quai Claude-Bernard | https://fr.wikipedia.org/wiki/Quai_Claude-Bernard |
| S38 | en.wikipedia, Part-Dieu (letta fino a char 100000 di 119672) | https://en.wikipedia.org/wiki/Part-Dieu |
| S39 | Grand Lyon WFS, layer `adr_voie_lieu.adrlineairevoie` (assi stradali, WGS84) | https://data.grandlyon.com/geoserver/metropole-de-lyon/ows |

Nota: WebFetch su fr.wikipedia restituisce un riassunto, non il testo; i valori vanno ricontrollati sulle pagine prima di una pubblicazione. Pagine 404 (titolo sbagliato): Rue_Édouard-Herriot_(Lyon), Rue_Président-Carnot_(Lyon), Boulevard_Laurent-Bonnevay(_(Lyon)), Boulevard_périphérique_Nord_de_Lyon.

## Discordanze e punti non confermati
- Rue de la République: proprietario dice 1853-56. Letto: piano Vaïsse 1853, esproprio 31/5/1854, nome Impériale 1862 (infobox "seconda metà XIX"). Il 1856 di completamento NON è confermato: conf medium.
- "Rue Centrale": S22 non la cita; Président-Carnot nasce nel 1890 (non Second Empire).
- Part-Dieu: caserme costruite 1851-63 (S38) vs terreno venduto 1844 (S32); terreno venduto al Comune 1957 (S32) vs 1960 (S38). Demolizione ~1960-65 solo da S38.
- Digue Tête-d'Or: 1759-1769 (S19) vs dopo la piena del 1856 (S29).
- Tunnel Croix-Rousse: 19 vs 20 aprile 1952 (stessa pagina).
- Quai Fulchiron: 1861 o 1851 (stessa pagina).
- Cours Vitton, Franklin-Roosevelt, Liberté, Garibaldi: nessuna data di apertura nelle pagine (solo intervalli/nomi).
- Piena 1856 (fr.wikipedia "Inondation de 1856 en France") letta: NON elenca i lavori dei quais del Rodano; gli anni dei lungofiumi del Rodano post-1856 restano da trovare.
- Non verificati (nomi dalla mia conoscenza, non da pagine lette): le 4 vie Part-Dieu nel regex (Vivier-Merle, Pompidou, Servient, Docteur-Bouchut).
- Forma nomi BD/Grand Lyon: "Rue Président Edouard Herriot" (senza accento su E), "Rue Président Carnot", "Rue de la République": i regex sono tolleranti.

## Dataset e mappe storiche
Raggiungibili con curl (non con WebFetch, che non risolve questi host):
- **Grand Lyon WFS** `https://data.grandlyon.com/geoserver/metropole-de-lyon/ows?service=WFS&request=GetCapabilities`. Layer trovati nel GetCapabilities:
  - `adr_voie_lieu.adrlineairevoie` (assi delle vie; campo `datedenom_creation` = data di denominazione, ~1986 per le vie principali: NON è data di apertura). Usato per i ring.
  - `adr_voie_lieu.adrchangementdenom` (zone di cambio denominazione).
  - `cad_cadastre.cadparcellehistorique` (parcelle storiche con `datehistorisation`, solo cadastre moderno).
  - `lyv_lyvia.lyvhistorique` (lavori stradali recenti, non storici).
  - Catalogo (SPA, non esplorabile via curl): https://data.grandlyon.com/ . Licenza non verificata (Etalab/ODbL da controllare).
  - Nessun dataset con anni di apertura delle vie o piani storici georeferenziati trovato nel WFS (ricerca sui titoli: histor/ancien/plan/voie/date).
- **David Rumsey** (https://www.davidrumsey.com/): rispondono con una pagina reCAPTCHA ("Verify Access"); non aggirata. Nessuna carta elencata: titoli/anni/licenza NON verificati. Da fare a mano da un browser (cercare "Lyon", piani del XVIII sec. e carta ~1850).
- **Archives de Lyon** (https://www.archives-lyon.fr/) e **Remonter le temps IGN** (https://remonterletemps.ign.fr/): host raggiungibili (HTTP 200) ma non ho letto pagine di contenuto: nulla da riportare come verificato. Il WMTS IGN su data.geopf.fr non è stato interrogato.
- Gallica: non tentato (403 indicato).

## Cosa servirebbe per georeferenziare le mappe storiche
1. Scaricare le immagini ad alta risoluzione (Rumsey fornisce spesso GeoTIFF/WMS per carte già georeferenziate, da verificare caso per caso) oppure il piano Archives de Lyon.
2. 6-10 punti di controllo per carta su elementi che esistono ancora (ponti, chiese, piazze Bellecour/Terreaux, Hôtel-Dieu), da OSM; trasformazione polinomiale 2° ordine in EPSG:2154/3857 (gdal_translate + gdalwarp).
3. Vettorializzare solo gli assi stradali (o confrontare per differenza con BD TOPO) per assegnare un anno minimo a ogni via presente/assente per carta: serve almeno una carta pre-1850, una ~1860-70 e una ~1900.
4. Verificare licenza di ogni carta (Rumsey: CC BY-NC-SA in generale, da controllare per carta).

## Ring proposti (gutting_proposta.json)
Derivati dagli assi reali Grand Lyon (S39) bufferizzati a mano (±12 m Herriot, ±14 m Carnot); lunghezze 1028/289 m contro 1025/285 m dichiarate in S21/S22. Non proposti perché senza coordinate/fonti: Cours Gambetta, Charlemagne, Lafayette (aperti su terreni liberi o non letti come demolizioni), Part-Dieu (caserme, non case), accessi dei tunnel di Croix-Rousse/Fourvière, estensione ovest di rue de la République già presente in story.json.
