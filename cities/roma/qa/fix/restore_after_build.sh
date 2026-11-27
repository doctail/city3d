#!/bin/sh
# Roma: i dati locali vengono da `kit build` (hist_kit); hist_roma.py e' il modulo vecchio. run.sh lancia gia' hist_kit build quando questo file esiste;
# qui lo si ripete (idempotente) cosi' il controllo POD PARITY del gate simula lo stesso passo. YB_DATA = cartella dati.
${PY:-python} -m kit.hist_kit build roma "${YB_DATA:-data_roma}"
