# Immagini d'archivio per il montaggio (Parigi, 29 ott 2026). Scarica da Wikimedia Commons SOLO i file la cui licenza, letta
# dall'API di Commons (extmetadata), e' pubblico dominio o CC0; gli altri li salta e li elenca. Scrive licenze.json con
# titolo, autore, data, licenza, URL della pagina: e' il credito per la descrizione.
# La sandbox della chat non raggiunge Commons: si lancia sul pod (CPU, 1-2 minuti).
# Uso: python3 tools/fetch_archivio.py parigi /workspace/archivio_parigi
import json, os, sys, re, time, urllib.parse, requests
CITY, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
LISTE = {
    'parigi': [
        ('01_1248_palais_cite', 'File:Les Très Riches Heures du duc de Berry juin.jpg'),
        ('02_1739_turgot_louvre', 'File:Louvre and Tuileries palaces on the map of Turgot 1739 - Kyoto U.jpg'),
        ('03_1739_turgot_place_dauphine', 'File:Place Dauphine on 1739 Turgot map of Paris - KyotoU.jpg'),
        ('04_1789_bastille', 'File:Prise de la Bastille.jpg'),
        ('05_1865_rue_glatigny', 'File:Rue de Glatigny, Paris, 1865.jpg'),
        ('06_1865_rue_marmousets', 'File:Charles Marville, Rue des Marmousets, ca. 1853–70.jpg'),
        ('07_1870_place_chatelet', 'File:Charles Marville, Place du Châtelet, ca. 1853–70.jpg'),
        ('08_1877_opera_demolition', "File:Between Rue de l'Échelle and Rue Saint Augustin - demolition.jpg"),
        ('09_1871_hotel_de_ville_rijks', 'File:Gezicht op het stadhuis in Parijs na de brand door de Commune van Parijs, RP-F-F19686.jpg'),
        ('10_1871_hotel_de_ville_liebert', 'File:Alphonse Liébert, Hôtel de Ville incendié Grande façade - Library of Congress.jpg'),
        ('11_1888_eiffel_durandelle', 'File:Louis-Emile Durandelle, The Eiffel Tower - State of the Construction, 1888.jpg'),
        ('12_1888_eiffel_juillet', 'File:Tour Eiffel, Juillet 1888.jpg'),
    ],
}
API = 'https://commons.wikimedia.org/w/api.php'
H = {'User-Agent': 'city3d-archivio/1.0 (YouTube Year Built; contatto via GitHub doctail/city3d)'}
OK = re.compile(r'^(public domain|pd|cc0)', re.I)
def clean(s): return re.sub(r'<[^>]+>', '', s or '').strip()
res = []
for key, title in LISTE[CITY]:
    r = requests.get(API, params={'action': 'query', 'titles': title, 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'format': 'json'}, headers=H, timeout=60).json()
    pg = next(iter(r['query']['pages'].values()))
    if 'imageinfo' not in pg: print('MANCA', title); res.append({'key': key, 'title': title, 'stato': 'non trovato'}); continue
    ii = pg['imageinfo'][0]; md = ii.get('extmetadata', {})
    lic = clean(md.get('LicenseShortName', {}).get('value')); pd = OK.match(lic) is not None
    row = {'key': key, 'title': title, 'licenza': lic, 'autore': clean(md.get('Artist', {}).get('value'))[:200],
           'data': clean(md.get('DateTimeOriginal', {}).get('value'))[:80], 'pagina': ii.get('descriptionurl'), 'px': [ii.get('width'), ii.get('height')],
           'stato': 'scaricato' if pd else 'SALTATO (licenza non PD/CC0)'}
    if pd:
        # 29 ott: Wikimedia rispondeva con una pagina d'errore (troppe richieste) salvata come immagine. Ora: estensione
        # senza parametri, pausa tra i file, controllo che sia davvero un'immagine, 5 tentativi con attesa crescente
        ext = os.path.splitext(urllib.parse.urlparse(ii['url']).path)[1].lower() or '.jpg'
        for k_ in range(5):
            time.sleep(4 + 10 * k_)
            d = requests.get(ii['url'], headers=H, timeout=180)
            if d.status_code == 200 and d.headers.get('content-type', '').startswith('image/'):
                open(os.path.join(OUT, key + ext), 'wb').write(d.content); break
            print('  riprovo', key, d.status_code, d.headers.get('content-type'))
        else: row['stato'] = 'ERRORE download (Wikimedia ha rifiutato 5 volte)'
    print(f"{row['stato']:32s} {lic:22s} {key}")
    res.append(row); json.dump(res, open(os.path.join(OUT, 'licenze.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(res, open(os.path.join(OUT, 'licenze.json'), 'w'), ensure_ascii=False, indent=1)
print('FATTO:', sum(r_['stato'] == 'scaricato' for r_ in res), 'immagini in', OUT)
