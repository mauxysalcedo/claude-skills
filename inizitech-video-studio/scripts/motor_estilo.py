import math, os, subprocess, sys, wave
import numpy as np
import skia

# ---- reutiliza las primitivas de dibujo de la v1 (colores, rrect, oval, texto, phone, chip...)
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'motor_base.py')).read().split("# ---------------------------------------------------------------- escenas")[0]
exec(_src)

OUT = os.environ.get("INIZI_OUT", "/tmp/inizi_out")
DUR = [3.0, 3.0, 4.0, 4.0, 3.2, 3.5]
STARTS = [0.0, 3.0, 6.0, 10.0, 14.0, 17.2]
OFF = [0.0, 0.15, 0.15, 0.15, 0.15, 0.15]  # los textos entran cuando el barrido ya va saliendo
GREEN_S = 0xFF5DBB63
GREEN_D = 0xFF3E9A4A


def ease_io(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------ envolvente de voz (para mover la boca)
def load_env(idx):
    w = wave.open(f"{OUT}/voz/v{idx+1}.wav")
    n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch)[:, 0].astype(np.float32) / 32768
    hop = sr / FPS
    nf = int(round(DUR[idx] * FPS))
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


ENV = None


# ------------------------------------------------------------ texto
def centered_line(c, parts, cy, size, pop=1.0, gap=18, rot=0.0, pulse=1.0):
    if pop <= 0.01:
        return
    widths = [text_w(t, size) for t, _ in parts]
    total = sum(widths) + gap * (len(parts) - 1) + sum(40 for _, m in parts if m != 'n')
    x = (W - total) / 2
    c.save()
    c.translate(W / 2, cy)
    c.rotate(rot * (1 - min(1, pop)) + rot * 0)
    c.scale(pop * pulse, pop * pulse)
    c.translate(-W / 2, -cy)
    for (t, m), w in zip(parts, widths):
        if m == 'n':
            draw_text(c, t, x, cy + size * 0.35, size, INK)
            x += w + gap
        else:
            col = PINK if m == 'h' else YEL
            tcol = WHITE if m == 'h' else INK
            bw = w + 40
            bh = size * 1.45
            top = cy - size * 0.85
            rrect(c, x, top, bw, bh, 28, fill=INK)
            rrect(c, x - 6, top - 8, bw, bh, 28, fill=col, line=INK, lw=6)
            draw_text(c, t, x - 6 + 20, cy + size * 0.33 - 8, size, tcol)
            x += bw + gap
    c.restore()


def tline(c, parts, cy, size, u, delay, rot=-4.0, gap=18, pulse_amp=0.0):
    k = clamp01((u - delay) / 0.38)
    pop = ease_out_back(k)
    pulse = 1.0 + (pulse_amp * math.sin((u - delay) * 7) if k >= 1 else 0.0)
    centered_line(c, parts, cy, size, pop, gap, rot=rot, pulse=pulse)


# ------------------------------------------------------------ fondo
def background2(c, t):
    background(c, t)
    for i in range(9):
        ph = i * 1.9
        x = (i * 173 + 80) % W
        y = (H - ((t * (40 + i * 7) + i * 230) % (H + 200))) + 100
        r = 22 + (i % 3) * 14
        if i % 2 == 0:
            c.drawCircle(x, y, r, paint(PINK_L, True, 6))
        else:
            c.drawCircle(x, y, r * 0.55, paint(0xFFFFB3D6))


# ------------------------------------------------------------ mascota v2
def mascot2(c, cx, by, t, mood="neutral", arm="down", scale=1.0, speak=0.0, look=(0, 0), u=10.0):
    k = clamp01(u / 0.5)
    e = ease_out_back(k) if k < 1 else 1.0
    s = math.sin(math.pi * k)
    jump = -80 * s
    b = math.sin(t * 5) * 8 * k
    ph = (t + 0.9) % 3.4
    blink = ph > 3.26
    c.save()
    c.translate(cx, by + b + jump)
    c.rotate(math.sin(t * 2.6) * 1.6)
    c.scale(scale * e * (1 - 0.08 * s), scale * e * (1 + 0.12 * s))
    for sx in (-60, 60):
        line(c, sx, -70, sx, -20, INK, 14)
        oval(c, sx + (8 if sx > 0 else -8), -10, 34, 18, fill=WHITE, line=INK, lw=8)
    body_y = -420
    rrect(c, -150, body_y, 300, 360, 100, fill=PINK, line=INK, lw=10)
    rrect(c, -122, body_y + 30, 26, 150, 13, fill=PINK_L)
    for sx in (-70, 70):
        rrect(c, sx - 24, body_y - 92, 48, 100, 10, fill=GRAY, line=INK, lw=9)
    bolt = skia.Path()
    pts = [(14, -190), (-34, -118), (-4, -118), (-18, -64), (34, -146), (4, -146)]
    bolt.moveTo(*pts[0])
    for p in pts[1:]:
        bolt.lineTo(*p)
    bolt.close()
    c.drawPath(bolt, paint(YEL))
    c.drawPath(bolt, paint(INK, True, 7))
    ey = body_y + 120
    for sx in (-62, 62):
        oval(c, sx, ey, 40, 48, fill=WHITE, line=INK, lw=8)
    lx, ly = look
    py = 14 if mood == "sad" else 0
    for sx in (-62, 62):
        if blink and mood not in ("yawn",):
            line(c, sx - 28, ey + 6, sx + 28, ey + 6, INK, 9)
        elif mood in ("happy", "wink") and not (mood == "wink" and sx == -62):
            c.drawArc(skia.Rect.MakeXYWH(sx - 30, ey - 12, 60, 50), 200, 140, False, paint(INK, True, 9))
        elif mood == "yawn":
            line(c, sx - 28, ey + 4, sx + 28, ey + 4, INK, 9)
        else:
            oval(c, sx + lx, ey + py + ly, 17, 22, fill=INK)
            oval(c, sx + lx + 6, ey + py + ly - 8, 6, 7, fill=WHITE)
    if mood == "sad":
        line(c, -100, ey - 42, -30, ey - 64, INK, 9)
        line(c, 100, ey - 42, 30, ey - 64, INK, 9)
    for sx in (-100, 100):
        oval(c, sx, ey + 62, 20, 12, fill=PINK_D)
    my = ey + 82
    if speak > 0.05:
        h = 8 + speak * 46
        w = 40 + speak * 14
        oval(c, 0, my + 14 + h * 0.3, w / 2, h / 2 + 4, fill=INK)
        if h > 26:
            oval(c, 0, my + 14 + h * 0.3 + h * 0.18, w / 2 - 10, h * 0.2, fill=PINK_D)
    elif mood == "sad":
        c.drawArc(skia.Rect.MakeXYWH(-34, my + 4, 68, 44), 200, 140, False, paint(INK, True, 9))
    elif mood == "yawn":
        oval(c, 0, my + 18, 30, 38, fill=INK)
        oval(c, 0, my + 36, 18, 14, fill=PINK_D)
    elif mood in ("happy", "wink", "point"):
        path = skia.Path()
        path.moveTo(-40, my)
        path.quadTo(0, my + 72, 40, my)
        path.close()
        c.drawPath(path, paint(INK))
        oval(c, 0, my + 28, 20, 12, fill=PINK_L)
    else:
        line(c, -22, my + 14, 22, my + 14, INK, 9)
    sh_y = body_y + 250
    wave = math.sin(t * 9) * 25
    if arm == "wave":
        line(c, 150, sh_y, 230, sh_y - 90 + wave, INK, 14)
        oval(c, 238, sh_y - 100 + wave, 26, 26, fill=WHITE, line=INK, lw=8)
    elif arm == "point":
        line(c, 150, sh_y, 250, sh_y - 150, INK, 14)
        oval(c, 258, sh_y - 162, 26, 26, fill=WHITE, line=INK, lw=8)
    else:
        line(c, 150, sh_y, 205, sh_y + 60, INK, 14)
        oval(c, 212, sh_y + 70, 24, 24, fill=WHITE, line=INK, lw=8)
    line(c, -150, sh_y, -205, sh_y + 60, INK, 14)
    oval(c, -212, sh_y + 70, 24, 24, fill=WHITE, line=INK, lw=8)
    c.restore()


# ------------------------------------------------------------ extras
def bolt_path(cx, cy, s=1.0):
    p = skia.Path()
    pts = [(14, -54), (-22, 0), (0, 0), (-12, 46), (24, -10), (2, -10)]
    p.moveTo(cx + pts[0][0] * s, cy + pts[0][1] * s)
    for x, y in pts[1:]:
        p.lineTo(cx + x * s, cy + y * s)
    p.close()
    return p


def ring(c, cx, cy, r, color, alpha, width):
    p = paint(color, True, width)
    p.setAlphaf(max(0.0, min(1.0, alpha)))
    c.drawCircle(cx, cy, r, p)


def cable_path(x1, y1, x2, y2):
    p = skia.Path()
    p.moveTo(x1, y1)
    p.cubicTo(x1 + 150, y1 + 100, x2 - 40, y2 + 220, x2, y2)
    return p


def draw_cable(c, path, draw=1.0, thick=18):
    pm = skia.PathMeasure(path, False)
    L = pm.getLength()
    seg = skia.Path()
    pm.getSegment(0, L * draw, seg, True)
    c.drawPath(seg, paint(INK, True, thick))
    c.drawPath(seg, paint(WHITE, True, thick * 0.45))


def flow(c, path, t, speed, n, size=14, bolts=False):
    pm = skia.PathMeasure(path, False)
    L = pm.getLength()
    for i in range(n):
        d = ((t * speed + i / n) % 1.0) * L
        pos, _ = pm.getPosTan(d)
        if bolts:
            c.drawPath(bolt_path(pos.x(), pos.y(), size / 28), paint(YEL))
            c.drawPath(bolt_path(pos.x(), pos.y(), size / 28), paint(INK, True, 3))
        else:
            c.drawCircle(pos.x(), pos.y(), size, paint(YEL))
            c.drawCircle(pos.x(), pos.y(), size, paint(INK, True, 4))


def bad_cable(c, path, t):
    pm = skia.PathMeasure(path, False)
    L = pm.getLength()
    seg = skia.Path()
    n = 34
    for i in range(n + 1):
        pos, tan = pm.getPosTan(L * i / n)
        nx, ny = -tan.y(), tan.x()
        j = (14 if i % 2 else -14) * (0.4 if i in (0, n) else 1)
        x, y = pos.x() + nx * j, pos.y() + ny * j
        if i == 0:
            seg.moveTo(x, y)
        else:
            seg.lineTo(x, y)
    c.drawPath(seg, paint(0xFF8A8A8A, True, 9))
    # chispas en el cable
    for k in range(3):
        if (t * 6 + k * 0.37) % 1 < 0.3:
            pos, _ = pm.getPosTan(L * (0.35 + 0.18 * k))
            c.drawPath(bolt_path(pos.x(), pos.y(), 0.55), paint(YEL))
            c.drawPath(bolt_path(pos.x(), pos.y(), 0.55), paint(INK, True, 3))


def x_mark(c, cx, cy, s, pop):
    if pop <= 0:
        return
    c.save()
    c.translate(cx, cy)
    c.scale(pop, pop)
    line(c, -s, -s, s, s, INK, 30)
    line(c, s, -s, -s, s, INK, 30)
    line(c, -s, -s, s, s, RED, 18)
    line(c, s, -s, -s, s, RED, 18)
    c.restore()


def turtle(c, x, y, t, scale=1.0):
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    ph = math.sin(t * 3.2)
    for lx, d in ((-46, 1), (-6, -1), (34, 1), (70, -1)):
        rrect(c, lx - 11 + ph * 6 * d, -34, 24, 36 + ph * 4 * d, 10, fill=GREEN_D, line=INK, lw=6)
    # cola y cabeza
    c.drawPath(_tri(-92, -30, -118, -22, -92, -14), paint(GREEN_D))
    oval(c, 104, -58, 36, 30, fill=GREEN_S, line=INK, lw=7)
    oval(c, 116, -64, 6, 7, fill=INK)
    c.drawArc(skia.Rect.MakeXYWH(104, -58, 26, 18), 10, 150, False, paint(INK, True, 5))
    # caparazon
    shell = skia.Rect.MakeLTRB(-100, -130, 80, -10)
    c.drawArc(shell, 180, 180, True, paint(GREEN_S))
    c.drawArc(shell, 180, 180, True, paint(INK, True, 8))
    for hx in (-50, -4, 42):
        oval(c, hx, -72, 18, 14, line=GREEN_D, lw=6)
    c.restore()


def _tri(x1, y1, x2, y2, x3, y3):
    p = skia.Path()
    p.moveTo(x1, y1)
    p.lineTo(x2, y2)
    p.lineTo(x3, y3)
    p.close()
    return p


def speed_lines(c, cx, cy, t, n=22, r0=210):
    for i in range(n):
        a = i / n * math.tau + 0.1
        r1 = r0 + 70 + 80 * (0.5 + 0.5 * math.sin(t * 16 + i * 1.7))
        p = paint(PINK_L, True, 10)
        c.drawLine(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * r1, cy + math.sin(a) * r1, p)


def confetti(c, ox, oy, age):
    if age <= 0 or age > 1.8:
        return
    cols = [PINK, YEL, WHITE, PINK_D, 0xFF7DD3FC]
    for i in range(34):
        a = i * 2.399
        sp = 380 + (i % 7) * 70
        x = ox + math.cos(a) * sp * age
        y = oy + math.sin(a) * sp * age * 0.8 + 600 * age * age - 250 * age
        c.save()
        c.translate(x, y)
        c.rotate(age * 400 + i * 30)
        rrect(c, -9, -5, 18, 10, 3, fill=cols[i % 5], line=INK, lw=3)
        c.restore()


def sweat(c, x, y, t):
    d = math.sin(t * 4) * 6
    p = skia.Path()
    p.moveTo(x, y - 34 + d)
    p.quadTo(x + 26, y + 6 + d, x, y + 24 + d)
    p.quadTo(x - 26, y + 6 + d, x, y - 34 + d)
    c.drawPath(p, paint(0xFF7DD3FC))
    c.drawPath(p, paint(INK, True, 6))


def wave_edge(edge, phase, below):
    p = skia.Path()
    base = H + 400 if below else -400
    p.moveTo(-40, base)
    x = -40
    while x <= W + 40:
        p.lineTo(x, edge + math.sin(x / 110 + phase) * 28)
        x += 40
    p.lineTo(W + 40, base)
    p.close()
    return p


def panel(c, mode, p, t):
    if mode == "in":
        edge = H + 120 - ease_io(p) * (H + 260)
        below = True
        light = edge - 48
    else:
        edge = (1 - ease_io(p)) * (H + 260) - 140
        below = False
        light = edge + 48
    c.drawPath(wave_edge(light, t * 6, below), paint(PINK_L))
    path = wave_edge(edge, t * 6 + 1.3, below)
    c.drawPath(path, paint(PINK))
    c.drawPath(path, paint(INK, True, 10))
    # rayito en el centro del barrido
    cy = (edge + (H * 0.5 if below else H * 0.5)) / 2
    if 0.25 < p < 1.0 or mode == "out":
        pass


# ------------------------------------------------------------ escenas (u = tiempo local sin el desfase del barrido)
def s1(c, t, sp):
    u = t
    background2(c, t)
    tline(c, [("¿Tu celular carga", 'n')], 330, 64, u, 0.0)
    tline(c, [("LENTO", 'h'), ("?", 'n')], 470, 110, u, 0.15, pulse_amp=0.03)
    # ondas de alarma
    for k in range(3):
        a = (u * 1.1 + k / 3) % 1
        ring(c, 790, 740, 40 + a * 150, RED, 0.8 * (1 - a), 8)
    blink_on = (u * 2.2) % 1 < 0.6
    phone(c, 720, 1010, 15 if blink_on else 15, t, shake=4 * (1 if u % 1.1 < 0.45 else 0.2), low=blink_on)
    mascot2(c, 300, 1650, t, mood="sad", speak=sp, look=(10, 8), u=u)
    sweat(c, 440, 1190, t)


def s2(c, t, sp):
    u = t - OFF[1]
    background2(c, t)
    tline(c, [("Casi siempre el", 'n')], 320, 64, u, 0.0)
    tline(c, [("culpable", 'n')], 450, 110, u, 0.1)
    tline(c, [("es tu cargador", 'h')], 620, 82, u, 1.0, pulse_amp=0.035)
    # flecha que rebota apuntando al texto resaltado
    if u > 1.2:
        d = math.sin(u * 8) * 10
        p = skia.Path()
        p.moveTo(800, 790 + d)
        p.lineTo(840, 750 + d)
        p.lineTo(820, 750 + d)
        p.lineTo(820, 700 + d)
        p.lineTo(780, 700 + d)
        p.lineTo(780, 750 + d)
        p.lineTo(760, 750 + d)
        p.close()
        c.drawPath(p, paint(YEL))
        c.drawPath(p, paint(INK, True, 7))
    phone(c, 720, 1070, 15, t, low=False, scale=0.8)
    mascot2(c, 300, 1650, t, mood="wink", arm="point", speak=sp, look=(10, -4), u=u)


def s3(c, t, sp):
    u = t - OFF[2]
    background2(c, t)
    tline(c, [("Uno de baja", 'n')], 320, 70, u, 0.0)
    tline(c, [("potencia", 'h'), ("va", 'n')], 480, 100, u, 0.12, pulse_amp=0.03)
    tline(c, [("a paso de tortuga", 'n')], 640, 66, u, 0.7)
    pct = 15 + 6 * clamp01(u / 3.6)
    cp = cable_path(452, 1500, 720, 1318)
    draw_cable(c, cp, 1.0, 16)
    flow(c, cp, u, 0.12, 3, 11)  # energia lenta y escasa
    phone(c, 720, 1070, pct, t, scale=0.8)
    chip(c, 760, 760, "5W", GRAY, INK, 60, ease_out_back((u - 0.5) / 0.35))
    # tortuga caminando muy despacio por el piso
    tx = 580 + 190 * ease_io(clamp01(u / 3.6))
    turtle(c, tx, 1650, t, 1.15)
    mascot2(c, 300, 1650, t, mood="yawn", speak=sp, u=u)
    zzz(c, 420, 1250, t)


def s4(c, t, sp):
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
    draw_text(c, "*ilustrativo", 850 - text_w("*ilustrativo", 28) / 2, 1400, 28, INK)


def s5(c, t, sp):
    u = t - OFF[4]
    background2(c, t)
    tline(c, [("Y ojo:", 'n')], 320, 80, u, 0.0)
    tline(c, [("el cable", 'h'), ("también", 'n')], 470, 90, u, 0.12, pulse_amp=0.03)
    tline(c, [("cuenta", 'n')], 620, 90, u, 0.25)
    cp = cable_path(452, 1500, 760, 1313)
    bad = u < 1.5
    if bad:
        draw_in = ease_out(clamp01((u - 0.3) / 0.5))
        if draw_in > 0.05:
            bad_cable(c, cp, t)
            flow(c, cp, u, 0.18, 2, 8)
        phone(c, 760, 1090, 20, t, scale=0.72, charging=True, low=False)
        x_mark(c, 640, 1420, 44, ease_out_back((u - 0.6) / 0.3))
        chip(c, 790, 1590, "cable malo", RED, WHITE, 40, ease_out_back((u - 0.55) / 0.35), rot=4)
    else:
        g = clamp01((u - 1.5) / 0.5)
        draw_cable(c, cp, 1.0, 18)
        flow(c, cp, u, 1.2, 8, 22, bolts=True)
        pct = 20 + 70 * ease_out(clamp01((u - 1.5) / 1.4))
        phone(c, 760, 1090, pct, t, scale=0.72, charging=True)
        chip(c, 790, 1590, "buen cable = OK", GREEN, WHITE, 40, ease_out_back((u - 1.55) / 0.35), rot=4)
        if g > 0.3:
            sparkles(c, 760, 1090, u, 6, 240)
    mascot2(c, 300, 1650, t, mood="happy" if not bad else "neutral", arm="wave", speak=sp, look=(8, -4), u=u)


def s6(c, t, sp):
    u = t - OFF[5]
    background2(c, t)
    tline(c, [("¿Cuál te", 'n')], 320, 80, u, 0.0)
    tline(c, [("conviene?", 'h')], 490, 110, u, 0.12, pulse_amp=0.03)
    tline(c, [("Escríbenos por DM", 'n')], 690, 62, u, 0.7)
    k = clamp01((u - 1.0) / 0.35)
    chip(c, 540, 850, "@inizitech", PINK, WHITE, 64, ease_out_back(k) * (1 + (0.04 * math.sin(u * 8) if k >= 1 else 0)), rot=-3)
    confetti(c, 540, 850, u - 1.0)
    mascot2(c, 540, 1650, t, mood="happy", arm="wave", scale=1.05, speak=sp, look=(0, 0), u=u)
    sparkles(c, 540, 1250, u, 7, 330)


SCENES = [s1, s2, s3, s4, s5, s6]


def render_frame(idx, t, i=None):
    global ENV
    if ENV is None:
        ENV = [load_env(k) for k in range(6)]
    fi = int(round(t * FPS)) if i is None else i
    sp = float(ENV[idx][min(fi, len(ENV[idx]) - 1)])
    surface = skia.Surface.MakeRaster(INFO)
    c = surface.getCanvas()
    z = 1.0 + 0.045 * (t / DUR[idx])  # zoom lento de camara
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-W / 2, -H / 2)
    SCENES[idx](c, t, sp)
    c.restore()
    # barridos de transicion (suben de abajo hacia arriba a traves del corte)
    if idx > 0 and t < 0.32:
        panel(c, "out", t / 0.32, t)
    if idx < 5 and t > DUR[idx] - 0.26:
        panel(c, "in", (t - (DUR[idx] - 0.26)) / 0.26, t)
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)


def render_scene(idx, outpath):
    n = int(round(DUR[idx] * FPS))
    tmp = outpath.replace(".mp4", "_tmp.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        arr = render_frame(idx, i / FPS, i)
        proc.stdin.write(np.ascontiguousarray(arr[:, :, :4]).tobytes())
    proc.stdin.close()
    if proc.wait() == 0:
        os.replace(tmp, outpath)
    else:
        raise SystemExit(f"ffmpeg fallo en escena {idx+1}")


# ------------------------------------------------------------ efectos de sonido
def make_sfx(path):
    sr = 44100
    total = int(sum(DUR) * sr)
    out = np.zeros(total, dtype=np.float32)

    def add(t0, sig, gain=1.0):
        i0 = int(t0 * sr)
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        j = min(total, i0 + len(sig))
        out[i0:j] += sig[: j - i0] * gain

    def pop(f0=900, f1=450, dur=0.09):
        t = np.arange(int(dur * sr)) / sr
        f = f0 + (f1 - f0) * (t / dur)
        ph = 2 * np.pi * np.cumsum(f) / sr
        return (np.sin(ph) * np.exp(-t * 38)).astype(np.float32)

    def beep(f=1000, dur=0.07):
        t = np.arange(int(dur * sr)) / sr
        return (np.sin(2 * np.pi * f * t) * np.minimum(1, t * 400) * np.exp(-t * 14)).astype(np.float32)

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

    pops = {
        0: [0.0, 0.15], 1: [0.15, 0.25, 1.15], 2: [0.15, 0.27, 0.85, 0.65],
        3: [0.15, 0.27, 0.40, 0.55], 4: [0.15, 0.27, 0.40, 0.75, 1.65], 5: [0.15, 0.27, 0.85, 1.15],
    }
    for idx, lst in pops.items():
        for tt in lst:
            add(STARTS[idx] + tt, pop(), 0.55)
    add(0.8, beep(), 0.25)
    add(1.6, beep(), 0.25)
    for k, T in enumerate(STARTS[1:]):
        add(T - 0.26, whoosh(0.5, k), 0.7)
    add(STARTS[3] + 3.05, ding(), 0.6)
    add(STARTS[4] + 1.65 + 0.1, ding(), 0.4)
    add(STARTS[5] + 1.15, ding(), 0.35)
    out = out / max(1e-6, float(np.max(np.abs(out)))) * 0.9
    pcm = (np.stack([out, out], axis=1) * 32767).astype(np.int16)
    w = wave.open(path, "wb")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
    w.close()


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        os.makedirs(f"{OUT}/stills2", exist_ok=True)
        picks = [(0, 0.25), (0, 1.6), (1, 0.1), (1, 2.0), (2, 2.4), (2, 3.9), (3, 1.2), (3, 3.2), (4, 0.9), (4, 2.5), (5, 0.3), (5, 2.4)]
        for n, (idx, tt) in enumerate(picks):
            arr = render_frame(idx, tt)
            skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(f"{OUT}/stills2/p{n:02d}.png", skia.kPNG)
        print("ok")
    elif mode == "sfx":
        make_sfx(f"{OUT}/sfx.wav")
        print("sfx ok")
    elif mode == "scene":
        i = int(sys.argv[2]) - 1
        render_scene(i, f"{OUT}/v2_scene{i+1}.mp4")
        print("scene ok")
    else:
        for i in range(6):
            render_scene(i, f"{OUT}/v2_scene{i+1}.mp4")
        print("scenes ok")
