#!/bin/bash
# Kit Year Built: unione finale video 3D + overlay trasparente + audio.
# Uso:  bash montaggio/monta_kit.sh <slug> [long|short] [cartella]     (cartella: dove stanno i file, default <repo>/out)
#   long : <slug>_full.mp4 + <slug>_overlay.webm + <slug>_audio.m4a            -> <slug>_finale.mp4
#   short: <slug>_full.mp4 + <slug>_short_overlay.webm + <slug>_short_audio.m4a -> <slug>_short_finale.mp4
#          (tutto il video da short.a a short.b accelerato, ultimo fotogramma fermo 1,5 s, 16:9 su copia sfocata; valori da public/kit_<slug>.json)
# Colore: CONTRAST (default 1.03) e SAT (default 1.08). Roma usava 1.04 / 1.10 (render gia' saturo). Serve ffmpeg.
set -e
SLUG=${1:?uso: monta_kit.sh <slug> [long|short] [cartella]}; MODE=${2:-long}
HERE=$(cd "$(dirname "$0")" && pwd); D=${3:-$(dirname "$HERE")/out}; cd "$D"
FF=$(command -v ffmpeg || ls /opt/pw-browsers/ffmpeg-*/ffmpeg-linux | head -1)
EQ="eq=contrast=${CONTRAST:-1.03}:saturation=${SAT:-1.08}"
if [ "$MODE" = short ]; then
  CFG=$HERE/public/kit_$SLUG.json
  read A B N < <(node -p "const s=require('$CFG').short; s.a+' '+s.b+' '+s.n")
  DUR=$(node -p "$N/24"); SP=$(node -p "(($DUR-1.5)/($B-$A)).toFixed(5)")
  for f in ${SLUG}_full.mp4 ${SLUG}_short_overlay.webm ${SLUG}_short_audio.m4a; do [ -s $f ] || { echo "manca $D/$f"; exit 1; }; done
  $FF -y -ss $A -t $(node -p "$B-$A") -i ${SLUG}_full.mp4 -c:v libvpx-vp9 -i ${SLUG}_short_overlay.webm -i ${SLUG}_short_audio.m4a -filter_complex "[0:v]setpts=PTS*$SP,fps=24,tpad=stop_mode=clone:stop_duration=1.5,$EQ,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t $DUR -movflags +faststart ${SLUG}_short_finale.mp4
  echo "FATTO: $D/${SLUG}_short_finale.mp4"
else
  for f in ${SLUG}_full.mp4 ${SLUG}_overlay.webm ${SLUG}_audio.m4a; do [ -s $f ] || { echo "manca $D/$f"; exit 1; }; done
  $FF -y -i ${SLUG}_full.mp4 -c:v libvpx-vp9 -i ${SLUG}_overlay.webm -i ${SLUG}_audio.m4a -filter_complex "[0:v]$EQ[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart ${SLUG}_finale.mp4
  echo "FATTO: $D/${SLUG}_finale.mp4 (controlla apertura 0:00-0:14, prime soste, taglio musicale, finale)"
fi
