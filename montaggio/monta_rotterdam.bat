@echo off
rem Year Built - Rotterdam: unisce video completo + grafiche + audio (musica con effetti sonori)
rem Metti in questa cartella: rotterdam_full.mp4, rotterdam_overlay.webm, rotterdam_audio.m4a e lancia questo file.
rem Colori: saturazione x1,7 e contrasto x1,06 (analisi concorrenti, 17 ott 2026).
ffmpeg -y -i rotterdam_full.mp4 -c:v libvpx-vp9 -i rotterdam_overlay.webm -i rotterdam_audio.m4a -filter_complex "[0:v]eq=contrast=1.06:saturation=1.7[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart rotterdam_finale.mp4
echo.
echo FATTO: rotterdam_finale.mp4
pause
