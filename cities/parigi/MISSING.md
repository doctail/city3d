# MISSING — Paris (dopo il passaggio storico-modellazione, branch yb/parigi)

Fonti nuove: 76 (id `W001`..`W076`, Wikipedia EN, citazione letterale dalla pagina scaricata). Etichette: [Certain] = data letta in una pagina scaricata; [Likely]/[Guessing] sono marcati in `conf: low` e nelle `note`.

## Compilato
- `city`: country France; style_preset `central` [Likely, ardesia/piombo]; titolo `EVOLUTION OF PARIS | 3D City Timelapse (1190-NOW) | No AI` (primo anno reale = 1190: hist_parigi.py e regia.open.rewind_to; 2.708 edifici vivi al 1190); 9 ere; 23 chip regime (Capetians, Valois, Burgundian-English 1418-1436, League, Bourbon, Revolution, Republic, Consulate, Empire, Restoration, Hundred Days, 2nd Restoration, July Monarchy, 2nd Republic, 2nd Empire, 3rd Republic, Commune, Occupation, GPRF, 4th, 5th), ognuno con fonte.
- Parisii, Lutetia romana, Merovingi: PRIMA del primo fotogramma, quindi solo come fonti (W001-W002), non come chip.
- `zones`: 6 nuclei del 1190 + 6 anelli (Filippo Augusto, Carlo V, Luigi XIII, Fermiers generaux, Thiers/annessione 1860, banlieue). Anelli = involucro convesso delle parti di mura del pack legacy o cerchi: SCHIZZI A MANO, conf low; gli intervalli `born` sono stime. Date delle mura da Wikipedia (1190-1213, 1356-1383, 1633-1636, 1784-1791, 1841-1846, annessione 1 gen 1860).
- `bridges`: 36 ponti, linea = asse dei contorni OSM del pack (reale), anni da Wikipedia/Ville de Paris; una voce sola per ponte (il kit tiene un solo y/d per contorno): le fasi sono in `phases` e `note`, i buchi (es. crollo 1499-1507) non sono modellati. Corretti rispetto alla tabella a memoria: Mirabeau 1897, Garigliano 1966, Senghor 1861, Tournelle 1620, Aval 1968.
- `landmarks`: kind per tutti i 20; fonti per i 6 senza (E019/E020, E008, E004, La Defense, G005, G012); Arc de Triomphe h=49,54 m da Wikipedia (il legacy 94,3 era sbagliato); Bastille, Grand Chatelet, Tuileries con `demolished`; Eiffel con fasi 27 gen 1887 - 6 mag 1889 (E004).
- `soste`: peso e fx su tutte, un solo `max` (Haussmann); Canal Saint-Martin resta bersaglio ad area.
- `montaggio`: 6 capitoli (I Medieval Paris 1190, II 1546, III 1790, IV 1853, V 1900, VI 1958; nessun cold open), `open` con 2.065.560 abitanti (INSEE D051), 104 cartelli (12 nuovi di regime, 2 corretti con fonte).

## Aggiunto (history, script `cities/parigi/build_history.py`, rigenerabile)
- `walls` (5): Filippo Augusto (perimetro ALPAGE `wall_p`), Carlo V (solo riva destra, asse della fascia ALPAGE), Luigi XIII (= "yellow ditches", tratti ALPAGE "Fossés jaunes"; date Wikipedia 1633-1636, le parti legacy dicono 1566-1643), Fermiers generaux (anello ALPAGE + 4 barriere `keep`), Thiers (anello a raggio mediano dei tratti del modulo legacy, tracciato [Likely] ~70 m fuori dai Boulevards des Marechaux, non ALPAGE). Date con citazione Wikipedia verificata come sottostringa del testo scaricato (W077+, 28 fonti nuove).
- `fires` (3): Notre-Dame 2019, Tuileries 1871, Hotel de Ville 1871 (poligoni dal pack legacy; solo fuoco/fumo, `destroy` false: le fasi sono dei monumenti).
- `lost`: nessuna voce. Bastille, Grand Chatelet e Tuileries hanno gia' `demolished` come monumenti.
- `gutting` (6): Rivoli est (until 1855.2), Strasbourg/Sebastopol (1859, stima), Saint-Michel (1860, stima), Saint-Germain (1877), Haussmann (1870, stima), Opera (1877). `from` = 1190 (tessuto antico gia' presente). Linee da capi/vertici di strada [lat, lon] (NON da OSM) + larghezza: errore atteso ~40 m, conf medium/low, `kit qa` b/c non lo vede.
- `water` (43 poligoni al posto dei 9 cerchi): Louviers 1843, volte Richard-Lenoir 1862 e Temple 1906, Arsenal, Villette (2 dic 1808), Saint-Martin, Ourcq (15 ago 1813), Saint-Denis (mag 1821) = fasi ALPAGE reali del pack (`landphases.json`, id nel nome). Eccezione: canale tra Ile Notre-Dame e Ile aux Vaches (A001) = striscia stimata di 22 m (nessun poligono ALPAGE/OSM), conf low.
- Doppione ponti: Pont Neuf e Pont Alexandre III tolti da `history.bridges` (restano come monumenti `bridge_arches`, con linea e fasi; ora 34 ponti).
- Controlli: `kit qa parigi --only a` PASS; su copia dati in /tmp (hist_kit + landmarks_kit build, nessun render) b/c: PASS, WARN solo 113 nastri stradali dopo il 2026. Pack e `hist_parigi.py` non toccati.

## ANCORA APERTO
1. OSM/Overpass non raggiungibile da qui (Nominatim e mirror rifiutati): i boulevard Haussmann vanno ricalcati su OSM (linee reali) e confrontati nel fotogramma locale; Saint-Germain/Sebastopol/Haussmann hanno un solo `until` (aperture a sezioni 1855-1877).
2. Mura: le parti legacy di `landmarks.json` e `landmarks_walls.json` del kit possono duplicarsi nel render (decidere quale tenere); `towers_every_m` solo su Filippo Augusto e Carlo V. Demolizioni a tratti = legacy/ALPAGE, solo gli estremi hanno fonte.
3. Ile Saint-Louis: la striscia del canale e' una stima; Arsenal (1806) e volta del Temple (1906) senza citazione, conf low; i poligoni ALPAGE hanno fine 1807-1809 (Arsenal), 1810.7-1813 (Villette/Ourcq).
4. `zones`: anelli e `born` da verificare nel confronto locale; zona banlieue da togliere se genera predecessori falsi (134K su 403K nel build di prova).
5. Ponti: Pont Rouelle senza data (y=1900 conf low); Concorde solo G011; un solo y/d per ponte.
6. Monumenti: preset = approssimazioni; Eiffel senza preset (modulo legacy); fasi quasi tutte solo del primo anno; La Defense: distretto 1958 vs Grande Arche 1982.
7. Cartelli senza `target`/`shot`; 60 senza didascalia. `data_reliable_from` 1800 = ipotesi. Capitoli, descrizione, tag, commento fisso, Reddit: da rifare dopo lo schedule (METADATA.md).
8. Nessun render e nessun `kit build` nel repo. Restano i controlli d-e (corridoi, drone) e R2.
