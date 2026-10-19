// Livello grafico del video di Copenaghen (19 ott 2026). Regole: gancio scritto nei primi 15 s, una scheda ogni ~10-15 s
// (titolo di 2-3 parole + una riga), etichette agganciate ai monumenti con la stessa camera del render
// (labels_copenhagen.json da labels_cam.py), contatori sugli incendi, schede sobrie (grigie) per peste, occupazione, 1945.
// Tempi in secondi, presi dalla regia (schedule_copenhagen.json -> soste). Testi in inglese americano. Numeri verificati
// (Wikipedia, 19 ott 2026): 1728 ~1.600 edifici, 28% della citta', 15.000 senza casa; 1795: 909 case, 6.000 senza casa;
// 1807: 2-5 settembre, ~195 civili uccisi, 300 razzi Congreve; 1711 peste ~1/3 degli abitanti; Shellhus 21 marzo 1945: 86 bambini.
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, staticFile, OffthreadVideo} from 'remotion';
import {Hud} from './hud';
import {COPENHAGEN} from './cities';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';
import YEARS from '../public/years_copenhagen.json';
import LABELS from '../public/labels_copenhagen.json';
import BLD from '../public/buildings_copenhagen.json';

const FPS = 24, N = 12276, INK = '#F6F1E7', ACC = '#E8B04A', GREY = '#cfd3d6', FIRE = '#FF8A3D', SH = '0 2px 14px rgba(0,0,0,0.6), 0 0 2px rgba(0,0,0,0.7)';
const yearAt = (f) => YEARS[String(Math.min(N, f + 1))] ?? 2026;
const T_TITLE = [3.2, 4.0, 8.4, 9.2], T_HUD = [15.4, 16.2, 497.5, 499.0], T_END = [499.5, 500.6];
const ramp = (s, [a, b, c, d]) => interpolate(s, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

// gancio (durante la sosta sul castello di Absalon)
const HOOK = [
  [9.6, 12.5, 'IT BURNED DOWN TWICE', 'and was shelled by the British fleet.'],
  [12.6, 15.4, '850 YEARS', 'Every building in its real year.'],
];
// schede: [inizio s, fine s, data, titolo, riga, tipo ('' | 'quiet' | 'fire'), etichette]
export const CARDS = [
  [15.8, 21.6, '1167', "Bishop Absalon's castle", 'A fortress on a tiny island guards a fishing village called Havn: "harbor".', '', ["Absalon's Castle"]],
  [30.0, 35.6, '1254', 'A real town', 'Havn gets its town charter. Merchants start calling it "the merchants\' harbor".'],
  [44.0, 49.6, '1300s', 'København', 'Køpmannæhafn, the merchants\' harbor, slowly becomes the city\'s name.'],
  [61.8, 67.4, '1369', 'Castle destroyed', 'The Hanseatic League tears down Absalon\'s castle. A new one soon rises.', '', ["Absalon's Castle"]],
  [78.6, 84.2, '1443', 'Capital of Denmark', 'The king settles here for good. Copenhagen has ruled Denmark ever since.'],
  [92.6, 98.2, '1536', 'The Reformation', 'Denmark turns Lutheran. Church lands pass to the crown.'],
  [103.2, 108.6, '1606', 'Rosenborg Castle', 'Christian IV builds a summer house just outside the walls.', '', ['Rosenborg Castle']],
  [110.0, 115.8, '1619', 'Børsen', 'A stock exchange crowned by four dragons with their tails twisted into a spire.', '', ['Børsen']],
  [118.9, 124.3, '1637', 'The Round Tower', 'An observatory with no stairs: a spiral ramp wide enough for a horse.', '', ['Rundetårn']],
  [133.6, 139.2, '1659', 'The Swedish assault', 'Swedish troops storm the walls at night. The city holds.'],
  [146.1, 151.4, '1671', 'Nyhavn', 'A new canal brings ships right into the heart of the city.', '', ['Nyhavn']],
  [168.6, 174.2, '1711', 'The plague', 'About a third of the people in the city die in a single year.', 'quiet'],
  [184.2, 194.2, '20 OCTOBER 1728', 'The Great Fire', 'Three days of flames. 28% of the city burns and 15,000 people lose their homes.', 'fire'],
  [207.0, 212.0, '1733', 'Christiansborg', 'A new royal palace rises on Absalon\'s island.', '', ['Christiansborg']],
  [215.1, 219.4, '1752', 'A golden spiral', '400 steps up the spire of Our Saviour\'s Church, the last 150 outside.', '', ['Church of Our Saviour']],
  [219.6, 225.6, '1750s', 'Frederiksstaden', 'A new royal district: four palaces around one octagonal square.', '', ['Amalienborg Palace']],
  [227.6, 233.2, '1770', 'Left unfinished', 'Too expensive: the Marble Church stands as a ruin for over 100 years.', '', ['Marble Church']],
  [235.0, 238.6, '1794', 'The palace burns', 'Christiansborg burns down.', 'fire', ['Christiansborg']],
  [238.9, 244.8, 'JUNE 1795', 'The second fire', '909 houses burn. 6,000 people lose their homes.', 'fire'],
  [248.0, 262.0, '2-5 SEPTEMBER 1807', 'British bombardment', 'The Royal Navy shells the city for three nights. About 195 civilians are killed.', 'quiet'],
  [262.5, 267.6, '1803–1828', 'Christiansborg II', 'The palace is rebuilt in a sober classical style.', '', ['Christiansborg']],
  [277.6, 282.2, '1843', 'Tivoli Gardens', 'An amusement park opens just outside the city gate. It is still there.', '', ['Tivoli Gardens']],
  [285.0, 290.6, '1852', 'The walls come down', 'For the first time in centuries, the city may build beyond its ramparts.'],
  [296.0, 301.6, '1870s', 'The bridge quarters', 'Nørrebro, Vesterbro, Østerbro. The population triples in 50 years.'],
  [312.9, 317.4, '1877', 'Work restarts', 'After a century as a ruin, the Marble Church is finished.', '', ['Marble Church']],
  [318.5, 322.6, '1884', 'It burns again', 'Christiansborg burns for the second time.', 'fire', ['Christiansborg']],
  [324.1, 329.6, '1894', 'The dome', 'One of the largest church domes in Scandinavia.', '', ['Marble Church']],
  [330.8, 336.2, '1905', 'City Hall', 'Its clock tower rises 105.6 meters over the new square.', '', ['City Hall']],
  [347.0, 352.6, '1913', 'The Little Mermaid', 'Too small to see from up here. This is where she sits.', '', ['The Little Mermaid']],
  [359.8, 365.0, '1907–1928', 'Christiansborg III', 'The third palace gets the tallest tower in town: 106 meters.', '', ['Christiansborg']],
  [365.8, 371.0, '1921–1940', 'Grundtvig Church', 'Yellow brick, built to look like a giant church organ.', '', ['Grundtvig Church']],
  [382.0, 388.0, '9 APRIL 1940', 'Occupation', 'German troops occupy Denmark. The city is spared heavy bombing.', 'quiet'],
  [390.8, 394.8, '21 MARCH 1945', 'The Shellhus raid', 'An RAF raid on Gestapo headquarters also hits a school. 86 children are killed.', 'quiet'],
  [404.8, 409.4, '1960', 'SAS Royal Hotel', 'Arne Jacobsen\'s hotel: Denmark\'s first skyscraper.', '', ['SAS Royal Hotel']],
  [419.0, 424.6, '1971', 'Christiania', 'Squatters take over an old military base and declare a free town.'],
  [428.0, 433.6, '1990s', 'Back to the harbor', 'Old docks turn into homes, offices and harbor baths.'],
  [435.8, 440.8, '1 JULY 2000', 'The Øresund Bridge', '16 km of bridge and tunnel to Sweden. Malmö is now a commute away.', '', ['Øresund Bridge']],
  [440.9, 444.9, '2005', 'The Opera House', 'A gift to the nation from the Mærsk shipping family.', '', ['Opera House']],
  [445.0, 449.0, '2008', 'The Royal Playhouse', 'A theater built out over the water.', '', ['Royal Playhouse']],
  [452.3, 457.4, '2019', 'CopenHill', 'A power plant with a ski slope on its roof.', '', ['CopenHill']],
  [470.5, 477.0, 'TODAY', 'Copenhagen', 'About 670,000 people live in the city. Tivoli is still lit up every night.', '', ['Tivoli Gardens']],
];
// contatori sulle schede degli incendi: [inizio, fine, etichetta, valore, prefisso]
const COUNTERS = [[184.4, 194.2, 'BUILDINGS LOST', 1600, '~'], [238.9, 244.8, 'HOUSES BURNED', 909, ''], [248.2, 262.0, 'CIVILIANS KILLED', 195, '~']];

const Hook = ({s}) => { const h = HOOK.find((x) => s >= x[0] && s < x[1]); if (!h) return null;
  const k = Math.min(1, (s - h[0]) / 0.45, (h[1] - s) / 0.45);
  return (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 120, opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.42 * k}), rgba(10,10,12,0) 62%)`}}>
    <div style={{font: '900 96px Montserrat', color: INK, textShadow: SH, letterSpacing: 2, textAlign: 'center', transform: `translateY(${(1 - k) * 14}px)`}}>{h[2]}</div>
    <div style={{font: '700 46px Montserrat', color: ACC, textShadow: SH, marginTop: 14, textAlign: 'center'}}>{h[3]}</div>
  </AbsoluteFill>); };

const Card = ({s}) => { const ev = CARDS.find((e) => s >= e[0] && s < e[1]); if (!ev) return null;
  const k = Math.min(1, (s - ev[0]) / 0.5, (ev[1] - s) / 0.5); const col = ev[5] === 'quiet' ? GREY : ev[5] === 'fire' ? FIRE : ACC;
  return (<div style={{position: 'absolute', left: 80, top: 78, width: 720, opacity: k, transform: `translateX(${(1 - k) * -30}px)`, display: 'flex', gap: 22}}>
    <div style={{width: 6, borderRadius: 3, background: col}} />
    <div><div style={{font: '700 24px Montserrat', letterSpacing: 4, color: col, textShadow: SH}}>{ev[2]}</div>
      <div style={{font: '900 52px Montserrat', color: INK, textShadow: SH, lineHeight: 1.08, marginTop: 4}}>{ev[3]}</div>
      <div style={{font: '500 27px Montserrat', color: INK, textShadow: SH, lineHeight: 1.35, marginTop: 10, opacity: 0.94}}>{ev[4]}</div></div></div>); };

const Count = ({s}) => { const c = COUNTERS.find((x) => s >= x[0] && s < x[1]); if (!c) return null;
  const u = Math.max(0, Math.min(1, (s - c[0]) / 3.2)); const n = Math.round(c[3] * (1 - Math.pow(1 - u, 3)));
  return (<div style={{position: 'absolute', left: 108, top: 330, opacity: Math.min(1, (s - c[0]) / 0.5, (c[1] - s) / 0.5)}}>
    <div style={{font: '700 20px Montserrat', letterSpacing: 4, color: GREY, textShadow: SH}}>{c[2]}</div>
    <div style={{font: '900 64px Montserrat', color: INK, textShadow: SH, fontVariantNumeric: 'tabular-nums'}}>{c[4]}{n.toLocaleString('en-US')}</div></div>); };

// etichetta: punto sul monumento, filo verticale e nome; solo se e' davanti alla camera e dentro il quadro
const Label = ({name, f, k, i = 0}) => { const L = LABELS.lm[name]; if (!L) return null; const p = L.p[f - LABELS.F0]; if (!p) return null;
  const [x, y, z] = p; if (z <= 0 || x < 70 || x > 1850 || y < 260 || y > 900) return null;
  const up = (92 + 64 * i) * k;
  return (<div style={{position: 'absolute', left: x, top: y, opacity: k}}>
    <div style={{position: 'absolute', left: -7, top: -7, width: 14, height: 14, borderRadius: 7, background: ACC, boxShadow: '0 0 0 3px rgba(0,0,0,0.45)'}} />
    <div style={{position: 'absolute', left: -1.5, top: -up, width: 3, height: up, background: 'rgba(246,241,231,0.9)', boxShadow: '0 0 6px rgba(0,0,0,0.6)'}} />
    <div style={{position: 'absolute', left: 0, top: -up - 52, transform: 'translateX(-50%)', whiteSpace: 'nowrap', padding: '8px 18px', borderRadius: 26, background: 'rgba(12,14,16,0.72)', font: '700 26px Montserrat', color: INK, letterSpacing: 1}}>{name}</div>
  </div>); };
const Labels = ({s, f}) => { const on = [];
  for (const e of CARDS) if (e[6] && s >= e[0] + 0.4 && s < e[1]) e[6].forEach((n) => on.push([n, Math.min(1, (s - e[0] - 0.4) / 0.5, (e[1] - s) / 0.5)]));
  return <>{on.map(([n, k], i) => <Label key={n} name={n} f={f} k={k} i={i} />)}</>; };

const bldAt = (y) => { const i = Math.max(0, Math.min(BLD.n.length - 2, Math.floor(y) - BLD.Y0)); const u = Math.max(0, Math.min(1, y - BLD.Y0 - i)); return Math.round(BLD.n[i] + (BLD.n[i + 1] - BLD.n[i]) * u); };
const Counter = ({y}) => (<div style={{position: 'absolute', right: 80, top: 78, textAlign: 'right'}}>
  <div style={{font: '700 18px Montserrat', letterSpacing: 4, color: 'rgba(246,241,231,0.75)', textShadow: SH}}>BUILDINGS STANDING</div>
  <div style={{font: '900 54px Montserrat', color: INK, textShadow: SH, fontVariantNumeric: 'tabular-nums'}}>{bldAt(y).toLocaleString('en-US')}</div></div>);

// apertura: anno grande in alto che corre all'indietro (2026 -> 1167) durante il riavvolgimento
const Rewind = ({s, y}) => { if (s > 9.6) return null; const k = Math.min(1, s / 0.4, (9.6 - s) / 0.4);
  return (<div style={{position: 'absolute', left: 0, right: 0, top: 70, textAlign: 'center', opacity: k}}>
    <div style={{font: '900 120px Montserrat', color: INK, textShadow: SH, fontVariantNumeric: 'tabular-nums', letterSpacing: 2}}>{Math.floor(y)}</div>
    {s < 3.0 && <div style={{font: '700 26px Montserrat', letterSpacing: 8, color: ACC, textShadow: SH}}>COPENHAGEN TODAY</div>}</div>); };

const Title = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.45 * k}), rgba(10,10,12,0) 65%)`}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>3D TIMELAPSE · EVERY REAL BUILDING</div>
  <div style={{font: '900 190px Montserrat', color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05, transform: `scale(${0.96 + 0.04 * k})`}}>COPENHAGEN</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />1167 TO NOW<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const End = ({k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.55 * k}), rgba(10,10,12,0.15) 75%)`}}>
  <div style={{font: '700 24px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>EVERY REAL BUILDING · 859 YEARS</div>
  <div style={{font: '900 120px Montserrat', color: INK, textShadow: SH, letterSpacing: 4, lineHeight: 1.1, marginTop: 10}}>WHICH CITY NEXT?</div>
  <div style={{font: '500 34px Montserrat', color: INK, textShadow: SH, marginTop: 18, opacity: 0.9}}>Tell us in the comments</div>
  <div style={{position: 'absolute', bottom: 70, font: '900 30px Montserrat', letterSpacing: 10, color: INK, textShadow: SH, opacity: 0.85}}>YEAR BUILT</div>
</AbsoluteFill>);

export const Overlay = ({bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAt(f);
  const kt = ramp(s, T_TITLE), kh = ramp(s, T_HUD), ke = interpolate(s, T_END, [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile('copenhagen_light.mp4')} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud year={y} city={COPENHAGEN} /></AbsoluteFill>}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Labels s={s} f={f + 1} /><Card s={s} /><Count s={s} /><Counter y={y} /></AbsoluteFill>}
    <Rewind s={s} y={y} />
    <Hook s={s} />
    {kt > 0 && <Title k={kt} />}
    {ke > 0 && <End k={ke} />}
  </AbsoluteFill>);
};
registerRoot(() => (<>
  <Composition id="CopenhagenOverlay" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: false}} />
  <Composition id="CopenhagenPreview" component={Overlay} durationInFrames={N} fps={FPS} width={1920} height={1080} defaultProps={{bg: true}} />
</>));
