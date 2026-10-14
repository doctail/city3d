#!/usr/bin/env bash
# Converte i fotogrammi PNG in JPG (qualita' 95) e cancella i PNG: libera spazio su disco. Uso: bash pack.sh out/full
D=${1:-out/full}; n=0
for p in "$D"/*.png; do
  [ -e "$p" ] || continue
  j="${p%.png}.jpg"; ffmpeg -loglevel error -y -i "$p" -q:v 2 "$j" && [ -s "$j" ] && rm "$p" && n=$((n+1))
done
echo "convertiti $n png in jpg"; du -sh "$D"
