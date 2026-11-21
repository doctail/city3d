#!/bin/bash
# Day 2 REALE finale: audio (-14 LUFS, TP<=-1.8) + montaggio frame + mux -> test/cozy_day2_final.mp4 (dopo il render in blender/day2_final_frames)
set -e; D=$(cd "$(dirname "$0")" && pwd); W=/tmp/d2a; mkdir -p $W
$D/mix_audio_day2_final.sh $W
cd $D/../blender && python3 -u day2_compose.py
ffmpeg -y -loglevel error -i $D/cozy_day2_silent.mp4 -i $W/day2_audio.wav -c:v copy -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart $D/cozy_day2_final.mp4
ls -l $D/cozy_day2_final.mp4
