#!/usr/bin/env bash
# Costantinopoli 1453 Short sul pod RunPod (GPU RTX): installa Blender, controlla la GPU, scarica i dati, renderizza 1555 fotogrammi, fa l'mp4 con la voce.
# Uscita: /workspace/costantinopoli_short.mp4    Log: /workspace/costantinopoli.log    Riprendibile: rilanciando salta i fotogrammi fatti.
# Prova locale senza GPU: ALLOW_CPU=1 BL=/tmp/bl RES="270 480" SPP=4 bash run_cpl.sh 2 700 701
set -e
cd "$(dirname "$0")"
T0=$(date +%s); step(){ echo; echo "=== $1  ($(( $(date +%s) - T0 ))s) ==="; }
step "1/4 pacchetti di sistema"
if command -v apt-get >/dev/null && [ "$(id -u)" = 0 ] && ! command -v ffmpeg >/dev/null; then apt-get update -qq >/dev/null; DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libxxf86vm1 libxfixes3 libxext6 >/dev/null || true; fi
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true
step "2/4 Blender (bpy) in Python 3.13"
BL=${BL:-/workspace/bl}
python3 -m pip install -q uv 2>/dev/null || python3 -m pip install -q --break-system-packages uv
[ -x $BL/bin/python ] || python3 -m uv venv -q -p 3.13 $BL
python3 -m uv pip install -q -p $BL/bin/python bpy==5.2.2 tifffile imagecodecs numpy pillow scipy
export PY=$BL/bin/python
step "3/4 GPU"
DEVICE=$($PY ../../gputest.py | tee /dev/stderr | grep DEVICE= | cut -d= -f2)
[ -n "$ALLOW_CPU" ] && DEVICE=CPU   # solo per la prova locale
if [ "$DEVICE" = "CPU" ] && [ -z "$ALLOW_CPU" ]; then echo "ERRORE: nessuna GPU funzionante. Termina il pod e aprine un altro (RTX)."; exit 3; fi
export DEVICE
step "4/4 render (i dati si scaricano al primo giro)"
bash render_pod.sh "${1:-3}" "${2:-0}" "${3:-1554}"
step "fine"
