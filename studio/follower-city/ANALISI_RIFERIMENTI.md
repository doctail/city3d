# Analisi dei 4 reel di riferimento (@popcornbillionproject, Day 1-4)

Etichette: [Certain] misurato con ffmpeg/numpy sui file; [Likely] deduzione. Tutti 720x1280, 30 fps, AAC 44,1 kHz.
Tempi di testo letti a 1 fotogramma/s (precisione ±0,5 s); tempi audio misurati a 10 ms.

## 1. Misure audio [Certain]
| Video | Durata | LUFS integrato | True peak | LRA |
|---|---|---|---|---|
| Day 1 | 10,9 s | -17,2 | +1,4 dBTP | 6,9 LU |
| Day 2 | 22,0 s | -15,4 | +0,7 dBTP | 17,7 LU |
| Day 3 | 32,1 s | -14,7 | +0,4 dBTP | 21,7 LU |
| Day 4 | 46,8 s | -14,3 | -1,3 dBTP | 19,9 LU |

Target nostro: -14 LUFS, true peak <= -1 dBTP (i riferimenti sforano: non copiare).

**Struttura sonora (uguale in tutti e 4):**
- **Il letto musicale quasi non c'è.** Su Day 4 (35-46 s) resta solo un pad tonale a circa -42 dB RMS, ~28 dB sotto i picchi degli effetti. Picchi spettrali a 164/248/328/369/415 Hz = E3, B3, E4, F#4, G#4: Mi maggiore add9, pad morbido, nessuna batteria. Nessun BPM misurabile del letto (l'autocorrelazione dà lo stesso valore su tutti i file, artefatto); la pulsazione la dà il pop (vedi sotto).
- **Il silenzio è punteggiatura.** Digitale zero per 0-0,22 s, 0,45-0,78 s, 2,2-3,1 s, 3,7-4,0 s (identici nei 4 video: stessa traccia di apertura); poi 17,7-19,7 s (Day 2, prima dell'etichetta finale), 21,4-24,0 e 26,2-29,8 s (Day 3, commento e sondaggio), 30,2-33,2 s (Day 4). Quando compare un cartello il suono cala a zero o al solo pad.
- **Hook sonoro a 0,22 s:** click secco ~3,9 kHz, picco -7/-17 dBFS.
- **Pop a 1,42 e 1,72 s:** due colpi a 0,29 s; corpo grave 54-130 Hz + crepitio 4 kHz, picchi -1/-9 dBFS (coincide col lampo visivo).
- **Stacco sulla scheda profilo a 3,3 s:** colpo grave 43-54 Hz (-4/-17 dBFS); ticks del contatore ~1 kHz (991 Hz = Si5) a 4,3-5,7 s (-7/-23 dBFS); chime finale su 1319 Hz (Mi6) e 1976 Hz (Si6), stessa tonalità del pad.
- **Crescita:** pulsazione di pop a 4/s (0,245-0,25 s: Day 2 10-14,3 s, Day 4 15,5-22,7 s), ognuno -1/-6 dBFS, dominante 65-170 Hz. RMS -12/-16 dB contro -25/-28 dB nei tratti vuoti. Questa è la vera ritmica (240 eventi/min), non una cassa.
- **Commento (Day 3 a 21 s, Day 4 a 34,5 s):** scintillio acuto (centroide ~3,4 kHz), poi quasi silenzio.
- **Coda "See you tomorrow!":** solo pad a -36/-43 dB RMS.

## 2. Scene e testi [Certain/Likely]
Testi bianchi con ombra, font geometrico bold, centrati a ~29% dell'altezza (zona sicura alta). Fondo scena monocromo.

| Day 1 (11 s) | Day 2 (22 s) | Day 3 (32 s) | Day 4 (47 s) | Cosa |
|---|---|---|---|---|
| 0-3,5 | 0-3,3 | 0-3,3 | 0-3,3 | HOOK "1 follower = 1 popcorn"; pop a 1,4 s |
| 3,5-6,6 | 3,3-7,0 | 3,3-7,0 | 3,3-7,1 | SCHEDA PROFILO bianca (mock Instagram), zoom sul numero follower, "+N" blu, "= N popcorns" in accento, "Day n" |
| 6,6-8,5 | 7-17 | 7-19 | 7-24 | SCENA: l'oggetto cresce |
| - | - | 19,5-21 | 24,7-30 | stacco macro + scintillio |
| - | - | 21-25 | 34,5-39,5 | COMMENTO in evidenza (Day 4: 3 commenti impilati, titolo "Custom popcorn requests") |
| - | 18-20 | 24-26 | 33-35 | ETICHETTA "N popcorns / DAY n" |
| - | - | 26-30 | - | sondaggio "You chose: fish bowl" |
| - | - | 28-30 | 42-44 | CTA ("Follow to become a popcorn in the comments" / "Drop your ideas in the comments") |
| 8,5-10,9 | 20-22 | 30-32 | 44-46,8 | "See you tomorrow!" fisso (ultimi ~2,5 s) |

Regole ricorrenti:
1. Hook entro 0,2 s (testo + tick), azione (pop) entro 1,5 s. Niente titolo/logo.
2. Scheda profilo SEMPRE a 3,3-7,0 s, taglio netto con colpo grave; il contatore sale sul numero reale del giorno.
3. Contatore identico ogni giorno; cambiano numero, "+N" e "Day n".
4. Richiesta di commento al 65-75% del video, dopo la scena, con scintillio.
5. CTA e "See you tomorrow!" negli ultimi 3-7 s; ultimo cartello fermo >= 2,5 s.
6. La durata cresce con la scena (11, 22, 32, 47 s); la struttura resta.

## 3. Scaletta riusabile (relativa, reel 25-30 s)
| t (s) | Elemento | Audio |
|---|---|---|
| 0,0-0,2 | scena vuota | silenzio digitale |
| 0,2 | testo hook "1 follower = 1 building" | tick 4 kHz, -10 dBFS |
| 1,4 / 1,7 | la costruzione compare (pop-up) | thud 60-120 Hz + crepitio, -6 dBFS; secondo colpo -12 |
| 3,3 | stacco su scheda profilo | colpo sub 45-55 Hz, -8 dBFS |
| 4,3-5,8 | contatore sale, "+N" blu | ticks ~1 kHz, -14 dBFS, uno per incremento |
| 5,8 | fine conteggio, "= N buildings" in accento | chime Mi6+Si6, -10 dBFS |
| 7,0 | ritorno alla scena | pad sale |
| 7-18 | scena / crescita | pop 4/s se più edifici, -6 dBFS |
| ~18-19 | sparkle, richiesta realizzata | shimmer 3-5 kHz, -16 dBFS |
| 19-23 | commento in evidenza | sparkle all'ingresso, poi quasi silenzio |
| ~23-25 | etichetta "N buildings / DAY n" | solo pad |
| 25-27 | CTA "Follow to become a building" | pad |
| 27-30 | "See you tomorrow!" fisso | pad, fade out |

## 4. Specifiche audio da replicare
- Mix -14 LUFS integrati, true peak <= -1 dBTP. Dinamica ampia (LRA 8-15 LU) voluta.
- Pad: Mi maggiore add9 (E3-B3-E4-F#4-G#4), lento, -38/-42 dB RMS sotto gli effetti, niente batteria. Pluck leggera = aggiunta nostra, non nei riferimenti.
- Effetti: pop/thud 60-130 Hz con transiente 4 kHz (picchi -6/-1 dBFS); tick contatore ~1 kHz < 30 ms; chime Mi6/Si6 con coda 0,8-1,2 s; sparkle 3-5 kHz; colpo sub 45-55 Hz sul cambio scena.
- Silenzi digitali 0,2-0,8 s prima di ogni nuovo cartello.
