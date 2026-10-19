#!/bin/bash
# Copenaghen: rende il livello grafico trasparente a pezzi da 800 fotogrammi (riprende se interrotto), poi li unisce.
# Uso: in una cartella Remotion con src/{copenhagen_overlay,hud,cities}.jsx e public/*.json:  bash ov_chunks_cph.sh
cd ${OVPROJ:-/home/claude/cphedit}; B=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell; O=${OVDIR:-ovp}; mkdir -p $O
N=12276
for a in $(seq 0 800 $((N - 1))); do b=$((a+799)); [ $b -gt $((N - 1)) ] && b=$((N - 1)); f=$O/p_$(printf %05d $a).webm
  [ -s $f.ok ] && continue
  npx remotion render src/copenhagen_overlay.jsx CopenhagenOverlay $f --frames=$a-$b --codec=vp9 --image-format=png --pixel-format=yuva420p --concurrency=2 --browser-executable=$B --log=error && echo ok > $f.ok
  echo "pezzo $a-$b fatto $(date +%H:%M)"
done
ls $O/p_*.webm | sed "s/^/file '/;s/$/'/" > $O/list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i $O/list.txt -c copy ${OVOUT:-copenhagen_overlay.webm} && echo FATTO
