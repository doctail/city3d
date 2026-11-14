# Thumbnail Lab — Valencia e serie Year Built (14/11/2026)
Metodo: ho guardato le immagini (nostre + 5 di Mattia dallo screenshot) e i mockup a 168 e 120 px. Nessun dato di CTR per-thumbnail oltre ai numeri del CONTESTO. Tag: [Certain]/[Likely]/[Guessing].
Nota [Likely]: le 5 miniature di Mattia nello screenshot sono verticali (282x422), quindi con ogni probabilità Short (titoli tipo "2,000 years in 25 seconds", "VPH"). Nel mockup le ho ritagliate in 16:9 al centro (nome + chip): perdono i chip degli anni in alto. Il confronto e' di STILE, non di CTR.

## 1. Tabella: cosa dice in 1 secondo, a dimensione telefono
| Miniatura | Soggetto | Contrasto | Parole | Gap di curiosita' | 168x94 | 120x68 |
|---|---|---|---|---|---|---|
| Nostra Valencia 1238→NOW | due immagini quasi identiche (campi verdi + citta' rossa) divise in diagonale | basso: stessi verdi/ocra, differenza solo a destra | 3 + tag (1238, NOW, VALENCIA, YEAR BUILT) | nessuno | nome si', anni piccoli, bandiera = macchia, tag illeggibile | solo "VALENCIA" |
| Nostre Madrid/NYC/Rotterdam/Parigi | split diagonale con foto simili, anni in alto | medio (grattacieli vs case) ma foto scura/rumorosa in basso | 3-4 | nessuno | nome si', resto no | nome |
| Mattia Santiago | split verde/citta', "SANTIAGO" + chip | alto (verde vs rosso) | 4 | lieve ("2,000 YEARS IN 3D") | tutto leggibile | nome + forse chip |
| Mattia Albufera | grande lago turchese su campo | molto alto, UN soggetto | 3 ("10x BIGGER") | si': "10x bigger" di cosa? | leggibile | leggibile |
| Mattia Valencia 1238 | campi + citta' + barca nera | medio | 3 ("WHY A BAT?") | si': domanda | leggibile | leggibile |
| Mattia DANA | spiaggia/ponte, tono sabbia | medio-basso | 5 | emozione, non curiosita' | nome si', chip piccolo | nome |
| Mattia Valencia 2000y | split foresta/citta' | medio | 4 | lieve | leggibile | nome |

Punti deboli NOSTRI [Certain, visti nel mockup]: (1) split di due immagini simili: l'occhio non vede "prima/dopo", vede un campo; (2) anni e freccia piccoli: a 168 px "1238 → NOW" e' rumore; (3) bandiera e tag "YEAR BUILT" sono pixel inutili; (4) la meta' bassa e' foto scura coperta da lettere spaziate con molto contorno nero (peso visivo, poco contrasto col fondo); (5) nessuna domanda ne' promessa: dice solo cosa c'e', non perche' cliccare; (6) tutte le nostre miniature hanno lo STESSO layout: niente identita' ma neanche varieta' da testare.
Cosa fa Mattia: un soggetto, nome enorme su banda scura, un chip con il gancio (domanda o numero), foto piu' luminosa e satura.

## 2. Regole per la serie (8)
1. **Un solo soggetto** riconoscibile a 120 px (un fiume, un lago, una citta' murata). Perche': a telefono si legge una forma, non una scena.
2. **Max 3-4 parole in tutto**, caratteri alti >= 12% dell'altezza. Sotto 168 px il testo piccolo sparisce: meglio una riga sola.
3. **Luminosita' e saturazione alte** (SAT 1.4, contrasto 1.15-1.2): il feed e' scuro, le foto spente affondano. Evitare in basso il nero pesante.
4. **Un contrasto netto tra le due meta'** (blu fiume vs verde parco, citta' vs campo). Se i due frame sono simili, NON fare lo split: meglio un frame solo.
5. **Anni**: un solo anno o un solo numero grande ("1957") oppure un chip semplice; l'intervallo "1238–NOW" e' bene nel titolo, non nella miniatura (e' gia' scritto accanto).
6. **Gancio senza volto**: domanda ("WHY MOVE A RIVER?"), numero ("1957"), contrasto visivo (RIVER → PARK), oppure la sproporzione ("10x BIGGER" alla Mattia). Viene dalla storia della citta' e dal video, non da un volto.
7. **Solo claim che il video sostiene** (Valencia: fiume deviato dal Plan Sur 1961-69, piena 1957, Jardi del Turia 1986; niente numeri di morti in miniatura).
8. **Da evitare**: bandiere, tag di canale, foto scure/rumorose, due immagini uguali, piu' di un colore di accento, lettere spaziate molto larghe che mangiano la foto.
Test della regola 3 e 1: nel mockup le candidate C e D si leggono anche a 120 px; la attuale no.

## 3. Candidate Valencia (1280x720 JPG, tutte < 400 KB) — cartella `analisi/ctr/thumbs/`
Render nuovi (CPU, 2 su 4 consentiti): stessa camera sopra Ciutat Vella (0,-1900,850 → 0,120,0), anno 1957.7 (fiume nel vecchio letto) e 2026 (Jardi verde). Il 1238 e' dal frame esistente (zoom sul centro).
| File | Concetto | Idea |
|---|---|---|
| val_A.jpg | domanda | "WHY MOVE A RIVER?" in giallo su citta' + fiume blu, freccia al fiume, chip VALENCIA |
| val_B.jpg | prima/dopo | split diagonale stessa camera: fiume blu (RIVER) → parco verde (PARK), freccia, nome |
| val_C.jpg | numero | "1957" enorme + "THE FLOOD", sfondo scurito e virato blu |
| val_D.jpg | minimale | un'immagine (citta' murata 1238 arancio su verde, fiume blu) + "VALENCIA" + chip 1238 |
Mockup: `feed_mockup.jpg` (168 px, 5 Mattia + attuale + A-D) e `feed_mockup_120.jpg`. Render sorgente non salvati nel repo (rifacibili con i comandi sopra).
Caveat onesto [Certain]: nella render 1957.7 l'acqua della piena non si vede (nelle NOTE e' "EFFETTO DA PROVARE"): per questo C e' scurita e non mostra acqua, e nessuna miniatura fa vedere l'inondazione.

## 4. Ranking (giudizio da guardare, [Guessing] sull'effetto reale)
1. **A** — unica con un gap di curiosita' + soggetto + testo leggibile a 168 px; replica il meccanismo che Mattia usa con "WHY A BAT?". Rischio: il titolo "EVOLUTION OF VALENCIA" non risponde alla domanda; coerenza titolo/miniatura da sistemare (titolo alternativo possibile: "Why Valencia Moved Its River | 3D Timelapse (1238–NOW) | No AI").
2. **C** — la piu' leggibile in assoluto, emozione forte; ma e' la piu' "cupa" nel feed chiaro e non mostra la citta'.
3. **B** — racconta la storia in un colpo (blu→verde), ma i chip RIVER/PARK sono piccoli a 120 px e la freccia confonde.
4. **D** — pulita ma e' quasi la formula di Mattia senza il suo gancio; ottima come controllo "minimale".
Tutte e quattro battono l'attuale in leggibilita' [Likely]; se battano anche in click, NON si sa.

## 5. Test
Se YouTube Studio offre "Test & compare" per il video Valencia: provare **A, C, B** (3 varianti; D di scorta). Serve un campione: con ~800 impressioni in 16 h il test avra' poco potere; il risultato si legge solo se YouTube distribuisce abbastanza impressioni (decine di migliaia = piu' affidabile) [Likely].
Cosa NON si puo' sapere senza test reale: quale stile fa piu' CTR; se il problema e' la miniatura o il titolo/nicchia/canale nuovo (94 iscritti); se il 1.3% dipende dalle prime ore (picco ~35% poi quasi 0 = pochi iscritti, poi pubblico freddo); se le miniature di Mattia funzionano per lo stile o perche' sono Short. Valore di partenza: 823 impressioni, 1.3%, 103 views (CONTESTO), un solo video.
