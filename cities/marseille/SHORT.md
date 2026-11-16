# Marseille — SHORT (16/11/2026) — PROVVISORIO fino al render

Come Lione: il Short NON ha un render a parte; è il video lungo (secondi 10,5 → 649,3) accelerato a 28 s, con overlay verticale e audio dedicati. Non lanciare `run.sh shorts`.
File: `marseille_full.mp4` (quello del pod), `marseille_short_overlay.webm` (`bash montaggio/ov_kit.sh marseille short`), `marseille_short_audio.m4a` (`sfx_kit.py`).
Valori da `kit_city.py` (formule lette in `kit_city.py` sullo schedule round 4, 655,3 s; `kit_marseille.json` non ancora generato): a = title_t + 1,0 = 10,5; b = durata − 6,0 = 649,3; n = 672 fotogrammi = 28 s; SP = (28 − 1,5) / (649,3 − 10,5) = 0,04148. **Da ricontrollare in `public/kit_marseille.json` (chiave `short`) dopo `kit_city.py` e dopo il render (se la durata cambia, cambiano b e SP).**

## Montaggio (cmd, una riga) → marseille_short.mp4 (1080x1920, 28 s)
```
ffmpeg -y -ss 10.5 -t 638.8 -i marseille_full.mp4 -c:v libvpx-vp9 -i marseille_short_overlay.webm -i marseille_short_audio.m4a -filter_complex "[0:v]setpts=PTS*0.04148,fps=24,tpad=stop_mode=clone:stop_duration=1.5,eq=contrast=1.03:saturation=1.08,split[s1][s2];[s1]scale=-2:1920,crop=1080:1920,boxblur=40:5,eq=brightness=-0.12[bg];[s2]scale=1080:608[fg];[bg][fg]overlay=0:656[m];[m][1:v]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a -c:v libx264 -preset slow -crf 18 -c:a copy -t 28 -movflags +faststart marseille_short.mp4
```
(forma identica a `cities/lyon/SHORT.md`. Overlay e audio dello Short prodotti e controllati (vedi sotto); il comando completo non è stato provato perché `marseille_full.mp4` ce l'ha il proprietario.)
File da scaricare per lo Short: `out/marseille_short_overlay.webm` (1,9 MB, 28,03 s, rigenerato: CTA dopo la dissolvenza dell'anno) e `out/marseille_short_audio.m4a` (697.731 byte, 28,000 s, -13,9 LUFS, picco -0,5 dBFS, nessun silenzio, fade finale). Nella cartella del proprietario insieme a `marseille_full.mp4`.
Intestazione automatica del Short: la story round 3 ha `montaggio.short_tag` = "2,625 YEARS IN 28 SECONDS" (verificato nel file): l'overlay dirà 2,625, coerente con la end card.

## Titolo (EN, ≤ 100 caratteri)
2,600 YEARS OF MARSEILLE IN 28 SECONDS | 3D Timelapse | No AI #Shorts

## Descrizione (EN)
```
Marseille, from the Greek colony of Massalia around 600 BC to the CMA CGM tower and the MuCEM, in 28 seconds. Every building that stands today appears in the year recorded for its group of buildings in the French building database; the old city is a reconstruction, and so is the Saint-Jean quarter before its destruction in 1943 (about a third of its footprint follows the 1940 German plan; the rest, and all heights and dates, are estimated).

NO AI imagery: every frame is rendered from open data.

Full 11-minute video, with Caesar's siege, the plague of 1720, the Rue Impériale and the Old Port rebuilt after 1943: {{URL_VIDEO_LONGO}}

Find your street: in what year does your building appear? Tell me in the comments.

Data: BDNB (CSTB), IGN BD TOPO, © OpenStreetMap contributors, Copernicus DEM GLO-30. Music: "Waking to Reality" by Unicorn Heads (YouTube Audio Library).

#Shorts #Marseille #3Dtimelapse #CityTimelapse #History
```

## Titoli e descrizioni nelle altre lingue (stessa struttura; link e hashtag uguali)
### fr
Titre : 2 600 ANS DE MARSEILLE EN 28 SECONDES | Timelapse 3D | Sans IA #Shorts
```
Marseille, de la colonie grecque de Massalia vers 600 av. J.-C. à la tour CMA CGM et au MuCEM, en 28 secondes. Chaque bâtiment actuel apparaît à l'année enregistrée pour son groupe de bâtiments dans la base nationale des bâtiments ; la vieille ville est une reconstitution, de même que le quartier Saint-Jean avant sa destruction en 1943 (environ un tiers de son emprise suit le plan allemand de 1940 ; le reste, ainsi que hauteurs et dates, est estimé).

SANS IA : chaque image est calculée à partir de données ouvertes.

La vidéo complète de 11 minutes, avec le siège de César, la peste de 1720, la rue Impériale et le Vieux-Port reconstruit après 1943 : {{URL_VIDEO_LONGO}}

Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire.

Données : BDNB (CSTB), IGN BD TOPO, © contributeurs OpenStreetMap, Copernicus DEM GLO-30. Musique : « Waking to Reality » de Unicorn Heads (YouTube Audio Library).

#Shorts #Marseille #3Dtimelapse #Histoire
```
### it
Titolo: 2.600 ANNI DI MARSIGLIA IN 28 SECONDI | Timelapse 3D | Senza IA #Shorts
```
Marsiglia, dalla colonia greca di Massalia intorno al 600 a.C. alla torre CMA CGM e al MuCEM, in 28 secondi. Ogni edificio di oggi compare nell'anno registrato per il suo gruppo di edifici nella banca dati nazionale francese; la città vecchia è una ricostruzione, come il quartiere Saint-Jean prima della distruzione del 1943 (circa un terzo della sua impronta segue la pianta tedesca del 1940; il resto, e tutte le altezze e le date, è stimato).

SENZA IA: ogni fotogramma è calcolato da dati aperti.

Il video completo di 11 minuti, con l'assedio di Cesare, la peste del 1720, la rue Impériale e il Vecchio Porto ricostruito dopo il 1943: {{URL_VIDEO_LONGO}}

Cerca la tua strada: in che anno compare il tuo edificio? Dimmelo nei commenti.

Dati: BDNB (CSTB), IGN BD TOPO, © contributori di OpenStreetMap, Copernicus DEM GLO-30. Musica: "Waking to Reality" di Unicorn Heads (YouTube Audio Library).

#Shorts #Marsiglia #3Dtimelapse #Storia
```
### es
Título: 2.600 AÑOS DE MARSELLA EN 28 SEGUNDOS | Timelapse 3D | Sin IA #Shorts
```
Marsella, desde la colonia griega de Massalia hacia el 600 a. C. hasta la torre CMA CGM y el MuCEM, en 28 segundos. Cada edificio actual aparece en el año registrado para su grupo de edificios en la base de datos nacional francesa; la ciudad vieja es una reconstrucción, igual que el barrio de Saint-Jean antes de su destrucción en 1943 (cerca de un tercio de su huella sigue el plano alemán de 1940; el resto, y todas las alturas y fechas, es estimado).

SIN IA: cada fotograma se genera con datos abiertos.

El vídeo completo de 11 minutos, con el sitio de César, la peste de 1720, la rue Impériale y el Puerto Viejo reconstruido tras 1943: {{URL_VIDEO_LONGO}}

Busca tu calle: ¿en qué año aparece tu edificio? Cuéntamelo en los comentarios.

Datos: BDNB (CSTB), IGN BD TOPO, © colaboradores de OpenStreetMap, Copernicus DEM GLO-30. Música: "Waking to Reality" de Unicorn Heads (YouTube Audio Library).

#Shorts #Marsella #3Dtimelapse #Historia
```
### de
Titel: 2.600 JAHRE MARSEILLE IN 28 SEKUNDEN | 3D-Zeitraffer | Ohne KI #Shorts
```
Marseille, von der griechischen Kolonie Massalia um 600 v. Chr. bis zum CMA-CGM-Turm und zum MuCEM, in 28 Sekunden. Jedes heutige Gebäude erscheint in dem Jahr, das in der französischen Gebäudedatenbank für seine Gebäudegruppe eingetragen ist; die Altstadt ist eine Rekonstruktion, ebenso das Viertel Saint-Jean vor seiner Zerstörung 1943 (etwa ein Drittel seiner Grundfläche folgt dem deutschen Plan von 1940; der Rest und alle Höhen und Daten sind geschätzt).

OHNE KI: Jedes Bild wird aus offenen Daten berechnet.

Das ganze 11-Minuten-Video, mit Caesars Belagerung, der Pest von 1720, der Rue Impériale und dem nach 1943 wiederaufgebauten Alten Hafen: {{URL_VIDEO_LONGO}}

Finde deine Straße: In welchem Jahr erscheint dein Gebäude? Sag es mir in den Kommentaren.

Daten: BDNB (CSTB), IGN BD TOPO, © OpenStreetMap-Mitwirkende, Copernicus DEM GLO-30. Musik: „Waking to Reality“ von Unicorn Heads (YouTube Audio Library).

#Shorts #Marseille #3DTimelapse #Geschichte
```
### pt-BR
Título: 2.600 ANOS DE MARSELHA EM 28 SEGUNDOS | Timelapse 3D | Sem IA #Shorts
```
Marselha, da colônia grega de Massalia por volta de 600 a.C. à torre CMA CGM e ao MuCEM, em 28 segundos. Cada edifício de hoje aparece no ano registrado para o seu grupo de edifícios na base de dados nacional francesa; a cidade velha é uma reconstrução, assim como o bairro Saint-Jean antes de sua destruição em 1943 (cerca de um terço de sua área segue a planta alemã de 1940; o resto, e todas as alturas e datas, é estimado).

SEM IA: cada quadro é calculado a partir de dados abertos.

O vídeo completo de 11 minutos, com o cerco de César, a peste de 1720, a rue Impériale e o Porto Velho reconstruído após 1943: {{URL_VIDEO_LONGO}}

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
Full video (11 minutes, with Caesar's siege, the plague of 1720 and the Old Port rebuilt after 1943): {{URL_VIDEO_LONGO}}

Find your street: in what year does your building appear? Tell me in the comments.
```
```
La vidéo complète (11 minutes, avec le siège de César, la peste de 1720 et le Vieux-Port reconstruit après 1943) : {{URL_VIDEO_LONGO}}

Cherchez votre rue : en quelle année apparaît votre immeuble ? Dites-le en commentaire.
```

## Quando pubblicarlo
Dopo il video lungo, con il suo link in {{URL_VIDEO_LONGO}}. Nessuna miniatura propria: YouTube prende un fotogramma; se la scelta è libera, uno dei primi secondi (la città di oggi). "11 minuti" = 10:55: se la durata finale cambia di più di ~30 s, correggere.
