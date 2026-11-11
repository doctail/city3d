#!/bin/bash
# Kit Year Built: rende il livello grafico (kit_overlay.jsx) a pezzi da 800 fotogrammi, riprende se interrotto, poi unisce i pezzi.
# Uso (da qualunque cartella):  bash montaggio/ov_kit.sh <slug> [long|short]
#   long  -> out/<slug>_overlay.webm        (KitOverlay, 1920x1080 trasparente VP9+alfa)
#   short -> out/<slug>_short_overlay.webm  (KitShort, 1080x1920)
# Prima esegue kit_city.py se public/kit_<slug>.json manca. Variabili: CHUNK (800), CONC (2), LIM (n. massimo di pezzi per lancio),
#   BROWSER (eseguibile chromium; se vuoto lo cerca da solo), STORY (percorso story.json per kit_city.py), FRAMES=a-b (solo per prove, niente concat).
set -e
SLUG=${1:?uso: ov_kit.sh <slug> [long|short]}; MODE=${2:-long}
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(dirname "$HERE"); cd "$HERE"
OUT=$ROOT/out; mkdir -p "$OUT"
[ -d node_modules ] || npm install --no-audit --no-fund
[ -s public/kit_$SLUG.json ] || python3 kit_city.py $SLUG ${STORY:+--story "$STORY"}
if [ "$MODE" = short ]; then COMP=KitShort; KEY=short.n; NAME=${SLUG}_short_overlay; else COMP=KitOverlay; KEY=n; NAME=${SLUG}_overlay; fi
N=$(node -p "require('./public/kit_$SLUG.json').$KEY"); LAST=$((N-1))
# chromium: BROWSER, poi headless shell di Playwright, poi chromium completo, poi quello di sistema (altrimenti Remotion lo scarica)
if [ -z "$BROWSER" ]; then
  for p in /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell /opt/pw-browsers/chromium-*/chrome-linux*/chrome \
           "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux*/chrome; do
    [ -x "$p" ] && { BROWSER=$p; break; }; done
  [ -z "$BROWSER" ] && BROWSER=$(command -v chromium chromium-browser google-chrome 2>/dev/null | head -1)
fi
BARG=(); [ -n "$BROWSER" ] && BARG=(--browser-executable="$BROWSER"); echo "browser: ${BROWSER:-(scaricato da Remotion)}  composizione $COMP  fotogrammi 0-$LAST"
PROPS="{\"slug\":\"$SLUG\"}"; CHUNK=${CHUNK:-800}; D=$OUT/${NAME}_pezzi; mkdir -p "$D"
if [ -n "$FRAMES" ]; then   # prova: un solo intervallo
  npx remotion render kit_overlay.jsx $COMP "$OUT/${NAME}_prova.webm" --props="$PROPS" --frames=$FRAMES --codec=vp9 --image-format=png --pixel-format=yuva420p --concurrency=${CONC:-2} "${BARG[@]}" --log=error; exit 0; fi
n=0; TOT=0
for a in $(seq 0 $CHUNK $LAST); do b=$((a+CHUNK-1)); [ $b -gt $LAST ] && b=$LAST; TOT=$((TOT+1)); f=$D/p_$(printf %05d $a).webm
  [ -s $f.ok ] && continue; n=$((n+1)); [ $n -gt ${LIM:-9999} ] && exit 0
  npx remotion render kit_overlay.jsx $COMP $f --props="$PROPS" --frames=$a-$b --codec=vp9 --image-format=png --pixel-format=yuva420p --concurrency=${CONC:-2} "${BARG[@]}" --log=error && echo ok > $f.ok
  echo "pezzo $a-$b fatto $(date +%H:%M)"
done
[ $(ls $D/*.ok 2>/dev/null | wc -l) -eq $TOT ] || { echo "ERRORE: pezzi mancanti (rilancia: riprende da dove era)"; exit 1; }
FF=$(command -v ffmpeg || ls /opt/pw-browsers/ffmpeg-*/ffmpeg-linux | head -1)
ls $D/p_*.webm | sed "s/^/file '/;s/$/'/" > $D/list.txt
$FF -loglevel error -y -f concat -safe 0 -i $D/list.txt -c copy "$OUT/$NAME.webm" && echo "FATTO: $OUT/$NAME.webm"
