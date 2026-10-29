# Pianta 2D della citta' in un anno (edifici di oggi esistenti + predecessori vivi + acqua di quell'anno), per i controlli storici.
# Uso: python tools/plan2d.py DATA uscita.png anno1,anno2,... [xmin,ymin,xmax,ymax] [colonne]
import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

def load(D):
    B = json.load(open(f'{D}/buildings.json')); H = json.load(open(f'{D}/hist.json'))
    L = json.load(open(f'{D}/land.json')); P = json.load(open(f'{D}/landphases.json')) if __import__('os').path.exists(f'{D}/landphases.json') else []
    land = unary_union([Polygon(r['ext'], r.get('holes', [])).buffer(0) for r in L])
    return B, H, land, P

def water_at(land, P, year, bb):
    W = box(*bb).difference(land)
    on = [Polygon(p['r']).buffer(0) for p in P if p['from'] <= year < p['to']]
    off = [Polygon(p['r']).buffer(0) for p in P if not (p['from'] <= year < p['to'])]
    # come build_render: una fase attiva e' terra sopra l'acqua; le zone a fasi non attive sono acqua
    return W.union(unary_union(off).intersection(box(*bb))).difference(unary_union(on))

def polys(g):
    out = []
    for q in (g.geoms if hasattr(g, 'geoms') else [g]):
        if q.geom_type == 'Polygon': out.append(np.array(q.exterior.coords)); out += [np.array(h.coords) for h in q.interiors]
    return out

def draw(ax, B, H, land, P, year, bb, title=None):
    x0, y0, x1, y1 = bb
    W = water_at(land, P, year, bb)
    ax.set_facecolor('#e9e4d6')
    ax.add_collection(PolyCollection([np.array(q.exterior.coords) for q in (W.geoms if hasattr(W, 'geoms') else [W]) if q.geom_type == 'Polygon'], facecolors='#6f97b8', edgecolors='none'))
    isl = [np.array(h.coords) for q in (W.geoms if hasattr(W, 'geoms') else [W]) if q.geom_type == 'Polygon' for h in q.interiors]
    ax.add_collection(PolyCollection(isl, facecolors='#e9e4d6', edgecolors='none'))
    def vis(o): return o['y'] <= year < o.get('d', 99999)
    inb = lambda o: x0 < o['r'][0][0] < x1 and y0 < o['r'][0][1] < y1
    now = [np.array(o['r']) for o in B if inb(o) and vis(o)]
    old = [np.array(o['r']) for o in H if inb(o) and vis(o)]
    ax.add_collection(PolyCollection(old, facecolors='#9a5b3c', edgecolors='none'))
    ax.add_collection(PolyCollection(now, facecolors='#3b3b3b', edgecolors='none'))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title or f'{year}: {len(now) + len(old)} edifici (marrone = scomparsi oggi)', fontsize=11)

if __name__ == '__main__':
    D, out, years = sys.argv[1], sys.argv[2], [float(v) for v in sys.argv[3].split(',')]
    bb = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else [-4500, -3500, 4500, 4000]
    nc = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    B, H, land, P = load(D)
    nr = (len(years) + nc - 1) // nc
    fig, axs = plt.subplots(nr, nc, figsize=(6 * nc, 6 * nr * (bb[3] - bb[1]) / (bb[2] - bb[0])), dpi=80, squeeze=False)
    for ax, y in zip(axs.flat, years): draw(ax, B, H, land, P, y, bb)
    for ax in list(axs.flat)[len(years):]: ax.axis('off')
    plt.tight_layout(); plt.savefig(out); print('ok', out)
