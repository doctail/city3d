# Titoli e packaging: cosa dicono i dati (14/11/2026)
Fonte: `concorrenti_titoli.csv` (41 video), FORMULA.md, PRODUZIONE_TIMELAPSE.md. Nessuna chiamata vidIQ. Grafico: `titoli_chart.png`.
Tag: [Certain] = lo dicono i numeri · [Likely] = coerente con i dati ma non provato · [Guessing] = ipotesi.

## 1. Cosa dicono i titoli dei concorrenti

Base: 41 video; 5 sono Short (<3 min) e li escludo. Restano **36 lunghi**, di cui **32 su canali sotto i 10K iscritti** (il nostro vero confronto). Attenzione: 20 canali diversi, molti con 1-6 video: il campione effettivo è circa 20 "casi", non 36.

| Gruppo (video lunghi) | n | Mediana views | Min–max |
|---|---|---|---|
| Tutti | 36 | 7.562 | 9 – 1.488.197 |
| Canali <10K iscritti | 32 | 5.025 | 9 – 1.263.729 |
| Canali <1K iscritti | 15 | 59 | 9 – 131.310 |
| Canali >=10K iscritti | 4 | 596.862 | 4.338 – 1.488.197 |

Sotto i 1.000 iscritti la mediana è ~60 views: solo 3 video su 15 superano 2.500. Mattia (131K) è l'eccezione, non la regola.

**Formato (solo canali <10K, mediana views)**

| Formato | n (canali) | Mediana | Nota |
|---|---|---|---|
| "N years in M minutes" / "on one map" | 16 (7) | 13.053 | include Mattia 131K, Urbavision 4 video 52–293K, ma anche Stratapolis (6 video, 580–13.7K) e Cities Through Time (59) |
| "Watch X grow" / "was built" | 2 (2) | 631.870 | CityEons Roma 1,26M e Forma Urbis 12: n=2, inutile |
| "CITY - 3D Timelapse" (+anni) | 7 (6) | 2.484 | How Cities Grew 1,12M, nobodycares 216K, ma anche 29 views |
| "EVOLUTION OF X \| ..." | 4 (4) | 269 | tutti canali di 0–1.230 iscritti; max 562 |
| altro | 3 (2) | 24 | |

- [Certain] Nel campione "N years in M minutes" ha la mediana più alta tra i formati con n decente, "EVOLUTION OF" la più bassa.
- [Guessing] che questo sia un effetto del formato: i 4 "EVOLUTION" sono i canali più piccoli e nuovi del campione (0–1.230 iscritti), e 2 su 4 sono su Valencia, tema già saturo. Formato, dimensione del canale e tema sono inseparabili con n=4.
- [Certain, e contraddice la lettura "il formato vince"] **Il test naturale migliore del campione**: lo stesso titolo identico "Valencia: 2,000 Years in 12 Minutes | 3D Timelapse (138 BC–2025/2026)" fa **131.310 views** (Mattia, 331 iscritti) e **59 views** (Cities Through Time, 339 iscritti, 3 giorni dopo, stessa dimensione di canale). Il titolo da solo non spiega un fattore ~2.200. Spiegano di più il video, la copertina, il push iniziale, il tempismo.
- Dall'altra parte del nostro stesso storico [Certain]: titolo "EVOLUTION OF ..." identico per NYC (843 views), Madrid (5.771), Rotterdam (9.765), Copenhagen (33.104); stile "Years in Minutes" per Seville (135), Paris (5.152), Rome (117). Ogni formato ha un risultato basso e uno alto. Il formato non ordina i nostri risultati.

**Lunghezza del titolo (caratteri)**
- Mediana 61, **31 su 41 titoli sono oltre 45 caratteri** (sul telefono vengono tagliati). Nessuno dei concorrenti lo evita in modo sistematico.
- Mediana views per fascia, canali <10K: <=40 (n=2): 115K · 41–55 (n=7): 2.0K · 56–70 (n=17): 6.6K · >70 (n=6): 4.4K. Spearman titolo-views nei piccoli: rho -0,10 (n=32, nessun segnale).
- [Certain] Tra tutti i lunghi (36) i 6 titoli <=40 caratteri hanno mediana 277K, ma 3 sono Latos Charts (118K iscritti) e sono i dati più confusi. Tra i piccoli, i 2 titoli corti sono nobodycares (Madrid 216K) e Timeline Cities (Venice 14,5K): n=2, nessuna conclusione.
- [Likely] Un titolo corto non fa male e il troncamento sul telefono è un rischio reale, ma il campione non prova che accorciare faccia crescere.

**Altre caratteristiche (canali <10K)**

| Caratteristica | Con (n, mediana) | Senza (n, mediana) | Lettura |
|---|---|---|---|
| Intervallo di anni nel titolo | 28, 2.950 | 4, 205.216 | n=4 senza, sono CityEons, How Cities Grew... non conta |
| "No AI" nel titolo | 5, 1.007 | 27, 8.489 | [Certain] tra i piccoli, "No AI" non si associa a più views; 4 canali, tutti piccoli |
| Titolo in spagnolo/turco/portoghese | 4, 28 | 28, 7.562 | n=4, canali da 1–53 iscritti |
| Durata 8–11 min | 9, 199.130 | | <8 min: 12, 5.025 · >=11 min: 11, 562 |

- Durata: i video da 8–11 min hanno la mediana più alta (199K contro 5K e 562). rho durata-views nei piccoli -0,15. [Likely] c'è una fascia 8–11 min favorita, ma il grosso viene dai pochi vincitori; **i nostri 8:31 e 8:32 sono già lì, Seville 5:27 e Rome 4:33 no**. Coerente con quanto già visto in FORMULA.md.
- "No AI": [Likely] è un valore per chi ha già deciso di cliccare (nei commenti di Mattia è lodato ovunque), non un motivo per cliccare. Sta meglio nelle prime righe della descrizione e nella copertina secondaria che nel titolo.

**Fattori di disturbo (con i numeri)**
- Iscritti: rho views-iscritti = **0,84** (n=32 piccoli, n=36 tutti). Il canale spiega molto più di qualsiasi caratteristica del titolo. Ma tra i piccoli ci sono eccezioni enormi: Mattia (331), The City Clock (818), CityEons (8,9K), How Cities Grew (4,6K).
- Età: rho età-views = 0,54 nei piccoli: i video più vecchi hanno più views, normale. Il campione ha età da 4 a 48 giorni: i video usciti da pochi giorni (Mattia 8 giorni, Santiago 2) non sono confrontabili con quelli di un mese.
- Tema: Roma, Parigi, Praga, Lisbona, Costantinopoli attirano da soli. Stesso formato Stratapolis: Roma 12.413 contro Lisbona 580. Stesso canale (Urbavision): Rio 293K contro Recife 69K.
- Valencia è un tema con 5 video nel CSV: 131K, 59, 32, 24, 12. Un solo successo su cinque, con titoli simili e anche con copertine diverse che non possiamo vedere (YouTube bloccato qui).
- [Certain] Quello che i dati NON possono sostenere: che un formato di titolo o la sua lunghezza causi più views. [Likely] che "N years in M minutes" sia un buon default sicuro (nessun risultato disastroso a parità di canale), ma non migliore.
- Cosa possono sostenere: i vincitori piccoli hanno quasi sempre **il nome della città all'inizio**, un **intervallo di anni**, e una **promessa di durata**; non c'è un formato unico; il titolo è circa uguale per vincitori e perdenti, quindi **il vantaggio sta altrove** (copertina, contenuto dei primi 30 s, spinta esterna, tema).

## 2. I nostri titoli

| Titolo | Caratteri | Visibile sul telefono (~42) |
|---|---|---|
| EVOLUTION OF VALENCIA \| 3D City Timelapse (1238–NOW) \| No AI | 60 | "EVOLUTION OF VALENCIA \| 3D City Timelapse (" — **gli anni e "No AI" si perdono** |
| EVOLUTION OF COPENHAGEN \| 3D City Timelapse (1167–NOW) \| No AI | 62 | "EVOLUTION OF COPENHAGEN \| 3D City Timela" — anche qui anni persi (ha vinto lo stesso) |
| SEVILLE, Spain - 778 Years in 5 Minutes | 39 | intero, ma "5 Minutes" è la dichiarazione di un video corto |

[Certain] sui conteggi; il troncamento esatto dipende dal dispositivo e dalla larghezza dei caratteri maiuscoli (le maiuscole larghe ne fanno stare meno, forse ~35–40).
- **Valencia**: "EVOLUTION OF VALENCIA" occupa 21 caratteri ed è l'informazione più importante, bene. Ma la parte distintiva (1238–NOW, No AI) cade dopo il taglio, e quello che resta ("| 3D City Timelapse") è il testo identico a Cornerstone (2,2M), Epoch e a decine di titoli: **non differenzia**. In MAIUSCOLO vicino a "VALENCIA: 2,000 YEARS..." di Mattia si legge come una copia di un formato generico. [Likely]
- **Ripetizione con la copertina**: la copertina di Valencia mostra già "1238 → NOW" e "VALENCIA" in grande; il titolo ripete esattamente città e anni. [Certain] che si ripetono; [Likely] che sia uno spreco: il titolo dovrebbe aggiungere quello che la copertina non dice (la promessa o la curiosità), non la stessa informazione. Mattia fa così: la copertina ha anni + città + una chip curiosa ("WHY A BAT?", "10x BIGGER"), il titolo aggiunge "2,000 Years in 12 Minutes".
- **Seville/Paris/Rome**: titolo corto e leggibile, ma "5 Minutes" sul 5:27 è un'ammissione di poco contenuto, mentre i concorrenti di successo promettono 8–12 minuti. Per Valencia (8:31) la promessa "8 Minutes" è coerente.
- **Sulla spiegazione del problema (onestà)**: 823 impressioni e CTR 1,3% = ~11 click. Intervallo di Poisson al 95% per 11 click: circa 5,5–19,7 click, cioè **CTR tra ~0,7% e ~2,4%**. Il dato non distingue un titolo "cattivo" da uno "medio". Le impressioni sono il vero blocco (un salto di ~600 in 16 ore, poi nulla). [Certain] sul calcolo.

## 3. Proposte

### (a) 5 formule per la serie
| # | Formula | Perché | Rischio |
|---|---|---|---|
| 1 | `<City>: <N> Years in <M> Minutes \| 3D Timelapse (<anno>–NOW)` | stesso schema dei vincitori piccoli (Mattia, Urbavision, TimeLoop): nome all'inizio, promessa di tempo; nessun disastro tra i piccoli | quasi identico a Mattia/Cities Through Time (confusione, non differenzia); "N Years" va calcolato sul nostro intervallo vero |
| 2 | `<City>: Every Building Appears the Year It Was Built` | è la promessa vera e unica del nostro video (catasto), diversa da quella degli altri; coerente con l'idea "ogni edificio nel suo anno" di vidIQ del 16 ott (punteggio 97) | lungo (51+); non provato; vero solo dopo il 1840 circa: non va promesso per l'epoca prima |
| 3 | `<City> 3D Timelapse (<anno>–NOW) \| No AI` corto, <=42 caratteri | tutto visibile sul telefono; nome + anni + marchio nei primi 42; Latos, nobodycares, Timeline Cities sono corti | meno promessa, più generico; copertina deve fare più lavoro |
| 4 | `I Rebuilt <City> in 3D: Every Building, Year by Year` | prima persona, curiosità; in linea con la voce "ogni commento riceve risposta" del canale vincitore | tono che il canale muto non ha; "Rebuilt" non è del tutto vero (dati reali + ricostruzione approssimata prima del 1840) |
| 5 | `<City>'s Last 800 Years in 3D \| <fatto locale curioso>` | un gancio specifico (il lago 10x più grande, il pipistrello) come in Mattia Shorts | richiede un fatto vero per ogni città; più lavoro editoriale; rischio clickbait |

Consiglio: usare 1 e 2 alternate per due città, con la **stessa copertina logica**, e guardare i risultati solo come indizio (vedi (d)).

### (b) Valencia: 4 alternative
| Titolo | Car. |
|---|---|
| Valencia: Every Building Appears the Year It Was Built (1238–NOW) | 65 |
| Valencia 1238–NOW: Every Real Building, No AI | 45 |
| Valencia, Spain: Nearly 800 Years in 8 Minutes \| 3D Timelapse | 63 |
| Valencia - 3D Timelapse (1238–NOW) \| No AI | 42 |

Controllare prima che l'intervallo e la durata corrispondano al video (8:31, dati dal 1238). Il terzo titolo è troppo vicino a Mattia: sceglierlo solo se si vuole entrare nella ricerca "Valencia years in minutes".
**Descrizione, prime 2 righe** (circa 150 caratteri mostrati nella ricerca; vanno scritte con fatti presenti nel video):
> Every building still standing in Valencia appears in the year it was built, from the 1238 conquest to today. No AI: real cadastre data, rendered frame by frame.
> Watch what the city looked like in the year your street appeared. (Roman Turia and Albufera context, sources and 12 chapters below.)
Il "curiosity gap" funziona solo se è vero: ad esempio "find the year your building appears" (vero con i dati del catasto, citato nei commenti di Mattia) e non una promessa generica. Non aggiungere numeri o fatti storici non verificati dal video.
Primo commento fissato: la domanda per la prossima città (Mattia lo fa), non nella descrizione.

### (c) Prossime 3 città (formula 2 e 1; solo fatti noti)
| Città | Titolo | Car. | Fatto usato |
|---|---|---|---|
| Granada | Granada: Every Building, the Year It Was Built | 46 | oppure "Granada 3D Timelapse: Alhambra to Today (No AI)" (47) |
| Córdoba | Córdoba - 3D Timelapse \| Roman Corduba to Today (No AI) | 55 | fondazione romana (Corduba) e Mezquita |
| Zaragoza | Zaragoza, from Roman Caesaraugusta to Today (3D) | 48 | colonia romana Caesaraugusta (Augusto) |

Per Granada l'anno di partenza (es. 1238, fondazione del regno nasride) va usato solo se è il vero inizio dei dati del video. Zaragoza e Granada sono le più richieste nei commenti di Mattia (lista in FORMULA.md); [Likely] il tema viene dalla domanda, non dal titolo.
Regola già nota (CONTESTO/PRODUZIONE): controllare con youtube_search i concorrenti degli ultimi 45 giorni sulla città prima di titolare.

### (d) Quando vale la pena cambiare un titolo su un video live
**Regola:**
1. **Non cambiare con meno di ~2.000 impressioni da home/consigliati/ricerca** (togliendo il picco iniziale di iscritti e il traffico esterno). Con 823 impressioni e 11 click l'intervallo è 0,7–2,4%: nessun cambio si può giudicare.
2. **Cambia una cosa sola per volta** (o il titolo o la copertina), a meno che il video sia davvero fermo: in quel caso, cambiare è un tentativo a basso costo, non un test.
3. Annota prima: data/ora, impressioni, click, CTR, fonte del traffico. Dopo il cambio, aspetta altre ~2.000 impressioni. Differenza "vera" solo se > ~1 punto percentuale (a 2.000 impressioni l'errore standard sul CTR vicino all'1–2% è ~0,25–0,3 punti: servono ~3 errori standard) e se non coincide con un picco esterno (Reddit).
4. **Come non ingannarsi**: il CTR scende da solo nel tempo (si passa dagli iscritti al pubblico freddo); un "prima/dopo" mescola questo effetto con quello del titolo. Il picco 35% iniziale di Valencia sono pochi iscritti. Il traffico Reddit non è CTR da impressioni. Un solo caso (una città) non dimostra niente: le città hanno temi diversi (NYC 843 contro Copenhagen 33K con lo stesso titolo).
5. Per le **copertine** conviene "Test & compare" di YouTube Studio (se disponibile per il canale [Guessing]); per i **titoli** non c'è un test equivalente di cui io sia certo: l'alternativa è alternare le formule sulle prossime 4–6 città e guardare la tendenza, sapendo che la città pesa più del titolo.
6. Cambia subito, senza aspettare, solo se il titolo è sbagliato (errore, anno falso) o la parte vincente è tagliata sul telefono.

**Per Valencia oggi**: [Likely] il titolo non è la causa principale (blocco di impressioni + tema saturo + 5 video concorrenti su Valencia). Se si cambia, farlo con una sola variante (la numero 2 di (b)) e solo dopo aver raccolto ~2.000 impressioni dalle sezioni non esterne; altrimenti conta la copertina.

## Limiti
- 36 video lunghi, ~20 canali, 4 grandi; i sottogruppi hanno n tra 2 e 17; nessun test statistico regge un confronto formato contro formato.
- Mancano nel CSV i video dei vincitori grandi citati (Cornerstone 2,2M, Timelapse Studio): non sono usati nei numeri sopra.
- Copertine dei concorrenti non visibili (YouTube bloccato qui): il confronto titolo-copertina è fatto solo sulle nostre e sulla descrizione di Mattia in CONTESTO.
