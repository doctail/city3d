#!/usr/bin/env bash
# Parigi, SECONDO GIRO (pod CPU, ~20-40 min, niente GPU). Uscita: /workspace/dati2_parigi.tgz da scaricare e caricare in chat.
#  - BDNB 2026-02-b dip. 75/92/93/94 ri-estratta con colonne in piu' (altezza massima, Merimee, materiali tetto/muri, usi)
#  - fonti storiche (fetch_fr_hist.py): Vasserot 1810-1836, alberi, arrondissement, vie con storico, Merimee, Wikidata, mappe storiche
# Una fonte che fallisce NON ferma le altre: il riepilogo finale (fonti.log) dice cosa e' arrivato.
# Uso:  cd /workspace && (git -C city3d pull || git clone https://github.com/doctail/city3d) && cd city3d && CITY=parigi bash data_fr2.sh
CITY=${CITY:-parigi}
cd /workspace/city3d || exit 1
PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v $c >/dev/null 2>&1 && $c -m pip --version >/dev/null 2>&1; then PY=$c; break; fi
done
[ -z "$PY" ] && { echo "Nessun Python con pip trovato"; exit 1; }
echo "uso $PY"
PKG="requests shapely pyproj numpy pandas geopandas pyogrio"
$PY -m pip install -q $PKG 2>/dev/null || $PY -m pip install -q --break-system-packages $PKG
OUT=/workspace/raw2_$CITY; mkdir -p $OUT /workspace/bdnb

M=2026-02-b; B=https://open-data.s3.fr-par.scw.cloud
for d in 75 92 93 94; do
  z=/workspace/bdnb/open_data_millesime_${M}_dep${d}_gpkg.zip
  [ -s $z ] || curl -fsSL --retry 3 -o $z.part "$B/bdnb_millesime_$M/millesime_${M}_dep$d/open_data_millesime_${M}_dep${d}_gpkg.zip" && mv -f $z.part $z 2>/dev/null &
done
$PY fetch_fr_hist.py city_$CITY.json $OUT &      # le fonti storiche in parallelo ai download BDNB
wait
for z in /workspace/bdnb/*.zip; do d=${z%.zip}; [ -d $d ] || unzip -q $z -d $d; done
G=$(find /workspace/bdnb -name bdnb.gpkg | tr '\n' ' ')
echo "GeoPackage BDNB: $G"
$PY fetch_fr_raw.py clip city_$CITY.json $OUT $G 2>&1 | tee $OUT/fetch_fr.log | grep -v "strato rel_\|strato metad"
cp city_$CITY.json $OUT/
tar czf /workspace/dati2_$CITY.tgz -C /workspace raw2_$CITY
echo; echo "=== RIEPILOGO FONTI ==="; grep -E "^(OK|FAIL)" $OUT/fonti.log
du -sh $OUT/* | sort -h | tail -15
ls -lh /workspace/dati2_$CITY.tgz
echo "FATTO: scarica dati2_$CITY.tgz da Jupyter, caricalo in chat (se supera il limite di upload dimmelo), poi TERMINA il Pod."
