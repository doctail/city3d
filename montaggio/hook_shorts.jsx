// Shorts con apertura "dal presente": 1,5 s della citta' di oggi + scritta, poi lo short normale che parte dal passato.
// NYC3H: ritaglio verticale da nyc_light.mp4 (come nyc_shorts.jsx S3). M1H/M3H: clip native di Madrid dal pod.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, interpolate, Sequence} from 'remotion';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YNYC from '../public/years_nyc.json';
import YMAD from '../public/years_madrid.json';
const FPS = 24, H = 36, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 3px 18px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.8)';
const W = 1920 * (1920 / 1080);   // video orizzontale scalato a 1920 di altezza

// hook: sorgente dell'apertura; main: sorgente dello short; year(f): anno al fotogramma f dello short
const DEF = {
  NYC3H: {city: 'NEW YORK', from: 1609, top: 'HOW NEW YORK BEGAN', sub: '1609 → 1700', n: Math.round(43 * FPS),
    hook: {src: 'nyc_light.mp4', crop: 0.62, start: Math.round(314 * FPS), rate: 1},
    main: {src: 'nyc_light.mp4', crop: 0.5, start: Math.round(5.5 * FPS), rate: 2.2},
    year: (f) => YNYC[String(Math.max(1, Math.min(7839, Math.round(5.5 * FPS + f * 2.2) + 1)))] ?? 2026},
  M1H: {city: 'MADRID', from: 1480, top: '500 YEARS OF MADRID', sub: 'EVERY REAL BUILDING', n: 1101,
    hook: {src: 'mshort2.mp4', start: 975, rate: 1}, main: {src: 'mshort1.mp4', start: 0, rate: 1},
    year: (f) => YMAD[String(Math.min(7839, 133 + f * 7))] ?? 2026},
  M3H: {city: 'MADRID', from: 1480, top: 'HOW MADRID BEGAN', sub: '1480 → 1700', n: 1134,
    hook: {src: 'mshort2.mp4', start: 975, rate: 1}, main: {src: 'mshort3.mp4', start: 0, rate: 1},
    year: (f) => YMAD[String(Math.min(7839, 133 + f * 2))] ?? 2026},
};

const Clip = ({s}) => s.crop != null
  ? (<div style={{position: 'absolute', left: -(W * s.crop - 540), top: 0, width: W, height: 1920}}>
      <OffthreadVideo src={staticFile(s.src)} startFrom={s.start} playbackRate={s.rate} muted style={{width: W, height: 1920}} /></div>)
  : <OffthreadVideo src={staticFile(s.src)} startFrom={s.start} playbackRate={s.rate} muted style={{width: 1080, height: 1920}} />;

const Shade = () => (<>
  <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 520, background: 'linear-gradient(180deg, rgba(8,10,12,0.7), rgba(8,10,12,0))'}} />
  <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 640, background: 'linear-gradient(0deg, rgba(8,10,12,0.75), rgba(8,10,12,0))'}} /></>);
const Year = ({city, y}) => (<>
  <div style={{position: 'absolute', bottom: 330, width: '100%', textAlign: 'center'}}>
    <div style={{font: '700 30px Montserrat', color: 'rgba(246,241,231,0.8)', letterSpacing: 10, textShadow: SH}}>{city}</div>
    <div style={{font: '900 230px Montserrat', color: INK, textShadow: SH, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.floor(y)}</div></div>
  <div style={{position: 'absolute', bottom: 210, width: '100%', textAlign: 'center', font: '900 28px Montserrat', letterSpacing: 10, color: INK, opacity: 0.8, textShadow: SH}}>YEAR BUILT</div></>);

const Hook = ({c}) => { const f = useCurrentFrame(); const k = interpolate(f, [0, 4], [0, 1], {extrapolateRight: 'clamp'});
  return (<AbsoluteFill style={{background: '#000'}}><Clip s={c.hook} /><Shade />
    <div style={{position: 'absolute', top: 190, width: '100%', textAlign: 'center', opacity: k}}>
      <div style={{font: '900 92px Montserrat', color: INK, textShadow: SH, lineHeight: 1.05, padding: '0 40px'}}>{c.city} TODAY</div>
      <div style={{font: '700 40px Montserrat', color: ACC, textShadow: SH, letterSpacing: 6, marginTop: 22}}>NOW WATCH IT GROW FROM {c.from}</div></div>
    <Year city={c.city} y={2026} /></AbsoluteFill>); };

const Main = ({c}) => { const f = useCurrentFrame(); const k = interpolate(f, [0, 10, c.n - 30, c.n], [0, 1, 1, 0.9], {extrapolateRight: 'clamp'});
  return (<AbsoluteFill style={{background: '#000'}}><Clip s={c.main} /><Shade />
    <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center', opacity: k}}>
      <div style={{font: '900 78px Montserrat', color: INK, textShadow: SH, letterSpacing: 2, lineHeight: 1.05, padding: '0 50px'}}>{c.top}</div>
      <div style={{font: '700 34px Montserrat', color: ACC, textShadow: SH, letterSpacing: 8, marginTop: 16}}>{c.sub}</div></div>
    <Year city={c.city} y={c.year(f)} /></AbsoluteFill>); };

const Short = ({id}) => { const c = DEF[id];
  return (<AbsoluteFill><Sequence durationInFrames={H}><Hook c={c} /></Sequence><Sequence from={H}><Main c={c} /></Sequence></AbsoluteFill>); };

registerRoot(() => (<>{Object.entries(DEF).map(([id, c]) => <Composition key={id} id={id} component={Short} durationInFrames={H + c.n} fps={FPS} width={1080} height={1920} defaultProps={{id}} />)}</>));
