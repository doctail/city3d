// Short di Siviglia (Year Built): "La moschea che diventa cattedrale", tratto 0:24-0:54,5 del video lungo (1335 -> 1570, circa 8 anni al secondo).
// Tagliato dal lungo (regola di Fabio: gli Shorts si tagliano dal video lungo). Verticale 1080x1920: il 16:9 sta al centro sopra una copia sfocata
// di se stesso (nessun ritaglio, nessuna perdita di nitidezza); sopra la domanda, sotto l'anno. Overlay trasparente: la sfocatura e' nel .bat.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, OffthreadVideo, staticFile} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_sevilla.json';
const FPS = 24, T0 = 24, N = 732, F0 = T0 * FPS, INK = '#F6F1E7', ACC = '#E8B04A', SH = '0 3px 18px rgba(0,0,0,0.7), 0 0 3px rgba(0,0,0,0.8)';
// sub: [inizio s, fine s, testo, colore]  (tempi dello Short)
const SUB = [[1.5, 7.0, '1356 · EARTHQUAKE', ACC], [7.2, 12.4, '1434 · THE MOSQUE BECOMES A CATHEDRAL', ACC], [12.8, 25.6, 'EVERY BUILDING IN ITS REAL YEAR', INK], [26.1, 30.5, '1568 · THE GIRALDA GETS ITS BELFRY', ACC]];
const Short = ({bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = YEARS[String(F0 + f + 1)] ?? 1570;
  const sub = SUB.find((x) => s >= x[0] && s < x[1]); const ks = sub ? Math.min(1, (s - sub[0]) / 0.3, (sub[1] - s) / 0.3) : 0;
  return (<AbsoluteFill>
    {bg && <><OffthreadVideo src={staticFile('sevilla_light.mp4')} startFrom={F0} muted style={{position: 'absolute', width: 3414, height: 1920, left: -1167, top: 0, filter: 'blur(36px) brightness(0.55)'}} />
      <OffthreadVideo src={staticFile('sevilla_light.mp4')} startFrom={F0} muted style={{position: 'absolute', width: 1080, height: 608, left: 0, top: 656}} /></>}
    <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center'}}>
      <div style={{font: '900 80px Montserrat', color: INK, textShadow: SH, letterSpacing: 1, lineHeight: 1.06, padding: '0 56px'}}>WHAT HAPPENED TO SEVILLE'S MOSQUE?</div>
    </div>
    <div style={{position: 'absolute', top: 520, width: '100%', textAlign: 'center', padding: '0 40px', boxSizing: 'border-box', height: 100}}>
      {sub && <div style={{font: '700 34px Montserrat', color: sub[3], textShadow: SH, letterSpacing: 5, opacity: ks, lineHeight: 1.2}}>{sub[2]}</div>}
    </div>
    <div style={{position: 'absolute', top: 1310, width: '100%', textAlign: 'center'}}>
      <div style={{font: '700 30px Montserrat', color: 'rgba(246,241,231,0.85)', letterSpacing: 10, textShadow: SH}}>SEVILLE</div>
      <div style={{font: '900 250px Montserrat', color: INK, textShadow: SH, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>{Math.floor(y)}</div>
    </div>
    <div style={{position: 'absolute', bottom: 150, width: '100%', textAlign: 'center', font: '900 28px Montserrat', letterSpacing: 9, color: INK, opacity: 0.85, textShadow: SH}}>YEAR BUILT · FULL STORY ON OUR CHANNEL</div>
  </AbsoluteFill>);
};
registerRoot(() => (<>
  <Composition id="SevilleShort" component={Short} durationInFrames={N} fps={FPS} width={1080} height={1920} defaultProps={{bg: false}} />
  <Composition id="SevilleShortPreview" component={Short} durationInFrames={N} fps={FPS} width={1080} height={1920} defaultProps={{bg: true}} />
</>));
