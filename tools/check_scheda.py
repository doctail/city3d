#!/usr/bin/env python3
"""Controllo automatico di una scheda di validazione storica (formato regia, 23 ott 2026).
Uso: python3 -I tools/check_scheda.py <cartella con validazione.json e CSV>
Esempio: python3 -I tools/check_scheda.py parigi/validazione
Non modificare questo file senza accordo della regia: se un controllo sembra sbagliato, segnalalo.
Stampa un riepilogo e i problemi; esce con codice 1 se ci sono problemi di formato.
"""
import csv, glob, json, os, re, sys, collections

USO = {'BRUSCO', 'GRADUALE', 'TEMPORANEO', 'NESSUNO'}
d = sys.argv[1] if len(sys.argv) > 1 else '.'
J = json.load(open(os.path.join(d, 'validazione.json'), encoding='utf-8'))
prob, conta = [], collections.Counter()

def nome(r):
    e = (r.get('Elemento') or r.get('Evento') or '').split('—')[0]
    return re.sub(r'[\s\-’\']+', ' ', e).strip().lower()

for s, rows in J.items():
    if s == '0':
        continue
    visti = collections.Counter()
    ids = collections.Counter(r.get('ID') for r in rows)
    for k, n in ids.items():
        if n > 1:
            prob.append((s, k, 'ID duplicato'))
    for r in rows:
        i = r.get('ID', '?')
        da, a = str(r.get('Da (anno)', '')), str(r.get('A (anno)', ''))
        u, m = r.get('Uso nel modello', ''), (r.get('Motivo') or '').upper()
        af, note = r.get('Affidabilità', ''), r.get('Note') or ''
        tipo = 'BLOCCO' if 'BLOCCO' in m else 'CONFLITTO' if 'CONFLITTO' in m else 'MEMORIA' if 'MEMORIA' in m else 'ASSENTE' if 'ASSENTE' in m else '-'
        conta[(s, tipo)] += 1
        for v in (da, a):
            if v and not re.fullmatch(r'-?\d{1,4}', v):
                prob.append((s, i, 'anno non numerico', v))
        if u not in USO:
            prob.append((s, i, 'Uso nel modello non valido', u))
        if u == 'NESSUNO' and (da or a):
            prob.append((s, i, 'NESSUNO con date'))
        if u in USO - {'NESSUNO'} and not da:
            prob.append((s, i, 'uso senza Da'))
        if u == 'BRUSCO' and da != a:
            prob.append((s, i, 'BRUSCO con Da diverso da A'))
        if re.fullmatch(r'-?\d+', da or 'x') and re.fullmatch(r'-?\d+', a or 'x') and int(a) < int(da):
            prob.append((s, i, 'A prima di Da'))
        if tipo == 'MEMORIA' and af != 'bassa':
            prob.append((s, i, 'DA MEMORIA non bassa', af))
        if tipo == 'CONFLITTO' and af == 'alta':
            prob.append((s, i, 'CONFLITTO con affidabilità alta'))
        if not da and not a and af not in ('n/d', ''):
            prob.append((s, i, 'date vuote ma affidabilità non n/d', af))
        if s == 'D' and r.get('Stima', 'no') not in ('sì', 'no'):
            prob.append((s, i, 'Stima diversa da sì/no', r.get('Stima')))
        if tipo == 'BLOCCO' and not re.search('[«"“]', note):
            prob.append((s, i, 'BLOCCO TECNICO senza citazione tra virgolette'))
        if s == 'D' and not str(r.get('Valore HUD', '')).isdigit():
            prob.append((s, i, 'Valore HUD non intero', r.get('Valore HUD')))
        if s != 'D':
            visti[nome(r) + '|' + (r.get('Elemento') or '').split('—')[-1].strip().lower()] += 1
    for k, n in visti.items():
        if n > 1:
            prob.append((s, '-', 'riga duplicata', k[:60]))

for f in sorted(glob.glob(os.path.join(d, '*.csv'))):
    s = os.path.basename(f).split('_')[0]
    jj = {x.get('ID'): x for x in J.get(s, [])}
    rows = list(csv.DictReader(open(f, encoding='utf-8')))
    if len(rows) != len(jj):
        prob.append((s, '-', 'CSV e JSON con numero di righe diverso', f'{len(rows)} vs {len(jj)}'))
    for r in rows:
        x = jj.get(r.get('ID'))
        if not x or (r.get('Da (anno)'), r.get('A (anno)')) != (str(x.get('Da (anno)', '')), str(x.get('A (anno)', ''))):
            prob.append((s, r.get('ID'), 'CSV diverso dal JSON'))

md = glob.glob(os.path.join(d, '*.md'))
for f in md:
    cur = None
    for n, l in enumerate(open(f, encoding='utf-8'), 1):
        if l.startswith('|'):
            k = l.count('|') - l.count('\\|')
            if cur is None:
                cur = k
            elif k != cur:
                prob.append(('md', n, 'riga di tabella con numero di | diverso'))
        else:
            cur = None
        if re.search(r'[^\s`#\\]##\s', l):
            prob.append(('md', n, 'titolo attaccato alla riga precedente'))

tot = sum(conta.values())
src = sum(v for (s, t), v in conta.items() if t == 'BLOCCO')
print(f'righe {tot}, con fonte citata {src} ({100*src//max(tot,1)}%)')
print('per sezione:', dict(sorted(conta.items())))
print('PROBLEMI', len(prob))
for p in prob:
    print('  ', *p)
sys.exit(1 if prob else 0)
