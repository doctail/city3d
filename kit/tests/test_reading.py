"""Test di regia.reading (tempo di lettura dei cartelli calcolato dal testo). Uso: python kit/tests/test_reading.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from kit.regia_kit import card_hold   # noqa: E402

def test_default_unchanged():
    assert card_hold({'title': 'a b c', 'lines': ['x y z']}) == 5.0
    assert card_hold({'hold_s': 7, 'title': 'a'}) == 7.0
    assert card_hold({'title': 'a'}, {}) == 5.0

def test_formula():
    R = {'wps': 10.0, 'base': 3.0, 'min': 4.0, 'max': 8.0}
    c = {'title': 'one two', 'lines': ['three four five six eight nine ten']}   # 9 parole
    assert abs(card_hold(c, R) - 3.9 - 0.1) < 1e-9 or card_hold(c, R) == 4.0       # 3 + 0,9 = 3,9 -> min 4
    assert card_hold({'title': ' '.join(['w'] * 30)}, R) == 6.0
    assert card_hold({'title': ' '.join(['w'] * 100)}, R) == 8.0                   # max
    assert card_hold({'hold_s': 5.5, 'title': 'w ' * 100}, R) == 5.5                # esplicito vince

if __name__ == '__main__':
    test_default_unchanged(); test_formula(); print('OK test_reading')
