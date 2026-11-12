"""Test di kit/hist_kit.py su una mini citta' sintetica (metri locali convertiti in [lat, lon]).
Uso:  /home/user/bl/bin/python -m unittest kit.tests.test_hist_kit -v   (dalla radice del repo)"""
import json, os, subprocess, sys, tempfile, unittest

from shapely.geometry import Point, Polygon

from kit import hist_kit as HK
from kit.geo import ROOT, Proj

P = Proj(40.0, 0.0)


def LL(pts):
    return [list(P.inv(x, y)) for x, y in pts]


def sq(cx, cy, h):
    return [[cx - h, cy - h], [cx + h, cy - h], [cx + h, cy + h], [cx - h, cy + h]]


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def make_city(tmp):
    D = os.path.join(tmp, 'data'); os.makedirs(D)
    story = {
        'version': 1,
        'city': {'slug': 'testville', 'name': 'Testville', 'lat0': 40.0, 'lon0': 0.0, 'start_year': 1200, 'end_year': 2026,
                 'data_dir': D},
        'sources': {'S1': {'url': 'x'}},
        'history': {
            'zones': [{'name': 'old', 'ring': LL(rect(-200, -200, 200, 200)), 'born': [1100, 1100], 'seed': None,
                       'era_height': [6, 8], 'src': ['S1'], 'conf': 'high'},
                      {'name': 'new', 'ring': LL(rect(0, -200, 400, 200)), 'born': [1300, 1350], 'seed': list(P.inv(0, 0)),
                       'era_height': [[1300, 9, 10], [1600, 12, 13]], 'src': ['S1'], 'conf': 'high'}],
            'walls': [{'name': 'Wall', 'ring': LL(rect(-250, -250, 250, 250)), 'built': [1150, 1160], 'demolished': 1870,
                       'height': 10, 'width': 4, 'towers_every_m': 50, 'keep': [list(P.inv(250, 0)) + [40]], 'src': ['S1']}],
            'gutting': [{'name': 'Plaza', 'ring': LL(rect(-180, -40, -60, 40)), 'from': 1100, 'until': 1900, 'src': ['S1']}],
            'lost': [{'name': 'Convent', 'ring': LL(rect(300, 100, 330, 130)), 'from': 1250, 'to': 1800, 'h': 14, 'src': ['S1']}],
            'fires': [{'name': 'Fire', 'ring': LL(rect(80, -60, 140, 60)), 'y': 1700, 'y1': 1700.05, 'destroy': True,
                       'origin': list(P.inv(80, 0)), 'src': ['S1']}],
            'water': [{'name': 'Marsh', 'ring': LL(rect(500, 0, 700, 200)), 'from': -9999, 'to': 1600, 'c': 'field'},
                      {'name': 'Low centre', 'ring': LL(rect(240, -230, 480, 10)), 'from': -9999, 'to': 99999, 'c': 'urban'}],
            'bridges': [{'name': 'Old Bridge', 'line': LL([[600, -300], [600, -200]]), 'w': 10, 'y': 1500, 'd': None},
                        {'name': 'Unnamed match', 'line': LL([[800, -300], [800, -200]]), 'w': 10, 'y': 1600},
                        {'name': 'New Bridge', 'line': LL([[900, -300], [900, -200]]), 'w': 10, 'y': 1700}]}}
    blds = [{'r': sq(100, 0, 5), 'h': 20, 'y': 1950},      # zona old+new e fuoco
            {'r': sq(120, 40, 5), 'h': 15, 'y': 1650},     # attuale vecchio dentro il fuoco
            {'r': sq(300, 0, 5), 'h': 20, 'y': 1950},      # solo zona new (rampa)
            {'r': sq(-150, -150, 5), 'h': 8, 'y': 1120},   # tra i primi del lotto: niente predecessore
            {'r': sq(-100, 120, 20), 'h': 25, 'y': 1960},  # grande: lottizzato
            {'r': sq(1000, 1000, 5), 'h': 10, 'y': 1900}]  # fuori: campagna fino al 1900
    blds += [{'r': sq(1000 + 12 * i, 1000, 4), 'h': 10, 'y': 1900 + i} for i in range(1, 5)]
    json.dump(blds, open(os.path.join(D, 'buildings.json'), 'w'))
    json.dump([{'r': rect(-150, -5, -90, 5), 'y': 1500, 'rail': 0}, {'r': rect(1000, -5, 1100, 5), 'y': 1500, 'rail': 0},
               {'r': rect(270, -15, 330, -9), 'y': 1960, 'rail': 0},       # vicolo (6 m) nella zona new: compare con la zona
               {'r': rect(250, 20, 350, 44), 'y': 1960, 'rail': 0}],       # viale (24 m): resta al 1960
              open(os.path.join(D, 'roads.json'), 'w'))
    json.dump([{'r': rect(595, -300, 605, -200), 'y': 2026, 'name': 'Old Bridge'},
               {'r': rect(796, -300, 806, -200), 'y': 2026, 'name': ''},
               {'r': rect(2000, 0, 2010, 50), 'y': 1990, 'name': 'Other'}], open(os.path.join(D, 'bridges.json'), 'w'))
    sp = os.path.join(tmp, 'story.json'); json.dump(story, open(sp, 'w'))
    return sp, D


def ld(D, n):
    with open(os.path.join(D, n + '.json')) as f: return json.load(f)


def at(items, x, y):
    return [h for h in items if Polygon(h['r']).buffer(0).contains(Point(x, y))]


class HistKit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); cls.sp, cls.D = make_city(cls.tmp.name)
        cls.st = HK.build(cls.sp, cls.D, quiet=True)
        cls.hist = ld(cls.D, 'hist'); cls.blds = ld(cls.D, 'buildings')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_zone_oldest_wins_and_dies_at_current(self):
        z = [h for h in at(self.hist, 300, 0) if h['kit'] == 'zone']
        self.assertEqual(len(z), 1); self.assertTrue(1300 <= z[0]['y'] <= 1350 + 3); self.assertTrue(1948 < z[0]['d'] < 1950)
        self.assertTrue(9 <= z[0]['h'] <= 10)
        o = [h for h in at(self.hist, 100, 0) if h['kit'] == 'zone']       # old+new sovrapposte: vale old (1100)
        self.assertEqual(o[0]['zone'], 'old'); self.assertLessEqual(o[0]['y'], 1100)

    def test_no_predecessor_for_early_or_outside(self):
        self.assertEqual(at(self.hist, -150, -150), [])
        self.assertEqual(at(self.hist, 1000, 1000), [])

    def test_large_footprint_split(self):
        self.assertGreater(len([h for h in self.hist if h['kit'] == 'zone' and -120 <= Polygon(h['r']).centroid.x <= -80
                                and 100 <= Polygon(h['r']).centroid.y <= 140]), 3)

    def test_gutting_fills_void_and_moves_roads(self):
        g = [h for h in self.hist if h['kit'] == 'gut']
        self.assertGreater(len(g), 20); self.assertEqual(self.st['gutting_filled']['Plaza'], len(g))
        G = Polygon(rect(-180, -40, -60, 40))
        for h in g:
            q = Polygon(h['r']); self.assertTrue(G.buffer(0.1).contains(q)); self.assertLess(h['d'], 1900)
            self.assertLessEqual(h['y'], 1200)          # citta' gia' piena all'inizio
        roads = ld(self.D, 'roads'); self.assertEqual([r['y'] for r in roads][:2], [1900, 1500])
        self.assertTrue(os.path.exists(os.path.join(self.D, 'roads_orig.json')))

    def test_lanes_follow_zone_avenues_stay(self):
        roads = ld(self.D, 'roads')
        self.assertTrue(1300 <= roads[2]['y'] < 1400); self.assertEqual(roads[3]['y'], 1960)

    def test_urban_slab_waits_for_houses(self):
        ph = [p for p in ld(self.D, 'landphases') if p['name'] == 'Low centre']
        urb = [p for p in ph if p['c'] == 'urban']; fld = [p for p in ph if p['c'] == 'field']
        self.assertTrue(urb and fld)
        self.assertTrue(all(p['from'] >= 1300 for p in urb))           # niente suolo urbano prima della zona new
        cell = [p for p in ph if Polygon(p['r']).contains(Point(300, 0))]
        self.assertEqual(sorted(p['c'] for p in cell), ['field', 'urban'])
        empty = [p for p in ph if Polygon(p['r']).contains(Point(420, -200))]   # nessuna casa vicina: sempre campo
        self.assertEqual([(p['c'], p['to']) for p in empty], [('field', 99999)])

    def test_lost(self):
        l = [h for h in self.hist if h['kit'] == 'lost']
        self.assertEqual(len(l), 1); self.assertEqual((l[0]['y'], l[0]['d'], l[0]['h']), (1250, 1800, 14))

    def test_fire_destroys_and_rebuilds(self):
        ps = sorted(at(self.hist, 100, 0), key=lambda h: h['y'])
        burnt = [h for h in ps if 1700 <= h['d'] <= 1700.05]
        self.assertEqual(len(burnt), 1)
        reb = [h for h in ps if h['y'] >= 1703.05]
        self.assertEqual(len(reb), 1); self.assertTrue(1948 < reb[0]['d'] < 1950)
        cur = [b for b in at(self.blds, 120, 40)][0]                 # edificio attuale del 1650: rinato dopo il fuoco
        self.assertEqual(cur['y_kit0'], 1650); self.assertGreaterEqual(cur['y'], 1703.05)
        copy = [h for h in at(self.hist, 120, 40) if h['y'] == 1650]
        self.assertEqual(len(copy), 1); self.assertTrue(1700 <= copy[0]['d'] <= 1700.05)
        f = ld(self.D, 'fires')[0]; self.assertEqual(f['houses'], self.st['fires_destroyed']['Fire']); self.assertIn('origin', f)

    def test_walls_parts(self):
        w = ld(self.D, 'landmarks_walls')
        self.assertTrue(all(p['t'] == 'prism' and 1150 <= p['y'] <= 1160 for p in w))
        towers = [p for p in w if p.get('tower')]; self.assertGreater(len(towers), 30)
        kept = [p for p in w if 'd' not in p]; self.assertTrue(kept)
        self.assertTrue(all(abs(p['cx'] - 250) < 50 for p in kept))
        self.assertTrue(all(1870 <= p['d'] <= 1872 for p in w if 'd' in p))

    def test_water_and_bridges(self):
        ph = ld(self.D, 'landphases'); self.assertEqual((ph[0]['from'], ph[0]['to'], ph[0]['c']), (-9999, 1600, 'field'))
        br = ld(self.D, 'bridges'); self.assertEqual(len(br), 4)
        self.assertEqual(br[0]['y'], 1500); self.assertEqual(br[1]['y'], 1600); self.assertEqual(br[2]['y'], 1990)
        self.assertEqual(br[3]['name'], 'New Bridge')

    def test_idempotent(self):
        before = {n: open(os.path.join(self.D, n + '.json')).read() for n in ('hist', 'buildings', 'roads', 'bridges', 'landmarks_walls')}
        HK.build(self.sp, self.D, quiet=True)
        for n, s in before.items(): self.assertEqual(s, open(os.path.join(self.D, n + '.json')).read(), n)

    def test_alive_stats(self):
        self.assertGreater(self.st['alive']['1200'], 30)

    def test_urban_year_and_wall(self):
        os.environ['CITY3D_STORY'] = self.sp; os.environ['CITY3D_DATA'] = self.D; HK.reset()
        try:
            self.assertEqual(HK.urban_year(-100, 0), 1100)
            self.assertGreaterEqual(HK.urban_year(390, 0), 1300 + 50 * 390 / ((400 ** 2 + 200 ** 2) ** 0.5) - 1e-6)
            self.assertEqual(HK.urban_year(350, -150), 9999)               # nella zona ma senza case vicine
            self.assertEqual(HK.urban_year(1010, 1000), 1900)
            self.assertEqual(HK.urban_year(5000, 5000), 9999)
            self.assertTrue(HK.WALL_P.contains(Point(0, 0)))
        finally:
            del os.environ['CITY3D_STORY'], os.environ['CITY3D_DATA']; HK.reset()

    def test_stub_import(self):
        p = HK.make_stub('testville', root=self.tmp.name)
        env = dict(os.environ, CITY3D_STORY=self.sp, CITY3D_DATA=self.D, PYTHONPATH=os.pathsep.join([self.tmp.name, ROOT]))
        out = subprocess.run([sys.executable, '-c', "m=__import__('hist_testville');print(m.urban_year(0,0), round(m.WALL_P.area))"],
                             env=env, cwd=self.tmp.name, capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr); self.assertEqual(out.stdout.split(), ['1100.0', '250000'])
        self.assertIn("os.environ.setdefault('CITY3D_STORY', 'cities/testville/story.json')", open(p).read())


if __name__ == '__main__':
    unittest.main()
