@echo off
rem Year Built - Madrid: unisce video completo + grafiche + musica
rem Metti in questa cartella: madrid_full.mp4, madrid_overlay.webm, musica.mp3 e lancia questo file.
ffmpeg -y -i madrid_full.mp4 -c:v libvpx-vp9 -i madrid_overlay.webm -i musica.mp3 -filter_complex "[0:v][1:v]overlay=format=auto,format=yuv420p[v];[2:a]afade=t=out:st=322:d=4.6[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -shortest -movflags +faststart madrid_finale.mp4
echo.
echo FATTO: madrid_finale.mp4
pause
