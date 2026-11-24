#!/usr/bin/env bash
# Verifica locale (senza GPU e senza il binario raea): generatore sui dati veri, controllo dei tipi contro l'SDK del clone raea,
# valutazione della composizione per 8 fotogrammi (conteggio parti 3D). Serve il clone: git clone https://github.com/shinyobjectz/raea
#   RAEA_REPO=/home/user/shinyobjectz/raea bash test_raea/verifica_locale.sh
set -e
cd "$(dirname "$0")"; R=${RAEA_REPO:-/home/user/shinyobjectz/raea}; V=${VENV:-/tmp/raea_ab_venv}
[ -x $V/bin/python ] || { python3 -m venv $V; $V/bin/pip install -q numpy mapbox_earcut; }
$V/bin/python gen_scene.py
( cd $R/sdk/raea && bun install >/dev/null )                    # react e tipi per tsc/bun (nel clone, non in city3d)
sed "s#/home/user/shinyobjectz/raea#$R#" raea/tsconfig.json > raea/tsconfig.local.json
( cd raea && $R/sdk/raea/node_modules/.bin/tsc -p tsconfig.local.json | grep -v "prelude.ts(6,1)" || true ); rm -f raea/tsconfig.local.json   # prelude.ts: errore gia' presente nell'SDK, non nostro
( cd raea && RAEA_SDK=$R/sdk bun run check_frames.tsx )
