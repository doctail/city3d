#!/usr/bin/env bash
# Parigi: i dati si preparano IN CHAT (servono i dati grezzi in raw_parigi/, non su GitHub). Ordine:
#   prep_parigi.py -> hist_parigi.py -> roads_parigi.py -> landmarks_parigi.py -> bridges_parigi.py -> dem_parigi.py -> regia_parigi.py
# Poi questo script comprime i file pronti in data_parigi_src/ (run.sh li decomprime in data_parigi/ sul pod).
set -e
cd "$(dirname "$0")"
mkdir -p data_parigi_src
for f in buildings.json hist.json roads.json landmarks.json landphases.json land.json parks.json wall_p.json urban_grid.npz dem.npz; do
  [ -s data_parigi/$f ] || { echo "MANCA data_parigi/$f"; exit 1; }
  gzip -9 -c data_parigi/$f > data_parigi_src/$f.gz
done
ls -lh data_parigi_src/
du -sh data_parigi_src/
