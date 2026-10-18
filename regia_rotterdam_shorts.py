# Regia degli Shorts "su un evento" di Rotterdam (proposta del 18 ott 2026, OK di Fabio). Camere PROPRIE, non quelle del lungo.
# Scrive schedule_rotterdam_shortB.json e schedule_rotterdam_shortC.json (24 fps, verticale 1080x1920).
#  B "Where did Rotterdam's center go?": 14 maggio 1940. Camera bassa e vicina sul centro, lenta rotazione.
#    0-6 s centro intatto (1936-1939, la scritta-domanda sta nel primo secondo) | 6-9,5 s scompare | 9,5-13 s vuoto |
#    13-24 s rinasce 1945-1962 | 24-26 s fermo (rimando al video lungo).
#  C "How did Rotterdam get a skyline?": Kop van Zuid / Wilhelminapier 1990-2026, camera bassa sul fiume che si avvicina.
#    Torri nei dati BAG: 1997, 2000 (Wilhelminapier, 122 m), 2005 (140 m), 2010 (158 m), 2011 Maastoren (165 m),
#    2013 De Rotterdam (152 m), 2017, 2022 Zalmhaven (203 m), 2023. Il ponte Erasmus NON e' nel modello (niente ponti).
# Origine (0, 0) = Stadhuis; Laurenskerk ~(536, 22); zona bombardata ~(-650..1440, -950..820).
import json, math

def orbit(t, T, cx, cy, r, h, a0, a1, tz=0.0, ease=True):
    u = t / T; u = u * u * (3 - 2 * u) if ease else u
    a = math.radians(a0 + (a1 - a0) * u)
    return [round(cx + r * math.sin(a), 1), round(cy - r * math.cos(a), 1), h], [cx, cy, tz]

def write(name, dur, years, camf, lens):
    cam = []
    n = int(dur * 2) + 1
    for i in range(n):
        t = round(i * dur / (n - 1), 2); p, q = camf(t); cam.append([t, p, q, lens])
    json.dump({'_doc': f'Short {name} di Rotterdam: generato da regia_rotterdam_shorts.py (modificare li\').',
               'duration': dur, 'lens': lens, 'years': years, 'cam': cam}, open(f'schedule_rotterdam_short{name}.json', 'w'), indent=1)
    print(name, dur, 's =', int(round(dur * 24)), 'fotogrammi')

# B: centro, raggio 1,9 km, altezza 750 m (piu' citta' e meno cielo nel verticale), rotazione lenta da -8 a +4 gradi attorno a sud
DB = 26.0
write('B', DB,
      [[0, 1936], [6.0, 1939.9], [7.0, 1940.0], [9.5, 1940.45], [13.0, 1942], [13.5, 1945], [24.0, 1962], [DB, 1962]],
      lambda t: orbit(t, DB, 420, -60, 1900, 750, -8, 4), 28)

# C: torri del Kop van Zuid, camera sul fiume a ovest che si avvicina (da 1,5 a 1,1 km) e scende un poco
DC = 27.0
def camC(t):
    u = t / DC; u = u * u * (3 - 2 * u)
    p = [round(-900 + 450 * u, 1), round(-2600 + 300 * u, 1), round(170 - 40 * u, 1)]   # sopra l'acqua: riflessi delle torri
    return p, [760, -1680, 100]      # torri di Wilhelminapier e Maastoren al centro del verticale
write('C', DC, [[0, 1988], [2.0, 1990], [24.0, 2026], [DC, 2026]], camC, 50)
