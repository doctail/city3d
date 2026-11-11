"""Utility comuni del kit: caricamento story, conversione [lat, lon] -> metri locali e ritorno."""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def story_path(slug):
    return os.path.join(ROOT, 'cities', slug, 'story.json')


def load_story(slug_or_path):
    p = slug_or_path if slug_or_path.endswith('.json') else story_path(slug_or_path)
    with open(p) as f:
        s = json.load(f)
    s['_path'] = os.path.abspath(p)
    s['_dir'] = os.path.dirname(s['_path'])
    return s


class Proj:
    """Proiezione locale equirettangolare, identica a build_render.py (KX = cos(lat0)*111320, KY = 110540)."""

    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        self.KX = math.cos(math.radians(lat0)) * 111320
        self.KY = 110540

    @classmethod
    def of(cls, story):
        return cls(story['city']['lat0'], story['city']['lon0'])

    def L(self, lat, lon):
        return ((lon - self.lon0) * self.KX, (lat - self.lat0) * self.KY)

    def inv(self, x, y):
        return (self.lat0 + y / self.KY, self.lon0 + x / self.KX)

    def ring(self, latlons):
        return [list(self.L(a, b)) for a, b in latlons]


def data_dir(story):
    """Cartella DATA della città: city.data_dir (relativa alla radice del repo) o data_<slug>."""
    d = story['city'].get('data_dir') or f"data_{story['city']['slug']}"
    return d if os.path.isabs(d) else os.path.join(ROOT, d)
