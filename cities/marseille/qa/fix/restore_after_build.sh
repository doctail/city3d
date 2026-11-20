#!/bin/sh
# Marseille: eseguito da `kit build marseille` (passo post) e da run.sh sul pod dopo hist_kit build. Costa storica: Lacydon e darsene Joliette/Arenc
# (history.water -> landphases.json) e edifici in acqua ritardati/scartati (water_fix.py, idempotente).
# Legge YB_DATA (cartella dati) se impostata: il gate la usa per simulare il pod senza toccare data_marseille.
set -e
R=$(cd "$(dirname "$0")/../../../.." && pwd); PY=${PY:-python3}
$PY "$R/cities/marseille/qa/fix/water_fix.py" --write
