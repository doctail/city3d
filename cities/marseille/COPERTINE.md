# Marseille — miniatura (formula Year Built/Lione, 16/11/2026) — PROVVISORIO: fotogrammi da ricontrollare dopo il render finale

Regole (analisi/ctr/MINIATURE.md + AVVIO "Thumbnail layout"): un solo soggetto leggibile, luminosa e satura (SAT 1,4, contrasto 1,2), una città piena per metà, anno = primo anno del video = 600 BC, destra = NOW, niente bandiere né tag canale, 3-4 parole. Formula di Lione: "43 BC > NOW". Il 1943 NON è in miniatura (né nel titolo): è un capitolo. Concorrenti (dato del proprietario): Timeline Cities, Brick Cities, ChronosPulse 3D, tutti "Marseille 600 BC → 2026" con bandiera e nome enorme.

## Miniatura finale
Testo "600 BC > NOW / MARSEILLE". File: `cities/marseille/copertina/miniatura_600BC_NOW_1280x720.jpg`.
- Sinistra `massalia_b` (anno -540, ritaglio `--lbox 480,0,720`), destra `now_day` (`--rbox 0,0,900`). Il ritaglio esclude il mare in basso; a destra resta l'azzurro del porto dietro la cattedrale.
- La sinistra è un fotogramma del -540, non del -600 esatto.
- Comando: `python -m kit.thumb_kit cities/marseille/copertina/miniatura_600BC_NOW_1280x720.jpg --left out/marseille_cover_massalia_b.jpg --right out/marseille_cover_now_day.jpg --title MARSEILLE --ly "600 BC" --ry NOW --lbox 480,0,720 --rbox 0,0,900 --text-size 104 --lx 225 --rx 1070`
- Notte (opzione): `now_night` aveva luminosità media 31 (soglia 90): alzata con gamma 0,45 a 92 → `copertina/marseille_cover_now_night_lift.jpg` (sollevamento forte).
- Scartate: `massalia_a` (metà sinistra vuota) e i concetti con il fotogramma 1943.

## Test a 168 px
`copertina/mockup_168_placeholder.png` è del layout vecchio con sfondi finti: NON rappresenta la miniatura finale, da rifare con il file vero. Il testo grande (nome città) si leggeva a 168 e 120 px; chip piccoli a 120 px (per questo `--text-size 104`). Non verificato sulla miniatura finale in un feed con i concorrenti.
