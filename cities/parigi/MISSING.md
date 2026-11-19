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

## ANCORA APERTO
1. `history.water`: 9 voci ancora CERCHI (isole unite 1655/1843, canali 1806-1821, volta del canale 1862/1906). `land.json` del pack non si legge in modo affidabile (anello esterno = scatola, buco da 81 km2): serve il contorno OSM dei canali e delle isole.
2. Haussmann 1853-1870: niente `gutting` (servono linee dei boulevard da OSM); niente `walls`/`lost`/`fires` come voci story (il pack legacy le ha gia' come parti).
3. `zones`: anelli e `born` da verificare nel confronto locale; la zona banlieue e' da togliere se genera predecessori falsi. La `hist.json` legacy (ALPAGE) e' migliore: decidere se `kit build` la deve rigenerare dalle zone.
4. Ponti: Pont Rouelle senza data (y=1900 conf low); Pont de la Concorde (pagina EN = disambigua, solo G011); un solo y/d per ponte. Pont Neuf e Alexandre III sono sia monumento (bridge_arches) sia ponte: controllare il doppione nel confronto locale.
5. Monumenti: preset = approssimazioni; Eiffel non ha preset (tenere il modulo legacy); fasi solo del primo anno per quasi tutti; La Defense: distretto 1958 vs Grande Arche 1982.
6. Cartelli senza `target`/`shot`; 60 senza didascalia. `data_reliable_from` 1800 = ipotesi. Capitoli con orari, descrizione, tag, commento fisso, Reddit: da rifare dopo lo schedule (METADATA.md).
7. Nessun render e nessun `kit build` eseguiti; `kit qa parigi --only a` = PASS. Restano da fare i controlli b-e (dati, densita', corridoi, drone) e R2 prima del pod.
