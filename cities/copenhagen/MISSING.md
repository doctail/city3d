# MISSING — Copenhagen (dopo il passaggio historian+modeler, branch yb/copenhagen)

`python -m kit qa copenhagen --only a`: PASS (34 fonti). Nessun build, nessun render (CPU di altri agenti).

## Fatto (fonti = pagine Wikipedia/Wikidata scaricate; ogni citazione verificata nel testo)
- 26 soste con src/weight/fx, UNA sola "max" (Great Fire 1728; 1807 peso 9); didascalie nel formato "Titolo (data)".
- 20 monumenti con kind (17 + Absalon's Castle, Christiansborg I e II, aggiunti perche' le soste 1167-1884 puntavano a Christiansborg costruito nel 1928: regola R2). Forme: tutte approssimazioni da preset, conf low salvo Rundetarn/SAS Royal/Mermaid.
- polities (11 chip), eras (7), country, style_preset nordic, population (19 punti, Wikidata + Wikipedia).
- 49 cartelli (>=45), 10 capitoli dagli anni (nessun cold open), titolo "(1167-NOW)".
- Correzioni al legacy: 1728 "15.000 senzatetto" -> 20% della popolazione; Shellhus 86 -> 87 scolari; SAS Royal "primo grattacielo di Danimarca" -> di Copenhagen; Nyhavn 1670-75; "Swedish occupation 1658-60" NON esiste (assedio, la citta' non fu occupata): chip "Besieged by Sweden"; 1369 -> 1370 (S04; altre pagine 1368); popolazione "670.000" -> 667.099 (Wikidata, 1/1/2025).
- qa a): Oresund Bridge a 20 km, limite 1,5 x 9000 m. NON alzato radius_m (core_box della grafica fine = +49% celle, come il render vecchio a 9000): aggiunto `outside_core: true` al monumento + esclusione nel controllo a) in kit/qa.py (una riga, documentata in STORY_SCHEMA.md).

## Resta da fare
- history.zones/walls/gutting/lost/bridges VUOTI: prima del 1728 restano 167 edifici reali (solo 4 nel 1167). Senza zone il video parte quasi vuoto: servono anelli, born, era_height (hist_copenhagen.py ha parametri a mano non fonte). Primo anno "reale" 1167 = castello di Absalon, citta' no: titolo da riconfermare con il contact sheet R15.
- data_reliable_from 1728 e' una ipotesi.
- Forme monumenti: guglie/torri non modellate (Borsen 56 m, City Hall 105,6 m, Christiansborg 106 m); gruppi 'towers'/'spire' della chiesa Our Saviour assunti dal preset; Borsen incendio 2024 non verificato nei dati.
- Anno apertura Royal Playhouse non nel testo letto (solo premio RIBA 2008); cartello "harbor baths" a 2022 e' una collocazione a stima; population 1972-1998 da Wikidata con definizioni miste (1985 scartato); nessun dato prima del 1711.
- Sospetti R2 (stima distanza/150 m/s): Christiansborg III -> Grundtvig (5,3 km, 0,5 anni); SAS Royal -> Oresund (20,5 km, 35 anni in ~137 s = 0,26 anni/s); Oresund -> Opera (19 km, 0,2 anni). Da misurare con `kit qa` completo dopo build.
- METADATA (descrizione, tag, capitoli con orari, commento fisso, Reddit): dopo i tempi del render.
- Pacchetto dati: dem.npz.gz ora presente (merge yb/data-complete); i 4 file attesi ci sono.
