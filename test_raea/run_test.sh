#!/usr/bin/env bash
# TEST A/B sullo STESSO pod: New York, primi 20 s (480 fotogrammi, 24 fps, 1920x1080, camera e anni di schedule_nyc.json)
#   A) Blender/Cycles (build_render.py, 8 campioni, OptiX, parametri del render finale)   B) raea (test_raea/raea/nyc20.tsx)
# Lancio (terminale del pod, template PyTorch, RTX 5080):
#   cd /workspace && git clone -b claude/install-two-repos-776mx3 https://github.com/doctail/city3d && bash city3d/test_raea/run_test.sh
# Variabili: ONLY=A | ONLY=B (una sola meta'), FORCE_B=1 (lancia B anche senza GPU NVIDIA visibile da Vulkan),
#            B_DESPITE=NOME_CHECK (se raea rifiuta il render per un controllo, solo se il proprietario lo accetta), B_QUALITY=high.
# Tutti i tempi (date +%s) vanno in test_raea/out/tempi.txt, una riga per fase. Non si ferma al primo errore: ogni fase dice rc=.
cd "$(dirname "$0")/.." || exit 2
REPO=$PWD; T=$REPO/test_raea; OUT=$T/out; mkdir -p "$OUT"
TIMES=$OUT/tempi.txt; : > "$TIMES"
PY=${PY:-/workspace/bl/bin/python}
NF=480; ONLY=${ONLY:-AB}
export PATH="$HOME/.local/bin:$HOME/.raea/bin:/root/.cargo/bin:$PATH"
T0=$(date +%s)
CUR=$OUT/fase_corrente.txt
rec(){ printf '%-44s %10s   %s\n' "$1" "$2" "${3:-}" | tee -a "$TIMES"; }   # il valore porta la sua unita'
phase(){ local _pn=$1; shift; echo "$_pn" > "$CUR"; echo; echo "=== $_pn  (da inizio: $(( $(date +%s) - T0 )) s)"; local _s _e _rc; _s=$(date +%s); "$@"; _rc=$?; _e=$(date +%s); rec "$_pn" "$((_e - _s)) s" "rc=$_rc"; return $_rc; }

# ---- picchi RAM e VRAM (campiona ogni 2 s; la RAM e' quella usata da tutto il pod, meno il valore di partenza) ----
mon_start(){ : > "$OUT/.ram"; : > "$OUT/.vram"
  ( while :; do awk '/MemTotal/{t=$2}/MemAvailable/{a=$2}END{print int((t-a)/1024)}' /proc/meminfo >> "$OUT/.ram"; nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> "$OUT/.vram" 2>/dev/null; sleep 2; done ) & MON=$!; }
mon_stop(){ kill "$MON" 2>/dev/null; wait "$MON" 2>/dev/null
  local r0 rp v0 vp; r0=$(head -1 "$OUT/.ram"); rp=$(sort -n "$OUT/.ram" | tail -1); v0=$(head -1 "$OUT/.vram"); vp=$(sort -n "$OUT/.vram" | tail -1)
  rec "$1 picco RAM pod" "${rp:-?} MB" "(partenza ${r0:-?} MB, aumento $(( ${rp:-0} - ${r0:-0} )) MB)"; rec "$1 picco VRAM" "${vp:-?} MB" "(partenza ${v0:-?} MB, aumento $(( ${vp:-0} - ${v0:-0} )) MB)"; }

# =====================================================================================================================
echo "######## TEST A/B  Blender / raea  -  New York 20 s ($NF fotogrammi, 1920x1080) ########"
echo "== GPU"; nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
GPUNAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1); echo "$GPUNAME" | grep -qi 5080 || echo "ATTENZIONE: la GPU non e' una RTX 5080 ($GPUNAME): il confronto vale solo per questo pod."
CU=$(python3 -c "import ctypes;print(ctypes.CDLL('libcuda.so.1').cuInit(0))" 2>&1); echo "cuInit = $CU (0 = ok)"
[ "$CU" = "0" ] || { echo "STOP: la GPU non si apre (cuInit != 0). Termina il pod e cambia host."; exit 2; }
echo "caps=$NVIDIA_DRIVER_CAPABILITIES"
echo "== codice"; git fetch -q origin 2>/dev/null; git pull -q --ff-only 2>&1 | tail -2
echo "VERSIONE: $(git log -1 --oneline) | branch $(git rev-parse --abbrev-ref HEAD) | schedule_nyc: $(python3 -c "import json;s=json.load(open('schedule_nyc.json'));print(round(s['duration']),'s totali, test: primi',$NF/24,'s')")"
git diff --quiet HEAD -- build_render.py run.sh schedule_nyc.json city_nyc.json kit || echo "ATTENZIONE: file di render modificati rispetto al commit"
rec "test" "-" "$(git log -1 --oneline) | GPU $GPUNAME | $(date -u +%FT%TZ)"
echo
echo "== AVANZAMENTO IN TEMPO REALE (apri un secondo terminale e incolla):"
echo "cd $REPO/test_raea/out; while :; do echo \"\$(date +%H:%M:%S) fase: \$(cat fase_corrente.txt) | A: \$(ls A_frames 2>/dev/null | grep -c jpg)/$NF | B: \$(tail -c 160 B_raea.log 2>/dev/null | tr '\\r\\n' '  ' | tail -c 70) \$(ls -l B_raea.mp4 2>/dev/null | awk '{print \$5/1e6\" MB\"}')\"; sleep 20; done"
echo

# ---------------------------------------------------------------- prerequisiti di sistema (comuni; ffmpeg, GPU) -------
sys_pkgs(){
  apt-get update -qq >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg jq curl ca-certificates git libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libxxf86vm1 libxfixes3 libxext6 >/dev/null
}
phase "0_pacchetti_sistema_ffmpeg" sys_pkgs

if [[ "$ONLY" == *A* ]]; then
# ====================================================== A) BLENDER ====================================================
inst_blender(){ pip install -q uv && { [ -x /workspace/bl/bin/python ] || uv venv -q -p 3.13 /workspace/bl; } && uv pip install -q -p /workspace/bl/bin/python bpy==5.2.2 shapely requests pyshp pyproj scipy; }
phase "A1_installazione_blender_bpy" inst_blender
gpu_test(){ DEV=$($PY gputest.py | tee /dev/stderr | grep DEVICE= | cut -d= -f2); echo "$DEV" > "$OUT/device.txt"; echo "uso: $DEV"; [ "$DEV" != "CPU" ] && [ -n "$DEV" ]; }
phase "A2_prova_gpu_gputest" gpu_test || { echo "NESSUNA GPU FUNZIONANTE per Blender: salto A."; ONLY=${ONLY/A/}; }
fi
if [[ "$ONLY" == *A* ]]; then
dati_nyc(){   # come run.sh, ramo kit di NYC (cities/nyc/story.json): data_nyc_src -> data_nyc, storia (hist_kit), moli e DEM (restore_after_build.sh)
  D=data_nyc; mkdir -p $D
  for g in data_nyc_src/*.gz; do b=$(basename "$g" .gz); [ -s $D/$b ] || gunzip -c "$g" > $D/$b; done; echo ok > $D/land_v3.ok
  [ -f hist_nyc.py ] || $PY -m kit.hist_kit make-stub nyc
  [ -f city_nyc.json ] || $PY -m kit.city_json nyc
  $PY -m kit.hist_kit build nyc $D && PY=$PY sh cities/nyc/qa/fix/restore_after_build.sh
}
phase "A3_dati_nyc_hist_e_moli" dati_nyc
DEV=$(cat "$OUT/device.txt" 2>/dev/null)
render_A(){
  rm -rf "$OUT/A_frames"; mon_start
  $PY build_render.py -- data_nyc "$OUT/A_frames" --frames 1 $NF --res 1920 1080 --samples 8 --device "$DEV" --schedule schedule_nyc.json --city city_nyc.json > "$OUT/A_blender.log" 2>&1
  local rc=$?; mon_stop "A"; return $rc
}
phase "A4_blender_scena+render_480_fotogrammi" render_A
# dal log: costruzione scena = tempo fino alla riga "render 1 -> 480"; s/fotogramma da FATTO e dalle righe per fotogramma (anno 2026 / riavvolgimento / 1609)
SC=$(grep -m1 "render 1 -> $NF" "$OUT/A_blender.log" | grep -o '([0-9]*s' | tr -d '(s')
rec "A_costruzione_scena (dentro A4)" "${SC:-?} s" "secondi da avvio build_render.py alla riga 'render 1 -> $NF'"
grep -E "FATTO|navi:|GPU|denoiser|rror" "$OUT/A_blender.log" | cut -c1-160 | tee -a "$OUT/A_resumo.txt"
awk '/\[build\] fotogramma/{f=$3; sub(":","",f); s=$4; sub("s","",s); n++; t+=s; if(f<=72){a+=s;na++} else if(f<=228){b+=s;nb++} else {c+=s;nc++}} END{if(n) printf "A secondi/fotogramma: tutti %.2f (n=%d) | anno 2026 f1-72 %.2f | riavvolgimento f73-228 %.2f | 1609 f229-480 %.2f\n", t/n,n,(na?a/na:0),(nb?b/nb:0),(nc?c/nc:0)}' "$OUT/A_blender.log" | tee -a "$TIMES"
encode_A(){ ffmpeg -loglevel error -y -framerate 24 -i "$OUT/A_frames/%04d.jpg" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p "$OUT/A_blender.mp4"; }
phase "A5_mp4_blender_ffmpeg" encode_A
fi

if [[ "$ONLY" == *B* ]]; then
# ====================================================== B) RAEA ====================================================
raea_deps(){ DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libasound2t64 libfontconfig1 libvulkan1 mesa-vulkan-drivers vulkan-tools >/dev/null 2>&1 || DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libasound2 libfontconfig1 libvulkan1 mesa-vulkan-drivers vulkan-tools >/dev/null; }
phase "B0_prerequisiti_raea_alsa_vulkan" raea_deps
echo "== Vulkan (raea disegna con Vulkan: deve vedere la NVIDIA, non llvmpipe)"; vulkaninfo --summary 2>/dev/null | grep -E "deviceName|driverName|deviceType" | head -8
VK=$(vulkaninfo --summary 2>/dev/null | grep -i deviceName | head -3); echo "$VK" > "$OUT/vulkan.txt"
if ! echo "$VK" | grep -qi nvidia && [ "${FORCE_B:-0}" != "1" ]; then
  echo "ATTENZIONE: Vulkan non vede la GPU NVIDIA (caps=$NVIDIA_DRIVER_CAPABILITIES). raea renderebbe su CPU (llvmpipe): il confronto non varrebbe. Salto B. Manda questa schermata in chat. (FORCE_B=1 per lanciare lo stesso)"; rec "B_vulkan" "-" "NVIDIA NON visibile: B saltato"; ONLY=${ONLY/B/}
fi
fi
if [[ "$ONLY" == *B* ]]; then
inst_raea_script(){ curl -fsSL https://raea.io/install | sh; }
inst_raea_tarball(){
  local u; u=$(curl -fsSL https://api.github.com/repos/shinyobjectz/raea/releases/latest | python3 -c "
import json,sys,re
r=json.load(sys.stdin)
for a in r.get('assets',[]):
    n=a['name'].lower()
    if 'linux' in n and re.search('x86_64|amd64|x64',n) and re.search(r'\.tar\.gz$|\.tgz$',n): print(a['browser_download_url']); break")
  [ -n "$u" ] || return 1; echo "tarball: $u"; mkdir -p /workspace/raea_dist && curl -fsSL "$u" | tar xz -C /workspace/raea_dist || return 1
  local b; b=$(find /workspace/raea_dist -type f -name raea | head -1); [ -n "$b" ] || return 1; install -m 755 "$b" /usr/local/bin/raea
}
inst_raea_cargo(){
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq build-essential pkg-config libasound2-dev libfontconfig1-dev libudev-dev libx11-dev libxkbcommon-dev libwayland-dev libssl-dev cmake >/dev/null
  command -v cargo >/dev/null || { curl -fsSL https://sh.rustup.rs | sh -s -- -y --profile minimal >/dev/null; }
  export PATH="/root/.cargo/bin:$PATH"
  [ -d /workspace/raea_src ] || git clone -q --depth 1 https://github.com/shinyobjectz/raea /workspace/raea_src
  ( cd /workspace/raea_src && cargo build --release -p raea-cli --no-default-features ) && install -m 755 /workspace/raea_src/target/release/raea /usr/local/bin/raea
}
if ! command -v raea >/dev/null; then
  phase "B1a_installazione_raea_script_ufficiale" inst_raea_script; export PATH="$HOME/.local/bin:$HOME/.raea/bin:$PATH"
  command -v raea >/dev/null || { phase "B1b_installazione_raea_tarball_releases" inst_raea_tarball; }
  command -v raea >/dev/null || { phase "B1c_installazione_raea_cargo_build" inst_raea_cargo; }
else rec "B1_installazione_raea" "0 s" "gia' presente"; fi
command -v raea >/dev/null || { echo "raea NON installabile: salto B."; rec "B_raea" "-" "NON installato: B saltato"; ONLY=${ONLY/B/}; }
fi
if [[ "$ONLY" == *B* ]]; then
echo "VERSIONE raea: $(raea --version 2>&1 | head -1)"; rec "raea_version" "-" "$(raea --version 2>&1 | head -1)"
gen_deps(){ pip install -q uv 2>/dev/null; [ -x "$PY" ] || { uv venv -q -p 3.13 /workspace/bl; }; uv pip install -q -p "$PY" numpy mapbox_earcut; }
phase "B2a_dipendenze_generatore_numpy_earcut" gen_deps
phase "B2b_costruzione_scena_generatore" $PY test_raea/gen_scene.py --stats "$OUT/scena_stats.json"
head -c 900 "$OUT/scena_stats.json" | tr '\n' ' ' | cut -c1-600; echo
export RAEA_SIGN=0 RAEA_MARK=0 RAEA_EXPORT_CACHE=0 RAEA_TIMES=1 RAEA_RENDER_STATS=1   # solo pixel e tempi: niente firma, niente filigrana, nessuna cache (un colpo di cache non misurerebbe nulla)
DESP=(); [ -n "${B_DESPITE:-}" ] && DESP=(--despite "$B_DESPITE" "test A/B")
frame0_B(){ raea render test_raea/raea/nyc20.tsx --composition nyc20 --frame 0 -o "$OUT/B_frame0.png" "${DESP[@]}" > "$OUT/B_frame0.log" 2>&1; }
phase "B3a_raea_avvio+1_fotogramma" frame0_B || { echo "raea ha rifiutato/fallito il fotogramma 0: ultime righe"; tail -15 "$OUT/B_frame0.log"; }
render_B(){
  rm -f "$OUT/B_raea.mp4"; mon_start
  RAEA_FRAME_LOG="$OUT/B_framelog.tsv" raea render test_raea/raea/nyc20.tsx --composition nyc20 -o "$OUT/B_raea.mp4" --quality "${B_QUALITY:-high}" "${DESP[@]}" > "$OUT/B_raea.log" 2>&1
  local rc=$?; mon_stop "B"; return $rc
}
phase "B3b_raea_render_480_fotogrammi" render_B || { echo "render raea fallito: ultime righe"; tail -20 "$OUT/B_raea.log"; }
BW=$(grep "B3b_raea_render" "$TIMES" | awk '{print $2" "$3}')
[ -n "$BW" ] && rec "B secondi/fotogramma (tempo totale B3b / $NF)" "$(awk -v w="${BW% s}" -v n=$NF 'BEGIN{printf "%.3f s", w/n}')" "comprende l'avvio e la costruzione scena di raea"
awk -F'\t' 'NR>2{n++; r+=$2; s+=$3; g+=$8} END{if(n) printf "B (RAEA_FRAME_LOG, senza il primo fotogramma, n=%d): React %.1f ms | sync %.1f ms | GPU %.1f ms a fotogramma\n", n, r/n, s/n, g/n}' "$OUT/B_framelog.tsv" 2>/dev/null | tee -a "$TIMES"
grep -E '"direct"|first frame|APPLIED|REFUSED|rror' "$OUT/B_raea.log" | head -6 | cut -c1-240
fi

# ====================================================== fotogrammi di confronto, foglio, consegna =====================
if [ -s "$OUT/A_blender.mp4" ] || [ -s "$OUT/B_raea.mp4" ]; then
FR="0 80 120 160 230 479"   # numeri di fotogramma (da 0): 2026, due tappe del riavvolgimento, 1609 in poi (quelli di Blender hanno nome n+1)
cmp_frames(){
  for v in A_blender B_raea; do [ -s "$OUT/$v.mp4" ] && for n in $FR; do ffmpeg -loglevel error -y -i "$OUT/$v.mp4" -vf "select=eq(n\,$n)" -frames:v 1 "$OUT/cmp_${v}_$(printf %03d $n).png"; done; done
  local ins=() fc="" k=0
  for n in $FR; do a="$OUT/cmp_A_blender_$(printf %03d $n).png"; b="$OUT/cmp_B_raea_$(printf %03d $n).png"
    if [ -s "$a" ] && [ -s "$b" ]; then ffmpeg -loglevel error -y -i "$a" -i "$b" -filter_complex "[0]scale=960:-2[a];[1]scale=960:-2[b];[a][b]hstack" "$OUT/riga_$(printf %03d $n).png"; ins+=(-i "$OUT/riga_$(printf %03d $n).png"); k=$((k+1)); fi; done
  [ "$k" -gt 0 ] && ffmpeg -loglevel error -y "${ins[@]}" -filter_complex "vstack=inputs=$k" "$OUT/confronto_A_sinistra_B_destra.png"
  for v in A_blender B_raea; do [ -s "$OUT/$v.mp4" ] && echo "$v: $(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames,width,height,duration -of csv=p=0 "$OUT/$v.mp4")"; done
}
phase "C_fotogrammi_di_confronto_e_foglio" cmp_frames
fi
TOT=$(( $(date +%s) - T0 )); rec "TOTALE_dall_inizio" "$TOT s" "~$(( TOT / 60 )) min"
( cd "$OUT" && tar czf risultati.tgz tempi.txt scena_stats.json A_blender.log B_raea.log B_frame0.log B_framelog.tsv vulkan.txt A_blender.mp4 B_raea.mp4 cmp_*.png confronto_A_sinistra_B_destra.png B_frame0.png 2>/dev/null; ls -lh risultati.tgz )
echo; echo "================ RIEPILOGO (test_raea/out/tempi.txt) ================"; cat "$TIMES"
echo
echo "FINITO. Si puo' SPEGNERE il pod (Terminate) SOLO quando hai scaricato dal browser (Jupyter, cartella city3d/test_raea/out):"
echo "  tempi.txt, confronto_A_sinistra_B_destra.png, A_blender.mp4, B_raea.mp4   (oppure tutto in risultati.tgz, senza i fotogrammi singoli)"
echo "e le dimensioni coincidono con 'ls -l'. Se una fase dice rc diverso da 0, manda in chat tempi.txt e le ultime righe del log di quella fase."
