#!/bin/bash
# Costantinopoli 1453: render 1080x1920, 24 fps, fotogrammi 0..1554 (64,8 s), infografica, mp4 con voce + effetti. Riprendibile.
cd "$(dirname "$0")"
PY=${PY:-python3}; JOBS=${1:-3}; A0=${2:-0}; A1=${3:-1554}; SPP=${SPP:-32}; RES=${RES:-"1080 1920"}
export DATA=$PWD/data/ THREADS=$(( $(nproc) / JOBS > 0 ? $(nproc) / JOBS : 1 ))
[ -s data/satellite_z14.jpg ] || $PY prep_data.py || { echo 'ERRORE: dati non scaricati, render non lanciato.'; exit 1; }
[ -s data/dem_smooth.npy ] || $PY cpl.py 0 /tmp/warm.png 64 114 1 > /tmp/warm.log 2>&1 || { echo 'ERRORE nella preparazione:'; tail -5 /tmp/warm.log; exit 1; }
mkdir -p frames comp
export PY SPP RES
seq $A0 $A1 | xargs -P $JOBS -I{} sh -c 'f=$(printf %04d {}); s=$($PY -c "print({}/24)"); [ -s comp/$f.jpg ] && exit 0; [ -s frames/$f.png ] || $PY cpl.py $s frames/$f.png $RES $SPP > frames/$f.log 2>&1 || { echo "ERRORE fotogramma $f:"; tail -3 frames/$f.log; exit 255; }; $PY overlay.py frames/$f.png $s comp/$f.jpg && echo "$f ok"'
N=$(ls comp/*.jpg 2>/dev/null | wc -l); echo "fotogrammi pronti: $N"
if [ "$A0" = 0 ] && [ "$A1" = 1554 ] && [ "$N" -ge 1555 ]; then
  ffmpeg -y -loglevel error -framerate 24 -i comp/%04d.jpg -i audio/cpl_mix.m4a -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest /workspace/costantinopoli_short.mp4 && echo "FATTO: /workspace/costantinopoli_short.mp4"
fi
