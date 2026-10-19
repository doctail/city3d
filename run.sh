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
NF=$($PY -c "import json;print(int(json.load(open('$SCHED'))['duration']*24))" 2>/dev/null || echo 7839)
NT=$($PY -c "import json;d=json.load(open('$SCHED'));print(int(d['night_t']*24)+1 if 'night_t' in d else 0)" 2>/dev/null || echo 0)
SCHED_N=${SCHED%.json}_night.json
PAT=%04d; [ "$NF" -gt 9999 ] && PAT=%05d
echo "fotogrammi $NF, notte dal fotogramma $NT, nomi $PAT"
step "3b/5 prova GPU"
nvidia-smi --query-gpu=name,driver_version,compute_mode --format=csv,noheader || true
echo "caps=$NVIDIA_DRIVER_CAPABILITIES"
DEV=$($PY gputest.py | tee /dev/stderr | grep DEVICE= | cut -d= -f2)
echo "uso: $DEV"
[ "$DEV" = "CPU" ] && { echo "NESSUNA GPU FUNZIONANTE: mi fermo. Manda lo screenshot."; exit 1; }

cover(){   # copertina: camera e anni da city_<citta>.json -> "cover"; 1920x1080, 32 campioni, ~3 min
  CV=$($PY -c "import json;c=json.load(open('city_$CITY.json')).get('cover');print(' '.join(map(str,c['cam'])),c.get('lens',40),' '.join(map(str,c['years']))) if c else print('')")
  [ -z "$CV" ] && { echo "nessuna camera 'cover' in city_$CITY.json"; return; }
  set -- $CV; CAM="$1 $2 $3 $4 $5 $6"; LENS=$7; shift 7
  for Y in "$@"; do
    rm -rf out/cover_$Y
    $PY build_render.py -- $D out/cover_$Y --frames 1 $NF --only $(( NF - 200 )) --year $Y --cam $CAM --lens $LENS --res 1920 1080 --samples 32 --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "fotogramma|rror"
    cp out/cover_$Y/$(printf $PAT $(( NF - 200 ))).jpg out/${CITY}_cover_$Y.jpg
  done; ls -lh out/${CITY}_cover_*.jpg
}
light(){   # versione leggera da caricare in chat (~55 MB): 960x540, bitrate fisso
  ffmpeg -loglevel error -y -i "$1" -vf scale=960:-2 -c:v libx264 -preset fast -b:v 1300k -maxrate 1400k -bufsize 2800k -pix_fmt yuv420p -an "$2"; ls -lh "$2"
}
MODE=${1:-}
if [ -z "$MODE" ]; then
  echo "Manca la modalita'. Uso:  CITY=madrid bash run.sh preview | full | shorts | cover | profile   (test = vecchia prova solo New York)"; exit 1
fi
if [ "$MODE" = "test" ] && [ "$CITY" != "nyc" ]; then echo "La modalita' test vale solo per New York: usa preview"; exit 1; fi
if [ "$MODE" = "preview" ]; then
  step "4/5 ANTEPRIMA: 2 fotogrammi al secondo, 960x540, durata reale (~6-8 min)"
  rm -rf out/prev out/prevn out/prevmix
  LASTD=$NF; [ "$NT" -gt 0 ] && LASTD=$(( NT + 240 ))
  $PY build_render.py -- $D out/prev --frames 1 $LASTD --step 12 --res 960 540 --samples 8 --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "\[build\]|Error|Traceback|rror"
  if [ "$NT" -gt 0 ]; then   # notte: stessa numerazione, passata separata (materiali notturni fissi)
    F0N=$(( ( (NT + 120 - 1 + 11) / 12 ) * 12 + 1 ))
    $PY build_render.py -- $D out/prevn --night --frames $F0N $NF --step 12 --res 960 540 --samples 8 --device $DEV --schedule $SCHED_N $CARGS 2>&1 | grep -E "FATTO|Error|Traceback|rror"
  fi
  PV=out/prev
  if [ "$NT" -gt 0 ]; then uv pip install -q -p $PY opencv-python-headless numpy; $PY dusk.py out/prev out/prevn out/prevmix $NT $NF 12; PV=out/prevmix; fi
  ffmpeg -loglevel error -y -framerate 2 -pattern_type glob -i "$PV/*.jpg" -c:v libx264 -crf 20 -pix_fmt yuv420p out/${CITY}_preview.mp4
  ls -lh out/${CITY}_preview.mp4
  [ -f tools/movimento.py ] && uv pip install -q -p $PY opencv-python-headless numpy; [ -f tools/movimento.py ] && $PY tools/movimento.py out/${CITY}_preview.mp4 out/${CITY}_movimento.json 2>&1 | tail -5
  step "FINITO"; echo "Scarica city3d/out/${CITY}_preview.mp4. NON terminare il Pod: se va bene lanciamo il completo."; exit 0
fi
if [ "$MODE" = "profile" ]; then
  step "PROFILO: 12 fotogrammi per variante (dove va il tempo per fotogramma)"
  for V in "--denoiser optix" "--denoiser oidn" "--denoiser none" "--denoiser optix --samples 2" "--denoiser optix --res 960 540"; do
    rm -rf /tmp/prof; echo "--- variante: $V"
    PF=$(( NF * 7 / 10 )); $PY build_render.py -- $D /tmp/prof $V --frames $PF $(( PF + 11 )) --res 1920 1080 --samples 8 --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "fotogramma|denoiser|rror" | awk '/fotogramma/{n++; if(n>2){split($4,t,"s"); s+=t[1]; k++}} !/fotogramma/{print} END{if(k) printf "    media senza i primi 2: %.2f s/fotogramma\n", s/k}' 
  done
  if [ "$NT" -gt 0 ]; then rm -rf /tmp/prof; echo "--- notte (optix)"
    $PY build_render.py -- $D /tmp/prof --night --denoiser optix --frames $(( NT + 200 )) $(( NT + 211 )) --res 1920 1080 --samples 8 --device $DEV --schedule $SCHED_N $CARGS 2>&1 | grep -E "fotogramma|rror" | awk '/fotogramma/{n++; if(n>2){split($4,t,"s"); s+=t[1]; k++}} END{if(k) printf "    media senza i primi 2: %.2f s/fotogramma\n", s/k}'
  fi
  step "FINITO profilo: manda lo screenshot"; exit 0
fi
if [ "$MODE" = "cover" ]; then step "COPERTINA"; cover; step "FINITO: scarica out/${CITY}_cover_*.jpg"; exit 0; fi
if [ "$MODE" = "shorts" ]; then
  step "SHORTS verticali 1080x1920"
  # voci in city_<citta>.json -> "shorts": [nome, primo, ultimo, passo, regia?, bin?]
  #   senza regia: tratto del video lungo (stessa camera, fotogrammi saltati = accelerazione)
  #   con regia: Short con camera e anni propri (schedule_<citta>_short<nome>.json), fotogrammi 1..N
  SH=$($PY -c "
import json
c=json.load(open('city_$CITY.json')) if '$CITY'!='nyc' else {}
L=c.get('shorts',[[1,133,7839,7],[2,5593,7839,2],[3,133,2400,2]])
print(';'.join(' '.join(map(str,(x+['-','-'])[:6])) for x in L))")
  IFS=';' read -ra SHS <<< "$SH"; NAMES=""
  for S in "${SHS[@]}"; do set -- $S; NAMES="$NAMES $1"
    SS=$SCHED; [ "$5" != "-" ] && SS=$5; BN=""; [ "$6" != "-" ] && BN="--bin $6"
    mkdir -p out/short$1; find out/short$1 -name "*.jpg" -size 0 -delete
    echo "--- short $1: fotogrammi $2-$3 passo $4, regia $SS $BN"
    $PY build_render.py -- $D out/short$1 --frames $2 $3 --step $4 --res 1080 1920 --samples ${SAMPLES:-8} --device $DEV --schedule $SS $BN $CARGS 2>&1 | grep -E "FATTO|Error|Traceback|rror"
  done
  for n in $NAMES; do ffmpeg -loglevel error -y -framerate 24 -pattern_type glob -i "out/short$n/*.jpg" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p out/${CITY}_short$n.mp4; done
  [ "${SHORTS_LIGHT:-1}" = "1" ] && for n in $NAMES; do ffmpeg -loglevel error -y -i out/${CITY}_short$n.mp4 -c:v libx264 -preset fast -b:v 4000k -maxrate 4500k -bufsize 9000k -pix_fmt yuv420p out/${CITY}_short${n}_light.mp4; done   # ~15 MB l'uno, per la chat
  ls -lh out/${CITY}_short*.mp4
  step "FINITO shorts: scarica out/${CITY}_short*.mp4 (i _light sono per la chat)"; exit 0
fi
if [ "$MODE" = "full" ]; then
  step "4/5 render VIDEO COMPLETO ($NF fotogrammi, riprende da dove si e' fermato)"
  mkdir -p out/full; find out/full \( -name "*.png" -o -name "*.jpg" \) -size 0 -delete
  LASTD=$NF; [ "$NT" -gt 0 ] && LASTD=$(( NT + 240 ))   # giorno fino a 10 s dopo l'inizio della notte (tramonto)
  $PY build_render.py -- $D out/full --frames 1 $LASTD --res 1920 1080 --samples ${SAMPLES:-8} --device $DEV --schedule $SCHED $CARGS 2>&1 | grep -E "\[build\]|Error|Traceback|rror"
  if [ "$NT" -gt 0 ]; then
    step "4b/5 NOTTE (fotogrammi $(( NT + 120 ))-$NF)"; mkdir -p out/night; find out/night -name "*.jpg" -size 0 -delete
    $PY build_render.py -- $D out/night --night --frames $(( NT + 120 )) $NF --res 1920 1080 --samples ${SAMPLES:-8} --device $DEV --schedule $SCHED_N $CARGS 2>&1 | grep -E "\[build\]|Error|Traceback|rror"
  fi
  step "5/5 video"
  bash pack.sh out/full   # eventuali png di vecchie partenze -> jpg
  if [ "$NT" -gt 0 ]; then   # tramonto (5 s) + crepuscolo in dissolvenza (5 s) dal fotogramma NT, poi notte: dusk.py
    uv pip install -q -p $PY opencv-python-headless numpy; rm -rf out/mix; $PY dusk.py out/full out/night out/mix $NT $NF
    ffmpeg -loglevel error -y -framerate 24 -i out/mix/$PAT.jpg -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p out/${CITY}_full.mp4
  else
    ffmpeg -loglevel error -y -framerate 24 -i out/full/$PAT.jpg -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p out/${CITY}_full.mp4
  fi
  cp out/full/years.json out/years.json
  ls -lh out/${CITY}_full.mp4
  step "5b/5 versione leggera per la chat"; light out/${CITY}_full.mp4 out/${CITY}_light.mp4
  [ "${NOCOVER:-0}" = "1" ] || { step "5c/5 copertina"; cover; }
  step "FINITO"; echo "Scarica da city3d/out: ${CITY}_full.mp4 (per te), ${CITY}_light.mp4 + years.json + ${CITY}_cover_*.jpg (da caricare in chat)."; exit 0
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
