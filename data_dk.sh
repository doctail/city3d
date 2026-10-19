#!/usr/bin/env bash
# Solo dati danesi (niente Blender, niente GPU: basta un pod CPU, ~20-30 min). Scarica:
#   - BBR INSPIRE (DK_INSPIRE_BBR.zip, ~800 MB, Dataforsyningen, senza account)
#   - estratto OSM della Danimarca (Geofabrik, ~450 MB)
# ritaglia Copenaghen e crea /workspace/dati_<citta>.tgz GREZZO da scaricare da Jupyter e caricare in chat. Poi TERMINARE il pod.
# Uso:  cd /workspace && git clone https://github.com/doctail/city3d && CITY=copenhagen bash city3d/data_dk.sh
set -e
CITY=${CITY:-copenhagen}
cd /workspace/city3d
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v $c >/dev/null 2>&1 && $c -m pip --version >/dev/null 2>&1; then PY=$c; break; fi
done
[ -z "$PY" ] && { echo "Nessun Python con pip trovato"; exit 1; }
echo "uso $PY"
PKG="requests shapely pyproj numpy pandas geopandas pyogrio osmium"
$PY -m pip install -q $PKG 2>/dev/null || $PY -m pip install -q --break-system-packages $PKG
cfg() { $PY -c "import json;print(json.load(open('city_$CITY.json'))['$1'])"; }
BBR_URL=$(cfg bbr_zip); PBF_URL=$(cfg osm_pbf)
BBR=/workspace/DK_INSPIRE_BBR.zip; PBF=/workspace/$(basename $PBF_URL)
OUT=/workspace/raw_$CITY; mkdir -p $OUT

# i due download in parallelo
[ -s $BBR ] || ( echo "scarico BBR"; curl -fL --retry 3 -A "Mozilla/5.0 city3d" -o $BBR.part "$BBR_URL" && mv $BBR.part $BBR ) &
[ -s $PBF ] || ( echo "scarico OSM"; curl -fL --retry 3 -o $PBF.part "$PBF_URL" && mv $PBF.part $PBF ) &
wait
ls -lh $BBR $PBF
# controllo: se il server ha restituito una pagina HTML invece dello zip, fermati e dillo
if ! unzip -tq $BBR >/dev/null 2>&1; then
  echo "ERRORE: $BBR non e' uno zip valido. Primi byte:"; head -c 400 $BBR; echo; exit 1
fi

$PY fetch_dk_raw.py $BBR city_$CITY.json $OUT/bbr.geojson
$PY osm_dk_raw.py $PBF city_$CITY.json $OUT/osm
cp city_$CITY.json $OUT/
tar czf /workspace/dati_$CITY.tgz -C /workspace raw_$CITY
ls -lh /workspace/dati_$CITY.tgz
echo "FATTO: scarica dati_$CITY.tgz da Jupyter (cartella principale), caricalo in chat, poi TERMINA il Pod."
