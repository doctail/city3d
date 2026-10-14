// Shorts verticali 1080x1920 ritagliati dal render orizzontale, accelerati, con anno grande e titolo.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, interpolate} from 'remotion';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_nyc.json';
const FPS = 24, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 3px 18px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.8)';
// t0: secondo di partenza nel video orizzontale, speed: accelerazione, cx: centro del ritaglio (0..1), dur: secondi dello short
export const SHORTS = {
  S1: {t0: 5.5, speed: 7.3, dur: 44, cx: 0.5, top: '400 YEARS OF NEW YORK', sub: 'EVERY REAL BUILDING'},
  S2: {t0: 233, speed: 2.2, dur: 42, cx: 0.62, top: 'THE SKYLINE RISES', sub: '1929 → 2026'},
  S3: {t0: 5.5, speed: 2.2, dur: 43, cx: 0.5, top: 'HOW NEW YORK BEGAN', sub: '1609 → 1700'},
};
const Short = ({id}) => {
  const c = SHORTS[id]; const f = useCurrentFrame(); const src = c.t0 * FPS + f * c.speed;
  const y = YEARS[String(Math.max(1, Math.min(7839, Math.round(src) + 1)))] ?? 2026;
  const k = interpolate(f, [0, 12, c.dur * FPS - 30, c.dur * FPS], [0, 1, 1, 0.9], {extrapolateRight: 'clamp'});
  const W = 1920 * (1920 / 1080);   // altezza 1920 -> larghezza video scalato 3413
  const left = -(W * c.cx - 540);
  return (<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
    <div style={{position: 'absolute', left, top: 0, width: W, height: 1920}}>
      <OffthreadVideo src={staticFile('nyc_light.mp4')} startFrom={Math.round(c.t0 * FPS)} playbackRate={c.speed} muted style={{width: W, height: 1920}} />
    </div>
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 520, background: 'linear-gradient(180deg, rgba(8,10,12,0.7), rgba(8,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 640, background: 'linear-gradient(0deg, rgba(8,10,12,0.75), rgba(8,10,12,0))'}} />
    <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center', opacity: k}}>
      <div style={{font: '900 78px Montserrat', color: INK, textShadow: SH, letterSpacing: 2, lineHeight: 1.05, padding: '0 50px'}}>{c.top}</div>
      <div style={{font: '700 34px Montserrat', color: ACC, textShadow: SH, letterSpacing: 8, marginTop: 16}}>{c.sub}</div>
    </div>
    <div style={{position: 'absolute', bottom: 330, width: '100%', textAlign: 'center'}}>
      <div style={{font: '700 30px Montserrat', color: 'rgba(246,241,231,0.8)', letterSpacing: 10, textShadow: SH}}>NEW YORK</div>
      <div style={{font: '900 230px Montserrat', color: INK, textShadow: SH, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.floor(y)}</div>
    </div>
    <div style={{position: 'absolute', bottom: 210, width: '100%', textAlign: 'center', font: '900 28px Montserrat', letterSpacing: 10, color: INK, opacity: 0.8, textShadow: SH}}>YEAR BUILT</div>
  </AbsoluteFill>);
};
registerRoot(() => (<>{Object.entries(SHORTS).map(([id, c]) => <Composition key={id} id={id} component={Short} durationInFrames={Math.round(c.dur * FPS)} fps={FPS} width={1080} height={1920} defaultProps={{id}} />)}</>));
