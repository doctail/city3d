# Valencia (città di PROVA del kit, esclusa dalla produzione): scelte e incertezze

story.json: 8 zone, 2 mura, 6 gutting, 2 lost, 1 fire, 16 fasi water, 5 bridges, 26 landmarks, 26 soste, 5 eventi, 45 fonti. JSON valido, ogni `src` esiste in `sources`.

## Geometrie (Nominatim/OSM; Overpass non raggiungibile: reset di connessione)
- Cinta cristiana 1356: confine OSM di Ciutat Vella (rel. 4231802) con il tratto nord corretto per passare da Torres de Serranos / calle Blanqueria. 161 ha. Keep: Serranos e Quart (raggio 45 m). conf medium.
- Cinta islamica: 7 ruderi OSM "Muralla Arab" (Dalt, Salines, Valldigna, Borras, Beneyto i Coll, Mestres, Bosseria) ancorano i lati O, NO, N ed E. Il lato SUD e' disegnato a stima lungo calles Comedies / Sant Vicent. 36 ha. conf low. Demolizione 1400 = convenzione.
- Ordine `walls`: la Cristiana e' PRIMA perche' `hist_kit` usa la prima cinta con `ring` come WALL_P (cinta 1356). Cambiare l'ordine cambia WALL_P.
- Zone: `hist_kit` fa vincere la zona piu' antica, quindi le zone annidate (islamica dentro 1356) sono volute. Suburbi Quart/Morvedre/Russafa, Boatella (inclusa nella cinta 1356 secondo la ricerca B, quindi born 1300-1356), El Grau (born 1500-1800) e Cabanyal (1750-1837): poligoni approssimati, conf low, date di formazione non documentate.
- Gutting: Plaza Redonda (rel. OSM), Paz e Av. del Oeste (linee OSM bufferizzate 14 e 20 m; il collegamento tra i due soli tratti OSM e' retto), Plaza de la Reina (way 636811203 +5 m), Plaza del Ayuntamiento divisa per latitudine in convento (1891) e Pescadores (1907). Av. del Oeste 1945 = stima (conf low).
- Water: geometrie dei poligoni OSM gia' in `data_valencia/landphases.json` (nuovo cauce e Jardi del Turia) riconvertite in [lat, lon]. Il kit accetta solo c = field|urban|park: il CANTIERE 1964-1969.97 usa "urban" (terra nuda), perche' "field" sarebbe uguale al campo. Parco in blocco dal 1986 (ripiego, in realta' a tratti fino al 2000).
- Piena 1957: lastra "urban" sul perimetro di Ciutat Vella rimossa per 1957.78-1957.80. conf low, EFFETTO DA PROVARE (se l'acqua resta sotto il DEM serve un piano d'acqua dedicato).
- Ponti: scelta mista. Pietra storici (Serranos, Mar, Real, San Jose, Trinidad) come `bridge_arches` nei landmarks (linea e larghezza nei params, ricavate dall'asse del poligono OSM); impalcati moderni in `history.bridges`: Exposicion 1909 (d 1957.78), Calatrava 1995, Aragon 1933, Flores 2003, Assut de l'Or 2008. Il sito esatto del ponte 1909 non e' verificato (usata la linea del ponte attuale). Nessun ponte e' in entrambe le liste.

## Revisione zone suburbane (QA corridoi 1800)
Le zone Quart, Morvedre, Russafa, El Grau e Cabanyal erano troppo larghe e coprivano la griglia moderna. Ora sono strisce strette lungo strade storiche OSM: Quart = calle de Quart (60 m), Morvedre = calle de Sagunt dal ponte di Serranos verso nord (60 m), Russafa = calle de Russafa (55 m) piu' nucleo r 90 m presso il Mercat de Russafa (la chiesa di San Valero non e' in OSM: posizione stimata), El Grau = nucleo r 170 m a Plaça de la Sal, Cabanyal = Carrer de la Barraca (90 m), nuova zona Canyamelar = Carrer del Progres (60 m). Tutte conf low. Boatella ed espansione 1356 restano: sono dentro la cinta, tessuto storico. Totale zone: 9.

## Landmarks
- 26 totali; footprint "auto" dove un edificio catastale contiene il punto, "none" altrimenti (Generalitat, ponti). Micalet "none" (stessa impronta della Cattedrale). Gli anni catastali al punto di Estacion del Norte, Oceanografic, Agora (2020-26) non sono affidabili: contano le fasi.
- Basilica, Generalitat, Santa Catalina, Mercado de Colon: date da memoria, conf low, senza fonte vera (`S37` segnaposto OSM). Verificare o togliere.
- Nessun `skyscraper`: non ho trovato una torre verificata per Valencia.
- Ciudadela (lost): inizio 1715 NON verificato (Wikipedia non raggiungibile); solo "1710s" dalla ricerca; fine 1901 (torreon). Posizione approssimata a est di Plaza Tetuan. Convento di San Francisco: impronta stimata 90x60 m al centro della piazza.

## Regia / montaggio
- 26 soste da REGIA_VALENCIA.md, riordinate per y0 (la stazione 1906 precede l'Esposizione 1909; la sosta 1887-1900 contiene la 1891, come in regia). Target = landmark, zona o `area:[lat,lon,raggio]`. shot dedotto dalla distanza (close <=240 m, medium 260-600, wide 900-6000 con elev. bassa, top >=1400 m o dall'alto). I nomi `fx` sono segnaposto.
- Eventi: 1609 (sober), 1707 Fueros (conf low, data da memoria), 1877 Russafa, 1897 annessioni, 1936 capitale della Repubblica (sober). DANA 2024 e bombardamenti 1937-39: esclusi come da controllo storico.
- Popolazione: solo 1500 (45.000), 1609 (58.000, media di 52,3-63,8k) e 2025 (841.558). Nessun punto 1238/1800/1900/1950 con fonte: l'HUD interpola. `open` dice "840,000 people".

## Da fare prima del pod
Anteprima CPU (1800, 1900, 1935, 1960, piena 1957, Plan Sur), controllo corridoi vuoti su Paz / Oeste / Reina, verifica dei punti marcati low.
