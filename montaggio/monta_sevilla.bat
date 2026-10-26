@echo off
rem Year Built - Siviglia: unisce video completo + grafiche (etichette, didascalie, HUD) + audio (2 tracce + effetti sonori)
rem Metti in questa cartella: sevilla_full.mp4, sevilla_overlay.webm, sevilla_audio.m4a e lancia questo file.
rem Colori: il render e' gia' saturo (~111 misurato sul light): solo ritocco leggero come Copenaghen (1,08), NON x1,7.
ffmpeg -y -i sevilla_full.mp4 -c:v libvpx-vp9 -i sevilla_overlay.webm -i sevilla_audio.m4a -filter_complex "[0:v]eq=contrast=1.03:saturation=1.08[b];[b][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart sevilla_finale.mp4
echo.
echo FATTO: sevilla_finale.mp4
pause
