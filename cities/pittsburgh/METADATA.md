# Pittsburgh: METADATA (YouTube) — SCHELETRO PROVVISORIO fino al render (yb-historian, 17/11/2026)

**Tutto provvisorio.** Nessun render ancora. Gli orari dei capitoli sono `TBD at render`: non inventati; si ricavano da `years.json` del render (capitolo = t_in della carta - 2,8 s; carta/sosta = t_in; nessun cold open, R14: gli orari sono quelli del render cosi' come sono). Schedule locale attuale: 9:41,1 (581 s), solo indicativo. Il primo capitolo e' 0:00.

## Title (<= 100 characters)
EVOLUTION OF PITTSBURGH | 3D City Timelapse (1754-NOW) | No AI

(Formula della serie, R14; anno = primo anno del video e della miniatura: 1754. Decisione e alternative in `NOTE_STORIA.md`.)

## Titles (translations, schema di Marseille)
- fr: ÉVOLUTION DE PITTSBURGH | Timelapse 3D de la ville (1754-AUJOURD'HUI) | Sans IA
- it: EVOLUZIONE DI PITTSBURGH | Timelapse 3D della città (1754-OGGI) | Senza IA
- es: EVOLUCIÓN DE PITTSBURGH | Timelapse 3D de la ciudad (1754-HOY) | Sin IA
- de: ENTWICKLUNG VON PITTSBURGH | 3D-Zeitraffer der Stadt (1754-HEUTE) | Ohne KI
- pt: EVOLUÇÃO DE PITTSBURGH | Timelapse 3D da cidade (1754-HOJE) | Sem IA

Lingue della serie per titolo, descrizione e capitoli: **EN (principale), fr, it, es, de, pt-BR**. Descrizioni e capitoli tradotti: da produrre (yb-packaging) con il testo finale e gli orari del render, come in `cities/marseille/CONSEGNA_YOUTUBE.md`.

## Description (EN) — bozza
Pittsburgh began as two forts at the Forks of the Ohio, where the Allegheny and Monongahela rivers meet. Watch 272 years of Pittsburgh grow, from the French Fort Duquesne in 1754 to the iron and steel city, the Renaissance, the closing of the mills and the towers of today.

NO AI imagery. Every frame is rendered from open data. Buildings that stand today appear in the year recorded by the Allegheny County assessor for their parcel, not necessarily the year of the oldest structure on it; downtown towers use the years and heights listed on Wikipedia and Wikidata. Before 1880 the city is a reconstruction, and so are the Lower Hill District before its clearance in the 1950s and the warehouses and rail yards of the Point: shapes and dates there are estimated. The steel mills are not in the data and do not appear.

Which city should grow next? Tell me in the comments. And if a building or a date is wrong in your neighborhood, tell me that too: I would rather fix it.

CHAPTERS
TBD at render. 0:00 Pittsburgh today, then, with their time from `years.json`:
- I · Forts on the Forks (1754)
- Fort Duquesne, then Fort Pitt (1754-64)
- II · A Town on the Frontier (1777)
- III · The Iron City (1816)
- The Great Fire (1845)
- IV · Steel City (1859)
- The Smithfield Street Bridge (1883)
- Homestead (1892)
- Allegheny City joins Pittsburgh (1907)
- The Hill District (1920)
- V · Between the Wars (1927)
- The St. Patrick's Day flood (1936)
- The Cathedral of Learning (1937)
- VI · Renaissance (1946)
- The Lower Hill is cleared (1956)
- The Civic Arena opens (1961)
- VII · Collapse and Reinvention (1970)
- PPG Place (1984)
- Three Rivers Stadium is imploded; PNC Park and Heinz Field open (2001)
- VIII · Eds, Meds and Robots (2004)
- Sources

(La lista e' il candidato; gli orari reali decidono quali voci distano almeno 10 s.)

SOURCES AND LICENSES (draft; verify before publishing)
- Buildings: Allegheny County Building Footprint Locations (WPRDC): roof outlines compiled photogrammetrically from aerial photography of 1992-93, updated in 2004 and 2015; year built from the Allegheny County property assessments. **The dataset page states "License not specified": check the county terms before publishing.**
- Streets, rivers: Allegheny County GIS street centerlines and river data (WPRDC). Terrain: USGS 3DEP 1 arc-second elevation.
- Downtown towers: heights and years from Wikipedia and Wikidata, checked with USGS LiDAR.
- History: Wikipedia (History of Pittsburgh, Fort Duquesne, Fort Pitt, Timeline of Pittsburgh, Great Fire of Pittsburgh, Pittsburgh flood of 1936, Mellon Arena, Hill District, Homestead strike, Cathedral of Learning and others listed on the sources card).
- Population: census figures via Wikipedia.
- Music: from the YouTube Audio Library (track names as in the final overlay).

## Regole del proprietario (applicate)
- Il 1936 NON e' un gancio da titolo o miniatura: e' un capitolo/cartello come gli altri; nessun cold open (R14).
- Miniatura: formula della serie `1754 > NOW / PITTSBURGH`, anno di partenza e NOW, nessuna bandiera. **Rischio**: il fotogramma 1754 e' un forte nel bosco; `NOTE_STORIA.md` propone di usare il Point 1759-61 (Fort Pitt) con il testo "1754". Da decidere con packaging prima dei `cover.shots`.
- Testi a schermo e titoli in inglese americano (verificato nella story).

## Dichiarazioni obbligatorie (da portare nei testi finali)
- Prima del 1880 la citta' e' una ricostruzione (pillola a schermo); Lower Hill e Point pre-1950s: ricostruzione.
- Le acciaierie (Homestead, Duquesne, J&L South Side...) non sono nel dato e non appaiono: il cartello 1991 lo dice.
- Anni degli edifici di oggi: particella (assessor), non edificio per edificio; il 11% dei footprint non ha anno ed e' stimato dai vicini (89% con anno vero, 60% dell'area, misura locale).
- Alluvione del 1936: limite noto, il livello dell'acqua nel render e' un valore di prova (3 m): non e' una sosta.
- Nessun numero di vittime oltre quelli sourced nei cartelli (flood: "at least 69"; Homestead: "ten men").

## Tag (provvisori; un solo campo, tutte le lingue, max 500 caratteri)
```
pittsburgh, evolution of pittsburgh, pittsburgh history, history of pittsburgh, pittsburgh 3d, 3d timelapse, city timelapse, city evolution, how pittsburgh grew, fort pitt, fort duquesne, steel city, point state park, pittsburgh bridges, pittsburgh skyline, civic arena, three rivers stadium, lower hill district, pittsburgh timelapse, no ai, histoire de pittsburgh, storia di pittsburgh, 3d map, urban history, year built
```
(~430 caratteri; da ricontare e adattare con la ricerca vidIQ solo se il proprietario la chiede: nessun credito speso qui.)

## Commento fissato (bozza EN; FR/IT da produrre)
```
Find your street: in what year does your building appear? Tell me in the comments (and the year you think it should be).

Which city should grow next? Vote with a comment.

Limits, so you can check: today's buildings take the year recorded for their parcel by the county assessor; downtown towers use Wikipedia and Wikidata years. Before 1880 the city is a reconstruction, and so are the Lower Hill District before 1956 and the Point's warehouses before the 1950s. The steel mills are not in the data. The 1936 flood is shown only as a story card: the water level in the render is a test value.
```

## Costo
NON misurato. Nessuna cifra. (Base misurata solo per Lione: ~29 s di pod per secondo di video + 30 min di scena per processo; non estrapolare a Pittsburgh, ~180K edifici, senza misura.)

## Cosa manca / dipende dal render
- Orari definitivi dei capitoli (`years.json`) e traduzioni di descrizione, capitoli e commento (fr, it, es, de, pt-BR).
- Miniatura e `cover.shots` (non pianificati qui).
- Reddit, distribuzione, nota stampa, comando di montaggio, Short: `COPERTINE.md`, `REDDIT_DISTRIBUZIONE.md`, `MONTAGGIO.md`, `SHORT.md` come Marseille: non prodotti in questo passo.
