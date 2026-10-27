# Valencia — audit report (2026-10-27)

**Static validation: PASS, 36/36 checks, 0 failures.** The prepared data schemas and geometries were checked against the existing renderer contract. No Blender render was executed.

## Prepared outputs
- 38,241 buildings total (35,145 Catastro and 3,096 OSM-only supplements).
- 35,059 original Catastro dates valid; 86 missing dates imputed from nearby dated Catastro buildings and flagged.
- 13,838 road/rail polygon components, 432 bridge-deck components, 414 park polygons.
- Four land polygons with 162 interior holes.
- 504 schematic historical predecessor footprints; 34 schematic Muslim-wall perimeter segments.
- DEM 868 × 868 at 30 m resolution.

## Warnings
- 1238–2026 is the active medieval-to-modern scope; Roman layers are research-only.
- The 1356 polygon is an urban extent, not a verified Christian-wall line; the Muslim wall is schematic.
- Road chronology outside historic extents is estimated from a local Catastro-year grid.
- The old Turia bed is approximated from modern river/park geometry.
- Unknown OSM-only buildings appear at 2026; 3,131 Catastro heights lack floor-count data.
- Camera schedule is a candidate and has not been visually validated. Blender smoke test and end-to-end render remain outstanding.

See `STATUS_AND_LIMITS.md` and the companion bundle's full `audit/validation_results.json` and provenance tables for detailed checks.
