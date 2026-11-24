# Risultati test A/B NYC 20 s (24/11/2026, pod A40, commit 2d510fd)
- Blender: scena 221 s + render 480 fot. ~917 s (1,90 s/fot.); totale fasi A ~1480 s incl. dati 301 s (dati comuni).
- raea 0.1.9: installazione 15 s, scena 14 s, avvio+1 fot. 35 s, render 480 fot. 103 s (0,215 s/fot. incl. avvio); totale B ~170 s.
- Velocità: ~7-9x su una scena MOLTO piu' vuota (solo edifici, terra, acqua: niente alberi, strade, ponti, navi, rilievo).
- Qualità: geometria e camera corrispondono; look molto piu' povero, riflesso solare bianco enorme sull'acqua (difetto di luce, da correggere).
- Non misurati: token di raea a regime, costo del pareggio di funzioni, GPU 0.0 ms nel log raea (da capire).
