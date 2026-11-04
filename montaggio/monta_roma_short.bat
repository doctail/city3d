@echo off
rem Year Built - ROMA: Short verticale 1080x1920, 28 s. Tutto il video (da 0:09 a 4:26, 753 a.C. -> 2026) accelerato 9,7 volte,
rem poi l'ultimo fotogramma fermo 1,5 s sotto "FULL VIDEO". Il 16:9 sta al centro su una copia sfocata di se stesso.
rem Metti in questa cartella: roma_full.mp4, roma_short.webm, roma_short.m4a e lancia questo file.
ffmpeg -y -ss 9.0 -t 257 -i roma_full.mp4 -c:v libvpx-vp9 -i roma_short.webm -i roma_short.m4a -filter_complex "[0:v]setpts=PTS*0.10311,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.04:saturation=1.10,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart roma_short_finale.mp4
echo.
echo FATTO: roma_short_finale.mp4
pause
