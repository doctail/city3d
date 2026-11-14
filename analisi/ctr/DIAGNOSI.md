# DIAGNOSI CTR / reach — Year Built (14/11/2026)
Fonti: CONTESTO.md, REGIA.md, PRODUZIONE_TIMELAPSE.md (Reddit, concorrenza, NYC), FORMULA.md, canale_yearbuilt.md, concorrenti_titoli.csv. Nessuna chiamata vidIQ. Tag: [Certain] dato nei file · [Likely] inferenza forte · [Guessing] ipotesi.

## 0. Verità scomoda
Il CTR non è "il" problema: con 7 video lunghi sullo stesso canale, stesso formato, stessa grafica, le views vanno da 117 a 33.104 (x280). Un CTR cattivo del canale non produce questa dispersione; la produce **la città/la concorrenza/la spinta esterna** [Likely]. Il CTR di Valencia a 16 h è un campione minuscolo e viziato (vedi 1). Un canale nuovo non risolverebbe nulla: porterebbe gli stessi difetti a 0 iscritti.

## 1. Tre problemi separati
| | Cosa dicono i dati | Cosa NON dicono |
|---|---|---|
| (a) Poche impressioni | Valencia: 823 imp in 16 h, piatte 6 h poi un salto di ~600 [Certain]. Madrid: 5 imp in 15 h con Meridian Madrid uscito 3 giorni prima [Certain]; dopo Reddit Home 17 / suggeriti 21 [Certain]. NYC: 4.900 imp in 39 h [Certain]. Valencia pubblicata in una città già "presa" (Mattia Maps 131K il 3 nov + 5 canali in 3 settimane; esclusa da noi l'11 nov, pubblicata il 13) [Certain]. | Non sappiamo le impressioni di Copenhagen, Rotterdam, Paris, Rome, Seville. Non sappiamo se il salto di 600 è un test di YouTube o una spinta esterna. |
| (b) CTR sulle impressioni date | NYC 2,4-2,7% su 4.900 imp [Certain] = nella fascia normale per canali piccoli (tipico 2-10%, non misurato qui) [Guessing]. Valencia 1,3% su 823 [Certain], ma vedi sotto. | Nessun CTR per Copenhagen (il vincitore). Nessun CTR per Seville/Rome/Paris. Senza il CTR del vincitore non si può dire che il CTR sia "la causa". |
| (c) Retention dopo il click | NYC: durata media 20,9%, 37% a 0:30, poi curva piatta 20-25% [Certain]; Madrid 30% [Certain]. Il crollo è nei primi 30 s, il resto tiene. | Retention di Valencia/Copenhagen non nei file. Il 21% è su un pubblico misto (TV 25%, Home 67%), non confrontabile con un benchmark. |

**Affidabilità di 823 impressioni.** CTR 1,3% = circa 11 click (10-11). Intervallo di Wilson 95% (binomiale) ≈ **0,7% – 2,4%**. Per confronto NYC (4.900 imp, 2,4%): intervallo ≈ 2,0 – 2,9%.
- Implicazione 1: Valencia è *forse* sotto NYC (i due intervalli si toccano a ~2,4%), ma non è provato [Likely].
- Implicazione 2: il vero valore può essere 2%+, cioè normale. Non si può concludere "titolo/copertina sbagliati" da 11 click [Certain].
- Implicazione 3 (peggio): l'intervallo binomiale assume impressioni omogenee; qui sono 2 popolazioni (picco ~35% iniziale = pochi iscritti/fedeli; poi un blocco di ~600 imp in un salto, probabilmente un'unica superficie, es. un test Home/suggeriti) [Likely]. Il CTR "vero" è quello del blocco da 600, che è quasi tutto lo 0-1%: dice che quel blocco non ha convertito, non che la copertina è peggiore delle altre.
- ~90 delle 103 views non vengono da impression-click (Reddit/esterno) [Likely]: il video "vive" di traffico esterno, non di browse.
- Valutare il CTR solo a ≥ 3.000 impressioni (CI ±~0,4 punti a CTR 2%) e meglio ≥ 5.000.

**Tabella 7 video (dati CONTESTO, views all'11/11)**
| Video | Title style | Views | Nota concorrenza/spinta |
|---|---|---|---|
| NYC | EVOLUTION | 843 | nicchia vs Cornerstone 2,2M |
| Madrid | EVOLUTION | 5.771 | r/Madrid; Meridian 15K 3 gg prima |
| Rotterdam | EVOLUTION | 9.765 | 3° arrivato; TimeLoop 121K |
| Copenhagen | EVOLUTION | 33.104 | città libera in 3D [Certain, REGIA]; 8:32, modello completo |
| Seville | "SEVILLE, Spain - 778 Years..." | 135 | uscito senza strade; Avenues of Time il 29/10, TimeLoop |
| Paris | stile Seville | 5.152 | città enorme, stile "non EVOLUTION" |
| Rome | stile Seville (poi EVOLUTION 11/11) | 117 | CityEons 1,26M, Timelapse Studio 2,9M: la più satura |
Lettura: [Certain] lo stile del titolo NON separa i vincitori dai perdenti (Paris stile Seville = 5.152; NYC EVOLUTION = 843). [Likely] separano: saturazione della città, spinta esterna (Reddit), qualità del video (Copenhagen primo con modello completo, 8:32). Sono confusi insieme: 7 punti, tre variabili, nessun controllo.

## 2. Ipotesi sul reach basso, in ordine di evidenza
| # | Ipotesi | Evidenza a favore | Test più economico | Conferma / rifiuto |
|---|---|---|---|---|
| 1 | **Città satura / spazio già preso** (concorrenza nello stesso intervallo) | Madrid 5 imp (Meridian); Valencia (Mattia 131K, +5 canali); Rome 117; Seville 135; Copenhagen libera = 33K [Certain su fatti, Likely su causa] | Scegliere la prossima città con youtube_search 45 gg PRIMA del lavoro (decisione di Fabio 11/11) e confrontare impressioni a 24 h con la saturazione (n. video >5K) | Conferma: città libera → ≥3.000 imp a 48 h; satura → <1.500. Rifiuto: città libera con <1.000 imp a 48 h |
| 2 | **Spinta esterna del primo ora insufficiente** (nuovo account; Reddit non converte in browse) | Madrid: Reddit → primi suggeriti [Certain]; Valencia 90/103 esterne e poi imp piatte [Likely]; Reddit r/spain ha rimosso l'account | Per ogni video: registrare Esterna/Home/Suggeriti a 2 h e 24 h; alternare con/senza post Reddit su 2 città simili non è fattibile, quindi misurare solo il rapporto Esterna→Suggeriti | Conferma: dopo il picco esterno le imp restano piatte. Rifiuto: le imp salgono nelle 24 h dopo il picco |
| 3 | **Copertina: troppo "grafica", poco curiosità** (nome+anni ok, ma niente soggetto-gancio/sottotitolo-chip) | Mattia: chip anni + nome enorme + chip sottotitolo/domanda ("2,000 YEARS IN 3D", "WHY A BAT?") [Certain]; NYC 2,4% [Certain]; Valencia 1,3% (campione piccolo) | Studio "Test & compare" 3 varianti (vedi §4) | Conferma: una variante >= +30% di quota-guardate su ≥ 5.000 imp totali. Rifiuto: tutte entro ±15% |
| 4 | **Qualità/retention dei primi 30 s → test di distribuzione** | NYC 37% a 0:30 [Certain]; REGIA: "il problema dimostrato è l'inizio" | Confrontare 0:30 e durata media di Valencia (Copenhagen come riferimento) | Conferma: 0:30 <45% e impressioni che si fermano dopo 24-48 h. Rifiuto: >55% e poche imp comunque |
| 5 | **Tema e formato di contenuto** (documentario con cartoline di storia vs "timelapse + etichette") | Mattia 135K con ~70 cards, ma Santiago 738 views in 2 gg: il formato da solo non spiega [Certain] | Aggiungere 1 sola variabile: più contesto-card in una città libera | Conferma: ritenzione >30% e imp ≥ città libera precedente. Rifiuto: nessun cambio |
| 6 | **Pagina del canale debole** (avatar, banner, trailer, nome vs @handle, no playlist, no parole chiave) | canale 94 iscritti; playlist "da creare" in canale_yearbuilt.md [Certain]; impatto sul CTR dei suggeriti: minimo | Fix in 30 min oggi (§4); nessuna misura separata | Effetto probabilmente piccolo; non attribuirgli risultati. Rifiuto implicito se tutto resta uguale |
| 7 | **Mix di audience: Shorts battaglie con voce sintetica** sullo stesso canale | Shorts 1,1K/400/280 che non portano al lungo [Certain]; pubblico Shorts ≠ pubblico lungo [Likely]; Cornerstone zero Shorts [Certain]; effetto sul browse dei lunghi: non misurato [Guessing] | Spostare/unlist gli Shorts battaglia (§4) e vedere se "chi è il pubblico" in Analytics cambia | Conferma: % spettatori che guardano anche i lunghi cresce; rifiuto: nessun cambio dopo 3 video |
| 8 | **Timing di caricamento** | Nessun dato nostro; consiglio "lunedì" di vidIQ è generico [Certain su fonte] | Pubblicare alla stessa ora (es. 16:00 locale del pubblico della città) per tutto l'esperimento: variabile controllata, non testata | Non testare ora: effetto di secondo ordine con 94 iscritti |
| 9 | **Titolo non nella lingua del pubblico/titoli non tradotti** (YouTube ha tradotto Siviglia in italiano nel feed del proprietario) | Fatto aneddotico (1 feed) [Certain]; titoli tradotti già pianificati in traduzioni.md; Valencia: commenti chiedono la lingua locale [Certain] | Aggiungere titoli tradotti (ES/lingua città) per ogni video; misurare la quota di views per lingua | Conferma: ≥15% views da paese/lingua della città. Rifiuto: <5% |
| 10 | **Mancanza di struttura seriale** (playlist, nome serie, stessa grafica/titolo "EVOLUTION OF X") | Il formato è già seriale nei titoli [Certain]; nessuna playlist; con 7 video l'effetto è trascurabile [Likely] | Playlist "Every City" + "Cities of Spain" + schermata finale | Non misurabile ora; fix gratuito |

## 3. Canale nuovo: pro e contro
| | Argomenti |
|---|---|
| A favore | Un canale nuovo ha lo stesso handicap (0 storia) ma senza i "voti negativi" accumulati? **[Guessing]**: YouTube non penalizza un canale per i video passati in modo documentato; un reset non è provato. Il vantaggio sarebbe solo estetico (nome, pulizia Shorts). |
| Contro | (1) Si perdono 94 iscritti + 7 video, di cui uno da 33K che mostra che il canale PUÒ ricevere distribuzione [Certain]. (2) Il cold start è identico: serve una spinta esterna anche a Copenhagen-livello. (3) Copenhagen 33.104 e Rome 117 stesso canale, stesso formato → il canale non è "bruciato" [Likely]. (4) Un nuovo canale riparte da 0 con la stessa pipeline in una nicchia intasata. (5) Si buttano 2-3 settimane per ricostruire. |
| Costi | 94 iscritti, 7 video, Reddit (account u/Mobile-Cream3431 → collegamento al canale), tempo di setup. |

**Raccomandazione [Likely]: NON aprire un nuovo canale ora.** Il segnale decisivo: Copenhagen/Rome/Seville mostrano che il canale non è la variabile. Cambierei idea (cioè nuovo canale / pivot) solo se, dopo l'esperimento di 4 settimane (§4), **tutti e 8 i video lunghi in città "libere" restano sotto 1.000 impressioni a 48 h E il CTR misurato su ≥3.000 imp è ≥3%** → problema di distribuzione del canale, non di CTR. Oppure se 3 città libere di seguito con ≥5 post esterni non superano 300 views a 7 giorni. In quel caso vale più un nuovo canale con un formato diverso (documentario con cards) che lo stesso canale.

## 4. Piano 4 settimane (2 lunghi/settimana = 8 video), una variabile alla volta
Regola base: città scelta con youtube_search 45 giorni PRIMA del lavoro, solo città "libere" (nessun video >5K), stesso orario di upload, stesso giorno-ora di post Reddit; costanti: titolo "EVOLUTION OF <CITY> | 3D City Timelapse (<year>–NOW)", durata ≥8 min, musica Audio Library, stessa descrizione-modello.
| Settimana | Video | Variabile cambiata | Il resto |
|---|---|---|---|
| 1 | A1, A2 | **Copertina**: A/B/C in Studio "Test & compare" su A1 (3 varianti: attuale / chip sottotitolo-domanda stile Mattia / soggetto-gancio vicino). A2: stessa copertina vincente | Titolo uguale |
| 2 | B1, B2 | **Titolo**: B1 "EVOLUTION OF X..." vs B2 stile "I Rebuilt X..."/"Every building in X appears the year it was built" (vidIQ già propone) | Copertina vincente di S1 |
| 3 | C1, C2 | **Apertura (primi 30 s)**: C1 con apertura attuale; C2 con hook "empty plain / first event at ~30 s + card di contesto" (stile Mattia) | Titolo/copertina vincenti |
| 4 | D1, D2 | **Spinta esterna**: D1 post Reddit nella prima ora; D2 senza post (o ritardato di 24 h) | Tutto il resto fisso |
Nota: le città diverse confondono i risultati; per leggerli usare il **rapporto** (impressioni a 48 h, CTR, 30 s) tra i due video della stessa settimana e confrontare con la media precedente, non i valori assoluti [Likely]. Con 2 video per variabile il risultato è indicativo, non statistico [Certain].

**Test copertina.** (1) Se Studio ha "Test & compare": 3 varianti, aspetta che chiuda (di solito 1-2 settimane); ok anche con pochi dati ma leggi la "quota di visualizzazione". (2) Se non c'è: cambia a orari fissi (es. A alle 0-24 h, B alle 24-48 h) e confronta finestre uguali in Analytics → Copertura (impressioni ≥1.000 per finestra); il traffico di Reddit va escluso dal CTR (guardare solo "Home/Suggeriti").
**Misure per ogni video.** | 2 h | 24 h | 48 h | 7 gg |
|---|---|---|---|
| Imp, CTR, views, Esterna/Home/Suggeriti | + 0:30, durata media %, iscritti | + CTR a ≥3.000 imp, prima di decidere | + durata media, ritorni |
**Stop-rules.** Non cambiare nulla prima delle 48 h o di 3.000 imp. Fermare la variabile se: (a) una variante di copertina è chiaramente peggiore (<1% su ≥1.500 imp) → togli; (b) il video supera 5.000 views in 48 h → NON toccare più copertina/titolo; (c) <300 imp a 48 h con spinta esterna fatta → diagnosticare la città (satura?) non la copertina.

**Fix pagina canale — oggi (30 min).** (1) Banner/icon verificati (già pronti); (2) descrizione e parole chiave dal kit; (3) **trailer** per i non iscritti (Copenhagen, 8:32); (4) creare 2 playlist: "Every City, Year by Year" e "Cities of Spain in 3D" (ci sono già ≥2-3 video); (5) schermata finale con "next city" sui lunghi; (6) commento fissato con domanda "Which city next?" (Mattia fa così); (7) titoli e descrizioni tradotti (ES/lingua città) per Valencia, Copenhagen. Nome vs @handle: tenere "Year Built" visibile; nessun cambio nome ora (rischio zero guadagno).

**Policy Shorts battaglia.** Raccomandazione [Likely]: **non cancellare** (hanno 1,1K/400/280 views, nessun danno provato), **unlist** i 2 battaglia (Thermopylae, Constantinople 1453) e metterli in una playlist "Shorts" per ripulire il profilo di pubblico (voce sintetica ≠ canale "No AI", incoerente col brand) [Guessing sull'effetto]; da ora al massimo 1 Short/città, sul momento forte, che rimanda al lungo (REGIA). Se dopo 4 settimane la quota "spettatori che guardano anche lunghi" non cambia, ignorarli. Non spostare su altro canale ora (spostare = perdere views/commenti e creare un altro canale da gestire).

## 5. Priorità (cosa fare davvero)
1. Estrarre da Studio il CTR e le fonti di traffico di Copenhagen e Rotterdam: oggi non abbiamo il CTR del vincitore; senza non si decide su un dato. 
2. Aspettare 48 h / 3.000 imp su Valencia; poi test copertina.
3. Applicare i fix pagina e la policy Shorts oggi.
