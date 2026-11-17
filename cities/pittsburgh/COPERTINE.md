# Pittsburgh: copertine (17/11/2026) — formula serie `1754 > NOW`

Decisione del proprietario: sinistra = i FORTI (anno 1754, fotogramma 1754.97 = mura di Fort Duquesne complete, dal 1754.34 al 1754.96), destra = 2026 (NOW). Niente bandiera, niente evento-gancio. Titolo grande PITTSBURGH.

## Inquadrature (`city.cover.shots` in `cities/pittsburgh/story.json`, copiate da `kit build` in `city_pittsburgh.json`)
- `forts` (scelta L3, round 2): anno 1754.97, cam [-920,15,140] -> [-1050,125,3], lens 26. Obliqua alta da sud-est (circa 35 gradi), il forte riempie il quadrato, fiumi e Point intorno. Il forte e' centrato a (-1050,130) m, lato circa 90 m.
- `now`: anno 2026, cam [-1250,-1000,330] -> [-330,120,80], lens 35, giorno. Dal Mount Washington verso nord-est: grattacieli, Monongahela e Allegheny.

## Pod: SECONDO terminale (mentre il principale rende)
Il comando PRINCIPALE deve contenere `NOCOVER=1` (run.sh riga 200: `[ "${NOCOVER:-0}" = "1" ] || { step "5c/5 copertina"; cover; }`, verificato), altrimenti `full` rifa' le copertine alla fine:
`NOCOVER=1 CITY=pittsburgh bash run.sh full`   (il resto della riga del GO invariato)

Secondo terminale, una riga (1920x1080, 32 campioni, un processo per scatto = 2 processi in parallelo, ~30 min di costruzione scena ciascuno; costo CPU/RAM insieme al main NON misurato):
`cd <cartella del repo sul pod> && CITY=pittsburgh bash run.sh cover`
File prodotti (nella cartella del repo sul pod): `out/pittsburgh_cover_forts.jpg` e `out/pittsburgh_cover_now.jpg` (JPG 1920x1080). Si scaricano con questi due nomi (scp o file manager del pod) in `cities/pittsburgh/copertina/`.

## Miniatura finale in locale (dai fotogrammi del pod, ritagli raddoppiati rispetto alla bozza 960x540)
`python -m kit.thumb_kit cities/pittsburgh/copertina/pittsburgh_thumb_1754_now_1280x720.jpg --left cities/pittsburgh/copertina/pittsburgh_cover_forts.jpg --right cities/pittsburgh/copertina/pittsburgh_cover_now.jpg --title PITTSBURGH --ly 1754 --ry NOW --lbox 464,0,1050 --rbox 800,0,1050 --text-size 104 --lx 225 --rx 1070`
Controllo a 168 px: `python -c "from PIL import Image;Image.open('cities/pittsburgh/copertina/pittsburgh_thumb_1754_now_1280x720.jpg').resize((168,94),Image.LANCZOS).save('cities/pittsburgh/copertina/mockup_168.png')"`
Nota: `thumb_kit` vuole il file di uscita come primo argomento (non lo slug).

## Bozza (CPU 960x540, 8 campioni, con rumore: sul pod 32 campioni)
`copertina/pittsburgh_thumb_1754_now_DRAFT.jpg` (da `frame_forts_1754_draft960.jpg` + `frame_now_draft960.jpg`, `--lbox 237,0,525 --rbox 400,0,525`), mockup `copertina/mockup_168_DRAFT.png`.
Debole: (1) il nome copre la parte bassa del forte (il box e' gia' a tutta altezza: se serve alzare il forte, spostare il target della cam di -15 m in y); (2) il forte e' tagliato un poco a sinistra/destra dallo scorrimento diagonale; (3) i forti sono blocchi marroni lisci su terra piatta, leggono come "fortino" ma sono meno ricchi dei grattacieli a destra; (4) a destra lo stadio (tetto rosso, correzione roof:false in altro branch) e' fuori ritaglio, il cielo occupa una fascia bianca in alto; (5) a 168 px si leggono 1754, NOW, PITTSBURGH e la differenza forte/grattacieli; i dettagli del forte no.

## Round 2 sinistra (17/11): alternative L1-L3, anno 1754.97 (tag NON in cover.shots: il pod rende solo `forts` e `now`)
Bozze: `copertina/pittsburgh_thumb_DRAFT_L1.jpg`, `_L2.jpg`, `_L3.jpg`; foglio con mockup a 168 e 120 px: `copertina/sheet_L1_L2_L3.jpg`; fotogrammi 960x540 `frame_forts_L1_960.jpg` ecc. Destra invariata. Bozze CPU 8 campioni.
- `forts_L1`: cam [-1550,-560,330,-1010,140,0], lens 35, obliqua alta da sud-ovest: Point, due fiumi, colline; forte ~23% del ritaglio, lbox 190,0,525 (960) = 380,0,1050 (1920). A 168 px il forte e' un puntino.
- `forts_L2`: cam [-720,-260,55,-1040,150,12], lens 35, bassa da sud-est, colline e cielo dietro; forte ~40% largo ma piatto, lbox 180,0,525 = 360,0,1050. A 168 px e' una striscia marrone.
- `forts_L3` (SCELTA): cam [-920,15,140,-1050,125,3], lens 26, forte intero con margine, terra del Point intorno; lbox 232,0,525 = 464,0,1050. A 168 px si legge come forte con 4 bastioni e il nome non copre i bastioni.
Perche L3: (1) unica che si legge a 168 px, L1 e L2 hanno il forte troppo piccolo; (2) forte interno al ritaglio, niente taglio ai bordi e fuori dalla zona del nome; (3) limite rimasto: sfondo ancora in gran parte acqua, bastioni a cubi (geometria del modello, non della camera) e nessun albero nel terreno 1754.
