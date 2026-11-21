#!/bin/bash
# raw (numpy) -> lowpass 15k + gain (~+8.2 dB) + limiter: ~-14 LUFS integrati, true peak ~-1.7 dBTP (misurato anche dopo AAC). Uso: mix_audio_day2_v3.sh <workdir>
set -e; W=$1; cd "$(dirname "$0")"
python3 cozy_audio_day2_v3.py $W/raw.wav
ffmpeg -v error -y -i $W/raw.wav -af "lowpass=f=15000,volume=8.2dB,alimiter=limit=0.7:attack=5:release=120:level=0" -ar 44100 $W/day2v3_audio.wav
