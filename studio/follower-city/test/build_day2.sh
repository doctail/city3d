#!/bin/bash
# Day 2: audio sintetizzato (loudnorm -14 LUFS) + video muto 270x480 (upscale lanczos 1080x1920) -> cozy_day2_1to12.mp4
# Prerequisito: python3 ../blender/anim_day2.py assemble  (produce ../blender/cozy_day2_silent.mp4)
set -e; cd "$(dirname "$0")"; W=${1:-/tmp}
python3 cozy_audio_day2.py $W/d2raw.wav
M=$(ffmpeg -nostats -i $W/d2raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -v error -y -i $W/d2raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 44100 $W/d2.wav
ffmpeg -v error -y -i ../blender/cozy_day2_silent.mp4 -i $W/d2.wav -vf "scale=1080:1920:flags=lanczos" -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -c:a aac -b:a 160k -shortest -movflags +faststart cozy_day2_1to12.mp4
ls -l cozy_day2_1to12.mp4
