# Pittsburgh: GO POD (26/11/2026). GO del proprietario ricevuto in chat il 26/11. Un solo messaggio da incollare.

Commit di render: `2888a02` (main). Lista pre-GO verificata dalla chat sui file: parity dati 0 differenze (rieseguita), regia_check 0/0, gate 0 FAIL, water_clip/bridge_fix attivi in `story.json`/`city_pittsburgh.json`, canale 'Ledger of Cities', foglio 6 fotogrammi visto e approvato dal proprietario.
Schedule committata: 617,6 s, 14.822 fotogrammi (nomi %05d), niente notte, 179.756 edifici al 2026, drone 0 voli lenti.

## Costo (base: Marsiglia/Lione, NON misurato su Pittsburgh sul pod) [Guessing]
- 0,8-1,2 s a fotogramma x 14.822 = 3,3-4,9 h + ~55 min di scena = 4-6 h, circa 2-3 EUR a 0,5 EUR/h (A40, prezzo vero all'accensione). NYC aveva misurato 4-5 s per 959K alberi: se i primi fotogrammi superano ~3 s, fermare e scrivere in chat.
- Copertine: NOCOVER=1 (si estraggono dal video in locale: 1754 forti, 1936 piena, 2026).

## Incolla nel terminale del pod (A40, 30 GB)
```
cat > /workspace/go_pgh.sh <<'EOS'
cd /workspace
echo "== GPU"; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
CU=$(python3 -c "import ctypes;print(ctypes.CDLL('libcuda.so.1').cuInit(0))"); echo "cuInit = $CU"
nvidia-smi --query-gpu=name --format=csv,noheader | grep -q A40 && [ "$CU" = "0" ] || { echo "STOP: serve A40 con cuInit = 0. Termina il pod e cambia regione/host."; exit 2; }
[ -d city3d ] || git clone -q https://github.com/doctail/city3d
cd city3d && git fetch -q origin && git checkout -q main && git pull -q --ff-only
git log -1 --oneline
git merge-base --is-ancestor 2888a02 HEAD || { echo "STOP: manca il commit 2888a02 (codice vecchio)."; exit 3; }
git diff --quiet 2888a02 HEAD -- run.sh build_render.py kit schedule_pittsburgh.json city_pittsburgh.json cities/pittsburgh/story.json hist_pittsburgh.py data_pittsburgh_src || { echo "STOP: i file di render sono cambiati dopo il GO. Chiedere in chat."; exit 4; }
rm -rf out/full 2>/dev/null
nohup env CITY=pittsburgh NOCOVER=1 bash run.sh full > /workspace/city3d/full.log 2>&1 &
sleep 2; echo "lanciato, pid $!"
EOS
bash /workspace/go_pgh.sh
```

## Banner (dopo 3-8 min)
```
cd /workspace/city3d && grep -E "VERSIONE|fotogrammi|uso:|hist_kit|water_clip|MANCANO|STOP|rror" full.log | cut -c1-200
```
Deve mostrare: `VERSIONE: <hash> ... | schedule_pittsburgh: 618 s, lens 32.0`; `fotogrammi 14822, notte dal fotogramma 0, nomi %05d`; `uso: OPTIX`. Errore o riga mancante: fermare e mandare la riga in chat.

## Avanzamento (una riga ogni 60 s)
```
cd /workspace/city3d; while :; do D=$(ls out/full 2>/dev/null|grep -c jpg); R=$(find out/full -name '*.jpg' -mmin -5 2>/dev/null|wc -l); echo "$(date +%H:%M) $D/14822 ultimi5min $R ETA_min $(( R>0 ? (14822-D)*5/R : -1 ))"; sleep 60; done
```
`-1` = ancora in costruzione scena (primi ~55 min, normale).

## Si chiude il pod SOLO quando
1. `full.log` finisce con `=== FINITO` senza errori.
2. `cd /workspace/city3d/out && ls -l pittsburgh_full.mp4 years.json && ffprobe -v error -show_entries format=duration -of csv=p=0 pittsburgh_full.mp4` (attesi ~617,6 s, 14.822 fotogrammi).
3. Scaricati `pittsburgh_full.mp4` e `years.json` (Jupyter, city3d/out) con dimensioni uguali a `ls -l`.
4. Solo allora Terminate (non Stop).

## Dopo il render (chat/agente, in locale)
Il proprietario carica in chat `years.json` e le due musiche (A "Waking to Reality", B "Monument"). Poi: `cp years.json montaggio/years_pittsburgh.json; python -m kit montaggio pittsburgh --A waking.mp3 --B monument.mp3 --overlay`; ricalcolare i tempi musica con `sfx_kit`; versione LIGHT spezzata (regola 26/11) e controllo dei fotogrammi prima dell'ok; poi consegna completa (vedi CONSEGNA_YOUTUBE.md).
