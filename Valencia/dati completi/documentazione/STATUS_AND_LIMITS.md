# Valencia — validation and production status

## Static data validation
**PASS: 36/36 checks, 0 failures.** Validation covered configuration, data schemas, feature counts, polygon validity, date coverage/provenance flags, DEM dimensions, historical source-layer transforms, and source/output count reconciliation.

| Layer | Prepared count / coverage |
|---|---:|
| Catastro building footprints | 35,145 |
| Catastro valid original construction years | 35,059 (99.755%) |
| Missing Catastro years imputed and flagged | 86 |
| OSM-only building supplements | 3,096 |
| Total renderer building records | 38,241 |
| Road/rail polygon components | 13,838 |
| Bridge deck components | 432 |
| Park polygons | 414 |
| Land polygons / interior holes | 4 / 162 |
| Historical predecessor footprints | 504 |
| Historical wall approximation segments | 34 |
| DEM | 868 × 868 at 30 m; elevations −37 to 168 m |

## Not yet accepted for final rendering
- No Blender scene/frame/video render has been executed because Blender is unavailable in the preparation environment. Static schema checks do not replace a smoke render.
- `schedule_valencia.json` and `cover.cam` are candidate camera settings; framing, intersections, object clipping and memory use have not been visually tested.
- 1238–2026 is the active medieval-to-modern timeline. Roman layers remain research-only; BCE year rendering has not been tested.
- The 1356 polygon is a broad urban extent, not a surveyed Christian-wall line. The Muslim wall is a schematic perimeter approximation.
- Roads outside dated historic extents use a local construction-year-grid proxy, not documented road-opening dates.
- The old Turia bed and park boundaries are current-geometry proxies, not surveyed historic banks.
- 3,096 OSM-only buildings have unknown construction year/height and are placed at 2026 rather than assigned invented dates.
- 3,131 Catastro heights lack floor-count data; these are not measured heights.
- Municipal base-cartography supplemental extracts were partial and were not treated as complete citywide layers.

## Reproduction
The companion `Valencia_delivery.zip` contains `prepare_valencia.py`, `parse_catastro.py`, `build_historical.py`, `hist_valencia.py`, `validate_valencia.py`, all prepared renderer data, provenance/audit tables, historical source GeoJSONs, Catastro ZIP, and DEM source. The original Geofabrik source archive is ~276 MB and is not duplicated in the zip; it was supplied in the session and its URL is in `SOURCES.csv`.

To run a preview after extracting the bundle and installing Blender/bpy plus the documented Python dependencies, run the repo renderer from the extracted `Valencia_delivery` directory with the `data_valencia` directory and `--city city_valencia.json --schedule schedule_valencia.json`. First run only a low-resolution smoke test; do not start a full render before reviewing frames.
