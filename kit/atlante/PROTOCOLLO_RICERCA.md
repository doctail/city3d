# Protocollo ricerca dati per citta' (Year Built) - 13/11/2026
Obiettivo: per ogni citta' sapere se esiste l'ANNO DI COSTRUZIONE PER EDIFICIO scaricabile, e quanto e' completo.
Per ogni citta' compila una riga con: fonte ufficiale (nome, URL, formato, licenza) | host raggiungibile dal proxy (curl -m 20, 200/403) | copertura anno misurata | voto A/B/C | evento spettacolare storico | note.
Voti: A = anno per edificio, copertura >=70% nel centro, scaricabile. B = anno per edificio ma 35-70%, o solo per parti, o licenza/host da sbloccare. C = solo classi di eta' / stime / nessun dato.
Metodo universale OSM (host consentiti: overpass-api.de, download.geofabrik.de): in una finestra di ~1 km^2 nel centro storico conta gli edifici e quelli con start_date:
  curl -s --data-urlencode 'data=[out:json][timeout:60];(way["building"](S,W,N,E););out count;' https://overpass-api.de/api/interpreter
  e lo stesso con way["building"]["start_date"](S,W,N,E) -> copertura = secondo/primo. Misura SEMPRE la copertura OSM, anche se esiste un registro ufficiale.
Etichette di confidenza: [Certain] misurato/letto, [Likely] inferenza forte, [Guessing].
Host bloccati: elencali a parte ("DA SBLOCCARE: host - perche'") cosi' li sblocchiamo in un colpo solo. Non inventare dati: se un host e' bloccato dillo.
Regole: non chiamare vidIQ, non chiamare altri agenti, non fare git. Scrivi il risultato nel file indicato (markdown, tabella + sezione DA SBLOCCARE) e rispondi con un riepilogo <=8 righe.
