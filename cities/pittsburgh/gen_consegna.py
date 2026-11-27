#!/usr/bin/env python3
"""Genera cities/pittsburgh/CONSEGNA_YOUTUBE.md (6 lingue) con gli orari dei capitoli presi da montaggio/eventi_pittsburgh.json
(render finale, years.json del pod). Regola: capitolo = t_in della carta - 2,8 s (gia' in eventi); carta/sosta = t_in; orario arrotondato
per difetto; voci a distanza >= 10 s (verificato qui). Nessun cold open (R14). Uso: python3 cities/pittsburgh/gen_consegna.py"""
import json, os, math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E = json.load(open(os.path.join(ROOT, 'montaggio/eventi_pittsburgh.json')))
L = ['en', 'fr', 'it', 'es', 'de', 'pt']
# (tipo, chiave di ricerca, anno, {lingua: etichetta}); tipo: today | ch (numero romano) | card (titolo) | sosta (titolo) | src
T = [
 ('today', None, '', dict(en='Pittsburgh today', fr="Pittsburgh aujourd'hui", it='Pittsburgh oggi', es='Pittsburgh hoy', de='Pittsburgh heute', pt='Pittsburgh hoje')),
 ('ch', 'I', '1754', dict(en='I · Forts on the Forks', fr="I · Les forts de la fourche de l'Ohio", it="I · I forti alla biforcazione dell'Ohio", es='I · Los fuertes de la bifurcación del Ohio', de='I · Die Forts an der Gabelung des Ohio', pt='I · Os fortes na bifurcação do Ohio')),
 ('card', 'Pittsburgh gets its name', '1758', dict(en='Pittsburgh gets its name', fr='Pittsburgh reçoit son nom', it='Pittsburgh prende il suo nome', es='Pittsburgh recibe su nombre', de='Pittsburgh bekommt seinen Namen', pt='Pittsburgh recebe o seu nome')),
 ('ch', 'II', '1777', dict(en='II · A Town on the Frontier', fr='II · Une ville de la frontière', it='II · Una cittadina di frontiera', es='II · Un pueblo de la frontera', de='II · Eine Stadt an der Grenze', pt='II · Uma vila de fronteira')),
 ('card', 'Fort Pitt is torn down', '1797', dict(en='Fort Pitt is torn down', fr='Le fort Pitt est démoli', it='Fort Pitt viene demolito', es='Se derriba Fort Pitt', de='Fort Pitt wird abgerissen', pt='O Fort Pitt é demolido')),
 ('ch', 'III', '1816', dict(en='III · The Iron City', fr='III · La ville du fer', it='III · La città del ferro', es='III · La ciudad del hierro', de='III · Die Eisenstadt', pt='III · A cidade do ferro')),
 ('sosta', 'The Great Fire', '1845', dict(en='The Great Fire', fr='Le grand incendie', it='Il grande incendio', es='El gran incendio', de='Der Große Brand', pt='O grande incêndio')),
 ('card', 'The railroads arrive', '1854', dict(en='The railroads arrive', fr='Le chemin de fer arrive', it='Arriva la ferrovia', es='Llega el ferrocarril', de='Die Eisenbahn kommt', pt='A ferrovia chega')),
 ('ch', 'IV', '1859', dict(en='IV · Steel City', fr="IV · La ville de l'acier", it="IV · La città dell'acciaio", es='IV · La ciudad del acero', de='IV · Die Stahlstadt', pt='IV · A cidade do aço')),
 ('card', 'The city swallows its neighbors', '1868', dict(en='The city swallows its neighbors', fr='La ville absorbe ses voisines', it='La città assorbe i vicini', es='La ciudad absorbe a sus vecinos', de='Die Stadt schluckt ihre Nachbarn', pt='A cidade engole os vizinhos')),
 ('card', 'Bessemer steel at Braddock', '1875', dict(en='Bessemer steel at Braddock', fr="L'acier Bessemer à Braddock", it="L'acciaio Bessemer a Braddock", es='El acero Bessemer en Braddock', de='Bessemer-Stahl in Braddock', pt='O aço Bessemer em Braddock')),
 ('card', 'The railroad strike', '1877', dict(en='The railroad strike', fr='La grève des chemins de fer', it='Lo sciopero ferroviario', es='La huelga ferroviaria', de='Der Eisenbahnerstreik', pt='A greve ferroviária')),
 ('sosta', 'The Smithfield Street Bridge', '1883', dict(en='The Smithfield Street Bridge', fr='Le pont de Smithfield Street', it='Il ponte di Smithfield Street', es='El puente de Smithfield Street', de='Die Smithfield Street Bridge', pt='A ponte da Smithfield Street')),
 ('card', 'Homestead', '1892', dict(en='Homestead', fr='Homestead', it='Homestead', es='Homestead', de='Homestead', pt='Homestead')),
 ('card', 'U.S. Steel', '1901', dict(en='U.S. Steel', fr='U.S. Steel', it='U.S. Steel', es='U.S. Steel', de='U.S. Steel', pt='U.S. Steel')),
 ('card', 'Allegheny City joins Pittsburgh', '1907', dict(en='Allegheny City joins Pittsburgh', fr='Allegheny City rejoint Pittsburgh', it='Allegheny City entra a far parte di Pittsburgh', es='Allegheny City se une a Pittsburgh', de='Allegheny City wird eingemeindet', pt='Allegheny City une-se a Pittsburgh')),
 ('card', "Half of America's steel", '1911', dict(en="Half of America's steel", fr="La moitié de l'acier américain", it="Metà dell'acciaio americano", es='La mitad del acero de EE. UU.', de='Die Hälfte des US-Stahls', pt='Metade do aço dos EUA')),
 ('sosta', 'The Hill District, a center of Black life and jazz', '1920', dict(en='The Hill District, a center of Black life and jazz', fr='Le Hill District, centre de la vie noire et du jazz', it="L'Hill District, centro della vita nera e del jazz", es='El Hill District, centro de la vida negra y del jazz', de='Der Hill District, Zentrum des schwarzen Lebens und des Jazz', pt='O Hill District, centro da vida negra e do jazz')),
 ('ch', 'V', '1927', dict(en='V · Between the Wars', fr='V · Entre les deux guerres', it='V · Tra le due guerre', es='V · Entre guerras', de='V · Zwischen den Kriegen', pt='V · Entre as guerras')),
 ('card', "The St. Patrick's Day flood", '1936', dict(en="The St. Patrick's Day flood", fr='La crue de la Saint-Patrick', it="L'alluvione del giorno di San Patrizio", es='La inundación del día de San Patricio', de="Das St.-Patrick's-Day-Hochwasser", pt='A enchente do Dia de São Patrício')),
 ('ch', 'VI', '1946', dict(en='VI · Renaissance', fr='VI · Renaissance', it='VI · Rinascita (Renaissance)', es='VI · Renacimiento (Renaissance)', de='VI · Renaissance', pt='VI · Renascimento (Renaissance)')),
 ('card', 'The Lower Hill is cleared', '1956', dict(en='The Lower Hill is cleared', fr='Le Lower Hill est rasé', it='Il Lower Hill viene raso al suolo', es='Se arrasa el Lower Hill', de='Das Lower Hill wird abgeräumt', pt='O Lower Hill é demolido')),
 ('sosta', 'The Civic Arena opens on the cleared Lower Hill', '1961', dict(en='The Civic Arena opens', fr='Ouverture du Civic Arena', it='Apre il Civic Arena', es='Abre el Civic Arena', de='Das Civic Arena öffnet', pt='O Civic Arena abre')),
 ('ch', 'VII', '1970', dict(en='VII · Collapse and Reinvention', fr='VII · Effondrement et réinvention', it='VII · Crollo e reinvenzione', es='VII · Colapso y reinvención', de='VII · Zusammenbruch und Neuerfindung', pt='VII · Colapso e reinvenção')),
 ('card', 'The mills close', '1982', dict(en='The mills close', fr='Les aciéries ferment', it='Chiudono le acciaierie', es='Cierran las acerías', de='Die Stahlwerke schließen', pt='As siderúrgicas fecham')),
 ('card', 'The mills come down', '1991', dict(en='The mills come down', fr='Les aciéries sont démolies', it='Le acciaierie vengono demolite', es='Se demuelen las acerías', de='Die Stahlwerke werden abgerissen', pt='As siderúrgicas são demolidas')),
 ('ch', 'VIII', '2004', dict(en='VIII · Eds, Meds and Robots', fr='VIII · Universités, hôpitaux et robots', it='VIII · Università, ospedali e robot', es='VIII · Universidades, hospitales y robots', de='VIII · Hochschulen, Kliniken und Roboter', pt='VIII · Universidades, hospitais e robôs')),
 ('card', 'The Igloo comes down', '2011', dict(en='The Igloo comes down', fr="L'Igloo est démoli", it="L'Igloo viene demolito", es='Se demuele el Igloo', de='Das Igloo wird abgerissen', pt='O Igloo é demolido')),
 ('card', 'The newest tower', '2024', dict(en='The newest tower', fr='La tour la plus récente', it='La torre più recente', es='La torre más reciente', de='Der neueste Turm', pt='A torre mais recente')),
 ('src', None, '', dict(en='Sources', fr='Sources', it='Fonti', es='Fuentes', de='Quellen', pt='Fontes')),
]


def t_of(kind, key):
    if kind == 'today': return 0.0
    if kind == 'ch': return next(c['t_in'] for c in E['chapters'] if c['num'] == key)
    if kind == 'card': return next(c['t_in'] for c in E['cards'] if c['title'] == key)
    if kind == 'sosta': return next(c['t_in'] for c in E['soste'] if c['title'] == key)
    return E['sources_card']['t_in']


_all = [(int(math.floor(t_of(k, key))), y, lab, k) for k, key, y, lab in T]
rows_k = []
for r in _all:   # YouTube: voci a distanza >= 10 s; se due sono piu' vicine si toglie la carta (capitoli e soste restano)
    if rows_k and r[0] - rows_k[-1][0] < 10:
        if r[3] == 'card': continue
        if rows_k[-1][3] == 'card': rows_k.pop()
    rows_k.append(r)
rows = [(t, y, lab) for t, y, lab, k in rows_k]
for (a, _, _), (b, _, _) in zip(rows, rows[1:]): assert b - a >= 10, (a, b)
print('capitoli', len(rows), 'su', len(_all), 'voci (tolte per distanza < 10 s:', [r[2]['en'] for r in _all if r not in rows_k], ')')
assert rows[0][0] == 0
fmt = lambda s: f'{s // 60}:{s % 60:02d}'


def chapters(lg, head):
    out = [head]
    for s, y, lab in rows:
        out.append(f'{fmt(s)} {lab[lg]}' + (f' ({y})' if y else ''))
    return '\n'.join(out)


TITLE = dict(
 en='EVOLUTION OF PITTSBURGH | 3D City Timelapse (1754–NOW) | No AI',
 fr="ÉVOLUTION DE PITTSBURGH | Timelapse 3D de la ville (1754–AUJOURD'HUI) | Sans IA",
 it='EVOLUZIONE DI PITTSBURGH | Timelapse 3D della città (1754–OGGI) | Senza IA',
 es='EVOLUCIÓN DE PITTSBURGH | Timelapse 3D de la ciudad (1754–HOY) | Sin IA',
 de='ENTWICKLUNG VON PITTSBURGH | 3D-Zeitraffer der Stadt (1754–HEUTE) | Ohne KI',
 pt='EVOLUÇÃO DE PITTSBURGH | Timelapse 3D da cidade (1754–HOJE) | Sem IA')

D = dict(
en="""Find your building: in what year does it appear? Pittsburgh grew from the Forks of the Ohio, where the Allegheny and Monongahela rivers meet, first with the French Fort Duquesne in 1754 and then with the British Fort Pitt. Watch 272 years of Pittsburgh, from the forts to the iron and steel city, the Renaissance, the closing of the mills and the towers of today.

NO AI imagery. Every frame is rendered from open data. Building outlines come from Allegheny County's building footprints (roof outlines compiled from aerial photography of 1992-93 and updated in 2004 and 2015). Buildings that stand today appear in the year recorded by the county assessor for their parcel, not necessarily the year of the oldest structure on it; about 89% of the footprints have a recorded year (60% of the area) and the rest are placed using their neighbors. The county data has no year for most commercial buildings, so the downtown towers use the years and heights listed on Wikipedia and Wikidata, checked against USGS LiDAR. Before 1880 the city is a reconstruction, marked on screen, and so are the Lower Hill District before its clearance in the 1950s and the warehouses and rail yards of the Point: shapes and dates there are estimated. The steel mills are not in the data and do not appear. The 1936 flood is a story card; its water level in the render is approximate. Ground and water colors come from Sentinel-2 imagery (ESA) and ESA WorldCover. Dates in the captions come from the sources listed below.

Which city should grow next? Tell me in the comments. If a building, a street or a date is wrong in your neighborhood, tell me that too: I would rather fix it. If your family lived in the Lower Hill, your memories and corrections are welcome.""",
fr="""Trouvez votre immeuble : en quelle année apparaît-il ? Pittsburgh est née à la fourche de l'Ohio, là où se rejoignent les rivières Allegheny et Monongahela, d'abord avec le fort français Duquesne en 1754, puis avec le fort britannique Pitt. Voyez 272 ans de Pittsburgh, des forts à la ville du fer et de l'acier, la Renaissance, la fermeture des aciéries et les tours d'aujourd'hui.

SANS IA. Chaque image est calculée à partir de données ouvertes. Les contours des bâtiments viennent des emprises de bâtiments du comté d'Allegheny (contours de toits relevés sur des photographies aériennes de 1992-93, mis à jour en 2004 et 2015). Les bâtiments actuels apparaissent à l'année enregistrée par l'évaluateur du comté pour leur parcelle, pas forcément celle de la plus ancienne construction ; environ 89 % des emprises ont une année enregistrée (60 % de la surface), les autres sont placées d'après leurs voisines. Les données du comté n'ont pas d'année pour la plupart des bâtiments commerciaux : les tours du centre-ville utilisent donc les années et hauteurs de Wikipédia et Wikidata, vérifiées avec le LiDAR de l'USGS. Avant 1880, la ville est une reconstitution, signalée à l'écran, de même que le Lower Hill District avant son nettoyage dans les années 1950 et les entrepôts et voies ferrées du Point : formes et dates y sont estimées. Les aciéries ne sont pas dans les données et n'apparaissent pas. La crue de 1936 est un panneau d'histoire ; son niveau d'eau dans le rendu est approximatif. Les couleurs du sol et de l'eau viennent d'images Sentinel-2 (ESA) et d'ESA WorldCover. Les dates des légendes viennent des sources ci-dessous.

Quelle ville devrait grandir la prochaine ? Dites-le-moi en commentaire. Si un bâtiment, une rue ou une date est faux dans votre quartier, dites-le aussi : je préfère le corriger. Si votre famille vivait dans le Lower Hill, vos souvenirs et vos corrections sont les bienvenus.""",
it="""Trova il tuo edificio: in che anno compare? Pittsburgh nasce alla biforcazione dell'Ohio, dove si incontrano i fiumi Allegheny e Monongahela, prima con il forte francese Duquesne nel 1754 e poi con il forte britannico Pitt. Guarda 272 anni di Pittsburgh, dai forti alla città del ferro e dell'acciaio, la Renaissance, la chiusura delle acciaierie e i grattacieli di oggi.

SENZA IA. Ogni fotogramma è calcolato da dati aperti. I contorni degli edifici vengono dalle impronte degli edifici della contea di Allegheny (contorni dei tetti ricavati da fotografie aeree del 1992-93 e aggiornati nel 2004 e nel 2015). Gli edifici di oggi compaiono nell'anno registrato dal catasto della contea per la loro particella, non necessariamente l'anno della costruzione più antica; circa l'89% delle impronte ha un anno registrato (il 60% dell'area) e le altre sono collocate in base ai vicini. I dati della contea non hanno l'anno per la maggior parte degli edifici commerciali, quindi i grattacieli del centro usano anni e altezze di Wikipedia e Wikidata, controllati con il LiDAR dell'USGS. Prima del 1880 la città è una ricostruzione, segnalata a schermo, così come il Lower Hill District prima dello sgombero degli anni Cinquanta e i magazzini e gli scali ferroviari del Point: forme e date lì sono stimate. Le acciaierie non sono nei dati e non compaiono. L'alluvione del 1936 è una scheda della storia; il livello dell'acqua nel render è approssimativo. I colori di terreno e acqua vengono da immagini Sentinel-2 (ESA) e da ESA WorldCover. Le date nelle didascalie vengono dalle fonti qui sotto.

Quale città dovrebbe crescere dopo? Dimmelo nei commenti. Se un edificio, una strada o una data è sbagliata nel tuo quartiere, dimmelo: preferisco correggere. Se la tua famiglia viveva nel Lower Hill, i tuoi ricordi e le tue correzioni sono benvenuti.""",
es="""Encuentra tu edificio: ¿en qué año aparece? Pittsburgh nació en la bifurcación del Ohio, donde se juntan los ríos Allegheny y Monongahela, primero con el fuerte francés Duquesne en 1754 y luego con el fuerte británico Pitt. Mira 272 años de Pittsburgh, desde los fuertes hasta la ciudad del hierro y del acero, el Renaissance, el cierre de las acerías y las torres de hoy.

SIN IA. Cada fotograma se calcula a partir de datos abiertos. Los contornos de los edificios vienen de las huellas de edificios del condado de Allegheny (contornos de tejados obtenidos de fotografías aéreas de 1992-93 y actualizados en 2004 y 2015). Los edificios actuales aparecen en el año registrado por el tasador del condado para su parcela, no necesariamente el de la construcción más antigua; cerca del 89 % de las huellas tiene un año registrado (el 60 % de la superficie) y el resto se coloca según sus vecinos. Los datos del condado no tienen año para la mayoría de los edificios comerciales, así que las torres del centro usan los años y alturas de Wikipedia y Wikidata, comprobados con el LiDAR del USGS. Antes de 1880 la ciudad es una reconstrucción, marcada en pantalla, igual que el Lower Hill District antes de su despeje en los años cincuenta y los almacenes y playas ferroviarias del Point: allí las formas y las fechas son estimadas. Las acerías no están en los datos y no aparecen. La inundación de 1936 es una tarjeta de la historia; su nivel de agua en el render es aproximado. Los colores del suelo y del agua vienen de imágenes Sentinel-2 (ESA) y de ESA WorldCover. Las fechas de los rótulos vienen de las fuentes de abajo.

¿Qué ciudad debería crecer después? Dímelo en los comentarios. Si un edificio, una calle o una fecha está mal en tu barrio, dímelo también: prefiero corregirlo. Si tu familia vivía en el Lower Hill, tus recuerdos y correcciones son bienvenidos.""",
de="""Finde dein Gebäude: In welchem Jahr erscheint es? Pittsburgh wuchs an der Gabelung des Ohio, wo die Flüsse Allegheny und Monongahela zusammenfließen, zuerst mit dem französischen Fort Duquesne 1754 und dann mit dem britischen Fort Pitt. Sieh 272 Jahre Pittsburgh, von den Forts zur Eisen- und Stahlstadt, zur Renaissance, zur Schließung der Stahlwerke und zu den Türmen von heute.

OHNE KI. Jedes Bild wird aus offenen Daten berechnet. Die Gebäudeumrisse stammen aus den Gebäudegrundrissen von Allegheny County (Dachumrisse aus Luftbildern von 1992-93, aktualisiert 2004 und 2015). Heute stehende Gebäude erscheinen in dem Jahr, das der Bezirksgutachter für ihr Grundstück verzeichnet hat, nicht unbedingt im Jahr des ältesten Baus darauf; rund 89 % der Grundrisse haben ein verzeichnetes Jahr (60 % der Fläche), die übrigen werden nach ihren Nachbarn gesetzt. Die Bezirksdaten haben für die meisten Geschäftsgebäude kein Jahr, deshalb nutzen die Türme der Innenstadt die Jahre und Höhen aus Wikipedia und Wikidata, geprüft mit USGS-LiDAR. Vor 1880 ist die Stadt eine Rekonstruktion, auf dem Bildschirm markiert, ebenso das Lower Hill District vor seiner Räumung in den 1950er Jahren und die Lagerhäuser und Gleisanlagen am Point: Formen und Daten sind dort geschätzt. Die Stahlwerke sind nicht in den Daten und erscheinen nicht. Das Hochwasser von 1936 ist eine Geschichtstafel; sein Wasserstand im Render ist ungefähr. Die Farben von Boden und Wasser stammen aus Sentinel-2-Bildern (ESA) und ESA WorldCover. Die Daten in den Einblendungen stammen aus den unten genannten Quellen.

Welche Stadt soll als Nächstes wachsen? Sag es mir in den Kommentaren. Wenn in deiner Nachbarschaft ein Gebäude, eine Straße oder ein Datum falsch ist, sag es mir auch: Ich korrigiere lieber. Wenn deine Familie im Lower Hill lebte, sind deine Erinnerungen und Korrekturen willkommen.""",
pt="""Encontre o seu edifício: em que ano ele aparece? Pittsburgh nasceu na bifurcação do Ohio, onde se encontram os rios Allegheny e Monongahela, primeiro com o forte francês Duquesne em 1754 e depois com o forte britânico Pitt. Veja 272 anos de Pittsburgh, dos fortes à cidade do ferro e do aço, o Renaissance, o fechamento das siderúrgicas e as torres de hoje.

SEM IA. Cada quadro é calculado a partir de dados abertos. Os contornos dos edifícios vêm das pegadas de edifícios do condado de Allegheny (contornos de telhados obtidos de fotografias aéreas de 1992-93 e atualizados em 2004 e 2015). Os edifícios atuais aparecem no ano registrado pelo avaliador do condado para o seu lote, não necessariamente o da construção mais antiga; cerca de 89% das pegadas têm um ano registrado (60% da área) e as demais são posicionadas conforme os vizinhos. Os dados do condado não têm ano para a maioria dos edifícios comerciais, então as torres do centro usam os anos e alturas da Wikipédia e do Wikidata, conferidos com o LiDAR do USGS. Antes de 1880 a cidade é uma reconstrução, marcada na tela, assim como o Lower Hill District antes da sua demolição nos anos 1950 e os armazéns e pátios ferroviários do Point: ali formas e datas são estimadas. As siderúrgicas não estão nos dados e não aparecem. A enchente de 1936 é um cartão da história; o nível da água no render é aproximado. As cores do solo e da água vêm de imagens Sentinel-2 (ESA) e do ESA WorldCover. As datas das legendas vêm das fontes abaixo.

Qual cidade deve crescer a seguir? Diga nos comentários. Se um edifício, uma rua ou uma data estiver errado no seu bairro, diga também: prefiro corrigir. Se a sua família morava no Lower Hill, suas lembranças e correções são bem-vindas.""")

HEAD = dict(en='CHAPTERS', fr='CHAPITRES', it='CAPITOLI', es='CAPÍTULOS', de='KAPITEL', pt='CAPÍTULOS')
NAME = dict(en='ENGLISH (main)', fr='FRANÇAIS', it='ITALIANO', es='ESPAÑOL', de='DEUTSCH', pt='PORTUGUÊS (BR)')

SRC = """SOURCES AND LICENSES
- Buildings: Allegheny County Building Footprint Locations (roof outlines compiled photogrammetrically from aerial photography of 1992-93, updated in 2004 and 2015) and Allegheny County property assessments (year built), via the Western Pennsylvania Regional Data Center (WPRDC).
- Downtown towers: heights and years from Wikipedia and Wikidata, checked with USGS 3DEP LiDAR.
- Streets and rivers: Allegheny County GIS (WPRDC). Terrain: USGS 3DEP 1 arc-second elevation.
- Colors: contains modified Copernicus Sentinel-2 data (ESA, 2024-2025) and ESA WorldCover 2021 (CC BY 4.0).
- History: Wikipedia EN (History of Pittsburgh, Timeline of Pittsburgh, Fort Duquesne, Fort Pitt, Point State Park, Great Fire of Pittsburgh, Pittsburgh flood of 1936, Carnegie Steel Company, Homestead strike, Great Railroad Strike of 1877, Mellon Arena, Hill District, Three Rivers Stadium, Smithfield Street Bridge, List of tallest buildings in Pittsburgh and the other articles on the sources card) and the NWS/USACE Pittsburgh gauge (1936 crest). Population: census figures via Wikipedia (Pittsburgh).
- Music: "Waking to Reality" by Unicorn Heads and "Monument" by TrackTribe, both from the YouTube Audio Library.

Rendered with an open-source 3D pipeline. Corrections are welcome in the comments."""

TAGS = ("pittsburgh, evolution of pittsburgh, pittsburgh history, history of pittsburgh, pittsburgh 3d, 3d timelapse, city timelapse, city evolution, "
        "how pittsburgh grew, fort pitt, fort duquesne, steel city, point state park, pittsburgh bridges, pittsburgh skyline, civic arena, "
        "three rivers stadium, lower hill district, pittsburgh timelapse, no ai, histoire de pittsburgh, storia di pittsburgh, 3d map, urban history, ledger of cities")
assert len(TAGS) <= 500, len(TAGS)

PIN = """Find your building: in what year does it appear? Tell me in the comments (and the year you think it should be).

Which city should grow next? Vote with a comment.

Limits, so you can check: today's buildings take the year recorded for their parcel by the county assessor, so buildings on the same parcel share a year, and about 11% of the footprints have no year and are placed by their neighbors. The county data has no year for most commercial buildings: downtown towers use Wikipedia and Wikidata years. Before 1880 the city is a reconstruction, and so are the Lower Hill District before 1956 and the Point's warehouses before the 1950s. The steel mills are not in the data. The 1936 flood is a story card and its water level is approximate. If a date, a street or a building is wrong, write it here and I will fix it.

If your family lived in the Lower Hill, your memories are welcome."""

o = ['# Pittsburgh: consegna completa YouTube (19/11/2026) — canale "Ledger of Cities"\n',
     f"Orari FINALI dal years.json vero del pod (14.822 fotogrammi = 617,6 s = 10:17; eventi rigenerati dagli stessi anni il 27/11: identici; ricavati da `montaggio/eventi_pittsburgh.json`, generati da `cities/pittsburgh/gen_consegna.py`). Regola: capitolo = t_in della carta - 2,8 s; carta/sosta = t_in; arrotondato per difetto; tutte le voci distano >= 10 s (verificato dallo script). Nessun cold open (R14): il video parte dal primo anno, un solo elenco di capitoli. Sources = 10:09. Gli orari valgono se il montaggio finale (overlay + audio) e' quello di `MONTAGGIO.md` (stessa durata del video del pod).\n"]
for lg in L:
    o += [f'\n---\n\n## {NAME[lg]}\n', '### Titolo', '```', TITLE[lg], '```', f'(lunghezza {len(TITLE[lg])})\n', '### Descrizione', '```',
          D[lg] + '\n\n' + chapters(lg, HEAD[lg]) + '\n\n' + SRC, '```']
    assert len(D[lg]) + len(SRC) + 900 < 5000, (lg, len(D[lg]))
o += ['\n---\n', f'## TAG (un solo campo YouTube, tutte le lingue insieme; {len(TAGS)} caratteri su 500)', '```', TAGS, '```\n',
      '## Commento fissato (EN; la lingua locale di Pittsburgh e\' l\'inglese: un solo blocco)', '```', PIN, '```\n',
      '## Impostazioni', 'Non per bambini. Aggiungere le 5 traduzioni (fr, it, es, de, pt-BR) di titolo e descrizione nella scheda video. Miniatura: `copertina/pittsburgh_thumb_1754_now_1280x720.jpg`. Montaggio: `MONTAGGIO.md`. Reddit, distribuzione, nota stampa: `REDDIT_DISTRIBUZIONE.md`.\n',
      '## Cosa manca / dipende', '- Link del video nei testi Reddit (`{{URL_VIDEO}}`): dopo la pubblicazione.',
      '- Licenza dei dati della contea (WPRDC dice "License not specified" sulla pagina del dataset): verificare i termini prima di pubblicare.',
      '- Livello d\'acqua dell\'alluvione 1936: nel testo e\' "approssimativo"; controllare 5:31-5:56 nel video finale.',
      '- Percentuali 89% (anni veri) e 60% (area): misura locale (`data_pittsburgh/misure_pgh.json`), non verificate altrove.']
open(os.path.join(ROOT, 'cities/pittsburgh/CONSEGNA_YOUTUBE.md'), 'w').write('\n'.join(o) + '\n')
print('ok', len(rows), 'voci; ultima', fmt(rows[-1][0]), '; tag', len(TAGS), '; desc max', max(len(D[l]) + len(SRC) + 900 for l in L))
