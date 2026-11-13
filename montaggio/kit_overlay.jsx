// Kit Year Built: UN solo livello grafico Remotion per tutte le citta' (generalizza roma_overlay.jsx).
// Legge tutto da public/kit_<slug>.json (generato da kit_city.py) e dai 4 json collegati (years, eventi, labels, labs).
// Composizioni: KitOverlay (trasparente 1920x1080), KitPreview (con video public/<slug>_light.mp4), KitShort (1080x1920).
// Selezione della citta': inputProps {"slug":"roma"}  (npx remotion render kit_overlay.jsx KitOverlay out.webm --props='{"slug":"roma"}')
// oppure variabile d'ambiente REMOTION_KIT_SLUG. Stile identico a Roma (Montserrat, INK, ACC).
import React from 'react';
import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, staticFile, OffthreadVideo} from 'remotion';
import '@fontsource/montserrat/500.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/900.css';

const FPS = 24, INK = '#F6F1E7', ACC = '#E8B04A', GREY = '#cfd3d6', SH = '0 2px 14px rgba(0,0,0,0.6), 0 0 2px rgba(0,0,0,0.7)';
const ramp = (s, [a, b, c, d]) => interpolate(s, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const clampI = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const yearLabel = (y) => { const v = Math.floor(y); return v < 0 ? `${-v} BC` : (v < 1000 ? `AD ${v}` : `${v}`); };

// ---- elementi opzionali del pacing "story" (cartelli, capitoli, polity, fonte popolazione, recap, CTA, fonti): tutto assente = nessun cambiamento ----
const BOX = 'rgba(12,14,16,0.72)';
const popLabelAt = (C, y) => { const P = C.POPSRC; if (!P) return null; let r = null; for (const [a, l] of P) if (a <= y) r = l; return r; };
const polityAt = (C, y) => { const P = C.POLITIES; if (!P) return null; let r = null; for (const q of P) if (q[0] <= y) r = q; return r; };
const win = (e, s, fade = 0.5) => (e && s >= e.t_in && s < e.t_out ? Math.min(1, (s - e.t_in) / fade, (e.t_out - s) / fade) : 0);
const find = (list, s) => (list || []).find((e) => s >= e.t_in && s < e.t_out);

// cartello: riquadro scuro traslucido, "ANNO · Titolo" oro, 1-2 righe bianche (alto a sinistra)
const Card = ({e, k}) => (<div style={{position: 'absolute', left: 80, top: 78, width: 780, opacity: k, transform: `translateY(${(1 - k) * -14}px)`}}>
  <div style={{padding: '22px 30px 24px', borderRadius: 16, background: BOX, borderLeft: `6px solid ${e.sober ? GREY : ACC}`, boxShadow: '0 6px 30px rgba(0,0,0,0.35)'}}>
    <div style={{font: '900 40px Montserrat', color: e.sober ? GREY : ACC, textShadow: SH, lineHeight: 1.12}}>{e.date} <span style={{opacity: 0.8}}>·</span> {e.title}</div>
    {e.lines.map((l, i) => <div key={i} style={{font: '500 29px Montserrat', color: INK, lineHeight: 1.34, marginTop: i ? 4 : 12}}>{l}</div>)}
  </div></div>);

// stile "mattia" (cfg.style): una sola riga di contesto, tagliata pulita a fine frase (o al clausola) se piu' lunga di ~96 caratteri
const oneLine = (t) => { t = String(t || '').trim(); if (t.length <= 96) return t;
  const ends = [...t.matchAll(/[.!?](?=\s+[A-Z])/g)].map((m) => m.index + 1).filter((i) => i <= 125); if (ends.length) return t.slice(0, ends[ends.length - 1]);
  if (t.length <= 125) return t;
  const cl = [...t.matchAll(/[,;]\s/g)].map((m) => m.index).filter((i) => i >= 45 && i <= 110); return cl.length ? t.slice(0, cl[cl.length - 1]) + '.' : t.slice(0, t.lastIndexOf(' ', 110)) + '...'; };
// cartello compatto: in basso al centro, sopra la timeline; max 900 px; titolo oro 30 px + una riga 22 px
const CardM = ({e, k}) => (<div style={{position: 'absolute', left: 0, right: 0, bottom: 96, display: 'flex', justifyContent: 'center', opacity: k, transform: `translateY(${(1 - k) * 8}px)`}}>
  <div style={{maxWidth: 900, boxSizing: 'border-box', padding: '12px 28px 14px', borderRadius: 12, background: 'rgba(12,14,16,0.84)', borderLeft: `5px solid ${e.sober ? GREY : ACC}`, boxShadow: '0 4px 22px rgba(0,0,0,0.35)', textAlign: 'left'}}>
    <div style={{font: '900 30px Montserrat', color: e.sober ? GREY : ACC, lineHeight: 1.15}}>{e.date} <span style={{opacity: 0.8}}>·</span> {e.title}</div>
    {e.lines && e.lines.length ? <div style={{font: '500 22px Montserrat', color: INK, lineHeight: 1.3, marginTop: 6}}>{oneLine(e.lines[0])}</div> : null}
  </div></div>);

const Chapter = ({e, k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.62 * k}), rgba(10,10,12,0.12) 78%)`, paddingBottom: 60}}>
  <div style={{font: '700 30px Montserrat', letterSpacing: 14, color: ACC, textShadow: SH}}>CHAPTER {e.num}</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 28, marginTop: 14, transform: `scale(${0.97 + 0.03 * k})`}}>
    <span style={{width: 110, height: 2, background: ACC}} />
    <div style={{font: `900 ${fitSize(e.title.toUpperCase(), 1500, 110, 6)}px Montserrat`, color: INK, textShadow: SH, letterSpacing: 6, whiteSpace: 'nowrap'}}>{e.title.toUpperCase()}</div>
    <span style={{width: 110, height: 2, background: ACC}} />
  </div></AbsoluteFill>);

const PolityChip = ({C, year}) => { const q = polityAt(C, year); if (!q) return null; const cols = q[2] && q[2].length ? q[2] : ['#888'];
  return (<div style={{position: 'absolute', left: 80, bottom: 300, display: 'inline-flex', alignItems: 'center', gap: 14, padding: '10px 22px 10px 12px', borderRadius: 10, background: BOX}}>
    <div style={{width: 54, height: 36, borderRadius: 4, overflow: 'hidden', display: 'flex', flexDirection: 'column', boxShadow: '0 0 0 2px rgba(255,255,255,0.35)'}}>{cols.map((c, i) => <div key={i} style={{flex: 1, background: c}} />)}</div>
    <div style={{font: '700 24px Montserrat', letterSpacing: 2, color: INK}}>{q[1]}</div></div>); };

// stile "mattia": polity e era sulla stessa riga
const HudLine = ({C, year, era}) => { const q = polityAt(C, year); const cols = q ? (q[2] && q[2].length ? q[2] : ['#888']) : null; const dup = q && q[1].toLowerCase().includes(era[1].toLowerCase());
  return (<div style={{position: 'absolute', left: 80, bottom: 206, display: 'inline-flex', alignItems: 'center', gap: 12, padding: '7px 18px 7px 10px', borderRadius: 9, background: BOX}}>
    {q ? <div style={{width: 40, height: 26, borderRadius: 3, overflow: 'hidden', display: 'flex', flexDirection: 'column', boxShadow: '0 0 0 2px rgba(255,255,255,0.35)'}}>{cols.map((c, i) => <div key={i} style={{flex: 1, background: c}} />)}</div> : null}
    {q ? <div style={{font: '700 20px Montserrat', letterSpacing: 1.5, color: INK}}>{q[1]}</div> : null}
    {q && !dup ? <span style={{width: 1, height: 20, background: 'rgba(246,241,231,0.4)'}} /> : null}
    {!dup ? <span style={{width: 11, height: 11, borderRadius: 6, background: era[2]}} /> : null}
    {!dup ? <div style={{font: '700 16px Montserrat', letterSpacing: 4, textTransform: 'uppercase', color: 'rgba(246,241,231,0.85)'}}>{era[1]}</div> : null}
  </div>); };

const Reconstruction = ({C, year, M}) => (C.RELIABLE_FROM != null && year < C.RELIABLE_FROM ? (<div style={{position: 'absolute', left: 0, right: 0, top: M ? 28 : 36, textAlign: 'center'}}>
  <span style={M ? {display: 'inline-block', padding: '4px 16px', borderRadius: 20, background: BOX, border: `1px solid ${ACC}`, font: '700 14px Montserrat', letterSpacing: 4, color: ACC} : {display: 'inline-block', padding: '8px 22px', borderRadius: 24, background: BOX, border: `1px solid ${ACC}`, font: '700 20px Montserrat', letterSpacing: 6, color: ACC}}>RECONSTRUCTION · APPROXIMATE</span></div>) : null);

const Recap = ({e, k}) => (<div style={{position: 'absolute', left: 0, right: 0, top: 70, textAlign: 'center', opacity: k}}>
  <div style={{display: 'inline-block', padding: '18px 44px', borderRadius: 16, background: BOX, borderBottom: `4px solid ${ACC}`}}>
    <div style={{font: `900 ${fitSize(e.text.toUpperCase(), 1500, 50, 4)}px Montserrat`, color: ACC, textShadow: SH, letterSpacing: 4}}>{e.text.toUpperCase()}</div></div></div>);

const Cta = ({e, k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.6 * k}), rgba(10,10,12,0.15) 78%)`}}>
  <div style={{font: `900 ${fitSize(e.text, 1700, 84, 3)}px Montserrat`, color: INK, textShadow: SH, textAlign: 'center', padding: '0 80px', lineHeight: 1.15, textWrap: 'balance'}}>{e.text}</div></AbsoluteFill>);

const SourcesCard = ({e, k, brand}) => { const n = Math.ceil(e.items.length / 2), cols = [e.items.slice(0, n), e.items.slice(n)];
  return (<AbsoluteFill style={{opacity: k, background: `rgba(10,10,12,${0.88 * k})`, alignItems: 'center', justifyContent: 'center'}}>
    <div style={{font: '700 28px Montserrat', letterSpacing: 14, color: ACC}}>SOURCES</div>
    <div style={{display: 'flex', gap: 60, margin: '30px 90px 0', alignItems: 'flex-start'}}>{cols.map((c, ci) => <div key={ci} style={{width: 790}}>{c.map((t, i) => <div key={i} style={{font: '500 22px Montserrat', color: INK, lineHeight: 1.42, opacity: 0.92, marginBottom: 6}}>· {t}</div>)}</div>)}</div>
    <div style={{marginTop: 38, padding: '12px 34px', borderRadius: 14, border: `2px solid ${ACC}`, font: '900 30px Montserrat', letterSpacing: 4, color: ACC}}>{e.no_ai}</div>
    <div style={{position: 'absolute', bottom: 56, font: '900 26px Montserrat', letterSpacing: 10, color: INK, opacity: 0.8}}>{brand}</div>
  </AbsoluteFill>); };

// ---- dati della citta' (tutto da cfg) ----
const popAt = (C, y) => { const P = C.POP; for (let i = 1; i < P.length; i++) if (y <= P[i][0]) { const [a, pa] = P[i - 1], [b, pb] = P[i]; const t = (y - a) / (b - a); return Math.exp(Math.log(pa) + (Math.log(pb) - Math.log(pa)) * t); } return P[P.length - 1][1]; };
const eraAt = (C, y) => [...C.ERAS].reverse().find((e) => y >= e[0]) || C.ERAS[0];
const fmtPop = (p) => { const q = p > 1e4 ? 100 : 10; return Math.round(p / q) * q; };
const fitSize = (text, width, max, ls = 6) => Math.min(max, Math.floor((width / Math.max(1, text.length) - ls) / 0.8));

const Spark = ({C, year, w = 360, h = 84}) => { const {Y0, Y1} = C; const top = Math.log10(C.POPMAX); const lx = (y) => ((y - Y0) / (Y1 - Y0)) * w; const ly = (p) => h - (Math.log10(Math.max(p, 10)) - 1) / (top - 1) * h;
  const pts = []; for (let y = Y0; y <= year; y += 2) pts.push(`${lx(y).toFixed(1)},${ly(popAt(C, y)).toFixed(1)}`); pts.push(`${lx(year)},${ly(popAt(C, year))}`);
  return (<svg width={w} height={h + 6} style={{overflow: 'visible'}}>
    {[2, 3, 4, 5].map((e) => <line key={e} x1={0} x2={w} y1={ly(10 ** e)} y2={ly(10 ** e)} stroke="rgba(246,241,231,0.14)" strokeWidth={1} />)}
    <polyline points={`0,${h} ${pts.join(' ')} ${lx(year)},${h}`} fill="rgba(232,176,74,0.16)" stroke="none" />
    <polyline points={pts.join(' ')} fill="none" stroke={ACC} strokeWidth={3} strokeLinejoin="round" />
    <circle cx={lx(year)} cy={ly(popAt(C, year))} r={6} fill={ACC} stroke="#1b1b1b" strokeWidth={1.5} /></svg>); };

const Timeline = ({C, year}) => { const {Y0, Y1, ERAS} = C; const W = 1760; const x = (y) => ((y - Y0) / (Y1 - Y0)) * W;
  return (<div style={{position: 'absolute', left: 80, bottom: 46, width: W, height: 26}}>
    {ERAS.map((e, i) => { const a = x(e[0]), b = x(i + 1 < ERAS.length ? ERAS[i + 1][0] : Y1); const on = year >= e[0];
      return <div key={i} style={{position: 'absolute', left: a, width: b - a - 3, top: 10, height: 6, background: e[2], opacity: on ? 0.95 : 0.25, borderRadius: 3}} />; })}
    {C.TICKS.map((y) => <div key={y} style={{position: 'absolute', left: x(y) - 40, width: 80, top: 22, textAlign: 'center', font: '500 15px Montserrat', color: 'rgba(246,241,231,0.7)', textShadow: SH}}>{y < 0 ? `${-y} BC` : y}</div>)}
    <div style={{position: 'absolute', left: x(year) - 2, top: -6, width: 4, height: 30, background: INK, borderRadius: 2, boxShadow: '0 0 12px rgba(255,255,255,0.8)'}} />
  </div>); };

const Hud = ({C, year, M}) => { const era = eraAt(C, year); const p = popAt(C, year); const est = year < C.EST_UNTIL || year > 2022;
  return (<AbsoluteFill>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 420, background: 'linear-gradient(0deg, rgba(10,10,12,0.62), rgba(10,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 900, height: 420, background: 'radial-gradient(ellipse at 0% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', right: 0, top: 0, width: 700, height: 340, background: 'radial-gradient(ellipse at 100% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', left: 80, bottom: 104}}>
      {M ? null : <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, font: '700 22px Montserrat', letterSpacing: 5, textTransform: 'uppercase', color: INK, textShadow: SH}}><span style={{width: 14, height: 14, borderRadius: 7, background: era[2], boxShadow: '0 0 0 3px rgba(0,0,0,0.35)'}} />{era[1]}</div>}
      <div style={{font: `900 ${M ? 98 : 150}px Montserrat`, color: INK, textShadow: SH, lineHeight: 0.95, fontVariantNumeric: 'tabular-nums', letterSpacing: -2}}>{yearLabel(year)}</div>
    </div>
    <div style={{position: 'absolute', right: 80, top: M ? 66 : 78, textAlign: 'right'}}>
      <div style={{font: `700 ${M ? 15 : 18}px Montserrat`, letterSpacing: M ? 3 : 4, color: 'rgba(246,241,231,0.75)', textShadow: SH}}>POPULATION <span style={{opacity: 0.7, letterSpacing: 2}}>· {C.popLabel}</span></div>
      <div style={{font: `900 ${M ? 42 : 52}px Montserrat`, color: ACC, textShadow: SH, fontVariantNumeric: 'tabular-nums', margin: M ? '2px 0 8px' : '2px 0 10px'}}>{est ? '~' : ''}{fmtPop(p).toLocaleString('en-US')}</div>
      {popLabelAt(C, year) ? <div style={{font: `700 ${M ? 14 : 17}px Montserrat`, letterSpacing: M ? 3 : 4, color: 'rgba(246,241,231,0.75)', textShadow: SH, margin: '-6px 0 10px', textTransform: 'uppercase'}}>{popLabelAt(C, year)}</div> : null}
      <div style={{display: 'inline-block'}}>{M ? <Spark C={C} year={year} w={290} h={66} /> : <Spark C={C} year={year} />}</div>
    </div>
    <Timeline C={C} year={year} />
    {M ? <HudLine C={C} year={year} era={era} /> : <PolityChip C={C} year={year} />}
    <Reconstruction C={C} year={year} M={M} />
  </AbsoluteFill>); };

// didascalie continue (alto a sinistra): [t_in, t_out, date, title, line]; sober = barra grigia (tragedie)
const Cap = ({EV, s}) => { const e = EV.didascalie.find((c) => s >= c.t_in && s < c.t_out); if (!e) return null;
  const k = Math.min(1, (s - e.t_in) / 0.5, (e.t_out - s) / 0.5);
  return (<div style={{position: 'absolute', left: 80, top: 78, width: 700, opacity: k, transform: `translateX(${(1 - k) * -30}px)`, display: 'flex', gap: 22}}>
    <div style={{width: 6, borderRadius: 3, background: e.sober ? GREY : ACC}} />
    <div><div style={{font: '700 24px Montserrat', letterSpacing: 4, color: e.sober ? GREY : ACC, textShadow: SH}}>{e.date.toUpperCase()}</div>
      <div style={{font: '900 50px Montserrat', color: INK, textShadow: SH, lineHeight: 1.08, marginTop: 4}}>{e.title}</div>
      <div style={{font: '500 27px Montserrat', color: INK, textShadow: SH, lineHeight: 1.35, marginTop: 10, opacity: 0.94}}>{e.line}</div></div></div>); };

// soste con picchiata (basso, al centro)
const mkTok = (excl) => (t) => t.toLowerCase().split(/[^a-z]+/).filter((w) => w.length > 4 && !excl.includes(w));
const stopAt = (EV, cfg, s) => { const FS = cfg.t.first_stop_at; return EV.soste.map((x, i) => (i === 0 && x.t_in < FS ? {...x, t_in: FS, t_out: x.t_out + (FS - x.t_in)} : x)).find((x) => s >= x.t_in && s < x.t_out); };
const Stop = ({EV, cfg, s}) => { const tok = mkTok(cfg.tok_exclude);
  const e = stopAt(EV, cfg, s); if (!e) return null;
  // se in alto a sinistra c'e' gia' la didascalia dello stesso fatto (stesse parole chiave), il titolo della sosta non si ripete
  const cp = EV.didascalie.find((c) => s >= c.t_in && s < c.t_out); if (cp && tok(cp.title).some((w) => tok(e.title).includes(w))) return null;
  const k = Math.min(1, (s - e.t_in) / 0.5, (e.t_out - s) / 0.5);
  return (<div style={{position: 'absolute', left: 900, width: 860, bottom: 132, textAlign: 'center', opacity: k, transform: `translateY(${(1 - k) * 16}px)`}}>
    <div style={{display: 'inline-block', padding: '16px 34px', borderRadius: 14, background: 'rgba(12,14,16,0.62)', borderBottom: `4px solid ${ACC}`}}>
      <div style={{font: '900 44px Montserrat', color: INK, textShadow: SH, lineHeight: 1.12, textWrap: 'balance'}}>{e.title}</div>
      {e.sub ? <div style={{font: '700 26px Montserrat', letterSpacing: 4, color: ACC, textShadow: SH, marginTop: 8}}>{e.sub.toUpperCase()}</div> : null}
    </div></div>); };

// Subscribe animato: entra, clic, diventa "SUBSCRIBED" con campanella
const Subscribe = ({t0, s}) => { const u = s - t0; if (t0 == null || u < 0 || u > 5.2) return null;
  const k = Math.min(1, u / 0.45, (5.2 - u) / 0.45); const click = u > 2.0; const press = interpolate(u, [1.8, 2.0, 2.15], [1, 0.92, 1], clampI);
  const ring = click ? Math.sin((u - 2.1) * 22) * Math.max(0, 1 - (u - 2.1) / 1.3) * 18 : 0;
  const cx = interpolate(u, [0.5, 1.8], [90, 24], {...clampI, easing: (x) => 1 - Math.pow(1 - x, 3)}), cy = interpolate(u, [0.5, 1.8], [70, 20], clampI);
  return (<div style={{position: 'absolute', right: 80, bottom: 150, opacity: k, transform: `translateX(${(1 - k) * 60}px)`}}>
    <div style={{position: 'relative', display: 'flex', alignItems: 'center', gap: 16, transform: `scale(${press})`}}>
      <div style={{padding: '16px 30px', borderRadius: 40, background: click ? 'rgba(80,80,84,0.92)' : '#E62117', font: '900 30px Montserrat', color: '#fff', letterSpacing: 2, boxShadow: '0 4px 18px rgba(0,0,0,0.5)'}}>{click ? '✓ SUBSCRIBED' : 'SUBSCRIBE'}</div>
      <div style={{width: 62, height: 62, borderRadius: 31, background: 'rgba(12,14,16,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 34, transform: `rotate(${ring}deg)`, transformOrigin: '50% 12%'}}>🔔</div>
      {!click && u > 0.5 && <svg width={40} height={40} viewBox="0 0 24 24" style={{position: 'absolute', left: 90 + cx, top: 20 + cy, filter: 'drop-shadow(0 2px 3px rgba(0,0,0,0.6))'}}><path d="M5 3l14 8-6 1.5L10 19z" fill="#fff" stroke="#111" strokeWidth={1.2} /></svg>}
    </div></div>); };

// apertura: sul presente, poi "N YEARS" nel riavvolgimento. open = [[t0, t1, titolo, sotto], ...]
const Open = ({open, s}) => { const h = open.find((x) => s >= x[0] && s < x[1]); if (!h) return null;
  const k = Math.min(1, (s - h[0]) / 0.45, (h[1] - s) / 0.45);
  return (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', paddingBottom: 140, opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.42 * k}), rgba(10,10,12,0) 62%)`}}>
    <div style={{font: `900 ${fitSize(h[2], 1700, 110, 4)}px Montserrat`, color: INK, textShadow: SH, letterSpacing: 4, textAlign: 'center', transform: `translateY(${(1 - k) * 14}px)`}}>{h[2]}</div>
    {h[3] ? <div style={{font: '700 46px Montserrat', color: ACC, textShadow: SH, marginTop: 12, textAlign: 'center'}}>{h[3]}</div> : null}
  </AbsoluteFill>); };

const Title = ({text, k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.45 * k}), rgba(10,10,12,0) 65%)`, paddingBottom: 90}}>
  <div style={{font: '700 26px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>{text.title_kicker}</div>
  <div style={{font: `900 ${fitSize(text.title[0], 1700, 200)}px Montserrat`, color: INK, textShadow: SH, letterSpacing: 6, lineHeight: 1.05, transform: `scale(${0.96 + 0.04 * k})`, whiteSpace: 'nowrap'}}>{text.title[0]}</div>
  <div style={{display: 'flex', alignItems: 'center', gap: 26, font: '700 34px Montserrat', letterSpacing: 8, color: INK, textShadow: SH}}><span style={{width: 120, height: 2, background: ACC}} />{text.title[1]}<span style={{width: 120, height: 2, background: ACC}} /></div>
</AbsoluteFill>);

const End = ({text, k}) => (<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: k, background: `radial-gradient(ellipse at center, rgba(10,10,12,${0.55 * k}), rgba(10,10,12,0.15) 75%)`}}>
  <div style={{font: '700 24px Montserrat', letterSpacing: 10, color: ACC, textShadow: SH}}>{text.end[0]}</div>
  <div style={{font: `900 ${fitSize(text.end[1], 1800, 120, 4)}px Montserrat`, color: INK, textShadow: SH, letterSpacing: 4, lineHeight: 1.1, marginTop: 10}}>{text.end[1]}</div>
  <div style={{font: '500 34px Montserrat', color: INK, textShadow: SH, marginTop: 18, opacity: 0.9}}>{text.end_sub}</div>
  <div style={{position: 'absolute', bottom: 70, font: '900 30px Montserrat', letterSpacing: 10, color: INK, textShadow: SH, opacity: 0.85}}>{text.brand}</div>
</AbsoluteFill>);

// etichette sui monumenti: posizione proiettata con la STESSA camera del render (labels json da labels_cam.py).
// Finestre a tempo [inizio s, fine s, nomi]; ogni etichetta compare solo se il monumento esiste in quell'anno ed e' nel quadro.
const Label = ({LABELS, LAB_END, area, name, f, k, i = 0, year, cap, cfg}) => { const L = LABELS.lm[name]; if (!L) return null; if (year < L.y || year >= (LAB_END[name] ?? 9999)) return null;
  const p = L.p[f - LABELS.F0]; if (!p) return null;
  const [x, y, z] = p; const [xa, xb, ya, yb] = area; if (z <= 0 || x < xa || x > xb || y < ya || y > yb) return null;
  const up = (92 + 64 * i) * k;
  // se il cartellino coprirebbe la didascalia in alto a sinistra, il filo va verso il basso; se anche sotto c'e' l'HUD, non si mostra
  const down = cap && x - 110 < 800 && y - up - 52 < 330;
  if (down && (y + up + 60 > yb || (x - 110 < 620 && y + up + 60 > 760))) return null;
  return (<div style={{position: 'absolute', left: x, top: y, opacity: k}}>
    <div style={{position: 'absolute', left: -7, top: -7, width: 14, height: 14, borderRadius: 7, background: ACC, boxShadow: '0 0 0 3px rgba(0,0,0,0.45)'}} />
    <div style={{position: 'absolute', left: -1.5, top: down ? 0 : -up, width: 3, height: up, background: 'rgba(246,241,231,0.9)', boxShadow: '0 0 6px rgba(0,0,0,0.6)'}} />
    <div style={{position: 'absolute', left: 0, top: down ? up : -up - 52, transform: 'translateX(-50%)', whiteSpace: 'nowrap', padding: '8px 18px', borderRadius: 26, background: 'rgba(12,14,16,0.72)', font: '700 26px Montserrat', color: INK, letterSpacing: 1}}>{name}{cfg.label_years && L.y > -9999 ? ` · ${Math.floor(L.y)}` : ''}</div>
  </div>); };
const Labels = ({D, cfg, s, f, year}) => { const on = new Map(); if (s < cfg.t.labels_from || !D.labels || !D.labs) return null;
  const cap = D.eventi.didascalie.some((c) => s >= c.t_in - 0.3 && s < c.t_out + 0.3) || (cfg.style === 'mattia' ? [] : (D.eventi.cards || [])).some((c) => s >= c.t_in - 0.3 && s < c.t_out + 0.3);
  for (const e of D.labs.labs) if (s >= e[0] && s < e[1]) e[2].forEach((n) => { if (!on.has(n)) on.set(n, Math.min(1, (s - e[0]) / 0.5, (e[1] - s) / 0.5)); });
  return <>{[...on.entries()].map(([n, k], i) => <Label key={n} LABELS={D.labels} LAB_END={D.labs.end || {}} area={cfg.label_area} name={n} f={f} k={k} i={i} year={year} cap={cap} cfg={cfg} />)}</>; };

const yearAtF = (D, N) => (f) => D.years[String(Math.min(N, f + 1))] ?? 2026;

export const Overlay = ({cfg, data: D, bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAtF(D, cfg.n)(f); const T = cfg.t;
  const kh = ramp(s, T.hud), kt = ramp(s, T.title), ks = ramp(s, T.sepia), ke = interpolate(s, T.end, [0, 1], clampI);
  const M = cfg.style === 'mattia'; const EVx = D.eventi, chap = find(EVx.chapters, s), kch = chap ? win(chap, s) : 0, card = find(EVx.cards, s);
  const rc = find(EVx.recap && [EVx.recap], s), cta = find(EVx.cta && [EVx.cta], s), src = find(EVx.sources_card && [EVx.sources_card], s);
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile(cfg.preview_video)} style={{width: 1920, height: 1080}} />}
    {ks > 0 && <AbsoluteFill style={{background: `rgba(${T.sepia_rgb.join(',')},${0.34 * ks})`}} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud C={cfg.city} year={y} M={M} /><Labels D={D} cfg={cfg} s={s} f={f + 1} year={y} /><Cap EV={D.eventi} s={s} />{card && !chap && (M ? !stopAt(EVx, cfg, s) && <CardM e={card} k={win(card, s, 0.25)} /> : <Card e={card} k={win(card, s)} />)}{rc && <Recap e={EVx.recap} k={win(EVx.recap, s, 0.8)} />}{chap && <Chapter e={chap} k={kch} />}<Stop EV={D.eventi} cfg={cfg} s={s} /><Subscribe t0={cfg.t.subscribe ?? D.eventi.subscribe_t} s={s} /></AbsoluteFill>}
    <Open open={cfg.text.open} s={s} />
    {kt > 0 && <Title text={cfg.text} k={kt} />}
    {ke > 0 && <End text={cfg.text} k={ke} />}
    {cta && <Cta e={EVx.cta} k={win(EVx.cta, s, 0.7)} />}
    {src && <SourcesCard e={EVx.sources_card} k={win(EVx.sources_card, s, 0.8)} brand={cfg.text.brand} />}
  </AbsoluteFill>);
};

// Short verticale 1080x1920: tutto il video (dopo l'apertura, a -> b s) accelerato in ~28 s. Sopra: nome citta' e tag; sotto: anno, era, popolazione.
export const Short = ({cfg, data: D}) => { const C = cfg.city, S = cfg.short; const f = useCurrentFrame(); const s = f / FPS; const dur = S.n / FPS;
  const src = S.a + (S.b - S.a) * Math.min(1, s / (dur - 1.5)); const y = yearAtF(D, cfg.n)(Math.round(src * FPS));
  const k0 = interpolate(s, [0, 0.4], [0, 1], {extrapolateRight: 'clamp'}); const ke = interpolate(s, [dur - 1.4, dur - 0.8], [0, 1], clampI);
  const era = eraAt(C, y); const name = cfg.text.short_name;
  return (<AbsoluteFill>
    <div style={{position: 'absolute', top: 210, width: 1080, textAlign: 'center', opacity: k0}}>
      <div style={{font: '700 40px Montserrat', letterSpacing: 12, color: ACC, textShadow: SH}}>{cfg.text.short_tag}</div>
      <div style={{font: `900 ${fitSize(name, 1000, 190, 8)}px Montserrat`, color: INK, textShadow: SH, letterSpacing: 8, lineHeight: 1.05, whiteSpace: 'nowrap'}}>{name}</div></div>
    <div style={{position: 'absolute', top: 1330, width: 1080, textAlign: 'center', opacity: k0 * (1 - ke)}}>
      <div style={{font: '900 230px Montserrat', color: INK, textShadow: SH, fontVariantNumeric: 'tabular-nums', lineHeight: 1}}>{yearLabel(y)}</div>
      <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, font: '700 38px Montserrat', letterSpacing: 6, textTransform: 'uppercase', color: INK, textShadow: SH, marginTop: 10}}><span style={{width: 20, height: 20, borderRadius: 10, background: era[2]}} />{era[1]}</div>
      <div style={{font: '900 52px Montserrat', color: ACC, textShadow: SH, marginTop: 26}}>{y < C.EST_UNTIL ? '~' : ''}{fmtPop(popAt(C, y)).toLocaleString('en-US')} <span style={{font: '700 30px Montserrat', color: INK, letterSpacing: 3}}>PEOPLE</span></div></div>
    {ke > 0 && <div style={{position: 'absolute', top: 1360, width: 1080, textAlign: 'center', opacity: ke}}>
      <div style={{font: '900 84px Montserrat', color: INK, textShadow: SH}}>FULL VIDEO</div>
      <div style={{font: '700 40px Montserrat', color: ACC, textShadow: SH, marginTop: 10, letterSpacing: 4}}>ON THE CHANNEL ↑</div></div>}
  </AbsoluteFill>); };

// ---- caricamento: kit_<slug>.json + i 4 json collegati (public/). Anche la durata viene dal json. ----
const envSlug = () => { try { return process.env.REMOTION_KIT_SLUG || ''; } catch (e) { return ''; } };
const getJson = async (name, signal, optional = false) => { const r = await fetch(staticFile(name), {signal}); if (!r.ok) { if (optional) return null; throw new Error(`public/${name} non trovato (lancia kit_city.py)`); } return r.json(); };
const load = (kind) => async ({props, abortSignal}) => {
  const slug = props.slug || envSlug(); if (!slug) throw new Error('manca slug: --props=\'{"slug":"roma"}\' oppure REMOTION_KIT_SLUG');
  const cfg = await getJson(`kit_${slug}.json`, abortSignal);
  const [years, eventi, labels, labs] = await Promise.all([getJson(cfg.files.years, abortSignal), getJson(cfg.files.eventi, abortSignal), cfg.files.labels ? getJson(cfg.files.labels, abortSignal) : null, cfg.files.labs ? getJson(cfg.files.labs, abortSignal) : null]);
  const n = kind === 'short' ? cfg.short.n : cfg.n;
  return {durationInFrames: n, props: {...props, slug, cfg, data: {years, eventi, labels, labs}}};
};
const Root = () => (<>
  <Composition id="KitOverlay" component={Overlay} durationInFrames={24} fps={FPS} width={1920} height={1080} defaultProps={{slug: envSlug(), bg: false}} calculateMetadata={load('long')} />
  <Composition id="KitPreview" component={Overlay} durationInFrames={24} fps={FPS} width={1920} height={1080} defaultProps={{slug: envSlug(), bg: true}} calculateMetadata={load('long')} />
  <Composition id="KitShort" component={Short} durationInFrames={24} fps={FPS} width={1080} height={1920} defaultProps={{slug: envSlug()}} calculateMetadata={load('short')} />
</>);
registerRoot(Root);
