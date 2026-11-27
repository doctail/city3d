# Pittsburgh: SHORT (44 s, whole video sped up)

## Command (Windows cmd, one line, in the folder with pittsburgh_full.mp4 and pittsburgh_audio.m4a)
ffmpeg -y -ss 14.5 -t 585.5 -i pittsburgh_full.mp4 -i pittsburgh_audio.m4a -filter_complex "[0:v]setpts=PTS/13.3,fps=24,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608:flags=lanczos[fg];[bg][fg]overlay=0:656,format=yuv420p[v];[1:a]atrim=20:64,asetpts=PTS-STARTPTS,afade=t=in:d=1,afade=t=out:st=42:d=2[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -t 44 -movflags +faststart pittsburgh_short.mp4

Tested on Linux with a 1920x1080 test video: output h264 1080x1920 + AAC. Not run on the real pittsburgh_full.mp4 (not available here). Layout: 16:9 video centered over a blurred, darkened copy (Valencia style); 14.5 s to 600 s of the video (1754 to 2026) at 13.3x. No text overlay (no short overlay file exists). Music: excerpt 0:20-1:04 of the long video's audio, with fades.

## Title
272 Years of Pittsburgh in 44 Seconds (Every Real Building) #shorts

## Description
Pittsburgh grows in 3D, from Fort Duquesne in 1754 to the skyline of today, one real building at a time. 272 years in 44 seconds.

Full video (10 min, NO AI, every building in its real year): [link to the full video]

Which city should grow next? Tell me in the comments.

#shorts #pittsburgh #timelapse #citygrowth #3d #history

## Tags
pittsburgh, pittsburgh history, pittsburgh timelapse, city growth, 3d city timelapse, city timelapse, fort pitt, steel city, urban growth, before and after, no ai

## Pinned comment
Full 10-minute version, with every date and source: [link to the full video] . Find your building and tell me its year!

## Settings
Not made for kids. Related video: the Pittsburgh long video. Music: Waking to Reality (Unicorn Heads), YouTube Audio Library. Publish 2 days after the long video.
