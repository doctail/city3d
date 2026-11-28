# Copenaghen: GO POD (BOZZA, NON dato). Il GO lo da' la chat dopo l'ok del proprietario sui 6 fotogrammi (`cities/copenhagen/delivery/foglio6/`). Un solo messaggio da incollare.

Commit di render: `d570c19` (branch `yb/copenhagen-go`, regia e navi nuove; va unito a `main` PRIMA del GO, il pod scarica main). Sostituire l'hash con quello del merge se cambia.
Schedule: 660 s, 15.840 fotogrammi (nomi %05d), notte dal fotogramma 15.481 (giorno fino a 15.721, notte 15.601-15.840), lens 32, 17 soste in hover, 131.817 edifici al 2026.
Il pod usa `hist_kit` (story) tramite `cities/copenhagen/qa/fix/restore_after_build.sh`: `hist_copenhagen.py` e `data_copenhagen_src` NON cambiano.

## Costo (NON misurato su GPU) [Guessing]
- Base: Marsiglia 0,8 s/fotogramma, Lione 1,19 s (145K), Copenaghen vecchio ~1,9 s con notte e fuoco (PROSSIMA_COPENAGHEN). Copenaghen ha ~267K oggetti (reali + predecessori): 1,0-1,9 s x 15.961 = 4,4-8,4 h + 2 scene (giorno, notte) di 0,5-1 h = 5,5-10 h, circa 2,7-5 EUR a 0,5 EUR/h. Locale CPU (4 core, bpy 5.3): costruzione scena + 58 fotogrammi 480x270 = 3.297 s (non confrontabile con A40). Se i primi fotogrammi superano ~3 s, fermare e scrivere in chat.
- Copertine: NOCOVER=1 (si estraggono dal video in locale).

## Incolla nel terminale del pod (A40, 30 GB)
```
cat > /workspace/go_cph.sh <<'EOS'
cd /workspace
echo "== GPU"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
CU=$(python3 -c "import ctypes;print(ctypes.CDLL('libcuda.so.1').cuInit(0))"); echo "cuInit = $CU"
nvidia-smi --query-gpu=name --format=csv,noheader | grep -q A40 && [ "$CU" = "0" ] || { echo "STOP: serve A40 con cuInit = 0. Termina il pod e cambia regione/host."; exit 2; }
[ -d city3d ] || git clone -q https://github.com/doctail/city3d
cd city3d && git fetch -q origin && git checkout -q main && git pull -q --ff-only
git log -1 --oneline
git merge-base --is-ancestor d570c19 HEAD || { echo "STOP: manca il commit d570c19 (codice vecchio)."; exit 3; }
git diff --quiet d570c19 HEAD -- run.sh build_render.py kit tools schedule_copenhagen.json schedule_copenhagen_night.json city_copenhagen.json cities/copenhagen/traffic.json cities/copenhagen/story.json cities/copenhagen/palette.json cities/copenhagen/qa/fix hist_cph_kit.py data_copenhagen_src || { echo "STOP: i file di render sono cambiati dopo il GO. Chiedere in chat."; exit 4; }
rm -rf out/full out/night 2>/dev/null
nohup env CITY=copenhagen NOCOVER=1 bash run.sh full > /workspace/city3d/full.log 2>&1 &
sleep 2; echo "lanciato, pid $!"
EOS
bash /workspace/go_cph.sh
```

## Banner (dopo 3-8 min)
```
cd /workspace/city3d && grep -E "VERSIONE|fotogrammi|uso:|restore|reclaim|filtra|changed|MANCANO|STOP|rror" full.log | cut -c1-200
```
Deve mostrare: `VERSIONE: <hash> ... | schedule_copenhagen: 660 s, lens 32.0`; `fotogrammi 15840, notte dal fotogramma 15481, nomi %05d`; `uso: OPTIX`; `[restore] reclaim.json rimosso`; `changed 248 delayed 248 dropped 0`; `[filtra] edifici 131938 -> 131817`. Errore o riga mancante: fermare e mandare la riga in chat.

## Avanzamento (una riga ogni 60 s)
```
cd /workspace/city3d; while :; do D=$(ls out/full 2>/dev/null|grep -c jpg); R=$(find out/full -name '*.jpg' -mmin -5 2>/dev/null|wc -l); echo "$(date +%H:%M) $D/15721 ultimi5min $R ETA_min $(( R>0 ? (15721-D)*5/R : -1 ))"; sleep 60; done
```
`-1` = scena in costruzione (30-60 min). Poi la notte: `out/night` (240 fotogrammi, seconda scena).

## Si chiude il pod SOLO quando
1. `full.log` finisce con `=== FINITO` senza errori.
2. `cd /workspace/city3d/out && ls -l copenhagen_full.mp4 years.json && ffprobe -v error -show_entries format=duration -of csv=p=0 copenhagen_full.mp4` (attesi ~660 s, 15.840 fotogrammi).
3. Scaricati `copenhagen_full.mp4` e `years.json` (Jupyter, city3d/out) con dimensioni uguali a `ls -l`.
4. Solo allora Terminate (non Stop).

## Dopo il render (chat/agente, in locale)
`cp years.json montaggio/years_copenhagen.json; python -m kit montaggio copenhagen --A waking.mp3 --B monument.mp3 --overlay`; tempi musica con `sfx_kit`; versione LIGHT spezzata e controllo dei fotogrammi; poi consegna completa.
