# Kit Year Built: `story.json`, la scheda unica di una città

Una città = una cartella `cities/<slug>/` con **un solo file scritto da umani/agenti**: `story.json`.
Tutto il resto (hist, landmarks, schedule, eventi, overlay, audio, controlli) è **generato dal kit**.
Coordinate: sempre **[lat, lon]** (WGS84) nella story; il kit converte in metri locali (x est, y nord) con
`KX = cos(lat0)*111320`, `KY = 110540` attorno a `city.lat0/lon0` (stessa convenzione di `build_render.py`).
Anni: float, negativi = a.C. Ogni data storica porta `src` (id in `sources`) e `conf` (`high|medium|low`).

```jsonc
{
  "version": 1,
  "city": {
    "slug": "valencia", "name": "Valencia", "country": "Spain",
    "lat0": 39.4753, "lon0": -0.3758, "radius_m": 12000,
    "start_year": 1238, "end_year": 2026,
    "title": "EVOLUTION OF VALENCIA | 3D City Timelapse (1238–NOW) | No AI",
    "data_source": "catastro",          // catastro | bbr | bag | osm | custom
    "data_dir": "Valencia/dati completi/dati_generati",   // cartella DATA già pronta (opz.)
    "style_preset": "mediterranean",    // mediterranean | nordic | central | atlantic (palette in kit/presets.py)
    "population": [[1238, 15000], [1500, 45000], [2026, 800000]],   // HUD; ogni punto con fonte in "pop_src"
    "pop_src": ["S7"],
    "eras": [[1238, "Kingdom of Valencia", "#c9a24a"], [1865, "Modern city", "#6aa0c8"]]
  },

  "sources": { "S1": {"url": "https://…", "title": "…", "quote": "…"} },

  "history": {
    // Aree costruite prima del catasto: ogni edificio attuale dentro l'area riceve un PREDECESSORE
    // nato in [born0, born1] (rampa dal punto "seed" verso il bordo, o uniforme se seed manca)
    // che muore all'anno di costruzione dell'edificio attuale. Regola r/Madrid: città piena all'anno di partenza.
    "zones": [
      {"name": "Muslim walled city", "ring": [[39.47, -0.38], …], "born": [1238, 1238], "seed": null,
       "era_height": [6, 12], "src": ["S2"], "conf": "high"}
    ],
    // Mura: anello (ring) o linea (line). Costruite tra built[0] e built[1], demolite a "demolished"
    // salvo i tratti "keep" (cerchi [lat, lon, raggio_m]) che restano.
    "walls": [
      {"name": "Christian wall", "ring": [[…]], "built": [1356, 1370], "demolished": 1865,
       "height": 10, "width": 4, "towers_every_m": 60,
       "keep": [[39.4796, -0.3759, 40]], "src": ["S3"], "conf": "high"}
    ],
    // Strade/piazze aperte demolendo case: dentro il ring, PRIMA di "until", il vuoto lasciato dalla
    // strada moderna si riempie di case predecessore; i nastri stradali nel ring compaiono da "until".
    "gutting": [
      {"name": "Plaza de la Reina", "ring": [[…]], "from": 1238, "until": 1962, "src": ["S4"], "conf": "medium"}
    ],
    // Edifici scomparsi espliciti (conventi, cittadelle…): blocco con altezza h tra from e to.
    "lost": [{"name": "Convent of San Francisco", "ring": [[…]], "from": 1239, "to": 1891, "h": 14, "src": ["S5"]}],
    // Incendi/bombardamenti: fuoco e fumo nella finestra [y, y1]; destroy=true demolisce gli edifici
    // nati prima di y dentro il ring e li fa rinascere dopo y1 (+ rebuild_years).
    "fires": [{"name": "Siege of 1812", "ring": [[…]], "y": 1811.98, "y1": 1812.03, "destroy": false,
               "flames": 40, "smoke": 6, "src": ["S6"]}],
    // Acqua/terra che cambia: lastra di terra di tipo c visibile solo in [from, to). Fuori: acqua.
    "water": [{"name": "New Turia channel (field)", "ring": [[…]], "from": -9999, "to": 1964, "c": "field"}],
    // Ponti (impalcato) su linea [lat, lon]…, larghezza w, esistenti in [y, d).
    "bridges": [{"name": "Puente del Real", "line": [[…], […]], "w": 12, "y": 1594, "d": null, "src": ["S8"]}]
  },

  // Monumenti parametrici: kind = preset di kit/landmarks_kit.py. "at" = punto; con "footprint": "auto"
  // il kit usa l'impronta dell'edificio del catasto che contiene "at" (e lo toglie con clear).
  "landmarks": [
    {"name": "Cathedral", "kind": "cathedral", "at": [39.4757, -0.3752], "footprint": "auto",
     "params": {"nave_h": 26, "tower_ref": "Micalet"},
     "phases": [{"y": 1262, "y1": 1300}], "label": true, "src": ["S9"], "conf": "high"}
  ],

  "regia": {
    "music": "waking_monument",          // modello musicale in kit/music/<nome>.json (ancore misurate)
    "duration": 511.5, "night": true,
    "open": {"year": 2026, "rewind_to": 1238},
    // Soste: anni coperti, durata, didascalia "Titolo (data)", bersaglio = nome di un landmark o "fire:<nome>"
    // o "area:[lat,lon,raggio]"; shot = close | medium | wide | top; fx = suono del montaggio.
    "soste": [
      {"y0": 1238.0, "y1": 1238.8, "dur": 6, "caption": "James I takes Valencia (1238)",
       "target": "Muslim walled city", "shot": "medium", "fx": "crowd"}
    ],
    "rmin": 0.5, "rmax": 8.0
  },

  "montaggio": {
    "open": ["VALENCIA TODAY", "800,000 people"],
    "title": ["VALENCIA", "1238 TO NOW"],
    "end": ["VALENCIA · 788 YEARS", "WHICH CITY NEXT?"],
    "events": [{"y": 1609, "title": "Expulsion of the Moriscos", "line": "…", "sober": true}]
  }
}
```

## Regole che il kit controlla da solo (`kit/qa.py`)
1. Ogni `history.*`, `landmarks[*]`, `soste[*]` con un anno ha `src` esistente in `sources` (salvo `conf: "low"` dichiarato).
2. Città piena all'anno di partenza: edifici vivi al `start_year` dentro le zone ≥ soglia di densità.
3. Nessun "corridoio vuoto": per gli anni chiave, le aree di strada moderna dentro il centro storico devono essere coperte da edifici o comparire solo dopo un `gutting.until`.
4. `roads.json` presente; costo dei cambi entro budget; schedule coerente (soste ordinate, didascalie nel formato "Titolo (data)").
5. Anteprima locale: fotogrammi CPU dall'alto e di sosta in `cities/<slug>/qa/`, da guardare prima del pod.

## Pacing "story" e grafica documentaria (tutto OPZIONALE; senza queste chiavi l'output e' identico a prima)
Idea da `analisi/mattia_valencia/FORMULA.md`: documentario in cartelli, tempo pesato dalla storia, HUD onesto, piano sequenza, recap, fonti.
```jsonc
{
  "city": {
    // punto popolazione con terzo elemento = fonte della stima, mostrata sotto il numero:
    // "rough estimate" | "historical estimate" | "census" | "building registry"  (vale fino al punto successivo)
    "population": [[1238, 15000, "rough estimate"], [1900, 213000, "census"], [2025, 841558, "building registry"]],
    "polities": [{"y": 1238, "name": "Kingdom of Valencia · James I", "flag_colors": ["#fcdd09", "#da121a"]}],  // chip in basso a sinistra, strisce orizzontali
    "data_reliable_from": 1840      // prima di questo anno: pillola "RECONSTRUCTION · APPROXIMATE"
  },
  "regia": {
    "pacing": "story",              // default "buildings" (comportamento storico, Copenhagen invariata)
    "camera": "continuous",         // default: stacchi come prima. "continuous" = un piano sequenza PCHIP sui bersagli di cartelli/soste
    "duration": 150,                // il budget di tempo: la corsa tra i cartelli si ricava da qui
    "open": {"story_lead": 3.4}     // pausa sul titolo prima del primo cartello (+2,8 s se c'e' il capitolo I)
  },
  "montaggio": {
    "cards": [{"y": 1483, "title": "The Silk Exchange", "lines": ["1-2 righe"], "chapter": "titolo capitolo (facoltativo)",
               "hold_s": 5, "src": ["S1"], "target": "Lonja de la Seda", "shot": "medium", "labels": ["nome monumento"]}],
    "chapters": [{"y": 1238, "title": "Christian Valencia"}],   // numeri romani automatici (I, II, ...); come "chapter" sul cartello
    "recap": {"seconds": 20, "text": "…"},    // ultimi N s da UN punto di vista alto e fisso, start_year -> end_year (prima di CTA e fonti)
    "cta": "Which city should grow next? Tell me in the comments",
    "sources_card": {"seconds": 8, "max": 14, "no_ai": "NO AI: every frame is rendered from open data"},  // default ON in pacing story
    "label_years": true             // pillole monumenti "Nome · anno"
  }
}
```
- **Tempo.** Rewind fino a `start_year`, pausa, poi per ogni voce (cartello o sosta, ordinate per anno; le soste contano come cartelli) il contatore
  **si ferma a 0,2 anni/s** per `hold_s` (soste: `dur`) e **corre** tra una voce e l'altra alla velocita' che fa stare tutto in `regia.duration`
  (tetto 25 anni/s: se serve di piu', `regia.txt` avvisa). Niente ancore musicali; `night` e' false se non lo scrivi.
- **Coda del video** (regia calcola, lo schedule la porta in `end_plan`): `recap` -> CTA (4,5 s) -> carta delle fonti (default 8 s); l'HUD esce prima della CTA.
  La carta delle fonti elenca i `title` di `story.sources` + riga "NO AI" e sostituisce la schermata finale "WHICH CITY NEXT?".
- **Grafica** (`kit_overlay.jsx`): cartello = riquadro scuro traslucido in alto a sinistra, "ANNO · Titolo" oro + 1-2 righe bianche (data nel formato di `yfmt`: `1238`, `AD 711`, `138 BC`);
  capitolo = titolo centrale ("CHAPTER II" + titolo), mostrato nei 2,8 s prima del cartello che lo apre; chip polity in basso a sinistra sopra l'anno;
  fonte popolazione sotto il numero; pillola ricostruzione in alto al centro. Dati in `eventi_<slug>.json` (`cards, chapters, recap, cta, sources_card`, da `kit/eventi_kit.py`)
  e `kit_<slug>.json` (`city.POPSRC, POLITIES, RELIABLE_FROM`, da `montaggio/kit_city.py`). `labs_kit.py` mette l'etichetta del monumento durante i cartelli con `target`/`labels`.
- Per i cartelli con `src`, `kit/qa.py` non e' ancora esteso: la regola 1 (ogni data con fonte) va controllata a mano.
- Test: `python kit/tests/test_story_mode.py` (fixture `fixtures/story_valencia_cards.json` = delta su `cities/valencia/story.json`, 5 cartelli, 2 capitoli, 2 polity).
