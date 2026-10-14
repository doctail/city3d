# Year Built — cosa cambia dal prossimo video

## Già fatto nel codice (dopo il render di New York)
- Fotogrammi in **JPG 95** (~0,7 MB a 1080p). I PNG pesavano 8 MB l'uno: 7839 fotogrammi = 63 GB, più del disco del pod.
- `pack.sh`: converte eventuali PNG in JPG e libera spazio.
- Strade disegnate a mano **spente** (`--roads` per riaccenderle): erano le righe chiare dritte nel New Jersey e nel Queens.
- New Jersey: tessuto urbano a tetti piccoli e strade dritte invece dei "mattoni".
- Denoiser **OptiX** sulle GPU OptiX (`--denoiser optix|oidn|none`).
- `bash run.sh profile`: 5 varianti × 12 fotogrammi, stampa i secondi per fotogramma di ognuna. Da lanciare **all'inizio** del prossimo pod (circa 6 minuti, pochi centesimi) prima del render completo.
- Cielo sfumato con alone del sole e nuvole; camera bassa e obiettivo per chiave (`[t, pos, target, mm]`).
- Foschia esclusa dal campionamento luci: niente picchi da 12 s quando compaiono oggetti.

## Numeri reali di New York (RTX 5080, 0,39 $/h)
- Costruzione scena: 60 s. Memoria GPU: 3,3 GB su 16.
- 3,8 s/fotogramma costanti anche con la scena quasi vuota (1610): il tempo è quasi tutto **costo fisso**, non dipende da quanta città c'è.
- 16 → 8 campioni ha tolto solo 0,8 s. Il resto (≈3 s) va scoperto con `run.sh profile`. Sospetti: avvio del denoiser a ogni fotogramma, sincronizzazione dei 2.465 oggetti.
- Riavvolgimento 2026→1609: ~7 s/fotogramma per circa 90 fotogrammi (migliaia di oggetti che cambiano).
- Totale stimato: ~8,3 ore, ~3,3 $.

## Obiettivo per il prossimo
- ≤ 2 s/fotogramma → ~4,5 ore → < 2 € su 5080.
- Ordine al pod: `run.sh profile` → scelgo la variante → `run.sh full`.

## Cosa è ancora specifico di New York (da staccare in un file città)
- `fetch_nyc.py`: NYC Open Data (Socrata), confini dei distretti, contee NJ/NY del Census.
- `hist_nyc.py`: fronte di urbanizzazione per latitudine (Manhattan) e distanza dal traghetto (Brooklyn).
- `build_render.py`: `nj_year` (distanza da Hoboken), griglia a 29°, Central Park 1858, box città e foresta, origine Midtown.
- `schedule_nyc.json`: anni e camera.
Da fare quando scegliamo la città: un `city_<nome>.json` con centro, area, fronti di urbanizzazione, angolo della griglia, parchi storici, e la regia; uno script di download per la fonte dati di quella città.

## Città candidate (serve l'anno di costruzione di ogni edificio, dati aperti)
- **Amsterdam / Olanda** — [Likely] il registro BAG ha l'anno di costruzione di ogni edificio e 3DBAG ha le altezze: dati migliori di New York, storia 1300→oggi perfetta per il formato.
- **Chicago** — [Likely] footprints comunali con anno di costruzione; storia forte (incendio 1871, primi grattacieli).
- **Vienna, Helsinki, Copenaghen** — [Guessing] dati aperti con anno di costruzione, da verificare.
- **Parigi** — [Guessing] dati più frammentati; più lavoro.
