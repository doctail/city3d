# Fonti cartografiche storiche di Marsiglia (yb-historian)

Letto il 2026-11-16 aprendo i ritagli a piena risoluzione. L'originale NON e nel repo (peso/licenza): `cities/marseille/mappe_raw/Stadtplan_von_Marseille_-_btv1b532606289.jpg` va riscaricato da Gallica/Commons se serve (9560x13126 px, 300 dpi).

| File | Titolo sul foglio | Anno | Editore | Scala | Qualita | Area | Georef |
|---|---|---|---|---|---|---|---|
| Stadtplan_von_Marseille_-_btv1b532606289.jpg | *Stadtplan von Marseille*, "Sonderausgabe 6.40", "Nur fuer Dienstgebrauch" | 1940 | Generalstab des Heeres, Abt. fuer Kriegskarten u. Vermessungswesen (Wehrmacht), 1940 | 1:10.000 stampata; misurata 0,845 x 0,853 m/px | Ottima: isolati tratteggiati marroni, strade crema, arterie gialle, quote; reticolo km | Mirabeau/Joliette a nord, Vieux-Port, Endoume/Roucas Blanc a sud, fino a Saint-Loup/Saint-Marguerite a est | si, `gcp_1940.json` |

Fonte: Gallica (BnF) btv1b532606289, copia su Wikimedia Commons; pubblico dominio (carta tedesca del 1940, secondo l'indicazione data dal proprietario: verificare la licenza Commons prima di pubblicare l'immagine in video).

## Sistema di coordinate [Certain, verificato]
Reticolo km stampato = **Lambert Sud (NTF Paris, EPSG:27563)**, numeri X 844-851 e Y 111-121. Verifica: Fort Saint-Jean calcolato (845.435; 115.131) cade sul fort a ~25 m; Porte d'Aix a 1 m, Bourse 6 m, Opera 13 m. Le linee del reticolo sono ruotate di ~1,9 gradi rispetto ai bordi del foglio (inclinazione ~0,035 px/px) e il foglio e dilatato ~1% in verticale (0,853 contro 0,845 m/px).

## Georeferenziazione
Affine a 6 parametri in EPSG:2154: 8 punti di fit = incroci del reticolo (posizione delle linee misurata a piena risoluzione, residuo 1,1 m rmse), 5 controlli = monumenti OSM (Cattedrale de la Major, Bourse, Porte d'Aix, Opera, Fort Saint-Nicolas). Errore sui controlli: mediana 13 m, max 45 m (Fort Saint-Nicolas: centroide OSM del contorno ampio del forte non coincide col bastione: [Likely] sbagliato il punto, non la mappa; senza di lui max 14 m). Poly2 non migliora. Limite: trasformazione datum NTF->WGS84 a 3 parametri (pyproj), ~2-5 m.

## Isolati Saint-Jean (test)
`saintjean_1940.png` = ritaglio 1770x1770 px (~1,5x1,5 km, x 2465-4235, y 6265-8035 del JPEG originale). `saintjean_isolati_test_1940.geojson` = poligoni di prova (soglia colore + componenti connesse, griglia km rimossa), esclusi i blocchi fusi > 20.000 m2. Vedi report per numeri e difetti. Non committare l'originale.
