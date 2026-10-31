@echo off
rem Year Built - PARIGI: estrae 6 fotogrammi candidati per la copertina dal render completo (PNG pieni). Caricali in chat.
rem 5:49 panoramica finale di giorno (2026, Eiffel e Sacre-Coeur) - 5:43 Notre-Dame - 4:33 Eiffel - 3:45 Haussmann - 0:01 Parigi oggi - 0:15 1200
for %%t in (349 343.5 273 225 1 15) do ffmpeg -y -loglevel error -ss %%t -i parigi_full.mp4 -frames:v 1 cover_%%t.png
echo FATTO: cover_*.png
pause
