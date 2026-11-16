# Lyon — SHORT (16/11/2026)

Il Short NON ha un render a parte: è il video lungo (secondi 10,5 → 559) accelerato a 28 s, con overlay verticale e audio dedicati. Non lanciare `run.sh shorts` per Lione (la sua configurazione calcola i fotogrammi su 300 s nominali, non sui 565 s veri).
File: `lyon_full.mp4` (quello del pod), `lyon_short_overlay.webm`, `lyon_short_audio.m4a`.

## Montaggio (cmd, una riga) → lyon_short_finale.mp4 (1080x1920, 28 s)
```
ffmpeg -y -ss 10.5 -t 548.5 -i lyon_full.mp4 -c:v libvpx-vp9 -i lyon_short_overlay.webm -i lyon_short_audio.m4a -filter_complex "[0:v]setpts=PTS*0.04831,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart lyon_short_finale.mp4
```
Verificato il 16/11 con un video di prova da 565 s al posto di `lyon_full.mp4`: esce `lyon_short_finale.mp4` h264 1080x1920 di 28,0 s con audio AAC; l'intestazione dice "2,069 YEARS IN 28 SECONDS" e la chiusura "FULL VIDEO ON THE CHANNEL".
(valori da `montaggio/public/kit_lyon.json`, chiave `short`: a = 10,5, b = 559, n = 672 fotogrammi = 28 s; SP = (28 - 1,5) / (559 - 10,5) = 0,04831.)

## Titolo (EN, <= 100 caratteri)
2,000 YEARS OF LYON IN 28 SECONDS | 3D Timelapse | No AI #Shorts

## Descrizione (EN)
```
Lyon, from the Roman colony of Lugdunum in 43 BC to the towers of Part-Dieu, in 28 seconds. Every building that stands today appears in the year recorded for its group of buildings in the French building registers; the old districts are an approximate reconstruction.

NO AI imagery: every frame is rendered from open data.

Full 9-minute video with the siege of 1793, the canuts, the 1856 flood and the bridges blown up in 1944: {{URL_VIDEO_LONGO}}

Find your street: in what year does your building appear? Tell me in the comments.

Data: BDNB (CSTB), IGN BD TOPO, © OpenStreetMap contributors. Music: "Waking to Reality" by Unicorn Heads (YouTube Audio Library).

#Shorts #Lyon #3Dtimelapse #CityTimelapse #History
```

## Titoli e descrizioni nelle altre lingue (stessa struttura; il link e gli hashtag restano uguali)
### fr
Titre : 2 000 ANS DE LYON EN 28 SECONDES | Timelapse 3D | Sans IA #Shorts
```
Lyon, de la colonie romaine de Lugdunum en 43 av. J.-C. aux tours de la Part-Dieu, en 28 secondes. Chaque bâtiment actuel apparaît à l'année enregistrée pour son groupe de bâtiments dans les registres français ; les quartiers anciens sont une reconstitution approximative.

SANS IA : chaque image est calculée à partir de données ouvertes.

La vidéo complète de 9 minutes, avec le siège de 1793, les canuts, la crue de 1856 et les ponts dynamités en 1944 : {{URL_VIDEO_LONGO}}

Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire.

Données : BDNB (CSTB), IGN BD TOPO, © contributeurs OpenStreetMap. Musique : « Waking to Reality » de Unicorn Heads (YouTube Audio Library).

#Shorts #Lyon #3Dtimelapse #Histoire
```
### it
Titolo: 2.000 ANNI DI LIONE IN 28 SECONDI | Timelapse 3D | Senza IA #Shorts
```
Lione, dalla colonia romana di Lugdunum nel 43 a.C. alle torri della Part-Dieu, in 28 secondi. Ogni edificio di oggi compare nell'anno registrato per il suo gruppo di edifici nei registri francesi; i quartieri antichi sono una ricostruzione approssimativa.

SENZA IA: ogni fotogramma è calcolato da dati aperti.

Il video completo di 9 minuti, con l'assedio del 1793, i canuts, la piena del 1856 e i ponti saltati in aria nel 1944: {{URL_VIDEO_LONGO}}

Cerca la tua strada: in che anno compare il tuo edificio? Dimmelo nei commenti.

Dati: BDNB (CSTB), IGN BD TOPO, © contributori di OpenStreetMap. Musica: "Waking to Reality" di Unicorn Heads (YouTube Audio Library).

#Shorts #Lyon #3Dtimelapse #Storia
```
### es
Título: 2.000 AÑOS DE LYON EN 28 SEGUNDOS | Timelapse 3D | Sin IA #Shorts
```
Lyon, desde la colonia romana de Lugdunum en el 43 a. C. hasta las torres de la Part-Dieu, en 28 segundos. Cada edificio actual aparece en el año registrado para su grupo de edificios en los registros franceses; los barrios antiguos son una reconstrucción aproximada.

SIN IA: cada fotograma se genera con datos abiertos.

El vídeo completo de 9 minutos, con el asedio de 1793, los canuts, la inundación de 1856 y los puentes volados en 1944: {{URL_VIDEO_LONGO}}

Busca tu calle: ¿en qué año aparece tu edificio? Cuéntamelo en los comentarios.

Datos: BDNB (CSTB), IGN BD TOPO, © colaboradores de OpenStreetMap. Música: "Waking to Reality" de Unicorn Heads (YouTube Audio Library).

#Shorts #Lyon #3Dtimelapse #Historia
```
### de
Titel: 2.000 JAHRE LYON IN 28 SEKUNDEN | 3D-Zeitraffer | Ohne KI #Shorts
```
Lyon, von der römischen Kolonie Lugdunum im Jahr 43 v. Chr. bis zu den Türmen der Part-Dieu, in 28 Sekunden. Jedes heutige Gebäude erscheint in dem Jahr, das in den französischen Registern für seine Gebäudegruppe eingetragen ist; die alten Viertel sind eine ungefähre Rekonstruktion.

OHNE KI: Jedes Bild wird aus offenen Daten berechnet.

Das ganze 9-Minuten-Video mit der Belagerung von 1793, den Canuts, dem Hochwasser von 1856 und den 1944 gesprengten Brücken: {{URL_VIDEO_LONGO}}

Finde deine Straße: In welchem Jahr erscheint dein Gebäude? Sag es mir in den Kommentaren.

Daten: BDNB (CSTB), IGN BD TOPO, © OpenStreetMap-Mitwirkende. Musik: „Waking to Reality“ von Unicorn Heads (YouTube Audio Library).

#Shorts #Lyon #3DTimelapse #Geschichte
```
### pt-BR
Título: 2.000 ANOS DE LYON EM 28 SEGUNDOS | Timelapse 3D | Sem IA #Shorts
```
Lyon, da colônia romana de Lugdunum em 43 a.C. às torres da Part-Dieu, em 28 segundos. Cada edifício de hoje aparece no ano registrado para o seu grupo de edifícios nos registros franceses; os bairros antigos são uma reconstrução aproximada.

SEM IA: cada quadro é calculado a partir de dados abertos.

O vídeo completo de 9 minutos, com o cerco de 1793, os canuts, a cheia de 1856 e as pontes explodidas em 1944: {{URL_VIDEO_LONGO}}

Procure a sua rua: em que ano aparece o seu prédio? Conte nos comentários.

Dados: BDNB (CSTB), IGN BD TOPO, © colaboradores do OpenStreetMap. Música: "Waking to Reality" de Unicorn Heads (YouTube Audio Library).

#Shorts #Lyon #3Dtimelapse #História
```

## Tag (< 500 caratteri)
```
lyon, lyon 3d, lyon timelapse, 3d timelapse, city timelapse, evolution of lyon, history of lyon, lugdunum, how lyon grew, lyon in 28 seconds, shorts, no ai, histoire de lyon, lyon 3d timelapse, year built
```

## Commento fissato (EN + FR)
```
Full video (9 minutes, with the siege of 1793, the canuts, the 1856 flood and the 1944 bridges): {{URL_VIDEO_LONGO}}

Find your street: in what year does your building appear? Tell me in the comments.
```
```
La vidéo complète (9 minutes, avec le siège de 1793, les canuts, la crue de 1856 et les ponts de 1944) : {{URL_VIDEO_LONGO}}

Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire.
```

## Quando pubblicarlo
Dopo il video lungo, con il suo link nel campo {{URL_VIDEO_LONGO}} (descrizione e commento fissato). Il Short non ha miniatura propria: YouTube prende un fotogramma; se la scelta è libera, scegli uno dei primi secondi (la città di oggi).
