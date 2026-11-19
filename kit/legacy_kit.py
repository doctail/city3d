"""Importatore generico delle citta' "vecchie": legacy (hist_/regia_/landmarks_/eventi/labels/metadata...) -> cities/<slug>/story.json.

Uso:  python -m kit legacy <slug> [--force]      (o: python -m kit.legacy_kit <slug> [--force])

Scrive cities/<slug>/story.json (camera 'drone', pacing 'story', default Marseille) e cities/<slug>/MISSING.md.
REGOLA: non inventa fatti. Cio' che i file legacy non danno resta un TODO marcato nel campo e registrato nella lista
`_legacy_gaps` della story (path, campo, motivo) e in MISSING.md. Le fonti vengono SOLO da cio' che il legacy cita
davvero (scheda di validazione <slug>/validazione/validazione.json, id nei commenti di regia/landmarks); altrimenti
l'elemento riceve conf "low" (la deroga dichiarata dalla regola 1 di qa) + gap "src".

Fonti lette (tutte opzionali, si usa quello che c'e'):
  city_<slug>.json (lat0, lon0, radius_m) · schedule_<slug>.json (soste con anni, curva degli anni -> start/end, notte)
  regia_<slug>.py (SOSTE, CAPS via AST: mai eseguito, solo valutatore ristretto; id scheda nei commenti)
  hist_<slug>.py (WATER_KEYS, anelli lat/lon letterali, punti L(lat,lon)) · bridges_<slug>.py (nomi dei ponti)
  montaggio/landmarks_<slug>.json (nome -> [x, y, h, anno]) · landmarks_<slug>.py (commenti "# --- Nome (E021 ...)" -> id)
  montaggio/labs_<slug>.json (etichette nel tempo) · montaggio/eventi_<slug>.json / eventi_<slug>.json (cartelli, sub)
  metadata_<slug>.md · traduzioni_<slug>.md · <slug>/validazione/validazione.json (fonti, popolazione, affidabilita')
  data_<slug>_src/ (completezza del pacchetto dati per `kit pack` / `kit data`)
"""
import ast, glob, gzip, json, math, os, re, sys, unicodedata

from . import geo

DRONE = {'pitch_max': 30, 'alt_max': 500, 'd_min': 1400, 'drift_vmax': 8, 'rho_max': 1400}   # default Marseille
LENS = 32
MIN_CARDS = 45
NEED_PACK = ['buildings.json', 'roads.json', 'land.json', 'dem.npz']
CONF = {'alta': 'high', 'media': 'medium', 'bassa': 'low'}


def P(f): return os.path.join(geo.ROOT, f)
def _read(f):
    try:
        with open(P(f), encoding='utf-8') as fh: return fh.read()
    except OSError: return None
def _json(f):
    t = _read(f)
    try: return json.loads(t) if t else None
    except ValueError: return None
def _norm(s): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()).strip()
def _yfmt(y): return f'{int(-y) if y < 0 else int(y)} BC' if y < 0 else str(int(y))


class Gaps:
    def __init__(self): self.rows = []
    def add(self, path, field, reason): self.rows.append({'path': path, 'field': field, 'reason': reason})
    def count(self, field): return sum(1 for r in self.rows if r['field'] == field)


# ------------------------------------------------------------------------------------------------ valutatore AST ristretto
class _Env(dict): pass


def _seval(n, env):
    """Valuta solo: costanti, tuple/liste, + - * /, nomi gia' noti, chiamate a funzioni in env (lab, L, round, abs, min, max), *spread."""
    if isinstance(n, ast.Constant): return n.value
    if isinstance(n, ast.Name):
        if n.id in env: return env[n.id]
        raise KeyError(n.id)
    if isinstance(n, (ast.Tuple, ast.List)):
        out = []
        for e in n.elts:
            if isinstance(e, ast.Starred): out += list(_seval(e.value, env))
            else: out.append(_seval(e, env))
        return tuple(out) if isinstance(n, ast.Tuple) else out
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        v = _seval(n.operand, env); return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        a, b = _seval(n.left, env), _seval(n.right, env)
        return a + b if isinstance(n.op, ast.Add) else a - b if isinstance(n.op, ast.Sub) else a * b if isinstance(n.op, ast.Mult) else a / b
    if isinstance(n, ast.Subscript):
        return _seval(n.value, env)[_seval(n.slice, env)]
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('lab', 'L', 'round', 'abs', 'min', 'max') and n.func.id in env:
        return env[n.func.id](*[_seval(a, env) for a in n.args])
    raise ValueError(type(n).__name__)


def _module(slug, pre):
    t = _read(f'{pre}_{slug}.py')
    if t is None: return None, None
    try: return ast.parse(t), t.splitlines()
    except SyntaxError: return None, None


def _assigns(tree, env, names=None):
    """Valuta in ordine gli assegnamenti di modulo; ritorna {nome: (valore, nodo)} (l'ultimo valutabile vince)."""
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            k = n.targets[0].id
            try: v = _seval(n.value, env)
            except Exception: continue
            env[k] = v; out[k] = (v, n.value)
    return out


def _ids(lines, node):
    """Id scheda (A001, E021...) nel commento a fine riga dell'elemento."""
    ln = lines[node.lineno - 1] if node.lineno - 1 < len(lines) else ''
    c = ln.split('#', 1)[1] if '#' in ln else ''
    return re.findall(r'\b([A-G]\d{3})\b', c)


# ------------------------------------------------------------------------------------------------ importazione
def _projection(city):
    lat0, lon0 = city['lat0'], city['lon0']
    return geo.Proj(lat0, lon0)


def _inv(Pj, x, y):
    la, lo = Pj.inv(x, y); return [round(la, 6), round(lo, 6)]


def _circle(lat, lon, r, n=16):
    KX = math.cos(math.radians(lat)) * 111320; KY = 110540
    return [[round(lat + r * math.sin(2 * math.pi * i / n) / KY, 6), round(lon + r * math.cos(2 * math.pi * i / n) / KX, 6)] for i in range(n)]


def _sources(slug, used_ids):
    """Fonti dalla scheda di validazione, solo per gli id usati. Ritorna (sources, info{id: (conf, row)})."""
    V = _json(f'{slug}/validazione/validazione.json') or {}
    info, src = {}, {}
    for sec, rows in V.items():
        if not isinstance(rows, list): continue
        for r in rows:
            if isinstance(r, dict) and r.get('ID'): info[r['ID']] = r
    for i in sorted(used_ids):
        r = info.get(i)
        if not r: continue
        urls = re.findall(r'https?://\S+', str(r.get('Fonte', '')))
        src[i] = {'url': urls[0].rstrip(';,') if urls else '', 'title': (r.get('Elemento') or r.get('Evento') or r.get('Definizione') or i),
                  'quote': r.get('Note', '')}
        if not urls: src[i].pop('url')
    return src, info


def _conf(ids, info):
    cs = [CONF.get(str(info[i].get('Affidabilità', '')).lower()) for i in ids if i in info]
    cs = [c for c in cs if c]
    if not cs: return 'low'
    return 'low' if 'low' in cs else ('medium' if 'medium' in cs else 'high')


def run(slug, force=False):
    story_p = geo.story_path(slug)
    if os.path.exists(story_p) and not force:
        raise FileExistsError(f'{os.path.relpath(story_p, geo.ROOT)} esiste gia\' (usa --force per rigenerare)')
    G = Gaps()
    cj = _json(f'city_{slug}.json')
    if not cj or 'lat0' not in cj: raise SystemExit(f'city_{slug}.json assente o senza lat0/lon0: niente da importare')
    sch = _json(f'schedule_{slug}.json') or {}
    meta = _read(f'metadata_{slug}.md') or ''
    Pj = geo.Proj(cj['lat0'], cj['lon0'])
    used = set()

    # ---- city
    years = sch.get('years') or []
    ys = [p[1] for p in years if isinstance(p, list) and len(p) == 2]
    start_y = int(math.floor(min(ys))) if ys else None
    end_y = int(round(max(ys))) if ys else 2026
    if start_y is None:
        G.add('city', 'start_year', 'schedule_<slug>.json senza curva degli anni'); start_y = -1
    m = re.search(r'EVOLUTION OF ([A-Z][A-Z \-\']+?) \|[^\n]*', meta)
    title = m.group(0).strip() if m else None
    name = m.group(1).title() if m else slug.capitalize()
    if not m: G.add('city', 'title/name', 'metadata_<slug>.md senza titolo serie "EVOLUTION OF <CITY> | ..."; nome dallo slug')
    if not title:
        title = f'EVOLUTION OF {name.upper()} | 3D City Timelapse ({_yfmt(start_y)}-NOW) | No AI'
    city = {'slug': slug, 'name': name, 'country': 'TODO', 'lat0': cj['lat0'], 'lon0': cj['lon0'], 'radius_m': cj.get('radius_m', 9000),
            'start_year': start_y, 'end_year': end_y, 'title': title, 'data_source': 'custom', 'data_dir': f'data_{slug}',
            'style_preset': 'mediterranean', 'population': [], 'pop_src': [], 'eras': []}
    G.add('city', 'country', 'non nei file legacy (TODO)')
    G.add('city', 'style_preset', "default 'mediterranean' (il legacy ha lo stile in city_<slug>.json, non e' un preset): scegliere")
    G.add('city', 'eras', 'nessuna periodizzazione nel legacy')
    G.add('city', 'polities', 'nessun regime/chip bandiera nel legacy: ogni regime da compilare (regola R2)')
    G.add('city', 'data_reliable_from', 'non nel legacy')

    # ---- moduli legacy letti via AST
    base_env = _Env({'round': round, 'abs': abs, 'min': min, 'max': max, 'math': math})
    lm_json = _json(f'montaggio/landmarks_{slug}.json') or {}
    def _lab(n):   # nome esatto, poi per contenimento (lmc('Maestranza') -> 'Maestranza Bullring')
        if n in lm_json: return tuple(lm_json[n][:2])
        for k, v in lm_json.items():
            if _norm(n) and (_norm(n) in _norm(k) or _norm(k) in _norm(n)): return tuple(v[:2])
        raise KeyError(n)
    base_env['lab'] = base_env['lmc'] = _lab
    base_env['L'] = lambda la, lo: Pj.L(la, lo)
    rt, rl = _module(slug, 'regia')
    ht, hl = _module(slug, 'hist')
    bt, bl = _module(slug, 'bridges')
    if rt is None: G.add('regia', 'SOSTE/CAPS', f'regia_{slug}.py assente o non analizzabile: soste da schedule, cartelli da eventi')
    renv = _Env(base_env)
    R = _assigns(rt, renv) if rt else {}
    henv = _Env(base_env)
    H = _assigns(ht, henv) if ht else {}

    # ---- landmarks (montaggio/landmarks_<slug>.json: nome -> [x, y, h, anno])
    lt = _read(f'landmarks_{slug}.py') or ''
    lm_ids = {}   # nome normalizzato -> id scheda, dai commenti "# --- Nome (E021 ...; E022 ...)"
    for mm in re.finditer(r'#\s*-{2,}\s*(.+?)\s*\(([^)]*)\)', lt):
        ids = re.findall(r'\b([A-G]\d{3})\b', mm.group(2))
        if ids: lm_ids[_norm(mm.group(1))] = ids
    landmarks, lm_xy = [], {}
    for nm, v in lm_json.items():
        if not (isinstance(v, list) and len(v) >= 4): continue
        x, y, h, yr = v[:4]
        ids = []
        for k, i in lm_ids.items():
            if k and (k in _norm(nm) or _norm(nm) in k): ids = i; break
        used.update(ids)
        lm = {'name': nm, 'kind': 'TODO', 'at': _inv(Pj, x, y), 'footprint': 'auto', 'params': {'h': h},
              'phases': [{'y': yr}], 'label': True}
        if ids: lm['src'] = ids
        landmarks.append(lm); lm_xy[nm] = (x, y)
        lm['_legacy'] = f'geometria bespoke in landmarks_{slug}.py; anno = {yr} (primo anno della scheda), altezza {h} m'
    if landmarks:
        G.add('landmarks', 'kind', f'{len(landmarks)} monumenti con geometria bespoke in landmarks_{slug}.py: scegliere un preset di kit/landmarks_kit.py o tenere il modulo legacy; phases con solo il primo anno')
    else:
        G.add('landmarks', 'landmarks', f'montaggio/landmarks_{slug}.json assente')

    # ---- soste: anni/didascalie dallo schedule; bersaglio/id/durata dalla regia
    soste, rsost = [], []
    if 'SOSTE' in R:
        for node, tup in zip(R['SOSTE'][1].elts if isinstance(R['SOSTE'][1], ast.List) else [], R['SOSTE'][0]):
            rsost.append((tup, _ids(rl, node), node))
    elif rt is not None:   # lista non valutabile in blocco (es. bersaglio con funzione ignota): elemento per elemento, bersaglio perso
        for n in rt.body:
            if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'SOSTE' and isinstance(n.value, ast.List):
                for node in n.value.elts:
                    try: tup = _seval(node, renv)
                    except Exception:
                        try: tup = tuple(_seval(e, renv) for e in node.elts[:4]) + (None,)
                        except Exception: continue
                    rsost.append((tup, _ids(rl, node), node))
                break
    by_cap = {t[3]: (t, ids, nd) for t, ids, nd in rsost if len(t) > 3}

    def tgt_of(raw, node=None):
        if isinstance(raw, tuple) and raw and isinstance(raw[0], str): raw = raw[0]   # ('Nome monumento', dist, incl, az0, az1, lens)
        """-> (target, note) dal 5o elemento della sosta legacy."""
        if isinstance(raw, str):
            for nm in lm_xy:
                if _norm(nm) == _norm(raw): return nm, None
            for nm in lm_xy:
                if _norm(raw) in _norm(nm) or _norm(nm) in _norm(raw): return nm, f"nome legacy '{raw}' -> '{nm}'"
            for k, (v, _) in H.items():
                if _norm(k) == _norm(raw) and isinstance(v, tuple) and len(v) == 2:
                    la, lo = Pj.inv(*v); return f'area:[{la:.5f},{lo:.5f},500]', f"punto '{k}' di hist_{slug}.py"
            return None, f"bersaglio legacy '{raw}' non risolto"
        if isinstance(raw, tuple) and len(raw) >= 2 and all(isinstance(a, (int, float)) for a in raw[:2]):
            # se l'espressione legacy parte da una variabile che e' la posizione di un monumento (ND, BASTILLE...) il bersaglio e' quel monumento
            if node is not None:
                for nn in ast.walk(node):
                    if isinstance(nn, ast.Name) and isinstance(renv.get(nn.id), tuple) and len(renv[nn.id]) == 2:
                        for nm, p in lm_xy.items():
                            if abs(p[0] - renv[nn.id][0]) < 0.6 and abs(p[1] - renv[nn.id][1]) < 0.6:
                                return nm, f"punto di mira legacy = {nn.id} spostato (monumento '{nm}')"
            if lm_xy:
                nm, d = min(((n, math.hypot(raw[0] - p[0], raw[1] - p[1])) for n, p in lm_xy.items()), key=lambda a: a[1])
                if d <= 700: return nm, f"punto di mira legacy a {d:.0f} m da '{nm}' (monumento piu' vicino)"
            la, lo = Pj.inv(raw[0], raw[1]); return f'area:[{la:.5f},{lo:.5f},450]', 'nessun monumento entro 700 m: area attorno al punto di mira legacy'
        return None, 'bersaglio legacy assente'

    for s in sch.get('soste') or []:
        if not (isinstance(s, list) and len(s) >= 5): continue
        t0, t1, y0, y1, cap = s[:5]
        so = {'y0': y0, 'y1': y1, 'dur': round(t1 - t0, 2), 'caption': cap, 'shot': 'medium'}
        t = by_cap.get(cap); ids = []
        if t:
            tup, ids, nd = t
            so['dur'] = tup[2]
            tg, note = tgt_of(tup[4] if len(tup) > 4 else None, nd.elts[4] if len(tup) > 4 and isinstance(nd, ast.Tuple) and len(nd.elts) > 4 else None)
        else:
            tg, note = None, 'sosta senza riga in regia_<slug>.py'
        if tg:
            so['target'] = tg
            if note: so['_legacy_target'] = note
            if tg.startswith('area:'): G.add(f'regia.soste[{len(soste)}]', 'target', f"'{cap}': {note}")
        else:
            so['target'] = 'TODO'; G.add(f'regia.soste[{len(soste)}]', 'target', f"'{cap}': {note}")
        ids = [i for i in ids]
        used.update(ids)
        if ids: so['src'] = ids
        so['conf'] = '__conf__'; so['_ids'] = ids
        soste.append(so)
    if not soste: G.add('regia', 'soste', 'nessuna sosta nello schedule legacy')
    npx = sum(1 for so in soste if 'piu\' vicino' in so.get('_legacy_target', '') or 'non risolto' in so.get('_legacy_target', '') or '-> ' in so.get('_legacy_target', ''))
    if npx: G.add('regia.soste', 'target', f"{npx} bersagli dedotti per vicinanza/nome approssimato (vedi _legacy_target di ogni sosta): verificare che il monumento sia quello giusto")
    G.add('regia.soste', 'weight', f'{len(soste)} soste senza peso (0-10 o "max"): default = forza dell\'fx; scegliere almeno la piu\' forte come "max"')
    G.add('regia.soste', 'fx', 'nessun fx del montaggio nel legacy (campo omesso)')

    # ---- cartelli (cards): CAPS della regia (con id scheda) altrimenti didascalie di eventi_<slug>.json
    ev = _json(f'montaggio/eventi_{slug}.json') or _json(f'eventi_{slug}.json') or {}
    didas = ev.get('didascalie') or []
    labs = (_json(f'montaggio/labs_{slug}.json') or {}).get('labs') or []
    by_title = {d.get('title'): d for d in didas}

    def year_at(t):
        best = None
        for tt, yy in years:
            if tt <= t: best = yy
            else: break
        return best
    raw_cards = []
    if 'CAPS' in R:
        for node, tup in zip(R['CAPS'][1].elts, R['CAPS'][0]):
            if len(tup) >= 4: raw_cards.append((tup[0], tup[1], tup[2], tup[3], _ids(rl, node)))
    else:
        for d in didas:
            y = year_at(d.get('t_in', 0))
            if y is None: continue
            raw_cards.append((round(y, 1), d.get('date', ''), d.get('title', ''), d.get('line', ''), []))
    cards, nomatch, noids = [], 0, 0
    for y, date, ttl, line, ids in raw_cards:
        c = {'y': y, 'title': ttl, 'lines': [line] if line else [], 'hold_s': 5, 'legacy_date': date}
        d = by_title.get(ttl)
        if d and d.get('t_out') and d.get('t_in') is not None:
            c['hold_s'] = round(d['t_out'] - d['t_in'], 1)
            lb = sorted({n for a, b, names in labs if a < d['t_out'] and b > d['t_in'] for n in names})
            if lb: c['labels'] = lb
            if d.get('sober'): c['sober'] = True
        else: nomatch += 1
        used.update(ids)
        if ids: c['src'] = ids
        else: noids += 1
        c['_ids'] = ids
        cards.append(c)
    cards.sort(key=lambda c: c['y'])
    G.add('montaggio.cards', 'cards', f'{len(cards)} cartelli importati ({"da CAPS di regia" if "CAPS" in R else "da eventi_<slug>.json"}); '
          + (f'SOTTO IL MINIMO di {MIN_CARDS}: ne mancano {MIN_CARDS - len(cards)}' if len(cards) < MIN_CARDS else f'minimo {MIN_CARDS} rispettato'))
    if nomatch: G.add('montaggio.cards', 'hold_s', f'{nomatch} cartelli senza didascalia in eventi (hold_s 5 s di default, nessuna etichetta monumento)')
    G.add('montaggio.cards', 'target/shot', 'il legacy non ha bersaglio per i cartelli (volano durante i tratti)')
    G.add('montaggio', 'chapters', 'nessun capitolo storico nel legacy (capitoli_<slug>.txt e metadata sono per orari di video, non per anni): tracciare dalle ere')

    # ---- fonti, conf (dopo aver raccolto gli id usati)
    # popolazione dalla scheda (sezione D, 'Valore HUD')
    V = _json(f'{slug}/validazione/validazione.json') or {}
    pops = []
    for r in V.get('D', []) if isinstance(V.get('D'), list) else []:
        if r.get('Valore HUD') is None or r.get('Da (anno)') is None: continue
        pops.append((r, 'historical estimate' if str(r.get('Stima', '')).lower().startswith('s') else 'census'))
    for r, _ in pops: used.add(r['ID'])
    sources, info = _sources(slug, used)
    for lst in (soste, cards):
        for it in lst:
            ids = it.pop('_ids', [])
            it['src'] = [i for i in ids if i in sources] or None
            if it['src'] is None: it.pop('src')
            if 'conf' in it or lst is cards:
                it['conf'] = _conf(ids, info) if ids else 'low'
    unknown = sorted({i for lst in (soste, cards) for it in lst for i in (it.get('src') or [])} - set(sources))
    for lm in landmarks:
        ids = [i for i in lm.get('src', []) if i in sources]
        if ids: lm['src'] = ids; lm['conf'] = _conf(ids, info)
        else: lm.pop('src', None); lm['conf'] = 'low'
    if pops:
        city['population'] = [[r['Da (anno)'], r['Valore HUD'], lab] for r, lab in pops]
        city['pop_src'] = [r['ID'] for r, _ in pops if r['ID'] in sources]
        city['pop_conf'] = [_conf([r['ID']], info) for r, _ in pops]
    else:
        G.add('city', 'population', 'nessuna serie di popolazione nel legacy (la scheda non c\'e\'): HUD senza popolazione')
    no_src = {'soste': sum(1 for s in soste if not s.get('src')), 'cards': sum(1 for c in cards if not c.get('src')),
              'landmarks': sum(1 for l in landmarks if not l.get('src'))}
    if not sources:
        G.add('sources', 'sources', f'nessuna scheda di validazione per {slug}: 0 fonti; tutti gli elementi importati sono conf "low" (deroga regola 1) e vanno risalvati con una fonte reale')
    else:
        G.add('sources', 'sources', f'{len(sources)} fonti dalla scheda (id citati nei commenti legacy); elementi senza id/fonte: '
              f"{no_src['soste']} soste, {no_src['cards']} cartelli, {no_src['landmarks']} monumenti (conf low)")
    if unknown: G.add('sources', 'ids', 'id citati nei commenti ma assenti dalla scheda: ' + ', '.join(unknown))

    # ---- storia: acqua (WATER_KEYS), anelli letterali, mura (walls_*.json), ponti (nomi)
    hist = {'zones': [], 'walls': [], 'gutting': [], 'lost': [], 'fires': [], 'floods': [], 'water': [], 'bridges': []}
    wk = H.get('WATER_KEYS', (None,))[0]
    for w in wk or []:
        try: wid, la, lo, r, a, b, kind = w
        except Exception: continue
        item = {'name': f'{wid} (water {kind})', 'ring': _circle(la, lo, r), 'c': 'field', 'src': [wid] if wid in sources else None, 'conf': _conf([wid], info) if wid in sources else 'low',
                '_legacy': f"cerchio r={r} m attorno al punto di riferimento della scheda (non il poligono reale); {a}-{b}; tipo {kind}"}
        # fill = acqua -> terra: la terra compare dall'anno finale; dig = terra -> acqua: la terra sparisce dall'anno iniziale
        if kind == 'fill': item['from'] = b          # 'to' assente = per sempre (default del kit)
        else: item['to'] = a                         # 'from' assente = da sempre
        if item['src'] is None: item.pop('src')
        hist['water'].append(item)
    if hist['water']: G.add('history.water', 'ring', f"{len(hist['water'])} voci d'acqua come CERCHI attorno al punto di riferimento (WATER_KEYS): sostituire con i poligoni reali")
    for k, (v, node) in H.items():   # anelli lat/lon letterali (>= 5 punti vicini al centro): mura/recinti con anni ignoti
        if isinstance(v, (list, tuple)) and len(v) >= 5 and all(isinstance(p, tuple) and len(p) == 2 and all(isinstance(a, float) for a in p) for p in v) \
                and all(abs(p[0] - cj['lat0']) < 0.5 and abs(p[1] - cj['lon0']) < 0.5 for p in v) and not k.endswith('_P'):
            hist['walls'].append({'name': k.title(), 'ring': [[a, b] for a, b in v], 'built': [None, None], 'demolished': None, 'conf': 'low',
                                  '_legacy': f'anello letterale {k} in hist_{slug}.py; anni non nel legacy'})
            G.add(f'history.walls[{len(hist["walls"]) - 1}]', 'built/demolished/src', f'{k}: solo il tracciato; costruzione/demolizione/altezza/fonte da compilare')
    for f in glob.glob(P(f'data_{slug}_src/walls_*.json')):
        j = _json(os.path.relpath(f, geo.ROOT))
        if isinstance(j, dict) and isinstance(j.get('ring'), list) and len(j['ring']) >= 3:
            hist['walls'].append({'name': f"Walls ({os.path.basename(f)})", 'ring': [_inv(Pj, x, y) for x, y in j['ring']], 'built': [None, None],
                                  'demolished': None, 'conf': 'low', '_legacy': f'anello metrico di {os.path.basename(f)}'})
            G.add(f'history.walls[{len(hist["walls"]) - 1}]', 'built/demolished/src', f'{os.path.basename(f)}: solo il tracciato; anni e fonte da compilare')
    bt_names = []
    if bt:
        bn = _read(f'bridges_{slug}.py') or ''
        m2 = re.search(r'^B\s*=\s*\{(.*?)^\}', bn, re.S | re.M)
        bt_names = re.findall(r"^\s*'([a-z0-9_]+)'\s*:", m2.group(1), re.M) if m2 else []
    if bt_names: G.add('history.bridges', 'bridges', f'{len(bt_names)} ponti nel legacy (geometria da OSM, non letterale): ' + ', '.join(bt_names[:14]) + (' ...' if len(bt_names) > 14 else '') + ' -> servono line [lat,lon], larghezza, anni, fonte')
    else: G.add('history.bridges', 'bridges', f'nessun bridges_{slug}.py leggibile (vedi anche bridges.json di radice, non per citta\')')
    G.add('history.zones', 'zones', 'nessuna zona pre-catasto con anello e anni di nascita nel legacy (le zone sono codice in hist_<slug>.py: nuclei/villaggi con parametri a mano): anelli, born, era_height da compilare')
    G.add('history', 'walls/gutting/lost/fires', 'mura/sventramenti/edifici perduti/incendi sono generati da codice o da dati esterni (ALPAGE ecc.) nel legacy: non importabili in modo letterale')
    for k in list(hist):
        if not hist[k] and k in ('floods',): del hist[k]

    # ---- eventi (montaggio.events): sub delle soste
    events = []
    for e in ev.get('soste') or []:
        if e.get('sub'):
            s = next((s for s in soste if s['caption'] == e.get('title')), None)
            if s: events.append({'y': s['y0'], 'title': e['title'], 'line': e['sub'], 'sober': False})
    # ---- regia
    night = bool(sch.get('night_t')) or os.path.exists(P(f'schedule_{slug}_night.json'))
    regia = {'camera': 'drone', 'music': 'waking_monument', 'duration': 'auto', 'max_duration': 660, 'night': night, 'pacing': 'story',
             'open': {'year': end_y, 'rewind_to': start_y}, 'soste': soste, 'rmin': 1.0, 'rmax': 8.0,
             'drone': dict(DRONE), 'lens': LENS}
    if night: regia['night_hold'] = 15
    n_years = end_y - start_y
    mont = {'style': 'mattia', 'open': [f'{name.upper()} TODAY'], 'title': [name.upper(), f'{_yfmt(start_y)} TO NOW'],
            'end': [f'{name.upper()} · {n_years:,} YEARS', 'WHICH CITY NEXT?'], 'label_years': True, 'cards': cards,
            'events': events, 'cta': 'Which city should grow next? Tell me in the comments',
            'sources_card': {'seconds': 8, 'max': 14, 'no_ai': 'NO AI: every frame is rendered from open data'}}
    G.add('montaggio', 'open', "solo il titolo base ('<CITY> TODAY'): aggiungere la popolazione di oggi con fonte")

    # ---- metadata / traduzioni (solo registrati, non ricopiati: restano nei file legacy)
    legacy_meta = {'metadata_file': f'metadata_{slug}.md' if meta else None,
                   'translations_file': f'traduzioni_{slug}.md' if _read(f'traduzioni_{slug}.md') else None,
                   'translation_languages': re.findall(r'^## ([A-Z][^\n]*)$', _read(f'traduzioni_{slug}.md') or '', re.M),
                   'video_chapter_lines': len(re.findall(r'^\d{1,2}:\d{2}', meta, re.M)),
                   'old_thumbnail_files': sorted(os.path.basename(f) for f in glob.glob(P(f'copertina_{slug}*.jpg')))}
    G.add('metadata', 'chapters/description/tags', "capitoli con orari (legacy: orari del vecchio render, non validi per il drone), descrizione, tag, commento fisso, Reddit: da rifare nel formato kit (cities/<slug>/METADATA.md)")

    # ---- pacchetto dati
    gz = P(f'data_{slug}_src')
    have = {f[:-3] if f.endswith('.gz') else f for f in os.listdir(gz)} if os.path.isdir(gz) else set()
    miss_pack = [f for f in NEED_PACK if f not in have]
    pack = {'dir': f'data_{slug}_src', 'present': sorted(f for f in have if f.endswith(('.json', '.npz'))), 'missing_for_kit': miss_pack,
            'complete': not miss_pack}
    if miss_pack: G.add('data', 'data_src', f'data_{slug}_src incompleto per kit data/pack: mancano ' + ', '.join(miss_pack))

    # ---- story
    for it in hist.values():
        pass
    story = {'version': 1, 'city': city, 'sources': sources, 'history': hist, 'landmarks': landmarks, 'qa': {'accept': []},
             'regia': regia, 'montaggio': mont, 'legacy': {**legacy_meta, 'data_package': pack},
             '_legacy_gaps': G.rows}
    os.makedirs(os.path.dirname(story_p), exist_ok=True)
    with open(story_p, 'w', encoding='utf-8') as fh: json.dump(story, fh, indent=1, ensure_ascii=False)
    write_missing(slug, story, G, pack)
    return story, G


def write_missing(slug, story, G, pack):
    c, rg, mo = story['city'], story['regia'], story['montaggio']
    L = [f'# MISSING — {c["name"]} (importato dal legacy da `python -m kit legacy {slug}`)', '',
         'Campi richiesti dal formato kit che il legacy non poteva dare. Niente e\' stato inventato: i campi sono `TODO`/vuoti/`conf: "low"` e sono elencati in `story._legacy_gaps`.', '',
         '## Importato', f'- soste: {len(rg["soste"])} (con bersaglio risolto: {sum(1 for s in rg["soste"] if s["target"] != "TODO")}, con fonte: {sum(1 for s in rg["soste"] if s.get("src"))})',
         f'- cartelli: {len(mo["cards"])} (con fonte: {sum(1 for x in mo["cards"] if x.get("src"))}); minimo richiesto {MIN_CARDS}: ' + ('OK' if len(mo['cards']) >= MIN_CARDS else f'MANCANO {MIN_CARDS - len(mo["cards"])}'),
         f'- monumenti: {len(story["landmarks"])} (con fonte: {sum(1 for x in story["landmarks"] if x.get("src"))}); tutti `kind: TODO`',
         f'- fonti: {len(story["sources"])} · popolazione: {len(c["population"])} punti · acqua: {len(story["history"]["water"])} · mura: {len(story["history"]["walls"])} · ponti: 0 · zone: 0',
         f'- eventi: {len(mo["events"])} · camera drone (pitch_max {rg["drone"]["pitch_max"]}, alt_max {rg["drone"]["alt_max"]}, d_min {rg["drone"]["d_min"]}, drift_vmax {rg["drone"]["drift_vmax"]}, rho_max {rg["drone"]["rho_max"]}, lens {rg["lens"]})', '',
         '## Da compilare (storico)', '']
    sections = [('Fonti', ['sources', 'ids']), ('Regimi/polities, ere, popolazione', ['polities', 'eras', 'population', 'data_reliable_from', 'country', 'style_preset', 'title/name', 'start_year']),
                ('Zone, mura, acqua, ponti', ['zones', 'ring', 'built/demolished/src', 'bridges', 'walls/gutting/lost/fires']),
                ('Monumenti', ['kind', 'landmarks']), ('Soste (bersaglio, peso, fx)', ['target', 'weight', 'fx', 'soste']),
                ('Cartelli e capitoli', ['cards', 'hold_s', 'target/shot', 'chapters']), ('Montaggio e consegna', ['open', 'chapters/description/tags']),
                ('Pacchetto dati', ['data_src'])]
    done = set()
    for title, fields in sections:
        rows = [r for r in G.rows if r['field'] in fields]
        if not rows: continue
        L.append(f'### {title}')
        for r in rows: L.append(f'- `{r["path"]}` · {r["field"]}: {r["reason"]}'); done.add(id(r))
        L.append('')
    rest = [r for r in G.rows if id(r) not in done]
    if rest:
        L.append('### Altro')
        L += [f'- `{r["path"]}` · {r["field"]}: {r["reason"]}' for r in rest]; L.append('')
    L += ['## Pacchetto dati per `kit pack`/`kit data`', f'- cartella: `{pack["dir"]}`; presenti: {", ".join(pack["present"]) or "nessuno"}',
          '- completo' if pack['complete'] else f'- INCOMPLETO, mancano: {", ".join(pack["missing_for_kit"])}', '']
    with open(os.path.join(os.path.dirname(geo.story_path(slug)), 'MISSING.md'), 'w', encoding='utf-8') as fh: fh.write('\n'.join(L))


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a: print(__doc__); return 2
    try: story, G = run(a[0], force='--force' in a)
    except FileExistsError as e: print(e); return 1
    print(f'story: soste {len(story["regia"]["soste"])}, cartelli {len(story["montaggio"]["cards"])}, monumenti {len(story["landmarks"])}, lacune {len(G.rows)}')
    return 0


if __name__ == '__main__': sys.exit(main())
