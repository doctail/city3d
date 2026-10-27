# Valencia — YearBuiltCities

This directory contains Valencia-specific configuration, chronology, sources and validation status. It does not modify files outside `Valencia/`.

## Active period
**1238–2026.** The 1238 start is a medieval-to-modern production scope, not the founding date of Valencia. Roman sources (138 BCE onward) are preserved in the research package but excluded from the active timeline because BCE support and a building-level Roman footprint chronology have not been validated in the renderer.

## Current data-preparation result
- 38,241 renderer building records: 35,145 Catastro + 3,096 OSM-only supplements.
- 35,059/35,145 Catastro records have valid original construction years (99.755%); 86 missing years are imputed and flagged.
- 13,838 road/rail polygon components; 432 bridge-deck components; 414 park polygons.
- DEM: 868 × 868 samples, 30 m cell, −37 to 168 m.
- Static validation: **36/36 checks passed**.

## Important production status
This is **not yet visually/render approved**. The candidate camera schedule is not smoke-tested in Blender; no frame/video render was executed in the preparation environment. Historical walls and some road/river phases use explicitly documented spatial proxies. See [STATUS_AND_LIMITS.md](STATUS_AND_LIMITS.md).

## Files
- `city_valencia.json`: renderer city configuration.
- `schedule_valencia.json`: candidate camera and timeline schedule; not visually validated.
- `SOURCES.csv`, `CHRONOLOGY.csv`: source register and dated urban events.
- `STATUS_AND_LIMITS.md`: counts, validation scope, limitations and outstanding render gate.
- `data_valencia/README.md`: data-file inventory and rebuild instructions.

## Data bundle
The processed JSON/NPZ files, source layers, preparation scripts, provenance CSVs, and raw Catastro/DEM sources are packaged in the companion artifact `Valencia_delivery.zip` attached in the ChatGPT conversation. The Geofabrik source archive is ~276 MB and is not duplicated in this directory; its URL and snapshot are documented in the bundle. To render, extract the bundle so that `data_valencia/`, `city_valencia.json`, `schedule_valencia.json`, `hist_valencia.py`, and `urban_grid_valencia.json` are together under this directory, then run the renderer from this working directory.

No files outside `Valencia/` were changed by this commit.
