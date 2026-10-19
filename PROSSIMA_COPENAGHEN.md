# Copenaghen — piano per la nuova chat (deciso con Fabio il 19 ott 2026)

Leggi PRIMA: `PRODUZIONE_TIMELAPSE.md` (regole di Fabio, flusso, sezioni del 18-19 ott: analisi del concorrente NYC 96K e "LA NICCHIA SI STA INTASANDO"). Questo file dice solo cosa cambia per Copenaghen.

## Perché Copenaghen
- 19 ott 2026, vidIQ youtube_search ultimi 45 giorni: nessun video 3D aereo di crescita su Copenaghen. C'è solo Epoch Timelapse (AI, camera fissa su Amalienborg, 24 set, 6.770 visualizzazioni).
- Città già prese da altri e quindi scartate: Chicago, San Francisco, Boston, Seattle, Lisbona, Stoccolma, Berlino, Barcellona, Amsterdam, Las Vegas.
- **Ricontrollare con youtube_search "Copenhagen 3D timelapse" (ultimi 45 giorni) prima del render e il giorno prima dell'uscita.** Se esce un concorrente forte (>5K), avvisare Fabio subito.

## Decisioni
- Budget pod per questo video: **fino a 4,5 €** (Fabio, 19 ott). Sempre OK esplicito di Fabio prima di aprire un pod.
- Calendario obiettivo: dati e regia 19-21 ott → render 22-23 ott → montaggio → **uscita martedì 27 ott** (Rotterdam esce giovedì 22 ott).
- **2 Shorts** (non 3), come deciso per le città dopo Rotterdam. Usare i risultati del test A/B/C di Rotterdam quando arrivano.
- Primo video con il **modello completo** (vedi sotto). Non è più sufficiente "ogni edificio reale": i dati veri non ci distinguono dai cloni, lo spettacolo sì.

## Il modello completo (cose che vanno nel RENDER)
1. **Apertura a terra / bassa** con oggetti a scala umana (navi nel porto, castello di Absalon), evento spettacolare entro 45 s. Niente campi vuoti visti dall'alto.
2. **Monumenti modellati** (anche semplici: volumi + tetto/guglia riconoscibile) e **camera che va vicino quando salgono**, ogni 15-30 s: Rundetårn, Børsen (guglia a draghi), Rosenborg, Christiansborg, Marmorkirken (cupola), Amalienborg, Vor Frelsers Kirke (guglia a spirale), Rådhus, Tivoli, Den Lille Havfrue, Operaen, Det Kongelige Teater (Skuespilhuset), Øresundsbron, CopenHill/Amager Bakke.
3. **Fuoco**: incendi 1728 e 1795, bombardamento 1807. Fiamme/bagliore nel render (emissione + fumo volumetrico leggero o sprite), edifici che spariscono (`d=<anno>` in build_render) e ricostruzione.
4. **Finale notturno** negli ultimi 30-40 s: cielo scuro, finestre con emissione casuale, Tivoli illuminato. La copertina "2026" va fatta di notte.
5. Camera sempre in movimento, alternando alto/basso/vicino (regola drone di Madrid solo per i tratti larghi).
6. Stima tempi: misurare con `run.sh profile` PRIMA del full; con notte e fuoco +10-20% rispetto a ~1,9 s/fotogramma.

## Al MONTAGGIO (tutto quello già fatto per Rotterdam)
Saturazione x1,7 + contrasto x1,06; schede evento ogni 15-20 s; effetti sonori (fuoco, cannoni 1807, cantiere, campane); gancio scritto nei primi 15 s (es. "IN 1807 THE BRITISH FIRED 14,000 ROCKETS AT THIS CITY" — verificare il numero); etichette dei monumenti agganciate alla posizione 3D; contatore popolazione; scheda sobria per tragedie (1711 peste, 1945 Shellhus).

## Dati (DA VERIFICARE — prima cosa da fare)
- **Anno di costruzione per edificio**: BBR (Bygnings- og Boligregistret), campo `opførelsesår` / `byg026Opførelsesår`, via Datafordeler (datafordeler.dk). Probabilmente serve un utente gratuito (servizi "web user"/token) oppure il download dal pod. In alternativa: open data del Comune di Copenaghen (opendata.dk / kk.dk) se ha un layer edifici con anno.
- **Impronte e altezze**: GeoDanmark (bygninger) via Dataforsyningen (token gratuito) oppure OSM; altezze da DHM (modello di elevazione) o numero di piani BBR (`byg054AntalEtager`).
- Acqua, parchi, porto: OSM (Geofabrik Danimarca + `osm_pbf.py`, come per Rotterdam).
- La rete della sandbox blocca quasi tutto: i download vanno fatti sul pod CPU (con OK di Fabio) come per Rotterdam (`data_nl.sh` come modello → scrivere `data_dk.sh`).
- Strato storico (`hist_copenhagen.py`): la città fino al 1850 era chiusa nei bastioni (Volden, linea dei laghi) → crescita compressa dentro le mura, poi esplosione dei quartieri "brokvartererne" (Nørrebro, Vesterbro, Østerbro) dopo il 1852. Christianshavn dal 1617, Frederiksstaden dal 1749. Edifici distrutti: 1728 (~1.670 case, centro nord-ovest), 1795 (~940, tra Gammeltorv e Slotsholmen), 1807 (~300, zona Vor Frue/università).

## Cronologia (verificare date e numeri prima di metterli a schermo)
- 1167 il vescovo Absalon costruisce il castello su Slotsholmen (fondazione)
- 1254 diritti di città · 1443 capitale
- 1606-1640 Christian IV: Rosenborg, Børsen, Rundetårn (1637-42), Nyboder, Christianshavn (1617)
- 1659 assalto svedese respinto
- 1671-73 scavo di Nyhavn
- 1711 peste (circa un terzo degli abitanti) — sobria
- **20-23 ottobre 1728 grande incendio** (anniversario: 20 ottobre!)
- 1749 Frederiksstaden, Amalienborg (1750-60), Marmorkirken iniziata (finita 1894)
- 1794 brucia Christiansborg · **giugno 1795 secondo grande incendio**
- 1801 battaglia di Copenaghen (Nelson)
- **2-5 settembre 1807 bombardamento inglese**
- 1843 Tivoli · 1847 prima ferrovia · 1852-1870 cadono le mura, nascono i quartieri dei ponti
- 1884 Christiansborg brucia di nuovo · 1905 nuovo Municipio · 1913 la Sirenetta
- 1940 occupazione tedesca · 21 marzo 1945 bombardamento dello Shellhus (bombe anche su una scuola) — sobria
- 1947 Finger Plan · 1971 Christiania · 2000 ponte dell'Øresund · 2002 Metro · 2005 Opera · 2019 CopenHill
- Popolazione (comune, da verificare con Statistics Denmark): ~60-70K inizio '700, ~100K 1800, ~400K 1900, picco ~770K 1950, ~470K 1990, ~670K oggi.

## Titolo e copertina
- Titolo da provare (stile prima persona, mai usato finora): "I Rebuilt 850 Years of Copenhagen in 3D (Every Real Building)" — confrontare con "Evolution of Copenhagen in 3D | 850 Years, Every Real Building (No AI)" con vidiq_score_title.
- Copertina: sinistra a livello del suolo (castello/navi 1167 o città in fiamme 1807), destra Copenaghen di notte 2026 (Nyhavn/Opera illuminati); "1167 → 2026" con 2026 giallo; "COPENHAGEN" enorme; bandiera danese (aggiungere `flag_dk` a thumb_city.py).

## Crediti vidIQ
Al 19 ott restano ~50 crediti, ricarica il 27 ott. La scansione automatica di lunedì 26 ne usa fino a 45: in questa chat usarne il meno possibile (solo i due ricontrolli youtube_search, 5 crediti l'uno).
