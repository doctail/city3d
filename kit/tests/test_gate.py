"""Test di kit/gate.py (GO dossier) su uno schedule sintetico: nessun bpy, nessun DATA.
Uso (dalla radice del repo):  python -m pytest kit/tests/test_gate.py -q     oppure   python -m unittest kit.tests.test_gate -v"""
import json, os, re, tempfile, unittest
from unittest import mock

import numpy as np

from kit import gate, qa
from kit.geo import ROOT


def synth(dur=100.0, lens=35.0):
    """Schedule drone sintetico a 1 chiave/s: camera a 1000 m di quota che guarda 1000 m piu' in la' a terra (distanza 1414 m, pitch 45 gradi)."""
    cam = [[float(t), [t * 10.0, 0.0, 1000.0], [t * 10.0 + 1000.0, 0.0, 0.0], lens] for t in range(int(dur) + 1)]
    # anni: 0-10 s fermi a 1000 (apertura), poi 20 anni/s; volo 40-60 s quasi fermo (0,1 anni/s)
    yrs = [[0.0, 1000.0], [10.0, 1000.0], [40.0, 1400.0], [60.0, 1402.0], [dur, 2026.0]]
    stays = [[10.0, 20.0, 0.0, 0.0, 'A'], [30.0, 40.0, 0.0, 0.0, 'B'], [60.0, 70.0, 0.0, 0.0, 'C'], [90.0, dur, 0.0, 0.0, 'finale']]
    return {'duration': dur, 'lens': lens, 'cam': cam, 'years': yrs, 'camera': 'drone', 'drone': {'stays': stays}, 'night_t': 90.0,
            'soste': [[s[0], s[1], 1000.0, 1001.0, s[4]] for s in stays]}


STORY = {'city': {'slug': 'x', 'name': 'Xville', 'start_year': 1000, 'end_year': 2026},
         'landmarks': [{'name': 'Tower'}, {'name': 'Chapel'}, {'name': 'Mill'}, {'name': 'Gate'}],
         'regia': {'soste': [{'caption': 'A', 'target': 'Tower'}, {'caption': 'B', 'target': 'Chapel'}, {'caption': 'C', 'target': 'Mill'}]},
         'montaggio': {'chapters': [{'y': 1000, 'title': 'First'}, {'y': 1200, 'title': 'Second'}, {'y': 1800, 'title': 'Third'}], 'cards': []}}


class TestMetrics(unittest.TestCase):
    def test_distance_and_pitch(self):
        M = gate.camera_metrics(synth())
        self.assertAlmostEqual(float(np.median(M['dist'])), 1414.2, delta=1)       # 35 mm: nessuna conversione
        self.assertAlmostEqual(float(np.median(M['pitch'])), 45.0, delta=0.01)
        M2 = gate.camera_metrics(synth(lens=70.0))
        self.assertAlmostEqual(float(np.median(M2['dist'])), 707.1, delta=1)      # equivalente a 35 mm scala con la lente

    def test_r2_numbers(self):
        n = gate.r2_numbers(gate.camera_metrics(synth()))
        self.assertAlmostEqual(n['pitch_p95'], 45.0, delta=0.01)
        self.assertEqual(n['frac_pitch_ok'], 0.0)                                  # 45 non e' < 45

    def test_reference_cities_match_the_post_mortem(self):
        """I riferimenti scritti in AVVIO_NUOVA_CITTA (R2): Copenaghen 1397 m / mediana 23-27 gradi, Lione 930 m / 66 gradi."""
        for slug, dist, pitch in (('copenhagen', 1397, 26), ('lyon', 930, 66)):
            p = os.path.join(ROOT, f'schedule_{slug}.json')
            if not os.path.exists(p): self.skipTest(p)
            M = gate.camera_metrics(json.load(open(p)))
            self.assertAlmostEqual(float(np.median(M['dist'])), dist, delta=3)
            self.assertAlmostEqual(float(np.median(M['pitch'])), pitch, delta=1)


class TestFlights(unittest.TestCase):
    def setUp(self):
        self.sc = synth(); self.M = gate.camera_metrics(self.sc); self.rows = gate.flight_table(self.sc, self.M)

    def test_rows(self):
        self.assertEqual([(f['start'], f['end']) for f in self.rows], [(0.0, 10.0), (20.0, 30.0), (40.0, 60.0), (70.0, 90.0)])
        self.assertEqual(self.rows[0]['note'], 'opening')
        self.assertEqual(self.rows[3]['to'], 'finale')

    def test_flag_only_slow_long_non_exempt(self):
        flags = [f['n'] for f in self.rows if f['flag']]
        self.assertEqual(flags, [3])                                              # 40-60 s: 20 s a 0,1 anni/s
        self.assertAlmostEqual(self.rows[2]['rate'], 0.1, places=2)

    def test_opening_with_frozen_years_is_exempt(self):
        self.assertFalse(self.rows[0]['flag'])                                     # 0-10 s: anni fermi ma e' l'apertura

    def test_row_numbers(self):
        f = self.rows[1]
        self.assertAlmostEqual(f['dist_med'], 1414.2, delta=1); self.assertAlmostEqual(f['pitch_max'], 45.0, delta=0.01); self.assertEqual(f['alt_max'], 1000.0)


class TestShots(unittest.TestCase):
    def test_at_least_8_shots_with_required_groups(self):
        sc = synth(); M = gate.camera_metrics(sc)
        shots = gate.select_shots(STORY, sc, M, D=None)
        g = [s['group'] for s in shots]
        self.assertGreaterEqual(len(shots), gate.MIN_FRAMES)
        self.assertEqual(g.count('flight'), 3)
        self.assertEqual(g.count('hover'), 2)                                      # prima e dopo del primo monumento
        self.assertEqual(g.count('intro'), 12)                                     # primi 12 s, uno al secondo
        self.assertEqual(g.count('chapter'), 3)
        self.assertGreaterEqual(g.count('small'), 2)
        h = [s for s in shots if s['group'] == 'hover']
        self.assertLess(h[0]['t'], h[1]['t']); self.assertTrue(10.0 <= h[0]['t'] <= h[1]['t'] <= 20.0)
        self.assertEqual([s['t'] for s in shots if s['group'] == 'intro'], [float(k) for k in range(12)])

    def test_chapter_times_follow_year_curve(self):
        ct = gate.chapter_times(STORY, synth())
        self.assertEqual([c[1] for c in ct], ['First', 'Second', 'Third'])
        self.assertTrue(all(a[0] < b[0] for a, b in zip(ct, ct[1:])))

    def test_shot_fields_for_render(self):
        for s in gate.select_shots(STORY, synth(), gate.camera_metrics(synth())):
            for k in ('label', 'year', 'pos', 'tgt', 'lens'): self.assertIn(k, s)
            self.assertEqual(len(s['pos']), 3)


class TestPackagingAndCost(unittest.TestCase):
    def test_title_formula_matches_lyon_metadata(self):
        t, ylab = gate.title_for('Lyon', -43)
        self.assertEqual(ylab, '43 BC')
        lt, _ = gate.lyon_reference()
        if lt is None: self.skipTest('cities/lyon/METADATA.md')
        self.assertEqual(t, lt)
        self.assertEqual(gate.title_for('Marseille', -600)[0], 'EVOLUTION OF MARSEILLE | 3D City Timelapse (600 BC–NOW) | No AI')
        self.assertEqual(gate.title_for('Valencia', 138)[1], '138')
        self.assertNotIn('cold', t.lower())

    def test_cost_measured_basis_for_lyon_like_city(self):
        lines, same = gate.cost_block('lyon', {'duration': 565.0, 'night_t': 550.0}, 145000)
        txt = '\n'.join(lines)
        self.assertTrue(same); self.assertNotIn('non misurato', txt)
        self.assertIn('29 pod-s per video-s', txt); self.assertIn('30 min', txt)
        self.assertRegex(txt, r'= \*\*5 h 3\d min of pod')                          # 29 x 565 s + 2 x 30 min = 5 h 33 min circa

    def test_cost_not_measured_when_city_differs_or_unknown(self):
        for nb in (60000, 400000, None):
            lines, same = gate.cost_block('x', {'duration': 600.0, 'night_t': 1.0}, nb)
            txt = '\n'.join(lines)
            self.assertFalse(same); self.assertIn('non misurato', txt); self.assertIn('Range [Guessing]', txt)
        self.assertIn('go straight to `full`', '\n'.join(gate.cost_block('x', {'duration': 600.0}, 400000)[0]))

    def test_banner_format_like_run_sh(self):
        txt, br, st = gate.banner('lyon', {'duration': 565.0, 'lens': 30.0}, None)
        self.assertRegex(txt, r'^VERSIONE: [0-9a-f]{7,} .* \| schedule_lyon: 565 s, lens 30\.0$')


class TestContactAndRun(unittest.TestCase):
    def test_contact_sheet(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            fr = []
            for i in range(9):
                p = os.path.join(d, f'{i}.jpg'); Image.new('RGB', (480, 270), (i * 20, 50, 90)).save(p)
                fr.append(({'group': 'intro', 'label': f'intro {i}', 't': float(i), 'year': 1000.0}, p))
            out = gate.contact_sheet(fr, os.path.join(d, 'cs.jpg'))
            self.assertEqual(Image.open(out).size, (4 * 480, 3 * (270 + 22)))

    def test_plots_written(self):
        sc = synth(); M = gate.camera_metrics(sc)
        with tempfile.TemporaryDirectory() as d:
            p = gate.plots(M, gate.flight_table(sc, M), gate.r2_numbers(M), os.path.join(d, 'p.png'), 'Xville', gate.stays_of(sc))
            self.assertGreater(os.path.getsize(p), 10000)

    def test_missing_schedule_fails(self):
        with tempfile.TemporaryDirectory() as d:
            rc, R = gate.run('lyon', out=d, sched=os.path.join(d, 'nope.json'))
        self.assertEqual(rc, 1); self.assertEqual(R.worst(), 'FAIL')

    def test_exit_nonzero_when_frames_not_produced(self):
        """Senza fotogrammi (bpy assente / render fallito) il gate FALLISCE e lo dice."""
        p = os.path.join(ROOT, 'schedule_lyon.json')
        if not os.path.exists(p): self.skipTest(p)
        with tempfile.TemporaryDirectory() as d, mock.patch.object(qa, 'render_frames', return_value=[]):
            rc, R = gate.run('lyon', out=d, data=os.path.join(d, 'nodata'))
            self.assertEqual(rc, 1)
            self.assertTrue(any(r[1] == 'FAIL' and 'frames not produced' in r[2] for r in R.rows))
            self.assertTrue(os.path.exists(os.path.join(d, 'DOSSIER.md')))        # il dossier si scrive comunque, con "NOT PRODUCED"
            self.assertIn('NOT PRODUCED', open(os.path.join(d, 'DOSSIER.md')).read())

    def test_nothing_written_inside_the_city_folder_with_out(self):
        p = os.path.join(ROOT, 'cities', 'lyon')
        if not os.path.isdir(p): self.skipTest(p)
        before = sorted(os.listdir(p)); qb = sorted(os.listdir(os.path.join(p, 'qa'))) if os.path.isdir(os.path.join(p, 'qa')) else []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(qa, 'render_frames', return_value=[]):
            gate.run('lyon', out=d, data=os.path.join(d, 'nodata'))
        self.assertEqual(before, sorted(os.listdir(p)))
        self.assertEqual(qb, sorted(os.listdir(os.path.join(p, 'qa'))) if os.path.isdir(os.path.join(p, 'qa')) else [])


if __name__ == '__main__':
    unittest.main()
