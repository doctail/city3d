# New York: GO POD (20/11/2026). Un solo messaggio, pronto da incollare

Stato: scritto dalla chat, NON ancora acceso nessun pod. Il GO vale solo se la chat lo conferma nel messaggio che contiene questo testo.

## Prima riga: due correzioni a run.sh trovate nella verifica (commit `0194a7d`, gia' incluse)
1. `CITY=nyc` entrava nel ramo VECCHIO (`D=data`, `fetch_nyc.py` scarica i dati da internet, nessun `--city`). Ora il ramo vecchio vale solo senza `cities/nyc/story.json`: NYC usa `data_nyc` + `city_nyc.json` come le altre citta'.
2. `hist_nyc.py` e' il modulo VECCHIO (non lo stub del kit) e `data_nyc_src` non conteneva landmarks, ponti, fires, floods, landphases (moli): il pod avrebbe reso una citta' senza monumenti, ponti e moli. Ora `data_nyc_src` e' ripacchettato e run.sh per NYC fa `kit.hist_kit build` + `restore_after_build.sh` (moli e DEM).
   Verifica [Certain]: in una copia pulita, da `data_nyc_src` -> hist -> restore escono file con lo STESSO md5 di `data_nyc` locale (hist, landphases, landmarks, roads, bridges, fires, floods, dem). Costo locale del passo hist: 2 min 9 s.

## Costo (NON misurato sul pod) AGGIORNATO 20/11
- Il primo lancio sul pod ha misurato 4-5 s a fotogramma (non 1,2 s come Lione): ETA ~15 h. Pod fermato dal proprietario. Causa: 959K alberi (PERF_ANALISI.md). Rimedio approvato: alberi a 1/3 di densita' con chiome x1,6 (`vegetation` in city_nyc.json e story.json), commit 0194a7d.
- Stima con 1/3 alberi, SENZA `SEG` (SEG non provato end-to-end, non usarlo): ~2,25 s a fotogramma (misura locale CPU ~2x, NON del pod) x 13.186 = ~8,2 h giorno + notte e scena. Totale atteso **~8-9 h, ~5-5,5 EUR** [Likely]. Controllare il tempo dei primi fotogrammi: se resta sopra ~3 s a fotogramma, fermare e avvisare la chat.
- Prezzo: A40 Secure era 0,59 $/h il 16/10 (da `PRODUZIONE_TIMELAPSE.md`, non rimisurato): **~3,0-3,8 $** (circa 2,7-3,3 EUR). Il prezzo vero e' quello che mostra RunPod all'accensione.
- Copertine: NON si fanno sul pod (vedi sotto), risparmiano ~35 min di `run.sh full` e 5 processi da ~10 GB di RAM.

## Messaggio da incollare nel terminale del pod (template PyTorch, 30 GB, A40)

Incolla TUTTO il blocco in una volta. Si ferma da solo se la GPU o la versione non vanno.

```
cat > /workspace/go_nyc.sh <<'EOF'
cd /workspace
echo "== GPU"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
CU=$(python3 -c "import ctypes;print(ctypes.CDLL('libcuda.so.1').cuInit(0))"); echo "cuInit = $CU"
nvidia-smi --query-gpu=name --format=csv,noheader | grep -q A40 && [ "$CU" = "0" ] || { echo "STOP: serve A40 con cuInit = 0. Termina il pod e cambia regione/host."; exit 2; }
echo "== codice"
[ -d city3d ] || git clone -q https://github.com/doctail/city3d
cd city3d && git fetch -q origin && git checkout -q main && git pull -q --ff-only
git log -1 --oneline
git merge-base --is-ancestor 0194a7d HEAD || { echo "STOP: il pod non ha il commit 0194a7d (codice vecchio). Non lanciare."; exit 3; }
git diff --quiet 0194a7d HEAD -- run.sh build_render.py kit schedule_nyc.json schedule_nyc_night.json city_nyc.json cities/nyc/story.json data_nyc_src || { echo "STOP: i file di render sono cambiati dopo 0194a7d. Avvisa la chat."; exit 4; }
rm -rf out/full out/night 2>/dev/null   # i fotogrammi del primo lancio hanno gli alberi vecchi: run.sh riprende da dove si e' fermato, quindi vanno cancellati
echo "== lancio full (giorno 13186 + notte 240 fotogrammi, niente copertine)"
nohup env CITY=nyc NOCOVER=1 bash run.sh full > /workspace/city3d/full.log 2>&1 &
sleep 2; echo "lanciato, pid $!"
EOF
bash /workspace/go_nyc.sh
```

### Banner da verificare (compare dopo 3-8 min, dopo apt/pip e il passo dati)
```
cd /workspace/city3d && grep -E "VERSIONE|fotogrammi|uso:|hist_kit\] edifici vivi|restore\] landphases|MANCANO|STOP|rror" full.log | cut -c1-200
```
Deve mostrare TUTTO questo (se manca una riga o c'e' un errore: fermare e mandare la riga in chat):
- `VERSIONE: <hash di git log -1> ... | schedule_nyc: 554 s, lens 32.0`
- `fotogrammi 13305, notte dal fotogramma 12946, nomi %05d`
- `uso: OPTIX` (se `CUDA` va bene ma piu' lento; se `CPU` lo script si ferma da solo)
- `[hist_kit] edifici vivi: 1609: 0, 1500: 0, 1800: 12043, 1900: 291454` (identico al locale)
- `[restore] landphases 714 pier entries 347 dem D max 202 m`

### Avanzamento in tempo reale (una riga, ogni 60 s)
```
cd /workspace/city3d; while :; do D=$(ls out/full 2>/dev/null|grep -c jpg); N=$(ls out/night 2>/dev/null|grep -c jpg); R=$(find out/full out/night -name '*.jpg' -mmin -5 2>/dev/null|wc -l); echo "$(date +%H:%M) giorno $D/13186 notte $N/240 ultimi5min $R ETA_min $(( R>0 ? (13186-D+240-N)*5/R : -1 ))"; tail -1 full.log|cut -c1-110; sleep 60; done
```
ETA = solo fotogrammi (non conta la scena della notte, ~30 min, ne' la codifica finale). `-1` = fermo o ancora in costruzione scena (i primi 30+ min non ci sono fotogrammi: e' normale). Se il giorno si ferma, run.sh scrive `GIORNO INCOMPLETO` ed esce: rilanciare lo stesso blocco (riprende da dove era).

### Copertine
- NON servono dal pod. La miniatura finale c'e' gia' (`cities/nyc/delivery/copertina/nyc_thumb_1609_now_1280x720.jpg`, da frame locali; la meta' destra e' del 2015). `run.sh full` di base chiude con un passo copertine di altri ~35 min e 5 scene in parallelo: e' ridondante, per questo `NOCOVER=1`.
- Dopo il render la chat estrae dal video, in locale e gratis, i fotogrammi 1609 (t=0), 2026 giorno (t=530 s, prima del tramonto a 539,4 s) e 2026 notte (t=550 s): `ffmpeg -ss 530 -i nyc_full.mp4 -frames:v 1 nyc_cover_now_day.jpg`. Se serve una copertina con camera nuova, e' una sessione pod NUOVA con costo dichiarato, mai "mentre e' acceso".

### Si puo' chiudere il pod SOLO quando (tutte vere)
1. `full.log` finisce con `=== FINITO` e `tail -3 full.log` non ha errori.
2. Controllo sul pod (durata attesa 554,4 s, ~13.305 fotogrammi):
```
cd /workspace/city3d/out && ls -l nyc_full.mp4 years.json && ffprobe -v error -show_entries format=duration -of csv=p=0 nyc_full.mp4
```
3. Scaricati dal browser (Jupyter, cartella `city3d/out`, tasto destro > Download): **`nyc_full.mp4`** e **`years.json`**. Dimensioni uguali a `ls -l`. (Nessuna copertina da scaricare.)
4. Solo allora: **Terminate** (non Stop). Qualsiasi correzione dopo e' una sessione nuova (scena + fotogrammi, costo dichiarato prima).

---

# POST-RENDER (montaggio): chi fa che cosa

## File che servono al montaggio
| File | Da dove | Chi |
|---|---|---|
| `nyc_full.mp4` | render del pod | proprietario (download) |
| `years.json` | render del pod (`out/years.json`) | proprietario (download) |
| musica A: "Waking to Reality" (Unicorn Heads), file `a55ce738-Waking_to_Reality_-_Unicorn_Heads.mp3` | YouTube Audio Library | **proprietario** |
| musica B: "Monument" (TrackTribe), file `b863fd68-Monument_-_TrackTribe.mp3` | YouTube Audio Library | **proprietario** |
| `nyc_overlay.webm` | `python -m kit montaggio nyc --overlay` | chat/agente, locale |
| `nyc_audio.m4a` | `montaggio/sfx_kit.py` | chat/agente, locale (serve la musica) |
| `nyc_finale.mp4` | una riga `cmd` (vedi `MONTAGGIO.md`) | proprietario, sul suo PC |

## Musica: cosa deve fornire il proprietario [Certain per i nomi, Likely per la fonte]
- `cities/nyc/story.json` ha `regia.music = "waking_monument"`; `kit/music/waking_monument.json` fissa le due tracce: A "Waking to Reality" - Unicorn Heads (272,6 s) e B "Monument" - TrackTribe (251,5 s). Sono le stesse di Parigi e Marsiglia ("YouTube Audio Library", come scritto nelle loro consegne).
- NON sono nel repo (nessun .mp3 in `city3d`): vanno scaricate dalla YouTube Audio Library e inviate in chat (cartella qualsiasi, nomi dei file come sopra o `waking.mp3` / `monument.mp3`; la chat le passa con `--A` e `--B`, o `KIT_MUSIC_A` / `KIT_MUSIC_B`). Con la sola A il mix funziona ("musica: solo A"), ma il modello e' A+B.

## Ordine in locale (chat/agente), dopo aver ricevuto video, years.json e musica
```
cp years.json montaggio/years_nyc.json        # sostituisce il years_nyc.json di prova (7.839 fotogrammi) con quello vero del render
python -m kit montaggio nyc --A waking.mp3 --B monument.mp3 --overlay
```
che esegue `kit_city.py nyc` (tempi HUD/titolo/fine dallo schedule), `sfx_kit.py nyc --A --B` (musica + effetti delle soste, -14 LUFS -> `out/nyc_audio.m4a`) e `ov_kit.sh nyc long` (-> `out/nyc_overlay.webm`, a pezzi da 800 fotogrammi, riprende se interrotto; la prima volta fa `npm install` in `montaggio/`; chromium da `/opt/pw-browsers`). Poi il proprietario mette `nyc_full.mp4`, `nyc_overlay.webm`, `nyc_audio.m4a` nella stessa cartella e lancia la riga `ffmpeg` di `cities/nyc/delivery/MONTAGGIO.md`.

## Da sapere (verificato oggi con `kit_city.py nyc`)
- `montaggio/labels_nyc.json` NON esiste: l'overlay uscirebbe senza etichette sui monumenti. Prima del render overlay va generato (`montaggio/labels_cam.py` + `labs_nyc.json`, che esiste) da un agente, altrimenti e' una scelta da registrare.
- `kit_city` avvisa: years di prova a 7.839 fotogrammi (si risolve con il `years.json` vero) e `city.est_until` assente (usa 1800: la popolazione prima e' mostrata con "~").
- Overlay: 13.306 fotogrammi (554,4 s). Il render ne fa 13.305: nel montaggio `-shortest` chiude alla durata piu' corta.
- Controlli R13 sull'overlay vero (fermo immagine a ogni inizio capitolo, ogni cartello, primi 12 s, ultimi 15 s): da fare dopo, NON fatti.
