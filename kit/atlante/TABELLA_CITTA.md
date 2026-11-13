# TABELLA CITTA' (13/11/2026) - sintesi di tutte le misure

Criterio a due colonne (concordato col proprietario):
- **Dato** = anno di costruzione per edificio da registro ufficiale: A (>=70% nel centro, scaricabile), B (35-70%, o per gruppo/parcel, o parziale), C (solo classi/stime/niente).
- **Kit** = fattibile col nostro kit: SI' anche con il metodo Roma (impronte OSM sul pod + classi di eta' ISTAT o simili + modello storico). Roma e' fatta cosi': l'anno e' una stima per sezione, non un dato per edificio.
- **Saturazione**: NON ancora verificata con vidIQ (5 crediti a citta'), tranne dove indicato dai file BACKLOG/ATLANTE. Regola: <5K libera; 5K-100K solo con prodotto migliore e angolo diverso; >100K domanda provata, caso test.
- Etichette: [Certain] misurato su campione reale, [Likely] inferenza, [Guessing] ipotesi. Dettagli e DA SBLOCCARE nei file per area.

## Candidate (Dato A/B misurato, Kit SI')
| Citta' | Dato | Misura | Piu' vecchio | Geometria | Evento storico | Saturazione |
|---|---|---|---|---|---|---|
| **Lione** | A (gruppo) | 82,2% citta' / 92,2% centro [Certain] | n.m. | BDNB batiment_groupe | Croix-Rousse, rivolte canuts, bombardamenti 1944 [Guessing] | da verificare |
| **Tolosa** | A (gruppo) | 73,1% / 88,0% | n.m. | BDNB | alluvione 1875 (Garonna) [Guessing] | da verificare |
| **Strasburgo** | A (gruppo) | 78,6% / 89,6% | n.m. | BDNB | assedio 1870, Neustadt tedesca [Guessing] | da verificare |
| **Bordeaux** | A (gruppo) | 77,3% / 86,1% | n.m. | BDNB | demolizione mura, Haussmann locale [Guessing] | da verificare |
| **Nizza** | A (gruppo) | 73,5% / 87,1% | n.m. | BDNB | annessione 1860, Promenade [Guessing] | da verificare |
| **Marsiglia** | B citta' / A centro | 67,9% / 82,4% | n.m. | BDNB (arrondissement 13201-13216) | Vieux-Port 1943 [Guessing] | da verificare |
| **Montpellier** | A (gruppo) | 73,3% / 82,0% | n.m. | BDNB | [Guessing] | da verificare |
| **Lille** | A (gruppo) | 76,5% / 81,9% | n.m. | BDNB | assedio 1914, ricostruzione [Guessing] | da verificare |
| **Nantes** | A (gruppo) | 72,7% / 80,1% | n.m. | BDNB | Ile de Nantes, cantieri [Guessing] | da verificare |
| **Washington DC** | A | 99,5% su 109.411 record CAMA [Certain] | 1870 | join SSL con 185.695 poligoni (96%) | 1814, Capitol, L'Enfant [Guessing] | da verificare |
| **Pittsburgh** | A | 87% (WPRDC, CC0) [Certain] | 1770 (5 rec.) | join via PIN | acciaio, 3 fiumi [Guessing] | da verificare |
| **Portland (OR)** | A | 90% [Certain] | n.m. | taxlot nello stesso layer | [Guessing] | da verificare |
| Denver | B | 96,7% (CCYRBLT, per parcel) [Certain] | 1884 | join parcel 99% | gold rush [Guessing] | da verificare |
| Los Angeles County | B | 99,7% tra le righe con edificio [Certain] | 1885 | nessuna nella tabella | [Guessing] | da verificare |
| Richmond VA | B | 100% su 66.248 poligoni [Certain] | 1890 | poligoni (da verificare) | 1865 [Guessing] | da verificare |
| Cambridge MA | B | 87,4% [Certain] | 1850 | da verificare | | da verificare |
| Philadelphia | B | 93% ma anno reale solo 23% (resto stima OPA) [Certain] | 1700s non separati | join PWD ~100% | [Guessing] | da verificare |
| Baltimora | B | 82% (56% al netto di picchi tondi) [Certain] | 23 prima del 1800 | | incendio 1904 [Guessing] | da verificare |
| Minneapolis | B | 88% [Certain] | n.m. | nessuna nel layer | [Guessing] | da verificare |
| Amburgo | B | 37% (25% Altstadt) su 406.415 edifici [Certain] | 1500 (placeholder) | WFS ALKIS | incendio 1842, bombardamenti 1943 | libera [Certain, vidIQ 13/11] |

## Italia (metodo Roma: OSM + ISTAT 2011 per sezione, Kit SI')
ISTAT 2011 per sezione (dati-cpa_2011.zip, 52 MB) verificato scaricabile [Certain]: classi di epoca solo per sezione, non per edificio. 2021: solo E3, nessuna epoca. Citta': Milano, Torino, Genova, Bologna, Venezia, Palermo, Bari, Trieste, Verona. Saturazione da verificare (Roma 1,26M CityEons, Firenze Tree The City, Napoli Stratapolis 8,5K, Budapest Urbis Anno).

## Escluse o non praticabili
| Citta' | Motivo |
|---|---|
| Londra | satura (CityEons 746K, 4 canali oltre 7K in 45 gg); dato C (Colouring London a bande, geometrie OS con licenza dubbia) |
| Berlino | satura (Latos 1,18M, CityEons 352K); ALKIS WFS 784.178 edifici senza campo anno: 0% [Certain] |
| Vienna | satura per BACKLOG (337K); dato: anno esatto 19,4% in citta', 87,5% in Innere Stadt; classi ~86% |
| Praga, Atene, Lisbona, Istanbul, Malaga | sature (BACKLOG) |
| Monaco, Francoforte, Stoccarda, Dresda, Lipsia, Norimberga, Brema, Hannover, Graz | C: nessun dataset con anno per edificio trovato/accessibile |
| Mosca, San Pietroburgo | solo dati a livello di condominio, rischio alto (sanzioni, accesso), non raccomandate |
| New Orleans, Charleston, Cincinnati, St. Louis | footprint senza campo anno (C) |

## Non misurate (host morti o da sbloccare)
Helsinki (c_valmpvm, Atlante: A, host kartta.hel.fi/hri.fi), Zurigo (gbauj, geolion.zh.ch), Basilea, Tallinn; Detroit, Savannah, Nashville, Atlanta, Cleveland, San Antonio (portali bloccati); Baviera e Assia (WFS 403); Edimburgo/Manchester; Oslo, Varsavia, Cracovia (campo anno non confermato).

## Limiti noti
- Overpass e Geofabrik irraggiungibili dalla sessione (000): nessuna misura di copertura OSM start_date.
- Cittadine BDNB: unita' = gruppo di edifici, non edificio singolo.
- Arrotondamenti: DC 20% dei validi su decenni tondi, Baltimora picchi 1900/1910/1920 [Likely imputazione].
