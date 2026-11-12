"""Controlli automatici di una citta' del kit (PASS / WARN / FAIL) con report in cities/<slug>/qa/REPORT.md.

Uso:  python -m kit.qa <slug> [--render] [--story PATH] [--data DIR] [--city JSON] [--schedule JSON] [--only a,b,c,d,e]
      (con /home/user/bl/bin/python: servono numpy, scipy, shapely, PIL; bpy solo per --render)

  a) story: schema minimo e fonti (ogni data con src esistente in sources, salvo conf "low")
  b) DATA: buildings, roads (obbligatorio), land, dem, landmarks, hist; anni fuori range
  c) densita' nelle zone storiche all'anno di partenza, 1500, 1800 (edifici vivi vs 2026): "nel 1480 non era quattro case"
  d) corridoi vuoti: raster 4 m di edifici vivi + nastri stradali visibili negli anni chiave nel centro storico;
     aree vuote allungate (strade moderne senza case e senza nastro), nastri prima del gutting, gutting non riempiti.
     PNG 2D in cities/<slug>/qa/corridoi_<anno>.png
  e) costo dei cambi (tools/costo_cambi.py) e schedule (soste ordinate, didascalie "Titolo (data)", evento forte entro 45 s)
  f) --render: fotogrammi CPU locali (480x270, 4 campioni, niente denoiser) dall'alto del centro in 4 anni chiave e uno per
     ciascuna delle 3 soste piu' lunghe, UNA sola costruzione della scena (schedule QA a blocchi fermi + --only),
     foglio contatti cities/<slug>/qa/contact.jpg
Esce con 1 se c'e' almeno un FAIL.
"""
import json, math, os, re, subprocess, sys, time

import numpy as np

from . import geo

PASS, WARN, FAIL = 'PASS', 'WARN', 'FAIL'
FPS = 24
CELL = 4.0                       # m per cella del raster dei corridoi
YEAR_KEYS = {  # campi-anno per tipo di voce della story (per la regola delle fonti)
    'zones': ('born',), 'walls': ('built', 'demolished'), 'gutting': ('from', 'until'), 'lost': ('from', 'to'),
    'fires': ('y', 'y1'), 'water': ('from', 'to'), 'bridges': ('y', 'd')}
CAPTION_RE = re.compile(r'^\S.*\S \((?=[^)]*\d)[^()]+\)$')


class Report:
    def __init__(self):
        self.rows = []      # (sezione, esito, titolo, dettaglio)
        self.images = []

    def add(self, sec, st, title, detail=''):
        self.rows.append((sec, st, title, detail))
        print(f'[qa] {sec} {st:4s} {title}' + (f' — {detail}' if detail and len(detail) < 160 else ''), flush=True)

    def worst(self, sec=None):
        s = [r[1] for r in self.rows if sec is None or r[0] == sec]
        return FAIL if FAIL in s else WARN if WARN in s else PASS

    def write(self, path, slug):
        lines = [f'# QA {slug}', '', f'Generato da `python -m kit.qa` il {time.strftime("%Y-%m-%d %H:%M")}. '
                 f'Esito complessivo: **{self.worst()}**', '']
        names = {'a': 'a) Story e fonti', 'b': 'b) DATA', 'c': 'c) Densita\' storica', 'd': 'd) Corridoi vuoti',
                 'e': 'e) Costo e schedule', 'f': 'f) Fotogrammi locali'}
        lines += ['| Sezione | Esito |', '|---|---|'] + [f'| {names[k]} | {self.worst(k)} |' for k in names if any(r[0] == k for r in self.rows)]
        for k, n in names.items():
            rr = [r for r in self.rows if r[0] == k]
            if not rr: continue
            lines += ['', f'## {n}', '']
            for _, st, t, d in rr:
                lines.append(f'- **{st}** {t}' + (f'\n  - {d}' if d else ''))
        if self.images:
            lines += ['', '## Immagini', ''] + [f'![{os.path.basename(p)}]({os.path.basename(p)})' for p in self.images]
        with open(path, 'w') as f: f.write('\n'.join(lines) + '\n')


# ---------------------------------------------------------------------------------------------------- utilita'
def _load(p, default=None):
    try:
        with open(p) as f: return json.load(f)
    except FileNotFoundError:
        return default


def _ring_arr(rings):
    """Aree (shoelace) e centroidi approssimati (media vertici) di una lista di ring [[x,y],...]."""
    n = len(rings); A = np.zeros(n); C = np.zeros((n, 2))
    for i, r in enumerate(rings):
        a = np.asarray(r, float)
        if a.ndim != 2 or len(a) < 3: continue
        x, y = a[:, 0], a[:, 1]
        A[i] = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))); C[i] = a.mean(0)
    return A, C


def _poly(P, latlons):
    from shapely.geometry import Polygon
    return Polygon(P.ring(latlons)).buffer(0)


def _all_dates(item, kind):
    out = []
    for k in YEAR_KEYS.get(kind, ()):
        v = item.get(k)
        if isinstance(v, (list, tuple)): out += [x for x in v if isinstance(x, (int, float))]
        elif isinstance(v, (int, float)): out.append(v)
    return out


# ---------------------------------------------------------------------------------------------------- a) story
def check_story(story, R):
    S = 'a'; c = story.get('city', {}); src = story.get('sources', {}) or {}
    miss = [k for k in ('slug', 'name', 'lat0', 'lon0', 'start_year', 'end_year', 'style_preset', 'data_source') if k not in c]
    R.add(S, FAIL if miss else PASS, 'chiavi city', ('mancano: ' + ', '.join(miss)) if miss else '')
    if miss and any(k in miss for k in ('lat0', 'lon0', 'start_year', 'end_year')): return
    y0, y1 = float(c['start_year']), float(c['end_year'])
    if y0 >= y1: R.add(S, FAIL, 'start_year >= end_year', f'{y0} / {y1}')
    try:
        from . import presets
        if c.get('style_preset') and c['style_preset'] not in presets.PRESETS:
            R.add(S, FAIL, 'style_preset sconosciuto', f"{c['style_preset']} (validi: {sorted(presets.PRESETS)})")
    except ImportError: pass
    bad_src = [k for k, v in src.items() if not (isinstance(v, dict) and (str(v.get('url', '')).startswith('http') or v.get('title')))]
    R.add(S, WARN if bad_src else PASS, f'{len(src)} fonti', ('senza url/titolo: ' + ', '.join(bad_src)) if bad_src else '')
    P = geo.Proj.of(story); rad = float(c.get('radius_m', 12000)) * 1.5
    nosrc, unk, far, outr, badring = [], [], [], [], []

    def chk_src(label, it, dates):
        ids = it.get('src') or []
        if isinstance(ids, str): ids = [ids]
        u = [i for i in ids if i not in src]
        if u: unk.append(f'{label}: {",".join(u)}')
        if dates and not [i for i in ids if i in src] and it.get('conf') != 'low': nosrc.append(label)

    def chk_geom(label, it):
        for key in ('ring', 'line', 'at'):
            v = it.get(key)
            if not v: continue
            pts = [v] if key == 'at' else v
            if key == 'ring' and len(pts) < 3: badring.append(label)
            for p in pts:
                if not (isinstance(p, (list, tuple)) and len(p) >= 2): badring.append(label); break
                x, y = P.L(p[0], p[1])
                if math.hypot(x, y) > rad: far.append(f'{label} ({p[0]:.4f},{p[1]:.4f})'); break
    H = story.get('history', {}) or {}
    for kind, items in H.items():
        for i, it in enumerate(items or []):
            lab = f"history.{kind}[{i}] {it.get('name', '')}".strip()
            d = _all_dates(it, kind); chk_src(lab, it, d); chk_geom(lab, it)
            for v in d:
                if -9000 < v < y0 - 1000 or v > y1 + 1: outr.append(f'{lab}: {v}')
    names = set()
    for i, lm in enumerate(story.get('landmarks', []) or []):
        lab = f"landmarks[{i}] {lm.get('name', '')}"; names.add(lm.get('name'))
        d = [p.get(k) for p in lm.get('phases', []) for k in ('y', 'y1', 'd') if isinstance(p.get(k), (int, float))]
        chk_src(lab, lm, d); chk_geom(lab, lm)
        if not lm.get('phases'): nosrc.append(lab + ' (senza phases)')
        for v in d:
            if v > y1 + 1: outr.append(f'{lab}: {v}')
    sourced = {it.get('name') for k, its in H.items() for it in (its or []) if it.get('src') or it.get('conf') == 'low'}
    sourced |= {lm.get('name') for lm in story.get('landmarks', []) or [] if lm.get('src') or lm.get('conf') == 'low'}
    ws = []
    for i, so in enumerate((story.get('regia', {}) or {}).get('soste', []) or []):
        t = str(so.get('target', '')); tn = t.split(':', 1)[1] if t.startswith('fire:') else t
        if so.get('src'): chk_src(f'soste[{i}]', so, [so.get('y0')])
        elif not (tn in sourced or t.startswith('area:')) and so.get('conf') != 'low':
            ws.append(f"soste[{i}] '{so.get('caption', '')}' (bersaglio '{t}' senza fonte)")
    for p in c.get('population', []) or []:
        if not c.get('pop_src'): ws.append('population senza pop_src'); break
    for p in c.get('pop_src', []) or []:
        if p not in src: unk.append(f'pop_src: {p}')
    R.add(S, FAIL if nosrc else PASS, 'date con fonte', ('senza src valido (e conf != low): ' + '; '.join(nosrc[:12]) + (f' … (+{len(nosrc)-12})' if len(nosrc) > 12 else '')) if nosrc else '')
    if unk: R.add(S, FAIL, 'id di fonte inesistenti', '; '.join(unk[:12]))
    if ws: R.add(S, WARN, 'soste/popolazione senza fonte', '; '.join(ws[:8]))
    if far: R.add(S, FAIL, f'coordinate oltre 1,5 x radius_m (lat/lon invertiti?)', '; '.join(far[:8]))
    if badring: R.add(S, FAIL, 'geometrie non valide (ring < 3 punti o punti malformati)', '; '.join(sorted(set(badring))[:8]))
    if outr: R.add(S, WARN, 'date fuori dall\'intervallo del video', '; '.join(outr[:8]))
    for i, z in enumerate(H.get('zones', []) or []):
        b = z.get('born', [])
        if not (isinstance(b, list) and len(b) == 2 and b[0] <= b[1]): R.add(S, FAIL, f'zona {z.get("name", i)}: born non valido', str(b))
    for i, g in enumerate(H.get('gutting', []) or []):
        if not (g.get('until') and g.get('ring')): R.add(S, FAIL, f'gutting {g.get("name", i)} senza until/ring')


# ---------------------------------------------------------------------------------------------------- b) DATA
def load_data(D):
    out = {}
    for k in ('buildings', 'hist', 'roads', 'land', 'landmarks', 'parks', 'bridges', 'landphases'):
        out[k] = _load(os.path.join(D, k + '.json'))
    out['dem'] = os.path.exists(os.path.join(D, 'dem.npz'))
    return out


def check_data(story, D, DD, R):
    S = 'b'; c = story['city']; y0, y1 = float(c['start_year']), float(c['end_year'])
    if not os.path.isdir(D): R.add(S, FAIL, 'cartella DATA assente', D); return
    R.add(S, PASS, 'cartella DATA', os.path.relpath(D, geo.ROOT))
    need = {'buildings': FAIL, 'roads': FAIL, 'hist': FAIL, 'land': WARN, 'landmarks': FAIL if story.get('landmarks') else WARN}
    for k, sev in need.items():
        v = DD.get(k)
        empty = v is None or (isinstance(v, (list, dict)) and len(v) == 0 and k != 'hist')
        if v is None: R.add(S, sev, f'{k}.json mancante', 'roads.json e\' obbligatorio (Siviglia 26 ott)' if k == 'roads' else
                             'lancia python -m kit build' if k in ('hist', 'landmarks') else '')
        elif empty: R.add(S, sev, f'{k}.json vuoto')
        else: R.add(S, PASS, f'{k}.json', f'{len(v.get("parts", [])) if isinstance(v, dict) else len(v)} voci')
    R.add(S, PASS if DD['dem'] else WARN, 'dem.npz', '' if DD['dem'] else 'manca: citta\' piatta')
    B = DD.get('buildings') or []; H = DD.get('hist') or []
    if B:
        y = np.array([b.get('y', np.nan) for b in B], float); d = np.array([b.get('d', 99999) for b in B], float)
        nan = int(np.isnan(y).sum()); fut = int((y > y1 + 1).sum()); old = int((y < y0).sum()); dly = int((d <= y).sum())
        bad = sum(1 for b in B if len(b.get('r', [])) < 3)
        st = FAIL if (nan or fut > max(5, 0.001 * len(B)) or bad) else WARN if (fut or dly) else PASS
        R.add(S, st, f'anni edifici ({len(B)})', f'senza anno {nan}, dopo {y1:.0f}: {fut}, prima di {y0:.0f} (compaiono all\'inizio): {old}, d<=y: {dly}, ring<3: {bad}')
    if H:
        y = np.array([h.get('y', np.nan) for h in H], float); d = np.array([h.get('d', np.nan) for h in H], float)
        bad = int(np.isnan(y).sum() + np.isnan(d).sum()); inv = int((d < y).sum()); fut = int((y > y1 + 1).sum())
        R.add(S, FAIL if bad else WARN if (inv or fut) else PASS, f'hist ({len(H)} predecessori)', f'senza y/d {bad}, d<y {inv}, nati dopo {y1:.0f}: {fut}')
    RD = DD.get('roads') or []
    if RD:
        y = np.array([r.get('y', np.nan) for r in RD], float)
        nan = int(np.isnan(y).sum()); fut = int((y > y1 + 1).sum())
        R.add(S, FAIL if nan else WARN if fut else PASS, f'anni strade ({len(RD)} nastri)', f'senza anno {nan}, dopo {y1:.0f}: {fut}; '
              f'visibili all\'inizio {int((y <= y0).sum())}, nel 1800 {int((y <= 1800).sum())}')


# ---------------------------------------------------------------------------------------------------- c) densita'
def _alive(Y, OB, OD):
    return (OB <= Y) & (OD > Y)


def build_objs(DD):
    """Edifici + predecessori + parti di landmark con impronta, al netto di landmarks.clear (come build_render)."""
    B = DD.get('buildings') or []; H = DD.get('hist') or []; L = DD.get('landmarks') or {}
    objs = [(b['r'], b.get('y', 0), b.get('d', 99999)) for b in B + H if len(b.get('r', [])) >= 3]
    cd = [c for c in (L.get('clear') or []) if isinstance(c, dict) and c.get('r')]
    if cd:
        try:
            import shapely
            from shapely.geometry import Polygon
            _, C0 = _ring_arr([o[0] for o in objs])
            for c in cd:
                ins = shapely.contains_xy(Polygon(c['r']).buffer(0), C0[:, 0], C0[:, 1]); yc = float(c.get('y', 0))
                objs = [(o[0], o[1], min(o[2], yc) if i else o[2]) for o, i in zip(objs, ins)]
        except Exception as e:
            print('[qa] clear a tempo ignorato:', e)
    if any(not isinstance(c, dict) for c in (L.get('clear') or [])):
        try:
            from shapely.geometry import Polygon
            from shapely.ops import unary_union
            import shapely
            cl = unary_union([Polygon(r).buffer(0) for r in L['clear'] if not isinstance(r, dict) and len(r) >= 3])
            _, C = _ring_arr([o[0] for o in objs]); keep = ~shapely.contains_xy(cl, C[:, 0], C[:, 1])
            objs = [o for o, k in zip(objs, keep) if k]
        except Exception as e:
            print('[qa] clear ignorato:', e)
    for p in L.get('parts', []):
        if p.get('r') and len(p['r']) >= 3: objs.append((p['r'], p.get('y', 0), p.get('d', 99999)))
    rings = [o[0] for o in objs]; A, C = _ring_arr(rings)
    return rings, np.array([o[1] for o in objs], float), np.array([o[2] for o in objs], float), A, C


def check_density(story, DD, R, objs):
    S = 'c'; import shapely
    c = story['city']; y0, y1 = float(c['start_year']), float(c['end_year']); P = geo.Proj.of(story)
    Z = (story.get('history', {}) or {}).get('zones', []) or []
    if not Z: R.add(S, WARN, 'nessuna zona storica nella story', 'impossibile verificare la citta\' piena all\'anno di partenza'); return
    rings, OB, OD, A, C = objs
    if not len(rings): R.add(S, FAIL, 'nessun edificio'); return
    yrs = [y for y in sorted({y0, 1500.0, 1800.0}) if y0 <= y <= y1]
    for z in Z:
        try: pz = _poly(P, z['ring'])
        except Exception as e: R.add(S, FAIL, f'zona {z.get("name")}: ring non valido', str(e)); continue
        inz = shapely.contains_xy(pz, C[:, 0], C[:, 1]); ha = pz.area / 1e4
        if ha <= 0: continue
        now = _alive(y1, OB, OD) & inz; n_now = int(now.sum()); a_now = A[now].sum()
        born1 = float((z.get('born') or [y0, y0])[-1])
        for Y in yrs:
            if Y < born1: continue
            al = _alive(Y, OB, OD) & inz; n = int(al.sum()); cov = A[al].sum() / pz.area
            ratio = n / max(1, n_now)
            cr = cov / max(1e-6, a_now / pz.area)   # copertura relativa al 2026 (zone con molto vuoto anche oggi: porti, orti)
            st = PASS if ratio >= 0.6 and cr >= 0.5 else FAIL if ratio < 0.3 or cr < 0.25 else WARN
            R.add(S, st, f'{z.get("name", "zona")} nel {Y:.0f}', f'{n} edifici vivi ({n / ha:.0f}/ha, copertura {cov:.0%}) contro {n_now} '
                  f'({n_now / ha:.0f}/ha, copertura {a_now / pz.area:.0%}) nel {y1:.0f}: rapporto {ratio:.2f}')


# ---------------------------------------------------------------------------------------------------- d) corridoi
def _raster(rings, shape, ox, oy, cell, img=None):
    from PIL import Image, ImageDraw
    im = img or Image.new('1', (shape[1], shape[0]), 0); dr = ImageDraw.Draw(im)
    H = shape[0]
    for r in rings:
        a = np.asarray(r, float)
        if len(a) < 3: continue
        px = (a[:, 0] - ox) / cell; py = H - (a[:, 1] - oy) / cell
        if px.max() < 0 or py.max() < 0 or px.min() > shape[1] or py.min() > H: continue
        dr.polygon(list(zip(px.tolist(), py.tolist())), fill=1)
    return im


def _mask(rings, shape, ox, oy, cell):
    return np.array(_raster(rings, shape, ox, oy, cell), bool)


def _land_rings(L):
    ext, holes = [], []
    for e in L or []:
        if isinstance(e, dict): ext.append(e.get('ext', [])); holes += e.get('holes', [])
        else: ext.append(e)
    return ext, holes


def _components(mask, min_cells):
    from scipy import ndimage
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0: return []
    idx = ndimage.find_objects(lab); out = []
    for i, sl in enumerate(idx, 1):
        sub = lab[sl] == i; k = int(sub.sum())
        if k < min_cells: continue
        yy, xx = np.nonzero(sub); yy = yy + sl[0].start; xx = xx + sl[1].start
        cov = np.cov(np.vstack([xx, yy])) if k > 2 else np.eye(2)
        ev = np.sort(np.linalg.eigvalsh(cov))[::-1]
        L = math.sqrt(12 * max(ev[0], 1e-6)) * CELL; W = k * CELL * CELL / max(L, 1e-6)
        out.append({'id': i, 'cells': k, 'area': k * CELL * CELL, 'L': L, 'W': W, 'sl': sl, 'mask': (lab == i)})
    return out


def check_corridors(story, D, DD, R, qadir, objs):
    S = 'd'; from scipy import ndimage; from PIL import Image, ImageDraw
    c = story['city']; y0, y1 = float(c['start_year']), float(c['end_year']); P = geo.Proj.of(story)
    H = story.get('history', {}) or {}; Z = H.get('zones', []) or []; G = H.get('gutting', []) or []
    zr = [(P.ring(z['ring']), float((z.get('born') or [y0])[0])) for z in Z if z.get('ring')]
    zf = [(P.ring(z['ring']), float((z.get('born') or [y0])[-1])) for z in Z if z.get('ring')]   # zona completa (fine rampa)
    gr = [(P.ring(g['ring']), float(g.get('from', -9999)), float(g['until']), g.get('name', 'gutting')) for g in G if g.get('ring') and g.get('until')]
    if zr:
        pts = np.array([p for r, _ in zr for p in r] + [p for g in gr for p in g[0]])
        x0, yb0 = pts.min(0) - 80; x1, yb1 = pts.max(0) + 80
    else:
        R.add(S, WARN, 'nessuna zona: centro storico = 1,5 km attorno all\'origine')
        x0 = yb0 = -1500.0; x1 = yb1 = 1500.0; zr = [([[-1500, -1500], [1500, -1500], [1500, 1500], [-1500, 1500]], y0)]
    cell = CELL
    W_, H_ = int((x1 - x0) / cell) + 1, int((yb1 - yb0) / cell) + 1
    if max(W_, H_) > 2500: R.add(S, WARN, 'centro storico molto grande: raster limitato a 10 km'); W_, H_ = min(W_, 2500), min(H_, 2500)
    shape = (H_, W_)
    rings, OB, OD, A, C = objs
    sel = (C[:, 0] > x0 - 200) & (C[:, 0] < x1 + 200) & (C[:, 1] > yb0 - 200) & (C[:, 1] < yb1 + 200)
    rings = [r for r, s in zip(rings, sel) if s]; OB, OD = OB[sel], OD[sel]
    RD = [r for r in (DD.get('roads') or []) if len(r.get('r', [])) >= 3]
    rc = np.array([np.asarray(r['r'], float).mean(0) for r in RD]) if RD else np.zeros((0, 2))
    rsel = (rc[:, 0] > x0 - 300) & (rc[:, 0] < x1 + 300) & (rc[:, 1] > yb0 - 300) & (rc[:, 1] < yb1 + 300) if len(rc) else []
    RD = [r for r, s in zip(RD, rsel) if s]; RY = np.array([r.get('y', 0) for r in RD], float)
    ext, holes = _land_rings(DD.get('land'))
    land = _mask(ext, shape, x0, yb0, cell) & ~_mask(holes, shape, x0, yb0, cell) if ext else np.ones(shape, bool)
    parks = _mask(DD.get('parks') or [], shape, x0, yb0, cell)
    lp = DD.get('landphases') or []
    keys = [y0, y0 + 100, 1800, 1900, 1950]
    keys = sorted({float(k) for k in keys if y0 <= k <= y1})
    nfail = 0
    for Y in keys:
        center = _mask([r for r, b in zr if b <= Y], shape, x0, yb0, cell)
        if not center.any(): continue
        al = (OB <= Y) & (OD > Y)
        bld = _mask([r for r, a in zip(rings, al) if a], shape, x0, yb0, cell)
        vis = _mask([r['r'] for r, y in zip(RD, RY) if y <= Y], shape, x0, yb0, cell)
        fut = _mask([r['r'] for r, y in zip(RD, RY) if y > Y], shape, x0, yb0, cell)
        wat = _mask([p['r'] for p in lp if p.get('from', -9e9) <= Y < p.get('to', 9e9)], shape, x0, yb0, cell) if lp else np.zeros(shape, bool)
        ok_ground = land | wat
        void = center & ok_ground & ~bld & ~vis & ~parks
        wide = ndimage.binary_opening(void, structure=np.ones((3, 3)), iterations=1)   # toglie i vicoli < ~12 m
        comps = _components(wide, int(1200 / cell / cell))
        A_, D_ = [], []
        for k in comps:
            if not (k['L'] >= 120 and k['L'] / max(k['W'], 1) >= 4): continue
            ff = float((k['mask'] & fut).sum()) / k['cells']
            k['fut'] = ff
            (A_ if ff >= 0.3 else D_).append(k)
        # nastri visibili prima del gutting / gutting non riempiti
        gb, gv = [], []
        for ring, gf, gu, gn in gr:
            if not (gf <= Y < gu): continue
            gm = _mask([ring], shape, x0, yb0, cell) & ok_ground & _mask([r for r, b in zf if b <= Y], shape, x0, yb0, cell)   # solo dove una zona e' gia' nata per intero
            if not gm.any(): continue
            gin = ndimage.binary_erosion(gm, iterations=2)   # 8 m dal bordo: i nastri che sfiorano il ring non contano
            v_ = float((gin & vis & ~bld).sum()) * cell * cell
            e_ = float((gm & ~bld & ~vis & ~parks).sum()) / gm.sum()
            if v_ > 60: gb.append(f'{gn}: {v_:.0f} m² di nastro visibile prima del {gu:.0f}')
            if e_ > 0.35: gv.append(f'{gn}: {e_:.0%} vuoto (case predecessore mancanti)')
        # viali larghi gia' visibili (solo informazione: se aperti sventrando, va dichiarato un gutting)
        void2 = center & ok_ground & ~bld & ~parks
        wide2 = ndimage.binary_opening(void2, structure=np.ones((3, 3)), iterations=2)
        C_ = [k for k in _components(wide2 & vis, int(2000 / cell / cell)) if k['L'] >= 200 and k['W'] >= 18 and k['L'] / k['W'] >= 5] if Y <= 1900 else []
        # immagine 2D
        img = np.zeros(shape + (3,), np.uint8); img[:] = (40, 70, 110)
        img[land] = (205, 214, 190); img[center & land] = (236, 230, 214); img[parks] = (150, 190, 120)
        img[fut & ~bld] = (250, 200, 150); img[vis] = (120, 120, 120); img[bld] = (150, 80, 55)
        for k in A_: img[k['mask']] = (230, 20, 20)
        for k in D_: img[k['mask']] = (240, 200, 0)
        for k in C_: img[k['mask'] & vis] = (60, 60, 230)
        sf = max(1, math.ceil(900 / W_))   # ingrandimento per leggere i dettagli (celle di 4 m)
        im = Image.fromarray(img).resize((W_ * sf, H_ * sf), Image.NEAREST); dr = ImageDraw.Draw(im)
        px_ = lambda a: list(zip(((a[:, 0] - x0) / cell * sf).tolist(), ((H_ - (a[:, 1] - yb0) / cell) * sf).tolist()))
        for r, b in zr:
            if b <= Y:
                a = np.asarray(r + [r[0]], float); dr.line(px_(a), fill=(0, 0, 0), width=2)
        for ring, gf, gu, gn in gr:
            a = np.asarray(ring + [ring[0]], float); dr.line(px_(a), fill=(220, 0, 220), width=2)
        for i, k in enumerate(A_ + D_ + C_, 1):
            sl = k['sl']; dr.text(((sl[1].stop + 2) * sf, sl[0].start * sf), str(i), fill=(0, 0, 0))
        hd = Image.new('RGB', (im.width, im.height + 34), (255, 255, 255)); hd.paste(im, (0, 34)); im = hd; dr = ImageDraw.Draw(im)
        dr.text((4, 2), f'{c.get("name", "")} {Y:.0f}  marrone=edifici  grigio=strade visibili  arancio chiaro=strade future', fill=(0, 0, 0))
        dr.text((4, 16), 'ROSSO=corridoio strada moderna  GIALLO=vuoto allungato  BLU=viale largo visibile  viola=gutting', fill=(0, 0, 0))
        p = os.path.join(qadir, f'corridoi_{Y:.0f}.png'); im.save(p); R.images.append(p)

        def desc(k, i):
            cx = x0 + (k['sl'][1].start + k['sl'][1].stop) / 2 * cell; cy = yb0 + (H_ - (k['sl'][0].start + k['sl'][0].stop) / 2) * cell
            la, lo = P.inv(cx, cy)
            return f'#{i} {k["L"]:.0f}x{k["W"]:.0f} m a ({la:.5f},{lo:.5f})'
        n = 1
        if A_:
            R.add(S, FAIL, f'{Y:.0f}: {len(A_)} corridoi con forma di strada moderna (niente case, niente nastro)', '; '.join(desc(k, n + i) for i, k in enumerate(A_[:6])) + f' — {os.path.basename(p)}')
            nfail += 1
        n += len(A_)
        if D_: R.add(S, WARN, f'{Y:.0f}: {len(D_)} aree vuote allungate', '; '.join(desc(k, n + i) for i, k in enumerate(D_[:6])) + f' — {os.path.basename(p)}')
        n += len(D_)
        if C_: R.add(S, WARN, f'{Y:.0f}: {len(C_)} viali larghi gia\' visibili (se aperti sventrando: gutting)', '; '.join(desc(k, n + i) for i, k in enumerate(sorted(C_, key=lambda k: -k['L'])[:5])))
        if gb: R.add(S, FAIL, f'{Y:.0f}: nastri stradali prima dell\'apertura', '; '.join(gb)); nfail += 1
        if gv: R.add(S, FAIL, f'{Y:.0f}: gutting non riempiti', '; '.join(gv)); nfail += 1
        if not (A_ or D_ or gb or gv): R.add(S, PASS, f'{Y:.0f}: nessun corridoio vuoto', os.path.basename(p))


# ---------------------------------------------------------------------------------------------------- e) costo e schedule
def _year_at(t, Y):
    return float(np.interp(t, Y[:, 0], Y[:, 1]))


def check_schedule(story, D, R, city_json, sched_path):
    S = 'e'; c = story['city']; y0, y1 = float(c['start_year']), float(c['end_year'])
    if not os.path.exists(city_json): R.add(S, FAIL, f'{os.path.basename(city_json)} mancante', 'python -m kit.city_json <slug>')
    sc = _load(sched_path)
    if sc is None: R.add(S, FAIL, f'{os.path.basename(sched_path)} mancante', 'lancia la regia (python -m kit build)'); return None
    if os.path.exists(city_json):
        t = time.time()
        p = subprocess.run([sys.executable, os.path.join(geo.ROOT, 'tools', 'costo_cambi.py'), city_json, D, sched_path], capture_output=True, text=True, cwd=geo.ROOT)
        line = (p.stdout.strip().splitlines() or [p.stderr.strip()[-300:]])[0] if (p.stdout or p.stderr) else ''
        R.add(S, PASS if p.returncode == 0 else FAIL, f'costo dei cambi ({time.time() - t:.0f} s)', line.replace('[costo] ', '') + (' ' + p.stdout.strip().splitlines()[-1] if p.returncode == 2 else ''))
    dur = float(sc.get('duration', 0)); Y = np.array(sc.get('years', []), float)
    if Y.ndim != 2 or len(Y) < 2: R.add(S, FAIL, 'schedule senza years'); return sc
    want = (story.get('regia') or {}).get('duration')
    if want and abs(float(want) - dur) > 0.5: R.add(S, WARN, 'durata diversa dalla story', f'{dur} contro {want}')
    if np.any(np.diff(Y[:, 0]) < -1e-6): R.add(S, FAIL, 'years non ordinati nel tempo')
    if Y[:, 1].min() > y0 + 1: R.add(S, FAIL, 'la regia non arriva all\'anno di partenza', f'minimo {Y[:, 1].min():.0f} > {y0:.0f}')
    if abs(Y[-1, 1] - y1) > 1: R.add(S, WARN, 'la regia non finisce all\'anno finale', f'{Y[-1, 1]:.0f}')
    cam = sc.get('cam', [])
    if not cam: R.add(S, FAIL, 'schedule senza camera')
    elif cam[-1][0] > dur + 0.5 or any(len(k) < 3 for k in cam): R.add(S, FAIL, 'chiavi camera oltre la durata o malformate')
    so = sc.get('soste', []) or []
    if not so: R.add(S, WARN, 'nessuna sosta nello schedule'); return sc
    bad, order, caps, yrs = [], [], [], []
    for i, s in enumerate(so):
        if len(s) < 5: bad.append(str(i)); continue
        t0, t1, a0, a1, cap = s[:5]
        if not (t1 > t0): bad.append(f'{i}: t1<=t0')
        if a1 < a0: bad.append(f'{i}: anni a rovescio')
        if i and t0 < so[i - 1][1] - 1e-6: order.append(f'{i}: {so[i - 1][4]} / {cap}')
        if not CAPTION_RE.match(str(cap)): caps.append(str(cap))
        ya = _year_at((t0 + t1) / 2, Y)
        if not (min(a0, a1) - max(2, 0.05 * abs(a1 - a0)) <= ya <= max(a0, a1) + max(2, 0.05 * abs(a1 - a0))): yrs.append(f'{cap}: anno a meta\' sosta {ya:.0f}')
    R.add(S, FAIL if bad else PASS, f'{len(so)} soste ben formate', '; '.join(bad))
    R.add(S, FAIL if order else PASS, 'soste ordinate e non sovrapposte', '; '.join(order[:5]))
    R.add(S, FAIL if caps else PASS, 'didascalie "Titolo (data)"', '; '.join(caps[:6]))
    if (story.get('regia') or {}).get('pacing') == 'story':   # controllo duro: le soste cadono sugli anni della storia, i cartelli tengono il proprio anno
        want = sorted((float(x['y0']), float(x.get('y1', x['y0'])), x.get('caption')) for x in (story.get('regia') or {}).get('soste', []) or []
                      if Y[:, 1].min() <= float(x['y0']) < 2026.0)
        got = sorted((float(s[2]), float(s[3]), s[4]) for s in so)
        mm = []
        if len(want) != len(got): mm.append(f'{len(got)} soste nello schedule, {len(want)} nella story')
        for w, g in zip(want, got):
            if abs(w[0] - g[0]) > 0.01 or abs(w[1] - g[1]) > 0.01: mm.append(f"{w[2]}: story {w[0]}-{w[1]}, schedule {g[0]}-{g[1]}")
        for s in so:   # e la curva degli anni deve toccare davvero [y0, y1] all'inizio e alla fine della sosta
            for tt_, yy_ in ((s[0] + 0.05, s[2]), (s[1] - 0.05, s[3])):
                if abs(_year_at(tt_, Y) - yy_) > 0.01 + 0.02 * abs(s[3] - s[2]): mm.append(f"{s[4]}: curva anni {_year_at(tt_, Y):.2f} invece di {yy_}"); break
        for c in sc.get('cards', []) or []:
            for tt_ in (c['t_in'] + 0.05, c['t_out'] - 0.05):
                if abs(_year_at(tt_, Y) - float(c['y'])) > 0.01: mm.append(f"cartello '{c['title']}': anno {_year_at(tt_, Y):.2f} invece di {c['y']}"); break
        R.add(S, FAIL if mm else PASS, 'soste e cartelli sugli anni della story (0,01)', '; '.join(mm[:6]))
    if yrs: R.add(S, WARN, 'anni delle soste diversi da quelli della regia', '; '.join(yrs[:5]))
    # evento forte entro 45 s: prima sosta, oppure incendio / evento del montaggio dopo il riavvolgimento
    tmin = float(Y[int(np.argmin(Y[:, 1])), 0])
    ev = [s[0] for s in so]
    H = story.get('history', {}) or {}
    ys = [f.get('y') for f in H.get('fires', []) or []] + [e.get('y') for e in (story.get('montaggio', {}) or {}).get('events', []) or [] if not e.get('sober')]
    tt = np.linspace(tmin, dur, 4000); yy = np.interp(tt, Y[:, 0], Y[:, 1])
    for y in ys:
        if isinstance(y, (int, float)):
            j = np.nonzero(yy >= y)[0]
            if len(j): ev.append(float(tt[j[0]]))
    first = min(ev) if ev else 1e9
    R.add(S, PASS if first <= 45 else WARN, 'evento forte entro 45 s', f'primo a {first:.1f} s')
    if (story.get('regia') or {}).get('night'):
        npth = sched_path.replace('.json', '_night.json')
        R.add(S, PASS if ('night_t' in sc and os.path.exists(npth)) else WARN, 'notte', f'night_t={sc.get("night_t")}, {os.path.basename(npth)} {"ok" if os.path.exists(npth) else "mancante"}')
    return sc


# ---------------------------------------------------------------------------------------------------- f) render locale
def _bpy_python():
    for p in (os.environ.get('KIT_BPY'), '/home/user/bl/bin/python', '/workspace/bl/bin/python', sys.executable):
        if p and os.path.exists(p):
            if subprocess.run([p, '-c', 'import bpy'], capture_output=True).returncode == 0: return p
    return None


def _cam_at(sc, t):
    K = sc['cam']; ts = [k[0] for k in K]
    j = int(np.searchsorted(ts, t))
    if j <= 0: k = K[0]; return list(k[1]), list(k[2]), float(k[3]) if len(k) > 3 else float(sc.get('lens', 35))
    if j >= len(K): k = K[-1]; return list(k[1]), list(k[2]), float(k[3]) if len(k) > 3 else float(sc.get('lens', 35))
    a, b = K[j - 1], K[j]; u = (t - a[0]) / max(1e-6, b[0] - a[0])
    lp = lambda p, q: [p[i] + (q[i] - p[i]) * u for i in range(3)]
    la = float(a[3]) if len(a) > 3 else float(sc.get('lens', 35)); lb = float(b[3]) if len(b) > 3 else la
    return lp(a[1], b[1]), lp(a[2], b[2]), la + (lb - la) * u


def qa_shots(story, sc, D):
    """Inquadrature QA: dall'alto del centro storico in 4 anni chiave + 3 soste piu' lunghe."""
    c = story['city']; y0, y1 = float(c['start_year']), float(c['end_year']); P = geo.Proj.of(story)
    from .city_json import _zone_extent
    H = story.get('history', {}) or {}
    cx, cy, e = _zone_extent(story, P, ('walls',) if H.get('walls') else ('zones', 'walls', 'gutting'))   # centro = mura, se ci sono
    dem = 0.0
    try:
        z = np.load(os.path.join(D, 'dem.npz')); ix = int((cx - float(z['x0'])) / float(z['cell'])); iy = int((cy - float(z['y0'])) / float(z['cell']))
        dem = float(z['D'][min(max(iy, 0), z['D'].shape[0] - 1), min(max(ix, 0), z['D'].shape[1] - 1)])
    except Exception: pass
    h = 2.2 * e + dem
    shots = []
    for Y in sorted({y0, y0 + 100 if y0 + 100 < 1800 else None, 1800 if y0 < 1800 < y1 else None, 1900 if y0 < 1900 < y1 else None, y1} - {None})[:5]:
        if len(shots) >= 4 and Y != y1: continue
        shots.append({'label': f'alto {Y:.0f}', 'year': Y, 'pos': [cx, cy - 0.06 * h, h], 'tgt': [cx, cy, dem], 'lens': 35})
    if sc and sc.get('soste'):
        top = sorted(sc['soste'], key=lambda s: -(s[1] - s[0]))[:3]
        Yp = np.array(sc['years'], float)
        for s in sorted(top, key=lambda s: s[0]):
            t = (s[0] + s[1]) / 2; p, tg, ln = _cam_at(sc, t)
            shots.append({'label': str(s[4])[:48], 'year': _year_at(t, Yp), 'pos': p, 'tgt': tg, 'lens': ln})
    return shots


def render_frames(story, D, city_json, sc, qadir, R):
    S = 'f'
    py = _bpy_python()
    if not py: R.add(S, WARN, 'bpy non disponibile: niente fotogrammi', 'imposta KIT_BPY=/percorso/python-con-bpy'); return
    shots = qa_shots(story, sc, D)
    HOLD = 16   # ogni inquadratura e' un blocco fermo di 16 fotogrammi: anno costante (crescita completa), camera esatta al centro
    years, cam, only = [], [], []
    for i, s in enumerate(shots):
        f0 = i * HOLD + 1; fm = f0 + HOLD // 2
        years += [[(f0 - 1) / FPS, s['year']], [(f0 + HOLD - 2) / FPS, s['year']]]
        cam.append([(fm - 1) / FPS, [round(v, 1) for v in s['pos']], [round(v, 1) for v in s['tgt']], round(s['lens'], 1)])
        only.append(fm)
    qs = {'_doc': 'schedule QA generato da kit/qa.py (blocchi fermi)', 'duration': len(shots) * HOLD / FPS, 'lens': 35, 'years': years, 'cam': cam}
    sp = os.path.join(qadir, 'schedule_qa.json'); json.dump(qs, open(sp, 'w'), indent=1)
    out = os.path.join(qadir, 'frames'); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    cmd = [py, os.path.join(geo.ROOT, 'build_render.py'), '--', D, out, '--frames', '1', str(len(shots) * HOLD), '--only', ','.join(map(str, only)),
           '--res', '480', '270', '--samples', '4', '--denoiser', 'none', '--device', 'CPU', '--schedule', sp, '--city', city_json]
    t = time.time(); log = os.path.join(qadir, 'render.log')
    print('[qa] render:', ' '.join(cmd[1:]), flush=True)
    with open(log, 'w') as lf:
        p = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=geo.ROOT, env=dict(os.environ, LOOK=os.environ.get('LOOK', '')))
    tail = open(log).read().splitlines()[-3:]
    got = [(s, os.path.join(out, f'{fm:04d}.jpg')) for s, fm in zip(shots, only)]
    ok = [(s, f) for s, f in got if os.path.exists(f)]
    if p.returncode != 0 or len(ok) < len(got):
        R.add(S, FAIL, f'render locale: {len(ok)}/{len(got)} fotogrammi (exit {p.returncode}, {time.time() - t:.0f} s)', ' | '.join(tail) + f' — log {os.path.relpath(log, geo.ROOT)}')
    else:
        R.add(S, PASS, f'render locale: {len(ok)} fotogrammi in {time.time() - t:.0f} s', os.path.relpath(log, geo.ROOT))
    if ok:
        from PIL import Image, ImageDraw
        cols = 3; rows = math.ceil(len(ok) / cols); W, Hh = 480, 270
        sheet = Image.new('RGB', (cols * W, rows * (Hh + 22)), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
        for i, (s, f) in enumerate(ok):
            x, y = (i % cols) * W, (i // cols) * (Hh + 22)
            sheet.paste(Image.open(f).convert('RGB').resize((W, Hh)), (x, y + 22))
            dr.text((x + 6, y + 5), s['label'] if s['label'].startswith('alto') else f'{s["label"]}  [anno {s["year"]:.0f}]', fill=(240, 240, 240))
        cp = os.path.join(qadir, 'contact.jpg'); sheet.save(cp, quality=90); R.images.append(cp)
        R.add(S, PASS, 'foglio contatti', os.path.relpath(cp, geo.ROOT) + ': guardalo prima del pod (strade come nastri chiari, centro pieno)')


# ---------------------------------------------------------------------------------------------------- main
def run(slug_or_story, data=None, render=False, only=None, city_json=None, sched=None):
    story = geo.load_story(slug_or_story)
    slug = story.get('city', {}).get('slug') or os.path.basename(story['_dir'])
    qadir = os.path.join(story['_dir'], 'qa'); os.makedirs(qadir, exist_ok=True)
    R = Report(); only = set(only or 'abcdef')
    if 'a' in only: check_story(story, R)
    if R.worst('a') == FAIL and any(r[2] == 'chiavi city' and r[1] == FAIL for r in R.rows):
        R.write(os.path.join(qadir, 'REPORT.md'), slug); return R
    D = data or geo.data_dir(story)
    DD = load_data(D) if os.path.isdir(D) else {}
    if 'b' in only: check_data(story, D, DD, R)
    objs = build_objs(DD) if DD.get('buildings') else None
    if 'c' in only and objs: check_density(story, DD, R, objs)
    if 'd' in only and objs: check_corridors(story, D, DD, R, qadir, objs)
    city_json = city_json or os.path.join(geo.ROOT, f'city_{slug}.json'); sp = sched or os.path.join(geo.ROOT, f'schedule_{slug}.json')
    sc = check_schedule(story, D, R, city_json, sp) if 'e' in only else _load(sp)
    if render and os.path.exists(city_json): render_frames(story, D, city_json, sc, qadir, R)
    elif render: R.add('f', FAIL, 'render impossibile: manca il city json')
    rp = os.path.join(qadir, 'REPORT.md'); R.write(rp, slug)
    print(f'[qa] esito {R.worst()} — report {os.path.relpath(rp, geo.ROOT)}', flush=True)
    return R


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0].startswith('-'): print(__doc__); return 1
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    R = run(opt('--story') or a[0], data=opt('--data'), render='--render' in a, only=(opt('--only') or 'abcdef').replace(',', ''),
          city_json=opt('--city'), sched=opt('--schedule'))
    return 1 if R.worst() == FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
