# Valencia: SHORT (28 s, from the long video)

## Command (Windows cmd, in the folder with valencia_full.mp4, valencia_short_overlay.webm, valencia_short_audio.m4a)
ffmpeg -y -ss 10.5 -t 495 -i valencia_full.mp4 -c:v libvpx-vp9 -i valencia_short_overlay.webm -i valencia_short_audio.m4a -filter_complex "[0:v]setpts=PTS*0.053535,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart valencia_short_finale.mp4

## Title
788 years of Valencia in 30 seconds #shorts

## Description
Valencia grew around the Turia river, was flooded in 1957, and then the river was moved. 788 years in 30 seconds, 1238 to today.

Full video (8 min, NO AI, every building in its real year): https://youtu.be/tMGOl-1gL_Y

Which city should grow next? Tell me in the comments.

#shorts #valencia #timelapse #citygrowth #3d

## Pinned comment
Full 8-minute version, with every date and source: https://youtu.be/tMGOl-1gL_Y . Find your building and tell me its year!

## Settings
Not made for kids. Related video: the Valencia long video. Music: Waking to Reality (Unicorn Heads), Monument (TrackTribe), YouTube Audio Library.
