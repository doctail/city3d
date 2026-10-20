// Shorts di Copenaghen (20 ott 2026): livelli grafici TRASPARENTI 1080x1920 da sovrapporre alle clip native del pod
// (copenhagen_shortA/B/C.mp4) con monta_copenhagen_shorts.bat. Tutti con regia propria (regia_copenhagen_shorts.py).
// A = controllo (tutta la storia). B = Grande Incendio del 1728. C = Christiansborg brucia due volte (1794, 1884).
// Niente apertura sul presente. La domanda/affermazione e' scritta dal primo fotogramma.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YA from '../public/years_copenhagen_shortA.json';
import YB from '../public/years_copenhagen_shortB.json';
import YC from '../public/years_copenhagen_shortC.json';
import LC from '../public/labels_copenhagen_shortC.json';
const FPS = 24, INK = '#F6F1E7', ACC = '#E8B04A', GREY = '#cfd3d6', FIRE = '#F08A4B', SH = '0 3px 18px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.8)';
// sub: [inizio s, fine s, testo, colore]; lab: [inizio s, fine s, monumento]
export const SHORTS = {
  A: {n: 672, year: (f) => YA[String(f + 1)], top: '859 YEARS OF COPENHAGEN', sub: [[0, 25.5, 'EVERY REAL BUILDING', ACC], [25.5, 99, 'FULL STORY ON OUR CHANNEL', INK]]},
  B: {n: 624, year: (f) => YB[String(f + 1)], top: 'WHAT HAPPENED TO COPENHAGEN IN 1728?',
      sub: [[4.6, 12.6, '20 OCTOBER 1728 · THE GREAT FIRE', FIRE], [12.7, 15.9, '~1,600 BUILDINGS LOST', GREY], [16.0, 23.9, 'THE CITY REBUILDS', ACC], [24.0, 99, 'FULL STORY ON OUR CHANNEL', INK]]},
  C: {n: 672, year: (f) => YC[String(f + 1)], top: 'THIS PALACE BURNED DOWN TWICE',
      sub: [[2.4, 7.4, 'CHRISTIANSBORG I', ACC], [7.6, 11.5, 'FIRE · 26 FEBRUARY 1794', FIRE], [12.6, 16.8, 'CHRISTIANSBORG II', ACC], [17.0, 20.9, 'FIRE · 3 OCTOBER 1884', FIRE], [21.5, 25.9, 'THE THIRD PALACE', ACC], [26.0, 99, 'FULL STORY ON OUR CHANNEL', INK]],
      lab: [[0.2, 1.9, 'Copenhagen Castle'], [24.6, 28, 'Christiansborg']], L: LC},
};
const Label = ({c, name, f, k, i}) => { const p = c.L.lm[name].p[f - c.L.F0]; if (!p) return null; const [x, y, z] = p;
  if (z <= 0 || x < 80 || x > 1000 || y < 500 || y > 1500) return null; const up = (110 + 80 * i) * k;
  return (<div style={{position: 'absolute', left: x, top: y, opacity: k}}>
    <div style={{position: 'absolute', left: -9, top: -9, width: 18, height: 18, borderRadius: 9, background: ACC, boxShadow: '0 0 0 4px rgba(0,0,0,0.45)'}} />
    <div style={{position: 'absolute', left: -2, top: -up, width: 4, height: up, background: 'rgba(246,241,231,0.9)'}} />
    <div style={{position: 'absolute', left: 0, top: -up - 66, transform: 'translateX(-50%)', whiteSpace: 'nowrap', padding: '10px 24px', borderRadius: 32, background: 'rgba(12,14,16,0.72)', font: '700 36px Montserrat', color: INK}}>{name}</div>
  </div>); };
const Short = ({id}) => {
  const c = SHORTS[id]; const f = useCurrentFrame(); const s = f / FPS; const y = c.year(f) ?? 2026;
  const sub = c.sub.find((x) => s >= x[0] && s < x[1]); const ks = sub ? Math.min(1, (s - sub[0]) / 0.3, (sub[1] - s) / 0.3) : 0;
  return (<AbsoluteFill>
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 560, background: 'linear-gradient(180deg, rgba(8,10,12,0.62), rgba(8,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 640, background: 'linear-gradient(0deg, rgba(8,10,12,0.72), rgba(8,10,12,0))'}} />
    <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center'}}>
      <div style={{font: '900 76px Montserrat', color: INK, textShadow: SH, letterSpacing: 1, lineHeight: 1.06, padding: '0 60px'}}>{c.top}</div>
      {sub && <div style={{font: '700 36px Montserrat', color: sub[3], textShadow: SH, letterSpacing: 7, marginTop: 20, opacity: ks}}>{sub[2]}</div>}
    </div>
    {(c.lab || []).filter((l) => s >= l[0] && s < l[1]).map((l, i) => <Label key={l[2]} c={c} name={l[2]} f={f + 1} i={i} k={Math.min(1, (s - l[0]) / 0.4, (l[1] - s) / 0.4)} />)}
    <div style={{position: 'absolute', bottom: 330, width: '100%', textAlign: 'center'}}>
      <div style={{font: '700 30px Montserrat', color: 'rgba(246,241,231,0.8)', letterSpacing: 10, textShadow: SH}}>COPENHAGEN</div>
      <div style={{font: '900 230px Montserrat', color: INK, textShadow: SH, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.floor(y)}</div>
    </div>
    <div style={{position: 'absolute', bottom: 210, width: '100%', textAlign: 'center', font: '900 28px Montserrat', letterSpacing: 10, color: INK, opacity: 0.8, textShadow: SH}}>YEAR BUILT</div>
  </AbsoluteFill>);
};
registerRoot(() => (<>{Object.entries(SHORTS).map(([id, c]) => <Composition key={id} id={`Short${id}`} component={Short} durationInFrames={c.n} fps={FPS} width={1080} height={1920} defaultProps={{id}} />)}</>));
