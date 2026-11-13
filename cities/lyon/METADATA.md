# Lyon: METADATA (YouTube)

Chapter times are placeholders `{{t:YEAR}}` (the second the counter reaches that year/card in the final render): derive them from `regia.txt` after rendering, never by hand. The first chapter must be 0:00, at least 3 chapters.

## Title (<= 100 characters)
EVOLUTION OF LYON | 3D City Timelapse (43 BC–NOW) | No AI

## Description (EN)
Lyon was founded on a hill between two rivers, and it has been rebuilt, besieged, flooded and bombed ever since. Watch more than 2,000 years of Lyon grow, from the Roman colony of Lugdunum in 43 BC to the towers of Part-Dieu and the tip of the Confluence.

NO AI imagery. Every frame is rendered from open data. Buildings that stand today appear in the period given for their group of buildings in the source data (not building by building), and earlier districts are an approximate reconstruction on the historical footprint. Dates in the captions come from the sources listed below; where a source is thin, the story says so.

Which city should grow next? Tell me in the comments. And if a building or a monument is missing from your neighborhood, tell me that too: I would rather fix it.

CHAPTERS
{{t:open}} Lyon today
{{t:-43}} I · Capital of the Gauls: Lugdunum is founded (43 BC)
{{t:177}} The martyrs of Lugdunum (AD 177)
{{t:1180}} II · Cathedral, Fairs and Silk: Saint-Jean is begun (1180)
{{t:1461}} The fairs of Lyon (1461)
{{t:1708}} Place Bellecour (1715)
{{t:1793.60}} III · Siege and Revolt: the siege of Lyon (1793)
{{t:1801}} Jacquard's loom (1801)
{{t:1831.89}} The canut revolts (1831 and 1834)
{{t:1852}} IV · Floods and Boulevards: three towns join Lyon (1852)
{{t:1856.41}} The Rhône floods the left bank (1856)
{{t:1872}} Notre-Dame de Fourvière (1872–84)
{{t:1944.66}} V · Bridges and Liberation: the bridges are blown up (1944)
{{t:1960}} VI · Towers and Rivers: Part-Dieu (1960–77)
{{t:2012}} Musée des Confluences (2014)
{{t:recap}} 2,000 years in 20 seconds, from one spot
{{t:sources}} Sources

SOURCES AND LICENSES
- Buildings (year per group of buildings), terrain and elevation (DEM): data prepared in `data_lyon/` by the data agent. TO FILL IN once the sources and licenses are confirmed (expected: IGN / open data of the Métropole de Lyon).
- Streets, rivers and bridges: BD TOPO (IGN, Licence Ouverte Etalab 2.0), and © OpenStreetMap contributors (ODbL) for coordinates of named places.
- History: Wikipedia EN/FR (Lugdunum, History of Lyon, Canut revolts, Siege of Lyon, Inondation de 1856 en France, Liste des ponts de Lyon, Libération de Lyon, Lyon from the First to the Second Empire, Part-Dieu, Lyon Cathedral, Basilica of Notre-Dame de Fourvière, Musée des Confluences, Place Bellecour, Croix-Rousse, Lyon).
- Music: same tracks as the other Year Built videos (confirm credits at publication).

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments.

## Tags (EN + FR, <= 500 characters in total)
lyon, evolution of lyon, lyon history, lyon 3d, 3d timelapse, city timelapse, city evolution, how lyon grew, history of lyon, lugdunum, roman lyon, croix-rousse, canuts, silk lyon, fourviere, vieux lyon, presqu'ile, part-dieu, confluence, lyon timelapse, no ai, histoire de lyon, evolution de lyon, lyon 3d, ponts de lyon 1944

## Titles (translations)
- fr: ÉVOLUTION DE LYON | Timelapse 3D de la ville (43 av. J.-C.–AUJOURD'HUI) | Sans IA
- it: EVOLUZIONE DI LIONE | Timelapse 3D della città (43 a.C.–OGGI) | Senza IA
- es: EVOLUCIÓN DE LYON | Timelapse 3D de la ciudad (43 a. C.–HOY) | Sin IA
- de: ENTWICKLUNG VON LYON | 3D-Zeitraffer der Stadt (43 v. Chr.–HEUTE) | Ohne KI
- pt-BR: EVOLUÇÃO DE LYON | Timelapse 3D da cidade (43 a.C.–HOJE) | Sem IA

## Descriptions (translations)
Each translation = the promise, the NO AI note and the question. Append, unchanged, the CHAPTERS block (with the translated chapter names when the final timestamps are in) and the SOURCES AND LICENSES block from the English description.

### fr
Lyon est née sur une colline entre deux fleuves, puis a été reconstruite, assiégée, inondée et bombardée. Voyez plus de 2 000 ans de Lyon, de la colonie romaine de Lugdunum en 43 av. J.-C. aux tours de la Part-Dieu et à la pointe de la Confluence.

SANS IA. Chaque image est calculée à partir de données ouvertes. Les bâtiments actuels apparaissent à la période indiquée pour leur groupe de bâtiments (pas bâtiment par bâtiment) et les quartiers plus anciens sont une reconstitution approximative.

Quelle ville devrait grandir la prochaine ? Dites-le-moi en commentaire. Et s'il manque un bâtiment ou un monument dans votre quartier, dites-le aussi : je préfère le corriger.

### it
Lione è nata su una collina tra due fiumi ed è stata ricostruita, assediata, allagata e bombardata. Guarda più di 2.000 anni di Lione, dalla colonia romana di Lugdunum nel 43 a.C. alle torri della Part-Dieu e alla punta della Confluence.

SENZA IA. Ogni fotogramma è generato da dati aperti. Gli edifici attuali compaiono nel periodo indicato per il loro gruppo di edifici (non edificio per edificio) e i quartieri più antichi sono una ricostruzione approssimata.

Quale città dovrebbe crescere la prossima? Dimmelo nei commenti. E se manca un edificio o un monumento nel tuo quartiere, dimmelo: preferisco correggerlo.

## Note for the owner (IT, not for YouTube)

### Scelte di stile
- **Preset `mediterranean`** (non `central`): muri ocra/rosati e tetti di tegole (Vieux-Lyon, Pentes della Croix-Rousse, gran parte della Presqu'île) sono la palette dominante di Lione, e `mediterranean` ha già terracotta e ocra. `central` (pietra chiara, ardesia, mansarde alla parigina) rende bene gli isolati ottocenteschi della Presqu'île e dei Brotteaux ma farebbe grigi i quartieri antichi. Scelta da confermare sui fotogrammi QA; il passaggio a `central` e' una riga (`city.style_preset`).
- **Inizio 43 a.C.**: titolo dell'owner mantenuto. Le fonti (S1, S2) dicono "fondata nel 43 a.C." ma la data è dibattuta: il primo cartello lo dice. Nessun motivo per cambiare l'inizio.
- Regime "story": `pacing: story`, `camera: drone`, `duration: "auto"`, 22 soste, 38 cartelli, 6 capitoli.

### Anni per gruppo di edifici
Nella story nessun anno e' attribuito a un edificio singolo. I predecessori storici sono 7 `history.zones` (born/seed) con confini stimati (tutti `conf: low`, tranne la zona della riva sinistra, `medium`). I 7 monumenti parametrici sono marcatori di luogo con fase di costruzione (teatro e anfiteatro romani come anelli, il kit non ha un preset teatro; Confluences come volume generico).

### Date con `conf: "low"` (fonte mancante o non letta)
- Popolazione -43 (1.000) e 150 (60.000): stime mie, nessuna fonte letta (snippet di ricerca danno 50.000-80.000 per il II sec.).
- Cartello 1245 (Primo Concilio di Lione): S11 nomina il concilio ma non l'anno.
- Cartello 1536 (privilegi della seta di Francesco I): S2 non dà l'anno.
- Cartello 1834.31 (forte contro la Croix-Rousse): S3 non dà l'anno.
- Cartello e sosta "Rue Impériale" (anni 1850; `gutting.until` 1857 e' una scelta): S8 dice solo "anni 1850".
- Ponti: ponti "pre-1944" (anni di origine segnaposto: Guillotière 1200, Pasteur 1900, Lafayette e Ainay 1830) e Guillotière "rebuilt" 1954 (non letto in fonte aperta). Distruzione 1944 e riaperture Pasteur 1952 e Lafayette 1946: da S6, `medium`.
- Fuochi 1793 e 1834, Hôtel-Dieu 1944: date da S4/S3/S7 ma luoghi stimati. Inondazione 1856: `conf: low` per poligono e profondità.
- Polities: "Roman Empire" (-27) e "French Republic" (1793), `conf: low`.

### Punti più incerti
1. **Date della rivolta del 1831**: S3 dà 22 nov-3 dic 1831, S14 dice "ottobre 1831". Usato S3, `medium`.
2. **Piena del 1856**: rottura dell'argine della Tête d'Or il 29-30 maggio (Archives municipales, solo da snippet di ricerca) oppure 31 maggio-1 giugno (Cybele, snippet): le pagine delle Archives non erano raggiungibili dalla sandbox. La story usa "fine maggio 1856" (y 1856.41) da S5, che riporta 18 morti a La Guillotière e la visita di Napoleone III il 2 giugno. Il poligono della piena e' stimato.
3. **Ponti del 1944**: S6 indica 1, 2 e 3 settembre per ponti diversi; usato 1-3 settembre (y 1944.66-1944.70). Il kit non ha "ponte distrutto e ricostruito": ogni ponte e' modellato come due voci (vecchio, spostato di 25 m, e nuovo) per non far sovrapporre le due fasi nella funzione `bridges_pass`; verificare sul DATA reale.
4. **Coordinate**: punti presi da OpenStreetMap/Nominatim (S16). Stimati e non verificati: seed e poligoni delle zone, centro del teatro romano (punto del museo Lugdunum), linee dei ponti Pasteur e d'Ainay, ring di tutti i fuochi e della piena. Il centro del quartiere e' usato dove manca di meglio.
5. **Cartelli**: S14 per l'UNESCO 1998 parla di "area", il sito e' piu' ampio.
6. Fonti non raggiungibili dalla sandbox (rete): musee-orsay.fr, archives-lyon.fr, cerege.fr, vici.org. Nessuna e' in `sources`.

### Problema del kit (non toccato)
`python -m kit.city_json lyon` fallisce con `regia.duration: "auto"` (`float('auto')` alla riga 85 di `kit/city_json.py`, ramo shorts). Il validatore (`build_city` + `validate`) passa con `duration` numerica; `kit.qa.check_story` passa (chiavi, 16 fonti, date con fonte). `python -m kit qa lyon` e il vero `--check-only` aspettano `data_lyon/` (non ancora presente).
