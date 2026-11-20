#!/bin/bash
# raw (numpy) -> loudnorm 2 passi a -14 LUFS, TP -1 dBTP. Uso: mix_audio.sh <workdir>
set -e; W=$1; cd "$(dirname "$0")"
python3 cozy_audio.py $W/raw.wav
M=$(ffmpeg -nostats -i $W/raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -v error -y -i $W/raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 44100 $W/cozy_test_audio.wav
