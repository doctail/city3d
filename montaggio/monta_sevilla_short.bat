@echo off
rem Year Built - Siviglia: Short "What happened to Seville's mosque?" (0:24-0:54,5 del video lungo, 1335 -> 1570), verticale 1080x1920.
rem Metti in questa cartella: sevilla_full.mp4, sevilla_short.webm, sevilla_short.m4a e lancia questo file.
rem Il 16:9 sta al centro su una copia sfocata di se stesso (nessun ritaglio). Audio: stesso mix del lungo (musica + effetti), -14 LUFS.
ffmpeg -y -ss 24 -t 30.5 -i sevilla_full.mp4 -c:v libvpx-vp9 -i sevilla_short.webm -i sevilla_short.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart sevilla_short_finale.mp4
echo.
echo FATTO: sevilla_short_finale.mp4
pause
