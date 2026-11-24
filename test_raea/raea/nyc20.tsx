// New York, primi 20 s (480 fotogrammi, 24 fps, 1920x1080): stessa camera e stessi anni di schedule_nyc.json.
// I dati (edifici, terra, fasi di terra, parchi, camera, anni) arrivano da scene.gen.ts, scritto da ../gen_scene.py
// dagli stessi file di build_render.py. Look semplice: sole, ambiente, nebbia, edifici piatti per classe di colore.
// Tutto dipende solo dal fotogramma (useCurrentFrame): niente stato, niente Math.random.
import { AbsoluteFill, Composition, registerRoot, useCurrentFrame } from "raea";
import { Fog } from "raea/3d";
import { Camera3d } from "raea/camera";
import { AmbientLight, DirectionalLight } from "raea/light";
import { BufferMesh, Mesh3d, Plane3d } from "raea/mesh";
import { StandardMaterial } from "raea/pbr";
import { Transform } from "raea/transform";
import { DATA } from "./scene.gen";

const SKY = "#bcd0e2"; // sfondo piatto e nebbia dello stesso colore (come l'aloni di build_render, haze 0.8/0.88/0.96)
const SUN = { el: 22, rot: 140 }; // city_nyc.json: sun_el, sun_rot (gradi, Blender)

// ---- crescita: la stessa funzione di build_render.py (growth) ----
function growth(year: number, dur: number, b0: number): number {
  const t = (year - b0) / dur;
  if (t <= 0) return 0;
  return t >= 1 ? 1 : t + 0.18 * Math.sin(Math.PI * t);
}
const mix = (a: string, b: string, u: number) => {
  const p = (h: string, i: number) => parseInt(h.slice(1 + 2 * i, 3 + 2 * i), 16);
  const c = [0, 1, 2].map((i) => Math.round(p(a, i) + (p(b, i) - p(a, i)) * u).toString(16).padStart(2, "0"));
  return "#" + c.join("");
};
const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

// la direzione del sole: Blender (x, y, z su) -> raea (x, z, -y); il sole sta verso (sin a sin c, -sin a cos c, cos a)
const a = ((90 - SUN.el) * Math.PI) / 180, c = (SUN.rot * Math.PI) / 180;
const SUN_AT: [number, number, number] = [Math.sin(a) * Math.sin(c), Math.cos(a), Math.sin(a) * Math.cos(c)].map((v) => v * 1000) as [number, number, number];

function Shot() {
  const f = useCurrentFrame();
  const i = Math.min(DATA.frames - 1, Math.max(0, f));
  const year = DATA.years[i], dur = DATA.durs[i];
  const [px, py, pz, tx, ty, tz, lens] = DATA.cam[i];
  const fov = 2 * Math.atan((18 / lens) * (9 / 16)); // sensore 36 mm sul lato lungo, come Blender (verticale 16:9)
  const forest = "#5d9c3f", urban = "#cdc5b4"; // forest_base e urban di city_nyc.json
  const ground = mix(forest, urban, clamp01((year - 1800) / 120));
  return (
    <AbsoluteFill style={{ background: SKY }}>
      <Camera3d transform={Transform.fromXyz(px, py, pz).lookingAt([tx, ty, tz])} projection={{ Perspective: { fov, near: 5, far: 60000 } }}>
        <Fog color={SKY} near={3000} far={16000} />
      </Camera3d>
      <AmbientLight brightness={900} />
      <DirectionalLight illuminance={12000} transform={Transform.fromXyz(...SUN_AT).lookingAt([0, 0, 0])} />
      {/* mare */}
      <Mesh3d name="water" transform={Transform.fromXyz(tx, DATA.waterY, tz)}>
        <Plane3d half_size={[60000, 60000]} />
        <StandardMaterial base_color="#126a84" perceptual_roughness={0.25} />
      </Mesh3d>
      {/* terra di base, fasi di terra, parchi */}
      {DATA.land.length > 0 && (
        <Mesh3d name="land">
          <BufferMesh positions={DATA.land} />
          <StandardMaterial base_color={ground} perceptual_roughness={0.95} cull_mode={null} />
        </Mesh3d>
      )}
      {DATA.phases.map((ph, k) =>
        year >= ph.from && year < ph.to ? (
          <Mesh3d name={`phase${k}`} key={k}>
            <BufferMesh positions={ph.p} />
            <StandardMaterial base_color="#b8ad98" perceptual_roughness={0.95} cull_mode={null} />
          </Mesh3d>
        ) : null,
      )}
      {year >= 1858 && DATA.parks.length > 0 && (
        <Mesh3d name="parks">
          <BufferMesh positions={DATA.parks} />
          <StandardMaterial base_color="#5f8a3e" perceptual_roughness={0.95} cull_mode={null} />
        </Mesh3d>
      )}
      {/* edifici: un blocco per (cella, anni, colore); compare e cresce per scala in altezza dal suo anno */}
      {DATA.chunks.map((ch, k) => {
        const g = growth(year, dur, ch.b0);
        if (g < 0.002) return null;
        return (
          <Mesh3d name={`b${k}`} key={k} transform={Transform.fromScale([1, g, 1])}>
            <BufferMesh positions={ch.p} />
            <StandardMaterial base_color={DATA.classes[ch.c]} perceptual_roughness={0.9} cull_mode={null} />
          </Mesh3d>
        );
      })}
    </AbsoluteFill>
  );
}

registerRoot(() => <Composition id="nyc20" component={Shot} width={1920} height={1080} fps={24} durationInFrames={480} />);
