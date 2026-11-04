# Eventi del video di Roma (4 nov 2026): didascalie (alto a sinistra) a tempo dall'anno, soste dalla regia, Subscribe.
# Uso (da city3d/): python3 montaggio/eventi_roma.py -> montaggio/eventi_roma.json
import json, re
Y = json.load(open('montaggio/years_roma.json')); FPS = 24
S = json.load(open('schedule_roma.json'))
fr = sorted((int(k), v) for k, v in Y.items())
def t_of(year, after=8.0):
    for f, y in fr:
        t = (f - 1) / FPS
        if t >= after and y >= year: return t
    return None
def yfmt(y):
    y = int(round(y)) if abs(y - round(y)) < 0.01 else int(y)
    return f'{-y} BC' if y < 0 else (f'AD {y}' if y < 1000 else str(y))
# (anno, titolo, riga)  -- niente doppioni delle soste
EV = [
    (-616, 'The Etruscan kings', 'They drain the marshes between the hills. The Forum is born.'),
    (-509, 'No more kings', 'The last king is driven out. Rome becomes a republic.'),
    (-390, 'The Gauls sack Rome', 'Only the Capitoline Hill holds out.'),
    (-312, 'The Appian Way', 'The first great Roman road, and the first aqueduct.'),
    (-146, 'Carthage destroyed', 'Rome now rules the Mediterranean.'),
    (-44, 'The Ides of March', 'Julius Caesar is murdered in the Senate.'),
    (-27, 'Augustus, first emperor', '"I found Rome a city of brick and left it a city of marble."'),
    (64, 'The Great Fire', 'Ten of the fourteen districts burn. Nero rebuilds.'),
    (117, 'The empire at its largest', 'From Scotland to Iraq, ruled from this city.'),
    (180, 'A million people', 'The largest city the world has ever seen.'),
    (330, 'A new capital', 'Constantine moves the emperor to Constantinople.'),
    (476, 'The end of the Western Empire', 'The last emperor in the West is deposed.'),
    (590, 'Plague and floods', 'Fewer than 50,000 people live inside walls built for a million.'),
    (800, 'Charlemagne', "Crowned emperor in Old St Peter's on Christmas Day."),
    (1084, 'The Normans', 'Allies of the Pope burn much of the city.'),
    (1309, 'The Popes leave', 'The papacy moves to Avignon. Rome falls to ~17,000 people.'),
    (1377, 'The Popes return', 'Rome starts to grow again, around the Vatican.'),
    (1527, 'The Sack of Rome', "Charles V's unpaid troops loot the city for months."),
    (1762, 'Trevi Fountain', 'Finished after 30 years of work.'),
    (1798, 'Napoleon', 'French troops arrive. The Pope is taken prisoner.'),
    (1922, 'March on Rome', 'Mussolini takes power.'),
    (1944, 'Liberation', 'Allied troops enter Rome on 4 June 1944.', True),
]
soste = []
for t0, t1, y0, y1, txt in S['soste']:
    m = re.match(r'(.*?)\s*\(([^)]*)\)\s*$', txt)
    title, sub = (m.group(1), m.group(2)) if m else (txt, '')
    soste.append({'t_in': t0, 't_out': t1, 'title': title, 'sub': sub})
did = []
last = 0.0
for e in EV:
    y, ti, li = e[:3]; t = t_of(y)
    if t is None: continue
    t = max(t, last + 0.4)
    # le soste stanno in basso al centro: la didascalia (alto a sinistra) puo' sovrapporsi
    dur = 4.6 if len(li) < 60 else 5.4
    did.append({'t_in': round(t, 2), 't_out': round(t + dur, 2), 'date': yfmt(y), 'title': ti, 'line': li, 'sober': bool(e[3]) if len(e) > 3 else False})
    last = t + dur
out = {'didascalie': did, 'soste': soste, 'subscribe_t': 96.0}
json.dump(out, open('montaggio/eventi_roma.json', 'w'), ensure_ascii=False, indent=1)
for d in did: print(f"{int(d['t_in'] // 60)}:{d['t_in'] % 60:04.1f}  {d['date']:>8}  {d['title']}")
