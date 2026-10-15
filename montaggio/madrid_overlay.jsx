// Livello grafico del video di Madrid: titolo, HUD (anno, epoca, popolazione, timeline, eventi), finale.
// Reso con sfondo trasparente (WebM VP9 con alfa) e poi sovrapposto al render 3D con ffmpeg.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, staticFile, Img, OffthreadVideo} from 'remotion';
import {Hud} from './hud';
import {MADRID} from './cities';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_madrid.json';

const FPS = 24, N = 7839, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 2px 14px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.6)';
const yearAt = (f) => YEARS[String(Math.min(N, f + 1))] ?? 2026;
const T_TITLE = [0.4, 1.2, 4.2, 5.2], T_HUD = [5.4, 6.0, 317.0, 318.0], T_END = [318.6, 319.6];
const ramp = (s, [a, b, c, d]) => interpolate(s, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

const Title = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.45 * k}), rgba(10,10,12,0) 65%)`}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>EVERY BUILDING IN ITS REAL YEAR</div>
  <div style={{font: '900 210px Montserrat', color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05, transform: `scale(${0.96 + 0.04 * k})`}}>MADRID</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />1480 · 2026<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const End = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.55 * k}), rgba(10,10,12,0.15) 75%)`}}>
  <div style={{font: '700 24px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>120,964 BUILDINGS · 546 YEARS</div>
  <div style={{font: '900 120px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, lineHeight: 1.1, marginTop: 10}}>WHICH CITY NEXT?</div>
  <div style={{font: '500 34px Montserrat', color: INK, textShadow: SH, marginTop: 18, opacity: 0.9}}>Tell us in the comments</div>
  <div style={{position: 'absolute', bottom: 70, font: '900 30px Montserrat', letterSpacing: 10, color: INK, textShadow: SH, opacity: 0.85}}>YEAR BUILT</div>
</AbsoluteFill>);

export const Overlay = ({bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAt(f);
  const kt = ramp(s, T_TITLE), kh = ramp(s, T_HUD), ke = interpolate(s, T_END, [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile('madrid_light.mp4')} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud year={y} city={MADRID} /></AbsoluteFill>}
    {kt > 0 && <Title k={kt} />}
    {ke > 0 && <End k={ke} />}
  </AbsoluteFill>);
};
registerRoot(() => (<>
  <Composition id="MadridOverlay" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: false}} />
  <Composition id="MadridPreview" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: true}} />
</>));
