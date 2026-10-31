@echo off
rem Year Built - PARIGI: Short verticale 1080x1920, 28 s. Tutto il video (da 0:09,5 a 5:50, 1190 -> 2026) accelerato 12,8 volte,
rem poi l'ultimo fotogramma fermo 1,5 s sotto "FULL VIDEO". Il 16:9 sta al centro su una copia sfocata di se stesso.
rem Metti in questa cartella: parigi_full.mp4, parigi_short.webm, parigi_short.m4a e lancia questo file.
ffmpeg -y -ss 9.5 -t 340.5 -i parigi_full.mp4 -c:v libvpx-vp9 -i parigi_short.webm -i parigi_short.m4a -filter_complex "[0:v]setpts=PTS*0.07783,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.04:saturation=1.25,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart parigi_short_finale.mp4
echo.
echo FATTO: parigi_short_finale.mp4
pause
