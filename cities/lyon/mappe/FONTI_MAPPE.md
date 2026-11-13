# Fonti cartografiche storiche di Lione (yb-historian / georeferenziatore)

Letto il 2026-11-13 aprendo ogni immagine in `cities/lyon/mappe_raw/` (i nomi dei file NON sono stati considerati affidabili). Le immagini originali sono riproduzioni Gallica/BnF: NON committarle (licenza e peso da valutare). Anche gli `overlay_*.png` contengono la mappa trasformata (~8-10 MB l'uno): trattarli come derivati non committabili finche la licenza non e chiarita.

Riga di credito stampata sui fogli JPEG: **"Source gallica.bnf.fr / Bibliothèque nationale de France"** (presente in 1735, 1808, 1838, 1845, 1852, 1865, 1873). Il file `lyon 1855.png` e ritagliato e NON mostra la riga: la provenienza Gallica/BnF e presunta, non verificabile dal file.

## Tabella sintetica

| File | Titolo letto sul foglio | Anno dichiarato | Autore / editore | Scala | Qualita | Area coperta | Georef |
|---|---|---|---|---|---|---|---|
| 1735.JPEG | *Plan géométral de la ville de Lyon*, levé et gravé par Claude Seraucourt, vérifié et orienté par le R.P. Grégoire (Tiers-ordre de S. François), "en 1735 augmenté et rectifié" | 1735 | Seraucourt (rilievo e incisione), P. Grégoire | scala grafica non leggibile con certezza; dalla georef ~4.07 x 4.09 m/px (modello finale; 4.0 x 4.3 usando solo i 6 punti di fit: anisotropia instabile) | Alta nel dettaglio urbano, ma distorta (vedi sotto); vedute e cartigli ai bordi | Presqu'île, Vieux-Lyon, colline di Fourvière/Croix-Rousse, bastioni nord. NON copre Brotteaux/Guillotière (solo la testa del ponte) | si |
| 1808.JPEG | *Nouveau plan topographique et historique de la ville de Lyon, avec les projets d'agrandissements, l'An 1808* (riquadro: carta del dip. Rhône) | 1808 | non leggibile | non letta | Include PROGETTI di ingrandimento: non e uno stato reale | Presqu'île, Croix-Rousse, Vieux-Lyon, Brotteaux/Guillotière in progetto | no |
| 1838.JPEG | *Plan de la ville de Lyon 1838* con "Noms des rues, places et édifices publics indiqués par numéros" | 1838 | non leggibile | barra grafica in basso (valori non letti) | Pianta tecnica a tratto, con elenco numerato | Presqu'île, Croix-Rousse, Vaise, Guillotière e primi viali dei Brotteaux | no |
| 1845.JPEG | *Nouveau plan de la ville de Lyon où sont représentés les monuments anciens et modernes… avec Ponts, Quais, Forts, Glacis*; "Prix du plan 2f25, du guide 3f" | 1845 | gravé par Hamoir/Ramoir (lettura incerta) à Paris; se vend chez Boullieux, rue de Bourbon 33, Lyon | non letta | Buona; **stessa lastra del 1852**: sovrapposta con shift di 32 px, il contenuto coincide quasi ovunque | Presqu'île, Vieux-Lyon, Croix-Rousse parziale, strisce di Brotteaux e Guillotière | no (derivabile dal 1852) |
| 1852.JPEG | stesso titolo del 1845, data stampata 1852 | 1852 | stesso editore/incisore | non letta; georef 4.27 x 4.29 m/px (isotropa) | Buona nel centro; ruotata (nord a destra, ~25 deg). **Non e un rilievo indipendente: lastra 1845 ridatata 1852 con ritocchi limitati** | Presqu'île, Vieux-Lyon, Croix-Rousse sud, Perrache (progetto), strisce di Brotteaux e Guillotière (il foglio taglia a est) | si |
| lyon 1855.png | *Plan topographique de la ville de Lyon et de ses environs*, levé, dessiné et gravé sur pierre sous l'administration de M. Jayr (préfet du Rhône, "présentement Ministre des Travaux publics") e di M. Chaper (préfet actuel) | **"Publié en 1847"** (legenda) | Eugène Rembielinski (ingegnere geografo e incisore) e L. Dignoscyo | "Échelle métrique" (valore non leggibile); georef 6.4 x 6.6 m/px | La piu ricca e la piu estesa; fortificazioni, forti, chemins, parcelle; alcuni pannelli ai bordi tagliati | Presqu'île, Vieux-Lyon, Croix-Rousse, Brotteaux, Guillotière, Part-Dieu, Montplaisir, Perrache, isole del Rodano | si |
| 1865.JPEG | *Nouveau plan de la ville de Lyon et de ses nouveaux quartiers*, "Publié en Avril 1865" | 1865 | J.B. Cadola, marchand d'estampes, Cours de Brosses 2, Lyon | non letta; georef 5.1 x 6.0 m/px (anisotropa 15%: pochi punti) | Buona; confini colorati dei comuni; elenco vie | tutta la citta, con Brotteaux/Guillotière/Part-Dieu in tessuto urbano | si, DEBOLE (vedi errori) |
| 1873.JPEG | *Nouveau plan illustré de la ville de Lyon et de ses faubourgs*, dessiné par Driat, Paris, Garnier frères | **anno non leggibile sul foglio** (il nome file dice 1873: non verificato) | Driat (disegno), Garnier frères | non letta | Colorata per arrondissement; fogli ripiegati | Citta intera + faubourgs | no |

## Discrepanza 1855 / 1847
Il file `lyon 1855.png` dichiara **"Publié en 1847"** nel blocco titolo. Il nome file "1855" non e supportato da nulla di leggibile sul foglio. La successione dei prefetti citata (Jayr, "présentement Ministre", e Chaper "préfet actuel") e coerente con il 1847 secondo le mie conoscenze generali, da confermare con una fonte. Il contenuto e coerente con una data pre-1850: Perrache e solo un reticolo con caserme e ippodromo, nessun tessuto da stazione. DECISIONE: usare **1847** come data della fonte (nei `year_bound` delle proposte). I file prodotti per questa mappa si chiamano `*_1855` solo perche e la richiesta del proprietario.

## Avvertenze per la lettura
- 1852 e 1845 sono la stessa lastra: valgono come UNA sola evidenza (stato ~1845-1847), non due.
- 1808 contiene progetti: non si usa per dire che una strada esisteva.
- 1735 non e metrico: errore di controllo ~47 m al centro, distorsione fino a ~250-300 m sul lato est (il ponte della Guillotière risulta lungo ~470 m contro ~200 m attuali; nessun GCP a est del Rodano). Non usare per decisioni fini a est della Presqu'île.
- La legenda di 1873 non riporta un anno leggibile: non usarla come "esiste gia al 1873".

## Georeferenziazione: errori residui (metri, EPSG:2154)
Modello: affine a 6 parametri in Lambert-93 (rotazione, scala anisotropa, shear, traslazione). Provati anche polinomio di 2 grado e thin-plate-spline con smoothing 0.5/2.0 (scipy): NON migliori sul campione di controllo. Punti di controllo (GCP): centroidi/angoli OSM (Nominatim, 2026-11-13: Place Bellecour, Place des Terreaux, Palais Saint-Pierre/Hôtel de Ville storico, cattedrale Saint-Jean, Hôtel-Dieu, Saint-Nizier, Saint-Paul, Saint-Bonaventure, Place Carnot, Ainay, Palais de Justice, Célestins, ponti Bonaparte/Palais, Place Gabriel-Péri, ecc.) e i punti medi dei ponti Guillotière/Lafayette dal kit. La mappa 1855 e 1735 usano gli spigoli dei ponti sul lato Presqu'île. Nessun punto di `story.json` usato non verificato.

| Mappa | GCP (fit + controllo) | Residuo su GCP di fit (RMSE / max) | Errore sul campione di controllo (RMSE / max) | Leave-one-out su tutti (RMSE) | Giudizio |
|---|---|---|---|---|---|
| 1852 | 10 + 5 = 15 | 15.1 / 27.1 | 14.2 / 21.2 | 17.7 | OK nel centro (<40 m). Foglio ruotato; copre solo strisce a est del Rodano |
| 1855 (1847) | 12 + 4 = 16 | 30.1 / 56.3 | 39.6 / 75.7 | 39.5 | Al limite dei 40 m. Centro-Presqu'île 6-35 m; PIU DI 40 m sui ponti del Rodano e sulla riva sinistra (Morand 56, Lafayette ovest 76). NON per decisioni fini a est del Rodano |
| 1735 | 6 + 4 = 10 (<12, non raggiunti i 12 richiesti) | 11.6 / 17.4 | 46.9 / 79.6 | 36.1 | **Supera 40 m**: non usare per decisioni fini. Al centro (Terreaux, Saint-Jean, Saint-Nizier) 7-33 m; Fourvière 80 m; scala instabile (anisotropia 0.5-6% a seconda dei punti) |
| 1865 | 4 + 1 = 5 usabili (1 scartato) | 7.9 / 12.1 | 8.8 (1 solo punto) | 20.9 | DEBOLE: pochi punti, solo Presqu'île/Brotteaux nord; anisotropia 15%. Solo indicativo |

Coordinate dei punti e residui per punto: `gcp_<anno>.json`. Il file contiene anche il poligono di copertura del foglio (`coverage_wgs84`).

## Estensione edificata urbana (`extent_<anno>.geojson`)
Poligoni disegnati a mano sull'immagine georeferenziata (nessuna soglia automatica: la soglia di densita dell'inchiostro e stata provata ma il tratteggio dei rilievi e le particelle agricole la rendono inservibile). Tolleranza ~100 m; il fiume attuale (`data_lyon/land.json`) e sottratto. Estensioni prodotte per 1735, 1852 e 1855; NON prodotta per il 1865. Fuori dal poligono di copertura (`kind: map_coverage`) la mappa non dice nulla: l'assenza non prova nulla. Nel 1852 mancano Part-Dieu, Montplaisir e Guillotière est (foglio ritagliato).

## Quais e Rodano a piu bracci
Vedi `proposta_roads_maps.json` > `river_notes` (tutte `low`/`medium`: nessuna larghezza e misurata in modo affidabile).
