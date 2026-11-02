#!/usr/bin/env bash
# Roma, dati grezzi (pod CPU, niente GPU, ~15-25 min). Scarica e ritaglia:
#   - OSM Italia centro (Geofabrik): edifici, strade, acqua, parchi entro 12 km da Piazza Venezia
#   - rilievo Copernicus + copertura del suolo (tools/fetch_far.py, come Parigi)
#   - ISTAT 2011: sezioni di censimento del Lazio + periodo di costruzione degli edifici (facoltativo: se fallisce si va avanti)
# Uso:  cd /workspace && git clone https://github.com/doctail/city3d && bash city3d/data_roma.sh
# Esce /workspace/dati_roma.tgz da scaricare da Jupyter e caricare in chat. Poi TERMINARE il pod.
set -e
CITY=roma
cd /workspace/city3d
PY=python3
PKG="requests shapely pyproj numpy osmium rasterio"
$PY -m pip install -q $PKG 2>/dev/null || $PY -m pip install -q --break-system-packages $PKG
cfg() { $PY -c "import json;print(json.load(open('city_$CITY.json'))['$1'])"; }
PBF_URL=$(cfg osm_pbf); PBF=/workspace/$(basename $PBF_URL)
OUT=/workspace/raw_$CITY; mkdir -p $OUT
[ -s $PBF ] || ( echo "scarico OSM centro Italia"; curl -fL --retry 3 -o $PBF.part "$PBF_URL" && mv $PBF.part $PBF ) &
( curl -fL --retry 2 -A "Mozilla/5.0 city3d" -o $OUT/istat_basi.zip "$(cfg istat_basi)" && unzip -tq $OUT/istat_basi.zip && echo "ISTAT basi ok" || { echo "AVVISO: ISTAT basi non scaricate"; rm -f $OUT/istat_basi.zip; } ) &
( curl -fL --retry 2 -A "Mozilla/5.0 city3d" -o $OUT/istat_dati.zip "$(cfg istat_dati)" && unzip -tq $OUT/istat_dati.zip && echo "ISTAT dati ok" || { echo "AVVISO: ISTAT dati non scaricati"; rm -f $OUT/istat_dati.zip; } ) &
wait
ls -lh $PBF
$PY osm_dk_raw.py $PBF city_$CITY.json $OUT/osm
SKIP_DEM= $PY tools/fetch_far.py city_$CITY.json /workspace/far_$CITY 40 2>&1 | tail -5 || echo "AVVISO: rilievo non completo"
cp -r /workspace/far_$CITY $OUT/ 2>/dev/null || true
cp city_$CITY.json $OUT/
tar czf /workspace/dati_$CITY.tgz -C /workspace raw_$CITY
ls -lh /workspace/dati_$CITY.tgz
echo "FATTO: scarica dati_$CITY.tgz da Jupyter (cartella principale), caricalo in chat, poi TERMINA il Pod."
