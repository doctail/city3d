#!/bin/bash
# Day 1 finale: audio (-14 LUFS, TP<=-2) + montaggio frame + mux -> cozy_day1_final.mp4 (dopo il render in blender/day1_final_frames)
set -e; D=$(cd "$(dirname "$0")" && pwd); W=/tmp/d1a; mkdir -p $W
$D/mix_audio_day1.sh $W
cd $D/../blender && python3 -u anim_day1_final.py assemble
ffmpeg -y -loglevel error -i $D/cozy_day1_silent.mp4 -i $W/day1_audio.wav -c:v copy -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart $D/cozy_day1_final.mp4
ls -l $D/cozy_day1_final.mp4
