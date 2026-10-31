@echo off
rem Year Built - PARIGI: montaggio finale del video lungo (6:30). Metti in questa cartella:
rem   parigi_full.mp4 (il render completo del pod), parigi_overlay.webm (grafiche), parigi_audio.m4a (musica + effetti, -14 LUFS)
rem e lancia questo file. Serve ffmpeg nel PATH. Colore: contrasto 1,04 e saturazione 1,25 (il render e' spento: SATAVG 9,7).
rem Le grafiche vengono adattate alla risoluzione del render (1080p o 1440p) da scale2ref.
ffmpeg -y -i parigi_full.mp4 -c:v libvpx-vp9 -i parigi_overlay.webm -i parigi_audio.m4a -filter_complex "[0:v]eq=contrast=1.04:saturation=1.25[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart parigi_finale.mp4
echo.
echo FATTO: parigi_finale.mp4 (controlla 0:00-0:15, 2:15 Bastiglia, 3:39 Haussmann, 4:30 Eiffel, 6:28 finale)
pause
