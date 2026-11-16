# Marseille — SHORT (16/11/2026) — PROVVISORIO fino al render

Come Lione: il Short NON ha un render a parte; è il video lungo (secondi 10,5 → 649,1) accelerato a 28 s, con overlay verticale e audio dedicati. Non lanciare `run.sh shorts`.
File: `marseille_full.mp4` (quello del pod), `marseille_short_overlay.webm` (`bash montaggio/ov_kit.sh marseille short`), `marseille_short_audio.m4a` (`sfx_kit.py`).
Valori da `kit_city.py` (formule lette nel codice, non ancora generato `kit_marseille.json`): a = title_t + 1,0 = 10,5; b = durata − 6,0 = 649,1; n = 672 fotogrammi = 28 s; SP = (28 − 1,5) / (649,1 − 10,5) = 0,04150. **Da ricontrollare in `public/kit_marseille.json` (chiave `short`) dopo `kit_city.py` e dopo il render (se la durata cambia, cambiano b e SP).**

## Montaggio (cmd, una riga) → marseille_short_finale.mp4 (1080x1920, 28 s)
```
ffmpeg -y -ss 10.5 -t 638.6 -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_short_overlay.webm -i marseille_short_audio.m4a -filter_complex "[0:v]setpts=PTS*0.0415,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart marseille_short_finale.mp4
```
(forma identica a `cities/lyon/SHORT.md`; non verificata con un video di prova: non c'è ancora `marseille_full.mp4`.)
**Errore da evitare:** l'intestazione automatica del Short dice "2,626 YEARS IN 28 SECONDS" (`yrs_n` = 2026 − (−600)), mentre la end card della story dice 2,625. Mettere in `story.json` → `montaggio.short_tag: "2,625 YEARS IN 28 SECONDS"` prima di generare l'overlay.

## Titolo (EN, ≤ 100 caratteri)
2,600 YEARS OF MARSEILLE IN 28 SECONDS | 3D Timelapse | No AI #Shorts

## Descrizione (EN)
```
Marseille, from the Greek colony of Massalia around 600 BC to the CMA CGM tower and the MuCEM, in 28 seconds. Every building that stands today appears in the year recorded for its group of buildings in the French building database; the old city, and the Saint-Jean quarter before it was dynamited in 1943, are an approximate reconstruction.

NO AI imagery: every frame is rendered from open data.

Full 11-minute video, with the Saint-Jean quarter dynamited in 1943: {{URL_VIDEO_LONGO}}

Find your street: in what year does your building appear? Tell me in the comments.

Data: BDNB (CSTB), IGN BD TOPO, © OpenStreetMap contributors, Copernicus DEM GLO-30. Music: "Waking to Reality" by Unicorn Heads (YouTube Audio Library).

#Shorts #Marseille #3Dtimelapse #CityTimelapse #History
```

## Titoli e descrizioni nelle altre lingue (stessa struttura; link e hashtag uguali)
### fr
Titre : 2 600 ANS DE MARSEILLE EN 28 SECONDES | Timelapse 3D | Sans IA #Shorts
```
Marseille, de la colonie grecque de Massalia vers 600 av. J.-C. à la tour CMA CGM et au MuCEM, en 28 secondes. Chaque bâtiment actuel apparaît à l'année enregistrée pour son groupe de bâtiments dans la base nationale des bâtiments ; la vieille ville, et le quartier Saint-Jean avant son dynamitage en 1943, sont une reconstitution approximative.

SANS IA : chaque image est calculée à partir de données ouvertes.

La vidéo complète de 11 minutes, avec le quartier Saint-Jean dynamité en 1943 : {{URL_VIDEO_LONGO}}

Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire.

Données : BDNB (CSTB), IGN BD TOPO, © contributeurs OpenStreetMap, Copernicus DEM GLO-30. Musique : « Waking to Reality » de Unicorn Heads (YouTube Audio Library).

#Shorts #Marseille #3Dtimelapse #Histoire
```
### it
Titolo: 2.600 ANNI DI MARSIGLIA IN 28 SECONDI | Timelapse 3D | Senza IA #Shorts
```
Marsiglia, dalla colonia greca di Massalia intorno al 600 a.C. alla torre CMA CGM e al MuCEM, in 28 secondi. Ogni edificio di oggi compare nell'anno registrato per il suo gruppo di edifici nella banca dati nazionale francese; la città vecchia, e il quartiere Saint-Jean prima che venisse fatto saltare nel 1943, sono una ricostruzione approssimativa.

SENZA IA: ogni fotogramma è calcolato da dati aperti.

Il video completo di 11 minuti, con il quartiere Saint-Jean fatto saltare nel 1943: {{URL_VIDEO_LONGO}}

Cerca la tua strada: in che anno compare il tuo edificio? Dimmelo nei commenti.

Dati: BDNB (CSTB), IGN BD TOPO, © contributori di OpenStreetMap, Copernicus DEM GLO-30. Musica: "Waking to Reality" di Unicorn Heads (YouTube Audio Library).

#Shorts #Marsiglia #3Dtimelapse #Storia
```
### es
Título: 2.600 AÑOS DE MARSELLA EN 28 SEGUNDOS | Timelapse 3D | Sin IA #Shorts
```
Marsella, desde la colonia griega de Massalia hacia el 600 a. C. hasta la torre CMA CGM y el MuCEM, en 28 segundos. Cada edificio actual aparece en el año registrado para su grupo de edificios en la base de datos nacional francesa; la ciudad vieja, y el barrio de Saint-Jean antes de ser dinamitado en 1943, son una reconstrucción aproximada.

SIN IA: cada fotograma se genera con datos abiertos.

El vídeo completo de 11 minutos, con el barrio de Saint-Jean dinamitado en 1943: {{URL_VIDEO_LONGO}}

Busca tu calle: ¿en qué año aparece tu edificio? Cuéntamelo en los comentarios.

Datos: BDNB (CSTB), IGN BD TOPO, © colaboradores de OpenStreetMap, Copernicus DEM GLO-30. Música: "Waking to Reality" de Unicorn Heads (YouTube Audio Library).

#Shorts #Marsella #3Dtimelapse #Historia
```
### de
Titel: 2.600 JAHRE MARSEILLE IN 28 SEKUNDEN | 3D-Zeitraffer | Ohne KI #Shorts
```
Marseille, von der griechischen Kolonie Massalia um 600 v. Chr. bis zum CMA-CGM-Turm und zum MuCEM, in 28 Sekunden. Jedes heutige Gebäude erscheint in dem Jahr, das in der französischen Gebäudedatenbank für seine Gebäudegruppe eingetragen ist; die Altstadt und das Viertel Saint-Jean vor seiner Sprengung 1943 sind eine ungefähre Rekonstruktion.

OHNE KI: Jedes Bild wird aus offenen Daten berechnet.

Das ganze 11-Minuten-Video, mit dem 1943 gesprengten Viertel Saint-Jean: {{URL_VIDEO_LONGO}}

Finde deine Straße: In welchem Jahr erscheint dein Gebäude? Sag es mir in den Kommentaren.

Daten: BDNB (CSTB), IGN BD TOPO, © OpenStreetMap-Mitwirkende, Copernicus DEM GLO-30. Musik: „Waking to Reality“ von Unicorn Heads (YouTube Audio Library).

#Shorts #Marseille #3DTimelapse #Geschichte
```
### pt-BR
Título: 2.600 ANOS DE MARSELHA EM 28 SEGUNDOS | Timelapse 3D | Sem IA #Shorts
```
Marselha, da colônia grega de Massalia por volta de 600 a.C. à torre CMA CGM e ao MuCEM, em 28 segundos. Cada edifício de hoje aparece no ano registrado para o seu grupo de edifícios na base de dados nacional francesa; a cidade velha, e o bairro Saint-Jean antes de ser dinamitado em 1943, são uma reconstrução aproximada.

SEM IA: cada quadro é calculado a partir de dados abertos.

O vídeo completo de 11 minutos, com o bairro Saint-Jean dinamitado em 1943: {{URL_VIDEO_LONGO}}

Procure a sua rua: em que ano aparece o seu prédio? Conte nos comentários.

Dados: BDNB (CSTB), IGN BD TOPO, © colaboradores do OpenStreetMap, Copernicus DEM GLO-30. Música: "Waking to Reality" de Unicorn Heads (YouTube Audio Library).

#Shorts #Marselha #3Dtimelapse #História
```

## Tag (< 500 caratteri)
```
marseille, marseille 3d, marseille timelapse, 3d timelapse, city timelapse, evolution of marseille, history of marseille, massalia, how marseille grew, marseille in 28 seconds, shorts, no ai, histoire de marseille, marseille 3d timelapse, marsiglia, marsella, year built
```

## Commento fissato (EN + FR)
```
Full video (11 minutes, with the Saint-Jean quarter dynamited in 1943): {{URL_VIDEO_LONGO}}

Find your street: in what year does your building appear? Tell me in the comments.
```
```
La vidéo complète (11 minutes, avec le quartier Saint-Jean dynamité en 1943) : {{URL_VIDEO_LONGO}}

Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire.
```

## Quando pubblicarlo
Dopo il video lungo, con il suo link in {{URL_VIDEO_LONGO}}. Nessuna miniatura propria: YouTube prende un fotogramma; se la scelta è libera, uno dei primi secondi (la città di oggi). "11 minuti" = 10:55 senza cold open (11:04 con): se la durata finale cambia di più di ~30 s, correggere.
