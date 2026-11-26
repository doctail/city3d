# New York: final montage (Windows cmd, no .bat), updated 26/11/2026 on the real overlay and audio
No cold open (R14): the video starts as rendered; chapters use the render's times.
Put in one folder: `nyc_full.mp4` (pod render), `nyc_overlay.webm`, `nyc_audio.m4a` (names as in `montaggio/monta_kit.sh`; `python -m kit montaggio nyc --overlay` + `sfx_kit.py` make `out/nyc_overlay.webm` and `out/nyc_audio.m4a`). ffmpeg in the PATH. Open `cmd` in that folder. One line (identical to `monta_kit.sh nyc long`, only the slug differs):

## Merge: nyc_finale.mp4
```
ffmpeg -y -i nyc_full.mp4 -c:v libvpx-vp9 -i nyc_overlay.webm -i nyc_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart nyc_finale.mp4
```
The overlay is 41 MB (over 30 MB), so it is delivered as two files: `out/nyc_overlay_1.webm` (23 MB, frames 0-7199) and `out/nyc_overlay_2.webm` (18 MB, frames 7200-13305). Put both in the folder with `nyc_full.mp4` and `nyc_audio.m4a` (14 MB), run this line FIRST (it makes `nyc_overlay.webm`), then the merge line above:
```
(echo file nyc_overlay_1.webm)>list.txt && (echo file nyc_overlay_2.webm)>>list.txt && ffmpeg -y -f concat -safe 0 -i list.txt -c copy nyc_overlay.webm
```
(Tested here: the concat gives 554.5 s.)

R13 DONE 24-26/11/2026 on the real overlay (stills composited on a grey-blue background, one by one): first 12 s second by second, title card, every chapter card (I-X), every monument card, every stop caption, every monument label window, the Subscribe clip, CTA, the whole Sources card and the last 15 s. Fixed: population `~NaN` at 1609 (log of 0), cards and stop captions covering the polity chip (now right-aligned), monument labels never shown (`label_area` was in meters, now screen pixels), label covering the population box (flips below), Sources list split mid-sentence. Checks of timing from the schedule (confirmed on the real years.json): title 9.7 s; chapter I 0:12; VI 4:49, VII 5:01; CTA 541.9 s (9:01.9); Sources 546.4 s (9:06); end 554.4 s (9:14). Audio: `out/nyc_audio.m4a` 554.4 s, music A+B, -13.9 LUFS, true peak -0.7 dBTP, no gap over 1 s, no clipping.
OPEN: `years.json` has 13,186 frames (549.4 s), 119-120 fewer than the schedule. Check `nyc_full.mp4` is 554.4 s; if shorter, `-shortest` cuts the end (Sources card).
