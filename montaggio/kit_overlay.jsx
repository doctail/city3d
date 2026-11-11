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

const Hud = ({C, year}) => { const era = eraAt(C, year); const p = popAt(C, year); const est = year < C.EST_UNTIL || year > 2022;
  return (<AbsoluteFill>
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 420, background: 'linear-gradient(0deg, rgba(10,10,12,0.62), rgba(10,10,12,0))'}} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 900, height: 420, background: 'radial-gradient(ellipse at 0% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', right: 0, top: 0, width: 700, height: 340, background: 'radial-gradient(ellipse at 100% 0%, rgba(10,10,12,0.45), rgba(10,10,12,0) 70%)'}} />
    <div style={{position: 'absolute', left: 80, bottom: 104}}>
      <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, font: '700 22px Montserrat', letterSpacing: 5, textTransform: 'uppercase', color: INK, textShadow: SH}}><span style={{width: 14, height: 14, borderRadius: 7, background: era[2], boxShadow: '0 0 0 3px rgba(0,0,0,0.35)'}} />{era[1]}</div>
      <div style={{font: '900 150px Montserrat', color: INK, textShadow: SH, lineHeight: 0.95, fontVariantNumeric: 'tabular-nums', letterSpacing: -2}}>{yearLabel(year)}</div>
    </div>
    <div style={{position: 'absolute', right: 80, top: 78, textAlign: 'right'}}>
      <div style={{font: '700 18px Montserrat', letterSpacing: 4, color: 'rgba(246,241,231,0.75)', textShadow: SH}}>POPULATION <span style={{opacity: 0.7, letterSpacing: 2}}>· {C.popLabel}</span></div>
      <div style={{font: '900 52px Montserrat', color: ACC, textShadow: SH, fontVariantNumeric: 'tabular-nums', margin: '2px 0 10px'}}>{est ? '~' : ''}{fmtPop(p).toLocaleString('en-US')}</div>
      <div style={{display: 'inline-block'}}><Spark C={C} year={year} /></div>
    </div>
    <Timeline C={C} year={year} />
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
const Stop = ({EV, cfg, s}) => { const FS = cfg.t.first_stop_at; const tok = mkTok(cfg.tok_exclude);
  const e = EV.soste.map((x, i) => (i === 0 && x.t_in < FS ? {...x, t_in: FS, t_out: x.t_out + (FS - x.t_in)} : x)).find((x) => s >= x.t_in && s < x.t_out); if (!e) return null;
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
const Label = ({LABELS, LAB_END, area, name, f, k, i = 0, year, cap}) => { const L = LABELS.lm[name]; if (!L) return null; if (year < L.y || year >= (LAB_END[name] ?? 9999)) return null;
  const p = L.p[f - LABELS.F0]; if (!p) return null;
  const [x, y, z] = p; const [xa, xb, ya, yb] = area; if (z <= 0 || x < xa || x > xb || y < ya || y > yb) return null;
  const up = (92 + 64 * i) * k;
  // se il cartellino coprirebbe la didascalia in alto a sinistra, il filo va verso il basso; se anche sotto c'e' l'HUD, non si mostra
  const down = cap && x - 110 < 800 && y - up - 52 < 330;
  if (down && (y + up + 60 > yb || (x - 110 < 620 && y + up + 60 > 760))) return null;
  return (<div style={{position: 'absolute', left: x, top: y, opacity: k}}>
    <div style={{position: 'absolute', left: -7, top: -7, width: 14, height: 14, borderRadius: 7, background: ACC, boxShadow: '0 0 0 3px rgba(0,0,0,0.45)'}} />
    <div style={{position: 'absolute', left: -1.5, top: down ? 0 : -up, width: 3, height: up, background: 'rgba(246,241,231,0.9)', boxShadow: '0 0 6px rgba(0,0,0,0.6)'}} />
    <div style={{position: 'absolute', left: 0, top: down ? up : -up - 52, transform: 'translateX(-50%)', whiteSpace: 'nowrap', padding: '8px 18px', borderRadius: 26, background: 'rgba(12,14,16,0.72)', font: '700 26px Montserrat', color: INK, letterSpacing: 1}}>{name}</div>
  </div>); };
const Labels = ({D, cfg, s, f, year}) => { const on = new Map(); if (s < cfg.t.labels_from || !D.labels || !D.labs) return null;
  const cap = D.eventi.didascalie.some((c) => s >= c.t_in - 0.3 && s < c.t_out + 0.3);
  for (const e of D.labs.labs) if (s >= e[0] && s < e[1]) e[2].forEach((n) => { if (!on.has(n)) on.set(n, Math.min(1, (s - e[0]) / 0.5, (e[1] - s) / 0.5)); });
  return <>{[...on.entries()].map(([n, k], i) => <Label key={n} LABELS={D.labels} LAB_END={D.labs.end || {}} area={cfg.label_area} name={n} f={f} k={k} i={i} year={year} cap={cap} />)}</>; };

const yearAtF = (D, N) => (f) => D.years[String(Math.min(N, f + 1))] ?? 2026;

export const Overlay = ({cfg, data: D, bg = false}) => {
  const f = useCurrentFrame(); const s = f / FPS; const y = yearAtF(D, cfg.n)(f); const T = cfg.t;
  const kh = ramp(s, T.hud), kt = ramp(s, T.title), ks = ramp(s, T.sepia), ke = interpolate(s, T.end, [0, 1], clampI);
  return (<AbsoluteFill>
    {bg && <OffthreadVideo src={staticFile(cfg.preview_video)} style={{width: 1920, height: 1080}} />}
    {ks > 0 && <AbsoluteFill style={{background: `rgba(${T.sepia_rgb.join(',')},${0.34 * ks})`}} />}
    {kh > 0 && <AbsoluteFill style={{opacity: kh}}><Hud C={cfg.city} year={y} /><Labels D={D} cfg={cfg} s={s} f={f + 1} year={y} /><Cap EV={D.eventi} s={s} /><Stop EV={D.eventi} cfg={cfg} s={s} /><Subscribe t0={cfg.t.subscribe ?? D.eventi.subscribe_t} s={s} /></AbsoluteFill>}
    <Open open={cfg.text.open} s={s} />
    {kt > 0 && <Title text={cfg.text} k={kt} />}
    {ke > 0 && <End text={cfg.text} k={ke} />}
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
