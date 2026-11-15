# Year Built: a new city with the kit (from 13/11/2026)

Prompt to paste at the start of a new chat:
> "Year Built: new city <CITY>. Use the kit (city3d repo, branch claude/inspiring-turing-oy4h6k, file kit/AVVIO_NUOVA_CITTA.md). Agents with explicit models (yb-scout haiku, yb-historian/yb-modeler/yb-qa sonnet), max 2-3 in parallel. The chat runs on Sonnet."

## Steps (★ = the owner's OK)
1. **yb-scout**: vidIQ search "<City> 3D timelapse" (5 credits) + open-data check (year per building).
   Saturation rule (12/11): best video under 5K = free; 5K–100K = go only with a clearly better product and a different angle; over 100K = proven demand, a test case.
2. **Data**: Spain → `fetch_es.py` (Catastro); Denmark → `fetch_dk.py`; Netherlands → `fetch_nl.py`. Other countries: see `kit/ATLANTE_DATI.md` (the source and download host may have to be unlocked).
3. **yb-historian** → `cities/<slug>/story.json` (sources, zones, walls, gutting, water/floods, monuments, ~45 cards, 25 soste, chapters, polities) + METADATA.md. The camera is the **drone** (`regia.camera: "drone"`, written by `kit init`; needs `pacing: "story"`): one continuous flight, no cuts; at each sosta it comes in fast and low, stops and hovers in front of the target, then flies on. Cards ride along and are never stops. The video's length comes from the story's rhythm (`regia.duration` absent or "auto"): every stop gets its flight and hover, cards ride along, quiet years run at the construction rhythm. Nothing is dropped unless you set a smaller `duration` or `max_duration`; then the lowest-`weight` soste become target-less cards, and a sosta with `weight: "max"` (the strongest moment) is never dropped. The music follows the duration (playlist with crossfades and a closing fade). See STORY_SCHEMA.md.
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
- The duration is NOT a target: the story's rhythm decides (8:31 was only Copenhagen's two tracks). Music follows the duration.
- Look at the preview before the full render: two previews caught 6 defects.
- Floods: `history.floods` (muddy water draped on the terrain) is restrained; a caption explains it.
- Use local names (Valencian, Catalan…) on monuments: viewers point it out.

## Camera "drone" (13/11/2026, default for new cities; owner's request: no jumpy cuts)
- `regia.camera: "drone"` = one continuous flight (low, fast fly-in, arc around the monument, climb out). Fallback: `"cuts"` (old behaviour).
- **Every sosta with a target is flown to and hovered over; the video simply gets as long as the rhythm needs** (Valencia: all 25 soste, about 12:50). Spread the soste geographically and put all other events in cards WITHOUT a target. Check the QA rhythm WARN (gaps over 15 s without a new card or sosta).
- The motion has been checked only on 6 still frames, never on a video: judge it on the first preview on the pod (10 min) and send the split preview to the chat.
- Known limits: the opening is only about 1 km from the first stop (250 m/s cap), the Plan Sur / cruise frames look almost straight down (about 2,900 m).

## Packaging rules (14/11/2026)
- The promise of the thumbnail/title must appear in the first 30-60 s (a cold open of the climax for 5-8 s, then the rewind). A question in the thumbnail is only allowed if the video answers it early.
- Do not A/B test thumbnails under about 3,000 impressions per variant. Do not read a CTR under about 3,000 impressions.
- Long-video thumbnail and Short thumbnail are different jobs: a single big number or a question belongs to a Short.

## Hook frame (from Copenhagen's CTR of 6.8% vs Valencia's 1.3%, 14/11/2026; hypothesis, n=2)
- Choose the city also for a dramatic, visible event (fire, bombardment, flood, quake) and decide the HOOK FRAME in the story before the render: one striking moment that goes on the thumbnail (one half) and in the cold open. Copenhagen's thumbnail: flames and smoke vs a night city with lights.
- The hook frame must really be visible in the 3D render (Valencia's 1957 flood water was not): check it with a CPU frame before the pod.
- Add a `thumbnail_hook` key to story.json: year, camera, what it shows.

## Thumbnail layout (15/11/2026, from the 7 Valencia thumbnails: 131K winner vs 12-60 view flops; hypothesis)
- Split screen, BOTH halves full of city: the left half must not be empty field (Valencia v1: a small red patch on green; the 131K winner had a dense Roman city). If the first year is a small town, zoom on it until it fills the half.
- Thick white sans (Inter ExtraBold) for the city name, black outline; years in yellow with outline; the right label is a year or "NOW", never thin letter-spaced type. Saturation x1.4, contrast x1.2.
- Generate with `python -m kit.thumb_kit <slug> --left A.jpg --right B.jpg --title NAME --ly YEAR --lbox x,y,w --rbox x,y,w` (CPU frames from the QA, free). Check at 168 px.
- Honest limit: a near-clone of the winner's design got 59 views, so the thumbnail is necessary, not sufficient. The gate is per video (Mattia Maps, 331 subs: Valencia 131K, Santiago 738).

## Reading retention (15/11/2026)
- Do not read a retention curve under about 3,000 impressions: a few dozen viewers, many from Reddit/direct links, say nothing about the feed.
- Valencia's first curve: plateau at 28% from 2:30 to 6:30 (the middle is fine), but 50% lost by 0:30. The first 30 s count in the first test too: cold open of the hook frame, no slow intro. Working only on clicks without the opening makes the first test worse.

## Go / no-go gates (14/11/2026, thresholds provisional: recalibrate after 3 more videos)
1. BEFORE any data work: free city (no relevant 3D timelapse above 5K views in 45 days, or a clearly different angle), per-building year data, AND a spectacular visible event (the hook frame). If one is missing, do not produce.
2. BEFORE the story: a packaging check (30 min, free): thumbnail + title + hook frame rendered with one CPU frame, compared at 168 px in a feed mockup with the competitors (analisi/ctr/thumbs/feed_mockup.jpg). It must read in 1 second and its promise must be in the first 30-60 s of the video.
3. AFTER publication, read ONLY at 24 h: healthy = more than 10K impressions and CTR >= 4% (Copenhagen: 51.9K, 6.8%); stalled = under 2K impressions or CTR under 2% (Valencia 16 h: 823, 1.3%). Stalled: ONE change at most (thumbnail), then move on; never more.
4. Three stalled videos in a row: stop producing, review the selection (steps 1-2), do not make more videos.
5. Frequency follows the gates, not the calendar: one video that passes beats two that do not. No ads as a lever: 15 EUR buys about 10,000 views of 30 s and did not trigger Home (Rotterdam).

## Distribution list per city (BEFORE publishing; owner's request 14/11/2026)
Every city needs, ready at launch: 6-10 local communities (city and country subreddits, local-history Facebook groups, local blogs and outlets) with the admin-approval message, the post with the hook "find your building" as the first line, and a press note. Template: cities/valencia/DISTRIBUZIONE.md. External viewers watch about 3 minutes, so they are the right first audience for the algorithm.

## Lessons from Lyon (15/11/2026): how NOT to burn pod time and money (owner's rules)
**Method (owner's order, 15/11): the chat orchestrates, the agents do the work, as in Valencia.**
- yb-scout (haiku), yb-historian / yb-modeler / yb-qa (sonnet), max 2-3 in parallel. If the `yb-*` agent types do not exist in the session, use `general-purpose` with the explicit model. The chat decides, checks the reports and talks to the owner; it does NOT write code or iterate on fixes itself, and it does not test one idea at a time on the pod.
- Every pod run costs money: say what it costs BEFORE asking for it, and give the progress command together with the launch command.

**Pod rules**
1. Scene build is the cost: about 30 min per process for a 145K-building city (Lyon), paid at every launch (preview, cover, check frames, full, night). Put ALL checks of one round in ONE pod session, in parallel (covers + check frames + preview at the same time).
2. No `PREVIEW_NIGHT=1` (+30 min); the night is checked in the full render. For big cities skip the separate preview and launch `full`: watch the first frames and re-render only a wrong segment (one scene build + a few frames).
3. `git pull` first, then read the banner that `run.sh` prints (commit, schedule duration, lens). Lyon lost a whole test because the pod ran the old schedule.
4. Always send the progress one-liner (frames done / total, frames in the last 5 min, ETA); the day total is `int(night_t*24)+241`, then the night is a second scene build for ~240 frames.
5. Run `python -m kit qa <slug>` locally before any pod run; it now FAILs on the three errors that cost Lyon pod time (below).

**Data / story errors that cost a pod run (now caught by QA)**
- BDNB groups without `annee_construction` (28% in Lyon) arrive as `y = 0` = year 0 AD: modern buildings in the Roman era. Infer from neighbours (median of 6 within 150 m, rounded to 5 years) and mark them; QA FAILs on `y = 0` when `start_year < 0`.
- A landmark whose body appears after the middle of its hover is invisible during its own stop (Confluences: body at 2014.97 = end of the hover). QA FAILs on it.
- Frozen counter: two stops less than ~1 year apart in different places make a 25-35 s flight with the years almost still (owner's definition of a "gap": a static city, the viewer leaves). QA WARNs on flights of 12 s or more under 0.4 years/s; turn one of the two stops into a card (no target) so the flight covers more years.
- `bld` targets (monuments) are capped at 20-35 degrees and `alt_max` m: for hero shots use an `area:[lat,lon,r]` target.
- Camera too close: new options `drone.cruise_k` (0.35), `cruise_min` (250), `alt_max` (200), `clear`, `rho_max` and `regia.lens` (35). Lyon uses 0.6 / 450 / 350 / 60 / 900 and lens 30 with `wide` shots. NOT validated in a full render yet: check this note after the Lyon video and update the defaults if it works.

**Packaging**
- The year on the thumbnail must be the video's first year (title "43 BC-NOW" means the thumbnail says 43 BC), never the year of the hook frame. The hook (fire) goes into the 5-8 s cold open, not on the thumbnail with its own year.
- Covers: `city.cover.shots` (per-shot camera and year, rendered in parallel by `run.sh cover`), 1080p on the pod; 960x540 preview frames are too soft. Lift night frames to a mean luminance of at least 90 (Lyon's first night cover was 31: owner: "too dark").
- Do the packaging check (thumbnail + title + hook frame, 168 px) BEFORE the story, as the gate says: Lyon did it after the render.
- Lyon full render on the A40 (15/11): 16,649 s = 4 h 37 min for 13,441 day frames + 240 night frames (565 s of video, 145K building groups), i.e. about 29 pod-seconds per second of video plus the 30 min scene build. `run.sh full` ends with a cover step (another ~35 min): skip or kill it when the covers already exist.
