#!/usr/bin/env bash
# Solo download dei dati di New York (niente Blender, niente GPU): poi si scarica dati_nyc.tgz da Jupyter.
set -e
mkdir -p /workspace && cd /workspace/city3d
python3 -m pip install -q requests shapely pyshp 2>/dev/null || python3 -m pip install -q --break-system-packages requests shapely pyshp
python3 fetch_nyc.py data
tar czf /workspace/dati_nyc.tgz data/*.json data/*.ok
ls -lh /workspace/dati_nyc.tgz
echo "FATTO: scarica dati_nyc.tgz da Jupyter (cartella principale), poi TERMINA il Pod."
