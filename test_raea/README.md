# Test A/B: Blender/Cycles contro raea, New York primi 20 s

Stessa scena, stesso pod (RTX 5080): 480 fotogrammi, 24 fps, 1920x1080, anni e camera di `schedule_nyc.json`.
A = `build_render.py` (8 campioni, OptiX, parametri del render finale). B = `raea/nyc20.tsx` (raea).

## Lancio (terminale del pod)
`cd /workspace && git clone -b claude/install-two-repos-776mx3 https://github.com/doctail/city3d && bash city3d/test_raea/run_test.sh`
Lo script stampa il comando di avanzamento. Tempi di ogni fase in `out/tempi.txt`; fine: `out/confronto_A_sinistra_B_destra.png`, `A_blender.mp4`, `B_raea.mp4`, `risultati.tgz`. `ONLY=A` o `ONLY=B` per una meta' sola.

## File
- `run_test.sh`: uno script, fasi misurate con `date +%s` (prerequisiti, installazione Blender, GPU, dati, render A; installazione raea con ripiego tarball e poi `cargo build`, costruzione scena, avvio+1 fotogramma, render B), picchi RAM/VRAM, 6 fotogrammi fissi (0, 80, 120, 160, 230, 479) e foglio affiancato.
- `gen_scene.py`: legge `data_nyc_src` (edifici, terra, fasi di terra, parchi) e lo schedule, scrive `raea/scene.gen.ts` (non in git, lo crea il pod).
- `raea/nyc20.tsx`: la composizione. `raea/check_frames.tsx`, `verifica_locale.sh`: controlli locali.

## Verificato in locale
- [Certain] Il generatore gira sui dati veri: 145.927 edifici nel file, 145.874 validi, 2.515 in inquadratura nei 20 s (taglio fuori campo), 403 blocchi, ~92k triangoli, 9 MB. Edifici presenti nei 20 s solo nei primi 176 fotogrammi (poi l'anno e' 1609: terra e acqua).
- [Certain] La composizione passa `tsc` contro l'SDK del clone (provato con un errore voluto: lo vede). L'unico errore e' di `prelude.ts` dell'SDK, non nostro.
- [Certain] `check_frames.tsx` valuta la composizione con l'SDK vero (`renderFrame`): camera, luci, nebbia, 434 parti a 2026, 3 parti nel 1609.
- [Certain] `run_test.sh`: sintassi e flusso completo provati con finti `nvidia-smi`, `raea`, `bpy`: fasi, tempi, parsing dei log, foglio di confronto. Non provato con i programmi veri.
- [Likely] Le API usate (BufferMesh, Mesh3d, Fog, DirectionalLight, `raea render --composition/--quality`, `RAEA_FRAME_LOG`) sono lette dalle guide e dal codice del clone.

## NON verificato
- Nessun render raea: il binario non e' scaricabile da qui (raea.io e releases 403). Non so se `raea render` accetta la scena (controlli di stage), quanto dura, ne' che aspetto ha. [Guessing] Sole, ambiente e nebbia sono valori tirati a occhio.
- Vulkan sul pod: se vede solo llvmpipe, lo script salta B (`FORCE_B=1` per forzare). Installatore, tarball e `cargo build` mai eseguiti (nome dell'asset e dipendenze di build sono ipotesi).
- Costo di React in raea: ogni fotogramma con la citta' porta ~8 MB di geometria da serializzare; la pagina gira su QuickJS senza JIT (docs/linux.feature). [Guessing] puo' essere lento nei primi ~176 fotogrammi.
- Blender sul pod: stesse fasi di `run.sh` ma mai rilanciate da qui; `restore_after_build.sh` e `hist_kit` come per il render vero.

## Differenze tra le due scene (il confronto di tempo NON e' alla pari)
A ha: edifici storici e demoliti, monumenti, ponti, moli, rilievo DEM, alberi, navi, strade, acqua con onde, cielo con nuvole, 8 campioni con denoiser. B ha: solo gli edifici attuali dal loro anno (prismi piatti, 8 colori; crescita per scala come in Blender, con blocchi da 8 anni), terra, fasi di terra (acceso/spento), parchi dal 1858, acqua piana, sole+ambiente+nebbia. Niente alberi, strade, ponti, navi, rilievo, ombre fini.
