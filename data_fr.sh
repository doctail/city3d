#!/usr/bin/env bash
# Solo dati francesi (niente Blender, niente GPU: basta un pod CPU, ~20-30 min). Scarica in parallelo:
#   - BDNB open data, GeoPackage dei dipartimenti in city_<citta>.json -> bdnb_deps (URL trovati via API data.gouv)
#   - estratto OSM Ile-de-France (Geofabrik, ~300 MB): edifici OSM, acqua, parchi, strade, ponti (osm_dk_raw.py, generico)
#   - DEM Copernicus GLO-30 (tile in dem_tiles)
# Ritaglia e crea /workspace/dati_<citta>.tgz da scaricare da Jupyter e caricare in chat. Poi TERMINARE il pod.
# Stampa SUBITO la copertura per arrondissement (anno valido / totale): se un arrondissement e' sotto il 70%, dirlo a Fabio.
# Uso:  cd /workspace && git clone https://github.com/doctail/city3d && CITY=parigi bash city3d/data_fr.sh
#       URL BDNB a mano (se l'API non li trova):  BDNB_URLS="url1 url2" CITY=parigi bash city3d/data_fr.sh
set -e
CITY=${CITY:-parigi}
cd /workspace/city3d
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v $c >/dev/null 2>&1 && $c -m pip --version >/dev/null 2>&1; then PY=$c; break; fi
done
[ -z "$PY" ] && { echo "Nessun Python con pip trovato"; exit 1; }
PKG="requests shapely pyproj numpy pandas geopandas pyogrio osmium"
$PY -m pip install -q $PKG 2>/dev/null || $PY -m pip install -q --break-system-packages $PKG
cfg() { $PY -c "import json;v=json.load(open('city_$CITY.json'))['$1'];print(' '.join(v) if isinstance(v,list) else v)"; }
PBF_URL=$(cfg osm_pbf); PBF=/workspace/$(basename $PBF_URL)
OUT=/workspace/raw_$CITY; mkdir -p $OUT /workspace/bdnb
URLS=${BDNB_URLS:-$($PY fetch_fr_raw.py urls city_$CITY.json)}
echo "BDNB:"; echo "$URLS"
[ -z "$URLS" ] && { echo "ERRORE: nessun URL BDNB. Cercali su data.gouv.fr (BDNB, GeoPackage per dipartimento) e rilancia con BDNB_URLS=..."; exit 1; }

get() { [ -s "$2" ] || { curl -fL --retry 3 -A "Mozilla/5.0 city3d" -o "$2.part" "$1" && mv "$2.part" "$2"; }; }
get "$PBF_URL" $PBF &
for u in $(cfg dem_tiles); do get "$u" $OUT/$(basename $u) & done
for u in $URLS; do get "$u" /workspace/bdnb/$(basename "${u%%\?*}") & done
wait
ls -lh $PBF $OUT/*.tif /workspace/bdnb/

GPKG=""
for z in /workspace/bdnb/*; do
  case "$z" in
    *.zip) unzip -tq "$z" >/dev/null 2>&1 || { echo "ERRORE: $z non e' uno zip valido:"; head -c 300 "$z"; echo; exit 1; }
           d=/workspace/bdnb/$(basename "$z" .zip); [ -d "$d" ] || unzip -q "$z" -d "$d"
           GPKG="$GPKG $(find "$d" -name '*.gpkg' | tr '\n' ' ')";;
    *.gpkg) GPKG="$GPKG $z";;
  esac
done
echo "GeoPackage: $GPKG"
$PY fetch_fr_raw.py clip city_$CITY.json $OUT $GPKG 2>&1 | tee $OUT/fetch_fr.log
$PY osm_dk_raw.py $PBF city_$CITY.json $OUT/osm 2>&1 | tee $OUT/osm.log
cp city_$CITY.json $OUT/
gzip -f $OUT/osm_*.geojson
tar czf /workspace/dati_$CITY.tgz -C /workspace raw_$CITY
ls -lh /workspace/dati_$CITY.tgz
echo "=== COPERTURA (anche in raw_$CITY/copertura.csv) ==="; grep -E "arr\.|e:" $OUT/fetch_fr.log | tail -22
echo "FATTO: scarica dati_$CITY.tgz da Jupyter (cartella principale), caricalo in chat, poi TERMINA il Pod."
