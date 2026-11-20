# New York: final montage (Windows cmd, no .bat), 20/11/2026: PROVISIONAL, no render exists yet
No cold open (R14): the video starts as rendered; chapters use the render's times.
Put in one folder: `nyc_full.mp4` (pod render), `nyc_overlay.webm`, `nyc_audio.m4a` (names as in `montaggio/monta_kit.sh`; `python -m kit montaggio nyc --overlay` + `sfx_kit.py` make `out/nyc_overlay.webm` and `out/nyc_audio.m4a`). ffmpeg in the PATH. Open `cmd` in that folder. One line (identical to `monta_kit.sh nyc long`, only the slug differs):

## Merge: nyc_finale.mp4
```
ffmpeg -y -i nyc_full.mp4 -c:v libvpx-vp9 -i nyc_overlay.webm -i nyc_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart nyc_finale.mp4
```
If the overlay is over 30 MB and has to be split in two downloads (as Marseille), one line in the same folder, then the line above:
```
(echo file nyc_overlay_1.webm)>list.txt && (echo file nyc_overlay_2.webm)>>list.txt && ffmpeg -y -f concat -safe 0 -i list.txt -c copy nyc_overlay.webm
```
Check (from `schedule_nyc.json`, to confirm on the render): title at 9.5 s; chapter I at 0:12; VI at 4:49 and VII at 5:01; "Which city should grow next" at 9:01.9; Sources card at 9:06 (546.4 s); end 9:14 (554.4 s). Overlay checks of R13 (stills at every chapter start, every card, first 12 s, last 15 s) are to be done on the real overlay: NOT done, nothing exists to check yet.
Cost of the pod: NOT measured. Local basis only: scene build 254 s, 41.6 s per 1080p frame on CPU, 10.3 GB RAM (not a pod figure).
