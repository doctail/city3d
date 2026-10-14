# Strato storico di Madrid: anno di urbanizzazione per distanza dalla Puerta del Sol (dalle piante storiche:
# nucleo medievale attorno all'Alcazar; capitale 1561; Cerca di Filippo IV 1625; Ensanche di Castro 1860;
# espansione del dopoguerra; periferie e PAU). Approssimato. Riusa build() di hist_nyc.
import math, sys
from hist_nyc import build, era_height
LAT0, LON0 = 40.4169, -3.7035
KX = math.cos(math.radians(LAT0)) * 111320; KY = 110540
ALCAZAR = (40.4179, -3.7143)
CURVE = [(0.0, 1450), (0.5, 1540), (1.0, 1580), (1.5, 1640), (1.8, 1860), (2.6, 1890), (3.3, 1920), (4.2, 1945),
         (5.0, 1958), (7.0, 1970), (10.0, 1985), (14.0, 2003)]
def interp(v, pts):
    if v <= pts[0][0]: return pts[0][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if v <= b: return ya + (yb - ya) * (v - a) / (b - a)
    return pts[-1][1]
def urban_year(x, y):
    la, lo = LAT0 + y / KY, LON0 + x / KX
    d_sol = math.hypot(x, y) / 1000.0
    d_alc = math.hypot((la - ALCAZAR[0]) * 111.0, (lo - ALCAZAR[1]) * 84.8)
    # il nucleo medievale e' attorno all'Alcazar; la citta' poi cresce soprattutto verso est (il Manzanares chiude a ovest)
    d = d_alc * (0.72 if x > -900 else 1.0)
    wob = 9 * math.sin(x / 170.0) + 7 * math.sin(y / 230.0 + x / 410.0)
    return interp(d, CURVE) + wob
if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'data', urban_year)
