#!/usr/bin/env bash
# Solo dati olandesi (niente Blender, niente GPU: basta un pod CPU). Scarica il 3DBAG (747 MB), ritaglia la citta',
# crea /workspace/dati_<citta>.tgz da scaricare da Jupyter e caricare in chat. Poi TERMINARE il pod.
# Uso:  cd /workspace && git clone https://github.com/doctail/city3d && CITY=rotterdam bash city3d/data_nl.sh
set -e
CITY=${CITY:-rotterdam}
mkdir -p /workspace && cd /workspace/city3d
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v $c >/dev/null 2>&1 && $c -m pip --version >/dev/null 2>&1; then PY=$c; break; fi
done
[ -z "$PY" ] && { echo "Nessun Python con pip trovato"; exit 1; }
echo "uso $PY"
$PY -m pip install -q requests shapely pyproj pyarrow numpy 2>/dev/null || $PY -m pip install -q --break-system-packages requests shapely pyproj pyarrow numpy
$PY fetch_nl.py data_$CITY city_$CITY.json
tar czf /workspace/dati_$CITY.tgz data_$CITY/*.json data_$CITY/*.ok
ls -lh /workspace/dati_$CITY.tgz
echo "FATTO: scarica dati_$CITY.tgz da Jupyter (cartella principale), caricalo in chat, poi TERMINA il Pod."
