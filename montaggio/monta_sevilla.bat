@echo off
rem Year Built - Siviglia: unisce video completo + grafiche + musica
rem Metti in questa cartella: sevilla_full.mp4, sevilla_overlay.webm, musica.mp3 (The Shining in Dubai - Unicorn Heads, 5:27) e lancia questo file.
rem Colori: saturazione x1,7 e contrasto x1,06 (analisi concorrenti, 17 ott 2026). Musica: parte da 0:00, dissolvenza finale dal secondo 322.
ffmpeg -y -i sevilla_full.mp4 -c:v libvpx-vp9 -i sevilla_overlay.webm -i musica.mp3 -filter_complex "[0:v]eq=contrast=1.06:saturation=1.7[b];[b][1:v]overlay=format=auto,format=yuv420p[v];[2:a]afade=t=out:st=322:d=4.6[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -shortest -movflags +faststart sevilla_finale.mp4
echo.
echo FATTO: sevilla_finale.mp4
pause
