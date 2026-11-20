#!/bin/sh
# NYC: run this AFTER every `python -m kit build nyc` (and after `kit data nyc` on a fresh checkout / on the pod).
# `kit build` regenerates data_nyc/landphases.json (hist_kit) and drops the pier phases; the flat-relief DEM is not produced by the kit.
#   1. dem.npz  : if raw Copernicus tiles are given (DEM_DIR), rebuild with dem_nyc.py (DEM_OPEN 900, ring flattening from story.json);
#                 otherwise restore the committed one from data_nyc_src/dem.npz.gz (identical output, md5 checked by `kit gate` parity).
#   2. piers.py --write : adds the pier-spike / slip landphases (idempotent, 'yb_pier' entries replaced).
# usage: sh cities/nyc/qa/fix/restore_after_build.sh [DEM_DIR]      (PY=python interpreter, default python3)
set -e
R=$(cd "$(dirname "$0")/../../../.." && pwd); PY=${PY:-python3}; D=$R/data_nyc
[ -d "$D" ] || { echo "data_nyc missing: python -m kit data nyc"; exit 1; }
if [ -n "$1" ] && ls "$1"/Copernicus_DSM_COG_10_*_DEM.tif >/dev/null 2>&1; then
  (cd "$R" && DEM_OPEN=900 $PY dem_nyc.py "$1" "$D")
else
  gzip -dc "$R/data_nyc_src/dem.npz.gz" > "$D/dem.npz"; echo "[restore] dem.npz from data_nyc_src (no raw tiles given)"
fi
$PY "$R/cities/nyc/qa/fix/piers.py" --write
$PY - "$D" <<'P'
import json, sys, numpy as np
D = sys.argv[1]; ph = json.load(open(D + '/landphases.json')); z = np.load(D + '/dem.npz')
n = sum(1 for p in ph if p.get('yb_pier')); print('[restore] landphases', len(ph), 'pier entries', n, 'dem D max %.0f m' % float(z['D'].max()))
assert n > 300, 'restore incomplete: pier phases missing'
P
