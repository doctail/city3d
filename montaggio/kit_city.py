#!/usr/bin/env python3
"""Kit Year Built, passo montaggio 1: genera montaggio/public/kit_<slug>.json per kit_overlay.jsx.

Uso (dalla radice del repo city3d):
    python3 montaggio/kit_city.py <slug> [--story cities/<slug>/story.json] [--schedule schedule_<slug>.json]
                                        [--pub montaggio/public] [--fps 24]

Legge:  cities/<slug>/story.json (city, regia, montaggio)         [--story]
        schedule_<slug>.json (duration, years, soste, ...)         [--schedule]
        montaggio/{years,eventi,labels,labs}_<slug>.json           (se years/eventi mancano si ricavano, vedi sotto)
Scrive: montaggio/public/kit_<slug>.json + copie kit_<slug>_{years,eventi,labels,labs}.json (cartella public di Remotion)
        e, se mancano, montaggio/years_<slug>.json (da schedule.years) ed eventi_<slug>.json (da story.montaggio.events + soste).
Tutti i tempi di dissolvenza sono DERIVATI dallo schedule (riavvolgimento, prima sosta, durata): niente numeri a mano.
Chiavi facoltative in story.city: pop_label, est_until, ticks, popmax. In story.montaggio: open (2 o 4 stringhe),
title, end, end_sub, brand, title_kicker, tok_exclude, subscribe_t, label_area, sepia_rgb, short_tag, short_seconds.
"""
import json, math, os, re, shutil, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument('slug'); ap.add_argument('--story'); ap.add_argument('--schedule')
ap.add_argument('--pub', default=os.path.join(HERE, 'public')); ap.add_argument('--fps', type=int, default=24)
a = ap.parse_args(); slug = a.slug; FPS = a.fps


def first_existing(paths, what):
    for p in paths:
        if p and os.path.exists(p): return p
    sys.exit(f'ERRORE: {what} non trovato. Cercato in: ' + ', '.join(str(p) for p in paths if p))


story_p = first_existing([a.story, os.path.join(ROOT, 'cities', slug, 'story.json')], 'story.json')
sched_p = first_existing([a.schedule, os.path.join(ROOT, f'schedule_{slug}.json'), os.path.join(ROOT, 'cities', slug, f'schedule_{slug}.json'),
                          os.path.join(ROOT, 'cities', slug, 'out', f'schedule_{slug}.json')], 'schedule')
story = json.load(open(story_p, encoding='utf-8')); S = json.load(open(sched_p, encoding='utf-8'))
city = story['city']; mont = story.get('montaggio', {}); name = city['name']
Y0, Y1 = city['start_year'], city['end_year']; DUR = S['duration']; N = round(DUR * FPS)
warn = []


def yfmt(y):
    y = int(round(y)) if abs(y - round(y)) < 0.01 else int(y)
    return f'{-y} BC' if y < 0 else (f'AD {y}' if y < 1000 else str(y))


# ---- years: {"1":anno,...,"N":anno}; se manca lo si ricava dallo schedule (interpolazione lineare, anno al fotogramma f = years(t=(f-1)/FPS)) ----
years_p = os.path.join(HERE, f'years_{slug}.json')
if not os.path.exists(years_p):
    yr = S['years']; out = {}; j = 0
    for f in range(1, N + 1):
        t = (f - 1) / FPS
        while j + 1 < len(yr) - 1 and yr[j + 1][0] <= t: j += 1
        (t0, y0), (t1, y1) = yr[j], yr[min(j + 1, len(yr) - 1)]
        out[str(f)] = round(y0 if t1 <= t0 else y0 + (y1 - y0) * min(1.0, max(0.0, (t - t0) / (t1 - t0))), 4)
    json.dump(out, open(years_p, 'w')); print(f'years_{slug}.json ricavato dallo schedule ({N} fotogrammi)')
YEARS = json.load(open(years_p))
if len(YEARS) != N: warn.append(f'years ha {len(YEARS)} fotogrammi, durata schedule {DUR}s = {N}')

# ---- tempi chiave dallo schedule ----
soste = S['soste']
assert soste, 'schedule senza soste'
rt = soste[0][0]                                    # arrivo del riavvolgimento = inizio della prima sosta
rs = next((((int(f) - 1) / FPS) for f, y in sorted(YEARS.items(), key=lambda kv: int(kv[0])) if abs(y - Y1) > 1.0), 3.0)   # inizio riavvolgimento
rs = round(rs, 1)
T = {
    'hud': [0.2, 0.9, round(DUR - 2.6, 2), round(DUR - 1.7, 2)],        # HUD: dentro subito, fuori verso la fine
    'end': [round(DUR - 1.8, 2), round(DUR - 1.0, 2)],                   # schermata finale
    'sepia': [rs, round(rs + 1.6, 2), round(rt - 0.6, 2), round(rt + 1.0, 2)],   # viraggio nel riavvolgimento
    'title': [round(rt + 0.2, 2), round(rt + 0.8, 2), round(rt + 2.6, 2), round(rt + 3.3, 2)],   # titolo all'arrivo
    'first_stop_at': round(rt + 3.4, 2),                                 # la prima sosta parte dopo il titolo
    'labels_from': round(rt + 3.4, 2),                                   # nessuna etichetta sopra il titolo
    'sepia_rgb': mont.get('sepia_rgb', [120, 82, 38]),
}

# ---- dati citta' ----
POP = city['population']
mx = max(p for _, p in POP) * 1.1
POPMAX = city.get('popmax') or next(c * 10 ** k for k in range(3, 10) for c in (1, 2, 4, 10) if c * 10 ** k >= mx)
span = Y1 - Y0
if city.get('ticks'): TICKS = city['ticks']
else:
    step = next(s for s in (10, 20, 25, 50, 100, 200, 250, 500) if span / s <= 14)
    TICKS = [y for y in range(math.ceil((Y0 + span * 0.03) / step) * step, int(Y1 - span * 0.015) + 1, step)]
EST = city.get('est_until', Y0 if Y0 >= 1800 else 1800)
if 'est_until' not in city: warn.append(f'city.est_until assente: uso {EST} (prima di quell\'anno la popolazione e\' mostrata con "~")')
C = {'Y0': Y0, 'Y1': Y1, 'POPMAX': POPMAX, 'EST_UNTIL': EST, 'TICKS': TICKS, 'popLabel': city.get('pop_label', f'CITY OF {name.upper()}'),
     'POP': POP, 'ERAS': city['eras']}
yrs_n = int(round(span)); NAME = name.upper()

# ---- testi ----
op = mont.get('open', [f'{NAME} TODAY', ''])
open2 = ([op[2], op[3]] if len(op) >= 4 else [f'{yrs_n:,} YEARS', mont.get('open_sub', 'Every building in its real year.')])
text = {
    'open': [[0.3, round(rs - 0.1, 2), op[0], op[1] if len(op) > 1 else ''], [round(rs + 0.2, 2), round(rt, 2), open2[0], open2[1]]],
    'title_kicker': mont.get('title_kicker', '3D TIMELAPSE'),
    'title': mont.get('title', [NAME, f'{yfmt(Y0)} TO NOW']),
    'end': mont.get('end', [f'{NAME} · {yrs_n:,} YEARS', 'WHICH CITY NEXT?']),
    'end_sub': mont.get('end_sub', 'Tell us in the comments'),
    'brand': mont.get('brand', 'YEAR BUILT'),
    'short_name': mont.get('short_name', NAME),
    'short_tag': mont.get('short_tag', f'{yrs_n:,} YEARS IN 30 SECONDS'),
}
sn = round(mont.get('short_seconds', 28) * FPS)
short = {'n': sn, 'a': round(rt + 1.0, 2), 'b': round(DUR - 6.0, 2)}
tok_ex = sorted({w for w in re.split(r'[^a-z]+', name.lower()) if w} | set(w.lower() for w in mont.get('tok_exclude', [])))

# ---- eventi: se manca eventi_<slug>.json lo costruisce da story.montaggio.events + schedule.soste (come eventi_roma.py) ----
ev_p = os.path.join(HERE, f'eventi_{slug}.json')
if not os.path.exists(ev_p):
    fr = sorted((int(k), v) for k, v in YEARS.items())
    def t_of(year, after):
        for f, y in fr:
            t = (f - 1) / FPS
            if t >= after and y >= year: return t
    sos = []
    for t0, t1, y0, y1, txt in soste:
        m = re.match(r'(.*?)\s*\(([^)]*)\)\s*$', txt); sos.append({'t_in': t0, 't_out': t1, 'title': m.group(1) if m else txt, 'sub': m.group(2) if m else ''})
    did, last = [], 0.0
    for e in sorted(mont.get('events', []), key=lambda e: e['y']):
        t = t_of(e['y'], rt + 3.4)
        if t is None: continue
        t = max(t, last + 0.4); dur = 4.6 if len(e['line']) < 60 else 5.4
        did.append({'t_in': round(t, 2), 't_out': round(t + dur, 2), 'date': e.get('date', yfmt(e['y'])), 'title': e['title'], 'line': e['line'], 'sober': bool(e.get('sober'))}); last = t + dur
    sub_t = mont.get('subscribe_t')
    if sub_t is None:
        sub_t = round(DUR * 0.35, 1)
        for s_ in sos:
            if s_['t_in'] - 1 <= sub_t < s_['t_out']: sub_t = round(s_['t_out'] + 0.5, 1)
    json.dump({'didascalie': did, 'soste': sos, 'subscribe_t': sub_t}, open(ev_p, 'w'), ensure_ascii=False, indent=1)
    print(f'eventi_{slug}.json costruito da story.montaggio.events ({len(did)} didascalie)')
EV = json.load(open(ev_p, encoding='utf-8'))
for c in EV['soste']:
    if not c.get('sub'): warn.append(f'sosta senza data tra parentesi nel titolo: "{c["title"]}" (formato "Titolo (data)")')

# ---- copia in public/ ----
os.makedirs(a.pub, exist_ok=True)
files = {}
for k in ('years', 'eventi', 'labels', 'labs'):
    src = os.path.join(HERE, f'{k}_{slug}.json')
    if os.path.exists(src):
        files[k] = f'kit_{slug}_{k}.json'; shutil.copyfile(src, os.path.join(a.pub, files[k]))
    else:
        files[k] = None; warn.append(f'{k}_{slug}.json assente: ' + ('nessuna etichetta sui monumenti (labels_cam.py + labs)' if k in ('labels', 'labs') else 'OBBLIGATORIO'))
for k in ('years', 'eventi'):
    if not files[k]: sys.exit(f'ERRORE: manca {k}_{slug}.json')

cfg = {'slug': slug, 'name': name, 'fps': FPS, 'n': N, 'duration': DUR, 'city': C, 't': T, 'text': text, 'tok_exclude': tok_ex,
       'label_area': mont.get('label_area', [70, 1850, 230, 900]), 'short': short, 'files': files, 'preview_video': f'{slug}_light.mp4',
       'rewind': {'start': rs, 'arrive': rt}}
json.dump(cfg, open(os.path.join(a.pub, f'kit_{slug}.json'), 'w'), ensure_ascii=False, indent=1)
print(f'OK public/kit_{slug}.json: {N} fotogrammi ({DUR}s), riavvolgimento {rs}-{rt}s, titolo {T["title"][0]}s, HUD fino a {T["hud"][3]}s')
print(f'   POPMAX {POPMAX:g}, TICKS {TICKS}, tok_exclude {tok_ex}')
for w in warn: print('  [attenzione]', w)
