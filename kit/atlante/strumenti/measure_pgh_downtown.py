# Pittsburgh: misure centro prima/dopo (uso: python measure_pgh_downtown.py DATA_DIR [DATA_DIR ...]); legge buildings.json + buildings_y0_prov.json.
# Per anello 0,5/1/1,5 km: poligoni, quota anno vero (catasto) / esterno (Wikipedia/Wikidata) / stimato; mediane anno e altezza entro 1,2 km; torri >=100 m con altezza reale (lidar/wiki).
import json, sys, os, numpy as np
for D in sys.argv[1:]:
    B = json.load(open(os.path.join(D, 'buildings.json'))); P = json.load(open(os.path.join(D, 'buildings_y0_prov.json')))
    c = np.array([np.mean(o['r'], axis=0) for o in B]); d = np.hypot(c[:, 0], c[:, 1]); y = np.array([o['y'] for o in B]); h = np.array([o['h'] for o in B]); hs = np.array([o['hs'] for o in B])
    est = np.zeros(len(B), bool); est[P['estimated_indices']] = True; ext = np.zeros(len(B), bool); ext[P.get('external_year_indices', [])] = True
    out = {}
    for r in (500, 1000, 1500):
        m = d <= r; out[f'<={r}m'] = {'n': int(m.sum()), 'anno_catasto%': round(100 * float((m & ~est & ~ext).sum() / m.sum()), 1), 'anno_esterno%': round(100 * float((m & ext).sum() / m.sum()), 1), 'anno_stimato%': round(100 * float((m & est).sum() / m.sum()), 1)}
    m = d <= 1200; real = np.isin(hs, ['lidar', 'wiki']); t = h >= 100
    out['centro<=1200m'] = {'mediana_anno': float(np.median(y[m])), 'mediana_anno_solo_veri': float(np.median(y[m & ~est])), 'mediana_altezza_m': round(float(np.median(h[m])), 1), 'altezza_media_m': round(float(h[m].mean()), 1),
                            'torri>=100m': int((t & (d <= 3000)).sum()), 'torri>=100m_altezza_reale': int((t & real & (d <= 3000)).sum()), 'torri>=100m_tutte_9km': int(t.sum())}
    print(D, json.dumps(out))
