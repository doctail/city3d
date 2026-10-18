// Livello grafico del video di Rotterdam (regole del 17-18 ott 2026 dall'analisi dei concorrenti):
//  - gancio scritto nei primi 15 s (contrasto: "porto piu' grande d'Europa" / "diga su un ruscello" / "1940")
//  - una scheda ogni ~15 s, titolo di 2-3 parole + una riga, a TEMPO (secondi), non ad anno
//  - etichette sui monumenti quando compaiono, con la stessa camera del render (labels_rotterdam.json da labels_cam.py)
// Reso trasparente (WebM VP9 con alfa) e sovrapposto al render con ffmpeg (monta_rotterdam.bat).
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, staticFile, OffthreadVideo} from 'remotion';
import {Hud} from './hud';
import {ROTTERDAM} from './cities';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_rotterdam.json';
import LABELS from '../public/labels_rotterdam.json';

const FPS = 24, N = 7839, INK = '#F6F1E7', ACC = '#E8B04A', GREY = '#cfd3d6', SH = '0 2px 14px rgba(0,0,0,0.6), 0 0 2px rgba(0,0,0,0.7)';
const yearAt = (f) => YEARS[String(Math.min(N, f + 1))] ?? 2026;
const T_TITLE = [0.3, 1.0, 4.6, 5.4], T_HUD = [5.6, 6.2, 317.0, 318.0], T_END = [318.6, 319.6];
const ramp = (s, [a, b, c, d]) => interpolate(s, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

// gancio: due battute grandi al centro, poi sparisce prima della prima scheda
const HOOK = [
  [5.8, 10.4, "EUROPE'S BIGGEST PORT", 'started as a dam on a muddy stream.'],
  [10.6, 15.2, 'IN 1940 IT LOST ITS HEART', 'in a single afternoon. Watch what came back.'],
];
// schede: [inizio s, fine s, anno, titolo, riga, sobria?, etichette da accendere]
export const CARDS = [
  [16.0, 21.5, '1340', 'Rotte + dam', 'A dam on a small river called the Rotte. Guess where the name comes from.'],
  [37.7, 43.0, '1572', 'Spanish soldiers', 'Troops let in through the gate kill townspeople. Rotterdam joins the Dutch Revolt.'],
  [44.0, 49.5, '1600', 'The Water Town', "New harbors are dug inside the walls. Ships moor at the merchants' front doors."],
  [50.5, 56.0, '1630', 'Golden Age', 'Rotterdam helps run the Dutch East India Company, the giant of its age.'],
  [58.5, 64.0, '1700', 'Two quiet centuries', 'For 200 years the city barely moves past its medieval walls.', false, ['Laurenskerk']],
  [73.8, 79.3, '1855', 'Out of the walls', 'The Water Project: canals, parks and new streets finally break out.'],
  [87.0, 92.5, '1872', 'A new way to the sea', 'A straight canal to the North Sea opens. Bigger ships can reach the city.'],
  [100.0, 105.5, '1878', 'The south bank', 'A bridge and a railway reach the far side of the river. Docks follow fast.'],
  [115.7, 121.2, '1898', "Europe's first skyscraper?", 'The White House: 43 meters, ten floors. Rotterdam still claims the title.', false, ['Witte Huis']],
  [133.3, 138.8, '1910', 'Waalhaven', 'Once the largest dug harbor basin in the world.'],
  [150.0, 155.5, '1920', 'City Hall', 'It opens on the Coolsingel. Remember it: it survives what is coming.', false, ['City Hall']],
  [165.0, 170.5, '1926', 'Van Nelle Factory', 'Coffee, tea and tobacco in a glass factory. Today a World Heritage Site.', false, ['Van Nelle Factory']],
  [189.0, 195.0, '1935', '620,000 people', 'Rotterdam on the eve of war: crowded, busy, built over six centuries.'],
  [207.6, 219.5, '14 MAY 1940', 'The center is gone', 'German bombers strike for 15 minutes. Around 850 people are killed and 80,000 lose their homes.', true],
  [222.0, 227.5, '1946', 'Start from scratch', 'The ruins are cleared. Rotterdam chooses not to rebuild the old city.'],
  [230.9, 236.4, '1953', 'The Lijnbaan', "One of Europe's first car-free shopping streets."],
  [241.7, 247.2, '1960', 'Euromast', 'Built for a garden show. It still has the best view in town.', false, ['Euromast']],
  [256.8, 262.3, '1968', 'Underground', 'The first metro line in the Netherlands opens here.'],
  [280.8, 286.3, '1984', 'Cube Houses', 'Piet Blom tilts houses 45 degrees. Residents learn to live with slanted walls.', false, ['Cube Houses']],
  [289.2, 294.7, '1991', 'Delftse Poort', '150 meters of glass: for years the tallest building in the Netherlands.', false, ['Delftse Poort']],
  [297.6, 303.1, '1998', 'Manhattan on the Maas', 'The old docks of the south bank turn into a forest of towers.', false, ['Maastoren']],
  [310.4, 315.6, '2013', 'De Rotterdam', "Three towers, one 'vertical city': the largest building in the Netherlands.", false, ['De Rotterdam']],
];
// etichette senza scheda: i sopravvissuti nel silenzio dopo il bombardamento
const EXTRA = [[212.5, 219.5, ['Laurenskerk', 'City Hall'], 'survived'], [315.9, 318.5, ['Zalmhaven'], '203 m, 2022']];

const Hook = ({s}) => { const h = HOOK.find((x) => s >= x[0] && s < x[1]); if (!h) return null;
  const k = Math.min(1, (s - h[0]) / 0.45, (h[1] - s) / 0.45);
  return (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 120, opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.42 * k}), rgba(10,10,12,0) 62%)`}}>
    <div style={{font: '900 92px Montserrat', color: INK, textShadow: SH, letterSpacing: 2, textAlign: 'center', transform: `translateY(${(1 - k) * 14}px)`}}>{h[2]}</div>
    <div style={{font: '700 46px Montserrat', color: ACC, textShadow: SH, marginTop: 14, textAlign: 'center'}}>{h[3]}</div>
  </AbsoluteFill>); };

const Card = ({s}) => { const ev = CARDS.find((e) => s >= e[0] && s < e[1]); if (!ev) return null;
  const k = Math.min(1, (s - ev[0]) / 0.5, (ev[1] - s) / 0.5); const quiet = !!ev[5]; const col = quiet ? GREY : ACC;
  return (<div style={{position: 'absolute', left: 80, top: 78, width: 700, opacity: k, transform: `translateX(${(1 - k) * -30}px)`, display: 'flex', gap: 22}}>
    <div style={{width: 6, borderRadius: 3, background: col}} />
    <div><div style={{font: '700 24px Montserrat', letterSpacing: 4, color: col, textShadow: SH}}>{ev[2]}</div>
      <div style={{font: '900 52px Montserrat', color: INK, textShadow: SH, lineHeight: 1.08, marginTop: 4}}>{ev[3]}</div>
      <div style={{font: '500 27px Montserrat', color: INK, textShadow: SH, lineHeight: 1.35, marginTop: 10, opacity: 0.94}}>{ev[4]}</div></div></div>); };

// etichetta: punto sul monumento, filo verticale e nome; solo se e' davanti alla camera e dentro il quadro
const Label = ({name, f, k, tag, i = 0}) => { const L = LABELS.lm[name]; if (!L) return null; const p = L.p[f - LABELS.F0]; if (!p) return null;
  const [x, y, z] = p; if (z <= 0 || x < 70 || x > 1850 || y < 230 || y > 900) return null;
  const up = (92 + 64 * i) * k;   // piu' etichette insieme: fili di altezza diversa
  return (<div style={{position: 'absolute', left: x, top: y, opacity: k}}>
    <div style={{position: 'absolute', left: -7, top: -7, width: 14, height: 14, borderRadius: 7, background: ACC, boxShadow: '0 0 0 3px rgba(0,0,0,0.45)'}} />
    <div style={{position: 'absolute', left: -1.5, top: -up, width: 3, height: up, background: 'rgba(246,241,231,0.9)', boxShadow: '0 0 6px rgba(0,0,0,0.6)'}} />
    <div style={{position: 'absolute', left: 0, top: -up - 52, transform: 'translateX(-50%)', whiteSpace: 'nowrap', padding: '8px 18px', borderRadius: 26, background: 'rgba(12,14,16,0.72)', font: '700 26px Montserrat', color: INK, letterSpacing: 1}}>
      {name}{tag && <span style={{color: ACC, fontWeight: 500}}> · {tag}</span>}</div>
  </div>); };
const Labels = ({s, f}) => { const on = [];
  for (const e of CARDS) if (e[6] && s >= e[0] + 0.4 && s < e[1]) e[6].forEach((n) => on.push([n, Math.min(1, (s - e[0] - 0.4) / 0.5, (e[1] - s) / 0.5), null]));
  for (const e of EXTRA) if (s >= e[0] && s < e[1]) e[2].forEach((n) => on.push([n, Math.min(1, (s - e[0]) / 0.5, (e[1] - s) / 0.5), e[3]]));
  return <>{on.map(([n, k, t], i) => <Label key={n} name={n} f={f} k={k} tag={t} i={i} />)}</>; };

const Title = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.45 * k}), rgba(10,10,12,0) 65%)`}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>EVERY BUILDING IN ITS REAL YEAR</div>
  <div style={{font: '900 200px Montserrat', color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05, transform: `scale(${0.96 + 0.04 * k})`}}>ROTTERDAM</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />1340 · 2026<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const End = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.55 * k}), rgba(10,10,12,0.15) 75%)`}}>
  <div style={{font: '700 24px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>EVERY REAL BUILDING · 686 YEARS</div>
  <div style={{font: '900 120px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, lineHeight: 1.1, marginTop: 10}}>WHICH CITY NEXT?</div>
  <div style={{font: '500 34px Montserrat', color: INK, textShadow: SH, marginTop: 18, opacity: 0.9}}>Tell us in the comments</div>
  <div style={{position: 'absolute', bottom: 70, font: '900 30px Montserrat', letterSpacing: 10, color: INK, textShadow: SH, opacity: 0.85}}>YEAR BUILT</div>
</AbsoluteFill>);

export const Overlay = ({bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAt(f);
  const kt = ramp(s, T_TITLE), kh = ramp(s, T_HUD), ke = interpolate(s, T_END, [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile('rotterdam_light.mp4')} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud year={y} city={ROTTERDAM} /></AbsoluteFill>}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Labels s={s} f={f + 1} /><Card s={s} /></AbsoluteFill>}
    <Hook s={s} />
    {kt > 0 && <Title k={kt} />}
    {ke > 0 && <End k={ke} />}
  </AbsoluteFill>);
};
registerRoot(() => (<>
  <Composition id="RotterdamOverlay" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: false}} />
  <Composition id="RotterdamPreview" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: true}} />
</>));
