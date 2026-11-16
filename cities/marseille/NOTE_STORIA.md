# Marseille: note della story (yb-historian, 16/11/2026)

Tag: [Certain] letto in una pagina aperta | [Likely] coerente ma non riletto o fonte secondaria | [Guessing] stima mia, da verificare.
Fonti: `story.json` -> `sources` S1-S30 (URL e citazione). Pagine aperte con WebFetch: Wikipedia EN (History of Marseille, Timeline of Marseille, Provence, Incorporation of Provence, Marseille roundup, Hotel de Ville, Vieille Charite, St. Victor's Abbey, Marseille Cathedral, Notre-Dame de la Garde, Transporter Bridge, Euromediterranee, CMA CGM Tower, MuCEM, Marseille), Wikipedia FR (Rafle de Marseille, Fernand Pouillon, Cite radieuse, Rue de la Republique, Histoire de Marseille). Solo snippet di WebSearch (non riaperte): INA (demolizione 1-17 febbraio, ~1.400 edifici), sites-vauban (1666/1672/1694), Marseille Tourisme (Joliette 1844-1853, Docks), Jardin des Vestiges (mirror) e sintesi accademiche (mura greche), Catholic Encyclopedia (476/507/536). `marseille.fr` e `fresques.ina.fr` NON raggiungibili dal sandbox.

## Date piu' rischiose
| Dato | Valore usato | Stato |
|---|---|---|
| Fondazione Massalia | c. 600 a.C. | [Certain] (S1); l'area di 20 ha del primo impianto e' [Likely] (sintesi, S23) |
| Mura greche | fine V sec., IV sec., II sec. a.C. | [Guessing/low] solo mirror + sintesi: carta con `note` |
| Assedio di Cesare | 19 apr-6 set 49 a.C. = -48,70 .. -48,32 | [Certain] (S3) |
| Visigoti | 470 (Timeline) / 476 / 480 (Provence) | [Likely]: chip e carta a 470, conf low |
| Ostrogoti 508 / Franchi 536 | 507-508 / 536-537 | [Likely]: fonti discordanti |
| Comune di Marsiglia | 1214 (Timeline) / 1212-18 / 1219 / 1230 | [Guessing/low]: carta dice "early 13th century" |
| Carlo d'Angio | conte dal 1246, presa 1252, rivolta 1262-63 | [Certain] (S1, S2, S5) |
| Provenza alla Francia | morte Carlo III dic. 1481, unione 1486 | [Certain] (S4); chip a 1481,95 |
| Torre di re Renato | 1447-1453 | [Certain] (S21) |
| Forti Saint-Jean / Saint-Nicolas | inizio 1660 | [Certain] (S2); fine 1668 / 1664 [Guessing] (S21 dice solo "XVII sec.") |
| Hotel de Ville | 1653 (25 ott) - set 1673; sopravvive nel 1943 | [Certain] (S9) |
| Vieille Charite | 1671-1749 | [Certain] (S10) |
| Estensione di Luigi XIV | decisa 1666, mura vecchie rase 1672, nuova cinta 1694 | [Likely/low] (S24, snippet) |
| Peste | 1720, ~38.000 morti su ~75.000 | [Certain] (S21) |
| Joliette / Docks | bacino 1844-1853; Docks 1858-1863/66 | [Likely] (S25, snippet) |
| Gare Saint-Charles | 1848 | [Certain] (S2) |
| Rue Imperiale | lavori 1862, inaugurata 1864, 935 case, 61 vie | [Certain] (S14); `until` 1864,0 = inaugurazione |
| N.-D. de la Garde | 11 set 1853 - 1864 (consacrata incompiuta), statua 24 set 1870 | [Certain] (S13) |
| Cattedrale nuova | 1852; prima messa 1893; fine 1896; consacrazione 1897 | [Certain] (S12): fasi 1852-1893 |
| Transbordeur | 15 dic 1905 - 22 ago 1944 (torre nord), crollo 1 set 1945 | [Certain] (S19) |
| Rafle | 22-24 gen 1943 | [Certain] (S6, S7) |
| Dinamitaggio | dal 1 feb 1943 (S6); fine 17 feb (S8, solo snippet) | inizio [Certain], fine [Likely] |
| Edifici distrutti | ~1.500 (S6, S7) / ~1.400 (S8) | [Likely]: la carta dice "about 1,500" e la nota segnala la forchetta |
| Superficie | 14 ettari, 82 vie, 850 negozi | [Likely] (un solo testo, S6) |
| Sfollati | ~20.000 (S6, S7 infobox) / 30.000 (S7 testo) | [Likely]: carta "about 20,000" |
| Ricostruzione Pouillon | inizio 1949 (S20), elenco opere 1947-53; quartiere finito 1956 (S6) | [Likely]. NON verificato "1949-1955" |
| Cite Radieuse | 14 ott 1947 - 14 ott 1952, 56 m | [Certain] (S15) |
| Euromediterranee | 1995, 310 ha, +170 ha dal 2007 | [Certain] (S16) |
| Torre CMA CGM | lug 2006 - set 2011, 147 m | [Certain] (S17) |
| MuCEM | aperto 2013 (data esatta 7 giugno [Likely], non riletta); inizio cantiere 2010,0 [Guessing] | fase low |
| Zona non occupata / Vichy 1940 | conoscenza generale | [Likely] (S30 non riaperta) |
| Date dei regimi francesi (1792-1958) | date standard | [Likely] (S30 non riaperta) |
| Popolazione -600, -350 | 2.000 / 50.000 | [Guessing]: S1 dice picco ~50.000 nel IV sec.; -600 e' un segnaposto |

## Strutture del file
- 6 zone (Massalia arcaica, Massalia ellenistica, Saint-Victor, Marsiglia medievale, estensione di Luigi XIV, Joliette), 1 cinta (greca/medievale, demolita 1672-76), 1 gutting (Rue Imperiale), 2 incendi (assedio 49 a.C. senza distruzione; Saint-Jean 1943 con `destroy`), 1 ponte (Transbordeur). Anelli e punti sono SCHIZZI a mano (+-60..150 m), conf low: vanno ridisegnati su OSM e sulla pianta del 1940. Nessun `history.water`: il Lacydon, i moli e i bacini della Joliette/Arenc NON sono modellati (compaiono con la costa moderna dal primo fotogramma, salvo land.json datato da yb-modeler).
- 13 monumenti (coordinate Wikipedia: Cattedrale, Saint-Victor, N.-D. de la Garde, Gare Saint-Charles, Stade Velodrome, Vieille Charite; le altre a memoria, +-60..150 m: da verificare su OSM prima di `footprint: auto`).
- 15 soste, 38 cartelli, 8 capitoli, 24 chip di regime (da Massalia alla Quinta Repubblica).

## Distruzione di Saint-Jean: come la mostra il kit
- Il kit NON ha un formato "edificio scomparso con poligono preciso" da dati esterni: `history.lost` (blocco con altezza, from-to) esiste ma i predecessori di zona nello stesso anello farebbero doppioni. Scelta: `fires[1]` con `destroy: true`. Misurato in una COPIA di scratch (hist_kit build su copia di data_marseille, non nel repo): 397 oggetti nell'anello (3,93 ha di impronta) vivi fino al 1943,07; 381 al 1943,10; 132 al 1943,12; 0 al 1943,14; 3 nel 1949; 110 nel 1952; 226 (3,73 ha) nel 1956. Cioe' presente, dinamitato a ondata dal lato del forte (1943,088-1943,132), vuoto 1943-49, ricostruito 1950-56 (`rebuild_years: 7` + BDNB: 21 gruppi 1950-59 nell'anello).
- I 347 isolati di prova NON sono usati come geometria: nell'anello cadono 40 isolati (5,8 ha, il test esclude i blocchi fusi > 20.000 m2) contro 3,9 ha di predecessori generati: il pre-1943 mostrato e' un'approssimazione (~2/3 dell'area costruita del 1940). Per usare i poligoni veri servirebbe che il kit sopprimesse i predecessori nell'anello (modifica del kit, NON fatta). File di controllo: `saintjean_fire_ring_check.geojson` (anello + 40 isolati) per sovrapporlo alla pianta.
- I sopravvissuti (Hotel de Ville, Hotel de Cabre, Maison Diamantee, Saint-Laurent) restano fuori o dentro per caso: l'Hotel de Ville e' un `landmark` e l'anello finisce a ovest (lon 5,3693); gli altri tre NON sono protetti e possono sparire dal render. [Guessing] che cadano nell'anello: controllo di yb-modeler.
- Cartelli: "Saint-Jean quarter is gone" (1943,22) e "Rebuilding the Old Port" (1949) dichiarano distruzione e ricostruzione; la nota sul cartello 1943 chiede di scrivere nella descrizione che le case pre-1943 sono approssimate.

## Regia e durata
- `drone.pitch_max` 38, `regia.lens` 32 (30-35 richiesti), tutte le soste `wide`; distanze camera NON toccate (yb-camera). `max_duration` 660 s come rete: tagli solo se la durata naturale la supera (`weight` decide; "max" per Massalia e 1943).
- Durata: NON misurata (`kit build` non lanciato; un tentativo in scratch e' stato negato dal sistema). Stima per analogia con Lione (17 soste + 40 cartelli = 565 s, 9:25): 15 soste + 38 cartelli + 650 anni in piu' di epoca quieta a 30 anni/s (~+20 s) = circa 9:00-10:30, [Guessing]. Da misurare con `kit build` + `kit qa`.
- Contatore fermo: nessuna coppia di soste a meno di 1 anno in punti diversi. Voli lunghi con pochi anni da controllare in QA: Rue Imperiale (1864,3) -> N.-D. de la Garde (1871,0): ~1,9 km per 6,7 anni (~0,5 anni/s con 13 s di volo: al limite della soglia 0,4); Stazione (1848,9) -> Rue Imperiale (1862,5) ~1,1 km. Cite Radieuse e Stade sono solo cartelli (a 4 km da Saint-Jean un volo sarebbe stato fermo).
- Ogni sosta con monumento ha `y0` >= fine della fase: il corpo e' costruito prima di meta' hover (condizione QA di Lione/Confluences).
- Cold open (5-8 s): dal hover 1943 (9 s, y 1943,04-1943,14; distruzione 1943,088-1943,132 = circa 4,3 s -> 8,3 s dell'hover). I secondi esatti vanno letti dallo schedule dopo il render. La miniatura NON usa il 1943: anno = primo anno (600 a.C.), a destra NOW.
- Capitoli: nessun `open.story_lead` (regola R13); capitolo VII a 1940,6 (non cade dentro l'hover del 1943). I cartelli non cadono dentro le finestre delle soste.

## Validazione eseguita
- `python -m kit qa marseille` (repo): sezione a PASS (chiavi, 30 fonti, date con fonte); b/e FAIL per dati non costruiti (roads, hist, landmarks, city json, schedule): attesi, `kit build` non lanciato. Nota: ha riscritto `cities/marseille/qa/REPORT.md` e i `corridoi_*.png`.
- In scratch (copia con `hist_kit build`): sezione c tutta PASS (rapporto densita' storica 1,3-2,3 nelle zone); d WARN per aree vuote allungate (-500, 1800, 1900, 1950: i corridoi di 120-420 m vicino a (43,2985, 5,3683) e (43,2929, 5,3777) sono da guardare); nessun FAIL su gutting dopo il build.

## Round 2 (16/11/2026)
### Fonti nuove
- S31 Inventaire general (snippet di ricerca; pop.culture.gouv.fr ed ehne.fr non raggiungibili): legge 5 ago 1844 per la Joliette, in uso dal 1847, completata nel 1853 [Likely]; legge 10 giu 1854 (Lazaret) e decreto 23 nov 1856 (Lazaret e Arenc); Arenc iniziato nov 1856, moli Lazaret/Arenc 1856-1864 [Likely]; bacino Napoleone 1859 [Likely]; Digue du Large "completata nel 1925" (non 1847) [Likely]; Bassin National: NESSUNA data trovata [non verificato, non usato].
- S32 fr:Pont transbordeur de Marseille (aperta) [Certain]: tra i quais du Port e de Rive Neuve, impalcato 239 m, pilastri 86,6 m.
- Timeline of Marseille (S2) per i nuovi cartelli: 1876 tram a cavalli, 1884 colera, 1899 2.500 anni + nascita OM, set 1903 peste bubbonica, 13 nov 1919 incendio Grand Theatre, 1922 aeroporto, 9 ott 1934 assassinio di Alessandro I [Certain]; 1967 tunnel del Vieux-Port, 1977 metro e CMA CGM, 1983 TGV, 2001 Parc du 26e Centenaire, 2007 tram [Certain]; c. 290 martirio di Vittore, I sec. diocesi/catacombe (S1) [Likely: tradizione].

### Coordinate monumenti (story prima -> dopo, scarto da data_marseille/landmarks_osm.json)
| Monumento | Prima | Dopo | Scarto |
|---|---|---|---|
| CMA CGM Tower | 43,3053 5,3637 | 43,31508 5,36582 | 1.094 m (errore mio) |
| Fort Saint-Jean | 43,2951 5,3604 | 43,29545 5,36181 | 121 m (params l 150, w 100 da footprint OSM 15.093 m2) |
| Hotel de Ville | 43,2961 5,3703 | 43,29653 5,36984 | 61 m |
| Tour du Roi Renato | 43,2955 5,3611 | 43,29512 5,36166 | 58 m: nessun nodo OSM, ora ~40 m a sud del centro del forte [Guessing] |
| Cite Radieuse | 43,2619 5,3964 | 43,26146 5,39628 | 50 m |
| Vieille Charite | 43,3003 5,3678 | 43,30057 5,36827 | 48 m |
| Gare Saint-Charles | 43,3031 5,3811 | 43,30323 5,38164 | 46 m |
| Fort Saint-Nicolas | invariato | invariato | 17 m (params l 220, w 170 da footprint OSM 37.169 m2: prima 110 x 60) |
| MuCEM 31 m, N.-D. de la Garde 26 m, Stade 18 m, Saint-Victor 2 m, Major 11 m | invariati | | < 40 m |
- Transbordeur: ERRORE di round 1 (messo all'Hotel de Ville). Ora centrato sul nodo OSM (43,292385 5,364884), linea N-S di 239 m [orientamento Guessing]; la sosta usa `area:[43.2924,5.3649,260]`.
- Controllo "a vista": non possibile nel sandbox (nessun render). Le impronte `auto` vanno guardate nel prossimo `qa --render`.

### history.water: NON aggiunto, e perche'
`history.water` (landphases) mostra una lastra di TERRA solo in [from, to): serve per terra che SPARISCE (Valencia, Turia). Il Lacydon di 600 a.C. (insenatura che penetrava fino alla Borsa/Jardin des Vestiges) e i bacini della Joliette/Arenc sono l'opposto: terra di OGGI che era mare. Il kit non ha una chiave story per questo; `build_render.py` (righe 570-577, 734) legge `DATA/reclaim.json` = `[{"r": anello in metri locali, "y": anno}]` (terra di riporto che compare nell'anno y, materiale 'reclaim'), ma nulla nel kit lo genera. Servono anelli della costa pre-1844 (carta 1840 o Etat-Major) che non ho: non ho inventato geometrie. Per yb-modeler: `reclaim.json` con (a) quai della Joliette y 1853 (in uso dal 1847), (b) moli Lazaret/Arenc y 1864 (1856-64), (c) Digue du Large (1844-1925, a tratti), (d) banchine del Vieux-Port; il Lacydon antico richiederebbe l'inverso (acqua), non supportato.

### Strade (sezione d del REPORT)
- Nastri Rue Imperiale prima del 1864: nel REPORT corrente non c'e' piu' FAIL dopo il build; ma il corridoio largo #10 (1900, 589 x 73 m a 43,30428 5,36665, strada con y 1851,4) era FUORI dall'anello di 28 m: l'anello e' stato spostato ~45 m a est (stesso `gutting`, `until` 1864,0). Da riverificare nel prossimo qa.
- Viali larghi 1800 (#7 2055 x 68 m a 43,29722 5,37314: Quai/Canebiere, y strade ~ -250 = rampa di zona; #9 340 x 23 m; #8 369 x 18 m vicino a Fort Saint-Nicolas, y ~760) e 1900 (#11, #12 ripetizioni): NON sono sventramenti documentati in questa story (la Canebiere e' del XVII sec., esiste nel 1800): questione di `roads.json` (anni delle strade larghe), la gestisce yb-modeler. Non aggiunto nessun `gutting`.

### Ritmo: cartelli aggiunti (14) per i vuoti >15 s
Vuoti (per anni, build precedente): -48,3 -> 415 (aggiunti 100, 290); 1871,6 -> 1893,2 (1876, 1884); 1893,2 -> 1906,3 (1899, 1903); 1906,3 -> 1937,5 (1919,87, 1922,5, 1934,77); 1962,4 -> 1995 (1967, 1977, 1983); 1995 -> 2011,7 (2001, 2007). Cartelli totali 52. Nessuna sosta nuova (nessun rischio di contatore fermo). Dopo il prossimo build rivedere: (1) il vuoto 1906->1937 (3 cartelli, 4-6 s ciascuno), (2) se il Transbordeur (ora a 840 m dal vecchio punto) ha cambiato il volo 1893 -> 1906, (3) i tempi dei voli lunghi 1749 -> 1848 (Vieille Charite -> Stazione: 100 anni, nessun cartello nuovo in 1750-1843 oltre 1792 e 1793: se resta un vuoto, candidati verificati: 1789-1790 Marsiglia nel dipartimento Bouches-du-Rhone (S2), 1796 biblioteca pubblica, 1811 obelisco di Place Castellane, 1837 Porte d'Aix, tutti in S2).

## Round 3 (16/11/2026)
- Cold open: finestra pulita = hover 1943 a 450,12-459,12 s (9 s, nessun cartello; ultimo cartello finisce a 450,07, il prossimo parte a 461,05). Anni lineari 1943,04 -> 1943,14: dinamitaggio 1943,088-1943,132 = 454,4-458,4 s. Taglio consigliato 453,4-459,1 s (5,7 s) o 451,1-459,1 s (8 s). Letto da schedule_marseille.json (years.json non esiste prima del render): rileggere dopo ogni build. Regola kit (regia_kit.assign): i cartelli entro y1+2 anni di una sosta scorrono sul suo hover; per questo 'condemned' e' a y 1943,02 (prima dell'hover) e 'Liberation' e' stato spostato a y 1945,67 (crollo del Transbordeur, 1 set 1945, S19/S32).
- Lunghezza anni: da -600 a 2026 = 2.625 anni (non esiste l'anno 0: 600 a.C. e' l'anno -599 astronomico). Il kit calcola 2026-(-600) = 2.626; la story fissa 'short_tag' e la seconda schermata d'apertura (open a 4 voci) a 2,625.
- Dem: Copernicus GLO-30 (prep_marseille_osm.py r.180 legge Copernicus_DSM_COG_10_*_DEM.tif; data_fr.sh r.5).
- Miniatura: kit/thumb_kit.py ha ora --city/--text-size/--lx/--rx (default invariati: 118, 215, 1065); story cover.text_size 86, cover.text_rx 960.
