// Shorts verticali di Madrid: clip native 1080x1920 dal pod (gia' accelerate), con titolo, anno e firma.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, interpolate} from 'remotion';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_madrid.json';
const FPS = 24, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 3px 18px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.8)';
// f0/step: primo fotogramma e passo nel video lungo (come in run.sh shorts); n: fotogrammi della clip
export const SHORTS = {
  M1: {src: 'mshort1.mp4', f0: 133, step: 7, n: 1101, top: '500 YEARS OF MADRID', sub: 'EVERY REAL BUILDING'},
  M2: {src: 'mshort2.mp4', f0: 5593, step: 2, n: 1124, top: 'MADRID REACHES FOR THE SKY', sub: '1931 → 2026'},
  M3: {src: 'mshort3.mp4', f0: 133, step: 2, n: 1134, top: 'HOW MADRID BEGAN', sub: '1480 → 1700'},
};
const Short = ({id}) => {
  const c = SHORTS[id]; const f = useCurrentFrame();
  const y = YEARS[String(Math.min(7839, c.f0 + f * c.step))] ?? 2026;
  const k = interpolate(f, [0, 12, c.n - 30, c.n], [0, 1, 1, 0.9], {extrapolateRight: 'clamp'});
  return (<AbsoluteFill style={{background: '#000'}}>
    <OffthreadVideo src={staticFile(c.src)} muted style={{width: 1080, height: 1920}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 520, background: 'linear-gradient(180deg, rgba(8,10,12,0.7), rgba(8,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 640, background: 'linear-gradient(0deg, rgba(8,10,12,0.75), rgba(8,10,12,0))'}} />
    <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center', opacity: k}}>
      <div style={{font: '900 78px Montserrat', color: INK, textShadow: SH, letterSpacing: 2, lineHeight: 1.05, padding: '0 50px'}}>{c.top}</div>
      <div style={{font: '700 34px Montserrat', color: ACC, textShadow: SH, letterSpacing: 8, marginTop: 16}}>{c.sub}</div>
    </div>
    <div style={{position: 'absolute', bottom: 330, width: '100%', textAlign: 'center'}}>
      <div style={{font: '700 30px Montserrat', color: 'rgba(246,241,231,0.8)', letterSpacing: 10, textShadow: SH}}>MADRID</div>
      <div style={{font: '900 230px Montserrat', color: INK, textShadow: SH, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.floor(y)}</div>
    </div>
    <div style={{position: 'absolute', bottom: 210, width: '100%', textAlign: 'center', font: '900 28px Montserrat', letterSpacing: 10, color: INK, opacity: 0.8, textShadow: SH}}>YEAR BUILT</div>
  </AbsoluteFill>);
};
registerRoot(() => (<>{Object.entries(SHORTS).map(([id, c]) => <Composition key={id} id={id} component={Short} durationInFrames={c.n} fps={FPS} width={1080} height={1920} defaultProps={{id}} />)}</>));
