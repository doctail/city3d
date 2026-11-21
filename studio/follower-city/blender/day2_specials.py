"""Day 2 - edifici speciali (richieste dai commenti). Coordinate locali del lotto come mk_building: x = larghezza (centro 0),
y = 0 fronte del palazzo, y<0 verso la strada (marciapiede a y=-2), y>0 verso il retro (8 m), z=0 piano del selciato.
 - mk_villa: villa-casa di vetro cozy per @lillyflxwer (vetrate calde, steccato bianco, boxer + 3 cuccioli, bandierina a righe rosa-crema,
   tetto piano con piante). NIENTE bandiera 'playboy' (marchio/contenuto per adulti): bandierina neutra.
 - mk_og: edificio unico OG per @m.bardi56: caffe'/libreria d'angolo con insegna (tazza + libri). Nessun nome reale in scena.
"""
import math
import bpy, bmesh
from mathutils import Vector, Matrix
import cozy_city as cc
from cozy_city import MB, flat, m_win_lit, m_lamp, m_wood, m_iron, m_dark, m_trim, m_leaf, m_flow, m_stone, m_awn, m_cream, m_pot, m_sign, m_lettr, m_door

FAWN = (0.80, 0.52, 0.24)
MASK = (0.20, 0.12, 0.09)


def m_grass(): return flat("lawn", (0.47, 0.64, 0.30), rough=0.95)
def m_fence(): return flat("fencewhite", (0.98, 0.97, 0.93), rough=0.55)
def m_oak(): return flat("oak", (0.66, 0.46, 0.27), rough=0.6)
def m_walnut(): return flat("walnut", (0.38, 0.25, 0.16), rough=0.55)
def m_vcream(): return flat("vcream", (0.96, 0.92, 0.82), rough=0.8)
def m_fawn(): return flat("fawn", FAWN, rough=0.85)
def m_fawn2(): return flat("fawn2", (0.86, 0.60, 0.32), rough=0.85)
def m_mask(): return flat("mask", MASK, rough=0.8)
def m_white(): return flat("dogwhite", (0.97, 0.95, 0.90), rough=0.85)
def m_black(): return flat("black", (0.04, 0.04, 0.05), rough=0.4)
def m_pink(): return flat("flagpink", (0.95, 0.60, 0.70), rough=0.8)
def m_sofa(): return flat("sofa", (0.78, 0.40, 0.28), rough=0.9)
def m_rug(): return flat("rug", (0.92, 0.82, 0.62), rough=0.95)
def m_gold(): return flat("gold", (0.90, 0.72, 0.28), rough=0.3, metal=0.7)


def m_glass():
    """vetro: misto trasparente + riflesso (si vede l'interno caldo)."""
    if "vglass" in cc._mats:
        return cc._mats["vglass"]
    m = bpy.data.materials.new("vglass"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    pr = nt.nodes.new("ShaderNodeBsdfPrincipled")
    pr.inputs["Base Color"].default_value = (*cc.lin((0.74, 0.88, 0.86)), 1); pr.inputs["Roughness"].default_value = 0.04
    cc._spec(pr, 1.0)
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.22
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(pr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    cc._mats["vglass"] = m
    return m


def ell(b, cx, cy, cz, rx, ry, rz, m, sub=1):
    pb = bmesh.new()
    bmesh.ops.create_icosphere(pb, subdivisions=sub, radius=1.0)
    for v in pb.verts:
        v.co = Vector((v.co.x * rx + cx, v.co.y * ry + cy, v.co.z * rz + cz))
    pb.normal_update()
    b._add(pb, b.slot(m), True)
    pb.free()


def dog(b, x, y, yaw, sc, lying=False, pup=False):
    """boxer low-poly cozy: corpo fulvo, muso scuro, petto/calzini bianchi, orecchie ripiegate. Testa verso -y locale (poi ruotato di yaw)."""
    b.T = Matrix.Translation((x, y, 0.0)) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Scale(sc, 4)
    fw = m_fawn2() if pup else m_fawn()
    hk = 1.25 if pup else 1.0                                   # i cuccioli hanno la testa piu' grossa
    lh = 0.0 if not lying else 0.20                             # da sdraiato il corpo scende
    zb = 0.60 - lh
    ell(b, 0, 0.0, zb, 0.17, 0.42, 0.20, fw)                                  # torace/dorso
    ell(b, 0, -0.22, zb - 0.02, 0.17, 0.20, 0.22, m_white())                   # petto bianco
    ell(b, 0, 0.30, zb - 0.02, 0.16, 0.20, 0.20, fw)                           # coscia
    for sx_ in (-1, 1):
        if not lying:
            b.cyl(sx_ * 0.10, -0.26, 0.0, zb - 0.1, 0.045, fw, n=6)
            b.cyl(sx_ * 0.10, -0.26, 0.0, 0.11, 0.05, m_white(), n=6)
            b.cyl(sx_ * 0.11, 0.34, 0.0, zb - 0.1, 0.05, fw, n=6)
            b.cyl(sx_ * 0.11, 0.34, 0.0, 0.10, 0.055, m_white(), n=6)
        else:
            b.box(sx_ * 0.10 - 0.04, -0.50, 0.0, sx_ * 0.10 + 0.04, -0.26, 0.09, m_white())
            b.box(sx_ * 0.16 - 0.05, 0.22, 0.0, sx_ * 0.16 + 0.05, 0.46, 0.10, fw)
    ell(b, 0, -0.44, zb + 0.16, 0.11, 0.13, 0.17, fw)                          # collo
    hz = zb + 0.36
    b.box(-0.115 * hk, -0.74 * hk - 0.30 * (1 - hk), hz - 0.12, 0.115 * hk, -0.46, hz + 0.12 * hk, fw, bevel=0.035)   # testa
    b.box(-0.09 * hk, -0.82 * hk - 0.30 * (1 - hk), hz - 0.13, 0.09 * hk, -0.68 * hk - 0.30 * (1 - hk), hz + 0.02, m_mask(), bevel=0.03)   # muso scuro
    ell(b, 0, -0.835 * hk - 0.30 * (1 - hk), hz - 0.01, 0.035, 0.03, 0.03, m_black())                                    # naso
    for sx_ in (-1, 1):
        ell(b, sx_ * 0.07, -0.67 * hk - 0.30 * (1 - hk), hz + 0.07, 0.025, 0.02, 0.03, m_black())                        # occhi
        ell(b, sx_ * 0.115 * hk, -0.52, hz + 0.12, 0.035, 0.06, 0.075, m_mask())                                         # orecchie ripiegate
    b.cyl(0, 0.50, zb + 0.06, zb + 0.22, 0.03, fw, n=6, r2=0.02)               # coda mozza
    b.T = None


def rod_box(b, x0, y0, z0, x1, y1, z1, m):
    b.box(x0, y0, z0, x1, y1, z1, m)


def mk_villa(P, s):
    b = MB()
    hw = s['w'] / 2 - 0.02
    # ---- prato e vialetto
    b.box(-hw, -1.75, 0.0, hw, 3.5, 0.10, m_grass())
    for q in range(5):
        b.box(0.35, -1.55 + q * 0.78, 0.10, 1.05, -1.55 + q * 0.78 + 0.5, 0.15, m_stone(2))
    # ---- steccato bianco (davanti con cancelletto, ai lati)
    gate0, gate1 = 0.05, 1.35
    rails = [(-hw, gate0), (gate1, hw)]
    for (xa, xb) in rails:
        for zz in (0.28, 0.66):
            b.box(xa, -1.82, zz, xb, -1.78, zz + 0.07, m_fence())
        xx = xa + 0.12
        while xx < xb - 0.05:
            b.box(xx - 0.05, -1.84, 0.0, xx + 0.05, -1.76, 0.92, m_fence())
            b.prism([(xx - 0.05, 0.92), (xx + 0.05, 0.92), (xx, 1.04)], -1.84, -1.76, m_fence())
            xx += 0.40
    for xg in (gate0 - 0.07, gate1 + 0.07):
        b.box(xg - 0.08, -1.88, 0.0, xg + 0.08, -1.72, 1.08, m_fence())
        b.box(xg - 0.10, -1.90, 1.08, xg + 0.10, -1.70, 1.14, m_fence())
    for sx_ in (-1, 1):
        xs_ = sx_ * (hw - 0.04)
        for zz in (0.28, 0.66):
            b.box(xs_ - 0.02, -1.8, zz, xs_ + 0.02, 3.4, zz + 0.07, m_fence())
        yy = -1.4
        while yy < 3.4:
            b.box(xs_ - 0.04, yy - 0.05, 0.0, xs_ + 0.04, yy + 0.05, 0.92, m_fence())
            b.prism([(xs_ - 0.04, 0.92), (xs_ + 0.04, 0.92), (xs_, 1.04)], yy - 0.05, yy + 0.05, m_fence())
            yy += 0.40
    # ---- aiuole fiorite lungo lo steccato
    for xa in (-hw + 0.25, 1.9, 2.5):
        for q in range(4):
            ell(b, xa + 0.14 * (q % 2), -1.45 + 0.13 * (q // 2), 0.32 + 0.04 * q, 0.14, 0.13, 0.12, m_flow(q + int(xa * 3)), sub=1)
        ell(b, xa, -1.40, 0.18, 0.28, 0.2, 0.14, m_leaf(1), sub=1)
    # ---- veranda in legno + tetto veranda (e' il solaio del piano alto)
    b.box(-hw + 0.1, 1.7, 0.0, hw - 0.1, 3.5, 0.26, m_oak())
    for q in range(7):                                                   # gradini d'ingresso
        pass
    b.box(0.25, 1.35, 0.0, 1.15, 1.7, 0.18, m_oak())
    # ---- corpo: atrio doppia altezza a sinistra (x<-0.1) + due piani a destra
    xl, xm, xr = -hw + 0.1, -0.1, hw - 0.1
    yF, yB = 3.5, 8.0                                                    # fronte vetrata e retro
    # pavimento interno / retro caldo
    b.box(xl, yF, 0.0, xr, yB, 0.26, m_vcream())
    b.box(xl, yB - 0.1, 0.26, xr, yB, 6.3, m_vcream())
    b.box(xl, yB - 0.12, 0.30, xr, yB - 0.1, 3.0, m_win_lit())            # parete di fondo che 'brilla' (finestre calde)
    b.box(xm + 0.15, yB - 0.12, 3.6, xr - 0.1, yB - 0.1, 6.0, m_win_lit())
    # fianco sinistro (visibile dalla camera): tutto vetro con montanti
    b.box(xl, yF, 0.26, xl + 0.03, yB, 6.2, m_glass())
    for q in range(4):
        yy = yF + (yB - yF) * q / 3
        b.box(xl - 0.04, yy - 0.05, 0.26, xl + 0.08, yy + 0.05, 6.2, m_walnut())
    for zz in (0.26, 3.2, 6.2):
        b.box(xl - 0.04, yF, zz - 0.04, xl + 0.08, yB, zz + 0.04, m_walnut())
    b.box(xl, yF, 3.0, xl + 0.5, yB, 3.15, m_vcream())                   # ballatoio interno
    b.box(xr - 0.1, yF, 0.26, xr, yB, 6.3, m_walnut())
    # soletta del primo piano (solo a destra) + sbalzo = tetto veranda
    b.box(xm, 1.6, 3.15, xr + 0.1, yB, 3.45, m_vcream())
    b.box(xm, 1.56, 3.15, xr + 0.1, 1.6, 3.55, m_oak())
    # montanti veranda
    for xp in (xm + 0.2, xr - 0.1):
        b.box(xp - 0.07, 1.62, 0.26, xp + 0.07, 1.76, 3.15, m_oak())
    # --- vetrate piano terra (due campate: atrio + soggiorno) con montanti scuri
    def pane(xa, xb, za, zb, y=yF):
        b.box(xa, y - 0.03, za, xb, y + 0.0, zb, m_glass())
    def frame(xa, xb, za, zb, nx, nz, y=yF, mm=None):
        mm = mm or m_walnut()
        for q in range(nx + 1):
            xx = xa + (xb - xa) * q / nx
            b.box(xx - 0.05, y - 0.10, za, xx + 0.05, y + 0.04, zb, mm)
        for q in range(nz + 1):
            zz = za + (zb - za) * q / nz
            b.box(xa, y - 0.10, zz - 0.04, xb, y + 0.04, zz + 0.04, mm)
    # atrio (altezza piena 0.26..6.2)
    pane(xl, xm, 0.26, 6.2); frame(xl, xm, 0.26, 6.2, 3, 6)
    # piano terra a destra: porta + vetri
    pane(xm, xr, 0.26, 3.1); frame(xm, xr, 0.26, 3.1, 4, 1)
    b.box(0.25, yF - 0.12, 0.26, 1.15, yF - 0.04, 2.85, m_door(1))          # porta (verde salvia/blu)
    b.box(0.40, yF - 0.14, 0.9, 1.0, yF - 0.10, 2.65, m_glass())
    b.box(1.02, yF - 0.16, 1.4, 1.08, yF - 0.10, 1.5, m_gold())
    # piano alto a destra: parete a doghe di legno con grande finestra + balconcino vetro
    b.box(xm, 2.3, 3.45, xr, yF + 0.05, 6.2, m_oak())
    for q in range(int((xr - xm) / 0.22)):
        b.box(xm + q * 0.22, 2.24, 3.45, xm + q * 0.22 + 0.04, 2.30, 6.2, m_walnut())
    b.box(xm + 0.35, 2.20, 3.9, xr - 0.35, 2.28, 5.7, m_win_lit())
    pane(xm + 0.35, xr - 0.35, 3.9, 5.7, y=2.20)
    b.box(xm + 0.30, 2.16, 3.85, xr - 0.30, 2.22, 3.92, m_walnut()); b.box(xm + 0.30, 2.16, 5.7, xr - 0.30, 2.22, 5.78, m_walnut())
    b.box(xm + 0.60, 2.16, 3.9, xm + 0.66, 2.22, 5.7, m_walnut())
    b.box(xm + 0.30, 1.62, 3.45, xr - 0.1, 1.68, 4.45, m_glass())          # parapetto in vetro sul tetto veranda
    # --- tetto piano con pensilina, tetto verde e piante
    b.box(xl - 0.3, 1.3, 6.2, xm + 0.3, yB + 0.3, 6.45, m_vcream())
    b.box(xm - 0.3, 1.9, 6.2, xr + 0.35, yB + 0.3, 6.45, m_vcream())
    b.box(xl - 0.3, 1.3, 6.2, xr + 0.35, 1.36, 6.5, m_oak()) if False else None
    b.box(xl - 0.12, 1.5, 6.45, xm + 0.1, yB + 0.1, 6.62, m_grass())
    b.box(xm + 0.1, 2.1, 6.45, xr + 0.15, yB + 0.1, 6.62, m_grass())
    import random
    rg = random.Random(11)
    for q in range(16):                                                  # cespugli e fiori sul tetto
        xx = rg.uniform(xl, xr); yy = rg.uniform(2.3, 7.7)
        ell(b, xx, yy, 6.75, rg.uniform(0.22, 0.4), rg.uniform(0.22, 0.4), rg.uniform(0.15, 0.3), m_leaf(q), sub=1)
    for q in range(10):
        ell(b, rg.uniform(xl, xr), rg.uniform(2.3, 7.7), 6.98, 0.09, 0.09, 0.09, m_flow(q), sub=1)
    # --- interno visibile: divano, tappeto, tavolino, lampada, pianta, cucina, letto
    b.box(xm + 0.2, 4.7, 0.26, xr - 0.3, 6.4, 0.30, m_rug())
    b.box(xm + 0.35, 6.4, 0.30, xr - 0.45, 7.7, 1.0, m_sofa())
    b.box(xm + 0.35, 7.4, 0.9, xr - 0.45, 7.7, 1.5, m_sofa())
    b.box(xm + 1.2, 5.3, 0.30, xm + 2.2, 5.9, 0.75, m_oak())
    b.cyl(xr - 0.5, 4.2, 0.26, 2.2, 0.025, m_iron(), n=6); b.cyl(xr - 0.5, 4.2, 2.0, 2.4, 0.28, m_lamp(), n=10, r2=0.18)
    b.cyl(xl + 0.9, 5.6, 0.26, 0.9, 0.28, m_pot(), n=10)
    for q in range(5):
        ell(b, xl + 0.9 + 0.2 * math.cos(q * 1.3), 5.6 + 0.2 * math.sin(q * 1.3), 1.4 + 0.5 * (q % 3), 0.35, 0.35, 0.5, m_leaf(q), sub=1)
    b.cyl(xl + 1.5, 6.9, 0.26, 3.4, 0.45, m_pot(), n=10) if False else None
    for q in range(4):                                                   # pensili luce in atrio
        b.cyl(xl + 1.5, 4.8 + q * 0.0, 4.2 + q * 0.5, 6.1, 0.012, m_iron(), n=4)
        b.cyl(xl + 1.5, 4.8, 4.2 + q * 0.5, 4.5 + q * 0.5, 0.2, m_lamp(), n=10, r2=0.1)
        break
    b.box(xm + 0.4, 5.0, 3.45, xr - 0.6, 7.2, 3.85, m_vcream())          # letto (piano alto)
    b.box(xm + 0.4, 6.7, 3.85, xr - 0.6, 7.2, 4.5, m_oak())
    for q in range(2):
        b.box(xm + 0.6 + q * 1.1, 5.2, 3.85, xm + 1.4 + q * 1.1, 5.7, 4.0, m_pink())
    # --- bandierina neutra a righe rosa-crema sul portico (NO playboy), su asta con braccio
    xf_ = hw - 0.30
    b.cyl(xf_, 1.50, 0.10, 2.85, 0.04, m_iron(), n=6)
    ell(b, xf_, 1.50, 2.92, 0.08, 0.08, 0.08, m_gold(), sub=1)
    for q in range(6):
        b.box(xf_ - 1.30, 1.45, 2.75 - q * 0.14, xf_ - 0.04, 1.54, 2.75 - q * 0.14 + 0.14, m_pink() if q % 2 == 0 else m_cream())
    # --- sedia a dondolo + vasi sul portico, cassetta della posta
    b.box(-hw + 0.5, 2.0, 0.26, -hw + 1.4, 2.7, 0.7, m_wood())
    b.box(-hw + 0.5, 2.6, 0.7, -hw + 1.4, 2.7, 1.3, m_wood())
    for xx in (hw - 0.9, hw - 0.5):
        b.cyl(xx, 2.5, 0.26, 0.7, 0.2, m_pot(), n=10)
        ell(b, xx, 2.5, 0.95, 0.24, 0.24, 0.22, m_leaf(2), sub=1)
    b.box(hw - 0.18, -1.35, 0.0, hw - 0.10, -1.27, 0.95, m_wood()) if False else None
    # --- il boxer e i 3 cuccioli sul prato (testa verso la strada)
    dog(b, -1.55, 0.55, math.radians(25), 1.5)
    dog(b, -0.35, 1.05, math.radians(-20), 0.95, pup=True)
    dog(b, -2.45, 1.45, math.radians(60), 0.85, lying=True, pup=True)
    dog(b, -0.95, -0.70, math.radians(-50), 0.9, pup=True)
    return b


def mk_og(P, s):
    """Caffe'-libreria d'angolo: mansarda blu polvere, torretta, tenda a righe, tavolini; insegna a bandiera con tazza + libri."""
    b = cc.mk_building(P)
    hw = P['w'] / 2
    sx = -hw + 0.55
    b.T = Matrix.Translation((sx, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, 'Z')     # piano insegna perpendicolare alla facciata (visibile lungo la strada)
    # bracket e bordo (x' = lungo la facciata->sporgenza; qui costruiamo nel piano (x',z) estruso lungo y')
    b.box(-1.15, -0.04, 4.45, 0.0, 0.04, 4.52, m_iron())
    brd = m_sign(0)
    b.box(-1.45, -0.05, 4.95, 0.0, 0.05, 5.03, m_iron())
    b.box(-1.55, -0.12, 3.55, -0.15, 0.12, 4.95, brd, bevel=0.05)
    b.box(-1.50, 0.12, 3.60, -0.20, 0.14, 4.90, m_cream())                  # cornice chiara
    b.box(-1.45, 0.14, 3.65, -0.25, 0.16, 4.85, brd)
    # tazza + vapore (sinistra), 3 libri impilati (destra), in rilievo 'cream' luminoso
    b.prism([(-1.35, 3.85), (-0.95, 3.85), (-0.90, 4.30), (-1.40, 4.30)], 0.16, 0.22, m_lettr())
    b.box(-0.90, 0.16, 3.97, -0.76, 0.22, 4.15, m_lettr())
    b.box(-1.45, 0.16, 4.30, -0.85, 0.22, 4.35, m_lettr())
    for q in range(2):
        b.box(-1.28 + q * 0.22, 0.16, 4.45 + q * 0.05, -1.20 + q * 0.22, 0.22, 4.70 + q * 0.05, m_lettr())
    hs = [0.17, 0.14, 0.17]; zc = 3.78
    for q, cm in enumerate((m_awn(0), m_awn(1), m_awn(3))):
        b.box(-0.68, 0.16, zc, -0.32, 0.22, zc + hs[q], cm); zc += hs[q] + 0.02
    b.box(-0.60, 0.16, zc, -0.40, 0.22, zc + 0.30, m_awn(2))
    b.T = None
    return b


def register():
    """ordine di apparizione: lotto 1 std A (rank 3), 2 std B (rank 7), 3 edificio OG (rank 5, @m.bardi56), 4 villa (rank 9, @lillyflxwer)."""
    cc.SPECIAL.clear()
    cc.SPECIAL[3] = mk_og
    cc.SPECIAL[4] = mk_villa
    cc.PICK = [0, 3, 7, 5, 9]
    cc.LOT_OVERRIDE = {3: dict(style=2, w=6.25, n=3, wall=104, roof=2, shop=0, corner=1, door=1, gab=0, sidewin=1)}
