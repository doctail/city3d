# NYC fix tooling (branch yb/nyc-data)

After EVERY `python -m kit build nyc` (and on a fresh checkout / pod after `kit data nyc`) the NYC-specific data must be restored:

    PY=<python with numpy shapely scipy> sh cities/nyc/qa/fix/restore_after_build.sh [RAW_DEM_DIR]

`kit build nyc` now runs it automatically as its last step (kit/cli.py looks for `cities/<slug>/qa/fix/restore_after_build.sh`).
- `dem.npz`: flat-relief DEM (DEM_OPEN 900, relief flattened inside history.water rings). Rebuilt with `dem_nyc.py` only if the raw Copernicus tiles are passed; otherwise restored from `data_nyc_src/dem.npz.gz` (same result).
- `piers.py --write`: pier spikes (visible from 1850) and slips (filled until 1850) added to `landphases.json` (`yb_pier` entries, idempotent). `hist_kit` overwrites landphases, so without this step 1609 shows a comb of modern piers.

Fixed [Certain]: `kit build` now runs landmarks -> hist -> landmarks (2b, merges the walls hist writes). One build from fresh data gives 305144 predecessors and `kit qa nyc` WARN (no FAIL); no extra hist run needed.

Local frames: `shots.py NAME shots.json` (crop 1280x720). `YB_FULL=1 YB_SPP=8 python shots.py NAME shots.json` = whole city 1920x1080 (scene-cost measurement). Env `YB_PY` = interpreter with bpy.
