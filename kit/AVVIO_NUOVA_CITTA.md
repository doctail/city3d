# Year Built: a new city with the kit (from 13/11/2026)

> **READ FIRST (owner's order, 16/11/2026, after Lyon): read the section "POST-MORTEM LYON" at the end of this file BEFORE doing anything.** Lyon cost almost 10 pod-hours (over 5 EUR, only 4 h 37 min productive), a very long chat and many wasted tokens, because the chat improvised instead of following the kit. The rules there are mandatory: agents do the work, everything measurable is measured locally before the pod, the pod is switched on only on a written GO, and every delivery is complete the first time.

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
- Superseded 16-17/11: no hook, no cold open; see R14.
- Do not A/B test thumbnails under about 3,000 impressions per variant. Do not read a CTR under about 3,000 impressions.
- Long-video thumbnail and Short thumbnail are different jobs: a single big number or a question belongs to a Short.

## Hook frame
- Superseded 16-17/11: no hook, no cold open; see R14. (`thumbnail_hook` in story.json is no longer required; if present it is ignored.)

## Thumbnail layout (15/11/2026, from the 7 Valencia thumbnails: 131K winner vs 12-60 view flops; hypothesis)
- Split screen, BOTH halves full of city: the left half must not be empty field (Valencia v1: a small red patch on green; the 131K winner had a dense Roman city). If the first year is a small town, zoom on it until it fills the half.
- Thick white sans (Inter ExtraBold) for the city name, black outline; years in yellow with outline; the right label is a year or "NOW", never thin letter-spaced type. Saturation x1.4, contrast x1.2.
- Generate with `python -m kit.thumb_kit <slug> --left A.jpg --right B.jpg --title NAME --ly YEAR --lbox x,y,w --rbox x,y,w` (CPU frames from the QA, free). Check at 168 px.
- Honest limit: a near-clone of the winner's design got 59 views, so the thumbnail is necessary, not sufficient. The gate is per video (Mattia Maps, 331 subs: Valencia 131K, Santiago 738).

## Reading retention (15/11/2026)
- Do not read a retention curve under about 3,000 impressions: a few dozen viewers, many from Reddit/direct links, say nothing about the feed.
- Valencia's first curve: plateau at 28% from 2:30 to 6:30 (the middle is fine), but 50% lost by 0:30. The first 30 s count in the first test too: no slow intro (the cold-open idea is superseded 16-17/11, see R14). Working only on clicks without the opening makes the first test worse.

## Go / no-go gates (14/11/2026, thresholds provisional: recalibrate after 3 more videos)
1. BEFORE any data work: free city (no relevant 3D timelapse above 5K views in 45 days, or a clearly different angle; rule 5K/100K), per-building year data. If one is missing, do not produce. (The spectacular-event/hook requirement is superseded 16-17/11, see R14.)
2. BEFORE the story: a packaging check (30 min, free): thumbnail (`<first year> > NOW`) + title (series formula) rendered with one CPU frame, compared at 168 px in a feed mockup with the competitors (analisi/ctr/thumbs/feed_mockup.jpg). It must read in 1 second.
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
- The year on the thumbnail must be the video's first year (title "43 BC-NOW" means the thumbnail says 43 BC). (Lyon history: the old hook/cold-open idea is superseded 16-17/11, see R14.)
- Covers: `city.cover.shots` (per-shot camera and year, rendered in parallel by `run.sh cover`), 1080p on the pod; 960x540 preview frames are too soft. Lift night frames to a mean luminance of at least 90 (Lyon's first night cover was 31: owner: "too dark").
- Do the packaging check (thumbnail + title, 168 px) BEFORE the story, as the gate says: Lyon did it after the render.
- Lyon full render on the A40 (15/11): 16,649 s = 4 h 37 min for 13,441 day frames + 240 night frames (565 s of video, 145K building groups), i.e. about 29 pod-seconds per second of video plus the 30 min scene build. `run.sh full` ends with a cover step (another ~35 min): skip or kill it when the covers already exist.
- **Camera still too close in many stretches (owner, 15/11, after the full render).** Measured median camera-to-target distance (35 mm equivalent): Copenhagen 1,397 m (33K views), Paris 1,427, Madrid 2,538, Rotterdam 3,748, Lyon 930 (797 m at 30 mm) with `cruise_k` 0.6, `cruise_min` 450, `alt_max` 350, `wide` shots. `kit qa` now WARNs below 1,200 m. Tried in memory on Lyon: `regia.wide_min` 1400 only raises the median to 1,062 m, and `cruise_k` 1.0 / `cruise_min` 800 / `alt_max` 600 / `rho_max` 1400 to 1,060 m: the hover distance is not the problem; the median is dominated by the flights (about two thirds of the video), whose look point is only ~3 s ahead of the drone and whose approach is low (`fly()` in `kit/drone_kit.py`). NEXT CITY: have an agent change the flight profile (higher approach, look point farther ahead, a `lowness` parameter) and target at least 1,400 m before any pod run; check with the QA line "drone: distanza della camera".

## POD ON ONLY ON "GO" (owner's rule, 15/11/2026)
Lyon kept the pod on for almost 10 hours, over 5 EUR, of which only 4 h 37 min were the real render: the rest was test cycles and waiting while the chat changed things. The owner switches the pod on ONLY when the chat says GO, and the chat says GO only when ALL of this is true:
1. `python -m kit qa <slug>` has no FAIL and every WARN is explained (including "drone: distanza della camera" at least 1,200 m 35 mm-equivalent).
2. Data packed (`kit pack`), story/schedule committed and pushed; the chat quotes the commit and the schedule duration/lens that the pod banner must show.
3. Covers planned (`city.cover.shots`) and the thumbnail/title decided (no cold open, R14).
4. The chat gives, in ONE message, the whole command list: GPU check, `git pull`, version check, `full` launch, the real-time progress one-liner, the cover command, and the "you can close the pod when" condition (files downloaded: `lyon_full.mp4`, `years.json`, covers).
5. Cover frames run during the 30 min scene build of `full` (GPU idle, CPU work), not afterwards; kill the final cover step of `full` if the covers exist.
After the render the pod is switched off by the owner as soon as the files are downloaded; any fix is a NEW short session, announced with its cost (scene build + frames), never "while it is on".
- **Camera pitch (owner, 15/11): "when it is low it looks DOWN, like a very low satellite shot, not like flying forward".** Measured on Lyon's schedule: median look angle 66 degrees below the horizon (71 in flight, up to 86), 62% of the video over 60 degrees; Copenhagen, Paris, Rome: median 23-27, never over 45. Cause: in flight the look point is only ~150 m (3 s at 20-60 m/s) from a camera 660 m high. Fix in the kit: `drone.pitch_max` (default 90 = off) pushes the look point out horizontally along the direction of flight; with `pitch_max: 40` the same Lyon schedule gives median 37, p90 38, over 60 degrees 0.8% of the time, median distance 1,028 m (was 797), max look rotation 15 degrees per key (QA limit 20). NEXT CITY: set `drone.pitch_max` to 38-40 in the story from the start, and look at 3 flight frames locally before any pod run.
- Polity chips: list EVERY regime (Lyon had only Roman Empire and French Republic, so the chip said "Roman Empire" in 1536). The montage is separate from the render, so this one is fixable without the pod.


## POST-MORTEM LYON (16/11/2026): what went wrong and the rules that follow (mandatory)
Result: a video that exists, but the session was far slower and more expensive than any city before it, with a kit that was supposed to make it faster. Cost: pod on for almost 10 h (over 5 EUR; the full render itself was 4 h 37 min), a chat that ran for a whole day, many tokens spent on retries and large outputs, and an owner who had to ask for the same things again and again.

### The mistakes (all mine, the chat's; none of them was a kit limitation)
1. **The chat did the work instead of delegating.** Agents were used only for data, story, roads and maps; everything else (camera tuning, covers, thumbnails, QA fixes, montage, notes) was done by the chat, one idea at a time, with the owner paying for the pauses. Valencia ran with scout / historian / modeler / QA agents and a chat that only orchestrated.
2. **Problems were discovered on the pod, not locally.** Every one of these was measurable on the computer before the pod: 28% of the buildings at year 0 (the data agent warned me and I did not fix it), a monument invisible during its own hover, flights with the year counter frozen, a camera median distance of 930 m against 1,400 for Copenhagen, a look angle of 66 degrees below the horizon, a polity chip saying "Roman Empire" in 1536, a thumbnail year that was not the video's first year. All of this is now QA, but the habit is the rule: **measure first, compare with the reference cities, then ask for the pod.**
3. **The pod was used as a laboratory.** Preview with night (+30 min), covers with the wrong year, check frames on a stale checkout, check frames again; five sessions where one would do. Each launch pays about 30 min of scene build (145K building groups). No cost was announced before any of them.
4. **Wrong or unchecked statements.** "Years already run at the minimum speed" (false: the counter stretches over the flight), "I cannot write to Nodum" (false: the curl client worked), duration estimates of 7-20 min and 3 h that were really 30 min and 4 h 37 min, "Valencia was 12:50" (a plan, not the result). Estimates were stated as facts. The owner works from them.
5. **Several variables changed at once** (distance, lens, shot, cruise height) and pushed to the branch the pod pulls, before anybody had seen a frame. The owner then tested the wrong version.
6. **The owner's own analysis was not read before producing deliverables.** `analisi/ctr/MINIATURE.md` already said: bright, saturated, both halves full, one subject, year = first year, no flag. The first covers were dark, the year was the hook frame's, with a flag nobody had tested.
7. **Deliveries were incomplete and came in pieces.** Translations without translated chapters, no Reddit, no distribution, no montage command for a Windows user who cannot download a `.bat`: each one had to be asked for.
8. **Long jobs were launched in a way nobody could watch** (untracked background, `grep` buffering the log so `full.log` stayed empty), and no progress command was given with the launch command.

### The rules
**R1. Orchestrator and agents.** The chat decides, checks the reports and talks to the owner. Work is done by agents with explicit models, max 2-3 in parallel (yb-scout haiku; yb-historian, yb-modeler, yb-qa sonnet; if the `yb-*` types do not exist, `general-purpose` with the model). Add two roles Lyon proved necessary: **yb-camera** (flight profile, distances, pitch, lens: owns the camera QA numbers) and **yb-packaging** (thumbnail, title, hook, metadata in all languages, Reddit, distribution, montage commands). The chat writes no code except one-line fixes.
**R2. Measure before the pod.** `python -m kit qa <slug>` must be green (no FAIL, every WARN explained). Required numbers, compared with the reference cities (`schedule_copenhagen.json` 1,397 m, `schedule_parigi.json` 1,427 m, look angle median 23-27 degrees, never over 45): median camera distance at least 1,200 m (35 mm equivalent, target 1,400), look angle under 45 degrees for 95% of the time (`drone.pitch_max` 38-40), no flight of 12 s or more under 0.4 years/s, every targeted monument built before the middle of its hover, no building at year 0, polity chips for every regime, thumbnail and title checked at 168 px BEFORE the story.
**R3. The pod is on only after a written GO** (see "POD ON ONLY ON GO"). One session, one message with all the commands, the progress one-liner and the condition to switch off. Never test an idea one at a time on the pod. For big cities (over 100K buildings) skip the separate preview: `full`, check the early frames, re-render only a bad segment.
**R4. Say the cost before every paid action, with a measured basis.** Pod seconds per video second (Lyon: about 29), scene build (Lyon: 30 min per process), credits. If it is not measured, say "not measured" and give a range, never a single number.
**R5. One change at a time and nothing unverified on the branch the pod pulls.** Every pod command starts with `git pull` and the banner check (commit, schedule duration, lens). The chat quotes the expected banner.
**R6. Read the owner's analyses and notes before producing anything** (`analisi/`, Nodum CARD, RULES, this file). A deliverable that contradicts a rule already written is a mistake of the chat.
**R7. Complete delivery, the first time.** For every city the delivery is: final render checked, thumbnail (with and without options the owner asked for), title, description, chapters in all languages (translated, with the timestamps of the final render, with and without cold open), tags, pinned comment (EN and local language), Reddit post and first comment, distribution list, admin message, press note, the montage command as one `ffmpeg` line for `cmd` (no `.bat`), the cold open command, and the files sent with `SendUserFile`. If a part cannot be done, it is said in the FIRST line of the message with the reason, not left for the owner to find.
**R8. Verify before asserting.** If a tool or a file can answer, use it before replying. "I cannot" is only said after trying (Nodum via curl worked). Every claim carries [Certain] / [Likely] / [Guessing].
**R9. Long jobs are tracked.** Start them as tracked background tasks, check that the process is alive and the output grows, and re-launch if the sandbox restarts (it did, twice, and killed two jobs silently). Log lines are unbuffered (`grep --line-buffered`).
**R10. Token economy.** Do not print large files or logs (use `head`, counts, summaries); do not view the same images again; give agents the whole job and one report; keep the chat answers short and decisive. If something is wrong, say it in the first line and give the fix, not the history.
**R11. The owner's constraints.** Windows with `cmd`, no `.bat` downloads, no file reading outside what is sent; answers in Italian; titles and on-screen text in American English; tags and credits as in Valencia; no questions that the chat can answer itself.

### Definition of done for a city (checklist, copy it into the first message of the next city)
[ ] Gate 1 (free city, per-building data) and gate 2 (packaging check) passed BEFORE data work.
[ ] Agents assigned (R1), max 3 in parallel.
[ ] QA green and the R2 numbers on screen.
[ ] GO message written (R3) and approved by the owner.
[ ] Render finished, three or more segments checked (owner), pod switched off after downloads.
[ ] Overlay and audio produced locally; final merge command delivered.
[ ] All of R7 delivered in one message.
[ ] Notes updated (Nodum LESSONS, STATUS; this file) with measured numbers.

### R12. Alignment (owner's order, 16/11/2026): everything merged to everything, always
At every delivery and before closing (and at every stop) each repo touched (`doctail/city3d`, `doctail/athens-properties`) has the working branch merged into `main` (fast-forward or merge, push to `main`), and Nodum is updated with the same state as the chat: `STATUS Year Built`, `BACKLOG Year Built`, the city note, `LEDGER` if credits were spent, `LESSONS` if something was learned. Nothing stays only in the chat or only on a branch. If the Nodum MCP server is disconnected, use `kit/atlante/strumenti/nodum_mcp_curl.py` (the token is injected by the proxy). Before saying "done", check that `main` and Nodum contain what was said.

### R13. Check the overlay with your eyes before delivering (Lyon, 16/11/2026: the owner found a title collision that the chat had looked at and called correct)
- Lyon's story had an explicit `open.story_lead: 3.4`: it overrides the default `3.4 + 2.8` (the 2.8 s are for chapter I), so chapter I ("CHAPTER I / CAPITAL OF THE GAULS", from `first card - 2.8 s`) landed on top of the big title "LYON / 3D TIMELAPSE / 43 BC TO NOW": overlapping text in the final video. The chat rendered the very frame (12.5 s), saw the overlap and described it as fine. NEVER set `open.story_lead` explicitly when the story has chapter I; if the render is already done, drop the title card from the overlay with `montaggio.title_at: [-5,-4,-3,-2]` (new option of `kit_city.py`; four times = fade-in start, fade-in end, fade-out start, fade-out end).
- Delivery check for the overlay (mandatory, before sending): render stills at EVERY chapter start, every card start, the first 12 s second by second, the last 15 s, and compose a contact sheet; look for overlapping text, text on top of the HUD, and text cut at the edges. Say in the delivery message which frames were checked.

### R14. Packaging formula and NO cold open (owner's order, 16/11/2026, Marseille)
- **No cold open, ever.** The video starts from its first year, normally. Nobody asked to open with a dramatic event. Chapters and the montage command use the times of the render as is (no cold-open variant, no `-ss` window). This overrides the cold-open note in `analisi/ctr/MINIATURE.md` ("Owner's review 14/11").
- **Thumbnail = the series formula**: `<first year> > NOW` with two full halves of city (Lyon: 43 BC > NOW), city name huge at the bottom, no flag, no hook event. Crop with `--lbox/--rbox` to exclude sea and empty land; check that the first-year text is not clipped (`--text-size`, `--lx`).
- **Title = the series formula**: `EVOLUTION OF <CITY> | 3D City Timelapse (<first year>-NOW) | No AI`. A historical event is a chapter, never the theme of the title or thumbnail.
- Before deciding thumbnail or title, LOOK at the last approved ones (`cities/lyon/copertina`, `cities/lyon/METADATA.md`); the generic rules are not enough.
