#!/usr/bin/env bash
# Sfondo lontano vero (rilievo 40 km, copertura del suolo, urbanizzato per epoca) per una o piu' citta'. Pod CPU, ~10 min a citta'.
# Uso:  cd /workspace && git clone https://github.com/doctail/city3d && cd city3d && CITIES="parigi" bash far_data.sh
# Esce /workspace/far_<citta>.tgz (npz + tile del rilievo) da scaricare da Jupyter e caricare in chat. Poi TERMINARE il pod.
set -e
cd "$(dirname "$0")"
for C in ${CITIES:-parigi}; do
  OUT=/workspace/far_$C
  python3 tools/fetch_far.py city_$C.json $OUT 40
  tar czf /workspace/far_$C.tgz -C $OUT far_$C.npz $(cd $OUT && ls far_tmp/Copernicus_*.tif)
  ls -lh /workspace/far_$C.tgz
done
echo "FATTO: scarica /workspace/far_*.tgz e TERMINA il pod"
