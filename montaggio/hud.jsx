// Infografiche sovrapposte al render 3D: anno, epoca, popolazione con grafico, timeline, schede evento, titolo.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, Img, staticFile} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';

const INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 2px 14px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.6)';
// dati per citta' (anni, popolazione, epoche, eventi) in cities.js
import {NYC} from './cities';
const mk = (c) => ({...c, popAt: (y) => { const P = c.POP; for (let i = 1; i < P.length; i++) if (y <= P[i][0]) { const [a, pa] = P[i - 1], [b, pb] = P[i]; const t = (y - a) / (b - a); return pa <= 0 || pb <= 0 ? pa + (pb - pa) * t : Math.exp(Math.log(pa) + (Math.log(pb) - Math.log(pa)) * t); } return P[P.length - 1][1]; },
  eraAt: (y) => [...c.ERAS].reverse().find((e) => y >= e[0]) || c.ERAS[0]});
const fmtYear = (y) => `${Math.floor(y)}`;
const fmtPop = (p) => p < 1 ? '—' : Math.round(p / (p > 1e6 ? 1e4 : p > 1e4 ? 100 : 10)) * (p > 1e6 ? 1e4 : p > 1e4 ? 100 : 10);

// grafico popolazione: curva su scala logaritmica fino all'anno corrente
const Spark = ({c, year, w = 360, h = 92}) => { const {Y0, Y1, popAt} = c; const top = Math.log10(c.POPMAX || 9e6); const lx = (y) => ((y - Y0) / (Y1 - Y0)) * w; const ly = (p) => h - (Math.log10(Math.max(p, 10)) - 1) / (top - 1) * h;
  const pts = []; for (let y = Y0; y <= year; y += 2) pts.push(`${lx(y).toFixed(1)},${ly(popAt(y)).toFixed(1)}`); pts.push(`${lx(year)},${ly(popAt(year))}`);
  return (<svg width={w} height={h + 6} style={{overflow: 'visible'}}>
    {[2, 3, 4, 5, 6].filter((e) => e < top).map((e) => <line key={e} x1={0} x2={w} y1={ly(10 ** e)} y2={ly(10 ** e)} stroke="rgba(246,241,231,0.14)" strokeWidth={1} />)}
    <polyline points={`0,${h} ${pts.join(' ')} ${lx(year)},${h}`} fill="rgba(232,176,74,0.16)" stroke="none" />
    <polyline points={pts.join(' ')} fill="none" stroke={ACC} strokeWidth={3} strokeLinejoin="round" />
    <circle cx={lx(year)} cy={ly(popAt(year))} r={6} fill={ACC} stroke="#1b1b1b" strokeWidth={1.5} /></svg>); };

// barra del tempo con le epoche
const Timeline = ({c, year}) => { const {Y0, Y1, ERAS} = c; const W = 1760; const x = (y) => ((y - Y0) / (Y1 - Y0)) * W;
  return (<div style={{position: 'absolute', left: 80, bottom: 46, width: W, height: 26}}>
    {ERAS.map((e, i) => { const a = x(e[0]), b = x(i + 1 < ERAS.length ? ERAS[i + 1][0] : Y1); const on = year >= e[0];
      return <div key={i} style={{position: 'absolute', left: a, width: b - a - 3, top: 10, height: 6, background: e[2], opacity: on ? 0.95 : 0.25, borderRadius: 3}} />; })}
    {c.TICKS.map((y) => <div key={y} style={{position: 'absolute', left: x(y) - 30, width: 60, top: 22, textAlign: 'center', font: '500 15px Montserrat', color: 'rgba(246,241,231,0.7)', textShadow: SH}}>{y}</div>)}
    <div style={{position: 'absolute', left: x(year) - 2, top: -6, width: 4, height: 30, background: INK, borderRadius: 2, boxShadow: '0 0 12px rgba(255,255,255,0.8)'}} />
  </div>); };

const EventCard = ({c, year}) => { const ev = c.EVENTS.find((e) => year >= e[0] && year < e[1]); if (!ev) return null;
  const k = Math.min(1, (year - ev[0]) / 0.6, (ev[1] - year) / 0.6); const quiet = !!ev[4];
  return (<div style={{position: 'absolute', left: 80, top: 80, width: 640, opacity: k, transform: `translateX(${(1 - k) * -30}px)`, display: 'flex', gap: 22}}>
    <div style={{width: 6, borderRadius: 3, background: quiet ? '#cfd3d6' : ACC}} />
    <div><div style={{font: '700 22px Montserrat', letterSpacing: 4, color: quiet ? '#cfd3d6' : ACC, textShadow: SH}}>{ev[0]}</div>
      <div style={{font: '900 44px Montserrat', color: INK, textShadow: SH, lineHeight: 1.1, marginTop: 4}}>{ev[2]}</div>
      <div style={{font: '500 24px Montserrat', color: INK, textShadow: SH, lineHeight: 1.35, marginTop: 10, opacity: 0.92}}>{ev[3]}</div></div></div>); };

export const Hud = ({year, city = NYC}) => { const c = mk(city); const era = c.eraAt(year); const p = c.popAt(year);
  return (<AbsoluteFill>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 420, background: 'linear-gradient(0deg, rgba(10,10,12,0.62), rgba(10,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 900, height: 420, background: 'radial-gradient(ellipse at 0% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', left: 80, bottom: 104, display: 'flex', alignItems: 'flex-end', gap: 56}}>
      <div>
        <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, font: '700 22px Montserrat', letterSpacing: 5, textTransform: 'uppercase', color: INK, textShadow: SH}}><span style={{width: 14, height: 14, borderRadius: 7, background: era[2], boxShadow: '0 0 0 3px rgba(0,0,0,0.35)'}} />{era[1]}</div>
        <div style={{font: '900 150px Montserrat', color: INK, textShadow: SH, lineHeight: 0.95, fontVariantNumeric: 'tabular-nums', letterSpacing: -2}}>{fmtYear(year)}</div>
      </div>
      <div style={{paddingBottom: 14}}>
        <div style={{font: '700 18px Montserrat', letterSpacing: 4, color: 'rgba(246,241,231,0.75)', textShadow: SH}}>POPULATION <span style={{opacity: 0.7, letterSpacing: 2}}>· {c.popLabel(year)}</span></div>
        <div style={{font: '900 46px Montserrat', color: ACC, textShadow: SH, fontVariantNumeric: 'tabular-nums', margin: '2px 0 10px'}}>{p < 1 ? '—' : fmtPop(p).toLocaleString('en-US')}</div>
        <Spark c={c} year={year} />
      </div>
    </div>
    <Timeline c={c} year={year} /><EventCard c={c} year={year} />
  </AbsoluteFill>); };

export const TitleCard = ({k = 1}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(ellipse at center, rgba(10,10,12,0.35), rgba(10,10,12,0) 65%)', opacity: k}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>FROM A DUTCH TRADING POST TO A GLOBAL CAPITAL</div>
  <div style={{font: '900 210px Montserrat', color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05}}>NEW YORK</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />1624 · 2026<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const Test = ({year, mode}) => (<AbsoluteFill style={{background: '#222'}}>
  <Img src={staticFile('bg.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
  {mode === 'title' ? <TitleCard /> : <Hud year={year} />}
</AbsoluteFill>);
export const _HudTest = () => null;
// registerRoot(() => <Composition id="HudTest" component={Test} durationInFrames={1} fps={30} width={1920} height={1080} defaultProps={{year: 1664.5, mode: 'hud'}} />);
