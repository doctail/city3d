#!/bin/bash
# Day 2 v3 rimontaggio (nessun nuovo render): audio -14 LUFS + montaggio dai frame unici esistenti -> test/cozy_day2_v3_remix.mp4
set -e; D=$(cd "$(dirname "$0")" && pwd); W=/tmp/d2v3a; mkdir -p $W
$D/mix_audio_day2_v3.sh $W
cd $D/../blender && python3 -u day2_v3_compose.py
ffmpeg -y -loglevel error -i $D/cozy_day2_v3_silent.mp4 -i $W/day2v3_audio.wav -c:v copy -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart $D/cozy_day2_v3_remix.mp4
ls -l $D/cozy_day2_v3_remix.mp4
