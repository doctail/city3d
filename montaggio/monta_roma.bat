@echo off
rem Year Built - ROMA: montaggio finale del video lungo (4:32). Metti in questa cartella:
rem   roma_full.mp4 (render completo del pod), roma_overlay.webm (grafiche), roma_audio.m4a (musica + effetti, -14 LUFS)
rem e lancia questo file. Serve ffmpeg nel PATH. Colore: contrasto 1,04 e saturazione 1,10 (il render di Roma e' gia' saturo).
ffmpeg -y -i roma_full.mp4 -c:v libvpx-vp9 -i roma_overlay.webm -i roma_audio.m4a -filter_complex "[0:v]eq=contrast=1.04:saturation=1.10[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart roma_finale.mp4
echo.
echo FATTO: roma_finale.mp4 (controlla 0:00-0:14 apertura e Romolo, 1:25 Colosseo, 2:11 Alarico, 2:59 terremoto, 3:54 Porta Pia, 4:30 finale)
pause
