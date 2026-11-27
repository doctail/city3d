#!/bin/sh
# Copenhagen: hist_copenhagen.py (legacy, video vecchio) e data_copenhagen_src restano intatti; il render nuovo usa la story (hist_cph_kit.py, kit).
# Sul pod run.sh (ramo restore_after_build.sh) esegue solo `kit.hist_kit build`; qui si rifa' la stessa sequenza di `kit build` (landmarks -> hist -> landmarks mura)
# sui dati originali e si applicano le correzioni acqua. Idempotente. YB_DATA = cartella dati (gate/pod parity); PY = python.
set -e
R=$(cd "$(dirname "$0")/../../../.." && pwd); PY=${PY:-python3}; D=${YB_DATA:-$R/data_copenhagen}
[ -d "$D" ] || { echo "data_copenhagen missing: python -m kit data copenhagen"; exit 1; }
cd "$R"
$PY -m kit.landmarks_kit build copenhagen "$D"          # come kit build 1/5 (hist legge DATA/landmarks.json)
$PY -m kit.hist_kit build copenhagen "$D"               # come kit build 2/5
[ -f "$D/landmarks_walls.json" ] && $PY -m kit.landmarks_kit build copenhagen "$D"   # come kit build 2b/5
rm -f "$D/reclaim.json"; echo "[restore] reclaim.json rimosso (history.water lo sostituisce)"
YB_DATA="$D" $PY cities/copenhagen/qa/fix/water_fix.py --write        # predecessori sull'acqua: ritardati al primo anno con terra (yb_water)
$PY tools/filtra_edifici_acqua.py "$D" city_copenhagen.json            # edifici BBR con < 10% su terra: tolti (buildings_prefiltro.json.gz)
