// Controllo locale (senza GPU, senza il binario raea): la composizione si valuta davvero per alcuni fotogrammi con
// l'SDK del clone raea (renderFrame, come i test dell'SDK) e si contano le parti 3D che produce.
// Uso: RAEA_SDK=/percorso/raea/sdk bun run check_frames.tsx
import { getCompositions } from "raea";
import "./nyc20";
const SDK = process.env.RAEA_SDK ?? "/home/user/shinyobjectz/raea/sdk";
const { renderFrame } = await import(`${SDK}/raea/src/test`);
const comp = getCompositions()[0];
const C = comp.component as () => React.ReactElement;
const out: Record<string, unknown>[] = [];
for (const f of [0, 60, 100, 150, 200, 230, 300, 479]) {
  const t = performance.now();
  const h = renderFrame(<C />, { frame: f, width: 1920, height: 1080, fps: 24, durationInFrames: 480 });
  const meshes = (h.match(/data-3d="Mesh"/g) ?? []).length;
  out.push({ f, ms: Math.round(performance.now() - t), html_MB: +(h.length / 1e6).toFixed(2), mesh: meshes, kinds: [...new Set((h.match(/data-3d="[A-Za-z0-9]+"/g) ?? []))].join(" ").replace(/data-3d=/g, "") });
}
console.log(comp.id, comp.width, comp.height, comp.fps, comp.durationInFrames);
console.table(out);
