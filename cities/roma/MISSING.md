# MISSING — Rome (aggiornato da yb-historian + yb-modeler, branch yb/roma)

Stato: `python -m kit qa roma --only a` = PASS (53 fonti, date con fonte). Nessun build, nessun render, nessun pod. Le stime R2 sotto NON sono misure: valgono solo dopo `kit qa roma` completo.

## Compilato (con fonte)
- Fonti: 53 (Wikipedia EN/IT, Wikidata Q220). Ogni citazione e' stata ricontrollata come sottostringa del testo scaricato; per Wikidata la serie e' ricavata dal JSON.
- Monumenti: 19 con `kind`/`params`, tutti con `src`/`conf`. Tolti: `Palatine Hill` (collina, non un edificio), `Aurelian Walls` e `Servian Wall` (stanno in `history.walls`, evitano il doppio disegno); `Hadrian's Mausoleum` e `Castel Sant'Angelo` fusi in uno.
- Soste: 22, tutte con bersaglio risolto (i 3 TODO: Alaric -> area Porta Salaria; acquedotti 537 -> area Aqua Virgo/Pinciana, posizione stimata, conf low; capitale 1871 -> area Porta Pia). Un solo `weight: "max"` (Colosseum), fx e `src` su tutte. Il bersaglio "Palatine Palace" del 753 a.C. e' sostituito da un'`area` sul Palatino (il palazzo e' del I secolo d.C.).
- Cartelli: 48 (minimo 45), tutti con `src`; 8 capitoli da anni (nessun cold open).
- Regimi: 17 chip (Regno, Repubblica, Impero, Odoacre, Ostrogoti, Bizantini, Stato Pontificio, Repubblica Romana 1798, ripristino, Impero francese 1809-14, Repubblica Romana 1849, Regno d'Italia, fascismo, Roma liberata, Repubblica). `country: Italy`, `style_preset: mediterranean`, 10 ere.
- Popolazione: 37 punti (Wikidata dai censimenti dal 1861; stime Wikipedia IT/EN prima), con `pop_conf` e `pop_src`.
- Mura: Serviana (378 a.C., 246 ha), Aureliana (271-275, 8 m, torri ogni 29,6 m), Leonina (848-852, 3 km, 44 torri). Il Gianicolo e' dentro il tracciato aureliano (Trastevere, riva destra).
- Zone: 4 (primi insediamenti, Roma serviana, Roma entro le mura aureliane, Citta' Leonina). Incendio del 64.
- Titolo: `EVOLUTION OF ROME | 3D City Timelapse (753 BC-NOW) | No AI`. Primo anno davvero mostrato: 753 a.C. (`start_year`, `open.rewind_to` e prima sosta); "2,778 YEARS" (il vecchio "2,779" contava un anno zero).

## Da compilare / limiti (e perche')
- **Contorni non rilevati (conf low):** Serviana (anello legacy riscalato a 246 ha: Aventino e Termini restano fuori dal disegno), Leonina (schizzo a mano, perimetro forzato a 3 km), zona del Palatino, area dell'incendio. Servono tracciati veri (OSM `historic=citywalls` o archeologici), non raggiunti.
- **Parametri a mano (non dati):** `born`, `era_height` (metri), densita' delle 4 zone; il kit non ha spopolamento: la Roma imperiale resta finche' l'edificio attuale la sostituisce (R15: contact sheet locale prima del GO).
- **Scelte di modello non nelle fonti:** demolizione della Serviana (271), anni di costruzione di Palazzo di Domiziano (regno 81-96), Pantheon (124-126), Termini (1949), Stadio Olimpico (1951), Circo Massimo (329 a.C. = stalli).
- **Orientamenti/dimensioni** dal legacy `landmarks.json` e ipotesi (Pantheon, Marcello, S. Pietro, piazza S. Pietro approssimata): [Guessing], da vedere nel contact sheet.
- Non compilati per mancanza di fonte letta: `gutting`, `lost`, `water`, `bridges` (Ponte Elio 134 ecc.), piene del Tevere. Cartello etrusco "-615" tolto (data non verificata).
- Solo fonti secondarie (Wikipedia/Wikidata); nessuna fonte primaria.
- `data_reliable_from: 1919` [Likely]: gli anni degli edifici vengono da sezioni ISTAT 2011 (statistiche), non da catasto.
- Metadata (capitoli con orari, descrizione, tag, commento fisso, Reddit), miniature, consegna: non fatti (dipendono dal render).
- Credito dati nella carta delle fonti (ISTAT, OSM, Copernicus) dedotto da `prep_roma.py`/`data_roma.sh`: da confermare.

## Stime R2 (da confermare con `kit qa`)
- Monumenti: nessuno costruito dopo la meta' del proprio hover (controllato sulle fasi; ho spostato le finestre di Colosseo 77-84, Pantheon 122-130, cupola 1588-1596, Vittoriano 1908-1914).
- Voli: tra soste consecutive gli anni/s stimati (volo a 150 m/s) restano sopra 0,4; `regia.rmin` = 1.0. Non misurato dal kit.
- Anno di partenza: le uniche costruzioni vive nel 753 a.C. sono quelle della zona dei primi insediamenti (~86 ha); non verificato che non compaiano edifici moderni.
- Distanza camera mediana e inclinazione: non misurate (richiedono `kit build`).

## Pacchetto dati per `kit pack`/`kit data`
- cartella: `data_roma_src`; presenti: buildings, dem, land, landmarks, parks, roads (.gz). Completo.
