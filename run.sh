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
uv pip install -q -p /workspace/bl/bin/python bpy==5.2.2 shapely requests pyshp
PY=/workspace/bl/bin/python

cd /workspace/city3d
step "3/5 dati New York"
[ -s data/buildings.json ] || $PY fetch_nyc.py data
$PY hist_nyc.py data

step "3b/5 prova GPU"
nvidia-smi --query-gpu=name,driver_version,compute_mode --format=csv,noheader || true
echo "caps=$NVIDIA_DRIVER_CAPABILITIES"
DEV=$($PY gputest.py | tee /dev/stderr | grep DEVICE= | cut -d= -f2)
echo "uso: $DEV"
[ "$DEV" = "CPU" ] && { echo "NESSUNA GPU FUNZIONANTE: mi fermo. Manda lo screenshot."; exit 1; }

MODE=${1:-test}
if [ "$MODE" = "full" ]; then
  step "4/5 render VIDEO COMPLETO (7839 fotogrammi, riprende da dove si e' fermato)"
  $PY build_render.py -- data out/full --frames 1 7839 --res 1920 1080 --samples 16 --device $DEV --schedule schedule_nyc.json 2>&1 | grep -E "\[build\]|Error|Traceback|rror"
  step "5/5 video"
  ffmpeg -loglevel error -y -framerate 24 -i out/full/%04d.png -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p out/nyc_full.mp4
  cp out/full/years.json out/years.json
  ls -lh out/nyc_full.mp4; step "FINITO"; echo "Scarica city3d/out/nyc_full.mp4 e years.json, poi TERMINA il Pod."; exit 0
fi
step "4/5 render 240 fotogrammi 1920x1080"
rm -rf out/frames
$PY build_render.py -- data out/frames --frames 1 240 --res 1920 1080 --samples 16 --device $DEV 2>&1 | grep -E "\[build\]|Error|Traceback|rror"

step "5/5 video"
ffmpeg -loglevel error -y -framerate 24 -i out/frames/%04d.png -c:v libx264 -crf 17 -pix_fmt yuv420p out/test_nyc.mp4
cp out/frames/0001.png out/primo.png; cp out/frames/0240.png out/ultimo.png
ls -lh out/test_nyc.mp4
step "FINITO"
echo "Scarica /workspace/city3d/out/test_nyc.mp4 (e log.txt) da Jupyter, poi FERMA il Pod (Stop) per non pagare ore inutili."
