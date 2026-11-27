# MISSING — Copenhagen (dopo il passaggio historian+modeler, branch yb/copenhagen)

`python -m kit qa copenhagen --only a`: PASS (34 fonti). Nessun build, nessun render (CPU di altri agenti).

## Fatto (fonti = pagine Wikipedia/Wikidata scaricate; ogni citazione verificata nel testo)
- 26 soste con src/weight/fx, UNA sola "max" (Great Fire 1728; 1807 peso 9); didascalie nel formato "Titolo (data)".
- 20 monumenti con kind (17 + Absalon's Castle, Christiansborg I e II, aggiunti perche' le soste 1167-1884 puntavano a Christiansborg costruito nel 1928: regola R2). Forme: tutte approssimazioni da preset, conf low salvo Rundetarn/SAS Royal/Mermaid.
- polities (11 chip), eras (7), country, style_preset nordic, population (19 punti, Wikidata + Wikipedia).
- 49 cartelli (>=45), 10 capitoli dagli anni (nessun cold open), titolo "(1167-NOW)".
- Correzioni al legacy: 1728 "15.000 senzatetto" -> 20% della popolazione; Shellhus 86 -> 87 scolari; SAS Royal "primo grattacielo di Danimarca" -> di Copenhagen; Nyhavn 1670-75; "Swedish occupation 1658-60" NON esiste (assedio, la citta' non fu occupata): chip "Besieged by Sweden"; 1369 -> 1370 (S04; altre pagine 1368); popolazione "670.000" -> 667.099 (Wikidata, 1/1/2025).
- qa a): Oresund Bridge a 20 km, limite 1,5 x 9000 m. NON alzato radius_m (core_box della grafica fine = +49% celle, come il render vecchio a 9000): aggiunto `outside_core: true` al monumento + esclusione nel controllo a) in kit/qa.py (una riga, documentata in STORY_SCHEMA.md).

## Fatto in questo passaggio (history da hist_copenhagen.py / fetch_dk_roads.py, branch yb/copenhagen)
- history.zones 33 (bande concentriche per le curve di anno: citta' medievale, Ny-Kobenhavn, Nyhavn, Frederiksstaden, Christianshavn, Holmen, 5 villaggi, 11 anelli oltre i bastioni, 6 anelli Amager), walls 1 (bastioni, keep Kastellet e Christianshavn), fires 3 (1728, 1795, 1807 con origini), water 5 (terre di riporto), bridges 7. Fonti nuove S38-S56 (Wikipedia, citazioni verificate come sottostringa); S22/S23 estese.
- `kit qa copenhagen --only a`: PASS (54 fonti). Su copia dei dati (hist_kit build in /tmp, nessun render): qa b PASS, qa c PASS (castello di Absalon NON e' una zona: e' un landmark, la zona dava FAIL di densita' su 25.000 m2), qa d solo WARN (aree vuote nel 1800/1900/1950, nessun gutting).
- Correzioni al legacy: Teglvaerksbroen 2010 -> 2011 (foglia installata a gen 2011); Valby e Bronshoj 1186 (prima menzione, legacy 1250/1200); Kastrup 1749 (legacy 1700); Frederiksberg 1651 (legacy 1660); Islands Brygge riempimento 1901 (legacy 1905); bombardamento 1807 "oltre mille edifici" (legacy 300); rampe demolite a tratti 1853-1890 (il vallo ovest c'era ancora nel 1868, viale 1890), non solo 1853.
- La pagina S22 dice "died out on Sunday, 7 July": errore, il 5 giu 1795 era venerdi; finestra 5-7 giu.

## Resta da fare
- Anelli oltre i bastioni, bande medievali, rampe interne: anni da curve calibrate sul 10o percentile BBR, NON da fonte (conf low, nota "stima"). Area di riporto Sydhavn (1905) senza fonte; Sundbyvester senza fonte. Nessuna fonte per Ny-Kobenhavn oltre al 1612/1631.
- history.water sostituisce DATA/reclaim.json: al build kit togliere reclaim.json dalla cartella DATA (altrimenti lastra doppia). Colore 'field' invece di 'reclaim'.
- history.gutting, lost e mura medievali VUOTI (non c'erano dati legacy): H.C. Andersens Boulevard (1890/1930), Vester Voldgade, Kongens Nytorv, strade aperte tra i bastioni; QA d avvisa su aree vuote 1800/1900/1950.
- Ponti: solo 7 con fonte. Restano con anno legacy "Likely" non verificato: Hojbro (1300), Holmens Bro (1680), Borsbroen (1640), Marmorbroen (1745), Bryghusbroen/Lille Langebro mese, Dronning Louises Bro (1620/1887: pagina letta ma il poligono OSM non e' nominato), Cirkelbroen 2015 (nessun poligono), Kalvebod Bolge 2013, Sjaellandsbroen 1959, Metro 2002, Oresundsbanen 1999. Ponti senza nome nei dati hanno anni da edifici vicini.
- data_reliable_from 1728 e' una ipotesi, da confermare con il contact sheet.
- Titolo "(1167-NOW)": all'anno 1167 restano 4 edifici reali + landmark (castello); la citta' parte dal 1185.
- Forme monumenti: guglie/torri non modellate (Borsen 56 m, City Hall 105,6 m, Christiansborg 106 m); gruppi 'towers'/'spire' della chiesa Our Saviour assunti dal preset; Borsen incendio 2024 non verificato nei dati.
- Anno apertura Royal Playhouse non nel testo letto (solo premio RIBA 2008); cartello "harbor baths" a 2022 e' una collocazione a stima; population 1972-1998 da Wikidata con definizioni miste (1985 scartato); nessun dato prima del 1711.
- Sospetti R2 (stima distanza/150 m/s): Christiansborg III -> Grundtvig (5,3 km, 0,5 anni); SAS Royal -> Oresund (20,5 km, 35 anni in ~137 s = 0,26 anni/s); Oresund -> Opera (19 km, 0,2 anni). Da misurare con `kit qa` completo dopo build.
- METADATA (descrizione, tag, capitoli con orari, commento fisso, Reddit): dopo i tempi del render.
- Pacchetto dati: dem.npz.gz ora presente (merge yb/data-complete); i 4 file attesi ci sono.
