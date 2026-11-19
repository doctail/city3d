# MISSING — Rotterdam (aggiornato 19/11/2026, yb-historian + yb-modeler, branch yb/rotterdam)

Story ricostruita da testi scaricati (Wikipedia NL/EN, Wikidata). Ogni citazione in `sources[*].quote` e' una frase verbatim del testo scaricato (`research/verify_quotes.py`: 182 citazioni, 0 errate; testi in `research/sources_fetched/`; generatore `research/build_story.py`). Nessun kit build, nessun render (CPU di un altro agente): geometria dei monumenti, orientamento e rendering NON verificati. `python -m kit qa rotterdam --only a` = PASS.

## Compilato
- city: country Netherlands, start 1270 (diga sulla Rotte), titolo `EVOLUTION OF ROTTERDAM | 3D City Timelapse (1270-NOW) | No AI`, style_preset nordic [Guessing], 8 ere, 12 polity (County of Holland, Burgundian, Habsburg, Revolt 1573, Dutch Republic, Batavian, Kingdom of Holland, French Empire, United Netherlands, Kingdom of the Netherlands, German occupation 1940.38, Kingdom of the Netherlands 1945.34), popolazione 20 punti 1340-2023 (S1, S2, S3, Wikidata).
- soste: 18 (7 su monumento, 10 su area, 1 `fire:`), una `max` = bombardamento del 14 maggio 1940 (13:27-13:40, S6), fx e peso per ognuna.
- monumenti: 12 con kind e fasi con fonte (Laurenskerk, Witte Huis, City Hall, Euromast, Cube Houses, Markthal, De Rotterdam, Maastoren, Zalmhaven, Delftse Poort, Van Nelle, Pilgrim Fathers Church). Anni corretti: Maastoren 2006-2009 (non 2011), Euromast 1958-1960.
- history: 5 zone, 2 mura/dighe, 1 gutting, 1 fire distruttivo (1940). cards: 66 (tutte con `src`), 8 capitoli (nessun cold open), `data_reliable_from` 1900.

## Stime e punti deboli (conf low / [Guessing])
- Anelli e semi delle zone sono SCHIZZI a mano (+-150 m, dal legacy `hist_rotterdam.py` e da Wikidata); finestre di nascita (`born`) e altezze `era_height` sono stime.
- Mura: costruzione 1358-1500 con fonte (S3); anno di demolizione 1850 = SEGNAPOSTO senza fonte. Gutting Zandstraat: `from` 1825 = stima.
- Diga sulla Rotte (linea): posizione stimata; demolizione 1946 = [Likely] (il Basisplan sposta la diga sul fiume, S5).
- Fire 1940: anello = poligono dei danni del legacy (~3 km2; S5 dice 2,6 km2), fine fuoco 1940.385 e `rebuild_years` 5 = stime.
- Monumenti: footprint `auto` sul punto legacy puo' cadere su un sotto-blocco (Witte Huis 34 m2, City Hall = solo torre); Laurenskerk = chiesa sulla navata (torre = edificio catasto, BAG 1640); Markthal, Cube Houses, Van Nelle = `generic_footprint` approssimati; Markthal inizio cantiere 2011.5 = segnaposto. Da guardare al primo render locale.
- Date in conflitto tra fonti (annotate nelle `note`): carta 1340 (7 giugno NL / 7 luglio EN), diga 1260s (S1) / ~1270 (S3, S4), Witte Huis 1897 (NL) / 1898 (EN), Willemsbrug 1878 (S2, S3) / 1879 (S34), Pellegrini 1 agosto (S13) / 21 luglio 1620 (S14), popolazione anni 1670-1700.
- Popolazione: nessun punto per 1930-1960 nei testi scaricati (l'HUD interpola 1920 -> 1965); prima del 1340 nessun numero (HUD senza popolazione 1270-1340).
- Coordinate delle aree (diga, Waterstad, Hofplein, Lijnbaan, porti sud) = stime / Wikidata.

## Ancora da fare
- `history.bridges`: vuoto (il pacchetto dati non ha `bridges.json`; Erasmusbrug 1996, Willemsbrug 1878/1981, Hef non hanno linee verificate). Strade e ponti OSM sono comunque nei nastri di `roads.json` con anni propri.
- Canali interrati (Coolvest 1913-22, Binnenrotte 1869-71, Schie/Blaak dopo il 1940): `history.water` disegna solo TERRA a fasi, non acqua che sparisce: serve supporto kit, oppure restano visibili come strade.
- Porti storici prima del 1875 (Steiger, Oude Haven, Leuvehaven, Waterstad): assenti nei dati (harbours.json parte dal 1875).
- Maasvlakte (~30 km a ovest) e Nieuwe Waterweg (~20 km): fuori dal raggio dati (9 km): solo cartelli senza bersaglio; la sosta 1872 mostra i porti della riva sud.
- 1940 e ricostruzione dipendono da `fires_pass` (non verificato senza build).
- METADATA, capitoli con orari, descrizione, tag, commento fisso, Reddit: dopo il render (yb-packaging); i capitoli in anni sono gia' in `montaggio.chapters`.
- `kit qa` sezioni b-e (dati, corridoi, schedule/drone, camera) NON eseguite (richiedono build/CPU).

## R2: sospetti (stime dalla story, non misure)
- Monumento costruito dopo meta' hover: nessuno (7 monumenti bersaglio, tutti con inizio fase <= meta' hover; `research/r2_check.py`).
- Voli >= 12 s sotto 0,4 anni/s (stima distanza/150 m/s): borderline `1953.8 -> 1959.5` (Lijnbaan -> Euromast, ~12,7 s, ~0,45 anni/s) e `1960.4 -> 1961.5` (Euromast -> porti sud, ~10,7 s, ~0,10 anni/s: sotto i 12 s ma da ricontrollare nello schedule). Se `kit qa` conferma: spostare l'inizio hover Euromast/porti o togliere la sosta porti.
- Edifici all'anno 0, distanza camera mediana, pitch: non misurabili senza build.

## Pacchetto dati
- Completo per `kit pack`/`kit data` (ramo yb/data-complete 5d06c79): buildings, roads, dem, harbours, land, parks.
