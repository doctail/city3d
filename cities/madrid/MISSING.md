# MISSING — Madrid (aggiornato da yb-historian + yb-modeler, branch yb/madrid)

Stato: `python -m kit qa madrid --only a` = PASS (49 fonti, 0 FAIL). Non eseguiti: build, qa b-e, render (CPU occupata, ordine del giro).
Ogni citazione in `sources` e' stata verificata a macchina come sottostringa del testo scaricato (Wikipedia es/en, via action=raw; tabella S46 sul testo delle celle).

## Compilato
- soste 19 (860-2009, una "max" = Royal Palace), tutte con `src` e `conf`; bersagli: 10 landmark, 2 fuochi, 7 aree a mano.
- landmarks 17 (14 edifici + 2 ponti + Alcazar): 11 su impronta reale del catasto (`footprint: auto`), Palazzo Reale/Alcazar/Torre PwC/ponti come preset con POSIZIONE SEGNALATA.
- polities 16 (Emirato, Califfato, Taifa di Toledo, Castiglia, Reyes Catolicos, Asburgo, Borboni, Napoleonico, Restaurazione Fernandina, Sexenio, Restaurazione, II Repubblica, assedio, franchismo, transizione, democrazia), eras 8, capitoli 8 (niente cold open), popolazione 29 punti con etichetta.
- history: 5 zone (cittadella musulmana 4 ha, citta' cristiana 33 ha, arrabales, Madrid asburgica, Ensanche), 3 mura (musulmana, cristiana, Cerca di Filippo IV 1625-1868), 3 gutting (Gran Via 1917/1922/1929), 1 lost (Caños del Peral 1738-1817), 4 fuochi (Plaza Mayor 1631 e 1790, Alcazar 1734, fronte ovest 1936).
- cartelli 66 (minimo 45), tutti con fonte; titolo `EVOLUTION OF MADRID | 3D City Timelapse (860-NOW) | No AI`.

## Stime e punti deboli (R2: tutto cio' che e' ipotesi e' `conf` low/medium e [Guessing] nella nota)
- `start_year` 860: scelta mia (il vecchio video partiva dal 1480). Le strade dei dati partono dal 1467: 860-1467 senza nastri stradali, solo zone+mura. Alternativa: 1085 o 1480 (cambia titolo e capitoli). Da decidere col proprietario insieme alla guardata della timeline.
- Tutti gli anelli delle zone/mura/Cerca/Ensanche/gutting sono SCHIZZI A MANO (+-100 m), non georeferenziati. `born` ed `era_height` sono scelte di modello.
- La zona "Mayrit" contiene 0 edifici del catasto (l'area del Palazzo Reale e' vuota): la cittadella e' solo Alcazar (preset castle 80x65 m, ipotesi) + mura; nessuna casa predecessore.
- Predecessori attesi (edifici attuali dentro le zone): citta' cristiana 295, arrabales 1.323, Madrid asburgica 7.208, Ensanche 16.421 (anello 2.258 ha). Costo del cambio da MISURARE con qa c/e prima di ogni GO; se supera il budget, stringere l'anello Ensanche.
- Palazzo Reale: nessuna impronta entro 40 m, preset a coordinate Wikipedia (140x140 m ipotesi). Torre PwC: impronta catasto 224 m2, preset 38x38 m (resta anche il pezzetto del catasto). Ponti di Segovia e Toledo: linee centrate sulla banda d'acqua del DEM, +-100 m, da verificare in locale.
- Orientamento della Almudena (asse di default) e colori/altezze dei preset: non verificati con un render.
- Altezze Cuatro Torres: da infobox Wikipedia (Espacio 230 m; la pagina Cuatro Torres dice 224,5 m): scelto 230.
- Popolazione: punto 860 = segnaposto uguale al c.1000; 1000/1480 sono di Trapiello 2020 citato da S46, non ricontrollato; serie non omogenea per le annessioni 1948-54.
- `data_reliable_from` 1900 e' un'ipotesi (54 edifici datati <1850, 1.470 <1900): leggere il report density.
- Colori delle bandiere dei chip: illustrativi, non da fonte.

## Da fare prima del GO (nulla di questo e' stato eseguito)
1. `kit build madrid` + `qa madrid` (b-e): densita', corridoi, costo, camera (R2: distanza mediana >= 1.200 m, inclinazione < 45 gradi, nessun volo >= 12 s sotto 0,4 anni/s).
2. Contact sheet locale di 24 fotogrammi 860-2026 (R15) e copertine (860 > NOW) con bpy.
3. Ponti: `history.bridges` compilato (7 voci, S50-S53: Rey 1816, Franceses 1862, Princesa 1909/1929, Praga c.1925/1952/1968). Segovia e Toledo NON duplicati: restano solo i landmark `bridge_arches`. Linee agganciate alla banda d'acqua di land.json (+-150 m), Overpass/OSM non raggiungibile (nessuna geometria OSM letta), conf low/medium; Franceses = latitudine stimata; Princesa/Praga: date di demolizione non esatte. Da verificare in locale con la build.
4. Consegna R7: `cities/madrid/METADATA.md` (descrizione, capitoli con orari finali, tag, commento fissato EN+ES, Reddit, distribuzione, nota stampa, comando di montaggio), `kit pack`.
