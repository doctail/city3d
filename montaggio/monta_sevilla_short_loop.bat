@echo off
rem Year Built - Siviglia: Short PRINCIPALE "778 Years of Seville in 30 Seconds": tutto il video finale accelerato (x11), verticale 1080x1920, 29 s.
rem Metti in questa cartella: sevilla_finale.mp4 (uscita di monta_sevilla.bat) e sevilla_short_loop.m4a, poi lancia questo file.
rem Si usano i primi 319 s (senza il cartello finale): il video parte nel 2026 di giorno e finisce nel 2026 di notte, cosi' il loop riparte pulito.
rem Il 16:9 sta al centro su una copia sfocata (nessun ritaglio); titolo sopra, rimando al canale sotto. Musica: Monument (TrackTribe) dal suo 0:25, -14 LUFS.
ffmpeg -y -i sevilla_finale.mp4 -i sevilla_short_loop.m4a -filter_complex "[0:v]trim=0:319,setpts=(PTS-STARTPTS)/11.0,fps=30,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.15[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656,drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='778 YEARS OF SEVILLE':fontsize=86:fontcolor=0xF6F1E7:borderw=6:bordercolor=0x101214:x=(w-text_w)/2:y=300,drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='IN 30 SECONDS':fontsize=64:fontcolor=0xE8B04A:borderw=5:bordercolor=0x101214:x=(w-text_w)/2:y=410,drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='FULL VIDEO ON THE CHANNEL':fontsize=40:fontcolor=0xF6F1E7:borderw=4:bordercolor=0x101214:x=(w-text_w)/2:y=1500,format=yuv420p[v]" -map "[v]" -map 1:a -t 29 -c:v libx264 -preset slow -crf 18 -c:a copy -movflags +faststart sevilla_short_loop_finale.mp4
echo.
echo FATTO: sevilla_short_loop_finale.mp4
pause
