@echo off
rem Year Built - Siviglia: Short "What happened to Seville's mosque?" (0:24-0:54,5 del video lungo, 1335 -> 1570), verticale 1080x1920.
rem Metti in questa cartella: sevilla_full.mp4, sevilla_short.webm, musica.mp3 e lancia questo file.
rem Il 16:9 sta al centro su una copia sfocata di se stesso (nessun ritaglio); musica dallo stesso punto del lungo (24 s), -15 LUFS.
ffmpeg -y -ss 24 -t 30.5 -i sevilla_full.mp4 -c:v libvpx-vp9 -i sevilla_short.webm -ss 24 -t 30.5 -i musica.mp3 -filter_complex "[0:v]eq=contrast=1.06:saturation=1.7,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v];[2:a]afade=t=in:d=0.3,afade=t=out:st=29:d=1.5,loudnorm=I=-15:TP=-1.5:LRA=11[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -shortest -movflags +faststart sevilla_short_finale.mp4
echo.
echo FATTO: sevilla_short_finale.mp4
pause
