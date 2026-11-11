@echo off
rem Year Built - KIT: montaggio finale per qualsiasi citta'. Uso:  monta_kit.bat <slug> [short]
rem Metti nella cartella: <slug>_full.mp4 (render del pod), <slug>_overlay.webm, <slug>_audio.m4a (lungo)
rem                      oppure <slug>_short_overlay.webm, <slug>_short_audio.m4a (Short). Serve ffmpeg nel PATH.
rem Colore: contrasto 1,03 / saturazione 1,08 (cambia CONTRAST e SAT sotto; Roma: 1,04 / 1,10).
rem Per lo Short servono i valori A (secondo d'inizio), B (secondo di fine) e SP (=(28-1,5)/(B-A)) da public\kit_<slug>.json -> "short"; sono passati come 3o,4o,5o argomento:
rem   monta_kit.bat roma short 9 266 0.10311
setlocal
set SLUG=%1
if "%SLUG%"=="" ( echo uso: monta_kit.bat ^<slug^> [short A B SP] & exit /b 1 )
set CONTRAST=1.03
set SAT=1.08
if /i "%2"=="short" goto SHORT
ffmpeg -y -i %SLUG%_full.mp4 -c:v libvpx-vp9 -i %SLUG%_overlay.webm -i %SLUG%_audio.m4a -filter_complex "[0:v]eq=contrast=%CONTRAST%:saturation=%SAT%[b];[1:v][b]scale2ref=flags=lanczos[o][b2];[b2][o]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -shortest -movflags +faststart %SLUG%_finale.mp4
echo.
echo FATTO: %SLUG%_finale.mp4
goto END
:SHORT
set A=%3
set B=%4
set SP=%5
if "%SP%"=="" ( echo uso short: monta_kit.bat %SLUG% short A B SP & exit /b 1 )
set /a LEN=%B%-%A%
ffmpeg -y -ss %A% -t %LEN% -i %SLUG%_full.mp4 -c:v libvpx-vp9 -i %SLUG%_short_overlay.webm -i %SLUG%_short_audio.m4a -filter_complex "[0:v]setpts=PTS*%SP%,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=%CONTRAST%:saturation=%SAT%,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart %SLUG%_short_finale.mp4
echo.
echo FATTO: %SLUG%_short_finale.mp4
:END
pause
