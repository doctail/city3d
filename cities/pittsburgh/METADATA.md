# Pittsburgh: METADATA (YouTube) — FINALE sul render del pod (19/11/2026, canale "Ledger of Cities")

Titolo, descrizione, capitoli e tag completi e incollabili in 6 lingue: `CONSEGNA_YOUTUBE.md` (orari reali dal render: 617,6 s = 10:17, nessun cold open, R14). Miniatura: `copertina/pittsburgh_thumb_1754_now_1280x720.jpg`. Montaggio: `MONTAGGIO.md`. Reddit, distribuzione, nota stampa: `REDDIT_DISTRIBUZIONE.md`. Struttura come `cities/marseille/METADATA.md`.

## Title (<= 100 characters)
EVOLUTION OF PITTSBURGH | 3D City Timelapse (1754–NOW) | No AI

## Titles (translations)
- fr: ÉVOLUTION DE PITTSBURGH | Timelapse 3D de la ville (1754–AUJOURD'HUI) | Sans IA
- it: EVOLUZIONE DI PITTSBURGH | Timelapse 3D della città (1754–OGGI) | Senza IA
- es: EVOLUCIÓN DE PITTSBURGH | Timelapse 3D de la ciudad (1754–HOY) | Sin IA
- de: ENTWICKLUNG VON PITTSBURGH | 3D-Zeitraffer der Stadt (1754–HEUTE) | Ohne KI
- pt: EVOLUÇÃO DE PITTSBURGH | Timelapse 3D da cidade (1754–HOJE) | Sem IA

## Regole del proprietario (applicate)
- Gancio di serie "find your building" come prima riga di descrizione, commento fissato e Reddit. Nessun evento-gancio: il 1936 e' un capitolo (5:31), mai titolo o miniatura. Nessun cold open.
- Miniatura: `1754 > NOW / PITTSBURGH`, due meta' piene di citta', nessuna bandiera (forti a sinistra, skyline a destra).
- Canale: **Ledger of Cities** (nome nuovo dal 19/11): su schermo (`montaggio.channel` in `story.json`), nei testi e su Reddit. Nei file delle citta' vecchie resta "Year Built" (non rinominato).
- Testi e titoli in inglese americano. Lingua locale di Pittsburgh = inglese: commento fissato in un solo blocco.

## Dichiarazioni obbligatorie (nel testo di `CONSEGNA_YOUTUBE.md`)
- Impronte: Allegheny County Building Footprint Locations (fotogrammetria da fotografie aeree 1992-93, aggiornata 2004 e 2015) via WPRDC; anni dalle valutazioni della contea (particella, non edificio): 89% delle impronte con anno vero (60% dell'area), 11% stimato dai vicini (misura locale, `data_pittsburgh/misure_pgh.json`).
- La contea non ha l'anno per la maggior parte degli edifici commerciali: grattacieli del centro con anni e altezze da Wikipedia/Wikidata, controllati con LiDAR USGS 3DEP.
- Prima del 1880 ricostruzione (pillola a schermo, `data_reliable_from` 1880); Lower Hill prima del 1956 e magazzini del Point prima degli anni Cinquanta: ricostruzione. **Attenzione**: la brief del proprietario diceva "prima del 1836"; la story e il video dicono 1880 e il testo segue il video.
- Acciaierie assenti dal dato. Alluvione 1936 = cartello, livello d'acqua approssimativo [da controllare nel video finale].
- Colori: Sentinel-2 L2A (2024-2025, ESA) e ESA WorldCover 2021 (CC BY 4.0). Musica: Unicorn Heads, TrackTribe (YouTube Audio Library, nessuna attribuzione richiesta).
- Numeri nei testi: 272 anni; 89%/60%/11% (misura); nessun numero di vittime.

## Tag (428 caratteri su 500)
```
pittsburgh, evolution of pittsburgh, pittsburgh history, history of pittsburgh, pittsburgh 3d, 3d timelapse, city timelapse, city evolution, how pittsburgh grew, fort pitt, fort duquesne, steel city, point state park, pittsburgh bridges, pittsburgh skyline, civic arena, three rivers stadium, lower hill district, pittsburgh timelapse, no ai, histoire de pittsburgh, storia di pittsburgh, 3d map, urban history, ledger of cities
```

## Commento fissato
Blocco EN in `CONSEGNA_YOUTUBE.md` (apre con "Find your building").

## Costo
Non misurato in questa consegna. (Base misurata solo per Lione: ~29 s di pod per secondo di video + 30 min di scena per processo; Pittsburgh ha ~180K edifici.)

## Cosa manca / dipende
- Licenza dei dati della contea: la pagina del dataset WPRDC dice "License not specified": verificare i termini prima di pubblicare.
- Regole dei subreddit e dei gruppi: non verificate (reddit.com bloccato dal proxy, CONNECT 403).
- Link del video (`{{URL_VIDEO}}`) nei testi Reddit/stampa: dopo la pubblicazione.
