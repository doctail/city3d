# Finestre delle etichette sui monumenti (Parigi, 31 ott 2026): comparsa (primo istante in cui il monumento esiste ed e' nel
# quadro, 6 s) + soste della regia + panoramica finale prima della notte. Solo se il monumento e' visibile per >40% della finestra.
# Uso: python3 montaggio/labs_parigi.py  (da city3d/) -> montaggio/labs_parigi.json
import json, numpy as np
LB = json.load(open('montaggio/labels_parigi.json')); lm = LB['lm']; F0 = LB['F0']
S = json.load(open('schedule_parigi.json')); Y = np.array(S['years']); FPS = 24
EV = json.load(open('eventi_parigi.json'))
END = {'Tuileries Palace': 1883, 'Bastille': 1790, 'Grand Châtelet': 1810}
yr = lambda t: float(np.interp(t, Y[:, 0], Y[:, 1]))
def vis(n, t):
    x, y, z = lm[n]['p'][int(t * FPS) + 1 - F0]; y_ = yr(t)
    return z > 0 and 70 < x < 1850 and 230 < y < 900 and lm[n]['y'] <= y_ < END.get(n, 9999)
night = S['night_t']; wins = []
for n in lm:
    for t in np.arange(10.0, night, 0.25):
        if vis(n, t) and yr(t) - lm[n]['y'] < 60: wins.append([round(t, 2), round(t + 6, 2), [n]]); break
SOS = {'Philippe': ['Notre-Dame', 'Louvre'], 'Charles V': ['Bastille', 'Louvre'], 'Pont Neuf': ['Pont Neuf', 'Louvre'], 'Invalides': ['Les Invalides'],
       'Bastille falls': ['Bastille'], 'Canal': ['Hôtel de Ville'], 'Haussmann': ['Louvre', 'Hôtel de Ville', 'Palais Garnier'], 'Eiffel': ['Eiffel Tower'],
       'Montparnasse': ['Tour Montparnasse', 'Centre Pompidou'], 'Notre-Dame: fire': ['Notre-Dame', 'Sainte-Chapelle']}
for s in EV['soste']:
    for k, v in SOS.items():
        if k in s['title']: wins.append([s['t_in'], s['t_out'], v])
wins.append([night - 14, night - 1, ['Eiffel Tower', 'Sacré-Cœur', 'Tour Montparnasse', 'La Défense']])
ok = []
for a, b, ns in sorted(wins):
    ns2 = [n for n in ns if np.mean([vis(n, t) for t in np.arange(a, b, 0.5)]) > 0.4]
    ns2 = [n for n in ns2 if not any(a < w[1] and b > w[0] and n in w[2] for w in ok)]   # niente doppioni sovrapposti
    if ns2: ok.append([a, b, ns2])
json.dump({'labs': ok, 'end': END}, open('montaggio/labs_parigi.json', 'w'), ensure_ascii=False)
for w in ok: print(f'{int(w[0] // 60)}:{w[0] % 60:04.1f}  {round(yr(w[0]))}  {w[2]}')
