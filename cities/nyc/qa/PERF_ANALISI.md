# NYC render lento: analisi (20 nov 2026, branch yb/nyc-perf)

Misure LOCALI su CPU (4 core, bpy 5.2.2), 640x360 4 spp (PERF=1 in build_render.py). Non sono tempi del pod: valgono come RAPPORTI.
Pod: 4-5 s/fotogramma (A40), contro 0,8 s Marsiglia e 1,2 s Lione.

## Causa principale
[Certain] il costo per fotogramma e' un pavimento di sincronizzazione scena + BVH + render, che dipende dalla geometria/istanze PRESENTI nella scena, non da cosa cambia. Python per fotogramma (visibilita'/crescita): 0,01-0,4 s, trascurabile.
[Certain] le ~959K istanze di alberi (vegetazione GN, 85 oggetti) sono la voce piu' pesante: a 1930, togliendole, render 5,0 -> 2,15 s e sync (a scena ferma) 2,7 -> 0,06 s. Nel 1609 la scena ha 226 oggetti e 4 blocchi citta' ma con i 958K alberi costa comunque 5,5 s di render e 4 s di sync.
[Likely] secondo costo: 3234 blocchi citta' (6,74M vertici) + 305K predecessori + 3,55M vertici di alberi cotti nei parchi; gli oggetti "nascosti" restano in scena a z=-5000 e si pagano tutti. Qualunque oggetto cambi, la sync passa da ~4 s (nulla cambia) a ~8 s.
Confronto: Lione 3,4M vertici (1,2 s), Marsiglia 1,97M + 1,48M alberi (0,8 s), NYC ~11M vertici + 959K istanze (4-5 s).

## Misure (CPU, 640x360, 4 spp; sync = render 32x18 1 spp)
| caso (anno 1930) | sync | render |
|---|---|---|
| base | 8,3-9,1 (4,0 fermo) | 6,2 |
| toglie oggetti mai visibili in 600 fotogrammi (PRUNE) | 5,2-6,5 (2,7 fermo) | 4,9-5,0 |
| + senza vegetazione istanziata (solo ablazione, cambia l'aspetto) | ~0,06 | 2,15 |
Per anno con PRUNE (finestra 600): 1609 sync 3,9-5,7 / render 5,5; 1930 sync 5,2 / render 4,8; 2014 sync 4,9 / render 4,3-4,7 (base 1609: 10,2/6,3; 2014: 8,8/6,4).

## Aspetto (confronto numerico, 960x540 8 spp, fotogrammi 361, 8953, 11569, 13000)
- PRUNE (oggetti mai visibili nella finestra tolti DAVVERO dalla scena): IDENTICO. Differenza media 0,00-0,07/255, pixel con diff>8: <=0,003%, max 23 (rumore).
- CULL (alberi fuori inquadratura): NON identico, 0,1-2,6% pixel con diff>8 (anche con margine 2,5, quindi la causa non e' l'inquadratura: forse la riscrittura della mesh o i ~18K alberi dietro la camera; NON indagato). Quindi CULL e' spento, non usarlo finche' non e' chiarito.

## Leve (con stima, da verificare sul pod)
1. PRUNE a segmenti (SEG=N in run.sh): lossless. Gain misurato in CPU: -35% sync, -20% render => ~1,3-1,4x [Likely] sul pod. Costo: 1 ricostruzione scena (~3 min) per segmento; con SEG=1000 ~14 processi = ~40-45 min in piu'.
2. Alberi istanziati (959K): e' la leva grossa (fino a ~2x), ma cambia l'aspetto: densita' (vega_step 17 -> 24 m = -50% alberi), o forma piu' povera (sub 2 -> 1). Non applicata: la grafica e' approvata. Decisione del proprietario.
3. CULL alberi fuori inquadratura: ~-50% istanze nei segmenti; da correggere (vedi sopra).
4. Alberi cotti nei parchi (3,55M vertici, 12 vertici/albero, tree_mesh 'octa' = 6): ablazione dei parchi non ha mostrato guadagno misurabile in CPU; non priorita'.

## Formula di costo per citta' pesanti [Guessing, 3 punti: Lione, Marsiglia, NYC]
s/fotogramma(pod) ~ 0,25 + 0,35 * (Mvertici_citta_e_alberi_cotti) + 1,6 * (M istanze alberi vive)  (con 1080p, 8 spp, A40).
Prova: NYC 11M vertici, 0,96M istanze -> ~5,6 (misurato 4-5); Lione 3,4 -> 1,4 (1,2); Marsiglia 3,4 -> 1,4 (0,8). Sovrastima i piccoli: usare solo come ordine di grandezza. Ore pod = fotogrammi x s / 3600; euro ~ 0,62 x ore (NYC: 10 euro / 16 h).
Regola: prima del pod, misurare con PERF=1 (sync 32x18 1 spp a scena ferma) e contare istanze alberi vive; oltre ~500K istanze o ~8M vertici, segmentare con PRUNE.

## Stima NYC con PRUNE (SEG=1000)
13186 x 4,5 s / 1,35 = ~12,2 h + ~0,7 h di ricostruzioni = ~12,9 h ~ 8 euro (base: rapporto CPU, non misurato sul pod). L'obiettivo <2 s/fotogramma NON si raggiunge senza ridurre gli alberi.

## Cosa e' nel branch
build_render.py: PERF=1 (profilo per fase), PRUNE=1 (toglie oggetti mai visibili; WIN=N limita la finestra), CULL=1 (sperimentale, non identico), ABL (ablazioni di prova). run.sh: SEG=N (full a segmenti con PRUNE; non provato end-to-end su run.sh, provata solo la logica PRUNE in build_render). Nessuna modifica attiva di default.

## Aggiornamento: alberi istanziati a 1/3 (decisione del proprietario)
Opzione di citta' `vegetation.density` (griglia: passo / sqrt(density)) e `vegetation.scale_mul` (chioma piu' grande), env VEGDENS / VEGSCALE per prove. Messe in city_nyc.json e cities/nyc/story.json: density 0,3333, scale_mul 1,6. Le altre citta' non cambiano (default 1 e 1).
Istanze verificate: 958.688 -> 319.704 (0,333 esatto; riva 223.179 -> 74.490, vega 735.509 -> 245.214).
Misure CPU 640x360 4 spp, fotogramma che cambia (sync + render, s), stessa base di sopra:
| anno | base | 1/3 alberi | 1/3 + PRUNE (finestra 600) |
|---|---|---|---|
| 1609 | ~9,5 | 4,3 (2,2x) | 4,2 (2,3x) |
| 1930 | ~14,4 | 7,7 (1,9x) | 5,9 (2,4x) |
| 2014 | ~14,7 | 7,5 (2,0x) | 5,6 (2,6x) |
Stima NYC sul pod (base 4,5 s/fotogramma, 13186 fotogrammi, 0,62 euro/h, rapporto CPU non misurato su pod [Likely]):
- 1/3 alberi, senza segmenti: 4,5/2,0 = ~2,25 s -> 8,2 h -> ~5,1 euro.
- 1/3 alberi + PRUNE a segmenti (SEG=1000): 4,5/2,4 = ~1,9 s -> 7,0 h + ~0,7 h ricostruzioni = ~7,7 h -> ~4,8 euro.
Aspetto (1920x1080 8 spp, cities/nyc/qa/trees3/before|after|after_scale16): Manhattan 1930, 2014 e 2026 e i parchi: invariati (i loro alberi sono "cotti", non toccati). La foresta 1609 (e fino a ~1800, dove esistono alberi istanziati) PERDE carattere con 1/3 e scala 1,0: fascia di riva molto piu' rada e radure inland visibili. Con scale_mul 1,6 (a costo zero: stesse istanze) la copertura della chioma torna simile; restano alberi piu' grandi/alti (pioppi) e la riva un po' meno fitta.
