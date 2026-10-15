#!/usr/bin/env bash
# Acqua e parchi da OpenStreetMap (Overpass) scaricati dal pod: overpass-turbo dal browser spesso rifiuta le richieste grandi.
# Uso:  cd /workspace/city3d && git pull && CITY=rotterdam bash osm_nl.sh     -> /workspace/osm_<citta>.json (da scaricare da Jupyter)
CITY=${CITY:-rotterdam}; Q=osm_query_$CITY.txt; OUT=/workspace/osm_$CITY.json
for S in https://overpass-api.de/api/interpreter https://overpass.kumi.systems/api/interpreter https://overpass.private.coffee/api/interpreter; do
  echo "provo $S"
  if curl -sS -m 300 --data-urlencode "data@$Q" "$S" -o $OUT && head -c 200 $OUT | grep -q '"elements"'; then
    ls -lh $OUT; echo "FATTO: scarica osm_$CITY.json da Jupyter (cartella principale) e caricalo in chat."; exit 0
  fi
  echo "  non riuscito, provo il prossimo"; sleep 5
done
echo "Nessun server Overpass ha risposto: manda lo screenshot."; exit 1
