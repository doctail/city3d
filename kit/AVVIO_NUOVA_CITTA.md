# Year Built: a new city with the kit (from 13/11/2026)

Prompt to paste at the start of a new chat:
> "Year Built: new city <CITY>. Use the kit (city3d repo, branch claude/inspiring-turing-oy4h6k, file kit/AVVIO_NUOVA_CITTA.md). Agents with explicit models (yb-scout haiku, yb-historian/yb-modeler/yb-qa sonnet), max 2-3 in parallel. The chat runs on Sonnet."

## Steps (★ = the owner's OK)
1. **yb-scout**: vidIQ search "<City> 3D timelapse" (5 credits) + open-data check (year per building).
   Saturation rule (12/11): best video under 5K = free; 5K–100K = go only with a clearly better product and a different angle; over 100K = proven demand, a test case.
2. **Data**: Spain → `fetch_es.py` (Catastro); Denmark → `fetch_dk.py`; Netherlands → `fetch_nl.py`. Other countries: see `kit/ATLANTE_DATI.md` (the source and download host may have to be unlocked).
3. **yb-historian** → `cities/<slug>/story.json` (sources, zones, walls, gutting, water/floods, monuments, ~45 cards, 25 soste, chapters, polities) + METADATA.md. The camera is the **drone** (`regia.camera: "drone"`, written by `kit init`; needs `pacing: "story"`): one continuous flight, no cuts; at each sosta it comes in fast and low, stops and hovers in front of the target, then flies on. Cards ride along and are never stops. The total time is fixed by the music, so if the flights do not fit, the lowest-`weight` soste become target-less cards (listed in `regia.txt`). Give the soste you care about a `weight`, and leave a pause between far-apart soste; see STORY_SCHEMA.md.
4. **yb-modeler** → monuments checked by eye.
5. `python -m kit build <slug>` and `python -m kit qa <slug> --render` (local, free) → **yb-qa** looks at contact.jpg and `qa/drone_path.png` (max speed/acceleration/jerk, clearance, 0 jumps, hover and flight time, kept/dropped soste).
6. `python -m kit pack <slug>` + commit/push.
7. ★ **Pod**: **A40** (5080s gave cuInit 999 on 12/11). Before cloning: `python3 -c "import ctypes;print(ctypes.CDLL('libcuda.so.1').cuInit(0))"` must print 0.
   `cd /workspace && git clone -b claude/inspiring-turing-oy4h6k https://github.com/doctail/city3d && cd city3d && PREVIEW_NIGHT=1 CITY=<slug> bash run.sh preview`
   Split the preview for the chat: `ffmpeg -i out/<slug>_preview.mp4 -c:v libx264 -crf 24 -g 20 -an -f segment -segment_time 100 -reset_timestamps 1 out/prev_%d.mp4`
8. ★ Full render: `nohup env CITY=<slug> bash run.sh full > full.log 2>&1 &` (Valencia: about 2.5 h on the A40). Send only `out/years.json` to the chat.
9. Montaggio (local): years → `montaggio/years_<slug>.json`, `labels_cam.py`, `kit.eventi_kit`, `kit.labs_kit`, `kit_city.py`, `sfx_kit.py`, `ov_kit.sh <slug> long` (~1 h on CPU), cover with `thumb_city.py` (years in the TITLE → START → NOW).
10. ★ Final merge on the owner's PC (the ffmpeg command in `montaggio/monta_kit.bat`), upload, pinned comment, Reddit.

## Lessons from Valencia (12/11)
- `regia.duration` must match the music (two tracks = 511.5 s), or the video ends without music.
- Look at the preview before the full render: two previews caught 6 defects.
- Floods: `history.floods` (muddy water draped on the terrain) is restrained; a caption explains it.
- Use local names (Valencian, Catalan…) on monuments: viewers point it out.

## Camera "drone" (13/11/2026, default for new cities; owner's request: no jumpy cuts)
- `regia.camera: "drone"` = one continuous flight (low, fast fly-in, arc around the monument, climb out). Fallback: `"cuts"` (old behaviour).
- **A continuous flight cannot visit 44 places in 8 minutes.** On Valencia 16 of 44 stops were only flown over. For a new city: about 18 soste with a camera target, spread geographically (neighbouring monuments one after another), all other events as cards WITHOUT a target (they ride along with the flight). Check the QA WARN "soste solo sorvolate".
- The motion has been checked only on 6 still frames, never on a video: judge it on the first preview on the pod (10 min) and send the split preview to the chat.
- Known limits: the opening is only about 1 km from the first stop (250 m/s cap), the Plan Sur / cruise frames look almost straight down (about 2,900 m).

## TODO first in the next chat (owner's request, 13/11/2026)
- **Duration must come from the story, not from the music.** Today regia.duration (511.5 s) is inherited from Copenhagen's two tracks. Build: regia computes the natural duration (hover + flight + fast years in quiet periods); the music becomes a PLAYLIST of any length with automatic crossfades and a closing fade (kit/music/*.json measured per track by kit/music/analyze.py). Videos of 7 or 10+ minutes are fine: rhythm decides.
- **Rhythm QA**: flag gaps (more than about 12-15 s without a new stimulus: a card, a sosta, a chapter) and plot years per second. Calibrate on the retention curve of Valencia at 48 h (YouTube Studio).
- **Weights**: the city's strongest moment gets the highest `weight` on its sosta (Valencia: the Plan Sur) so the drone never drops it.
- The owner must supply 2-3 extra tracks (YouTube Audio Library, no attribution) for videos longer than 8:30.
