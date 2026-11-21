import math, os, subprocess, sys, wave, json
import numpy as np
import skia

# estilo v2 (plano, contorno oscuro, rosa fuerte) + utilidades de make2
_s2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'motor_estilo.py')).read().split('if __name__ == "__main__":')[0]
exec(_s2)

_dt_orig = draw_text


def draw_text(c, s, *a, **k):
    if s.startswith("*"):
        return
    return _dt_orig(c, s, *a, **k)


SKIN = 0xFFF5C6A5
GRAYT = 0xFF8A8A8A


# ------------------------------------------------------------------ utilidades de dibujo
def ctext(c, s, cx, cy, size, color=None):
    color = INK if color is None else color
    draw_text(c, s, cx - text_w(s, size) / 2, cy + size * 0.35, size, color)


def pp(u, delay, dur=0.35):
    return ease_out_back((u - delay) / dur)


def popbegin(c, cx, cy, p):
    c.save()
    c.translate(cx, cy)
    c.scale(max(p, 0.001), max(p, 0.001))
    c.translate(-cx, -cy)


def card(c, x, y, w, h, fill=WHITE, r=30, sh=8):
    rrect(c, x + sh, y + sh, w, h, r, fill=INK)
    rrect(c, x, y, w, h, r, fill=fill, line=INK, lw=7)


def check_icon(c, cx, cy, s, color=GREEN):
    p = skia.Path()
    p.moveTo(cx - s, cy)
    p.lineTo(cx - s * 0.3, cy + s * 0.7)
    p.lineTo(cx + s, cy - s * 0.7)
    c.drawPath(p, paint(INK, True, s * 0.6))
    c.drawPath(p, paint(color, True, s * 0.34))


def cross_icon(c, cx, cy, s, color=RED):
    for a, b in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
        c.drawLine(cx + a[0] * s, cy + a[1] * s, cx + b[0] * s, cy + b[1] * s, paint(INK, True, s * 0.6))
    for a, b in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
        c.drawLine(cx + a[0] * s, cy + a[1] * s, cx + b[0] * s, cy + b[1] * s, paint(color, True, s * 0.34))


def numcircle(c, cx, cy, n, r=34, col=None):
    col = PINK if col is None else col
    oval(c, cx, cy, r, r, fill=col, line=INK, lw=7)
    ctext(c, str(n), cx, cy, r * 1.15, WHITE)


def earbud(c, cx, cy, s=1.0, rot=0.0):
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -13, -8, 26, 104, 13, fill=WHITE, line=INK, lw=7)
    oval(c, 0, -22, 36, 32, fill=WHITE, line=INK, lw=7)
    oval(c, -10, -30, 9, 8, fill=0xFFE9E1EE)
    c.restore()


def case_icon(c, cx, cy, s=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    rrect(c, -62, -45, 124, 90, 36, fill=WHITE, line=INK, lw=8)
    line(c, -58, -6, 58, -6, INK, 6)
    oval(c, 0, 20, 7, 7, fill=GREEN)
    c.restore()


def ear(c, cx, cy, s=1.0, bud=True, bob=0.0):
    c.save()
    c.translate(cx, cy + bob)
    c.scale(s, s)
    oval(c, 0, 0, 78, 112, fill=SKIN, line=INK, lw=8)
    arc = skia.Path()
    arc.addArc(skia.Rect.MakeLTRB(-46, -72, 40, 62), 200, 270)
    c.drawPath(arc, paint(INK, True, 7))
    oval(c, 10, 22, 15, 22, fill=0xFFD9A07F, line=INK, lw=6)
    if bud:
        earbud(c, 14, 40, 0.9, 12)
    c.restore()


def watch(c, cx, cy, s=1.0, txt="10:10", sub=None, strap=None, rot=0.0):
    strap = PINK_L if strap is None else strap
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(s, s)
    rrect(c, -46, -230, 92, 150, 20, fill=strap, line=INK, lw=7)
    rrect(c, -46, 80, 92, 150, 20, fill=strap, line=INK, lw=7)
    rrect(c, -96, -108, 192, 216, 54, fill=INK)
    rrect(c, -100, -112, 192, 216, 54, fill=0xFF2B2B38, line=INK, lw=8)
    rrect(c, -84, -96, 160, 184, 42, fill=0xFF14141C)
    rrect(c, 96, -34, 16, 46, 7, fill=GRAY, line=INK, lw=6)
    ctext(c, txt, -8, -28 if sub else 0, 56, WHITE)
    if sub:
        ctext(c, sub, -8, 36, 30, YEL)
    c.restore()


def price_tag(c, cx, cy, w, h, text, size, col=None, rot=-6.0, pop=1.0):
    col = YEL if col is None else col
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(pop, pop)
    rrect(c, -w / 2 + 8, -h / 2 + 8, w, h, 36, fill=INK)
    rrect(c, -w / 2, -h / 2, w, h, 36, fill=col, line=INK, lw=8)
    oval(c, -w / 2 + 36, 0, 12, 12, fill=BG, line=INK, lw=6)
    ctext(c, text, 22, 0, size, INK)
    c.restore()


def magnifier(c, cx, cy, r):
    oval(c, cx, cy, r, r, fill=0x44FFFFFF, line=INK, lw=11)
    line(c, cx + r * 0.72, cy + r * 0.72, cx + r * 1.75, cy + r * 1.75, INK, 18)


def phone_begin(c, cx, cy, scale=1.0, shake=0.0, t=0.0):
    c.save()
    c.translate(cx + math.sin(t * 60) * shake, cy)
    c.scale(scale, scale)
    w, h = 340, 620
    rrect(c, -w / 2 + 10, -h / 2 + 12, w, h, 56, fill=INK)
    rrect(c, -w / 2, -h / 2, w, h, 56, fill=0xFF2B2B38, line=INK, lw=10)
    rrect(c, -w / 2 + 16, -h / 2 + 16, w - 32, h - 32, 42, fill=0xFF14141C)
    rrect(c, -50, -h / 2 + 30, 100, 26, 13, fill=INK)


def battery_icon(c, cx, cy, pct, w=200, h=110):
    rrect(c, cx - w / 2, cy - h / 2, w, h, 24, line=WHITE, lw=8)
    rrect(c, cx + w / 2 + 6, cy - 25, 16, 50, 6, fill=WHITE)
    col = RED if pct < 25 else (YEL if pct < 60 else GREEN)
    fw = max(0, (w - 20) * pct / 100)
    if fw > 0:
        rrect(c, cx - w / 2 + 10, cy - h / 2 + 10, fw, h - 20, 14, fill=col)


def balance(c, cx, cy, ang, coins=2, box=True, cuotas=0.0):
    """balanza: ang>0 inclina a la derecha (producto pesado)."""
    rad = math.radians(ang)
    line(c, cx, cy - 10, cx, cy + 150, INK, 16)
    rrect(c, cx - 70, cy + 140, 140, 26, 13, fill=PINK, line=INK, lw=7)
    line(c, cx - 200 * math.cos(rad), cy - 10 - 200 * math.sin(rad), cx + 200 * math.cos(rad), cy - 10 + 200 * math.sin(rad), INK, 14)
    oval(c, cx, cy - 10, 16, 16, fill=YEL, line=INK, lw=6)
    lx, ly = cx - 200 * math.cos(rad), cy - 10 - 200 * math.sin(rad)
    rx, ry = cx + 200 * math.cos(rad), cy - 10 + 200 * math.sin(rad)
    for px, py, items in ((lx, ly, "coins"), (rx, ry, "box")):
        line(c, px, py, px - 50, py + 110, INK, 6)
        line(c, px, py, px + 50, py + 110, INK, 6)
        oval(c, px, py + 118, 62, 14, fill=GRAY, line=INK, lw=7)
        if items == "coins":
            for k in range(coins):
                oval(c, px - 18 + k * 36, py + 92, 17, 17, fill=YEL, line=INK, lw=6)
        elif box:
            rrect(c, px - 42, py + 40, 84, 70, 12, fill=PINK_L, line=INK, lw=7)
            ctext(c, "$$$", px, py + 76, 34, INK)
            line(c, px, py + 40, px, py + 110, INK, 5)


def doc_icon(c, cx, cy, w=240, h=300):
    card(c, cx - w / 2, cy - h / 2, w, h, WHITE, 24)
    for k in range(5):
        rrect(c, cx - w / 2 + 30, cy - h / 2 + 40 + k * 44, w - 60 - (40 if k % 2 else 0), 14, 7, fill=GRAY)
    return


def smiley(c, cx, cy, r, col):
    oval(c, cx, cy, r, r, fill=col, line=INK, lw=6)
    oval(c, cx - r * 0.35, cy - r * 0.2, r * 0.12, r * 0.16, fill=INK)
    oval(c, cx + r * 0.35, cy - r * 0.2, r * 0.12, r * 0.16, fill=INK)
    c.drawArc(skia.Rect.MakeXYWH(cx - r * 0.45, cy - r * 0.1, r * 0.9, r * 0.7), 20, 140, False, paint(INK, True, 5))


def bubble(c, cx, cy, w, h, text, size, col, tcol, p):
    if p <= 0.02:
        return
    popbegin(c, cx, cy, p)
    rrect(c, cx - w / 2 + 6, cy - h / 2 + 6, w, h, h / 2, fill=INK)
    rrect(c, cx - w / 2, cy - h / 2, w, h, h / 2, fill=col, line=INK, lw=7)
    ctext(c, text, cx, cy, size, tcol)
    c.restore()


# ------------------------------------------------------------------ constructor generico de escenas
def L(parts, cy, size, delay, pulse=0.0, rot=-4.0, gap=18):
    return (parts, cy, size, delay, pulse, rot, gap)


def build(lines, prop=None, m=None, extra=None, first=False, foot=None):
    m = m or {}
    for parts, cy, size, delay, pulse, rot, gap in lines:
        wsum = sum(text_w(tx, size) + (70 if st in ('h', 'y') else 0) for tx, st in parts) + gap * (len(parts) - 1)
        if wsum > 900:
            print("AVISO desborde:", [tx for tx, _ in parts], int(wsum))

    def fn(c, t, sp):
        u = t if first else t - 0.15
        background2(c, t)
        for parts, cy, size, delay, pulse, rot, gap in lines:
            tline(c, parts, cy, size, u, delay, rot, gap, pulse)
        if foot:
            ctext(c, foot, W / 2, 770, 26, 0xFF6B5F7A)
        if prop:
            prop(c, u, t)
        mascot2(c, m.get('x', 300), 1650, t, mood=m.get('mood', 'happy'), arm=m.get('arm', 'wave'),
                scale=m.get('scale', 1.0), speak=sp, look=m.get('look', (0, 0)), u=u)
        if m.get('zzz'):
            zzz(c, 420, 1250, t)
        if m.get('sweat'):
            sweat(c, 440, 1190, t)
        if extra:
            extra(c, u, t)
    return fn


def auto_pops(lines, first=False, extra=()):
    off = 0.0 if first else 0.15
    return [off + l[3] for l in lines] + [off + e for e in extra]


# ------------------------------------------------------------------ V1: escenas nuevas (cargadores)
def s4L(c, t, sp):
    u = t - OFF[3]
    background2(c, t)
    tline(c, [("Uno de", 'n'), ("20W", 'y')], 320, 80, u, 0.0, pulse_amp=0.03)
    tline(c, [("carga mucho", 'n')], 460, 80, u, 0.12)
    tline(c, [("MÁS RÁPIDO", 'h')], 620, 90, u, 0.25, pulse_amp=0.035)
    f = ease_out(clamp01((u - 0.5) / 2.4))
    pct = 15 + 75 * f
    if 0.5 < u < 2.9:
        speed_lines(c, 720, 1070, t)
    cp = cable_path(452, 1500, 720, 1318)
    draw_cable(c, cp, 1.0, 16)
    flow(c, cp, u, 1.3, 9, 22, bolts=True)
    phone(c, 720, 1070, pct, t, shake=2.0 if f < 0.98 else 0, scale=0.8 + 0.02 * math.sin(u * 20) * (1 if f < 0.98 else 0), charging=True)
    chip(c, 760, 760, "20W", YEL, INK, 60, ease_out_back((u - 0.4) / 0.35))
    if f > 0.97:
        sparkles(c, 720, 1070, u, 8, 270)
    mascot2(c, 300, 1650, t, mood="happy", arm="wave", speak=sp, look=(6, -6), u=u)
    ctext(c, "*ilustrativo, depende", 790, 1468, 24, 0xFF6B5F7A)
    ctext(c, "de que tu celular lo soporte", 790, 1498, 24, 0xFF6B5F7A)


def s_label(c, t, sp):
    u = t - 0.15
    background2(c, t)
    tline(c, [("Mira la", 'n')], 320, 80, u, 0.0)
    tline(c, [("etiqueta", 'h')], 460, 110, u, 0.12, pulse_amp=0.03)
    tline(c, [("ahí dice los vatios (W)", 'n')], 610, 54, u, 0.7)
    p = pp(u, 0.5)
    if p > 0.02:
        popbegin(c, 720, 1010, p)
        card(c, 510, 850, 420, 300, WHITE)
        draw_text(c, "SALIDA", 548, 902, 28, GRAYT)
        rrect(c, 548, 922, 190, 12, 6, fill=GRAY)
        rrect(c, 548, 946, 140, 12, 6, fill=GRAY)
        pul = 1 + 0.03 * math.sin(u * 8)
        ctext(c, "20W", 720, 1050, 124 * pul, INK)
        rrect(c, 572, 980, 296, 140, 70, line=PINK, lw=9)
        c.restore()
    if u > 0.9:
        k = ease_out(clamp01((u - 0.9) / 0.5))
        magnifier(c, 900 - 120 * k, 1190 - 110 * k, 62)
    mascot2(c, 300, 1650, t, mood="happy", arm="point", speak=sp, look=(10, -4), u=u)


def s_heat(c, t, sp):
    u = t - 0.15
    background2(c, t)
    tline(c, [("Elige uno de", 'n')], 320, 64, u, 0.0)
    tline(c, [("buena calidad", 'h')], 450, 100, u, 0.12, pulse_amp=0.03)
    tline(c, [("los malos pueden calentarse", 'n')], 610, 50, u, 0.9)
    cx, cy = 650, 1090
    for sx in (-34, 34):
        rrect(c, cx + sx - 13, cy - 150, 26, 62, 8, fill=GRAY, line=INK, lw=7)
    rrect(c, cx - 82, cy - 100, 164, 190, 42, fill=GRAY, line=INK, lw=8)
    zz = skia.Path()
    zz.moveTo(cx - 20, cy - 80)
    zz.lineTo(cx + 8, cy - 40)
    zz.lineTo(cx - 12, cy - 10)
    zz.lineTo(cx + 16, cy + 30)
    c.drawPath(zz, paint(INK, True, 7))
    heat = clamp01((u - 0.6) / 1.0)
    for k in range(3):
        x0 = cx - 44 + k * 44
        path = skia.Path()
        for j in range(0, 21):
            yy = cy - 170 - j * 8
            xx = x0 + math.sin(j * 0.7 + t * 8 + k) * 10
            path.moveTo(xx, yy) if j == 0 else path.lineTo(xx, yy)
        pnt = paint(RED, True, 9)
        pnt.setAlphaf(0.9 * heat)
        c.drawPath(path, pnt)
    # termometro
    top = 1190 - (60 + 190 * ease_out(clamp01((u - 1.0) / 1.4)))
    rrect(c, 826, 930, 32, 250, 16, fill=WHITE, line=INK, lw=7)
    rrect(c, 835, top, 14, 1186 - top, 7, fill=RED)
    oval(c, 842, 1200, 36, 36, fill=RED, line=INK, lw=7)
    for k in range(5):
        line(c, 800, 960 + k * 44, 818, 960 + k * 44, INK, 5)
    mascot2(c, 300, 1650, t, mood="sad", arm="down", speak=sp, look=(10, 4), u=u)
    sweat(c, 440, 1190, t)


# ------------------------------------------------------------------ V2: audifonos
def p_v2_hook(c, u, t):
    cx, cy = 700, 1010
    for i, (lab, dx, dy, d) in enumerate((("Gym", -90, 190, 0.5), ("Estudio", 130, 190, 0.9), ("Calle", 20, 290, 1.3))):
        bubble(c, cx + dx, cy + dy, 200 if len(lab) > 4 else 150, 70, lab, 36, [PINK, YEL, GREEN][i], WHITE if i != 1 else INK, pp(u, d))
    p = pp(u, 0.3)
    if p > 0.02:
        popbegin(c, cx, cy, p)
        earbud(c, cx - 36, cy - 10, 1.5, -8 + math.sin(u * 4) * 3)
        earbud(c, cx + 36, cy - 10, 1.5, 8 - math.sin(u * 4) * 3)
        c.restore()
    if u > 1.5:
        ctext(c, "?", cx + 190, cy - 170 + math.sin(u * 6) * 8, 90, PINK)


def p_v2_three(c, u, t):
    for i, (lab, d) in enumerate((("Ajuste", 1.3), ("Ruido", 1.8), ("Batería", 2.3))):
        p = pp(u, d)
        if p <= 0.02:
            continue
        cy = 900 + i * 140
        popbegin(c, 740, cy, p)
        card(c, 540, cy - 52, 390, 104, WHITE, 26)
        numcircle(c, 598, cy, i + 1, 32)
        ctext(c, lab, 760, cy, 48, INK)
        c.restore()


def p_v2_fit(c, u, t):
    run = math.sin(u * 9) * 10
    ear(c, 700, 1030, 1.15, True, run)
    for k in range(3):
        a = (u * 2 + k / 3) % 1
        line(c, 560 - a * 30, 960 + k * 40, 520 - a * 30, 960 + k * 40, PINK_L, 8)
    p = pp(u, 1.3)
    if p > 0.02:
        popbegin(c, 860, 900, p)
        rrect(c, 780, 860, 170, 80, 40, fill=GREEN, line=INK, lw=7)
        ctext(c, "firmes", 865, 900, 34, WHITE)
        c.restore()


def p_v2_anc(c, u, t):
    ear(c, 700, 1030, 1.15, True, 0)
    k = clamp01((u - 1.2) / 0.9)
    for i in range(4):
        a = (u * 1.2 + i / 4) % 1
        r = 140 + a * 150
        al = (1 - a) * (1 - 0.85 * k)
        ring(c, 700, 1030, r, PINK, al, 9)
    p = pp(u, 1.3)
    if p > 0.02:
        popbegin(c, 800, 830, p)
        rrect(c, 640, 795, 300, 70, 35, fill=GREEN, line=INK, lw=7)
        ctext(c, "menos ruido", 790, 830, 34, WHITE)
        c.restore()


def p_v2_battery(c, u, t):
    cx, cy = 740, 960
    popbegin(c, cx, cy, pp(u, 0.3))
    card(c, cx - 190, cy - 110, 380, 220, 0xFF2B2B38, 30)
    battery_icon(c, cx - 10, cy, 25 + 70 * ease_out(clamp01((u - 0.5) / 1.6)), 220, 120)
    c.restore()
    p = pp(u, 0.8)
    if p > 0.02:
        popbegin(c, 600, 1210, p)
        case_icon(c, 600, 1210, 1.0)
        c.restore()
        popbegin(c, 800, 1210, p)
        earbud(c, 770, 1190, 0.9, -10)
        earbud(c, 835, 1190, 0.9, 10)
        c.restore()
    if u > 1.4:
        ctext(c, "+ horas", 740, 1370, 46, PINK)


def p_v2_budget(c, u, t):
    for i, (lab, h, col, d) in enumerate((("básico", 150, GRAY, 0.4), ("medio", 250, PINK_L, 0.8), ("pro", 350, PINK, 1.2))):
        p = pp(u, d)
        if p <= 0.02:
            continue
        x = 580 + i * 150
        hh = h * clamp01(p)
        rrect(c, x, 1300 - hh, 120, hh, 24, fill=col, line=INK, lw=8)
        if p > 0.6:
            earbud(c, x + 60, 1300 - hh + 50, 0.6, 0)
            ctext(c, lab, x + 60, 1345, 32, INK)


# ------------------------------------------------------------------ V3: relojes
def p_v3_hook(c, u, t):
    price_tag(c, 760, 960, 420, 130, "2x1", 84, YEL, -6, pp(u, 0.35))
    for i, (x, s_, r, d, col) in enumerate(((620, 0.75, -10, 0.6, PINK_L), (850, 0.75, 10, 0.9, 0xFF9DD9FF))):
        p = pp(u, d)
        if p > 0.02:
            popbegin(c, x, 1250, p)
            watch(c, x, 1250 + math.sin(u * 4 + i) * 8, s_, "10:10", None, col, r)
            c.restore()


def p_v3_feat(c, u, t):
    watch(c, 740, 1020, 1.05, "10:10", "8.432 pasos")
    for lab, x, y, d, col in (("avisos", 590, 790, 1.0, PINK), ("pasos", 900, 880, 1.6, GREEN), ("hora", 600, 1290, 0.5, YEL)):
        bubble(c, x, y, 190, 64, lab, 32, col, INK if col == YEL else WHITE, pp(u, d))


def p_v3_notif(c, u, t):
    popbegin(c, 600, 1110, pp(u, 0.3))
    phone_begin(c, 600, 1180, 0.45)
    ctext(c, "zz", 0, 0, 90, 0xFF6B5F7A)
    c.restore()
    c.restore()
    watch(c, 790, 1040, 0.95, "10:10")
    for i, (txt, y, d) in enumerate((("Mensaje nuevo", 780, 0.8), ("Llamada", 880, 1.4))):
        bubble(c, 800, y, 320, 66, txt, 30, WHITE if i else PINK, INK if i else WHITE, pp(u, d))


def p_v3_list(c, u, t):
    popbegin(c, 740, 1020, pp(u, 0.3))
    card(c, 520, 780, 430, 520, WHITE, 30)
    c.restore()
    rows = (("Notificaciones", True, 0.8), ("Pasos y más", True, 1.2), ("Buen precio", True, 1.6), ("No es premium", False, 2.2))
    for i, (lab, ok, d) in enumerate(rows):
        p = pp(u, d)
        if p <= 0.02:
            continue
        y = 850 + i * 112
        popbegin(c, 740, y, p)
        (check_icon if ok else cross_icon)(c, 574, y, 22, GREEN if ok else RED)
        draw_text(c, lab, 618, y + 14, 36, INK)
        c.restore()


def p_v3_compat(c, u, t):
    popbegin(c, 600, 1050, pp(u, 0.3))
    phone_begin(c, 600, 1050, 0.6)
    ctext(c, "OK", 0, 0, 90, GREEN)
    c.restore()
    c.restore()
    watch(c, 860, 1050, 0.85, "10:10")
    for k in range(5):
        a = (u * 1.5 + k / 5) % 1
        c.drawCircle(690 + a * 90, 1050, 9, paint(YEL))
        c.drawCircle(690 + a * 90, 1050, 9, paint(INK, True, 4))
    if u > 1.4:
        popbegin(c, 740, 800, pp(u, 1.4))
        check_icon(c, 740, 800, 46, GREEN)
        c.restore()


def p_v3_pay(c, u, t):
    price_tag(c, 740, 900, 420, 130, "2x1", 84, YEL, -5, pp(u, 0.35))
    bubble(c, 740, 1060, 360, 84, "a cuotas", 44, PINK, WHITE, pp(u, 1.4))
    bubble(c, 740, 1170, 400, 76, "Sistecrédito", 38, WHITE, INK, pp(u, 1.8))


# ------------------------------------------------------------------ V4: Sistecredito
def p_v4_hook(c, u, t):
    k = 1.0
    balance(c, 700, 960, 14 * (1 if u < 5 else 0), 2, True)


def p_v4_solution(c, u, t):
    k = ease_out(clamp01((u - 0.6) / 1.0))
    balance(c, 700, 960, 14 * (1 - k), 2 + int(3 * k), True)


def p_v4_approval(c, u, t):
    phone_begin(c, 720, 1030, 0.82)
    ctext(c, "Tu solicitud", 0, -150, 38, WHITE)
    rrect(c, -110, -90, 220, 26, 13, fill=0xFF3A3A4A)
    prog = ease_out(clamp01((u - 0.6) / 1.5))
    rrect(c, -110, -90, 220 * prog, 26, 13, fill=YEL if prog < 1 else GREEN)
    if prog >= 1:
        check_icon(c, 0, 60, 54, GREEN)
        ctext(c, "lista", 0, 160, 44, WHITE)
    else:
        ctext(c, "revisando...", 0, 60, 40, WHITE)
    c.restore()


def p_v4_steps(c, u, t):
    for i, (lab, d) in enumerate((("Elige tu producto", 0.9), ("Escríbenos", 1.5), ("Te contamos cómo", 2.1))):
        p = pp(u, d)
        if p <= 0.02:
            continue
        cy = 820 + i * 150
        popbegin(c, 700, cy, p)
        card(c, 480, cy - 55, 430, 110, WHITE, 26)
        numcircle(c, 538, cy, i + 1, 32)
        draw_text(c, lab, 590, cy + 12, 34, INK)
        c.restore()


def p_v4_conditions(c, u, t):
    popbegin(c, 720, 1050, pp(u, 0.3))
    doc_icon(c, 720, 1050)
    c.restore()
    if u > 0.8:
        k = ease_out(clamp01((u - 0.8) / 0.6))
        magnifier(c, 820 - 30 * math.sin(u * 3), 1020 + 20 * k, 70)
    if u > 1.8:
        popbegin(c, 900, 870, pp(u, 1.8))
        check_icon(c, 900, 870, 40, GREEN)
        c.restore()


def p_v4_clients(c, u, t):
    n = int(150 * ease_out(clamp01((u - 0.4) / 1.6)))
    ctext(c, f"+{n}", 740, 940, 150, PINK)
    cols = [PINK_L, YEL, 0xFF9DD9FF, GREEN_S, PINK_L, YEL, 0xFF9DD9FF, GREEN_S]
    for i in range(8):
        p = pp(u, 0.8 + i * 0.12)
        if p > 0.02:
            x = 560 + (i % 4) * 100
            y = 1090 + (i // 4) * 105
            popbegin(c, x, y, p)
            smiley(c, x, y, 38, cols[i])
            c.restore()



# ------------------------------------------------------------------ C1: cargadores (cuadricula estricta, sin textos de calidad/calentamiento)
def pc_1(c, u, t):
    for k in range(3):
        a = (u * 1.1 + k / 3) % 1
        ring(c, 790, 860, 40 + a * 150, RED, 0.8 * (1 - a), 8)
    blink_on = (u * 2.2) % 1 < 0.6
    phone(c, 720, 1070, 15, t, shake=4 * (1 if u % 1.1 < 0.45 else 0.2), low=blink_on, scale=0.8)


def pc_2(c, u, t):
    if u > 1.0:
        d = math.sin(u * 8) * 10
        p = skia.Path()
        p.moveTo(800, 790 + d)
        p.lineTo(840, 750 + d)
        p.lineTo(820, 750 + d)
        p.lineTo(820, 710 + d)
        p.lineTo(780, 710 + d)
        p.lineTo(780, 750 + d)
        p.lineTo(760, 750 + d)
        p.close()
        c.drawPath(p, paint(YEL))
        c.drawPath(p, paint(INK, True, 7))
    phone(c, 720, 1100, 15, t, low=False, scale=0.8)


def pc_3(c, u, t):
    pct = 15 + 6 * clamp01(u / 4.0)
    cp = cable_path(452, 1500, 720, 1348)
    draw_cable(c, cp, 1.0, 16)
    flow(c, cp, u, 0.12, 3, 11)
    phone(c, 720, 1100, pct, t, scale=0.8)
    chip(c, 800, 800, "5W", GRAY, INK, 60, ease_out_back((u - 0.5) / 0.35))
    tx = 580 + 190 * ease_io(clamp01(u / 4.0))
    turtle(c, tx, 1650, t, 1.15)


def pc_4(c, u, t):
    f = ease_out(clamp01((u - 0.5) / 2.4))
    pct = 15 + 75 * f
    if 0.5 < u < 2.9:
        speed_lines(c, 720, 1100, t)
    cp = cable_path(452, 1500, 720, 1348)
    draw_cable(c, cp, 1.0, 16)
    flow(c, cp, u, 1.3, 9, 22, bolts=True)
    phone(c, 720, 1100, pct, t, shake=2.0 if f < 0.98 else 0, scale=0.8, charging=True)
    chip(c, 800, 800, "20W", YEL, INK, 60, ease_out_back((u - 0.4) / 0.35))
    if f > 0.97:
        sparkles(c, 720, 1100, u, 8, 270)


def pc_5(c, u, t):
    p = pp(u, 0.5)
    if p > 0.02:
        popbegin(c, 720, 1050, p)
        card(c, 510, 890, 420, 300, WHITE)
        draw_text(c, "SALIDA", 548, 942, 28, GRAYT)
        rrect(c, 548, 962, 190, 12, 6, fill=GRAY)
        rrect(c, 548, 986, 140, 12, 6, fill=GRAY)
        ctext(c, "20W", 720, 1090, 124 * (1 + 0.03 * math.sin(u * 8)), INK)
        rrect(c, 572, 1020, 296, 140, 70, line=PINK, lw=9)
        c.restore()
    if u > 0.9:
        k = ease_out(clamp01((u - 0.9) / 0.5))
        magnifier(c, 900 - 120 * k, 1230 - 110 * k, 62)


def pc_6(c, u, t):
    cp = cable_path(452, 1500, 760, 1353)
    bad = u < 1.5
    if bad:
        if ease_out(clamp01((u - 0.3) / 0.5)) > 0.05:
            bad_cable(c, cp, t)
            flow(c, cp, u, 0.18, 2, 8)
        phone(c, 760, 1130, 20, t, scale=0.72, charging=True, low=False)
        x_mark(c, 640, 1440, 44, ease_out_back((u - 0.6) / 0.3))
        chip(c, 790, 1590, "incompatible", RED, WHITE, 40, ease_out_back((u - 0.55) / 0.35), rot=0)
    else:
        draw_cable(c, cp, 1.0, 18)
        flow(c, cp, u, 1.2, 8, 22, bolts=True)
        pct = 20 + 70 * ease_out(clamp01((u - 1.5) / 1.4))
        phone(c, 760, 1130, pct, t, scale=0.72, charging=True)
        chip(c, 790, 1590, "compatible", GREEN, WHITE, 40, ease_out_back((u - 1.55) / 0.35), rot=0)
        if clamp01((u - 1.5) / 0.5) > 0.3:
            sparkles(c, 760, 1130, u, 6, 240)


def pc_7(c, u, t):
    pct = 30 + 60 * ease_out(clamp01((u - 0.5) / 2.0))
    phone(c, 700, 1100, pct, t, scale=0.8, charging=True)
    p = pp(u, 1.2)
    if p > 0.02:
        popbegin(c, 900, 830, p)
        oval(c, 900, 830, 58, 58, fill=GREEN, line=INK, lw=8)
        check_icon(c, 900, 832, 26, WHITE)
        c.restore()


# ------------------------------------------------------------------ CTA generico
def cta_prop(c, u, t):
    k = clamp01((u - 1.0) / 0.35)
    chip(c, 540, 900, "@inizitech", PINK, WHITE, 64, ease_out_back(k) * (1 + (0.04 * math.sin(u * 8) if k >= 1 else 0)), rot=-3)
    confetti(c, 540, 900, u - 1.0)
    sparkles(c, 540, 1250, u, 7, 330)


def cta_scene(lines, extra_foot=None):
    return build(lines, cta_prop, dict(x=540, scale=1.05, mood='happy', arm='wave'), foot=extra_foot)


# ------------------------------------------------------------------ definicion de los videos
def lines_cta1():
    return [L([("¿Cuál te", 'n')], 320, 80, 0.0), L([("conviene?", 'h')], 490, 110, 0.12, 0.03),
            L([("Escríbenos por DM", 'n')], 690, 62, 0.7)]



def p_v4_steps2(c, u, t):
    for i, (lab, d) in enumerate((("Elige tu producto", 1.2), ("Escríbenos", 2.5), ("Te contamos cómo", 3.7))):
        p = pp(u, d)
        if p <= 0.02:
            continue
        cy = 820 + i * 150
        popbegin(c, 700, cy, p)
        card(c, 480, cy - 55, 430, 110, WHITE, 26)
        numcircle(c, 538, cy, i + 1, 32)
        draw_text(c, lab, 590, cy + 12, 34, INK)
        c.restore()


def p_v2_anc2(c, u, t):
    p_v2_anc(c, u - 1.6, t)


def p_v2_battery2(c, u, t):
    cx, cy = 740, 960
    popbegin(c, cx, cy, pp(u, 0.3))
    card(c, cx - 190, cy - 110, 380, 220, 0xFF2B2B38, 30)
    battery_icon(c, cx - 10, cy, 25 + 70 * ease_out(clamp01((u - 2.2) / 1.6)), 220, 120)
    c.restore()
    p = pp(u, 2.2)
    if p > 0.02:
        popbegin(c, 600, 1210, p)
        case_icon(c, 600, 1210, 1.0)
        c.restore()
        popbegin(c, 800, 1210, p)
        earbud(c, 770, 1190, 0.9, -10)
        earbud(c, 835, 1190, 0.9, 10)
        c.restore()
    if u > 3.2:
        ctext(c, "+ horas", 740, 1370, 46, PINK)


def p_v2_hook2(c, u, t):
    cx, cy = 700, 1010
    for i, (lab, dx, dy, d) in enumerate((("Gym", -90, 190, 0.6), ("Estudio", 130, 190, 1.0), ("Calle", 20, 290, 1.4))):
        bubble(c, cx + dx, cy + dy, 200 if len(lab) > 4 else 150, 70, lab, 36, [PINK, YEL, GREEN][i], WHITE if i != 1 else INK, pp(u, d))
    p = pp(u, 0.3)
    if p > 0.02:
        popbegin(c, cx, cy, p)
        earbud(c, cx - 36, cy - 10, 1.5, -8 + math.sin(u * 4) * 3)
        earbud(c, cx + 36, cy - 10, 1.5, 8 - math.sin(u * 4) * 3)
        c.restore()


def V(fn, pops, voice_key, dings=()):
    return dict(fn=fn, pops=pops, voice=voice_key, dings=list(dings))


def make_videos():
    v = {}
    # ---- V1 cargadores (largo)
    v['v1'] = [
        V(s1, [0.0, 0.15], 'v1_1'),
        V(s2, [0.15, 0.25, 1.15], 'v1_2'),
        V(s3, [0.15, 0.27, 0.85, 0.65], 'v1_3'),
        V(s4L, [0.15, 0.27, 0.40, 0.55], 'v1_4', [3.05]),
        V(s_label, [0.15, 0.27, 0.85, 0.65], 'v1_5'),
        V(s5, [0.15, 0.27, 0.40, 0.75, 1.65], 'v1_6', [1.75]),
        V(s_heat, [0.15, 0.27, 1.05], 'v1_7'),
        V(s6, [0.15, 0.27, 0.85, 1.15], 'v1_8', [1.15]),
    ]
    # ---- V2 audifonos
    l = [L([("¿Los", 'n'), ("MISMOS", 'h')], 330, 90, 0.0, 0.03), L([("audífonos para todo?", 'n')], 470, 60, 0.15)]
    s_hook2 = build(l, p_v2_hook, dict(mood='wink', arm='point', look=(10, -4)), first=True)
    l2 = [L([("Antes de comprar,", 'n')], 320, 60, 0.0), L([("fíjate en", 'n'), ("3", 'y')], 450, 90, 0.12),
          L([("cosas", 'h')], 600, 100, 0.25)]
    s_3 = build(l2, p_v2_three, dict(mood='happy', arm='point', look=(10, -4)))
    l3 = [L([("1.", 'y'), ("Ajuste", 'h')], 330, 96, 0.0, 0.03), L([("que no se te caigan", 'n')], 480, 58, 0.15)]
    s_fit = build(l3, p_v2_fit, dict(mood='happy', arm='wave'))
    l4 = [L([("2.", 'y'), ("Ruido", 'h')], 330, 96, 0.0, 0.03), L([("la cancelación de ruido", 'n')], 480, 52, 0.15),
          L([("baja los sonidos de afuera", 'n')], 560, 44, 0.5)]
    s_anc = build(l4, p_v2_anc, dict(mood='happy', arm='wave'))
    l5 = [L([("3.", 'y'), ("Batería", 'h')], 330, 96, 0.0, 0.03), L([("revisa las horas", 'n')], 480, 58, 0.15),
          L([("con y sin estuche", 'n')], 560, 50, 0.5)]
    s_bat = build(l5, p_v2_battery, dict(mood='happy', arm='wave'))
    l6 = [L([("Y según tu", 'n')], 320, 70, 0.0), L([("presupuesto", 'h')], 450, 100, 0.12, 0.03),
          L([("hay opciones", 'n')], 610, 60, 0.7), L([("para cada uso", 'n')], 690, 60, 0.9)]
    s_bud = build(l6, p_v2_budget, dict(mood='wink', arm='point'))
    l7 = [L([("Cuéntanos", 'n')], 320, 80, 0.0), L([("cómo los usas", 'h')], 450, 90, 0.12, 0.03),
          L([("y te decimos cuál te conviene", 'n')], 610, 46, 0.6), L([("Escríbenos por DM", 'n')], 700, 56, 1.0)]
    s_cta2 = cta_scene(l7)
    v['v2'] = [
        V(s_hook2, auto_pops(l, True, (0.3, 0.5, 0.9, 1.3)), 'v2_1'),
        V(s_3, auto_pops(l2, False, (1.3, 1.8, 2.3)), 'v2_2'),
        V(s_fit, auto_pops(l3, False, (1.3,)), 'v2_3'),
        V(s_anc, auto_pops(l4, False, (1.3,)), 'v2_4'),
        V(s_bat, auto_pops(l5, False, (0.3, 0.8)), 'v2_5'),
        V(s_bud, auto_pops(l6, False, (0.4, 0.8, 1.2)), 'v2_6'),
        V(s_cta2, auto_pops(l7, False, (1.0,)), 'v2_7', [1.15]),
    ]
    # ---- V3 relojes 2x1
    a = [L([("2x1", 'y'), ("en relojes", 'n')], 330, 84, 0.0, 0.03), L([("$110.000", 'h')], 480, 120, 0.15, 0.03)]
    s_h3 = build(a, p_v3_hook, dict(mood='wink', arm='point'), first=True, foot="*promo sujeta a disponibilidad")
    b = [L([("¿Qué hace un", 'n')], 320, 70, 0.0), L([("reloj inteligente?", 'h')], 450, 76, 0.12, 0.03)]
    s_f3 = build(b, p_v3_feat, dict(mood='happy', arm='point'))
    cc = [L([("Sin sacar", 'n')], 320, 80, 0.0), L([("el celular", 'h')], 450, 100, 0.12, 0.03), L([("ves tus avisos", 'n')], 610, 60, 0.7)]
    s_n3 = build(cc, p_v3_notif, dict(mood='happy', arm='wave'))
    d = [L([("Lo que", 'n'), ("sí", 'h')], 320, 80, 0.0), L([("y lo que no", 'n')], 450, 80, 0.12)]
    s_l3 = build(d, p_v3_list, dict(mood='wink', arm='point'))
    e = [L([("Revisa que sea", 'n')], 320, 64, 0.0), L([("compatible", 'h')], 450, 100, 0.12, 0.03), L([("con tu celular", 'n')], 610, 64, 0.7)]
    s_c3 = build(e, p_v3_compat, dict(mood='happy', arm='point'))
    f = [L([("Pregunta por", 'n')], 320, 64, 0.0), L([("la promo 2x1", 'h')], 450, 90, 0.12, 0.03), L([("y pagarlo a cuotas", 'n')], 610, 60, 0.7)]
    s_p3 = build(f, p_v3_pay, dict(mood='happy', arm='wave'), foot="*sujeto a aprobación y condiciones")
    v['v3'] = [
        V(s_h3, auto_pops(a, True, (0.35, 0.6, 0.9)), 'v3_1'),
        V(s_f3, auto_pops(b, False, (0.5, 1.0, 1.6)), 'v3_2'),
        V(s_n3, auto_pops(cc, False, (0.8, 1.4)), 'v3_3'),
        V(s_l3, auto_pops(d, False, (0.8, 1.2, 1.6, 2.2)), 'v3_4'),
        V(s_c3, auto_pops(e, False, (1.4,)), 'v3_5', [1.55]),
        V(s_p3, auto_pops(f, False, (0.35, 1.4, 1.8)), 'v3_6'),
        V(s6, [0.15, 0.27, 0.85, 1.15], 'v1_8', [1.15]),
    ]
    # ---- V4 Sistecredito
    def T(t1, t2, sub=None, subp='n', subsize=46, delay_sub=0.7):
        r = [L([(t1, 'n')], 330, 76, 0.0, 0.0, 0.0), L([(t2, 'h')], 480, 104, 0.12, 0.03, 0.0)]
        if sub:
            r.append(L([(sub, subp)], 640, subsize, delay_sub, 0.0, 0.0))
        return r
    g = T("¿Quieres un", "accesorio", "y hoy no tienes todo el dinero?")
    s_h4 = build(g, p_v4_hook, dict(mood='sad', arm='down', sweat=True, look=(10, 6)), first=True)
    h = T("Paga a", "CUOTAS", "con Sistecrédito", 'y', 56, 0.5)
    s_s4 = build(h, p_v4_solution, dict(mood='happy', arm='wave'))
    i_ = T("Aprobación", "rápida", "sujeta a condiciones", 'n', 46, 0.9)
    s_a4 = build(i_, p_v4_approval, dict(mood='happy', arm='point'))
    j = T("Así de", "fácil")
    s_t4 = build(j, p_v4_steps, dict(mood='wink', arm='point'))
    k_ = T("Lee bien las", "condiciones", "y compra lo que necesitas")
    s_c4 = build(k_, p_v4_conditions, dict(mood='happy', arm='point'))
    m_ = T("Más de", "150 clientes", "ya compraron en Inizitech")
    s_k4 = build(m_, p_v4_clients, dict(mood='happy', arm='wave'))
    n_ = T("¿Lo quieres", "a cuotas?", "Escríbenos por DM", 'n', 56)
    s_cta4 = cta_scene(n_)
    v['v4'] = [
        V(s_h4, auto_pops(g, True), 'v4_1'),
        V(s_s4, auto_pops(h, False), 'v4_2'),
        V(s_a4, auto_pops(i_, False, (0.6,)), 'v4_3', [2.2]),
        V(s_t4, auto_pops(j, False, (0.9, 1.5, 2.1)), 'v4_4'),
        V(s_c4, auto_pops(k_, False, (1.8,)), 'v4_5', [1.95]),
        V(s_k4, auto_pops(m_, False, (0.8, 0.92, 1.04)), 'v4_6'),
        V(s_cta4, auto_pops(n_, False, (1.0,)), 'v4_7', [1.15]),
    ]
    # ---- C1 cargadores (30 s, cuadricula estricta)
    def Tc(t1, t2, sub=None):
        r = [L([(t1, 'n')], 330, 76, 0.0, 0.0, 0.0), L([(t2, 'h')], 480, 104, 0.12, 0.03, 0.0)]
        if sub:
            r.append(L([(sub, 'n')], 640, 60, 0.7, 0.0, 0.0))
        return r
    q1 = Tc("¿Tu celular carga", "LENTO?")
    q2 = Tc("Casi siempre", "el culpable", "es el cargador")
    q3 = Tc("Uno de 5W va", "muy lento", "a paso de tortuga")
    q4 = Tc("Uno de 20W carga", "MÁS RÁPIDO", "si tu celular lo soporta")
    q5 = Tc("Mira la", "etiqueta", "ahí dice los vatios")
    q6 = Tc("Y el cable también", "cuenta", "usa uno compatible")
    q7 = Tc("Revisa que sea", "compatible", "con tu celular")
    q8 = Tc("¿Cuál te", "conviene?", "Escríbenos por DM")
    v['c1'] = [
        V(build(q1, pc_1, dict(mood='sad', arm='down', sweat=True, look=(10, 8)), first=True), auto_pops(q1, True, (0.8, 1.6)), 'c1_1'),
        V(build(q2, pc_2, dict(mood='wink', arm='point', look=(10, -4))), auto_pops(q2, False, (1.0,)), 'c1_2'),
        V(build(q3, pc_3, dict(mood='yawn', arm='down', zzz=True)), auto_pops(q3, False, (0.5,)), 'c1_3'),
        V(build(q4, pc_4, dict(mood='happy', arm='wave', look=(6, -6))), auto_pops(q4, False, (0.4,)), 'c1_4', [2.7]),
        V(build(q5, pc_5, dict(mood='happy', arm='point', look=(10, -4))), auto_pops(q5, False, (0.5,)), 'c1_5'),
        V(build(q6, pc_6, dict(mood='happy', arm='wave', look=(8, -4))), auto_pops(q6, False, (0.6, 1.55)), 'c1_6', [1.7]),
        V(build(q7, pc_7, dict(mood='happy', arm='point')), auto_pops(q7, False, (1.2,)), 'c1_7', [1.3]),
        V(cta_scene(q8), auto_pops(q8, False, (1.0,)), 'c1_8', [1.15]),
    ]
    # ---- A2 audifonos (muneco, guion aprobado)
    A1 = [L([("¿Vas a comprar", 'n')], 330, 70, 0.0), L([("audífonos?", 'h')], 480, 110, 0.12, 0.03), L([("fíjate en estas", 'n'), ("3", 'y'), ("cosas", 'n')], 640, 50, 1.7)]
    A2 = [L([("1.", 'y'), ("Ajuste", 'h')], 330, 96, 0.0, 0.03), L([("que no se te caigan", 'n')], 480, 58, 1.3)]
    A3 = [L([("2.", 'y'), ("Ruido", 'h')], 330, 96, 0.0, 0.03), L([("la cancelación de ruido", 'n')], 480, 52, 0.7), L([("baja los sonidos de afuera", 'n')], 560, 48, 3.0)]
    A4 = [L([("3.", 'y'), ("Batería", 'h')], 330, 96, 0.0, 0.03), L([("mira las horas", 'n')], 480, 58, 1.8), L([("con y sin estuche", 'n')], 560, 50, 2.9)]
    A5 = [L([("Y según tu", 'n')], 320, 70, 0.0), L([("presupuesto", 'h')], 450, 100, 0.12, 0.03), L([("hay opciones", 'n')], 610, 60, 0.9), L([("para cada uso", 'n')], 690, 60, 1.3)]
    A6 = [L([("Cuéntanos", 'n')], 320, 80, 0.0), L([("cómo los usas", 'h')], 450, 90, 0.12, 0.03), L([("y te decimos cuál te conviene", 'n')], 610, 50, 1.9)]
    A7 = [L([("Escríbenos", 'n')], 320, 80, 0.0), L([("por mensaje", 'n')], 450, 90, 0.12), L([("directo", 'h')], 600, 120, 0.35, 0.03)]
    v['a2'] = [
        V(build(A1, p_v2_three, dict(mood='wink', arm='point', look=(10, -4)), first=True), auto_pops(A1, True, (1.3, 1.8, 2.3)), 'a2_1'),
        V(build(A2, p_v2_fit, dict(mood='happy', arm='wave')), auto_pops(A2, False, (1.3,)), 'a2_2'),
        V(build(A3, p_v2_anc2, dict(mood='happy', arm='wave')), auto_pops(A3, False, (3.0,)), 'a2_3'),
        V(build(A4, p_v2_battery2, dict(mood='happy', arm='wave')), auto_pops(A4, False, (2.4, 3.4)), 'a2_4'),
        V(build(A5, p_v2_budget, dict(mood='wink', arm='point')), auto_pops(A5, False, (0.4, 0.8, 1.2)), 'a2_5'),
        V(build(A6, p_v2_hook2, dict(mood='happy', arm='point', look=(10, -4))), auto_pops(A6, False, (0.6, 1.0, 1.4)), 'a2_6'),
        V(cta_scene(A7), auto_pops(A7, False, (1.0,)), 'a2_7', [1.15]),
    ]
    # ---- S2 Sistecredito (muneco, guion aprobado)
    S1 = T("¿Quieres un", "accesorio", "y hoy no tienes todo el dinero?", 'n', 52)
    S2 = T("Paga a", "CUOTAS", "con Sistecrédito", 'y', 56, 0.9)
    S3 = T("Así de", "fácil")
    S4 = T("Sujeto a", "aprobación", "y condiciones, léelas bien", 'n', 52, 1.2)
    S5 = T("Más de", "150 clientes", "ya han comprado en Inizitech", 'n', 52, 1.0)
    S6 = T("¿Lo quieres", "a cuotas?", "Escríbenos por mensaje directo", 'n', 50)
    v['s2'] = [
        V(build(S1, p_v4_hook, dict(mood='sad', arm='down', sweat=True, look=(10, 6)), first=True), auto_pops(S1, True), 's2_1'),
        V(build(S2, p_v4_solution, dict(mood='happy', arm='wave')), auto_pops(S2, False), 's2_2'),
        V(build(S3, p_v4_steps2, dict(mood='wink', arm='point')), auto_pops(S3, False, (1.2, 2.5, 3.7)), 's2_3'),
        V(build(S4, p_v4_conditions, dict(mood='happy', arm='point')), auto_pops(S4, False, (1.9,)), 's2_4', [2.05]),
        V(build(S5, p_v4_clients, dict(mood='happy', arm='wave')), auto_pops(S5, False, (0.8, 0.92, 1.04)), 's2_5'),
        V(cta_scene(S6), auto_pops(S6, False, (1.0,)), 's2_6', [1.15]),
    ]
    # ---- videos nuevos: archivo videos_extra.py dentro de la carpeta de trabajo (INIZI_OUT/../videos_extra.py o INIZI_EXTRA)
    _extra = os.environ.get("INIZI_EXTRA", os.path.join(OUT, "videos_extra.py"))
    if os.path.exists(_extra):
        exec(compile(open(_extra).read(), _extra, "exec"), dict(globals(), v=v, T=T))
    return v


# ------------------------------------------------------------------ preparacion de audio, duraciones, render
CUR = {}


def ffprobe_dur(p):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", p])
    return float(out.decode().strip())


def prep(name, spec, vdir, raw):
    os.makedirs(vdir, exist_ok=True)
    durs, starts, acc = [], [], 0.0
    for i, sc in enumerate(spec):
        rd = ffprobe_dur(raw[sc['voice']])
        tail = 0.3 if name == 'c1' else 0.5
        d = math.ceil((rd + 0.3 + tail) * 10) / 10
        d = max(d, 2.8 if name == 'c1' else 3.0)
        durs.append(d)
        starts.append(acc)
        acc += d
        vp = f"{vdir}/voz{i+1}.wav"
        tmp = vp.replace(".wav", "_tmp.wav")
        subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", raw[sc['voice']], "-af",
                               f"aresample=44100,pan=stereo|c0=c0|c1=c0,adelay=300|300,apad=whole_dur={d},atrim=0:{d}",
                               "-ar", "44100", "-c:a", "pcm_s16le", tmp])
        os.replace(tmp, vp)
    with open(f"{vdir}/list.txt", "w") as f:
        for i in range(len(spec)):
            f.write(f"file 'voz{i+1}.wav'\n")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{vdir}/list.txt",
                           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", f"{vdir}/voz_total_tmp.wav"])
    os.replace(f"{vdir}/voz_total_tmp.wav", f"{vdir}/voz_total.wav")
    json.dump(dict(durs=durs, starts=starts), open(f"{vdir}/timing.json", "w"))
    print(name, "dur total", round(acc, 1), [round(x, 1) for x in durs])


def env_from(path, dur):
    w = wave.open(path)
    n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch)[:, 0].astype(np.float32) / 32768
    hop = sr / FPS
    nf = int(round(dur * FPS))
    env = []
    for i in range(nf):
        c0 = int(i * hop)
        s = a[max(0, c0 - int(hop * 0.6)): c0 + int(hop * 0.6)]
        env.append(float(np.sqrt(np.mean(s ** 2))) if len(s) else 0.0)
    env = np.array(env)
    m = np.percentile(env, 95) or 1e-6
    env = np.clip(env / m, 0, 1)
    env = np.convolve(env, np.array([0.25, 0.5, 0.25]), mode="same")
    env[env < 0.12] = 0.0
    return env


def load_video(name, with_env=True):
    spec = make_videos()[name]
    vdir = f"{OUT}/{name}"
    tm = json.load(open(f"{vdir}/timing.json"))
    CUR.update(name=name, spec=spec, durs=tm['durs'], starts=tm['starts'], vdir=vdir)
    if with_env:
        CUR['env'] = [env_from(f"{vdir}/voz{i+1}.wav", tm['durs'][i]) for i in range(len(spec))]


def render_frame_g(idx, t, i=None):
    fi = int(round(t * FPS)) if i is None else i
    env = CUR['env'][idx]
    sp = float(env[min(fi, len(env) - 1)])
    dur = CUR['durs'][idx]
    n = len(CUR['spec'])
    surface = skia.Surface.MakeRaster(INFO)
    c = surface.getCanvas()
    z = 1.0 + 0.045 * (t / dur)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    CUR['spec'][idx]['fn'](c, t, sp)
    c.restore()
    if idx > 0 and t < 0.32:
        panel(c, "out", t / 0.32, t)
    if idx < n - 1 and t > dur - 0.26:
        panel(c, "in", (t - (dur - 0.26)) / 0.26, t)
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)


def render_scene_g(idx, outpath):
    n = int(round(CUR['durs'][idx] * FPS))
    tmp = outpath.replace(".mp4", "_tmp.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        arr = render_frame_g(idx, i / FPS, i)
        proc.stdin.write(np.ascontiguousarray(arr[:, :, :4]).tobytes())
    proc.stdin.close()
    if proc.wait() == 0:
        os.replace(tmp, outpath)
    else:
        raise SystemExit(f"ffmpeg fallo en escena {idx+1}")


def make_sfx_g(path):
    sr = 44100
    durs, starts, spec = CUR['durs'], CUR['starts'], CUR['spec']
    total = int(sum(durs) * sr)
    out = np.zeros(total, dtype=np.float32)

    def add(t0, sig, gain=1.0):
        i0 = int(t0 * sr)
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        j = min(total, i0 + len(sig))
        if j > i0:
            out[i0:j] += sig[: j - i0] * gain

    def pop(f0=900, f1=450, dur=0.09):
        t = np.arange(int(dur * sr)) / sr
        f = f0 + (f1 - f0) * (t / dur)
        ph = 2 * np.pi * np.cumsum(f) / sr
        return (np.sin(ph) * np.exp(-t * 38)).astype(np.float32)

    def ding():
        t = np.arange(int(0.9 * sr)) / sr
        s = np.sin(2 * np.pi * 1320 * t) + 0.6 * np.sin(2 * np.pi * 1980 * t) + 0.3 * np.sin(2 * np.pi * 2640 * t)
        return (s * np.exp(-t * 5) * 0.5).astype(np.float32)

    def whoosh(dur=0.5, seed=0):
        rng = np.random.default_rng(seed)
        n = int(dur * sr)
        x = rng.standard_normal(n).astype(np.float32)
        y = np.zeros(n, dtype=np.float32)
        prev = 0.0
        for k in range(n):
            a = 0.02 + 0.38 * math.sin(math.pi * k / n) ** 1.5
            prev += a * (x[k] - prev)
            y[k] = prev
        env = np.sin(np.linspace(0, np.pi, n)) ** 1.4
        y = y * env
        return y / (np.max(np.abs(y)) + 1e-6)

    for idx, sc in enumerate(spec):
        for tt in sc['pops']:
            add(starts[idx] + tt, pop(), 0.55)
        for tt in sc['dings']:
            add(starts[idx] + tt, ding(), 0.5)
    for k, T in enumerate(starts[1:]):
        add(T - 0.26, whoosh(0.5, k), 0.7)
    if CUR['name'] == 'v1':
        add(0.8, pop(1000, 1000, 0.07), 0.25)
        add(1.6, pop(1000, 1000, 0.07), 0.25)
    out = out / max(1e-6, float(np.max(np.abs(out)))) * 0.9
    pcm = (np.stack([out, out], axis=1) * 32767).astype(np.int16)
    w = wave.open(path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
    w.close()


if __name__ == "__main__":
    name, mode = sys.argv[1], sys.argv[2]
    vdir = f"{OUT}/{name}"
    if mode == "prep":
        raw = json.load(open(f"{vdir}/raw.json"))
        prep(name, make_videos()[name], vdir, raw)
    elif mode == "stills":
        load_video(name)
        os.makedirs(f"{vdir}/stills", exist_ok=True)
        n = len(CUR['spec'])
        for i in range(n):
            d = CUR['durs'][i]
            tt = min(d - 0.5, 2.3 if d > 3.0 else 1.9)
            arr = render_frame_g(i, tt)
            skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(f"{vdir}/stills/s{i+1}.png", skia.kPNG)
        print("stills ok", n)
    elif mode == "scene":
        load_video(name)
        i = int(sys.argv[3]) - 1
        render_scene_g(i, f"{vdir}/scene{i+1}.mp4")
        print("scene ok")
    elif mode == "render":
        load_video(name)
        for i in range(len(CUR['spec'])):
            render_scene_g(i, f"{vdir}/scene{i+1}.mp4")
        make_sfx_g(f"{vdir}/sfx.wav")
        print("render ok", sum(CUR['durs']))
    elif mode == "sfx":
        load_video(name, with_env=False)
        make_sfx_g(f"{vdir}/sfx.wav")
        print("sfx ok")
