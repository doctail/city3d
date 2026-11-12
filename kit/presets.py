"""Preset di stile per city_<slug>.json (kit Year Built).

Ogni preset e' un city json COMPLETO salvo i campi di luogo (lat0/lon0, box, hist, cover...), che
kit/city_json.py calcola dalla story. Le palette vengono dalle citta' gia' pubblicate e approvate:
  - mediterranean: Roma (muri ocra/terracotta, coppi) + bianchi calce di Siviglia, suolo chiaro come Copenaghen
  - nordic:        Copenaghen (muri gialli/rossi saturi, tetti rossi, acqua verde-blu)
  - central:       Parigi (pietra chiara, ardesia, mansarde) ma con resa "Standard" leggibile come Roma/Cph
  - atlantic:      Siviglia/Porto (calce, azulejo, tetti bruno-rossi), acqua blu-grigia
Tutte usano view_transform Standard + look None (resa satura di Copenaghen/Roma), notte completa,
chiavi di stile esplicite (nessun default NYC di build_render.py).
"""
import copy

# --- stile comune: tutte le chiavi lette da build_render.py (ST.get) con valori sicuri -----------------
_BASE_STYLE = {
    "haze": [0.8, 0.88, 0.96],
    "era_split": 1900, "pitched_until": 1900, "pitched_max_area": 500,
    "glass": ["#7fb2d0", "#6ea6c8", "#8ec0da"], "glass_h": 60, "glass_min_area": 400,
    "window": "#2a3a4a",
    "wall_anc": ["#cfc8bc", "#bdb6aa", "#c9c2b4"],
    "urban_green": "#7fb04e", "hedge": "#2f6a25", "blocks": "#8f8778",
    "grass": "#76b84a", "tree": "#3f8a35", "forest_base": "#5d9c3f",
    "park_ground": "#5f8a3e", "reclaim": "#c9b993", "urban_phase": "#b8ad98",
    "street": "#e3dac6", "rail": "#8a8378", "bridge_deck": "#b9b2a4", "bridge_side": "#a39d92",
    "smoke": "#3a3532", "smoke_alpha": 0.85,
    "water": "#0f6c7c", "water2": "#2a9fae", "water_rough": 0.02, "wave_scale": 0.025, "wave_strength": 0.55,
    "sky_light": 0.35, "sun_energy": 5.0, "sky_in_reflections": True,
    "sunset_el": 4.0, "sunset_sun": 9.0, "exp_sunset": 0.35,
    "twilight_sun": 0.12, "twilight_sky": 0.05, "twilight_sky_col": "#1f2f5a", "exp_twilight": 0.0,
    # notte: night_bld_off e' il nome letto da build_render.py (night_off dei vecchi json non e' letto)
    "night_bld_off": 0.82, "night_floor_off": 0.45, "night_win_off": 0.22,
    "night_win": 4.5, "night_street": 0.9, "night_sky": 0.01, "moon": 0.05,
    "night_ground": [0.6, 6.0, 0.25], "night_lamp": "#ffa955", "bulb": 14.0, "bulb_size": 1.6,
}

# --- chiavi top-level comuni (look e geometria del suolo come Roma/Copenaghen) ---------------------------
_BASE_TOP = {
    "min_area_m2": 12, "land_half_m": 40000, "grid_deg": 0, "marsh": False,
    "haze_k": 1.0e9, "water_z": -1.5,
    "view_transform": "Standard", "look": "None", "exposure": -2.0,
    "sun_el": 24, "sun_rot": 230,
    "park_trees": 0.02, "block_trees": 0.0008, "tree_scale": [1.8, 3.2], "tree_lift": 2.5,
    "land_from_buildings": True, "land_close": 15, "blocks_by_building": True,
    "urban_ground": "footprints", "urban_buffer": 2.0, "urban_close": 2.0,
    "dur_min": 0.003, "merge_parts": True, "dem_band": 30.0,
    "bin": 4, "dbin": 8, "rewind_hold": 4,
    "ms_per_cambio": 12.0, "budget_cambi_h": 1.0,
}

PRESETS = {
    "mediterranean": {
        "top": {"exposure": -2.2, "sun_el": 24, "field_colors": ["#6f7a3c", "#7c8442", "#8c8a52", "#6a7539", "#94905c"]},
        "style": {
            "era_split": 1880, "pitched_until": 1700, "pitched_max_area": 400, "no_windows_before": 1300,
            "wall_old": ["#dcbf98", "#d6b38a", "#e2c8a4", "#d0aa80", "#ece6d8", "#f1ece2", "#d2ad5f", "#bd8459"],
            "roof_old": ["#c47a52", "#bb6f49", "#cc8660", "#b56a45", "#c27d58"],
            "wall_new": ["#dcc4a0", "#d6b892", "#e2ceae", "#eeeae1", "#e7e0d1", "#cfae86", "#e6d6ba"],
            "roof_new": ["#c48460", "#b8775a", "#cc9070", "#ab9c88", "#bfae98"],
            "wall_anc": ["#e0c29a", "#d9b68c", "#e5cca8", "#d3ab82", "#dec09a"],
            "urban": ["#d9cbae", "#d2c4a6", "#ddd1b6", "#cdbf9f", "#d6c8aa", "#cfc1a3"],
            "urban_dark": "#e3d7bf", "street": "#c9b78f", "grass": "#6f9a3c", "tree": "#3c5f26",
            "water": "#3d8fb0", "water2": "#5aa6c4",
        },
    },
    "nordic": {
        "top": {"exposure": -2.0, "sun_el": 20, "field_colors": ["#4e9a34", "#5aa53c", "#468f2f", "#63a944", "#55a039"]},
        "style": {
            "era_split": 1900, "pitched_until": 1930, "pitched_max_area": 500,
            "wall_old": ["#d9a441", "#e3b85c", "#c9653f", "#b8452f", "#e8c58a", "#d98a54", "#a8432f", "#efd9a8"],
            "roof_old": ["#b5482e", "#a63f28", "#c25a3a", "#9c3a26", "#b9512f"],
            "wall_new": ["#c9c9c4", "#bdbeba", "#b2b4b1", "#d2d0c9", "#aeafac"],
            "roof_new": ["#7d7f82", "#929496", "#6f7174", "#a3a4a3"],
            "urban": ["#d6cbb2", "#cfc4aa", "#dbd1b9", "#c9bea4", "#d3c8ae", "#ccc1a7"],
            "urban_dark": "#e8dfcb",
            "water": "#0f6c7c", "water2": "#2a9fae",
        },
    },
    "central": {
        "top": {"exposure": -2.0, "sun_el": 22, "sun_rot": 140, "field_colors": ["#677a43", "#78854e", "#8a8a58", "#6e7c48", "#848b5a"]},
        "style": {
            "era_split": 1850, "pitched_until": 1850, "pitched_max_area": 600, "glass_h": 70,
            "wall_old": ["#e4dac4", "#d9cdb1", "#e9e1cf", "#cdbf9f", "#d4c6a6", "#c8b896", "#ddd0b5", "#bfae8c"],
            "roof_old": ["#6a6f77", "#767a80", "#5f646b", "#8a5f4b", "#94654f", "#70757c"],
            "wall_new": ["#e8dfca", "#e2d7bf", "#ece5d4", "#ddd1b6", "#d6c9ab", "#efe9dc", "#cfc3a6"],
            "roof_new": ["#7f868f", "#8b9199", "#737a83", "#969ca3", "#6a7179", "#7a7f86"],
            "urban": ["#cdc5b4", "#c5bdab", "#d2cab9", "#bdb5a3", "#c9c1af", "#b9b09e"],
            "urban_dark": "#d6cebd", "street": "#c9c1b0", "grass": "#6f9440", "tree": "#3b5a2c",
            "water": "#2f6f86", "water2": "#4a8ea3",
        },
    },
    "atlantic": {
        "top": {"exposure": -2.0, "sun_el": 18, "field_colors": ["#6a8a3f", "#76904a", "#5f7f38", "#86955a", "#6f8a45"]},
        "style": {
            "era_split": 1940, "pitched_until": 1930, "pitched_max_area": 500,
            "wall_old": ["#ece6d8", "#e8dfcc", "#f1ece2", "#e4dac4", "#d2ad5f", "#c99c5e", "#bd8459", "#7fa3c4", "#dccfb0"],
            "roof_old": ["#b0583c", "#a5503a", "#b96748", "#9a4c36", "#a86046"],
            "wall_new": ["#eeeae1", "#e7e0d1", "#ddd3bf", "#f2efe8", "#d6c6a4", "#cdb48a", "#e3dccd"],
            "roof_new": ["#a9a49b", "#9b968d", "#b3aca0", "#a05a43", "#8a8379"],
            "urban": ["#cfc3ab", "#c7bba3", "#d4c9b2", "#bfb39b", "#cbbfa7", "#bcb098"],
            "urban_dark": "#d8cdb7", "street": "#d2c7b0",
            "water": "#2f6f8a", "water2": "#4a8aa4", "wave_strength": 0.35,
        },
    },
}

STYLE_REQUIRED = ["haze", "era_split", "wall_old", "roof_old", "wall_new", "roof_new", "wall_anc", "glass", "window",
                  "urban", "urban_dark", "urban_green", "grass", "tree", "forest_base", "street", "water", "water2",
                  "night_bld_off", "night_win", "night_street", "night_ground", "night_lamp"]


def preset(name):
    """Restituisce (top, style) completi per il preset."""
    if name not in PRESETS:
        raise KeyError(f"style_preset '{name}' sconosciuto: usa uno di {sorted(PRESETS)}")
    p = PRESETS[name]
    top = copy.deepcopy(_BASE_TOP); top.update(copy.deepcopy(p["top"]))
    st = copy.deepcopy(_BASE_STYLE); st.update(copy.deepcopy(p["style"]))
    return top, st
