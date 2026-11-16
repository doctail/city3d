# Marseille — miniature (packaging check, 16/11/2026) — PROVVISORIO: nessun fotogramma renderizzato

Regole usate (analisi/ctr/MINIATURE.md + owner's review 14/11 + AVVIO "Packaging"): un soggetto; luminosa e satura (SAT 1,4, contrasto 1,2); due metà piene e diverse (se simili, un fotogramma solo); anno = primo anno del video = 600 BC; niente bandiere né tag canale; 3-4 parole; promessa consegnata entro 30-60 s (cold open); mai ciò che arriva al 70%. Concorrenti (dato del proprietario): Timeline Cities, Brick Cities, ChronosPulse 3D: tutti "Marseille 600 BC → 2026", bandiera, nome enorme, nessuno ha il 1943.

## Test a 168 px (cosa ho fatto davvero)
Mockup `cities/marseille/copertina/mockup_168_placeholder.png` (3 layout a 168 px sopra e 120 px sotto, ingrandito 2x per vederlo). **Sfondi = rettangoli colorati finti: serve solo a giudicare il testo, NON la foto.** Layout fatto con `kit.thumb_kit` (stesso font Inter ExtraBold, contorno nero). Esito:
- "MARSEILLE" a 205 px: leggibile a 168 e a 120 [Certain, visto nel mockup].
- Chip "600 BC" e "NOW" a 96 px: leggibili a 168; a 120 piccoli ma ancora decifrabili.
- **"BLOWN UP" esce dal bordo destro** con la posizione fissa del kit (centro a x=1050): va centrato a x≈960 e portato a ≈86 px, oppure su due righe. `thumb_kit.compose` oggi ha font 118 px e x fissi: non l'ho toccato (kit non è tra i file consentiti); è una modifica di 2 righe (font e x del chip destro).
- Il testo del chip destro compete col nome: in B e C il gancio ("BLOWN UP") dovrebbe essere più grande del nome, non il contrario.
Non verificabile ora: se la foto vera sia luminosa e piena (serve il fotogramma, vedi sotto).

## Tre concetti
| | Soggetto | Testo (parole) | Anno | Fotogrammi `cover.shots` | Note |
|---|---|---|---|---|---|
| **A** sicuro | sinistra Massalia 600 BC, destra Marsiglia oggi | MARSEILLE · 600 BC · NOW (3) | 600 BC | `massalia_a` (anno -600) + `now_day` (2026, giorno; alternativa `now_night` sollevata a luminosità media ≥ 90) | Rispetta tutte le regole ma è la formula dei tre concorrenti: nessun gancio, nessuna differenza [Likely]. Controllo. |
| **B** consigliato | sinistra Massalia, destra Saint-Jean in fumo | MARSEILLE · 600 BC · BLOWN UP (4) | 600 BC (primo anno) | `massalia_a` + `hook_1943_mid` | Coerente con il titolo A; il gancio si vede subito in miniatura e viene consegnato nei primi 9 s dal cold open. Scarto dalla regola "a destra NOW" della story: serve l'OK del proprietario (nessun anno sulla metà destra, quindi niente anno-gancio sbagliato). |
| **C** gancio puro | un solo scenario prima/dopo, stessa camera | BLOWN UP (2) + nome piccolo | nessun anno | `hook_1943_pre` + `hook_1943_post` | Metà simili (stesso inquadramento): rischio regola 4; senza anno 600 BC rompe la regola 5. Solo come variante di test dopo ≥ 3.000 impressioni per variante. |

Parametri dei fotogrammi (dalla story, `city.cover.shots`, lens 35, camera `[x,y,z,tx,ty,tz]`, 1080p dal pod con `run.sh cover` → `out/marseille_cover_<tag>.jpg`):
- `massalia_a` anno -600, cam [-460,-760,700,-430,250,0] — **DRAFT**: Massalia è una piccola città, la metà sinistra deve essere piena di città: se nel fotogramma è un campo con pochi edifici, usare `massalia_b` (anno -540, cam [-300,-500,420,-400,200,0]) o stringere con `--lbox`.
- `now_day` anno 2026, stessa camera; `now_night` stessa camera di notte.
- `hook_1943_pre` anno 1943,07, `hook_1943_mid` 1943,11, `hook_1943_post` 1943,15, cam [-730,-650,420,-730,150,0].
- Prima del pod, su un fotogramma CPU: il fumo (flames 6, smoke 14) e i blocchi che spariscono devono leggersi a 168 px (nota della story). Se non si leggono, B e C cadono e resta A.
Comando (dopo i fotogrammi, esempio B; correggere prima font/posizione dei chip): `python -m kit.thumb_kit cities/marseille/copertina/marseille_thumb_600bc_blownup.jpg --left out/marseille_cover_massalia_a.jpg --right out/marseille_cover_hook_1943_mid.jpg --title MARSEILLE --ly "600 BC" --ry "BLOWN UP"`.
Con e senza opzioni (R7): A senza e con bandiera NON richiesta (regola: niente bandiere); consegnare B e A come file separati.

## Coerenza miniatura / titolo / video
Miniatura B promette "600 BC" + "BLOWN UP"; titolo A: "The Quarter the Germans Dynamited"; cold open 0:00-0:09 mostra il quartiere in piedi, il dinamitaggio e le macerie [da confermare con la finestra reale]. Niente "Panier" in miniatura (vedi `METADATA.md`).
