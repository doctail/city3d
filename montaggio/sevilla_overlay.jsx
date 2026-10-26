// Livello grafico del video di Siviglia (Year Built #5), 1920x1080, 24 fps, 7.839 fotogrammi. Reso trasparente (WebM VP9 con alfa)
// e sovrapposto al render con monta_sevilla.bat.
//  - apertura: "SEVILLE TODAY" (2026) -> "800 YEARS" durante il riavvolgimento -> sepia -> titolo a 1248
//  - HUD: epoca + anno grande in basso a sinistra, popolazione in alto a destra (scheda, sezione D), barra del tempo in basso
//  - soste (picchiate della regia): titolo in basso al centro, con data o sottotitolo
//  - didascalie continue (una ogni 10-14 s, 8 s a schermo) in alto a sinistra, tempi da eventi_sevilla.json (regia_sevilla.py)
//  - Subscribe animato a 165 s, finale "WHICH CITY NEXT?"
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, staticFile, OffthreadVideo} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_sevilla.json';
import EV from '../public/eventi_sevilla.json';
import {SEVILLE as C} from './cities';

const FPS = 24, N = 7839, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 2px 14px rgba(0,0,0,0.6), 0 0 2px rgba(0,0,0,0.7)';
const yearAt = (f) => YEARS[String(Math.min(N, f + 1))] ?? 2026;
const ramp = (s, [a, b, c, d]) => interpolate(s, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const T_HUD = [0.2, 0.9, 318.0, 319.0], T_END = [319.4, 320.4];
const T_SEPIA = [5.0, 9.5, 11.5, 14.5];
const T_TITLE = [9.6, 10.2, 11.8, 12.5];
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
const tok = (t) => t.toLowerCase().split(/[^a-z]+/).filter((w) => w.length > 4 && w !== 'seville');
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
  [0.3, 2.9, 'SEVILLE TODAY', 'c. 690,000 people'],
  [3.3, 6.6, '800 YEARS', 'from an Almohad city to Expo 92'],
];
const Open = ({s}) => { const h = OPEN.find((x) => s >= x[0] && s < x[1]); if (!h) return null;
  const k = Math.min(1, (s - h[0]) / 0.45, (h[1] - s) / 0.45);
  return (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 140, opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.42 * k}), rgba(10,10,12,0) 62%)`}}>
    <div style={{font: '900 110px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, textAlign: 'center', transform: `translateY(${(1 - k) * 14}px)`}}>{h[2]}</div>
    <div style={{font: '700 46px Montserrat', color: ACC, textShadow: SH, marginTop: 12, textAlign: 'center'}}>{h[3]}</div>
  </AbsoluteFill>); };

const Title = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.45 * k}), rgba(10,10,12,0) 65%)`, paddingBottom: 90}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>EVERY BUILDING IN ITS REAL YEAR</div>
  <div style={{font: '900 200px Montserrat', color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05, transform: `scale(${0.96 + 0.04 * k})`}}>SEVILLE</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />1248 · 2026<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const End = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.55 * k}), rgba(10,10,12,0.15) 75%)`}}>
  <div style={{font: '700 24px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>EVERY REAL BUILDING · 778 YEARS</div>
  <div style={{font: '900 120px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, lineHeight: 1.1, marginTop: 10}}>WHICH CITY NEXT?</div>
  <div style={{font: '500 34px Montserrat', color: INK, textShadow: SH, marginTop: 18, opacity: 0.9}}>Tell us in the comments</div>
  <div style={{position: 'absolute', bottom: 70, font: '900 30px Montserrat', letterSpacing: 10, color: INK, textShadow: SH, opacity: 0.85}}>YEAR BUILT</div>
</AbsoluteFill>);

export const Overlay = ({bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAt(f);
  const kh = ramp(s, T_HUD), kt = ramp(s, T_TITLE), ks = ramp(s, T_SEPIA), ke = interpolate(s, T_END, [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile('sevilla_light.mp4')} style={{width: 1920, height: 1080}} />}
    {ks > 0 && <AbsoluteFill style={{background: `rgba(120,82,38,${0.34 * ks})`}} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud year={y} /><Cap s={s} /><Stop s={s} /><Subscribe s={s} /></AbsoluteFill>}
    <Open s={s} />
    {kt > 0 && <Title k={kt} />}
    {ke > 0 && <End k={ke} />}
  </AbsoluteFill>);
};
registerRoot(() => (<>
  <Composition id="SevilleOverlay" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: false}} />
  <Composition id="SevillePreview" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: true}} />
</>));
