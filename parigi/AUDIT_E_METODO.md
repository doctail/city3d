# PARIS — DOSSIER DI RICERCA STORICA E GEOSPAZIALE
Data di chiusura della ricerca: 23 ottobre 2026

## Scopo e unità di analisi
Questo pacchetto integra fonti archivistiche, archeologiche, idrografiche, cartografiche, edilizie e ambientali per ricostruire l'evoluzione del territorio parigino dall'antichità al presente. Non è corretto descriverlo come un censimento nominale completo di ogni edificio mai esistito: nessun singolo registro copre integralmente tutte le epoche, e una parte del patrimonio edilizio scomparso è ricostruibile solo da piante, catasti, permessi, fotografie e scavi.

## Contenuto del pacchetto
- `FONTI.csv`: 40 fonti e dataset con URL, tipo, copertura e uso.
- `CRONOLOGIA.csv`: 43 eventi/periodi con livello di confidenza e fonte.
- `REGISTRO_ELEMENTI.csv`: 53 elementi e trasformazioni tra edifici, ponti, idrografia, topografia, mura, verde e infrastrutture.
- `REGISTRO_LAYER_GEOGRAFICI.csv`: 20 famiglie di layer geografici.
- `README.md`: indice.

## Evidenza storica: cosa è dimostrato
1. Cartografia catastale: Atlas Vasserot 1810–1836 e Vasserot-Bellanger 1830–1850, catasti delle comuni annesse 1808–1825 e revisioni, piani particellari 1900–1994, atlanti municipali 1937–2002 e piante edilizie archivistiche. Questi fondi permettono ricostruzioni ad alta risoluzione per periodi specifici, non una mappa continua anno per anno.
2. Archeologia: la carta archeologica comunale riunisce circa 2.000 operazioni; il portale del Ministero della Cultura documenta strutture gallo-romane e ricostruzioni di edifici scomparsi. La scoperta del 2026 presso Hôtel-Dieu è preliminarmente interpretata come possibile fortificazione gallica: la fonte ufficiale avverte che funzione e cronologia devono essere verificate.
3. Edifici moderni: BDNB e derivati forniscono footprint, altezze e anno di costruzione per molti edifici contemporanei. Le date sono ignote per parte dei fabbricati e gli anni più antichi possono essere arrotondati. La visualizzazione secondaria consultata indica 202.054 edifici superstiti datati su 229.034 footprint e 26.980 senza data; la copertura degli edifici demoliti è esplicitamente parziale.
4. Alberi e verde: il dataset municipale degli alberi copre solo parte degli alberi pubblici, escludendo proprietà private, boschi e altri insiemi; non è in tempo reale. Il dataset degli spazi verdi contiene categorie eterogenee, non tutte equivalenti a parchi storici.
5. Fiumi e topografia: il tracciato moderno della Senna non va proiettato senza modifiche su tutte le epoche. Fonti archeologiche descrivono paleoalvei, bracci secondari e pianure alluvionali; la Bièvre è stata progressivamente canalizzata e coperta.
6. Ponti: la fonte municipale conta 37 ponti sulla Senna urbana (circa 13 km); le date di attraversamento antico vanno distinte dalle strutture attuali, spesso ricostruite più volte.

## Protocollo di confidenza
- ALTA: data o fatto riportati da fonte istituzionale/archivistica e ben delimitati.
- MEDIA: ricostruzione plausibile ma incompleta, o struttura con cronologia stratificata.
- BASSA: tradizione, attribuzione preliminare o informazione che richiede riscontro archeologico/cartografico.

## Limiti espliciti
- Il registro elementi è un inventario ragionato di elementi storici ad alta rilevanza, non un elenco di ogni edificio di ogni secolo.
- Il dataset attuale degli alberi non ricostruisce gli alberi storici individuali: per quelli servono piani di piantumazione, foto aeree, mappe e archivi di parchi.
- Le geometrie storiche di edifici demoliti devono essere digitalizzate da piante e mappe georeferenziate; il solo anno di costruzione dei fabbricati superstiti non fornisce il volume dei predecessori.
- Per una ricostruzione tridimensionale accurata, le fonti raster/scan devono essere georeferenziate e le geometrie interpretate con livelli di confidenza; non va inventata una geometria dove la fonte non la mostra.

## Fonti principali
Consultare `FONTI.csv`. Le fonti principali sono Archives de Paris, Ministère de la Culture, Ville de Paris, Paris Data, BnF, UNESCO e dataset BDNB.

## Inventario dei layer geografici
Il file `REGISTRO_LAYER_GEOGRAFICI.csv` dettaglia 20 famiglie di layer: edifici contemporanei, catasti pre-1860, comuni annesse, permessi edilizi, archeologia, edifici antichi scomparsi, Senna/paleoalvei, Bièvre, canali, ponti, mura, modelli altimetrici IGN, alberi individuali, verde, statue/fontane, metropolitana/ferrovie e demolizioni.

## Topografia: distinzione obbligatoria
IGN mette a disposizione MNT LiDAR HD (terreno), MNS LiDAR HD (superficie con edifici e vegetazione), BD ALTI e curve di livello. Per un modello storico, il MNT contemporaneo non è una ricostruzione del suolo antico: cave, terrapieni, rive, riempimenti, trincee ferroviarie e opere stradali hanno modificato il rilievo. Le ricostruzioni storiche vanno perciò tenute in un layer separato con fonte e confidenza.
