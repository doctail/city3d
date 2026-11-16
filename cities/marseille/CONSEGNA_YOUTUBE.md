# Marseille — consegna completa YouTube (16/11/2026) — PROVVISORIA fino al render

**PROVVISORIO (nessun render ancora):** (1) gli orari dei capitoli vengono da `schedule_marseille.json` (durata 655,1 s; con cold open +9 s): da RICALCOLARE dopo il render con la stessa regola di Lione (capitolo = t_in della carta − 2,8 s; carta/sosta = t_in; arrotondato per difetto; Sources = `end_plan.sources[0]` = 647,1 s) e confrontare con `years.json`; (2) la finestra del cold open (secondi 451-460 del finale) va riletta da `years.json` (vedi `MONTAGGIO.md`); (3) la dichiarazione sul Saint-Jean pre-1943 va confrontata con ciò che il render mostra; (4) costo del pod: NON misurato, nessuna cifra.

Orari validi per il video SENZA cold open (finale 655,1 s = 10:55). Il blocco 'con cold open di 9 s' sostituisce il primo. Tutte le voci distano ≥ 10 s (verificato con script). I titoli qui sono quelli del candidato A di `METADATA.md`.

Due note prima di incollare: (a) il testo dichiara che gli isolati del Saint-Jean pre-1943 'seguono' la pianta tedesca del 1940 (dichiarazione voluta dal proprietario), ma `NOTE_STORIA.md` dice che i poligoni veri NON sono usati come geometria e che il pre-1943 mostrato copre circa 2/3 dell'area costruita: se il render resta così, sostituisci 'follow' con 'are approximated from' in tutte le lingue; (b) 'prima del 1850' viene da `city.data_reliable_from` = 1850 (la scritta RECONSTRUCTION compare a schermo sotto quell'anno; il proprietario aveva detto 1800).

---

## ENGLISH (principale)

### Titolo
```
Marseille: The Quarter the Germans Dynamited (600 BC–NOW)
```

### Descrizione (senza cold open)
```
Marseille began as a Greek colony on the Lacydon inlet around 600 BC, and it has been besieged, struck by plague, bombed and rebuilt ever since. Watch 2,625 years of Marseille grow, from Massalia to the CMA CGM tower and the MuCEM, including the winter of 1943, when German engineers dynamited the Saint-Jean quarter beside the Old Port: about 1,500 buildings, after a roundup that expelled about 20,000 people.

NO AI imagery. Every frame is rendered from open data. Buildings that stand today appear in the year recorded for their group of buildings in the French national building database (BDNB, built on the land registers), not building by building; groups with no recorded year are placed using their neighbors. Before 1850 the city is an approximate reconstruction on the historical footprint, marked on screen as "RECONSTRUCTION · APPROXIMATE". The Saint-Jean quarter before 1943 is also a reconstruction: its blocks follow the German army's 1940 plan of Marseille (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, public domain), not a survey of each house. After the war, the new buildings appear in the years recorded in the BDNB. Dates in the captions come from the sources listed below; where a source is thin, the story says so.

Which city should grow next? Tell me in the comments. If a building, a street or a date is wrong in your neighborhood, tell me that too: I would rather fix it. If your family lived in the Saint-Jean quarter, your memories and corrections are welcome.

CHAPTERS
0:00 Marseille today
0:12 I · The Greek Port: A colony on the Lacydon (600 BC)
0:43 Pytheas sails north (330 BC)
1:00 II · Under Rome: A city that backed the wrong side (49 BC)
1:32 III · Saints, Goths and Counts: Cassian and Saint-Victor (415)
1:57 Charles Martel sacks the city (739)
2:38 IV · Anjou and the Crown: Anjou takes Marseille (1252)
2:50 The Black Death (1348)
3:09 Provence joins France (1481)
3:23 V · The King's Port: The king enters through a breach (1660)
3:55 The Great Plague (1720)
4:12 The song of the Marseillais (1792)
4:28 VI · Gateway to the Empire: A new port for steam (1844)
4:55 Rue Impériale cuts through the old town (1862–64)
5:17 Notre-Dame de la Garde (1853–70)
6:15 The Transporter Bridge (1905)
6:57 Assassination on the quay (1934)
7:10 VII · Occupation and Ruins: Vichy and the bombs (1940)
7:26 The Saint-Jean quarter is dynamited (1943)
7:45 Rebuilding the Old Port (1949)
7:55 Le Corbusier's Radiant City (1952)
8:37 Metro and a shipping giant (1977)
9:00 VIII · A New Waterfront: Euroméditerranée (1995)
9:44 MuCEM and the Euroméditerranée waterfront (2013)
10:47 Sources

SOURCES AND LICENSES
- Buildings: BDNB, Base de Données Nationale des Bâtiments (CSTB), with the construction year from the Fichiers fonciers (DGFiP), per group of buildings; heights from IGN BD TOPO. Licence Ouverte 2.0 (Etalab). Groups without a recorded year are estimated from their nearest neighbors.
- Streets, rivers, railways and bridges: IGN BD TOPO (Licence Ouverte 2.0) and © OpenStreetMap contributors (ODbL). The opening year of most streets is an estimate from the surrounding buildings; the Rue Impériale (today Rue de la République) uses dated sources.
- Terrain and elevation: Copernicus DEM GLO-30 (ESA / European Union, Copernicus programme).
- Historical map used to place the blocks of the Saint-Jean quarter before 1943: Stadtplan von Marseille, Sonderausgabe 6.40 (Generalstab des Heeres, 1940), Bibliothèque nationale de France, Gallica (public domain).
- History: Wikipedia EN/FR (History of Marseille, Timeline of Marseille, Siege of Massilia, Marseille roundup, Rafle de Marseille, Hôtel de Ville, La Vieille Charité, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Cité radieuse, Euroméditerranée, CMA CGM Tower, MuCEM, Fernand Pouillon, Marseille) and INA, "La démolition du quartier du Vieux-Port". Population: figures and estimates from Wikipedia (Marseille), shown with their type (estimate or census).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.
```

### Capitoli con cold open di 9 s in testa (sostituiscono il blocco sopra)
```
CHAPTERS
0:00 Cold open: the Saint-Jean quarter, 1943
0:09 Marseille today
0:21 I · The Greek Port: A colony on the Lacydon (600 BC)
0:52 Pytheas sails north (330 BC)
1:09 II · Under Rome: A city that backed the wrong side (49 BC)
1:41 III · Saints, Goths and Counts: Cassian and Saint-Victor (415)
2:06 Charles Martel sacks the city (739)
2:47 IV · Anjou and the Crown: Anjou takes Marseille (1252)
2:59 The Black Death (1348)
3:18 Provence joins France (1481)
3:32 V · The King's Port: The king enters through a breach (1660)
4:04 The Great Plague (1720)
4:21 The song of the Marseillais (1792)
4:37 VI · Gateway to the Empire: A new port for steam (1844)
5:04 Rue Impériale cuts through the old town (1862–64)
5:26 Notre-Dame de la Garde (1853–70)
6:24 The Transporter Bridge (1905)
7:06 Assassination on the quay (1934)
7:19 VII · Occupation and Ruins: Vichy and the bombs (1940)
7:35 The Saint-Jean quarter is dynamited (1943)
7:54 Rebuilding the Old Port (1949)
8:04 Le Corbusier's Radiant City (1952)
8:46 Metro and a shipping giant (1977)
9:09 VIII · A New Waterfront: Euroméditerranée (1995)
9:53 MuCEM and the Euroméditerranée waterfront (2013)
10:56 Sources
```

---

## FRANÇAIS

### Titolo
```
Marseille : le quartier dynamité par les Allemands (600 av. J.-C.–AUJOURD'HUI)
```

### Descrizione (senza cold open)
```
Marseille est née comme colonie grecque sur l'anse du Lacydon vers 600 av. J.-C., puis a été assiégée, frappée par la peste, bombardée et reconstruite. Voyez 2 625 ans de Marseille, de Massalia à la tour CMA CGM et au MuCEM, y compris l'hiver 1943, quand des sapeurs allemands ont dynamité le quartier Saint-Jean, à côté du Vieux-Port : environ 1 500 immeubles, après une rafle qui a expulsé environ 20 000 personnes.

SANS IA. Chaque image est calculée à partir de données ouvertes. Les bâtiments actuels apparaissent à l'année enregistrée pour leur groupe de bâtiments dans la base nationale des bâtiments (BDNB, issue du cadastre), pas bâtiment par bâtiment ; les groupes sans année sont placés d'après leurs voisins. Avant 1850, la ville est une reconstitution approximative sur l'emprise historique, signalée à l'écran par « RECONSTRUCTION · APPROXIMATE ». Le quartier Saint-Jean avant 1943 est lui aussi une reconstitution : ses îlots suivent le plan de Marseille de l'armée allemande de 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, domaine public), pas un relevé maison par maison. Après la guerre, les nouveaux bâtiments apparaissent aux années enregistrées dans la BDNB. Les dates des légendes viennent des sources ci-dessous ; quand une source est mince, le récit le dit.

Quelle ville devrait grandir la prochaine ? Dites-le-moi en commentaire. Si un bâtiment, une rue ou une date est faux dans votre quartier, dites-le aussi : je préfère le corriger. Si votre famille vivait dans le quartier Saint-Jean, vos souvenirs et vos corrections sont les bienvenus.

CHAPITRES
0:00 Marseille aujourd'hui
0:12 I · Le port grec : une colonie sur le Lacydon (600 av. J.-C.)
0:43 Pythéas navigue vers le nord (330 av. J.-C.)
1:00 II · Sous Rome : une ville du mauvais côté (49 av. J.-C.)
1:32 III · Saints, Wisigoths et comtes : Cassien et Saint-Victor (415)
1:57 Charles Martel saccage la ville (739)
2:38 IV · L'Anjou et la Couronne : l'Anjou prend Marseille (1252)
2:50 La peste noire (1348)
3:09 La Provence rejoint la France (1481)
3:23 V · Le port du roi : le roi entre par une brèche (1660)
3:55 La grande peste (1720)
4:12 Le chant des Marseillais (1792)
4:28 VI · Porte de l'Empire : un nouveau port pour la vapeur (1844)
4:55 La rue Impériale éventre la vieille ville (1862-1864)
5:17 Notre-Dame de la Garde (1853-1870)
6:15 Le pont transbordeur (1905)
6:57 Assassinat sur le quai (1934)
7:10 VII · Occupation et ruines : Vichy et les bombes (1940)
7:26 Le quartier Saint-Jean est dynamité (1943)
7:45 La reconstruction du Vieux-Port (1949)
7:55 La Cité radieuse de Le Corbusier (1952)
8:37 Le métro et un géant du transport maritime (1977)
9:00 VIII · Un nouveau front de mer : Euroméditerranée (1995)
9:44 Le MuCEM et le front de mer d’Euroméditerranée (2013)
10:47 Sources

SOURCES AND LICENSES
- Buildings: BDNB, Base de Données Nationale des Bâtiments (CSTB), with the construction year from the Fichiers fonciers (DGFiP), per group of buildings; heights from IGN BD TOPO. Licence Ouverte 2.0 (Etalab). Groups without a recorded year are estimated from their nearest neighbors.
- Streets, rivers, railways and bridges: IGN BD TOPO (Licence Ouverte 2.0) and © OpenStreetMap contributors (ODbL). The opening year of most streets is an estimate from the surrounding buildings; the Rue Impériale (today Rue de la République) uses dated sources.
- Terrain and elevation: Copernicus DEM GLO-30 (ESA / European Union, Copernicus programme).
- Historical map used to place the blocks of the Saint-Jean quarter before 1943: Stadtplan von Marseille, Sonderausgabe 6.40 (Generalstab des Heeres, 1940), Bibliothèque nationale de France, Gallica (public domain).
- History: Wikipedia EN/FR (History of Marseille, Timeline of Marseille, Siege of Massilia, Marseille roundup, Rafle de Marseille, Hôtel de Ville, La Vieille Charité, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Cité radieuse, Euroméditerranée, CMA CGM Tower, MuCEM, Fernand Pouillon, Marseille) and INA, "La démolition du quartier du Vieux-Port". Population: figures and estimates from Wikipedia (Marseille), shown with their type (estimate or census).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.
```

### Capitoli con cold open di 9 s in testa (sostituiscono il blocco sopra)
```
CHAPITRES
0:00 Ouverture : le quartier Saint-Jean, 1943
0:09 Marseille aujourd'hui
0:21 I · Le port grec : une colonie sur le Lacydon (600 av. J.-C.)
0:52 Pythéas navigue vers le nord (330 av. J.-C.)
1:09 II · Sous Rome : une ville du mauvais côté (49 av. J.-C.)
1:41 III · Saints, Wisigoths et comtes : Cassien et Saint-Victor (415)
2:06 Charles Martel saccage la ville (739)
2:47 IV · L'Anjou et la Couronne : l'Anjou prend Marseille (1252)
2:59 La peste noire (1348)
3:18 La Provence rejoint la France (1481)
3:32 V · Le port du roi : le roi entre par une brèche (1660)
4:04 La grande peste (1720)
4:21 Le chant des Marseillais (1792)
4:37 VI · Porte de l'Empire : un nouveau port pour la vapeur (1844)
5:04 La rue Impériale éventre la vieille ville (1862-1864)
5:26 Notre-Dame de la Garde (1853-1870)
6:24 Le pont transbordeur (1905)
7:06 Assassinat sur le quai (1934)
7:19 VII · Occupation et ruines : Vichy et les bombes (1940)
7:35 Le quartier Saint-Jean est dynamité (1943)
7:54 La reconstruction du Vieux-Port (1949)
8:04 La Cité radieuse de Le Corbusier (1952)
8:46 Le métro et un géant du transport maritime (1977)
9:09 VIII · Un nouveau front de mer : Euroméditerranée (1995)
9:53 Le MuCEM et le front de mer d’Euroméditerranée (2013)
10:56 Sources
```

---

## ITALIANO

### Titolo
```
Marsiglia: il quartiere fatto saltare dai tedeschi (600 a.C.–OGGI)
```

### Descrizione (senza cold open)
```
Marsiglia è nata come colonia greca sull'insenatura del Lacydon intorno al 600 a.C., ed è stata assediata, colpita dalla peste, bombardata e ricostruita. Guarda 2.625 anni di Marsiglia, da Massalia alla torre CMA CGM e al MuCEM, compreso l'inverno del 1943, quando i genieri tedeschi fecero saltare il quartiere Saint-Jean accanto al Vecchio Porto: circa 1.500 edifici, dopo una retata che espulse circa 20.000 persone.

SENZA IA. Ogni fotogramma è calcolato da dati aperti. Gli edifici di oggi compaiono nell'anno registrato per il loro gruppo di edifici nella banca dati nazionale francese (BDNB, basata sul catasto), non edificio per edificio; i gruppi senza anno vengono collocati in base ai vicini. Prima del 1850 la città è una ricostruzione approssimativa sull'impronta storica, indicata a schermo con « RECONSTRUCTION · APPROXIMATE ». Anche il quartiere Saint-Jean prima del 1943 è una ricostruzione: i suoi isolati seguono la pianta di Marsiglia dell'esercito tedesco del 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, pubblico dominio), non un rilievo casa per casa. Dopo la guerra i nuovi edifici compaiono negli anni registrati nella BDNB. Le date delle didascalie vengono dalle fonti qui sotto; dove una fonte è debole, la storia lo dice.

Quale città dovrebbe crescere dopo? Dimmelo nei commenti. Se un edificio, una strada o una data è sbagliata nel tuo quartiere, dimmelo: preferisco correggerla. Se la tua famiglia viveva nel quartiere Saint-Jean, i tuoi ricordi e le tue correzioni sono benvenuti.

CAPITOLI
0:00 Marsiglia oggi
0:12 I · Il porto greco: una colonia sul Lacydon (600 a.C.)
0:43 Pitea naviga verso nord (330 a.C.)
1:00 II · Sotto Roma: una città dalla parte sbagliata (49 a.C.)
1:32 III · Santi, Goti e conti: Cassiano e San Vittore (415)
1:57 Carlo Martello saccheggia la città (739)
2:38 IV · Gli Angiò e la Corona: gli Angiò prendono Marsiglia (1252)
2:50 La peste nera (1348)
3:09 La Provenza entra in Francia (1481)
3:23 V · Il porto del re: il re entra da una breccia (1660)
3:55 La grande peste (1720)
4:12 Il canto dei marsigliesi (1792)
4:28 VI · La porta dell'Impero: un nuovo porto per il vapore (1844)
4:55 La rue Impériale taglia la città vecchia (1862–64)
5:17 Notre-Dame de la Garde (1853–70)
6:15 Il ponte trasbordatore (1905)
6:57 Assassinio sul molo (1934)
7:10 VII · Occupazione e rovine: Vichy e le bombe (1940)
7:26 Il quartiere Saint-Jean viene fatto saltare (1943)
7:45 La ricostruzione del Vecchio Porto (1949)
7:55 La Città radiosa di Le Corbusier (1952)
8:37 La metropolitana e un gigante della navigazione (1977)
9:00 VIII · Un nuovo lungomare: Euroméditerranée (1995)
9:44 Il MuCEM e il lungomare di Euroméditerranée (2013)
10:47 Fonti

SOURCES AND LICENSES
- Buildings: BDNB, Base de Données Nationale des Bâtiments (CSTB), with the construction year from the Fichiers fonciers (DGFiP), per group of buildings; heights from IGN BD TOPO. Licence Ouverte 2.0 (Etalab). Groups without a recorded year are estimated from their nearest neighbors.
- Streets, rivers, railways and bridges: IGN BD TOPO (Licence Ouverte 2.0) and © OpenStreetMap contributors (ODbL). The opening year of most streets is an estimate from the surrounding buildings; the Rue Impériale (today Rue de la République) uses dated sources.
- Terrain and elevation: Copernicus DEM GLO-30 (ESA / European Union, Copernicus programme).
- Historical map used to place the blocks of the Saint-Jean quarter before 1943: Stadtplan von Marseille, Sonderausgabe 6.40 (Generalstab des Heeres, 1940), Bibliothèque nationale de France, Gallica (public domain).
- History: Wikipedia EN/FR (History of Marseille, Timeline of Marseille, Siege of Massilia, Marseille roundup, Rafle de Marseille, Hôtel de Ville, La Vieille Charité, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Cité radieuse, Euroméditerranée, CMA CGM Tower, MuCEM, Fernand Pouillon, Marseille) and INA, "La démolition du quartier du Vieux-Port". Population: figures and estimates from Wikipedia (Marseille), shown with their type (estimate or census).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.
```

### Capitoli con cold open di 9 s in testa (sostituiscono il blocco sopra)
```
CAPITOLI
0:00 Apertura: il quartiere Saint-Jean, 1943
0:09 Marsiglia oggi
0:21 I · Il porto greco: una colonia sul Lacydon (600 a.C.)
0:52 Pitea naviga verso nord (330 a.C.)
1:09 II · Sotto Roma: una città dalla parte sbagliata (49 a.C.)
1:41 III · Santi, Goti e conti: Cassiano e San Vittore (415)
2:06 Carlo Martello saccheggia la città (739)
2:47 IV · Gli Angiò e la Corona: gli Angiò prendono Marsiglia (1252)
2:59 La peste nera (1348)
3:18 La Provenza entra in Francia (1481)
3:32 V · Il porto del re: il re entra da una breccia (1660)
4:04 La grande peste (1720)
4:21 Il canto dei marsigliesi (1792)
4:37 VI · La porta dell'Impero: un nuovo porto per il vapore (1844)
5:04 La rue Impériale taglia la città vecchia (1862–64)
5:26 Notre-Dame de la Garde (1853–70)
6:24 Il ponte trasbordatore (1905)
7:06 Assassinio sul molo (1934)
7:19 VII · Occupazione e rovine: Vichy e le bombe (1940)
7:35 Il quartiere Saint-Jean viene fatto saltare (1943)
7:54 La ricostruzione del Vecchio Porto (1949)
8:04 La Città radiosa di Le Corbusier (1952)
8:46 La metropolitana e un gigante della navigazione (1977)
9:09 VIII · Un nuovo lungomare: Euroméditerranée (1995)
9:53 Il MuCEM e il lungomare di Euroméditerranée (2013)
10:56 Fonti
```

---

## ESPAÑOL

### Titolo
```
Marsella: el barrio que los alemanes dinamitaron (600 a. C.–HOY)
```

### Descrizione (senza cold open)
```
Marsella nació como colonia griega en la ensenada del Lacydon hacia el 600 a. C., y desde entonces ha sido sitiada, golpeada por la peste, bombardeada y reconstruida. Mira 2.625 años de Marsella, desde Massalia hasta la torre CMA CGM y el MuCEM, incluido el invierno de 1943, cuando ingenieros alemanes dinamitaron el barrio de Saint-Jean junto al Puerto Viejo: unos 1.500 edificios, tras una redada que expulsó a unas 20.000 personas.

SIN IA. Cada fotograma se genera con datos abiertos. Los edificios actuales aparecen en el año registrado para su grupo de edificios en la base de datos nacional francesa (BDNB, basada en el catastro), no edificio por edificio; los grupos sin año se colocan según sus vecinos. Antes de 1850 la ciudad es una reconstrucción aproximada sobre la huella histórica, indicada en pantalla como « RECONSTRUCTION · APPROXIMATE ». El barrio de Saint-Jean antes de 1943 también es una reconstrucción: sus manzanas siguen el plano de Marsella del ejército alemán de 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, dominio público), no un levantamiento casa por casa. Tras la guerra, los nuevos edificios aparecen en los años registrados en la BDNB. Las fechas de los rótulos vienen de las fuentes de abajo; cuando una fuente es débil, la historia lo dice.

¿Qué ciudad debería crecer la próxima? Cuéntamelo en los comentarios. Si un edificio, una calle o una fecha es incorrecta en tu barrio, dímelo también: prefiero corregirlo. Si tu familia vivía en el barrio de Saint-Jean, tus recuerdos y correcciones son bienvenidos.

CAPÍTULOS
0:00 Marsella hoy
0:12 I · El puerto griego: una colonia en el Lacydon (600 a. C.)
0:43 Piteas navega hacia el norte (330 a. C.)
1:00 II · Bajo Roma: una ciudad del bando equivocado (49 a. C.)
1:32 III · Santos, godos y condes: Casiano y San Víctor (415)
1:57 Carlos Martel saquea la ciudad (739)
2:38 IV · Anjou y la Corona: Anjou toma Marsella (1252)
2:50 La peste negra (1348)
3:09 Provenza se une a Francia (1481)
3:23 V · El puerto del rey: el rey entra por una brecha (1660)
3:55 La gran peste (1720)
4:12 El canto de los marselleses (1792)
4:28 VI · Puerta del Imperio: un nuevo puerto para el vapor (1844)
4:55 La rue Impériale atraviesa la ciudad vieja (1862–64)
5:17 Notre-Dame de la Garde (1853–70)
6:15 El puente transbordador (1905)
6:57 Asesinato en el muelle (1934)
7:10 VII · Ocupación y ruinas: Vichy y las bombas (1940)
7:26 El barrio de Saint-Jean es dinamitado (1943)
7:45 La reconstrucción del Puerto Viejo (1949)
7:55 La Ciudad Radiante de Le Corbusier (1952)
8:37 El metro y un gigante naviero (1977)
9:00 VIII · Un nuevo frente marítimo: Euroméditerranée (1995)
9:44 El MuCEM y el frente marítimo de Euroméditerranée (2013)
10:47 Fuentes

SOURCES AND LICENSES
- Buildings: BDNB, Base de Données Nationale des Bâtiments (CSTB), with the construction year from the Fichiers fonciers (DGFiP), per group of buildings; heights from IGN BD TOPO. Licence Ouverte 2.0 (Etalab). Groups without a recorded year are estimated from their nearest neighbors.
- Streets, rivers, railways and bridges: IGN BD TOPO (Licence Ouverte 2.0) and © OpenStreetMap contributors (ODbL). The opening year of most streets is an estimate from the surrounding buildings; the Rue Impériale (today Rue de la République) uses dated sources.
- Terrain and elevation: Copernicus DEM GLO-30 (ESA / European Union, Copernicus programme).
- Historical map used to place the blocks of the Saint-Jean quarter before 1943: Stadtplan von Marseille, Sonderausgabe 6.40 (Generalstab des Heeres, 1940), Bibliothèque nationale de France, Gallica (public domain).
- History: Wikipedia EN/FR (History of Marseille, Timeline of Marseille, Siege of Massilia, Marseille roundup, Rafle de Marseille, Hôtel de Ville, La Vieille Charité, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Cité radieuse, Euroméditerranée, CMA CGM Tower, MuCEM, Fernand Pouillon, Marseille) and INA, "La démolition du quartier du Vieux-Port". Population: figures and estimates from Wikipedia (Marseille), shown with their type (estimate or census).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.
```

### Capitoli con cold open di 9 s in testa (sostituiscono il blocco sopra)
```
CAPÍTULOS
0:00 Apertura: el barrio de Saint-Jean, 1943
0:09 Marsella hoy
0:21 I · El puerto griego: una colonia en el Lacydon (600 a. C.)
0:52 Piteas navega hacia el norte (330 a. C.)
1:09 II · Bajo Roma: una ciudad del bando equivocado (49 a. C.)
1:41 III · Santos, godos y condes: Casiano y San Víctor (415)
2:06 Carlos Martel saquea la ciudad (739)
2:47 IV · Anjou y la Corona: Anjou toma Marsella (1252)
2:59 La peste negra (1348)
3:18 Provenza se une a Francia (1481)
3:32 V · El puerto del rey: el rey entra por una brecha (1660)
4:04 La gran peste (1720)
4:21 El canto de los marselleses (1792)
4:37 VI · Puerta del Imperio: un nuevo puerto para el vapor (1844)
5:04 La rue Impériale atraviesa la ciudad vieja (1862–64)
5:26 Notre-Dame de la Garde (1853–70)
6:24 El puente transbordador (1905)
7:06 Asesinato en el muelle (1934)
7:19 VII · Ocupación y ruinas: Vichy y las bombas (1940)
7:35 El barrio de Saint-Jean es dinamitado (1943)
7:54 La reconstrucción del Puerto Viejo (1949)
8:04 La Ciudad Radiante de Le Corbusier (1952)
8:46 El metro y un gigante naviero (1977)
9:09 VIII · Un nuevo frente marítimo: Euroméditerranée (1995)
9:53 El MuCEM y el frente marítimo de Euroméditerranée (2013)
10:56 Fuentes
```

---

## DEUTSCH

### Titolo
```
Marseille: das Viertel, das die Deutschen sprengten (600 v. Chr.–HEUTE)
```

### Descrizione (senza cold open)
```
Marseille entstand um 600 v. Chr. als griechische Kolonie an der Bucht des Lacydon und wurde seitdem belagert, von der Pest getroffen, bombardiert und wieder aufgebaut. Sieh 2.625 Jahre Marseille, von Massalia bis zum CMA-CGM-Turm und zum MuCEM, einschließlich des Winters 1943, als deutsche Pioniere das Viertel Saint-Jean neben dem Alten Hafen sprengten: etwa 1.500 Gebäude, nach einer Razzia, bei der etwa 20.000 Menschen vertrieben wurden.

OHNE KI. Jedes Bild wird aus offenen Daten berechnet. Heutige Gebäude erscheinen in dem Jahr, das in der französischen Gebäudedatenbank (BDNB, auf Grundlage des Katasters) für ihre Gebäudegruppe eingetragen ist, nicht Gebäude für Gebäude; Gruppen ohne Jahr werden nach den Nachbarn eingeordnet. Vor 1850 ist die Stadt eine ungefähre Rekonstruktion auf dem historischen Grundriss und auf dem Bildschirm als « RECONSTRUCTION · APPROXIMATE » markiert. Auch das Viertel Saint-Jean vor 1943 ist eine Rekonstruktion: Seine Blöcke folgen dem Stadtplan von Marseille der deutschen Armee von 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, gemeinfrei), nicht einer Aufnahme Haus für Haus. Nach dem Krieg erscheinen die neuen Gebäude in den Jahren, die in der BDNB eingetragen sind. Die Daten in den Einblendungen stammen aus den unten genannten Quellen; wo eine Quelle dünn ist, sagt die Geschichte das.

Welche Stadt soll als Nächstes wachsen? Sag es mir in den Kommentaren. Wenn in deinem Viertel ein Gebäude, eine Straße oder ein Datum falsch ist, sag mir das auch: Ich korrigiere es lieber. Wenn deine Familie im Viertel Saint-Jean lebte, sind deine Erinnerungen und Korrekturen willkommen.

KAPITEL
0:00 Marseille heute
0:12 I · Der griechische Hafen: eine Kolonie am Lacydon (600 v. Chr.)
0:43 Pytheas segelt nach Norden (330 v. Chr.)
1:00 II · Unter Rom: eine Stadt auf der falschen Seite (49 v. Chr.)
1:32 III · Heilige, Goten und Grafen: Cassianus und Saint-Victor (415)
1:57 Karl Martell plündert die Stadt (739)
2:38 IV · Anjou und die Krone: Anjou erobert Marseille (1252)
2:50 Der Schwarze Tod (1348)
3:09 Die Provence kommt zu Frankreich (1481)
3:23 V · Der Hafen des Königs: der König zieht durch eine Bresche ein (1660)
3:55 Die große Pest (1720)
4:12 Das Lied der Marseiller (1792)
4:28 VI · Tor zum Imperium: ein neuer Hafen für die Dampfschiffe (1844)
4:55 Die Rue Impériale durchschneidet die Altstadt (1862–64)
5:17 Notre-Dame de la Garde (1853–70)
6:15 Die Schwebefähre (1905)
6:57 Attentat am Kai (1934)
7:10 VII · Besatzung und Ruinen: Vichy und die Bomben (1940)
7:26 Das Viertel Saint-Jean wird gesprengt (1943)
7:45 Der Wiederaufbau des Alten Hafens (1949)
7:55 Le Corbusiers Cité radieuse (1952)
8:37 U-Bahn und ein Reedereiriese (1977)
9:00 VIII · Eine neue Uferpromenade: Euroméditerranée (1995)
9:44 Das MuCEM und die Uferpromenade von Euroméditerranée (2013)
10:47 Quellen

SOURCES AND LICENSES
- Buildings: BDNB, Base de Données Nationale des Bâtiments (CSTB), with the construction year from the Fichiers fonciers (DGFiP), per group of buildings; heights from IGN BD TOPO. Licence Ouverte 2.0 (Etalab). Groups without a recorded year are estimated from their nearest neighbors.
- Streets, rivers, railways and bridges: IGN BD TOPO (Licence Ouverte 2.0) and © OpenStreetMap contributors (ODbL). The opening year of most streets is an estimate from the surrounding buildings; the Rue Impériale (today Rue de la République) uses dated sources.
- Terrain and elevation: Copernicus DEM GLO-30 (ESA / European Union, Copernicus programme).
- Historical map used to place the blocks of the Saint-Jean quarter before 1943: Stadtplan von Marseille, Sonderausgabe 6.40 (Generalstab des Heeres, 1940), Bibliothèque nationale de France, Gallica (public domain).
- History: Wikipedia EN/FR (History of Marseille, Timeline of Marseille, Siege of Massilia, Marseille roundup, Rafle de Marseille, Hôtel de Ville, La Vieille Charité, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Cité radieuse, Euroméditerranée, CMA CGM Tower, MuCEM, Fernand Pouillon, Marseille) and INA, "La démolition du quartier du Vieux-Port". Population: figures and estimates from Wikipedia (Marseille), shown with their type (estimate or census).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.
```

### Capitoli con cold open di 9 s in testa (sostituiscono il blocco sopra)
```
KAPITEL
0:00 Auftakt: das Viertel Saint-Jean, 1943
0:09 Marseille heute
0:21 I · Der griechische Hafen: eine Kolonie am Lacydon (600 v. Chr.)
0:52 Pytheas segelt nach Norden (330 v. Chr.)
1:09 II · Unter Rom: eine Stadt auf der falschen Seite (49 v. Chr.)
1:41 III · Heilige, Goten und Grafen: Cassianus und Saint-Victor (415)
2:06 Karl Martell plündert die Stadt (739)
2:47 IV · Anjou und die Krone: Anjou erobert Marseille (1252)
2:59 Der Schwarze Tod (1348)
3:18 Die Provence kommt zu Frankreich (1481)
3:32 V · Der Hafen des Königs: der König zieht durch eine Bresche ein (1660)
4:04 Die große Pest (1720)
4:21 Das Lied der Marseiller (1792)
4:37 VI · Tor zum Imperium: ein neuer Hafen für die Dampfschiffe (1844)
5:04 Die Rue Impériale durchschneidet die Altstadt (1862–64)
5:26 Notre-Dame de la Garde (1853–70)
6:24 Die Schwebefähre (1905)
7:06 Attentat am Kai (1934)
7:19 VII · Besatzung und Ruinen: Vichy und die Bomben (1940)
7:35 Das Viertel Saint-Jean wird gesprengt (1943)
7:54 Der Wiederaufbau des Alten Hafens (1949)
8:04 Le Corbusiers Cité radieuse (1952)
8:46 U-Bahn und ein Reedereiriese (1977)
9:09 VIII · Eine neue Uferpromenade: Euroméditerranée (1995)
9:53 Das MuCEM und die Uferpromenade von Euroméditerranée (2013)
10:56 Quellen
```

---

## PORTUGUÊS (BR)

### Titolo
```
Marselha: o bairro que os alemães dinamitaram (600 a.C.–HOJE)
```

### Descrizione (senza cold open)
```
Marselha nasceu como colônia grega na enseada do Lacydon por volta de 600 a.C., e desde então foi sitiada, atingida pela peste, bombardeada e reconstruída. Veja 2.625 anos de Marselha, de Massalia à torre CMA CGM e ao MuCEM, incluindo o inverno de 1943, quando engenheiros alemães dinamitaram o bairro Saint-Jean, ao lado do Porto Velho: cerca de 1.500 edifícios, depois de uma batida que expulsou cerca de 20.000 pessoas.

SEM IA. Cada quadro é calculado a partir de dados abertos. Os edifícios de hoje aparecem no ano registrado para o seu grupo de edifícios na base de dados nacional francesa (BDNB, baseada no cadastro), não edifício por edifício; os grupos sem ano são posicionados pelos vizinhos. Antes de 1850 a cidade é uma reconstrução aproximada sobre a pegada histórica, marcada na tela como « RECONSTRUCTION · APPROXIMATE ». O bairro Saint-Jean antes de 1943 também é uma reconstrução: seus quarteirões seguem a planta de Marselha do exército alemão de 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, domínio público), não um levantamento casa por casa. Depois da guerra, os novos edifícios aparecem nos anos registrados na BDNB. As datas das legendas vêm das fontes abaixo; onde uma fonte é fraca, a história diz isso.

Qual cidade deve crescer a seguir? Conte-me nos comentários. Se um edifício, uma rua ou uma data estiver errada no seu bairro, me diga também: prefiro corrigir. Se a sua família morava no bairro Saint-Jean, suas memórias e correções são bem-vindas.

CAPÍTULOS
0:00 Marselha hoje
0:12 I · O porto grego: uma colônia no Lacydon (600 a.C.)
0:43 Píteas navega para o norte (330 a.C.)
1:00 II · Sob Roma: uma cidade do lado errado (49 a.C.)
1:32 III · Santos, godos e condes: Cassiano e São Vítor (415)
1:57 Carlos Martel saqueia a cidade (739)
2:38 IV · Anjou e a Coroa: Anjou toma Marselha (1252)
2:50 A peste negra (1348)
3:09 A Provença une-se à França (1481)
3:23 V · O porto do rei: o rei entra por uma brecha (1660)
3:55 A grande peste (1720)
4:12 O canto dos marselheses (1792)
4:28 VI · Porta do Império: um novo porto para o vapor (1844)
4:55 A rue Impériale corta a cidade velha (1862–64)
5:17 Notre-Dame de la Garde (1853–70)
6:15 A ponte transbordadora (1905)
6:57 Assassinato no cais (1934)
7:10 VII · Ocupação e ruínas: Vichy e as bombas (1940)
7:26 O bairro Saint-Jean é dinamitado (1943)
7:45 A reconstrução do Porto Velho (1949)
7:55 A Cidade Radiante de Le Corbusier (1952)
8:37 Metrô e um gigante do transporte marítimo (1977)
9:00 VIII · Uma nova orla: Euroméditerranée (1995)
9:44 O MuCEM e a orla da Euroméditerranée (2013)
10:47 Fontes

SOURCES AND LICENSES
- Buildings: BDNB, Base de Données Nationale des Bâtiments (CSTB), with the construction year from the Fichiers fonciers (DGFiP), per group of buildings; heights from IGN BD TOPO. Licence Ouverte 2.0 (Etalab). Groups without a recorded year are estimated from their nearest neighbors.
- Streets, rivers, railways and bridges: IGN BD TOPO (Licence Ouverte 2.0) and © OpenStreetMap contributors (ODbL). The opening year of most streets is an estimate from the surrounding buildings; the Rue Impériale (today Rue de la République) uses dated sources.
- Terrain and elevation: Copernicus DEM GLO-30 (ESA / European Union, Copernicus programme).
- Historical map used to place the blocks of the Saint-Jean quarter before 1943: Stadtplan von Marseille, Sonderausgabe 6.40 (Generalstab des Heeres, 1940), Bibliothèque nationale de France, Gallica (public domain).
- History: Wikipedia EN/FR (History of Marseille, Timeline of Marseille, Siege of Massilia, Marseille roundup, Rafle de Marseille, Hôtel de Ville, La Vieille Charité, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Cité radieuse, Euroméditerranée, CMA CGM Tower, MuCEM, Fernand Pouillon, Marseille) and INA, "La démolition du quartier du Vieux-Port". Population: figures and estimates from Wikipedia (Marseille), shown with their type (estimate or census).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.
```

### Capitoli con cold open di 9 s in testa (sostituiscono il blocco sopra)
```
CAPÍTULOS
0:00 Abertura: o bairro Saint-Jean, 1943
0:09 Marselha hoje
0:21 I · O porto grego: uma colônia no Lacydon (600 a.C.)
0:52 Píteas navega para o norte (330 a.C.)
1:09 II · Sob Roma: uma cidade do lado errado (49 a.C.)
1:41 III · Santos, godos e condes: Cassiano e São Vítor (415)
2:06 Carlos Martel saqueia a cidade (739)
2:47 IV · Anjou e a Coroa: Anjou toma Marselha (1252)
2:59 A peste negra (1348)
3:18 A Provença une-se à França (1481)
3:32 V · O porto do rei: o rei entra por uma brecha (1660)
4:04 A grande peste (1720)
4:21 O canto dos marselheses (1792)
4:37 VI · Porta do Império: um novo porto para o vapor (1844)
5:04 A rue Impériale corta a cidade velha (1862–64)
5:26 Notre-Dame de la Garde (1853–70)
6:24 A ponte transbordadora (1905)
7:06 Assassinato no cais (1934)
7:19 VII · Ocupação e ruínas: Vichy e as bombas (1940)
7:35 O bairro Saint-Jean é dinamitado (1943)
7:54 A reconstrução do Porto Velho (1949)
8:04 A Cidade Radiante de Le Corbusier (1952)
8:46 Metrô e um gigante do transporte marítimo (1977)
9:09 VIII · Uma nova orla: Euroméditerranée (1995)
9:53 O MuCEM e a orla da Euroméditerranée (2013)
10:56 Fontes
```

---

## TAG (un solo campo YouTube, tutte le lingue insieme; 437 caratteri su 500)
```
marseille, evolution of marseille, marseille history, history of marseille, marseille 3d, 3d timelapse, city timelapse, city evolution, how marseille grew, massalia, greek marseille, vieux-port, old port marseille, notre-dame de la garde, mucem, marseille 1943, saint-jean quarter, marseille timelapse, no ai, histoire de marseille, evolution de marseille, quartier saint-jean 1943, marsiglia, marsella, 3d map, urban history, year built
```

## Commento fissato (EN + FR)
```
Find your street: in what year does your building appear? Tell me in the comments (and the year you think it should be).

Which city should grow next? Vote with a comment.

Limits, so you can check: today's buildings come in groups from the French building database (BDNB), so buildings in the same group share a year; groups with no recorded year are placed by their neighbors. Before 1850 the city is a reconstruction, and so is the Saint-Jean quarter before its destruction in 1943. If a date, a street name or a monument is wrong, write it here and I will fix it.
```
```
Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire (et l'année où vous pensez qu'il devrait apparaître).

Quelle ville devrait grandir la prochaine ? Votez en commentaire.

Les limites, pour pouvoir vérifier : les bâtiments actuels viennent par groupes de la base nationale (BDNB), donc les bâtiments d'un même groupe partagent une année ; les groupes sans année sont placés d'après leurs voisins. Avant 1850 la ville est une reconstitution, de même que le quartier Saint-Jean avant sa destruction en 1943. Si une date, un nom de rue ou un monument est faux, écrivez-le ici et je corrige.

Si votre famille vivait dans le quartier Saint-Jean, vos souvenirs sont les bienvenus.
```

## Impostazioni
Non per bambini. Aggiungere le 5 traduzioni (fr, it, es, de, pt-BR) di titolo e descrizione nella scheda video. Miniatura: `COPERTINE.md`. Short: `SHORT.md`, dopo la pubblicazione. Montaggio e cold open: `MONTAGGIO.md`. Reddit, distribuzione, nota stampa: `REDDIT_DISTRIBUZIONE.md`.

## Cosa manca / dipende dal render
- Orari definitivi dei capitoli e finestra del cold open (da `years.json`).
- Miniatura finale (fotogrammi `cover.shots` dal pod a 1080p).
- Link del video lungo nei testi di Short/Reddit (`{{URL_VIDEO}}`, `{{URL_VIDEO_LONGO}}`).
- Costo del pod: non misurato.
- Percentuale di edifici senza anno: non scritta nei testi (non verificata).