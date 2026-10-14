#!/usr/bin/env bash
# Test New York sul Pod RunPod: installa Blender, scarica i dati, renderizza 10 secondi, crea l'mp4.
# Uso (dal terminale web del Pod):  cd /workspace && git clone https://github.com/doctail/city3d && bash city3d/run.sh
set -e
mkdir -p /workspace && cd /workspace
T0=$(date +%s); step(){ echo; echo "=== $1  ($(( $(date +%s) - T0 ))s) ==="; }

step "1/5 pacchetti di sistema"
apt-get update -qq >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libxxf86vm1 libxfixes3 libxext6 >/dev/null
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true

step "2/5 Blender (bpy) in Python 3.13"
pip install -q uv
[ -x /workspace/bl/bin/python ] || uv venv -q -p 3.13 /workspace/bl
uv pip install -q -p /workspace/bl/bin/python bpy==5.2.2 shapely requests pyshp pyproj
PY=/workspace/bl/bin/python

cd /workspace/city3d
CITY=${CITY:-nyc}   # CITY=madrid bash run.sh full
if [ "$CITY" = "nyc" ]; then
  D=data; SCHED=schedule_nyc.json; CARGS=""
  step "3/5 dati New York"
  [ -s data/buildings.json ] || $PY fetch_nyc.py data
  [ -f data/land_v3.ok ] || $PY fetch_nyc.py data --land-only
  $PY hist_nyc.py data
else
  D=data_$CITY; SCHED=schedule_$CITY.json; CARGS="--city city_$CITY.json"
  step "3/5 dati $CITY"
  mkdir -p $D
  if [ -d data_${CITY}_src ]; then for g in data_${CITY}_src/*.gz; do b=$(basename $g .gz); [ -s $D/$b ] || gunzip -c $g > $D/$b; done; echo ok > $D/land_v3.ok; fi   # dati gia' preparati in chat
  if [ "$CITY" = "madrid" ]; then [ -s $D/buildings.json ] || $PY fetch_es.py $D city_$CITY.json $(ls /workspace/*.zip 2>/dev/null | head -1); fi
  $PY hist_$CITY.py $D
fi
step "3b/5 prova GPU"
nvidia-smi --query-gpu=name,driver_version,compute_mode --format=csv,noheader || true
echo "caps=$NVIDIA_DRIVER_CAPABILITIES"
DEV=$($PY gputest.py | tee /dev/stderr | grep DEVICE= | cut -d= -f2)
echo "uso: $DEV"
[ "$DEV" = "CPU" ] && { echo "NESSUNA GPU FUNZIONANTE: mi fermo. Manda lo screenshot."; exit 1; }

MODE=${1:-test}
if [ "$MODE" = "preview" ]; then
  step "4/5 ANTEPRIMA: 2 fotogrammi al secondo, 960x540, durata reale (~6-8 min)"
  rm -rf out/prev
  $PY build_render.py -- $D out/prev --frames 1 7839 --step 12 --res 960 540 --samples 8 --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "\[build\]|Error|Traceback|rror"
  ffmpeg -loglevel error -y -framerate 2 -pattern_type glob -i 'out/prev/*.jpg' -c:v libx264 -crf 20 -pix_fmt yuv420p out/${CITY}_preview.mp4
  ls -lh out/${CITY}_preview.mp4; step "FINITO"; echo "Scarica city3d/out/${CITY}_preview.mp4. NON terminare il Pod: se va bene lanciamo il completo."; exit 0
fi
if [ "$MODE" = "profile" ]; then
  step "PROFILO: 12 fotogrammi per variante (dove va il tempo per fotogramma)"
  for V in "--denoiser optix" "--denoiser oidn" "--denoiser none" "--denoiser optix --samples 2" "--denoiser optix --res 960 540"; do
    rm -rf /tmp/prof; echo "--- variante: $V"
    $PY build_render.py -- $D /tmp/prof $V --frames 3000 3011 --res 1920 1080 --samples 8 --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "fotogramma|denoiser|rror" | awk '/fotogramma/{n++; if(n>2){split($4,t,"s"); s+=t[1]; k++}} !/fotogramma/{print} END{if(k) printf "    media senza i primi 2: %.2f s/fotogramma\n", s/k}' 
  done; step "FINITO profilo: manda lo screenshot"; exit 0
fi
if [ "$MODE" = "shorts" ]; then
  step "SHORTS verticali 1080x1920 (3 tratti, fotogrammi saltati = accelerazione)"
  # tratto: primo ultimo passo  (in fotogrammi del video lungo, 24 fps)
  for S in "1 133 7839 7" "2 5593 7839 2" "3 133 2400 2"; do set -- $S
    mkdir -p out/short$1; find out/short$1 -name "*.jpg" -size 0 -delete
    $PY build_render.py -- $D out/short$1 --frames $2 $3 --step $4 --res 1080 1920 --samples ${SAMPLES:-8} --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "FATTO|Error|Traceback|rror"
  done
  for n in 1 2 3; do ffmpeg -loglevel error -y -framerate 24 -pattern_type glob -i "out/short$n/*.jpg" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p out/${CITY}_short$n.mp4; done
  ls -lh out/${CITY}_short*.mp4
  step "FINITO shorts: scarica out/${CITY}_short1.mp4, _short2.mp4, _short3.mp4"; exit 0
fi
if [ "$MODE" = "full" ]; then
  step "4/5 render VIDEO COMPLETO (7839 fotogrammi, riprende da dove si e' fermato)"
  mkdir -p out/full; find out/full \( -name "*.png" -o -name "*.jpg" \) -size 0 -delete
  $PY build_render.py -- $D out/full --frames 1 7839 --res 1920 1080 --samples ${SAMPLES:-8} --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "\[build\]|Error|Traceback|rror"
  step "5/5 video"
  bash pack.sh out/full   # eventuali png di vecchie partenze -> jpg
  ffmpeg -loglevel error -y -framerate 24 -i out/full/%04d.jpg -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p out/${CITY}_full.mp4
  cp out/full/years.json out/years.json
  ls -lh out/${CITY}_full.mp4; step "FINITO"; echo "Scarica city3d/out/${CITY}_full.mp4 e years.json, poi TERMINA il Pod."; exit 0
fi
step "4/5 render 240 fotogrammi 1920x1080"
rm -rf out/frames
$PY build_render.py -- $D out/frames --frames 1 240 --res 1920 1080 --samples 16 --device $DEV 2>&1 | grep -E "\[build\]|Error|Traceback|rror"

step "5/5 video"
ffmpeg -loglevel error -y -framerate 24 -i out/frames/%04d.png -c:v libx264 -crf 17 -pix_fmt yuv420p out/test_nyc.mp4
cp out/frames/0001.png out/primo.png; cp out/frames/0240.png out/ultimo.png
ls -lh out/test_nyc.mp4
step "FINITO"
echo "Scarica /workspace/city3d/out/test_nyc.mp4 (e log.txt) da Jupyter, poi FERMA il Pod (Stop) per non pagare ore inutili."
