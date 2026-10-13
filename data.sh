#!/usr/bin/env bash
# Solo download dei dati di New York (niente Blender, niente GPU): poi si scarica dati_nyc.tgz da Jupyter.
set -e
mkdir -p /workspace && cd /workspace/city3d
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v $c >/dev/null 2>&1 && $c -m pip --version >/dev/null 2>&1; then PY=$c; break; fi
done
[ -z "$PY" ] && { echo "Nessun Python con pip trovato"; exit 1; }
echo "uso $PY"
$PY -m pip install -q requests shapely pyshp 2>/dev/null || $PY -m pip install -q --break-system-packages requests shapely pyshp
$PY fetch_nyc.py data
tar czf /workspace/dati_nyc.tgz data/*.json data/*.ok
ls -lh /workspace/dati_nyc.tgz
echo "FATTO: scarica dati_nyc.tgz da Jupyter (cartella principale), poi TERMINA il Pod."
