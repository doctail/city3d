// Livello grafico del video di Parigi (Year Built), 1920x1080, 24 fps, 9.360 fotogrammi (6:30). Reso trasparente (WebM VP9 con alfa)
// Labels: niente etichette prima di 12,6 s (sopra il titolo)
// e sovrapposto al render con monta_parigi.bat. Copiato da sevilla_overlay.jsx (31 ott 2026), in piu':
//  - immagini d'archivio (pubblico dominio / CC0, montaggio/archivio_parigi/licenze.json) in un riquadro a destra, 3,5 s ciascuna
//  - finestre delle etichette da labs_parigi.json (labs_parigi.py), titolo senza "EVERY REAL BUILDING"
//  - Short verticale (ParisShort): tutto il video accelerato in 28 s
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, staticFile, OffthreadVideo} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_parigi.json';
import EV from '../public/eventi_parigi.json';
import LABELS from '../public/labels_parigi.json';
import LABS_J from '../public/labs_parigi.json';
import {PARIS as C} from './cities';

const FPS = 24, N = 9360, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 2px 14px rgba(0,0,0,0.6), 0 0 2px rgba(0,0,0,0.7)';
const yearAt = (f) => YEARS[String(Math.min(N, f + 1))] ?? 2026;
const ramp = (s, [a, b, c, d]) => interpolate(s, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const T_HUD = [0.2, 0.9, 386.0, 387.0], T_END = [387.4, 388.4];
const T_SEPIA = [5.0, 9.3, 11.5, 14.5];
const T_TITLE = [9.4, 10.0, 11.8, 12.5];
const FIRST_STOP_AT = 13.0;   // la prima sosta (1248) parte dopo il titolo

const popAt = (y) => { const P = C.POP; for (let i = 1; i < P.length; i++) if (y <= P[i][0]) { const [a, pa] = P[i - 1], [b, pb] = P[i]; const t = (y - a) / (b - a); return Math.exp(Math.log(pa) + (Math.log(pb) - Math.log(pa)) * t); } return P[P.length - 1][1]; };
const eraAt = (y) => [...C.ERAS].reverse().find((e) => y >= e[0]) || C.ERAS[0];
const fmtPop = (p) => { const q = p > 1e4 ? 100 : 10; return Math.round(p / q) * q; };

const Spark = ({year, w = 360, h = 84}) => { const {Y0, Y1} = C; const top = Math.log10(C.POPMAX); const lx = (y) => ((y - Y0) / (Y1 - Y0)) * w; const ly = (p) => h - (Math.log10(Math.max(p, 10)) - 1) / (top - 1) * h;
  const pts = []; for (let y = Y0; y <= year; y += 2) pts.push(`${lx(y).toFixed(1)},${ly(popAt(y)).toFixed(1)}`); pts.push(`${lx(year)},${ly(popAt(year))}`);
  return (<svg width={w} height={h + 6} style={{overflow: 'visible'}}>
    {[2, 3, 4, 5].map((e) => <line key={e} x1={0} x2={w} y1={ly(10 ** e)} y2={ly(10 ** e)} stroke="rgba(246,241,231,0.14)" strokeWidth={1} />)}
    <polyline points={`0,${h} ${pts.join(' ')} ${lx(year)},${h}`} fill="rgba(232,176,74,0.16)" stroke="none" />
    <polyline points={pts.join(' ')} fill="none" stroke={ACC} strokeWidth={3} strokeLinejoin="round" />
    <circle cx={lx(year)} cy={ly(popAt(year))} r={6} fill={ACC} stroke="#1b1b1b" strokeWidth={1.5} /></svg>); };

const Timeline = ({year}) => { const {Y0, Y1, ERAS} = C; const W = 1760; const x = (y) => ((y - Y0) / (Y1 - Y0)) * W;
  return (<div style={{position: 'absolute', left: 80, bottom: 46, width: W, height: 26}}>
    {ERAS.map((e, i) => { const a = x(e[0]), b = x(i + 1 < ERAS.length ? ERAS[i + 1][0] : Y1); const on = year >= e[0];
      return <div key={i} style={{position: 'absolute', left: a, width: b - a - 3, top: 10, height: 6, background: e[2], opacity: on ? 0.95 : 0.25, borderRadius: 3}} />; })}
    {C.TICKS.map((y) => <div key={y} style={{position: 'absolute', left: x(y) - 30, width: 60, top: 22, textAlign: 'center', font: '500 15px Montserrat', color: 'rgba(246,241,231,0.7)', textShadow: SH}}>{y}</div>)}
    <div style={{position: 'absolute', left: x(year) - 2, top: -6, width: 4, height: 30, background: INK, borderRadius: 2, boxShadow: '0 0 12px rgba(255,255,255,0.8)'}} />
  </div>); };

const Hud = ({year}) => { const era = eraAt(year); const p = popAt(year); const est = year < C.EST_UNTIL || year > 2022;
  return (<AbsoluteFill>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 420, background: 'linear-gradient(0deg, rgba(10,10,12,0.62), rgba(10,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 900, height: 420, background: 'radial-gradient(ellipse at 0% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', right: 0, top: 0, width: 700, height: 340, background: 'radial-gradient(ellipse at 100% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', left: 80, bottom: 104}}>
      <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, font: '700 22px Montserrat', letterSpacing: 5, textTransform: 'uppercase', color: INK, textShadow: SH}}><span style={{width: 14, height: 14, borderRadius: 7, background: era[2], boxShadow: '0 0 0 3px rgba(0,0,0,0.35)'}} />{era[1]}</div>
      <div style={{font: '900 150px Montserrat', color: INK, textShadow: SH, lineHeight: 0.95, fontVariantNumeric: 'tabular-nums', letterSpacing: -2}}>{Math.floor(year)}</div>
    </div>
    <div style={{position: 'absolute', right: 80, top: 78, textAlign: 'right'}}>
      <div style={{font: '700 18px Montserrat', letterSpacing: 4, color: 'rgba(246,241,231,0.75)', textShadow: SH}}>POPULATION <span style={{opacity: 0.7, letterSpacing: 2}}>· {C.popLabel()}</span></div>
      <div style={{font: '900 52px Montserrat', color: ACC, textShadow: SH, fontVariantNumeric: 'tabular-nums', margin: '2px 0 10px'}}>{est ? '~' : ''}{fmtPop(p).toLocaleString('en-US')}</div>
      <div style={{display: 'inline-block'}}><Spark year={year} /></div>
    </div>
    <Timeline year={year} />
  </AbsoluteFill>); };

// didascalie continue (alto a sinistra): [t_in, t_out, date, title, line]
const Cap = ({s}) => { const e = EV.didascalie.find((c) => s >= c.t_in && s < c.t_out); if (!e) return null;
  const k = Math.min(1, (s - e.t_in) / 0.5, (e.t_out - s) / 0.5);
  return (<div style={{position: 'absolute', left: 80, top: 78, width: 700, opacity: k, transform: `translateX(${(1 - k) * -30}px)`, display: 'flex', gap: 22}}>
    <div style={{width: 6, borderRadius: 3, background: ACC}} />
    <div><div style={{font: '700 24px Montserrat', letterSpacing: 4, color: ACC, textShadow: SH}}>{e.date.toUpperCase()}</div>
      <div style={{font: '900 50px Montserrat', color: INK, textShadow: SH, lineHeight: 1.08, marginTop: 4}}>{e.title}</div>
      <div style={{font: '500 27px Montserrat', color: INK, textShadow: SH, lineHeight: 1.35, marginTop: 10, opacity: 0.94}}>{e.line}</div></div></div>); };

// soste con picchiata (basso, al centro)
const tok = (t) => t.toLowerCase().split(/[^a-z]+/).filter((w) => w.length > 4 && w !== 'paris');
const Stop = ({s}) => { const e = EV.soste.map((x, i) => (i === 0 ? {...x, t_in: Math.max(x.t_in, FIRST_STOP_AT), t_out: x.t_out + (FIRST_STOP_AT - x.t_in)} : x)).find((x) => s >= x.t_in && s < x.t_out); if (!e) return null;
  // se in alto a sinistra c'e' gia' la didascalia dello stesso fatto (stesse parole chiave), il titolo della sosta non si ripete
  const cp = EV.didascalie.find((c) => s >= c.t_in && s < c.t_out); if (cp && tok(cp.title).some((w) => tok(e.title).includes(w))) return null;
  const k = Math.min(1, (s - e.t_in) / 0.5, (e.t_out - s) / 0.5);
  return (<div style={{position: 'absolute', left: 520, width: 900, bottom: 132, textAlign: 'center', opacity: k, transform: `translateY(${(1 - k) * 16}px)`}}>
    <div style={{display: 'inline-block', padding: '16px 34px', borderRadius: 14, background: 'rgba(12,14,16,0.62)', borderBottom: `4px solid ${ACC}`}}>
      <div style={{font: '900 44px Montserrat', color: INK, textShadow: SH, lineHeight: 1.12, textWrap: 'balance'}}>{e.title}</div>
      {e.sub ? <div style={{font: '700 26px Montserrat', letterSpacing: 4, color: ACC, textShadow: SH, marginTop: 8}}>{e.sub.toUpperCase()}</div> : null}
    </div></div>); };

// Subscribe animato: entra, clic, diventa "SUBSCRIBED" con campanella
const Subscribe = ({s}) => { const t0 = EV.subscribe_t; const u = s - t0; if (u < 0 || u > 5.2) return null;
  const k = Math.min(1, u / 0.45, (5.2 - u) / 0.45); const click = u > 2.0; const press = interpolate(u, [1.8, 2.0, 2.15], [1, 0.92, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ring = click ? Math.sin((u - 2.1) * 22) * Math.max(0, 1 - (u - 2.1) / 1.3) * 18 : 0;
  const cx = interpolate(u, [0.5, 1.8], [90, 24], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: (x) => 1 - Math.pow(1 - x, 3)}), cy = interpolate(u, [0.5, 1.8], [70, 20], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<div style={{position: 'absolute', right: 80, bottom: 150, opacity: k, transform: `translateX(${(1 - k) * 60}px)`}}>
    <div style={{position: 'relative', display: 'flex', alignItems: 'center', gap: 16, transform: `scale(${press})`}}>
      <div style={{padding: '16px 30px', borderRadius: 40, background: click ? 'rgba(80,80,84,0.92)' : '#E62117', font: '900 30px Montserrat', color: '#fff', letterSpacing: 2, boxShadow: '0 4px 18px rgba(0,0,0,0.5)'}}>{click ? '✓ SUBSCRIBED' : 'SUBSCRIBE'}</div>
      <div style={{width: 62, height: 62, borderRadius: 31, background: 'rgba(12,14,16,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 34, transform: `rotate(${ring}deg)`, transformOrigin: '50% 12%'}}>🔔</div>
      {!click && u > 0.5 && <svg width={40} height={40} viewBox="0 0 24 24" style={{position: 'absolute', left: 90 + cx, top: 20 + cy, filter: 'drop-shadow(0 2px 3px rgba(0,0,0,0.6))'}}><path d="M5 3l14 8-6 1.5L10 19z" fill="#fff" stroke="#111" strokeWidth={1.2} /></svg>}
    </div></div>); };

// apertura: sul presente, poi "800 YEARS" nel riavvolgimento
const OPEN = [
  [0.3, 2.9, 'PARIS TODAY', '2,065,560 people'],
  [3.3, 8.8, '836 YEARS', 'from a walled island to a world capital'],
];
const Open = ({s}) => { const h = OPEN.find((x) => s >= x[0] && s < x[1]); if (!h) return null;
  const k = Math.min(1, (s - h[0]) / 0.45, (h[1] - s) / 0.45);
  return (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 140, opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.42 * k}), rgba(10,10,12,0) 62%)`}}>
    <div style={{font: '900 110px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, textAlign: 'center', transform: `translateY(${(1 - k) * 14}px)`}}>{h[2]}</div>
    <div style={{font: '700 46px Montserrat', color: ACC, textShadow: SH, marginTop: 12, textAlign: 'center'}}>{h[3]}</div>
  </AbsoluteFill>); };

const Title = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.45 * k}), rgba(10,10,12,0) 65%)`, paddingBottom: 90}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>3D TIMELAPSE</div>
  <div style={{font: '900 200px Montserrat', color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05, transform: `scale(${0.96 + 0.04 * k})`}}>PARIS</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />1190 TO NOW<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const End = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.55 * k}), rgba(10,10,12,0.15) 75%)`}}>
  <div style={{font: '700 24px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>PARIS · 836 YEARS</div>
  <div style={{font: '900 120px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, lineHeight: 1.1, marginTop: 10}}>WHICH CITY NEXT?</div>
  <div style={{font: '500 34px Montserrat', color: INK, textShadow: SH, marginTop: 18, opacity: 0.9}}>Tell us in the comments</div>
  <div style={{position: 'absolute', bottom: 70, font: '900 30px Montserrat', letterSpacing: 10, color: INK, textShadow: SH, opacity: 0.85}}>YEAR BUILT</div>
</AbsoluteFill>);

// etichette sui monumenti: posizione proiettata con la STESSA camera del render (labels_parigi.json da labels_cam.py).
// Finestre a tempo [inizio s, fine s, nomi]; ogni etichetta compare solo se il monumento esiste in quell'anno ed e' nel quadro.
const LABS = LABS_J.labs;
const LAB_END = LABS_J.end;
const Label = ({name, f, k, i = 0, year, cap}) => { const L = LABELS.lm[name]; if (!L) return null; if (year < L.y || year >= (LAB_END[name] ?? 9999)) return null;
  const p = L.p[f - LABELS.F0]; if (!p) return null;
  const [x, y, z] = p; if (z <= 0 || x < 70 || x > 1850 || y < 230 || y > 900) return null;
  const up = (92 + 64 * i) * k;
  // se il cartellino coprirebbe la didascalia in alto a sinistra, il filo va verso il basso; se anche sotto c'e' l'HUD, non si mostra
  const down = cap && x - 110 < 800 && y - up - 52 < 330;
  if (down && (y + up + 60 > 900 || (x - 110 < 620 && y + up + 60 > 760))) return null;
  return (<div style={{position: 'absolute', left: x, top: y, opacity: k}}>
    <div style={{position: 'absolute', left: -7, top: -7, width: 14, height: 14, borderRadius: 7, background: ACC, boxShadow: '0 0 0 3px rgba(0,0,0,0.45)'}} />
    <div style={{position: 'absolute', left: -1.5, top: down ? 0 : -up, width: 3, height: up, background: 'rgba(246,241,231,0.9)', boxShadow: '0 0 6px rgba(0,0,0,0.6)'}} />
    <div style={{position: 'absolute', left: 0, top: down ? up : -up - 52, transform: 'translateX(-50%)', whiteSpace: 'nowrap', padding: '8px 18px', borderRadius: 26, background: 'rgba(12,14,16,0.72)', font: '700 26px Montserrat', color: INK, letterSpacing: 1}}>{name}</div>
  </div>); };
const Labels = ({s, f, year}) => { const on = new Map(); if (s < 12.6) return null; const cap = EV.didascalie.some((c) => s >= c.t_in - 0.3 && s < c.t_out + 0.3);
  for (const e of LABS) if (s >= e[0] && s < e[1]) e[2].forEach((n) => { if (!on.has(n)) on.set(n, Math.min(1, (s - e[0]) / 0.5, (e[1] - s) / 0.5)); });
  return <>{[...on.entries()].map(([n, k], i) => <Label key={n} name={n} f={f} k={k} i={i} year={year} cap={cap} />)}</>; };


// immagini d'archivio: [t_in, t_out, file in public/arch, didascalia]. Riquadro a destra sotto la popolazione.
const ARCH = [
  [19.5, 23.0, '01_1248_palais_cite.jpg', 'Palais de la Cité and Sainte-Chapelle · Très Riches Heures, c. 1415'],
  [65.0, 68.5, '03_1739_turgot_place_dauphine.jpg', 'Pont Neuf and Place Dauphine · Turgot map, 1739'],
  [110.0, 113.5, '02_1739_turgot_louvre.jpg', 'The Louvre and the Tuileries · Turgot map, 1739'],
  [136.3, 140.3, '04_1789_bastille.jpg', 'The storming of the Bastille · Jean-Pierre Houël, 1789'],
  [219.8, 223.3, '05_1865_rue_glatigny.jpg', 'Rue de Glatigny before Haussmann · Charles Marville, 1865'],
  [223.6, 227.1, '06_1865_rue_marmousets.jpg', 'Rue des Marmousets, Île de la Cité · Charles Marville'],
  [227.4, 231.0, '07_1870_place_chatelet.jpg', 'Place du Châtelet · Charles Marville'],
  [233.0, 236.5, '10_1871_hotel_de_ville_liebert.jpg', 'Hôtel de Ville burned by the Commune · Alphonse Liébert, 1871'],
  [250.5, 254.0, '08_1877_opera_demolition.jpg', "Clearing the Avenue de l'Opéra · Charles Marville, 1877"],
  [271.0, 274.8, '11_1888_eiffel_durandelle.jpg', 'The Eiffel Tower under construction · Louis-Émile Durandelle, 1888'],
];
const Archive = ({s}) => { const e = ARCH.find((a) => s >= a[0] && s < a[1]); if (!e) return null;
  const k = Math.min(1, (s - e[0]) / 0.4, (e[1] - s) / 0.4); const z = 1 + 0.04 * (s - e[0]) / (e[1] - e[0]);
  return (<div style={{position: 'absolute', right: 80, top: 330, width: 520, opacity: k, transform: `translateX(${(1 - k) * 40}px) rotate(${(1 - k) * 2}deg)`}}>
    <div style={{padding: 10, background: '#EFE6D2', borderRadius: 6, boxShadow: '0 10px 34px rgba(0,0,0,0.55)'}}>
      <div style={{width: 500, height: 360, overflow: 'hidden', background: '#222'}}>
        <img src={staticFile('arch/' + e[2])} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z})`, filter: 'sepia(0.25) contrast(1.05)'}} /></div>
      <div style={{font: '600 17px Montserrat', color: '#2a241b', marginTop: 8, lineHeight: 1.3}}><span style={{fontWeight: 900, letterSpacing: 2}}>ARCHIVE · </span>{e[3]}</div>
    </div></div>); };

export const Overlay = ({bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAt(f);
  const kh = ramp(s, T_HUD), kt = ramp(s, T_TITLE), ks = ramp(s, T_SEPIA), ke = interpolate(s, T_END, [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile('parigi_light.mp4')} style={{width: 1920, height: 1080}} />}
    {ks > 0 && <AbsoluteFill style={{background: `rgba(120,82,38,${0.34 * ks})`}} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud year={y} /><Labels s={s} f={f + 1} year={y} /><Cap s={s} /><Stop s={s} /><Archive s={s} /><Subscribe s={s} /></AbsoluteFill>}
    <Open s={s} />
    {kt > 0 && <Title k={kt} />}
    {ke > 0 && <End k={ke} />}
  </AbsoluteFill>);
};

// Short verticale 1080x1920: tutto il video (dopo l'apertura, 9,5 -> 350 s) accelerato in 28 s. Sopra: PARIS e l'anno; sotto: popolazione.
const SN = 672, SA = 9.5, SB = 350.0;
export const Short = () => { const f = useCurrentFrame(); const s = f / FPS; const src = SA + (SB - SA) * Math.min(1, s / 26.5); const y = yearAt(Math.round(src * FPS));
  const k0 = interpolate(s, [0, 0.4], [0, 1], {extrapolateRight: 'clamp'}); const ke = interpolate(s, [26.6, 27.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const era = eraAt(y);
  return (<AbsoluteFill>
    <div style={{position: 'absolute', top: 210, width: 1080, textAlign: 'center', opacity: k0}}>
      <div style={{font: '700 40px Montserrat', letterSpacing: 12, color: ACC, textShadow: SH}}>836 YEARS IN 30 SECONDS</div>
      <div style={{font: '900 190px Montserrat', color: INK, textShadow: SH, letterSpacing: 8, lineHeight: 1.05}}>PARIS</div></div>
    <div style={{position: 'absolute', top: 1330, width: 1080, textAlign: 'center', opacity: k0 * (1 - ke)}}>
      <div style={{font: '900 230px Montserrat', color: INK, textShadow: SH, fontVariantNumeric: 'tabular-nums', lineHeight: 1}}>{Math.floor(y)}</div>
      <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, font: '700 38px Montserrat', letterSpacing: 6, textTransform: 'uppercase', color: INK, textShadow: SH, marginTop: 10}}><span style={{width: 20, height: 20, borderRadius: 10, background: era[2]}} />{era[1]}</div>
      <div style={{font: '900 52px Montserrat', color: ACC, textShadow: SH, marginTop: 26}}>{y < C.EST_UNTIL ? '~' : ''}{fmtPop(popAt(y)).toLocaleString('en-US')} <span style={{font: '700 30px Montserrat', color: INK, letterSpacing: 3}}>PEOPLE</span></div></div>
    {ke > 0 && <div style={{position: 'absolute', top: 1360, width: 1080, textAlign: 'center', opacity: ke}}>
      <div style={{font: '900 84px Montserrat', color: INK, textShadow: SH}}>FULL VIDEO</div>
      <div style={{font: '700 40px Montserrat', color: ACC, textShadow: SH, marginTop: 10, letterSpacing: 4}}>ON THE CHANNEL ↑</div></div>}
  </AbsoluteFill>); };
registerRoot(() => (<>
  <Composition id="ParisOverlay" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: false}} />
  <Composition id="ParisPreview" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: true}} />
  <Composition id="ParisShort" component={Short} durationInFrames={SN} fps={FPS} width={1080} height={1920} />
</>));
