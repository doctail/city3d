#!/usr/bin/env bash
# Acqua e parchi da OpenStreetMap senza Overpass: estratto della provincia da Geofabrik + filtro locale (osm_pbf.py).
# Uso:  cd /workspace/city3d && git pull && CITY=rotterdam bash osm_nl.sh     -> /workspace/osm_<citta>.json (da scaricare da Jupyter)
set -e
CITY=${CITY:-rotterdam}
PBF_URL=$(python3 -c "import json;print(json.load(open('city_$CITY.json'))['osm_pbf'])")
PBF=/workspace/$(basename $PBF_URL); OUT=/workspace/osm_$CITY.json
python3 -m pip install -q osmium shapely 2>/dev/null || python3 -m pip install -q --break-system-packages osmium shapely
[ -s $PBF ] || { echo "scarico $PBF_URL"; curl -fL --progress-bar -o $PBF.part "$PBF_URL" && mv $PBF.part $PBF; }
ls -lh $PBF
python3 osm_pbf.py $PBF city_$CITY.json $OUT
ls -lh $OUT; echo "FATTO: scarica osm_$CITY.json da Jupyter (cartella principale), caricalo in chat, poi TERMINA il Pod."
