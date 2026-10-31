#!/bin/bash
# rende il livello grafico a pezzi da 800 fotogrammi (riprende se interrotto), poi li unisce
cd /home/claude/city; B=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell; O=${OVDIR:-/home/claude/nycedit/ovp}; mkdir -p $O
LIM=${LIM:-99}; n=0
LAST=${LAST:-7838}
for a in $(seq 0 800 $LAST); do b=$((a+799)); [ $b -gt $LAST ] && b=$LAST; f=$O/p_$(printf %05d $a).webm
  [ -s $f.ok ] && continue; n=$((n+1)); [ $n -gt $LIM ] && exit 0
  npx remotion render src/${OVC:-nyc_overlay}.jsx ${OVID:-NycOverlay} $f --frames=$a-$b --codec=vp9 --image-format=png --pixel-format=yuva420p --concurrency=${CONC:-2} --browser-executable=$B --log=error && echo ok > $f.ok
done
[ $(ls $O/*.ok 2>/dev/null | wc -l) -eq $(seq 0 800 $LAST | wc -l) ] || { echo "ERRORE: pezzi mancanti"; exit 1; }
ls $O/p_*.webm | sed "s/^/file '/;s/$/'/" > $O/list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i $O/list.txt -c copy ${OVOUT:-/home/claude/nycedit/nyc_overlay.webm} && echo FATTO
