# Pittsburgh: note della story (yb-historian, 17/11/2026)

Tag: [Certain] letto in una pagina aperta in questa sessione | [Likely] coerente ma non riletto, o dal dataset skyline (2 fonti) | [Guessing] stima mia, da verificare.
Fonti: `story.json` -> `sources` S1-S33 (URL e citazione). Pagine Wikipedia EN aperte con l'API (`action=query&prop=extracts`): History of Pittsburgh, Fort Duquesne, Fort Pitt, Timeline of Pittsburgh, Great Fire, flood 1936, Mellon Arena (Civic Arena), Three Rivers Stadium, Smithfield Street Bridge, Point State Park, Carnegie Steel, Hill District, Homestead strike, Great Railroad Strike 1877, Cathedral of Learning, Gulf Tower, PPG Place, PNC Park, Acrisure Stadium, U.S. Steel Tower, Forbes Field, Fort Pitt Block House, Duquesne Incline, Strip District, Homestead Steel Works, J&L, Pittsburgh (censimento). Metadati WPRDC letti dall'API CKAN. Per Palazzo di giustizia, Frick Building, Union Station, Wabash Terminal, Carnegie Institute, Three Sisters, ponti: solo il dataset skyline (`pgh_skyline`, 67 monumenti, 23 verificati da 2 fonti), pagine NON riaperte.

## Primo anno: 1754 (decisione)
- **1754** = primo costruito documentato nel sito: Fort Prince George (17 feb 1754, Virginiani) e Fort Duquesne (aprile 1754, ~500 francesi) [Certain] (S3, S5). Titolo: `EVOLUTION OF PITTSBURGH | 3D City Timelapse (1754-NOW) | No AI`; 272 anni.
- Scartati: **1758** (nome Pittsburgh, Fort Pitt) perderebbe i francesi e il chip "New France"; **1780** = primo anno con edifici nel dato (10; sotto il 1850 solo 226, `misure_pgh_ext_years.json`): una citta' non c'e', e si perderebbero 26 anni di forti senza guadagnare dato.
- Costo/rischio dichiarato: all'anno 0 del video gli **edifici vivi sono 0** (il kit: "edifici vivi 1754: 0, 1800: 1.992, 1900: 47.081"; i forti sono mura, non edifici). I primi 45 s sono forti (hover di 23 s sul Point con 4 cartelli). **Rischio miniatura**: il fotogramma 1754 e' un forte nel bosco, non "due meta' piene di citta'" (regola 15/11). Rimedio previsto: sul lato sinistro usare il Point 1759-61 (Fort Pitt a stella + casette) con il testo "1754". Se il proprietario non lo accetta, il ripiego e' 1816 (citta'); costa il rifacimento dei primi 8 cartelli. [Likely] la scelta migliore, ma e' la decisione da guardare.

## Numeri (build locale `python -m kit build pittsburgh` + `kit qa`, 38 s, dati copiati in `data_pittsburgh/` ignorata da git)
- 12 soste, 50 cartelli, 8 capitoli, 8 chip polity, 18 monumenti, 7 zone/gutting, 2 forti (mura), 1 incendio, 7 anelli alluvione, 6 ponti, 32 fonti.
- Schedule: **9:41,1** (13.946 fotogrammi), hover 83 s, volo 470 s. `max_duration` 660 non limita nulla. `night: false` come nella story esistente (la notte = secondo build di scena: decisione del chat).
- QA: **nessun FAIL**; a) 3 PASS (chiavi, 32 fonti, date con fonte), b) dati PASS (179.756 edifici, anno 0: 0, hist 31.884 predecessori), e) velocita' max 235 m/s (limite 250), accelerazione 108 (120), distanza camera mediana **1.891 m** eq. 35 mm (soglia 1.200), nessun volo >=12 s sotto 0,4 anni/s, monumenti visibili a meta' hover, ritmo senza vuoti >15 s (max 14,3). Per stare nei limiti: `drone.v_leg` 90 (default 150; con 125 e 100 vmax 271 e 253 m/s).
- WARN non risolti (spiegati): d) corridoi/aree vuote/viali larghi 1800-1950 (la QA e' tarata su citta' antiche dense: qui sono i viali moderni (rive, rampe, ferrovie) senza predecessori); **2 FAIL d) 1854 trasformati in WARN con `qa.accept`** (rive del Monongahela e dell'Allegheny, riviera aperta nel 1854); grafico del percorso non fatto (manca matplotlib).
- **Non controllato dalla QA**: `qa --render` (serve bpy: nessun fotogramma visto), forma/aspetto dei monumenti e dei forti, posizione degli anelli disegnati a mano, ponti (se `bridges.json` della pipeline ha gia' il ponte il kit cambia solo l'anno, altrimenti ne aggiunge un secondo: 6 aggiornati / 4 aggiunti, da guardare), angolo di sguardo (nessuna riga QA; `pitch_max` 30 come Marsiglia), densita' storica (c) non stampata, miniature e `cover.shots` (non pianificati), cold open (nessuno, R14).

## Struttura e scelte
- **Cartelli e soste**: eventi senza bersaglio salvo i monumenti (etichetta). Stop (12) distribuiti: Point 1754-64 (O), Great Fire 1845 (S del centro), Monongahela Incline 1870 (S), Smithfield Street Bridge 1883, Courthouse 1888, Allegheny City 1907 (N), Hill District 1920 (E), Cathedral of Learning 1937 (Oakland, E), Civic Arena 1961 (Lower Hill), PPG Place 1984-85, Three Rivers/PNC/Heinz 2001 (N shore), Tower at PNC Plaza 2015. **12 e non 15**: ogni altra sosta (Union Station, Frick, Three Sisters, Gulf Tower, Forbes Field, US Steel Tower, Point Park 1974, Gateway/Wabash) falliva la regola "volo >=12 s sotto 0,4 anni/s" con i vicini, quindi e' un cartello con bersaglio; non ho riempito per arrivare a 15. Ogni monumento bersaglio ha il corpo finito prima di meta' hover (QA PASS).
- **Regola dei cartelli nell'hover** (letta in `regia_kit.assign`): un cartello entro y1+2 anni dalla sosta scorre nel suo hover; ho spostato Rebuilds (1847,5) e Allegheny (1907,0-1907,4) o allungato PPG (1984,3-1985,7) perche' gli anni del cartello e del contatore coincidano. Cartelli sopra l'hover del Point: 1755,5 / 1758,9 / 1763,5 / 1764,5 (coerenti con la finestra 1754,3-1764,9).
- **Capitoli** (8): Forts on the Forks 1754 | A Town on the Frontier 1777 | The Iron City 1816 | Steel City 1859,5 | Between the Wars 1927 | Renaissance 1946 | Collapse and Reinvention 1970,54 | Eds, Meds and Robots 2004,5. Nessun `open.story_lead` (c'e' il capitolo I, R13). Nessun gancio / cold open: **il 1936 e' un cartello e basta** (richiesta) e non una sosta; gli anelli alluvione (7, `depth` 3 = valore di prova) restano come nella story precedente: **limite noto, il visual dell'acqua non e' garantito**.
- **Chip polity (8)**: contesa Virginia/Nuova Francia 1754,0 -> New France (Fort Duquesne) 1754,3 -> British Empire (Fort Pitt) 1758,9 -> United States con disputa Virginia/Pennsylvania 1776,5 [Guessing/low: data = 4 luglio 1776, la disputa e' S2/S4] -> Pennsylvania 1780 -> Borough 1794 -> City 1816,21 -> Greater Pittsburgh 1907,95 (Allegheny annessa). Nessuno stato "stantio" al 2026.
- **Zone (5) e ricostruzioni**: Golden Triangle (1760-1850, seme a Fort Pitt), Allegheny City, South Side/Birmingham, Hill District, Strip/Lawrenceville; tutte `conf: low`, contorni a mano (+-100 m), mai rilevati. **Gutting**: Lower Hill (anelli di lotti rimossi 1955,5-1956,8; S14: 1.300 strutture, estate 1956; S8: 1955-60) e Point (magazzini e scali, fino al 1953; S11, S2). `data_reliable_from` 1880 (pillola "RECONSTRUCTION" prima). Non sono modellati: le acciaierie (demolite, non nei footprint), la Carnegie Building (demolita 1952, S12), il Bethel AME (1960).
- **Mura/forti** come `line` chiuse (non `ring`, per non diventare `WALL_P`, codice Valencia): Fort Duquesne (quadrato 70 m, 1754,3-55,0, distrutto 24 nov 1758) e Fort Pitt (pentagono R 95 m, 1759-61,5, demolito 1797,6-98,8: durata della demolizione [Guessing]). Posizione +-100 m: da spostare sulle linee di granito di Point State Park in OSM.
- **Incendio 1845**: ring ~27 ha del sud-ovest del centro, finestra visiva 12 giorni (1845,268-1845,30) solo per rendere visibili le fiamme durante un hover di 6 s; l'incendio reale duro' ore (S6). Effetto `destroy` solo sui predecessori (il centro attuale e' 1900+).

## Date piu' rischiose e conflitti (usato l'anno verificato)
| Dato | Valore usato | Stato |
|---|---|---|
| Fort Prince George / Duquesne | 17 feb / 18 apr 1754 | [Certain] (S3, S5) |
| Distruzione di Duquesne, Forbes | 24-25 nov 1758 | [Certain] (S3, S11) |
| Assedio di Fort Pitt | 22 giu 1763; sollievo 10 ago (S4) vs 20 ago (S5) | [Likely]: cartello dice "in August" |
| Block House | 1764 | [Certain] (S31; 2 fonti) |
| Fort Pitt abbandonato 1792, "decommissioned" 3 ago 1797, demolito | 1797,6-98,8 | [Likely]: la demolizione non ha data |
| Boro 1794, citta' 18 mar 1816 | | [Certain] (S5, S2) |
| Great Fire | 10 apr 1845, 1.200 edifici (fino a), 2 morti | [Certain] (S6); il testo del cartello non cita il numero |
| Ferrovie | PRR a Philadelphia **1854** (S2) vs 1852 (S5) | [Likely]: cartello 1854 + 1851 Cleveland |
| Smithfield Street Bridge | costruito 1881-83, aperto 19 mar 1883; ponte di legno 1818 bruciato nel 1845 | [Certain] (S10). S2 chiama 1818 il primo ponte sul fiume = Smithfield |
| Railroad strike 1877 | S2: oltre 40 edifici, 100 locomotive, 1.000 vagoni, 40 morti; S16: 39 / 104 / 1.200-1.383 | [Likely]: testo "about 40, 100, over 1,000" |
| Homestead | 6 lug 1892, 10 morti (3 detective, 7 operai) | [Certain] (S2, S15); fuori dalla mappa (10 km) |
| Carnegie Institute | prima galleria 5 nov 1895 | [Likely] (dataset, non riletto); `conf: low` sul monumento |
| Courthouse | 1888 (infobox/Wikidata/OSM) vs 1886 (S2: "courthouse and jail") | [Likely]: 1888; la prigione e' 1886 |
| Frick 1902, Union Station 1903 | dataset 2 fonti | [Likely] (pagine non riaperte) |
| Forbes Field | 30 giu 1909; incendio 17 lug 1971, demolizione dal 28 lug 1971 | [Certain] (S32 + S5); fine demolizione [Guessing] |
| Gulf Tower | 1932, 177,4 m, tallest fino al 1970 | [Certain] (S18) |
| Cathedral of Learning | scavi 1926, esterno finito ott 1934, **dedica giu 1937**; la lista dice 1936 | [Certain] (S17); la sosta sta sulla dedica (1937,2-1937,75, dopo il diluvio) |
| Lower Hill | 1955-60 (S8); 1.300 strutture, 8.000 residenti, estate 1956 (S14); 95 acri (S2) | [Likely]: tre fonti, non coincidono; cartello "about 1,300 structures / more than 8,000" |
| Civic Arena | aperta 17 set 1961; demolizione dal 26 set 2011; Timeline S5 "12 mar 1958 opens" (probabile posa) | [Certain] apertura; inizio cantiere 1958,2 [Guessing] |
| Three Rivers | scavo aprile 1968, aperto 16 lug 1970, implosione 11 feb 2001 | [Certain] (S9) |
| US Steel Tower | lista/infobox completata 1970, **dedica 30 set 1971** (S28), Wikidata 1971 | [Likely]: modello finito dal 1970,9; cartello a 1971,75 |
| PPG Place | posa 28 gen 1981, dedica 11 apr 1984; **193,6 m (lista, con guglie) vs 166 m (infobox, OSM)** | [Certain] date (S19); altezza 166 m + guglia |
| PNC Park / Heinz Field | scavo 7 apr 1999 / giu 1999; apertura 2001 / prima partita set 2001 | [Certain] (S20, S29); 9 aprile 2001 [Likely] non letto |
| Tower at PNC Plaza | aperta 2 ott 2015 | [Likely] (dataset, 2 fonti); inizio 2013,0 [Guessing] |
| FNB Financial Center | 2024 (lista Wikipedia) | [Likely]: non incrociato |
| Popolazione | 1761: 332 (Timeline; 1760: 464 nella stessa pagina), 1800-1990 Timeline, 2010-2020 S23; **1754: 500 = guarnigione francese, non residenti [Guessing]** | etichetta "rough estimate", conf low |
| Mappa "1992-2015 photogrammetry" (richiesta del chat) | [Certain]: CKAN WPRDC: roof outlines da foto aeree 1992/93, aggiornate dai voli 2004 e 2015; licenza "not specified" nei metadati: **da chiarire prima di pubblicare** | S24 |
| Strip, 2004,5 "Medicine replaces steel" | **anno tematico**: nessuna data singola (S33, S2) | [Guessing] |

## Cosa e' non verificato (riassunto)
1. Anelli di zone, gutting, mura e incendio: schizzi a mano, nessun rilievo (S, conf low).
2. Monumenti: costruzione iniziale di Frick (1901,0), Carnegie (1893,5), Gulf (1930,2), US Steel Tower (1967,5), Tower at PNC Plaza (2013,0), Union Station (1898,0) e la durata della demolizione di Forbes, Wabash, Fort Pitt: stime. Impronta `auto`: Cathedral of Learning (catasto 84 m > 22: usa `params`), Monongahela/Duquesne Incline, PNC Park (nessuna impronta entro 30 m: usa `params`). Il `clear` ha rimosso 14 edifici del catasto.
3. Ponti: linee schizzate da un centro Wikipedia/OSM (+-180 m); gli altri ponti della pipeline hanno **anni stimati** (`bridges.json` da fetch_pgh.py: anno = urbanizzazione): vanno corretti da yb-modeler (Panhandle 1903, Hot Metal 1900/1887, Liberty 1928, 16th St 1923, 10th St 1933, Birmingham 1976-77, Veterans 1988, Fort Wayne RR 1904, Manchester 1915-69, Point Bridge 1927-59).
4. Date secondarie di Timeline (1788, 1828, 1840, 1868, 1872): usate solo 1794, 1816, 1868, 1872.
5. Birmingham 1811 (zona South Side): conoscenza generale [Guessing].

## Host bloccati / non raggiunti (in questa sessione)
Nessun host ha risposto 403 al CONNECT in questa sessione. `en.wikipedia.org` API: **429 (rate limit)** su raffiche, risolto con pause (tre pagine per 3 tentativi: Allegheny County Courthouse, Union Station, Frick Building NON lette). `data.wprdc.org` raggiungibile (CKAN). Dal dataset skyline (agente precedente, non ritentati): `phlf.org`, `catalog.archives.gov`, `emporis.com`, `skyscrapercenter.com`, `loc.gov`, `nps.gov`, `npgallery.nps.gov`, `digital.library.pitt.edu` bloccati (403); `hmdb.org`, `pghcitypaper.com`, `pittsburghpa.gov`, `preservationpa.org`, `api.census.gov`, `historicpittsburgh.org`, `britannica.com`, `heinzhistorycenter.org`, `pittsburghhistory.org`, `pghbridges.com`, `buildingsofpa.org` senza risposta.

## Per il chat / agenti successivi
- Rigenerare: `python -m kit build pittsburgh` (30 s) con i dati `data_pittsburgh` (non versionati): i file derivati (`schedule_pittsburgh.json`, `city_pittsburgh.json`, `montaggio/*`) NON sono stati committati su questo ramo: andranno rigenerati dopo l'unione con il ramo colore (`look`, non toccato qui).
- Prima del GO: yb-camera guarda 3 fotogrammi di volo e un hover del Point (nessuna immagine vista); yb-modeler controlla i forti, Block House, Civic Arena (cupola), Three Rivers/Forbes (forma di default), US Steel Tower (impronta triangolare), CoL; yb-packaging decide la miniatura 1754 (vedi sopra) e prepara i capitoli con gli orari del render.
- Costo pod: **non misurato**; citta' di ~180K edifici (>100K): niente anteprima, direttamente `full`. Nessun numero finche' non c'e' una base misurata per Pittsburgh.
