#!/bin/bash
# Termopili Short: render 1080x1920, 24 fps, fotogrammi 0..1504 (62,7 s), overlay, mp4 con voce. Riprendibile.
# Di solito lo lancia run_termopili.sh. Uso diretto: PY=... DEVICE=OPTIX ./render_pod.sh [JOBS] [DA] [A]
cd "$(dirname "$0")"
PY=${PY:-python3}; JOBS=${1:-3}; A0=${2:-0}; A1=${3:-1504}; SPP=${SPP:-24}; RES=${RES:-"1080 1920"}
export DATA=$PWD/data/ FONTS=$PWD/fonts/ THREADS=$(( $(nproc) / JOBS > 0 ? $(nproc) / JOBS : 1 ))
[ -s data/satellite_z14.jpg ] || $PY prep_data.py || { echo 'ERRORE: dati non scaricati, render non lanciato.'; exit 1; }
mkdir -p frames comp
export PY SPP RES
seq $A0 $A1 | xargs -P $JOBS -I{} sh -c 'f=$(printf %04d {}); s=$($PY -c "print({}/24)"); [ -s comp/$f.jpg ] && exit 0; [ -s frames/$f.png ] || $PY thermo.py $s frames/$f.png $RES $SPP > frames/$f.log 2>&1 || { echo "ERRORE fotogramma $f:"; tail -3 frames/$f.log; exit 255; }; $PY overlay.py frames/$f.png $s comp/$f.jpg && echo "$f ok"'
N=$(ls comp/*.jpg 2>/dev/null | wc -l); echo "fotogrammi pronti: $N"
if [ "$A0" = 0 ] && [ "$A1" = 1504 ] && [ "$N" -ge 1505 ]; then
  ffmpeg -y -loglevel error -framerate 24 -i comp/%04d.jpg -i audio/termopili_voce_62s.mp3 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k /workspace/termopili_short.mp4 && echo "FATTO: /workspace/termopili_short.mp4"
fi
