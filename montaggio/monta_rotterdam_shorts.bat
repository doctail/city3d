@echo off
rem Year Built - Rotterdam: i 3 Shorts (A controllo, B 14 maggio 1940, C skyline).
rem Metti in questa cartella: rotterdam_shortA.mp4, _shortB.mp4, _shortC.mp4, rotterdam_shortA.webm, _shortB.webm, _shortC.webm, musica.mp3
rem Musica: A dal finale (4:00), B dal calo del brano (3:20: il silenzio cade sul centro vuoto), C dal crescendo (3:57).
call :one A 240 27.4
call :one B 200 24.3
call :one C 237 25.3
echo.
echo FATTO: rotterdam_shortA_finale.mp4, _shortB_finale.mp4, _shortC_finale.mp4
pause
goto :eof
:one
ffmpeg -y -i rotterdam_short%1.mp4 -c:v libvpx-vp9 -i rotterdam_short%1.webm -ss %2 -i musica.mp3 -filter_complex "[0:v]eq=contrast=1.06:saturation=1.7[b];[b][1:v]overlay=format=auto,format=yuv420p[v];[2:a]afade=t=in:d=0.3,afade=t=out:st=%3:d=1.7[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -shortest -movflags +faststart rotterdam_short%1_finale.mp4
goto :eof
