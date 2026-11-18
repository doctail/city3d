"""kit gate: il "GO dossier" del proprietario. UN comando che mette sotto gli occhi le prove PRIMA di ogni GO al pod (R2, R3, R4, R14).

Uso:  python -m kit gate <slug> [--out DIR] [--data DIR] [--schedule JSON] [--city JSON]
      (python con numpy/scipy/shapely/PIL/matplotlib E bpy: KIT_BPY=/percorso/python, vedi kit/README.md)
Scrive in DIR (default cities/<slug>/gate; con --out niente viene scritto dentro cities/<slug>):
  DOSSIER.md            tutti i blocchi sotto, con le immagini
  contact_sheet.jpg     fotogrammi REALI locali: 3 voli, hover prima/dopo del primo monumento, 2-3 monumenti piccoli,
                        primi 12 s secondo per secondo, ogni inizio capitolo
  plots.png             quota camera, distanza (equiv. 35 mm) e pitch nel tempo con le soglie R2 (1200 m; 45 gradi al 95%)
  flights.csv           tabella voli (inizio/fine, durata, anni/s, distanza mediana, quota max, pitch max, flag)
  drone_path.png        il grafico di kit.qa (percorso dall'alto)
  qa_REPORT.md          esito di kit.qa (sezioni a-e): FAIL / WARN uno per uno
  packaging_compare.jpg miniatura + titolo generati dal modello Lione approvato, affiancati a quelli di Lione (R14)
  work/                 schedule_qa.json, frames/, render.log
Banner atteso del pod (commit, durata schedule, lens), blocco costi (solo base misurata) e pacchetto packaging stanno nel DOSSIER.
Esce con 1 se c'e' un FAIL (anche R2: distanza < 1200 m, pitch >= 45 gradi al 95%) o se fotogrammi / grafici non sono stati prodotti.
"""
import csv, json, os, re, shutil, subprocess, sys, time

import numpy as np

from . import geo, qa

PASS, WARN, FAIL = qa.PASS, qa.WARN, qa.FAIL
R2 = {'dist_min': 1200.0, 'pitch_max': 45.0, 'pitch_pct': 95.0, 'slow_rate': 0.4, 'slow_s': 12.0}
# base misurata (Lione, post-mortem 16/11/2026): l'unica che esiste
LYON = {'slug': 'lyon', 'pod_s_per_video_s': 29.0, 'scene_build_min': 30.0, 'buildings': 145000, 'video_s': 565.0,
        'real_render_s': 4 * 3600 + 37 * 60, 'pod_eur_per_h': 0.5}
SIMILAR = 0.25            # la base di Lione vale solo se gli edifici differiscono meno del 25%
MIN_FRAMES = 8
INTRO_S = 12
CHAPTER_LEAD = 0.0        # il capitolo parte quando il contatore arriva al suo anno (METADATA: tempi derivati dal render)


# ------------------------------------------------------------------------------------------------ numeri camera
def camera_metrics(sc, dem=None):
    """Per ogni chiave camera: t, anno, quota (m sul mare e, con dem, sul terreno), distanza equiv. 35 mm, pitch (gradi sotto l'orizzonte)."""
    cam = sc['cam']
    t = np.array([k[0] for k in cam], float); P = np.array([k[1] for k in cam], float); L = np.array([k[2] for k in cam], float)
    lens = np.array([float(k[3]) if len(k) > 3 else float(sc.get('lens', 35)) for k in cam], float)
    Y = np.array(sc['years'], float)
    d = L - P
    dist = np.linalg.norm(d, axis=1) * 35.0 / lens
    horiz = np.hypot(d[:, 0], d[:, 1])
    pitch = np.degrees(np.arctan2(-d[:, 2], np.maximum(horiz, 1e-9)))
    agl = P[:, 2] - dem(P[:, 0], P[:, 1]) if dem is not None else None
    return {'t': t, 'year': np.interp(t, Y[:, 0], Y[:, 1]), 'alt': P[:, 2], 'agl': agl, 'dist': dist, 'pitch': pitch, 'P': P, 'L': L, 'lens': lens}


def stays_of(sc):
    """[(t0, t1, x, y, nome)] delle soste: dal drone se c'e', altrimenti dalle soste dello schedule (senza x,y)."""
    st = (sc.get('drone') or {}).get('stays')
    if st: return [tuple(x[:5]) for x in st]
    return [(s[0], s[1], None, None, s[4]) for s in (sc.get('soste') or [])]


def flight_table(sc, M):
    """Un volo = dalla fine dell'hover precedente (0 per il primo) all'arrivo del successivo. Marca i voli >= 12 s sotto 0,4 anni/s
    (stessa regola di kit.qa: esclusi l'apertura e l'avvicinamento al finale)."""
    Y = np.array(sc['years'], float); yat = lambda t: float(np.interp(t, Y[:, 0], Y[:, 1]))
    rows = []; prev = 0.0
    for i, (t0, t1, _x, _y, name) in enumerate(stays_of(sc)):
        a, b = float(prev), float(t0)
        if b - a > 0.05:
            m = (M['t'] >= a) & (M['t'] <= b)
            rate = abs(yat(b) - yat(a)) / (b - a)
            opening, finale = i == 0, name == 'finale'
            flag = (not opening) and (not finale) and (b - a) >= R2['slow_s'] and rate < R2['slow_rate']
            rows.append({'n': len(rows) + 1, 'start': a, 'end': b, 'dur': b - a, 'rate': rate, 'y0': yat(a), 'y1': yat(b),
                         'dist_med': float(np.median(M['dist'][m])) if m.any() else float('nan'),
                         'alt_max': float(M['alt'][m].max()) if m.any() else float('nan'),
                         'pitch_max': float(M['pitch'][m].max()) if m.any() else float('nan'),
                         'to': name, 'flag': bool(flag), 'note': 'opening' if opening else 'finale' if finale else ''})
        prev = t1
    return rows


def r2_numbers(M):
    return {'dist_med': float(np.median(M['dist'])), 'pitch_p95': float(np.percentile(M['pitch'], R2['pitch_pct'])),
            'pitch_max': float(M['pitch'].max()), 'frac_pitch_ok': float(np.mean(M['pitch'] < R2['pitch_max']))}


# ------------------------------------------------------------------------------------------------ inquadrature
def _year_curve_time(sc, y):
    """Primo secondo (dopo il riavvolgimento) in cui il contatore arriva all'anno y."""
    Y = np.array(sc['years'], float); tmin = float(Y[int(np.argmin(Y[:, 1])), 0])
    tt = np.linspace(tmin, float(sc['duration']), 6000); yy = np.interp(tt, Y[:, 0], Y[:, 1]); j = np.nonzero(yy >= y)[0]
    return float(tt[j[0]]) if len(j) else None


def chapter_times(story, sc):
    ch = [(float(c['y']), c.get('title', '')) for c in ((story.get('montaggio') or {}).get('chapters') or [])]
    ch += [(float(c['y']), c.get('chapter') if isinstance(c.get('chapter'), str) else c.get('title', ''))
           for c in ((story.get('montaggio') or {}).get('cards') or []) if c.get('chapter')]
    out, seen = [], set()
    for y, title in sorted(ch):
        if y in seen: continue
        seen.add(y); t = _year_curve_time(sc, y)
        if t is not None: out.append((max(0.0, t - CHAPTER_LEAD), title, y))
    return out


def _lm_size(story, D):
    """Ingombro (m) di ogni landmark dalle parti in DATA/landmarks.json; {} se non c'e'."""
    p = os.path.join(D or '', 'landmarks.json')
    if not os.path.exists(p): return {}
    try:
        parts = json.load(open(p)).get('parts') or []
    except Exception: return {}
    out = {}
    for l in story.get('landmarks') or []:
        n = l['name']; ext = []
        for q in parts:
            if not str(q.get('name', '')).startswith(n): continue
            if isinstance(q.get('r'), list) and len(q['r']):
                r = np.asarray(q['r'], float)[:, :2]; ext += [np.ptp(r[:, 0]), np.ptp(r[:, 1])]
            elif 'cx' in q: ext.append(2 * float(q.get('rad', q.get('r0', 5))))
            elif 'p0' in q: ext += [abs(q['p0'][0] - q['p1'][0]), abs(q['p0'][1] - q['p1'][1])]
        if ext: out[n] = float(max(ext))
    return out


def select_shots(story, sc, M, D=None):
    """Le inquadrature del dossier, ciascuna con 'group': flight, hover, small, intro, chapter."""
    shots = []
    cam_at = lambda t: qa._cam_at(sc, float(t))
    Y = np.array(sc['years'], float)

    def add(group, label, t):
        t = float(min(max(t, 0.0), float(sc['duration'])))
        p, tg, ln = cam_at(t); shots.append({'group': group, 'label': label, 't': t, 'year': qa._year_at(t, Y), 'pos': p, 'tgt': tg, 'lens': ln})
    flights = flight_table(sc, M)
    pick = []
    if flights:
        mid = [f for f in flights if not f['note']]
        cand = [flights[0]] + ([max(mid, key=lambda f: f['dur'])] if mid else []) + ([mid[-1]] if mid else [])
        for f in cand:
            if f not in pick: pick.append(f)
        for f in sorted(flights, key=lambda f: -f['dur']):
            if len(pick) >= 3: break
            if f not in pick: pick.append(f)
    for f in pick[:3]: add('flight', f"flight #{f['n']} -> {f['to'][:30]}", (f['start'] + f['end']) / 2)
    stays = stays_of(sc)
    tgt = {(x.get('caption')): x.get('target') for x in (story.get('regia') or {}).get('soste', []) or []}
    lm = {l['name'] for l in story.get('landmarks') or []}
    mon = [s for s in stays if tgt.get(s[4]) in lm and s[4] != 'finale']
    if mon:
        s = mon[0]; d = s[1] - s[0]
        add('hover', f'hover start: {s[4][:34]}', s[0] + min(0.5, 0.1 * d)); add('hover', f'hover end: {s[4][:34]}', s[1] - min(0.5, 0.1 * d))
        size = _lm_size(story, D)
        rest = sorted(mon[1:], key=lambda s: (size.get(tgt.get(s[4]), 1e9), s[1] - s[0]))[:3]
        for s in sorted(rest, key=lambda s: s[0])[:3]: add('small', f'small monument: {s[4][:30]}', (s[0] + s[1]) / 2)
    elif stays:
        s = stays[0]; add('hover', f'hover start: {s[4][:34]}', s[0] + 0.5); add('hover', f'hover end: {s[4][:34]}', s[1] - 0.5)
    for k in range(INTRO_S): add('intro', f'intro {k} s', k)
    for t, title, y in chapter_times(story, sc): add('chapter', f'chapter: {title[:28]}', t)
    return shots


def cover_shots(story, cj, sc, M):
    """Inquadrature per la miniatura dal 'cover' del city json: sinistra = primo anno (la prima con year == start_year, altrimenti la prima),
    destra = NOW (non notte). Senza cover: primo hover e ultimo fotogramma di volo (nota nel dossier)."""
    c = story['city']; y0, y1 = float(c['start_year']), float(c['end_year'])
    cv = (cj or {}).get('cover') or {}
    S = cv.get('shots') or []
    mk = lambda s, lab: {'group': 'thumb', 'label': lab, 'year': float(s['year']), 'pos': s['cam'][:3], 'tgt': s['cam'][3:6], 'lens': float(s.get('lens', 35)), 't': None}
    L = [s for s in S if abs(float(s['year']) - y0) < 1.0] or S[:1]
    R_ = [s for s in S if float(s['year']) >= y1 - 1 and not s.get('night')] or S[-1:]
    if L and R_:
        return mk(L[0], 'thumb left (first year)'), mk(R_[0], 'thumb right (NOW)'), cv
    Y = np.array(sc['years'], float); p0, g0, l0 = qa._cam_at(sc, 0.5); p1, g1, l1 = qa._cam_at(sc, float(sc['duration']) - 1)
    return ({'group': 'thumb', 'label': 'thumb left (fallback: t=0.5 s)', 'year': qa._year_at(0.5, Y), 'pos': p0, 'tgt': g0, 'lens': l0, 't': 0.5},
            {'group': 'thumb', 'label': 'thumb right (fallback: end)', 'year': y1, 'pos': p1, 'tgt': g1, 'lens': l1, 't': None}, cv)


# ------------------------------------------------------------------------------------------------ immagini e grafici
def _asc(t):
    import unicodedata
    return unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().replace('\u2013', '-')


def contact_sheet(frames, path, cols=4):
    from PIL import Image, ImageDraw
    W, H, B = 480, 270, 22
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * W, rows * (H + B)), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
    for i, (s, f) in enumerate(frames):
        x, y = (i % cols) * W, (i // cols) * (H + B)
        sheet.paste(Image.open(f).convert('RGB').resize((W, H)), (x, y + B))
        tt = f"t={s['t']:.1f}s " if s.get('t') is not None else ''
        dr.text((x + 5, y + 5), _asc(f"[{s['group']}] {s['label']}  {tt}y={s['year']:.0f}"), fill=(240, 240, 240))
    sheet.save(path, quality=88)
    return path


def plots(M, flights, nums, path, name, stays):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(13, 9), sharex=True, dpi=90)
    t = M['t']
    ax[0].plot(t, M['alt'], color='#1f6f8b', lw=1, label='camera altitude, m above sea')
    if M['agl'] is not None: ax[0].plot(t, M['agl'], color='#27ae60', lw=0.8, label='above ground (DEM), m')
    ax[0].set_ylabel('altitude (m)'); ax[0].legend(fontsize=7, loc='upper right')
    ax[1].plot(t, M['dist'], color='#8e44ad', lw=1)
    ax[1].axhline(R2['dist_min'], color='r', ls='--', lw=1.2, label=f"R2 minimum {R2['dist_min']:.0f} m")
    ax[1].axhline(nums['dist_med'], color='k', ls=':', lw=1, label=f"median {nums['dist_med']:.0f} m")
    ax[1].set_ylabel('distance, 35 mm equiv. (m)'); ax[1].set_yscale('log'); ax[1].legend(fontsize=7, loc='upper right')
    ax[2].plot(t, M['pitch'], color='#c0392b', lw=1)
    ax[2].axhline(R2['pitch_max'], color='r', ls='--', lw=1.2, label=f"R2 limit {R2['pitch_max']:.0f} deg (95% of the time: p95 = {nums['pitch_p95']:.0f} deg)")
    ax[2].set_ylabel('pitch below horizon (deg)'); ax[2].set_xlabel('video time (s)'); ax[2].legend(fontsize=7, loc='upper right')
    for a in ax:
        a.grid(alpha=0.3)
        for t0, t1, *_ in stays: a.axvspan(t0, t1, color='#f39c12', alpha=0.12, lw=0)
        for f in flights:
            if f['flag']: a.axvspan(f['start'], f['end'], color='#e74c3c', alpha=0.18, lw=0)
    ax[0].set_title(f"{name}: camera altitude, distance and pitch (orange = hovers, red = flagged flights >= {R2['slow_s']:.0f} s under {R2['slow_rate']} yr/s)", fontsize=9)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    return path


def title_for(name, y0):
    ys = lambda y: f'{-int(y)} BC' if y < 0 else f'{int(y)}'
    return f'EVOLUTION OF {name.upper()} | 3D City Timelapse ({ys(y0)}–NOW) | No AI', ys(y0)


def lyon_reference():
    """Titolo e miniatura approvati di Lione (cities/lyon/METADATA.md, cities/lyon/copertina)."""
    title = None; p = os.path.join(geo.ROOT, 'cities', 'lyon', 'METADATA.md')
    if os.path.exists(p):
        m = re.search(r'## Title[^\n]*\n+([^\n]+)', open(p).read()); title = m.group(1).strip() if m else None
    th = os.path.join(geo.ROOT, 'cities', 'lyon', 'copertina', 'lyon_thumb_43bc_now.jpg')
    return title, th if os.path.exists(th) else None


def packaging(story, left, right, cv, out, R):
    """Miniatura (bozza da fotogrammi CPU) + titolo dal modello di Lione, affiancati a quelli di Lione. Ritorna (titolo, path_confronto)."""
    from PIL import Image, ImageDraw
    from . import thumb_kit
    c = story['city']; title, ylab = title_for(c['name'], float(c['start_year']))
    work = os.path.join(out, 'work'); up = []
    for n, (s, f) in (('L', left), ('R', right)):
        pth = os.path.join(work, f'thumb_{n}.jpg'); Image.open(f).convert('RGB').resize((1280, 720), Image.LANCZOS).save(pth, quality=95); up.append(pth)
    th = os.path.join(out, 'thumb_draft.jpg')
    thumb_kit.compose(up[0], up[1], c['name'].upper(), ylab, 'NOW', (290, 0, 700), (290, 0, 700), th,
                      int(cv.get('text_size', 118)), int(cv.get('text_lx', 215)), int(cv.get('text_rx', 1065)))
    ltitle, lth = lyon_reference()
    W, H = 640, 360; sheet = Image.new('RGB', (2 * W + 30, H + 150), (24, 24, 24)); d = ImageDraw.Draw(sheet)
    new = Image.open(th).convert('RGB'); ref = Image.open(lth).convert('RGB') if lth else Image.new('RGB', (1280, 720), (60, 60, 60))
    sheet.paste(new.resize((W, H)), (10, 24)); sheet.paste(ref.resize((W, H)), (W + 20, 24))
    d.text((10, 6), f"NEW: {c['name']} (draft from 480x270 CPU frames: final cover must come from pod frames)", fill=(255, 214, 0))
    d.text((W + 20, 6), 'LYON, approved template' + ('' if lth else ' (file missing)'), fill=(255, 214, 0))
    d.text((10, H + 30), _asc(title), fill=(255, 255, 255)); d.text((W + 20, H + 30), _asc(ltitle or '(METADATA.md missing)'), fill=(255, 255, 255))
    for k, im in enumerate((new, ref)):            # R14 / "feed": leggibile a 168 px?
        sheet.paste(im.resize((168, 94)), (10 + k * (W + 10), H + 60))
    d.text((10 + 180, H + 70), 'feed size 168 px (left: new, right: Lyon)', fill=(200, 200, 200))
    cp = os.path.join(out, 'packaging_compare.jpg'); sheet.save(cp, quality=90)
    notes = []
    if abs(float(left[0]['year']) - float(c['start_year'])) > 1.0:
        notes.append(f"the left frame shows year {left[0]['year']:.0f}, the label says {ylab}: the frame must show the first year (Lyon's mistake)")
    if not (cv.get('shots')): notes.append("city json has no cover.shots: frames are a fallback (first hover / last flight second), define cover.shots")
    return title, ylab, cp, th, ltitle, notes


# ------------------------------------------------------------------------------------------------ banner, costi
def _git(*a):
    p = subprocess.run(['git', *a], capture_output=True, text=True, cwd=geo.ROOT)
    return p.stdout.strip() if p.returncode == 0 else ''


def banner(slug, sc, out_rel):
    """Banner che run.sh stampera' sul pod (run.sh riga 'VERSIONE'): commit, durata dello schedule, lens. Piu' stato push/dirty."""
    one = _git('log', '-1', '--oneline'); br = _git('rev-parse', '--abbrev-ref', 'HEAD')
    up = _git('rev-parse', '--abbrev-ref', '@{u}'); head = _git('rev-parse', 'HEAD'); remote = _git('rev-parse', '@{u}') if up else ''
    dirty = [l for l in _git('status', '--porcelain').splitlines() if not (out_rel and l[3:].startswith(out_rel))]
    relevant = [l for l in dirty if re.search(rf'(schedule_{slug}|city_{slug}|cities/{slug}|kit/|build_render|run\.sh|data_{slug})', l)]
    text = f"VERSIONE: {one} | schedule_{slug}: {round(float(sc['duration']))} s, lens {sc.get('lens')}"
    st = []
    if not up: st.append(f'branch {br} has no upstream: not pushed')
    elif head != remote: st.append(f'HEAD differs from {up}: push before the GO')
    if relevant: st.append(f'{len(relevant)} uncommitted changes that the pod will not see (e.g. {relevant[0].strip()})')
    return text, br, st


def count_buildings(D):
    p = os.path.join(D or '', 'buildings.json')
    if not os.path.exists(p): return None
    try: return len(json.load(open(p)))
    except Exception: return None


def hms(s):
    s = int(round(s)); return f'{s // 3600} h {s % 3600 // 60:02d} min' if s >= 3600 else f'{s // 60} min {s % 60:02d} s'


def cost_block(slug, sc, nb):
    """Costo del pod con base MISURATA (Lione). Se la citta' differisce (edifici oltre il 25% o ignoti): 'non misurato' + intervallo [Guessing]."""
    dur = float(sc['duration']); proc = 2 if sc.get('night_t') else 1     # giorno + notte = due costruzioni della scena (AVVIO, pod rule 4)
    L = LYON; L_check = L['real_render_s'] / L['video_s']
    lines = [f"Measured basis (Lyon, 16/11/2026) [Certain]: {L['pod_s_per_video_s']:.0f} pod-s per video-s (4 h 37 min real render / {L['video_s']:.0f} s = {L_check:.1f}), "
             f"+{L['scene_build_min']:.0f} min scene build per process ({L['buildings'] // 1000}K building groups), pod about {L['pod_eur_per_h']} EUR/h [Likely: over 5 EUR for about 10 h]."]
    same = nb is not None and abs(nb / L['buildings'] - 1) <= SIMILAR
    lines.append(f"This city: video {hms(dur)} ({dur:.0f} s), {proc} process(es) (day{' + night' if proc == 2 else ''}), buildings {f'{nb:,}' if nb else 'unknown (no DATA)'}.")
    if same:
        r = L['pod_s_per_video_s'] * dur; b = L['scene_build_min'] * 60 * proc; tot = r + b
        lines.append(f"Estimate scaled from Lyon [Likely]: render {hms(r)} + scene build {hms(b)} = **{hms(tot)} of pod, about {tot / 3600 * L['pod_eur_per_h']:.1f} EUR**. Say it as an estimate.")
    else:
        lo = 0.5 * L['pod_s_per_video_s'] * dur + 0.5 * L['scene_build_min'] * 60 * proc; hi = 1.5 * L['pod_s_per_video_s'] * dur + 2 * L['scene_build_min'] * 60 * proc
        lines.append(f"**non misurato**: the city differs from Lyon by more than {SIMILAR:.0%} in buildings (or the count is unknown). "
                     f"Range [Guessing]: {hms(lo)} to {hms(hi)} of pod ({lo / 3600 * L['pod_eur_per_h']:.1f} to {hi / 3600 * L['pod_eur_per_h']:.1f} EUR), "
                     f"i.e. 0.5x-1.5x the Lyon seconds per video-s and 0.5x-2x the scene build. Measure on the first full render, do not quote one number.")
    if nb and nb > 100000: lines.append('Over 100K buildings: no separate preview, go straight to `full`, check the first frames, re-render only a bad segment (R3).')
    return lines, same


# ------------------------------------------------------------------------------------------------ dossier
def pod_parity(slug, D, root=None):
    """POD PARITY: simula il passo dati di run.sh in una cartella vuota (gunzip di data_<slug>_src solo per i file mancanti, poi
    hist_<slug>.py) e confronta l'md5 di ogni json/npz con la cartella dati usata dal gate. Ritorna (differenze, nota)."""
    import gzip, hashlib, tempfile
    root = root or geo.ROOT; src = os.path.join(root, f'data_{slug}_src')
    if not os.path.isdir(src): return ['data_%s_src missing' % slug], 'no packed data: the pod would have no data'
    md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
    diffs = []
    with tempfile.TemporaryDirectory() as tmp:
        pd = os.path.join(tmp, 'data'); os.makedirs(pd)
        for g in sorted(os.listdir(src)):
            if g.endswith('.gz'):
                with gzip.open(os.path.join(src, g), 'rb') as i, open(os.path.join(pd, g[:-3]), 'wb') as o: shutil.copyfileobj(i, o)
        stub = os.path.join(root, f'hist_{slug}.py')
        if not os.path.exists(stub): diffs.append(f'hist_{slug}.py missing (run.sh would create it with make-stub)')
        else:
            r = subprocess.run([sys.executable, stub, pd], cwd=root, capture_output=True, text=True)
            if r.returncode: diffs.append('hist step failed: ' + (r.stderr or r.stdout)[-200:].replace('\n', ' '))
        for f in sorted(os.listdir(D)):
            if not (f.endswith('.json') or f.endswith('.npz')) or '.bak' in f: continue
            q = os.path.join(pd, f)
            if not os.path.exists(q): diffs.append(f'{f}: missing on the pod')
            elif md5(q) != md5(os.path.join(D, f)): diffs.append(f'{f}: differs (packed data stale)')
    return diffs, f'{len(diffs)} difference(s)'


def _md_flights(rows):
    h = ['| # | start s | end s | dur s | years/s | median dist m | max alt m | max pitch deg | to | flag |', '|---|---|---|---|---|---|---|---|---|---|']
    for f in rows:
        h.append(f"| {f['n']} | {f['start']:.1f} | {f['end']:.1f} | {f['dur']:.1f} | {f['rate']:.2f} | {f['dist_med']:.0f} | {f['alt_max']:.0f} | {f['pitch_max']:.0f} | {f['to'][:34]} | "
                 + ('**FLAG >= 12 s under 0.4 yr/s**' if f['flag'] else f"({f['note']})" if f['note'] else '') + ' |')
    return h


def run(slug, out=None, data=None, sched=None, city=None):
    """Costruisce il dossier. Ritorna (codice_uscita, Report)."""
    story = geo.load_story(slug); c = story['city']; slug = c.get('slug') or slug
    out = os.path.abspath(out or os.path.join(story['_dir'], 'gate')); work = os.path.join(out, 'work'); os.makedirs(work, exist_ok=True)
    out_rel = os.path.relpath(out, geo.ROOT) + '/' if out.startswith(geo.ROOT) else None
    R = qa.Report(); G = 'g'
    sp = sched or os.path.join(geo.ROOT, f'schedule_{slug}.json'); cjp = city or os.path.join(geo.ROOT, f'city_{slug}.json')
    sc = qa._load(sp); cj = qa._load(cjp)
    if sc is None or not sc.get('cam'):
        R.add(G, FAIL, f'{os.path.basename(sp)} missing or without camera', 'python -m kit build ' + slug)
        return 1, R
    D = data or geo.data_dir(story)
    t0 = time.time()
    # (4) kit qa, sezioni a-e, scritto nella cartella del dossier
    QR = qa.run(slug, data=D, only='abcde', city_json=cjp, sched=sp, qadir=os.path.join(work, 'qa'))
    for r in QR.rows:
        if r[1] in (FAIL,) and r[0] != 'f': R.add(G, FAIL, f'qa {r[0]}) {r[2]}', r[3])
    shutil.copy(os.path.join(work, 'qa', 'REPORT.md'), os.path.join(out, 'qa_REPORT.md'))
    dp = os.path.join(work, 'qa', 'drone_path.png')
    if os.path.exists(dp): shutil.copy(dp, os.path.join(out, 'drone_path.png'))
    # (2)(3) numeri camera, grafico, tabella voli
    dem = None
    try:
        from . import drone_kit; dem = drone_kit.load_dem(D) if os.path.exists(os.path.join(D, 'dem.npz')) else None
    except Exception as e: print('[gate] dem non letto:', e)
    M = camera_metrics(sc, dem); flights = flight_table(sc, M); nums = r2_numbers(M); stays = stays_of(sc)
    R.add(G, PASS if nums['dist_med'] >= R2['dist_min'] else FAIL, 'R2 camera distance', f"median {nums['dist_med']:.0f} m (35 mm equiv.), minimum {R2['dist_min']:.0f}; refs: Copenhagen 1397, Paris 1427")
    R.add(G, PASS if nums['pitch_p95'] < R2['pitch_max'] else FAIL, 'R2 look angle', f"p{R2['pitch_pct']:.0f} {nums['pitch_p95']:.0f} deg (limit {R2['pitch_max']:.0f}), {nums['frac_pitch_ok']:.1%} of keys under it, max {nums['pitch_max']:.0f} deg")
    fl = [f for f in flights if f['flag']]
    R.add(G, WARN if fl else PASS, 'R2 frozen-counter flights', f"{len(fl)} flight(s) >= {R2['slow_s']:.0f} s under {R2['slow_rate']} yr/s" + (': ' + '; '.join(f"#{f['n']} {f['start']:.0f}-{f['end']:.0f} s ({f['rate']:.2f})" for f in fl) if fl else ''))
    try:
        pp = plots(M, flights, nums, os.path.join(out, 'plots.png'), c.get('name', slug), stays); R.add(G, PASS, 'plots', os.path.basename(pp))
    except Exception as e:
        R.add(G, FAIL, 'plots not produced', str(e)); pp = None
    with open(os.path.join(out, 'flights.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(flights[0].keys()) if flights else ['n']); w.writeheader(); [w.writerow(r) for r in flights]
    try:
        pdif, pnote = pod_parity(slug, D)
        R.add(G, FAIL if pdif else PASS, 'POD PARITY', ('fresh unpack of data_%s_src + hist stub == local data: every json/npz md5 identical' % slug) if not pdif else '; '.join(pdif[:6]) + '  -> python -m kit pack ' + slug)
    except Exception as e: R.add(G, FAIL, 'POD PARITY', 'check not run: ' + str(e)[:200])
    # (1)(7) fotogrammi reali: una sola costruzione della scena per contact sheet + miniatura
    shots = select_shots(story, sc, M, D); tl, tr, cv = cover_shots(story, cj, sc, M)
    allshots = shots + [tl, tr]
    tmp = qa.Report()
    ok = qa.render_frames(story, D, cjp, sc, work, tmp, shots=allshots, sheet=False) or []
    for r in tmp.rows: print(f'[gate] render: {r[1]} {r[2]} {r[3][:200]}')
    got = {id(s): f for s, f in ok}
    cs = [(s, got[id(s)]) for s in shots if id(s) in got]
    sheet_path = None
    if len(cs) >= MIN_FRAMES:
        sheet_path = contact_sheet(cs, os.path.join(out, 'contact_sheet.jpg'))
        miss = len(shots) - len(cs)
        R.add(G, PASS if not miss else WARN, f'contact sheet: {len(cs)}/{len(shots)} real local frames', os.path.basename(sheet_path))
    else:
        R.add(G, FAIL, f'frames not produced: {len(cs)}/{len(shots)} (need >= {MIN_FRAMES})', ' | '.join(f'{r[2]} {r[3][:160]}' for r in tmp.rows) or 'see work/render.log')
    # packaging
    pk = None
    if id(tl) in got and id(tr) in got:
        try:
            pk = packaging(story, (tl, got[id(tl)]), (tr, got[id(tr)]), cv, out, R); R.add(G, PASS if not pk[5] else WARN, 'packaging draft', '; '.join(pk[5]) or 'thumbnail + title built from the Lyon template')
        except Exception as e: R.add(G, WARN, 'packaging draft not produced', str(e))
    else: R.add(G, WARN, 'packaging draft not produced', 'thumbnail frames missing')
    # banner, costi
    btxt, br, bst = banner(slug, sc, out_rel)
    for s in bst: R.add(G, WARN, 'banner', s)
    nb = count_buildings(D); clines, _same = cost_block(slug, sc, nb)
    # scrivi DOSSIER
    L = [f"# GO dossier: {c.get('name', slug)} ({slug})", '', f"Generated by `python -m kit gate {slug}` on {time.strftime('%Y-%m-%d %H:%M')} in {time.time() - t0:.0f} s. "
         f"**Overall: {R.worst()}** (gate checks, including every kit qa FAIL) / kit qa alone: **{QR.worst()}**. No pod before a written GO (R3).", '',
         '## Verdict (R2)', '']
    L += [f'- **{r[1]}** {r[2]}: {r[3]}' for r in R.rows]
    L += ['', '## 1. Contact sheet (real local CPU frames, 480x270)', '', f'![contact]({os.path.basename(sheet_path)})' if sheet_path else '**NOT PRODUCED**', '']
    L += ['Frames: ' + '; '.join(f"{s['group']}:{s['label']}@{s['t']:.1f}s" for s, _ in cs)] if cs else []
    L += ['', '## 2. Camera altitude, distance, pitch', '', '![plots](plots.png)' if pp else '**NOT PRODUCED**', '', '![path](drone_path.png)', '',
          f"Median distance {nums['dist_med']:.0f} m (>= {R2['dist_min']:.0f}); pitch p95 {nums['pitch_p95']:.0f} deg (< {R2['pitch_max']:.0f}); max pitch {nums['pitch_max']:.0f} deg.", '',
          '## 3. Flight table', ''] + _md_flights(flights)
    L += ['', '## 4. kit qa', '', f'Result: **{QR.worst()}** (full report: qa_REPORT.md)', '']
    for sec, st, t, d in QR.rows:
        if st in (FAIL, WARN): L.append(f'- **{st}** {sec}) {t}' + (f': {d}' if d else ''))
    if not any(r[1] in (FAIL, WARN) for r in QR.rows): L.append('- no FAIL, no WARN')
    L += ['', '## 5. Expected pod banner (quote it in the GO message)', '', '```', btxt, '```', '',
          f'Branch `{br}`. The GO message must contain, in ONE message: GPU check (`cuInit` = 0), `git pull` + this banner to verify, the launch command, the live progress one-liner, covers, and the condition to switch off (R3).', '']
    L += [f'- WARN {s}' for s in bst]
    L += ['', '## 6. Cost (measured basis only, R4)', ''] + [f'- {x}' for x in clines]
    L += ['', '## 7. Packaging (R14: series formula)', '']
    if pk:
        L += [f'- Title: `{pk[0]}`', f'- Lyon title (approved): `{pk[4]}`', f'- Thumbnail: `{pk[1]} > NOW`, city name `{c["name"].upper()}`, two full halves, no flag.',
              '- First-year hover frame and NOW frame come from the city json `cover.shots`; the draft is built from 480x270 CPU frames, the final cover is rendered on the pod frames.', '',
              '![packaging](packaging_compare.jpg)']
        L += [f'- WARN {n}' for n in pk[5]]
    else:
        L += ['**NOT PRODUCED** (needs the real frames).']
    L += ['']
    with open(os.path.join(out, 'DOSSIER.md'), 'w') as f: f.write('\n'.join(L) + '\n')
    fails = [r for r in R.rows if r[1] == FAIL]
    print(f"[gate] {c.get('name', slug)}: gate {R.worst()}, kit qa {QR.worst()}; dossier {out}/DOSSIER.md", flush=True)
    return (1 if fails else 0), R


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0].startswith('-'): print(__doc__); return 2
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    rc, _R = run(a[0], out=opt('--out'), data=opt('--data'), sched=opt('--schedule'), city=opt('--city'))
    return rc


if __name__ == '__main__':
    sys.exit(main())
