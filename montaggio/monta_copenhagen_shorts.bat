@echo off
rem Year Built - Copenaghen: i 3 Shorts (A controllo, B incendio 1728, C Christiansborg).
rem Metti in questa cartella: copenhagen_shortA.mp4, _shortB.mp4, _shortC.mp4 (dal pod), copenhagen_shortA.webm, _shortB.webm, _shortC.webm (grafiche) e copenhagen_shortA.m4a, _shortB.m4a, _shortC.m4a (musica + effetti).
call :one A
call :one B
call :one C
echo.
echo FATTO: copenhagen_shortA_finale.mp4, _shortB_finale.mp4, _shortC_finale.mp4
pause
goto :eof
:one
ffmpeg -y -i copenhagen_short%1.mp4 -c:v libvpx-vp9 -i copenhagen_short%1.webm -i copenhagen_short%1.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart copenhagen_short%1_finale.mp4
goto :eof
