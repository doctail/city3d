# Finestre delle etichette sui monumenti (Roma, 4 nov 2026): comparsa (6 s), soste della regia, panoramica finale.
# Solo se il monumento esiste ed e' nel quadro per >40% della finestra; massimo 4 insieme. Uso (da city3d/): python3 montaggio/labs_roma.py
import json, numpy as np
LB = json.load(open('montaggio/labels_roma.json')); lm = LB['lm']; F0 = LB['F0']
S = json.load(open('schedule_roma.json')); Y = np.array(S['years']); FPS = 24; DUR = S['duration']
EV = json.load(open('montaggio/eventi_roma.json'))
END = {'Temple of Jupiter': 455, 'Palatine Palace': 600, 'Palatine Hill': 92, "Hadrian's Mausoleum": 590, "Old St Peter's": 1506, 'Servian Wall': 300}
yr = lambda t: float(np.interp(t, Y[:, 0], Y[:, 1]))
def vis(n, t):
    i = int(t * FPS) + 1 - F0
    if i >= len(lm[n]['p']): return False
    x, y, z = lm[n]['p'][i]; y_ = yr(t)
    return z > 0 and 70 < x < 1850 and 180 < y < 900 and lm[n]['y'] <= y_ < END.get(n, 9999)
wins = []
for n in lm:
    for t in np.arange(10.0, DUR - 1, 0.25):
        if vis(n, t) and yr(t) - lm[n]['y'] < 150: wins.append([round(t, 2), round(t + 6, 2), [n]]); break
SOS = {'Romulus': ['Palatine Hill'], 'Temple of Jupiter': ['Temple of Jupiter'], 'Servian': ['Servian Wall'], 'Circus Maximus': ['Circus Maximus'],
       'Caesar': ['Circus Maximus', 'Theatre of Marcellus', 'Mausoleum of Augustus', 'Temple of Jupiter'], 'Marcellus': ['Theatre of Marcellus'],
       'Colosseum (AD': ['Colosseum'], 'Trajan': ["Trajan's Column"], 'Pantheon': ['Pantheon'], 'Hadrian': ["Hadrian's Mausoleum"],
       'Caracalla': ['Baths of Caracalla'], 'Aurelian': ['Aurelian Walls', 'Colosseum', 'Circus Maximus'], "Old St Peter": ["Old St Peter's"],
       'Alaric': ['Colosseum', 'Pantheon', 'Circus Maximus'], 'aqueducts': ['Colosseum', 'Circus Maximus', 'Baths of Caracalla', 'Baths of Diocletian'],
       'Earthquake': ['Colosseum'], "New St Peter": ["St Peter's Basilica"], 'dome': ["St Peter's Basilica"], 'colonnade': ["St Peter's Square", "St Peter's Basilica"],
       'capital of Italy': ['Colosseum', 'Pantheon', "St Peter's Basilica", 'Termini Station'], 'Vittoriano': ['Vittoriano', 'Colosseum'], 'Olympics': ['Stadio Olimpico']}
for s in EV['soste']:
    full = s['title'] + ' (' + s['sub'] + ')'
    for k, v in SOS.items():
        if k in full: wins.append([s['t_in'], s['t_out'], v])
wins.append([DUR - 13, DUR - 1.5, ['Colosseum', "St Peter's Basilica", 'Vittoriano', 'Pantheon']])
ok = []
for a, b, ns in sorted(wins):
    ns2 = [n for n in ns if np.mean([vis(n, t) for t in np.arange(a, b, 0.5)]) > 0.4]
    ns2 = [n for n in ns2 if not any(a < w[1] and b > w[0] and n in w[2] for w in ok)]
    busy = sum(len(w[2]) for w in ok if a < w[1] and b > w[0])
    ns2 = ns2[:max(0, 4 - busy)]
    if ns2: ok.append([a, b, ns2])
json.dump({'labs': ok, 'end': END}, open('montaggio/labs_roma.json', 'w'), ensure_ascii=False)
for w in ok: print(f'{int(w[0] // 60)}:{w[0] % 60:04.1f}  {round(yr(w[0]))}  {w[2]}')
