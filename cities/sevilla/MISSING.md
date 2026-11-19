# MISSING — Seville (aggiornato da yb-historian + yb-modeler, 19/11/2026, branch yb/sevilla)

Base: bozza del legacy (`yb/legacy-import` 004c513) + pacchetto dati (`yb/data-complete` 5d06c79: roads, land, dem, landphases, parks).
`python -m kit qa sevilla --only a` = PASS (chiavi city, 55 fonti, ogni data con fonte). Sezioni b-f NON eseguite (servono hist.json e un build: vietato in questa sessione).

## Fatto (con fonti)
- **Fonti: 55.** 39 pagine Wikipedia EN/ES scaricate oggi (S1-S40); ogni `quote` e' fatta di sottostringhe ESATTE del testo scaricato (verificato dallo script di generazione). 16 voci S50-S65 vengono dalla `scheda_validazione_storica.md`: i loro host non sono raggiungibili dal proxy, quindi sono registrate con `claim` (non `quote`) e `fetched: false`; ogni data che dipende solo da loro e' `conf: low` (o medium con una seconda fonte) con nota.
- **Cartelli: 58** (minimo 45), tutti con `src`: 42 high, 7 medium, 9 low. Testi riscritti dove la fonte li smentiva (vedi Conflitti). Nessun cold open.
- **Soste: 12** (11 legacy + Casa de Contratacion 1503). Bersagli sistemati: Maestranza e Isabel II ora puntano ai monumenti; 1248 -> Real Alcazar (la Cattedrale non esiste nel 1248); Corta de la Cartuja -> `area:` sul canale (prima puntava a Plaza Nueva, a 398 m); Los Remedios finestra 1960-1970. Peso: UNA `max` (Cattedrale 1401-1434), le altre 3-8; fx assegnati (crowd, hammer, bell, water, crash, firework, hum, horn).
- **Monumenti: 21 con `kind`**, fasi e fonti (8 high, 6 medium, 7 low). `build_landmark` provato in memoria per tutti: nessun errore. Impronte `auto` controllate sul catasto: Giralda/Moschea/Cattedrale cadono sulla stessa particella (19.329 m2; la torre usa i params); Santa Justa ha una particella di 418x149 m, ignorata con `max_fp`; Real Alcazar, Plaza de Espana, Cartuja Island e Isla Magica NON hanno edifici entro 30 m (params a mano, orientamento 0 [Guessing]; le ultime due sono solo una lastra da 0,15 m per l'etichetta: nessun edificio inventato).
- **city:** country Spain, `style_preset` mediterranean, titolo `EVOLUTION OF SEVILLE | 3D City Timelapse (1248-NOW) | No AI`, 7 ere, `data_reliable_from` 1900 [Guessing].
- **Polities (19 chip):** Tartessian Hisbaal, Roman Hispalis, Visigothic, Al-Andalus/Umayyad 712, Taifa Abbadid 1023, Almoravid 1091, Almohad 1147 (precedono lo start: il chip a 1248 e' "Almohad Seville"), Crown of Castile 1248.9, Spanish Empire + Casa de Contratacion 1503, trade moves to Cadiz 1717, French occupation 1810, Kingdom of Spain 1812.65, Second Republic 1931.29, Civil War 1936.54, Franco 1939.25, Transition 1975.89, Democratic Spain 1978.99, Expo 92 (20 apr - 12 ott 1992). Anni di Tartessos, Visigoti e Almohad: [Guessing]/low (le fonti non danno l'inizio per Siviglia).
- **Popolazione:** 25 punti. 1842-2021 censimenti INE (via Wikipedia EN, stesse cifre "de jure" della scheda), 2025 = 688.714; 1248-1800 stime della scheda (low). Etichette HUD rough estimate / census.
- **Mura:** muro almohade (anello legacy georeferenziato), costruito [1170,1210] (scheda), demolito [1868,1873], tratti `keep` Macarena e Alcazar. **Muro romano NON modellato**: precede lo start e non esiste un anello con fonte (Wikipedia: tratto del III sec. trovato nel 2021).
- **Acqua (12 voci `history.water`)**: Alameda (laguna 1574, S12 verificata), Corta de Tablada 1909/1919/1926 (S35 verificata), Vega de Triana 1933/1943 e Plan Brackenbury 1927-1951 (S35), taglio di Cartuja e tappo di Chapina (S36 conferma le opere; anni 1948-50 e 1975-82 solo dalla scheda, low), lago Expo 1992. **Piene** (1917, 1961, 1963): solo cartelli, nessuna estensione d'acqua nei dati: nessun `floods`.
- **Zone (9):** citta' murata piena al 1225 + Alameda, orti nord, Arenal, Triana, 4 arrabales (modelli a mano del legacy hist_sevilla.py, conf low/medium, dichiarati). **Perduti:** convento di Plaza Nueva (1270-1840, S11), isolato dell'Encarnacion (fino al 1811). **Ponti disegnati:** 5 in `history.bridges` (San Telmo, Remedios, Delicias, Cachorro, passerella Cartuja; assi dai contorni OSM).
- **Capitoli (7, dagli anni):** 1248 Castilian Seville, 1503 Gateway to the Indies, 1649 Plague and Decline, 1810 War and Reform, 1868 Walls Down, River Tamed, 1929 Exposition, War and Dictatorship, 1975 Democracy and Expo 92.

## Conflitti fra fonti (decisi nel file; rivedere se si vuole l'altra versione)
- Cattedrale: Wikipedia EN decisione 1401, lavori 1402 (scheda/legacy 1434) -> usato 1402; moschea demolita 1402-1434 (scelta di modello).
- Mura: EN "dopo la rivoluzione del 1868" vs scheda 1858-c.1873 -> demolizione [1868,1873]; didascalia "(from 1868)".
- Plaza Nueva: EN 1852-1856 (convento "San Fernando" 1270-1840) vs scheda 1848/1853/1857 -> usato EN.
- Peste 1649: EN Seville "quasi meta'" vs EN Great Plague "fino a un quarto" -> cartello "da un quarto a quasi la meta'".
- Terremoto: EN Giralda 1356 vs ES Historia 1355 -> 1356.
- Popolazione 1248: scheda ~50.000 vs EN ~80.000 entro fine XII sec. -> 50.000 (low).
- Plaza de Espana: EN "costruita nel 1928", scheda progetto 1914 -> fase 1914-1929, low.
- Legacy smentito e corretto: Inquisizione (tribunale 1478, primo auto de fe 1481; non "Triana Castle"), Alamillo (lavori 1989, non 1987), Torre del Oro (terzo piano 1760, non "cylindrical top"), Isabel II ("600 anni" -> quasi 700), 1842 "primo censimento moderno" (tolto), 1940 "raddoppia" (tolto), Santa Justa (2 mag 1991) e AVE (linea 1992), Maestranza "completata 1881" (EN/ES: architetto incaricato nel 1876; 1881 solo scheda), "Capital of Andalusia 1982" (nessun anno nelle fonti: sostituito da San Telmo dal 1989).

## Da fare / aperto
1. **Fonti non raggiungibili**: le date che vengono solo dalla scheda (Chapina 1948-50, Cartuja 1975-82, Tamarguillo 1961, piene 1917/1963, Encarnacion 1811/1820, stime di popolazione pre-1842) restano low finche' qualcuno non apre le pagine (alcazarsevilla.org, sevilla.org, ine.es, ucm.es sono bloccati dal proxy).
2. **kit build NON eseguito**: `hist_kit.build` rigenera `landphases.json` da `history.water` (finestre singole; il pacchetto 5d06c79 ha le strisce graduali Tablada 1909-26 e Alameda 1574-78). Prima del build decidere se tenere il file del pacchetto o quello rigenerato.
3. QA b-f non fatti: densita' all'anno di partenza (nessun edificio all'anno 0, citta' piena nel 1248), corridoi vuoti, schedule/camera (distanza mediana >= 1.200 m, inclinazione < 45), anteprime CPU. `kit qa sevilla` completo prima del GO.
4. Ponti Alamillo/Barqueta/Centenario: solo impalcato (preset `bridge_arches`); pilone e stralli bespoke restano in `bridges_sevilla.py`. Plaza de Espana (semicerchio) e Real Alcazar approssimati con `palace_courtyard`: orientamento da guardare in anteprima.
5. METADATA.md (capitoli con orari, descrizione, tag, commento fisso, Reddit) e miniatura (`1248 > NOW`) non rifatti: dipendono dal render.

## R2: sospetti (stime a mano, schedule non ancora generato) [Likely]
Calcolo: tratto = max(3,5 s, distanza / 150 m/s) fra bersagli consecutivi; anni = y0 successivo - y1 precedente.
- Voli >= 12 s sotto 0,4 anni/s: **nessuno** dopo le correzioni. Corta de la Cartuja spostata a 1979-1983: 21,5 s a 0,42 anni/s (prima 0,23); e' il piu' vicino al limite. Gli altri lunghi: Macarena 14 s a 0,94, Plaza de Espana 18 s a 2,1, Torre Sevilla 19 s a 1,1.
- Voli brevi con troppi anni (> `rate_cap` 30 anni/s: 1401, 1758, 1503): il kit allunghera' il tratto; da controllare nel RITMO.
- Monumenti costruiti dopo meta' hover: **nessuno**, ma a meta' hover sono PARZIALI (stima): Cattedrale 1417 (circa 15% dei lavori), Giralda 1563 (belfry in costruzione), Maestranza 1774 (cantiere fermo 1766-84), Isabel II 1848, Plaza de Espana 1921, Los Remedios 1965. Completi: Real Alcazar, Macarena walls, Alamillo (1992), Torre Sevilla (2016).
- Da misurare dopo il build: distanza mediana camera, inclinazione, edifici vivi all'anno 0.
