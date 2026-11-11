# Valencia — chiusura del controllo storico (11 nov 2026)

Aggiorna `SCHEDA_VALIDAZIONE.md` (29 ott). Ricerche grezze: `RICERCA_2026-11-11_A_date.md`, `RICERCA_2026-11-11_B_sventramenti_eventi.md`.
**Limite**: la rete della sessione blocca valencia.es, uv.es ed es/en.wikipedia.org. Le conferme vengono da estratti di ricerca, non dalle pagine lette. Per questo nessuna data nuova è segnata [Certain] se non era già nella scheda.

## 1. Correzioni alla scheda (da applicare a dati e regia)
| ID | Prima | Ora | Tag | Effetto nel modello |
|---|---|---|---|---|
| F001 | piena "novembre o ottobre" 1957 | **13–14 ottobre 1957** (≥81 morti; anche il ponte del 1909 crolla) | [Likely] | anno-evento 1957.78 |
| A001 | Plan Sur 1964–1969 | Piano approvato 22 lug 1958; legge 21 dic 1961; lavori dal 1964; **deviazione inaugurata il 22 dic 1969**; opere complementari fino al 1972–73 | [Likely] | `landphases.json`: il nuovo alveo resta campo fino al 1964, cantiere (terra nuda) 1964–1969.97, acqua da 1969.97. **Oggi i dati dicono 1973: sbagliato.** |
| A002 | giardino dal 1980, primo tratto 1986/87 | incarico a Bofill 1981, progetto 1982, lavori dei primi tratti dal 1984 circa, **primi tratti aperti nel 1986** (1987 = una sola fonte) | [Likely] | vecchio alveo: acqua fino al 1969.97 → letto asciutto → parco **a tratti** dal 1986 al 2000 circa (oggi è tutto il parco in blocco nel 1986: accettabile come ripiego) |
| C006 | Plaza del Ayuntamiento 1927–33 | progetto 1927, **lavori 1931–33**; la piazza di Goerlich è demolita nel 1961, forma attuale dopo | [Likely] | due fasi della piazza |
| E009 | Mercado Central 1910–28 | concorso 1910, progetto 1914, **prima pietra 30 dic 1915**, inaugurazione 23 gen 1928 | [Likely] | GRADUALE 1915–1928 |
| G014 | assente | ponte dell'Esposizione **22 mag 1909** (crolla nella piena del 1957); ponte di Calatrava "La Peineta" **1991–1995** | [Likely] | due ponti; nel 1957 il ponte 1909 sparisce |
| G002 | ponte di pietra di Serranos 1349 | nessuna data di fine trovata: **non modellare il 1349**, il ponte di pietra compare con la ricostruzione del 1518 (G003) | [Likely] | — |
| E002, E006, E007, E012 | conflitti | confermati: Miguelete 1381–1429 (1425 = fase), Torres de Quart 1441–1460, Lonja 1483 (pietra ufficiale; 1482 progetto), Museu de les Ciències 2000 | [Likely] | invariati |

## 2. Nuovi elementi datati (per i monumenti)
- Plaza de Toros 1850–1859 · Mestalla 20 mag 1923 · Casa Consistorial: prima pietra 30 giu 1906, assetto attuale 1965–67 [Guessing] · Ciudadela: demolita entro il 1901 (torrione), bastione sul fiume fino al 1958 · Esposizione Regionale 22 mag–22 dic 1909 (16 ha presso l'Alameda).
- Conquista: assedio dal 22 apr 1238, **entrata di Giacomo I il 9 ott 1238** [Certain]; il giorno della capitolazione (22, 28 o 29 set) è conteso: in video si scrive solo "1238".
- Assedio francese: Suchet, 26 dic 1811 – capitolazione 9 gen 1812 [Certain sulle date]. **Danni per quartiere: non trovati.**
- Bombardamenti della Guerra civile: dal febbraio 1937 [Likely]; zone colpite: non trovate.

## 3. Strade e piazze aperte demolendo case (regola r/Madrid)
Predecessori obbligatori fino all'anno di apertura (oggi `hist.json` ha 504 predecessori ma **nessuno è legato a queste strade**):
| Strada / piazza | Case presenti fino al | Tag |
|---|---|---|
| Plaza Redonda | 1840 | [Certain] |
| Calle de la Paz | 1872 (scomparsa a tratti fino al 1902) | [Likely] |
| Plaza del Ayuntamiento: convento di San Francisco | 1891; Barrio de Pescadores 1907; isolati nord-est 1929–31 | [Likely] |
| Avenida del Oeste (Barón de Cárcer) | anni '40 (demolizioni dopo il 1939) — **anno per tratto da trovare** | [Guessing] sull'anno |
| Plaza de la Reina | ultimo isolato demolito nel **1962** | [Likely] |
| Calle de las Barcas, Poeta Querol, Av. María Cristina, Plaza de la Virgen, San Vicente | non trovati | da verificare |
Ripiego se le date mancano: Av. del Oeste 1945, Poeta Querol e María Cristina 1930. Va scritto nel commento del codice come stima.

## 4. Scala della città (regola "nel 1480 non era quattro case")
- ~1500: **40–50.000 abitanti** dentro le mura (Ardit Lucas) [Likely]; ~1609: 52–64.000 [Likely]. Valencia era una delle città più grandi della penisola.
- **[Certain] dai dati: il modello oggi non regge.** Il catasto ha solo **254 edifici prima del 1850** contro 36.659 dopo; i predecessori sono 504. Una città da 45.000 abitanti mostrata con circa 750 edifici è l'errore di Madrid, moltiplicato.
- Correzione obbligatoria in `hist_valencia.py` (modello Siviglia, `pred_year`): ogni edificio del catasto dentro la cinta islamica nasce come predecessore dal 1238; dentro la cinta del 1356 dal 1356–1400; nei sobborghi fuori le mura (Quart, Morvedre, Russafa, Boatella) dal 1300 al 1600 a gradini. Il predecessore si sostituisce con l'edificio attuale all'anno del catasto.
- Annessioni (servono come fronti di urbanizzazione, non come eventi): Russafa 1877; Poblados Marítimos (Cabanyal, Grau) e Campanar 1897; Benimaclet 1891 [Likely].

## 5. Cosa NON si mostra (niente fatti inventati)
- Piene del 1321, 1517, 1589, 1776: date e danni non verificati → **nessun evento**. I ponti compaiono solo alle date verificate.
- Assedio del 1812: nessun edificio distrutto; si mostra solo fumo sul fronte delle mura, con didascalia datata.
- Bombardamenti 1937–39: niente fumo localizzato senza una fonte sulle zone colpite; al massimo una didascalia.
- DANA del 29 ott 2024 (237 morti): **niente acqua e niente sosta nel video**. Il ruolo del Plan Sur è dibattuto, quindi nessuna frase del tipo "il Plan Sur ha salvato la città". Se serve, una riga sobria in descrizione.
- Età romana: esclusa (inizio 1238, come da scheda).

## 6. Ancora aperti (non bloccano la regia, bloccano l'anteprima)
1. Anni per tratto di Avenida del Oeste e Plaza de la Reina (PDF Sánchez Muñoz, *Ars Longa* 22, uv.es).
2. Calle de Colón, Gran Vía Marqués del Turia / Germanías, Gran Vía Fernando el Católico: anni di apertura (oggi strade con l'anno dell'isolato: accettabile, non sono sventramenti).
3. Umbracle 2000/2001, Oceanogràfic 2002/2003: differenza di un anno, per il render è indifferente.
Per chiuderli serve la lettura diretta di valencia.es, uv.es e wikipedia (rete della sessione).
