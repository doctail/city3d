// Infografiche sovrapposte al render 3D: anno, epoca, popolazione con grafico, timeline, schede evento, titolo.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, Img, staticFile} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';

const INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 2px 14px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.6)';
const Y0 = 1600, Y1 = 2026;

// Popolazione (New York City; prima del 1898 solo Manhattan) — fonti: censimenti USA e stime coloniali
export const POP = [[1600, 0], [1624, 30], [1628, 270], [1664, 1500], [1698, 4937], [1712, 5840], [1737, 10664], [1756, 13046], [1771, 21863], [1776, 25000], [1783, 12000], [1790, 33131], [1800, 60515], [1810, 96373], [1820, 123706], [1830, 202589], [1840, 312710], [1850, 515547], [1860, 813669], [1870, 942292], [1880, 1164673], [1890, 1441216], [1897, 1900000], [1898, 3300000], [1900, 3437202], [1910, 4766883], [1920, 5620048], [1930, 6930446], [1940, 7454995], [1950, 7891957], [1960, 7781984], [1970, 7894862], [1980, 7071639], [1990, 7322564], [2000, 8008278], [2010, 8175133], [2020, 8804190], [2026, 8480000]];
export const popAt = (y) => { for (let i = 1; i < POP.length; i++) if (y <= POP[i][0]) { const [a, pa] = POP[i - 1], [b, pb] = POP[i]; const t = (y - a) / (b - a); return pa <= 0 || pb <= 0 ? pa + (pb - pa) * t : Math.exp(Math.log(pa) + (Math.log(pb) - Math.log(pa)) * t); } return POP[POP.length - 1][1]; };
export const ERAS = [[1600, 'Lenapehoking', '#7FA36B'], [1624, 'New Netherland', '#E07A3F'], [1664, 'British Colony', '#B8473A'], [1783, 'Young Republic', '#4F7FB8'], [1825, 'Port City', '#3E9AA0'], [1865, 'Gilded Age', '#C9A227'], [1898, 'Greater New York', '#8E6BBF'], [1945, 'Postwar City', '#6C8A9E'], [1990, 'Global City', '#D96C8A']];
const eraAt = (y) => [...ERAS].reverse().find((e) => y >= e[0]);
export const EVENTS = [
  [1609, 1615, 'Henry Hudson', 'An English captain sailing for the Dutch enters the harbor.'],
  [1625, 1631, 'Fort Amsterdam', 'The Dutch West India Company builds a fort at the tip of Manhattan.'],
  [1653, 1659, 'The wall', 'A timber wall guards the north edge of town. Wall Street follows its line.'],
  [1664, 1670, 'New Amsterdam becomes New York', 'English warships take the colony without a fight.'],
  [1776, 1783, 'Occupation', 'British troops hold the city for the whole Revolutionary War.'],
  [1825, 1831, 'The Erie Canal opens', 'Grain from the Great Lakes now flows to the port of New York.'],
  [1857, 1863, 'Central Park', 'Work begins on 843 acres in the middle of Manhattan.'],
  [1883, 1889, 'Brooklyn Bridge', 'The longest suspension bridge in the world links two cities.'],
  [1898, 1904, 'Five boroughs, one city', 'Manhattan, Brooklyn, Queens, the Bronx and Staten Island unite.'],
  [1904, 1909, 'The subway', 'The first underground line opens with 28 stations.'],
  [1931, 1936, 'Empire State Building', 'At 1,250 feet, the tallest building on Earth for 40 years.'],
  [2001, 2006, 'September 11, 2001', 'The World Trade Center is destroyed in a terrorist attack. 2,753 people are killed in New York.'],
  [2014, 2019, 'One World Trade Center', 'The new tower opens at 1,776 feet.'],
];
const fmtYear = (y) => `${Math.floor(y)}`;
const fmtPop = (p) => p < 1 ? '—' : Math.round(p / (p > 1e6 ? 1e4 : p > 1e4 ? 100 : 10)) * (p > 1e6 ? 1e4 : p > 1e4 ? 100 : 10);

// grafico popolazione: curva su scala logaritmica fino all'anno corrente
const Spark = ({year, w = 360, h = 92}) => { const lx = (y) => ((y - Y0) / (Y1 - Y0)) * w; const ly = (p) => h - (Math.log10(Math.max(p, 10)) - 1) / (Math.log10(9e6) - 1) * h;
  const pts = []; for (let y = Y0; y <= year; y += 2) pts.push(`${lx(y).toFixed(1)},${ly(popAt(y)).toFixed(1)}`); pts.push(`${lx(year)},${ly(popAt(year))}`);
  return (<svg width={w} height={h + 6} style={{overflow: 'visible'}}>
    {[2, 3, 4, 5, 6].map((e) => <line key={e} x1={0} x2={w} y1={ly(10 ** e)} y2={ly(10 ** e)} stroke="rgba(246,241,231,0.14)" strokeWidth={1} />)}
    <polyline points={`0,${h} ${pts.join(' ')} ${lx(year)},${h}`} fill="rgba(232,176,74,0.16)" stroke="none" />
    <polyline points={pts.join(' ')} fill="none" stroke={ACC} strokeWidth={3} strokeLinejoin="round" />
    <circle cx={lx(year)} cy={ly(popAt(year))} r={6} fill={ACC} stroke="#1b1b1b" strokeWidth={1.5} /></svg>); };

// barra del tempo con le epoche
const Timeline = ({year}) => { const W = 1760; const x = (y) => ((y - Y0) / (Y1 - Y0)) * W;
  return (<div style={{position: 'absolute', left: 80, bottom: 46, width: W, height: 26}}>
    {ERAS.map((e, i) => { const a = x(e[0]), b = x(i + 1 < ERAS.length ? ERAS[i + 1][0] : Y1); const on = year >= e[0];
      return <div key={i} style={{position: 'absolute', left: a, width: b - a - 3, top: 10, height: 6, background: e[2], opacity: on ? 0.95 : 0.25, borderRadius: 3}} />; })}
    {[1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000].map((y) => <div key={y} style={{position: 'absolute', left: x(y) - 30, width: 60, top: 22, textAlign: 'center', font: '500 15px Montserrat', color: 'rgba(246,241,231,0.7)', textShadow: SH}}>{y}</div>)}
    <div style={{position: 'absolute', left: x(year) - 2, top: -6, width: 4, height: 30, background: INK, borderRadius: 2, boxShadow: '0 0 12px rgba(255,255,255,0.8)'}} />
  </div>); };

const EventCard = ({year}) => { const ev = EVENTS.find((e) => year >= e[0] && year < e[1]); if (!ev) return null;
  const k = Math.min(1, (year - ev[0]) / 0.6, (ev[1] - year) / 0.6); const quiet = ev[0] === 2001;
  return (<div style={{position: 'absolute', left: 80, top: 80, width: 640, opacity: k, transform: `translateX(${(1 - k) * -30}px)`, display: 'flex', gap: 22}}>
    <div style={{width: 6, borderRadius: 3, background: quiet ? '#cfd3d6' : ACC}} />
    <div><div style={{font: '700 22px Montserrat', letterSpacing: 4, color: quiet ? '#cfd3d6' : ACC, textShadow: SH}}>{ev[0]}</div>
      <div style={{font: '900 44px Montserrat', color: INK, textShadow: SH, lineHeight: 1.1, marginTop: 4}}>{ev[2]}</div>
      <div style={{font: '500 24px Montserrat', color: INK, textShadow: SH, lineHeight: 1.35, marginTop: 10, opacity: 0.92}}>{ev[3]}</div></div></div>); };

export const Hud = ({year}) => { const era = eraAt(year); const p = popAt(year);
  return (<AbsoluteFill>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 420, background: 'linear-gradient(0deg, rgba(10,10,12,0.62), rgba(10,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 900, height: 420, background: 'radial-gradient(ellipse at 0% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', left: 80, bottom: 104, display: 'flex', alignItems: 'flex-end', gap: 56}}>
      <div>
        <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, font: '700 22px Montserrat', letterSpacing: 5, textTransform: 'uppercase', color: INK, textShadow: SH}}><span style={{width: 14, height: 14, borderRadius: 7, background: era[2], boxShadow: '0 0 0 3px rgba(0,0,0,0.35)'}} />{era[1]}</div>
        <div style={{font: '900 150px Montserrat', color: INK, textShadow: SH, lineHeight: 0.95, fontVariantNumeric: 'tabular-nums', letterSpacing: -2}}>{fmtYear(year)}</div>
      </div>
      <div style={{paddingBottom: 14}}>
        <div style={{font: '700 18px Montserrat', letterSpacing: 4, color: 'rgba(246,241,231,0.75)', textShadow: SH}}>POPULATION <span style={{opacity: 0.7, letterSpacing: 2}}>· {year >= 1898 ? 'FIVE BOROUGHS' : 'MANHATTAN'}</span></div>
        <div style={{font: '900 46px Montserrat', color: ACC, textShadow: SH, fontVariantNumeric: 'tabular-nums', margin: '2px 0 10px'}}>{p < 1 ? '—' : fmtPop(p).toLocaleString('en-US')}</div>
        <Spark year={year} />
      </div>
    </div>
    <Timeline year={year} /><EventCard year={year} />
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
