@echo off
rem Year Built - Copenaghen: unisce video completo (con tramonto gia' fuso) + grafiche + audio (2 tracce + effetti sonori)
rem Metti in questa cartella: copenhagen_full.mp4, copenhagen_overlay.webm, copenhagen_audio.m4a e lancia questo file.
rem Colori: il render ha gia' la saturazione giusta (stile leggibile, ~84): solo un ritocco leggero (1,08), non piu' x1,7.
ffmpeg -y -i copenhagen_full.mp4 -c:v libvpx-vp9 -i copenhagen_overlay.webm -i copenhagen_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart copenhagen_finale.mp4
echo.
echo FATTO: copenhagen_finale.mp4
pause
