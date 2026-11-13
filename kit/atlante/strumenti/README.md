# Strumenti usati nella ricerca del 13/11/2026

Script scritti in sessione cloud, salvati qui cosi' non vanno persi. Percorsi `/tmp/claude-0/...` dentro gli script sono della sessione: adattarli.

## BDNB (Francia) - per Lione e le altre citta'
- File dati: `https://open-data.s3.fr-par.scw.cloud/bdnb_millesime_2026-02-b/millesime_2026-02-b_dep<DD>/open_data_millesime_2026-02-b_dep<DD>_csv.zip` (un zip per dipartimento, DD = 69 Lione, 13 Marsiglia, 33 Bordeaux, 31 Tolosa, ...).
- Host da avere nell'allowlist: `open-data.s3.fr-par.scw.cloud` (la radice da' 403, un file vero funziona).
- Anno di costruzione: tabella `batiment_groupe_ffo_bat`, colonna `annee_construction` (NON in `batiment_groupe`). Geometria in `batiment_groupe` (WKT). Unita' = gruppo di edifici, non edificio singolo.
- Lione e Marsiglia in BDNB usano gli arrondissement: 69381-69389 e 13201-13216 (non 69123 / 13055).
- `rangeio.py`: apre lo zip via HTTP Range senza scaricarlo tutto (i CSV sono centinaia di MB). `measure_fr.py` e `analyze_fr.py`: misura % con anno per comune e entro 1 km dal centro (proiezione Lambert-93 a mano, senza pyproj).
- Risultati misurati (13/11): vedi `../TABELLA_CITTA.md` e `../italia_francia.md` (sezione MISURE sera).

## Amburgo
- `harvest_hamburg.py`: scarica tutti i 406.415 edifici del WFS `https://geodienste.hamburg.de/HH_WFS_INSPIRE_Gebaeude_2D_ALKIS` (tipo `bu-core2d:Building`, 3000 per pagina, STARTINDEX). Il filtro BBOX del server e' rotto (errore SRID): si filtra in locale. Anno in `dateOfConstruction/DateOfEvent/end` (fine anno UTC). `1500-01-09` = segnaposto da scartare. Risultato: 37% con anno.
- Il grezzo scaricato (182 MB, `/home/user/hh_raw`) NON e' nel repo: va riscaricato (circa 35 minuti in 3 flussi).

## Nodum via curl (quando i tool MCP non sono collegati)
- `nodum_mcp_curl.py`: client minimo verso `https://nodum.md/api/v1/mcp` (initialize + tools/call). Il token e' iniettato dal proxy, non va scritto nello script.
- Il token `nodum_mcp_...` funziona SOLO su `/api/v1/mcp`. L'endpoint REST `/api/v1/vaults` risponde 401 anche con token valido: non usarlo per verificare.
- Mai incollare token in chat.
