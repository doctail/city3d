#!/bin/bash
# rende il livello grafico a pezzi da 800 fotogrammi (riprende se interrotto), poi li unisce
cd /home/claude/city; B=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell; O=${OVDIR:-/home/claude/nycedit/ovp}; mkdir -p $O
LIM=${LIM:-99}; n=0
for a in $(seq 0 800 7838); do b=$((a+799)); [ $b -gt 7838 ] && b=7838; f=$O/p_$(printf %05d $a).webm
  [ -s $f.ok ] && continue; n=$((n+1)); [ $n -gt $LIM ] && exit 0
  npx remotion render src/${OVC:-nyc_overlay}.jsx ${OVID:-NycOverlay} $f --frames=$a-$b --codec=vp9 --image-format=png --pixel-format=yuva420p --concurrency=2 --browser-executable=$B --log=error && echo ok > $f.ok
done
ls $O/p_*.webm | sed "s/^/file '/;s/$/'/" > $O/list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i $O/list.txt -c copy ${OVOUT:-/home/claude/nycedit/nyc_overlay.webm} && echo FATTO
