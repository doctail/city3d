# Marseille — consegna completa YouTube (16/11/2026) — PROVVISORIA fino al render

**PROVVISORIO (nessun render ancora):** (1) gli orari dei capitoli vengono da `schedule_marseille.json` (durata 655,3 s): da RICALCOLARE dopo il render con la stessa regola di Lione (capitolo = t_in della carta − 2,8 s; carta/sosta = t_in; arrotondato per difetto; Sources = `end_plan.sources[0]` = 647,3 s) e confrontare con `years.json`; (2) la dichiarazione sul Saint-Jean pre-1943 va confrontata con ciò che il render mostra; (3) costo del pod: NON misurato, nessuna cifra.

Orari ricalcolati il 16/11 sullo schedule round 4 (durata 655,3 s, camera yb-camera r2). Validi per il video (finale 655,3 s = 10:55). Il video parte dal primo anno, senza apertura speciale. Tutte le voci distano ≥ 10 s (verificato con script).

Due note prima di incollare: (a) dichiarazione Saint-Jean misurata da yb-qa a 1942,9: 866 edifici, 8,35 ha; circa un terzo dell'impronta (30%, 279 lotti) segue la pianta tedesca 1940, il resto e tutte le altezze/date è stimato (sempre con la riserva); (b) 'prima del 1800' = `city.data_reliable_from` 1800 (la scritta RECONSTRUCTION compare a schermo sotto quell'anno).

---

## ENGLISH (principale)

### Titolo
```
EVOLUTION OF MARSEILLE | 3D City Timelapse (600 BC–NOW) | No AI
```

### Descrizione
```
Marseille began as a Greek colony on the Lacydon inlet around 600 BC, and it has been besieged, struck by plague, bombed and rebuilt ever since. Watch 2,625 years of Marseille grow, from Massalia to the CMA CGM tower and the MuCEM.

NO AI imagery. Every frame is rendered from open data. Buildings that stand today appear in the year recorded for their group of buildings in the French national building database (BDNB, built on the land registers), not building by building; groups with no recorded year are placed using their neighbors. Before 1800 the city is an approximate reconstruction on the historical footprint, marked on screen as "RECONSTRUCTION · APPROXIMATE". The Saint-Jean quarter, destroyed in 1943 (about 1,500 buildings, historical figure; the model shows about 870), is also a reconstruction: about a third of its footprint follows the 1940 German army plan of Marseille (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, public domain); the rest, and all heights and dates, are estimated. After the war, the new buildings appear in the years recorded in the BDNB. Dates in the captions come from the sources listed below; where a source is thin, the story says so.

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
4:53 Rue Impériale cuts through the old town (1862–64)
5:14 Notre-Dame de la Garde (1853–70)
6:13 The Transporter Bridge (1905)
6:55 Assassination on the quay (1934)
7:08 VII · Occupation and Ruins: Vichy and the bombs (1940)
7:27 Saint-Jean quarter destroyed (1943)
7:46 Rebuilding the Old Port (1949)
7:57 Le Corbusier's Radiant City (1952)
8:39 Metro and a shipping giant (1977)
9:02 VIII · A New Waterfront: Euroméditerranée (1995)
9:45 MuCEM and the Euroméditerranée waterfront (2013)
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

---

## FRANÇAIS

### Titolo
```
ÉVOLUTION DE MARSEILLE | Timelapse 3D de la ville (600 av. J.-C.–AUJOURD'HUI) | Sans IA
```

### Descrizione
```
Marseille est née comme colonie grecque sur l'anse du Lacydon vers 600 av. J.-C., puis a été assiégée, frappée par la peste, bombardée et reconstruite. Voyez 2 625 ans de Marseille, de Massalia à la tour CMA CGM et au MuCEM.

SANS IA. Chaque image est calculée à partir de données ouvertes. Les bâtiments actuels apparaissent à l'année enregistrée pour leur groupe de bâtiments dans la base nationale des bâtiments (BDNB, issue du cadastre), pas bâtiment par bâtiment ; les groupes sans année sont placés d'après leurs voisins. Avant 1800, la ville est une reconstitution approximative sur l'emprise historique, signalée à l'écran par « RECONSTRUCTION · APPROXIMATE ». Le quartier Saint-Jean, détruit en 1943 (environ 1 500 immeubles, chiffre historique ; le modèle en montre environ 870), est lui aussi une reconstitution : environ un tiers de son emprise suit le plan de Marseille de l'armée allemande de 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, domaine public) ; le reste, ainsi que toutes les hauteurs et les dates, est estimé. Après la guerre, les nouveaux bâtiments apparaissent aux années enregistrées dans la BDNB. Les dates des légendes viennent des sources ci-dessous ; quand une source est mince, le récit le dit.

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
4:53 La rue Impériale éventre la vieille ville (1862-1864)
5:14 Notre-Dame de la Garde (1853-1870)
6:13 Le pont transbordeur (1905)
6:55 Assassinat sur le quai (1934)
7:08 VII · Occupation et ruines : Vichy et les bombes (1940)
7:27 Le quartier Saint-Jean détruit (1943)
7:46 La reconstruction du Vieux-Port (1949)
7:57 La Cité radieuse de Le Corbusier (1952)
8:39 Le métro et un géant du transport maritime (1977)
9:02 VIII · Un nouveau front de mer : Euroméditerranée (1995)
9:45 Le MuCEM et le front de mer d’Euroméditerranée (2013)
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

---

## ITALIANO

### Titolo
```
EVOLUZIONE DI MARSIGLIA | Timelapse 3D della città (600 a.C.–OGGI) | Senza IA
```

### Descrizione
```
Marsiglia è nata come colonia greca sull'insenatura del Lacydon intorno al 600 a.C., ed è stata assediata, colpita dalla peste, bombardata e ricostruita. Guarda 2.625 anni di Marsiglia, da Massalia alla torre CMA CGM e al MuCEM.

SENZA IA. Ogni fotogramma è calcolato da dati aperti. Gli edifici di oggi compaiono nell'anno registrato per il loro gruppo di edifici nella banca dati nazionale francese (BDNB, basata sul catasto), non edificio per edificio; i gruppi senza anno vengono collocati in base ai vicini. Prima del 1800 la città è una ricostruzione approssimativa sull'impronta storica, indicata a schermo con « RECONSTRUCTION · APPROXIMATE ». Anche il quartiere Saint-Jean, distrutto nel 1943 (circa 1.500 edifici, dato storico; il modello ne mostra circa 870), è una ricostruzione: circa un terzo della sua impronta segue la pianta di Marsiglia dell'esercito tedesco del 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, pubblico dominio); il resto, e tutte le altezze e le date, è stimato. Dopo la guerra i nuovi edifici compaiono negli anni registrati nella BDNB. Le date delle didascalie vengono dalle fonti qui sotto; dove una fonte è debole, la storia lo dice.

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
4:53 La rue Impériale taglia la città vecchia (1862–64)
5:14 Notre-Dame de la Garde (1853–70)
6:13 Il ponte trasbordatore (1905)
6:55 Assassinio sul molo (1934)
7:08 VII · Occupazione e rovine: Vichy e le bombe (1940)
7:27 Il quartiere Saint-Jean distrutto (1943)
7:46 La ricostruzione del Vecchio Porto (1949)
7:57 La Città radiosa di Le Corbusier (1952)
8:39 La metropolitana e un gigante della navigazione (1977)
9:02 VIII · Un nuovo lungomare: Euroméditerranée (1995)
9:45 Il MuCEM e il lungomare di Euroméditerranée (2013)
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

---

## ESPAÑOL

### Titolo
```
EVOLUCIÓN DE MARSELLA | Timelapse 3D de la ciudad (600 a. C.–HOY) | Sin IA
```

### Descrizione
```
Marsella nació como colonia griega en la ensenada del Lacydon hacia el 600 a. C., y desde entonces ha sido sitiada, golpeada por la peste, bombardeada y reconstruida. Mira 2.625 años de Marsella, desde Massalia hasta la torre CMA CGM y el MuCEM.

SIN IA. Cada fotograma se genera con datos abiertos. Los edificios actuales aparecen en el año registrado para su grupo de edificios en la base de datos nacional francesa (BDNB, basada en el catastro), no edificio por edificio; los grupos sin año se colocan según sus vecinos. Antes de 1800 la ciudad es una reconstrucción aproximada sobre la huella histórica, indicada en pantalla como « RECONSTRUCTION · APPROXIMATE ». El barrio de Saint-Jean, destruido en 1943 (unos 1.500 edificios, cifra histórica; el modelo muestra unos 870), también es una reconstrucción: cerca de un tercio de su huella sigue el plano de Marsella del ejército alemán de 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, dominio público); el resto, y todas las alturas y fechas, es estimado. Tras la guerra, los nuevos edificios aparecen en los años registrados en la BDNB. Las fechas de los rótulos vienen de las fuentes de abajo; cuando una fuente es débil, la historia lo dice.

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
4:53 La rue Impériale atraviesa la ciudad vieja (1862–64)
5:14 Notre-Dame de la Garde (1853–70)
6:13 El puente transbordador (1905)
6:55 Asesinato en el muelle (1934)
7:08 VII · Ocupación y ruinas: Vichy y las bombas (1940)
7:27 El barrio de Saint-Jean destruido (1943)
7:46 La reconstrucción del Puerto Viejo (1949)
7:57 La Ciudad Radiante de Le Corbusier (1952)
8:39 El metro y un gigante naviero (1977)
9:02 VIII · Un nuevo frente marítimo: Euroméditerranée (1995)
9:45 El MuCEM y el frente marítimo de Euroméditerranée (2013)
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

---

## DEUTSCH

### Titolo
```
ENTWICKLUNG VON MARSEILLE | 3D-Zeitraffer der Stadt (600 v. Chr.–HEUTE) | Ohne KI
```

### Descrizione
```
Marseille entstand um 600 v. Chr. als griechische Kolonie an der Bucht des Lacydon und wurde seitdem belagert, von der Pest getroffen, bombardiert und wieder aufgebaut. Sieh 2.625 Jahre Marseille, von Massalia bis zum CMA-CGM-Turm und zum MuCEM.

OHNE KI. Jedes Bild wird aus offenen Daten berechnet. Heutige Gebäude erscheinen in dem Jahr, das in der französischen Gebäudedatenbank (BDNB, auf Grundlage des Katasters) für ihre Gebäudegruppe eingetragen ist, nicht Gebäude für Gebäude; Gruppen ohne Jahr werden nach den Nachbarn eingeordnet. Vor 1800 ist die Stadt eine ungefähre Rekonstruktion auf dem historischen Grundriss und auf dem Bildschirm als « RECONSTRUCTION · APPROXIMATE » markiert. Auch das 1943 zerstörte Viertel Saint-Jean (etwa 1.500 Gebäude, historische Zahl; das Modell zeigt etwa 870) ist eine Rekonstruktion: etwa ein Drittel seiner Grundfläche folgt dem Stadtplan von Marseille der deutschen Armee von 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, gemeinfrei); der Rest und alle Höhen und Daten sind geschätzt. Nach dem Krieg erscheinen die neuen Gebäude in den Jahren, die in der BDNB eingetragen sind. Die Daten in den Einblendungen stammen aus den unten genannten Quellen; wo eine Quelle dünn ist, sagt die Geschichte das.

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
4:53 Die Rue Impériale durchschneidet die Altstadt (1862–64)
5:14 Notre-Dame de la Garde (1853–70)
6:13 Die Schwebefähre (1905)
6:55 Attentat am Kai (1934)
7:08 VII · Besatzung und Ruinen: Vichy und die Bomben (1940)
7:27 Das Viertel Saint-Jean zerstört (1943)
7:46 Der Wiederaufbau des Alten Hafens (1949)
7:57 Le Corbusiers Cité radieuse (1952)
8:39 U-Bahn und ein Reedereiriese (1977)
9:02 VIII · Eine neue Uferpromenade: Euroméditerranée (1995)
9:45 Das MuCEM und die Uferpromenade von Euroméditerranée (2013)
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

---

## PORTUGUÊS (BR)

### Titolo
```
EVOLUÇÃO DE MARSELHA | Timelapse 3D da cidade (600 a.C.–HOJE) | Sem IA
```

### Descrizione
```
Marselha nasceu como colônia grega na enseada do Lacydon por volta de 600 a.C., e desde então foi sitiada, atingida pela peste, bombardeada e reconstruída. Veja 2.625 anos de Marselha, de Massalia à torre CMA CGM e ao MuCEM.

SEM IA. Cada quadro é calculado a partir de dados abertos. Os edifícios de hoje aparecem no ano registrado para o seu grupo de edifícios na base de dados nacional francesa (BDNB, baseada no cadastro), não edifício por edifício; os grupos sem ano são posicionados pelos vizinhos. Antes de 1800 a cidade é uma reconstrução aproximada sobre a pegada histórica, marcada na tela como « RECONSTRUCTION · APPROXIMATE ». O bairro Saint-Jean, destruído em 1943 (cerca de 1.500 edifícios, número histórico; o modelo mostra cerca de 870), também é uma reconstrução: cerca de um terço de sua área segue a planta de Marselha do exército alemão de 1940 (Stadtplan von Marseille, Sonderausgabe 6.40, BnF Gallica, domínio público); o resto, e todas as alturas e datas, é estimado. Depois da guerra, os novos edifícios aparecem nos anos registrados na BDNB. As datas das legendas vêm das fontes abaixo; onde uma fonte é fraca, a história diz isso.

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
4:53 A rue Impériale corta a cidade velha (1862–64)
5:14 Notre-Dame de la Garde (1853–70)
6:13 A ponte transbordadora (1905)
6:55 Assassinato no cais (1934)
7:08 VII · Ocupação e ruínas: Vichy e as bombas (1940)
7:27 O bairro Saint-Jean destruído (1943)
7:46 A reconstrução do Porto Velho (1949)
7:57 A Cidade Radiante de Le Corbusier (1952)
8:39 Metrô e um gigante do transporte marítimo (1977)
9:02 VIII · Uma nova orla: Euroméditerranée (1995)
9:45 O MuCEM e a orla da Euroméditerranée (2013)
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

---

## TAG (un solo campo YouTube, tutte le lingue insieme; 437 caratteri su 500)
```
marseille, evolution of marseille, marseille history, history of marseille, marseille 3d, 3d timelapse, city timelapse, city evolution, how marseille grew, massalia, greek marseille, vieux-port, old port marseille, notre-dame de la garde, mucem, marseille 1943, saint-jean quarter, marseille timelapse, no ai, histoire de marseille, evolution de marseille, quartier saint-jean 1943, marsiglia, marsella, 3d map, urban history, year built
```

## Commento fissato (EN + FR)
```
Find your street: in what year does your building appear? Tell me in the comments (and the year you think it should be).

Which city should grow next? Vote with a comment.

Limits, so you can check: today's buildings come in groups from the French building database (BDNB), so buildings in the same group share a year; groups with no recorded year are placed by their neighbors. Before 1800 the city is a reconstruction, and so is the Saint-Jean quarter before its destruction in 1943: about a third of its footprint follows the 1940 German plan (BnF Gallica); the rest, and all heights and dates, are estimated. If a date, a street name or a monument is wrong, write it here and I will fix it.
```
```
Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire (et l'année où vous pensez qu'il devrait apparaître).

Quelle ville devrait grandir la prochaine ? Votez en commentaire.

Les limites, pour pouvoir vérifier : les bâtiments actuels viennent par groupes de la base nationale (BDNB), donc les bâtiments d'un même groupe partagent une année ; les groupes sans année sont placés d'après leurs voisins. Avant 1800 la ville est une reconstitution, de même que le quartier Saint-Jean avant sa destruction en 1943 : environ un tiers de son emprise suit le plan allemand de 1940 (BnF Gallica) ; le reste, ainsi que toutes les hauteurs et les dates, est estimé. Si une date, un nom de rue ou un monument est faux, écrivez-le ici et je corrige.

Si votre famille vivait dans le quartier Saint-Jean, vos souvenirs sont les bienvenus.
```

## Impostazioni
Non per bambini. Aggiungere le 5 traduzioni (fr, it, es, de, pt-BR) di titolo e descrizione nella scheda video. Miniatura: `COPERTINE.md`. Short: `SHORT.md`, dopo la pubblicazione. Montaggio: `MONTAGGIO.md`. Reddit, distribuzione, nota stampa: `REDDIT_DISTRIBUZIONE.md`.

## Cosa manca / dipende dal render
- Orari definitivi dei capitoli (da `years.json`, stessa regola).
- Miniatura finale (fotogrammi `cover.shots` dal pod a 1080p).
- Link del video lungo nei testi di Short/Reddit (`{{URL_VIDEO}}`, `{{URL_VIDEO_LONGO}}`).
- Costo del pod: non misurato.
- Percentuale di edifici senza anno: non scritta nei testi (non verificata).