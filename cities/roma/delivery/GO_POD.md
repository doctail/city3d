# Roma: GO POD (BOZZA, 27/11/2026). NON ancora dato: serve il GO scritto della chat e il merge su main. Un solo messaggio da incollare.

Commit di render: `4d35e46` (oggi SOLO su `claude/prossima-citta-finire-2o3ryt`; il GO vale quando `main` lo contiene: merge pulito verificato con `git merge-tree`, main ha 2 commit in piu' che toccano solo `kit/regia_check.py` e `montaggio/years_pittsburgh.json`). Lo script sotto si ferma da solo se main non contiene 4d35e46.
Verificato sui file (27/11): POD PARITY 0 differenze (md5 di tutti i json/npz, rieseguita); `run.sh` per Roma esegue `hist_kit build` + `restore_after_build.sh` (esiste, idempotente); start_year -753, field_colors 5 toni oliva, look/palette, 22 soste, incendi `destroy` (455-547 d.C.), 4 ponti, 1 area d'acqua (Isola Tiberina) attivi in `story.json` e `city_roma.json`; costo cambi 50.842 (~0,17 h, budget 1 h); edifici su acqua: 0 fino al 1800, 1 nel 1900-1950, 3 nel 2000-2026 (residui, da accettare). Schedule: 660 s, 15.840 fotogrammi (%05d), niente notte, lens 32.
Aperti (WARN, non FAIL): regia_check (versione di main) 0 tempi morti ma 12 tratti con camera ferma >8 s e anno +10 (8-22 s e' il rewind iniziale; 26-51 s +177 a; 99-133 s +148 a; 470-496 s +173 a; Pittsburgh ne aveva 3); corridoi/aree vuote del gate sezione d (accettate in story); densita' 1500 (11.352 vs 10.110 nel 2026). Cover: in `city_roma.json` ora 3 scatti (753 a.C., 120 d.C., 2026); il gate va rilanciato dopo il merge per vedere la bozza.

## Costo [Guessing: Roma NON misurata sul pod]
Base Marsiglia: 0,8 s/fotogramma x 15.840 = ~3,5 h + ~30 min di scena = ~4 h, ~0,5 EUR/h = ~2 EUR. Roma ha 92.562 edifici e 1.706 monumenti: se i primi fotogrammi superano ~2 s, fermare e scrivere in chat. Picco RAM locale ~11 GB per processo (A40 30 GB: un solo processo).
Copertine: NOCOVER=1 (3 processi `cover` in parallelo rischiano ~33 GB). Si estraggono dal video in locale: -753 (primo fotogramma), ~anno 120, 2026 (ultimo).

## Incolla nel terminale del pod (A40, 30 GB)
```
cat > /workspace/go_roma.sh <<'EOS'
cd /workspace
echo "== GPU"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
CU=$(python3 -c "import ctypes;print(ctypes.CDLL('libcuda.so.1').cuInit(0))"); echo "cuInit = $CU"
nvidia-smi --query-gpu=name --format=csv,noheader | grep -q A40 && [ "$CU" = "0" ] || { echo "STOP: serve A40 con cuInit = 0. Termina il pod e cambia regione/host."; exit 2; }
[ -d city3d ] || git clone -q https://github.com/doctail/city3d
cd city3d && git fetch -q origin && git checkout -q main && git pull -q --ff-only
git log -1 --oneline
git merge-base --is-ancestor 4d35e46 HEAD || { echo "STOP: manca il commit 4d35e46 (main non e' stato unito o codice vecchio)."; exit 3; }
git diff --quiet 4d35e46 HEAD -- run.sh build_render.py kit ':!kit/regia_check.py' schedule_roma.json city_roma.json cities/roma/story.json hist_roma.py data_roma_src || { echo "STOP: i file di render sono cambiati dopo il GO. Chiedere in chat."; exit 4; }
rm -rf out/full 2>/dev/null
nohup env CITY=roma NOCOVER=1 bash run.sh full > /workspace/city3d/full.log 2>&1 &
sleep 2; echo "lanciato, pid $!"
EOS
bash /workspace/go_roma.sh
```
`run.sh` fa da solo: dati da `data_roma_src`, poi `python -m kit.hist_kit build roma data_roma` + `restore_after_build.sh` (step hist_kit build), prova GPU (OPTIX), controllo costo, render `full` a 1920x1080, 24 fps, fotogrammi 1-15840, `--device` scelto da `gputest.py` (si ferma se CPU).

## Banner (dopo 3-8 min)
```
cd /workspace/city3d && grep -E "VERSIONE|fotogrammi|uso:|hist_kit|costo|MANCANO|STOP|rror" full.log | cut -c1-200
```
Deve mostrare: `VERSIONE: <hash> ... | schedule_roma: 660 s, lens 32.0`; `fotogrammi 15840, notte dal fotogramma 0, nomi %05d`; `[costo] ... cambi in tutto il video 50842`; `uso: OPTIX`. Errore o riga mancante: fermare e mandare la riga in chat.

## Avanzamento (una riga ogni 60 s)
```
cd /workspace/city3d; while :; do D=$(ls out/full 2>/dev/null|grep -c jpg); R=$(find out/full -name '*.jpg' -mmin -5 2>/dev/null|wc -l); echo "$(date +%H:%M) $D/15840 ultimi5min $R ETA_min $(( R>0 ? (15840-D)*5/R : -1 ))"; sleep 60; done
```
`-1` = ancora in costruzione scena (primi ~30-55 min, normale).

## Si chiude il pod SOLO quando
1. `full.log` finisce con `=== FINITO` senza errori.
2. `cd /workspace/city3d/out && ls -l roma_full.mp4 years.json && ffprobe -v error -show_entries format=duration -of csv=p=0 roma_full.mp4` (attesi ~660 s, 15.840 fotogrammi).
3. Scaricati `roma_full.mp4` e `years.json` (Jupyter, city3d/out) con dimensioni uguali a `ls -l`.
4. Solo allora Terminate (non Stop).

## Dopo il render (chat/agente, in locale)
`cp years.json montaggio/years_roma.json; python -m kit montaggio roma --A waking.mp3 --B monument.mp3 --overlay` (musica `waking_monument`), poi LIGHT spezzata e controllo fotogrammi (regola 26/11), copertine dal video (753 a.C./120 d.C./2026), consegna completa (CONSEGNA_YOUTUBE.md).
