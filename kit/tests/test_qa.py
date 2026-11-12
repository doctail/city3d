"""Test di kit/qa.py, kit/city_json.py e tools/costo_cambi.py (bin dal city json) su una mini citta' sintetica.
Uso:  /home/user/bl/bin/python -m unittest kit.tests.test_qa -v   (dalla radice del repo)"""
import json, os, subprocess, sys, tempfile, unittest

from kit import qa, city_json
from kit.geo import ROOT, Proj

P = Proj(40.0, 0.0)
LL = lambda pts: [list(P.inv(x, y)) for x, y in pts]
rect = lambda x0, y0, x1, y1: [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
AVE = (268, 298)   # viale moderno largo 30 m, aperto nel 1910 (case a passo 24 m: nessuna striscia vuota ai bordi)


def houses(x0, x1, y0, y1, s=20, gap=4):
    out, x = [], x0
    while x + s <= x1:
        y = y0
        while y + s <= y1:
            out.append(rect(x, y, x + s, y + s)); y += s + gap
        x += s + gap
    return out


def make(tmp, fill_avenue=False, predecessors=True, gut_road=False, soste=None, landmark_src=True):
    D = os.path.join(tmp, 'data'); os.makedirs(D, exist_ok=True)
    zone = rect(0, 0, 590, 580)
    story = {'version': 1,
             'city': {'slug': 'qaville', 'name': 'Qaville', 'country': 'X', 'lat0': 40.0, 'lon0': 0.0, 'radius_m': 3000,
                      'start_year': 1200, 'end_year': 2026, 'data_source': 'custom', 'data_dir': D, 'style_preset': 'central'},
             'sources': {'S1': {'url': 'https://example.org/s1', 'title': 'Fonte'}},
             'history': {'zones': [{'name': 'Old town', 'ring': LL(zone), 'born': [1200, 1200], 'src': ['S1'], 'conf': 'high'}],
                         'gutting': [{'name': 'Square', 'ring': LL(rect(100, 100, 168, 168)), 'from': 1200, 'until': 1960, 'src': ['S1']}]},
             'landmarks': [{'name': 'Church', 'kind': 'church', 'at': LL([[50, 50]])[0], 'phases': [{'y': 1300}],
                            **({'src': ['S1']} if landmark_src else {})}],
             'regia': {'duration': 60.0, 'soste': []}}
    os.makedirs(os.path.join(tmp, 'city'), exist_ok=True)
    sp = os.path.join(tmp, 'city', 'story.json'); json.dump(story, open(sp, 'w'))
    blds = [{'r': r, 'h': 12, 'y': 1950} for r in houses(4, AVE[0], 4, 580) + houses(AVE[1] + 4, 590, 4, 580)
            if not (96 < r[0][0] < 164 and 96 < r[0][1] < 164)]
    hist = [dict(b, y=1200, d=1950) for b in blds] if predecessors else []
    hist += [{'r': r, 'h': 9, 'y': 1200, 'd': 1960} for r in houses(100, 168, 100, 168) if not (gut_road and r[0][0] == 124)]   # gutting riempito
    if fill_avenue: hist += [{'r': r, 'h': 9, 'y': 1200, 'd': 1910} for r in houses(AVE[0], AVE[1], 4, 580, s=13, gap=3)]
    roads = [{'r': rect(AVE[0], 0, AVE[1], 580), 'y': 1910, 'rail': 0}]
    if gut_road: roads.append({'r': rect(124, 100, 144, 168), 'y': 1200, 'rail': 0})   # nastro della piazza visibile dal 1200
    json.dump(blds, open(os.path.join(D, 'buildings.json'), 'w')); json.dump(hist, open(os.path.join(D, 'hist.json'), 'w'))
    json.dump(roads, open(os.path.join(D, 'roads.json'), 'w')); json.dump([rect(-3000, -3000, 3000, 3000)], open(os.path.join(D, 'land.json'), 'w'))
    json.dump({'parts': [], 'clear': [], 'labels': []}, open(os.path.join(D, 'landmarks.json'), 'w'))
    sc = {'duration': 60.0, 'lens': 35, 'years': [[0, 2026], [3, 2026], [8, 1200], [20, 1500], [25, 1510], [60, 2026]],
          'cam': [[0, [0, -900, 700], [300, 300, 0], 35], [60, [0, -900, 700], [300, 300, 0], 35]],
          'soste': soste if soste is not None else [[20.0, 25.0, 1500.0, 1510.0, 'Great fire (1500)']]}
    sch = os.path.join(tmp, 'schedule_qaville.json'); json.dump(sc, open(sch, 'w'))
    return sp, D, sch


def fails(R, sec, word=''):
    return [r for r in R.rows if r[0] == sec and r[1] == 'FAIL' and word in r[2]]


class TestQA(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.tmp = self.t.name

    def tearDown(self):
        self.t.cleanup()

    def test_sources(self):
        sp, D, _ = make(self.tmp, landmark_src=False)
        R = qa.run(sp, only='a'); self.assertTrue(fails(R, 'a', 'date con fonte'))
        sp, D, _ = make(self.tmp, landmark_src=True)
        R = qa.run(sp, only='a'); self.assertEqual(R.worst('a'), 'PASS')

    def test_density(self):
        sp, D, _ = make(self.tmp, predecessors=False)
        R = qa.run(sp, only='c'); self.assertTrue(fails(R, 'c', '1200'))
        sp, D, _ = make(self.tmp, predecessors=True, fill_avenue=True)
        R = qa.run(sp, only='c'); self.assertEqual(R.worst('c'), 'PASS')

    def test_corridor_modern_street(self):
        sp, D, _ = make(self.tmp, fill_avenue=False)
        R = qa.run(sp, only='d'); self.assertTrue(fails(R, 'd', 'strada moderna'))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, 'city', 'qa', 'corridoi_1200.png')))
        sp, D, _ = make(self.tmp, fill_avenue=True)
        R = qa.run(sp, only='d'); self.assertFalse(fails(R, 'd'), R.rows)

    def test_road_before_gutting(self):
        sp, D, _ = make(self.tmp, fill_avenue=True, gut_road=True)
        R = qa.run(sp, only='d'); self.assertTrue(fails(R, 'd', 'prima dell\'apertura'))

    def test_data_roads_required(self):
        sp, D, _ = make(self.tmp)
        os.remove(os.path.join(D, 'roads.json'))
        R = qa.run(sp, only='b'); self.assertTrue(fails(R, 'b', 'roads.json'))

    def test_schedule_and_cost(self):
        sp, D, sch = make(self.tmp, fill_avenue=True)
        cj = os.path.join(self.tmp, 'city_qaville.json')
        from kit import geo
        json.dump(city_json.build_city(geo.load_story(sp)), open(cj, 'w'))
        R = qa.run(sp, only='e', city_json=cj, sched=sch)
        self.assertEqual(R.worst('e'), 'PASS', R.rows)
        sp, D, sch = make(self.tmp, soste=[[52.0, 57.0, 1900, 1905, 'No date here'], [46.0, 51.0, 1800, 1801, 'Late (1800)']])
        R = qa.run(sp, only='e', city_json=cj, sched=sch)
        self.assertTrue(fails(R, 'e', 'didascalie')); self.assertTrue(fails(R, 'e', 'ordinate'))
        self.assertTrue([r for r in R.rows if r[2] == 'evento forte entro 45 s' and r[1] == 'WARN'])


class TestCityJson(unittest.TestCase):
    def test_complete_and_valid(self):
        with tempfile.TemporaryDirectory() as t:
            sp, D, _ = make(t)
            from kit import geo
            c = city_json.build_city(geo.load_story(sp))
            self.assertEqual(city_json.validate(c), [])
            for k in city_json.NYC_DEFAULT_KEYS: self.assertIn(k, c)
            self.assertEqual(c['hist'], 'hist_qaville'); self.assertNotIn('night_off', c['style']); self.assertIn('night_bld_off', c['style'])
            del c['core_box']; c['style'].pop('wall_old')
            e = city_json.validate(c); self.assertTrue(any('core_box' in x for x in e)); self.assertTrue(any('wall_old' in x for x in e))

    def test_presets(self):
        from kit import presets
        for n in presets.PRESETS:
            top, st = presets.preset(n)
            for k in presets.STYLE_REQUIRED: self.assertIn(k, st, (n, k))


class TestCostoBin(unittest.TestCase):
    def test_bin_from_city_json(self):
        with tempfile.TemporaryDirectory() as t:
            D = os.path.join(t, 'd'); os.makedirs(D)
            json.dump([{'r': rect(i, 0, i + 5, 5), 'h': 5, 'y': 1000 + i} for i in range(0, 400, 1)], open(os.path.join(D, 'buildings.json'), 'w'))
            s = os.path.join(t, 's.json'); json.dump({'duration': 2.0, 'years': [[0, 1000], [2, 1400]]}, open(s, 'w'))
            n = {}
            for b in (4, 10):
                c = os.path.join(t, f'c{b}.json'); json.dump({'bin': b}, open(c, 'w'))
                o = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'costo_cambi.py'), c, D, s], capture_output=True, text=True).stdout
                n[b] = int(o.split("oggetti citta' ")[1].split(',')[0])
            self.assertEqual(n[4], 100); self.assertEqual(n[10], 40)


if __name__ == '__main__':
    unittest.main()
