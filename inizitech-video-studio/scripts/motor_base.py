import math, os, subprocess, sys
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
import glob
HERE = os.path.dirname(os.path.abspath(__file__))
_FONTS = [os.environ.get("INIZI_FONT", ""), os.path.join(HERE, "Poppins-Bold.ttf"),
          "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"] + glob.glob("/usr/share/fonts/**/Poppins-Bold.ttf", recursive=True)
FONT = next(f for f in _FONTS if f and os.path.exists(f))
TF = skia.Typeface.MakeFromFile(FONT)

# paleta Inizitech (rosa / crema / negro)
BG = 0xFFFFE3F0
DOT = 0xFFFFC2DE
PINK = 0xFFFF5FAE
PINK_L = 0xFFFF9CCB
PINK_D = 0xFFE03C90
INK = 0xFF1A1A1A
WHITE = 0xFFFFFFFF
YEL = 0xFFFFD93D
RED = 0xFFFF4D4D
GREEN = 0xFF2ECC71
GRAY = 0xFFD9D9D9

INFO = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def clamp01(x):
    return max(0.0, min(1.0, x))


def paint(color, stroke=None, width=0, aa=True):
    p = skia.Paint(AntiAlias=aa, Color=color)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def rrect(c, x, y, w, h, r, fill=None, line=None, lw=0):
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    if fill is not None:
        c.drawRoundRect(rect, r, r, paint(fill))
    if line is not None:
        c.drawRoundRect(rect, r, r, paint(line, True, lw))


def oval(c, cx, cy, rx, ry, fill=None, line=None, lw=0):
    rect = skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)
    if fill is not None:
        c.drawOval(rect, paint(fill))
    if line is not None:
        c.drawOval(rect, paint(line, True, lw))


def line(c, x1, y1, x2, y2, color, w):
    c.drawLine(x1, y1, x2, y2, paint(color, True, w))


def font(size):
    f = skia.Font(TF, size)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    return f


def text_w(s, size):
    return font(size).measureText(s)


def draw_text(c, s, x, y, size, color=INK, outline=None, ow=0, shadow=None):
    f = font(size)
    if shadow:
        c.drawString(s, x + shadow[0], y + shadow[1], f, paint(shadow[2]))
    if outline is not None:
        c.drawString(s, x, y, f, paint(outline, True, ow))
    c.drawString(s, x, y, f, paint(color))


def centered_line(c, parts, cy, size, pop=1.0, gap=18):
    """parts: [(texto, modo)] modo: 'n' normal, 'h' resaltado rosa, 'y' resaltado amarillo"""
    widths = [text_w(t, size) for t, _ in parts]
    total = sum(widths) + gap * (len(parts) - 1) + sum(40 for _, m in parts if m != 'n')
    x = (W - total) / 2
    c.save()
    c.translate(W / 2, cy)
    c.scale(pop, pop)
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


def background(c, t):
    c.clear(BG)
    off = (t * 20) % 60
    for gx in range(-1, W // 60 + 2):
        for gy in range(-1, H // 60 + 2):
            c.drawCircle(gx * 60 + off, gy * 60 + off, 4, paint(DOT))


# ---------------------------------------------------------------- mascota
def mascot(c, cx, by, t, mood="neutral", arm="down", scale=1.0, bob=True, hold=None):
    """cx: centro, by: base de los pies."""
    b = math.sin(t * 5) * 8 if bob else 0
    c.save()
    c.translate(cx, by + b)
    c.scale(scale, scale)
    # piernas y zapatos
    for sx in (-60, 60):
        line(c, sx, -70, sx, -20, INK, 14)
        oval(c, sx + (8 if sx > 0 else -8), -10, 34, 18, fill=WHITE, line=INK, lw=8)
    # cuerpo
    body_y = -420
    rrect(c, -150, body_y, 300, 360, 100, fill=PINK, line=INK, lw=10)
    # brillo
    rrect(c, -122, body_y + 30, 26, 150, 13, fill=PINK_L)
    # clavijas
    for sx in (-70, 70):
        rrect(c, sx - 24, body_y - 92, 48, 100, 10, fill=GRAY, line=INK, lw=9)
    # rayito en la barriga
    bolt = skia.Path()
    pts = [(14, -190), (-34, -118), (-4, -118), (-18, -64), (34, -146), (4, -146)]
    bolt.moveTo(*pts[0])
    for p in pts[1:]:
        bolt.lineTo(*p)
    bolt.close()
    c.drawPath(bolt, paint(YEL))
    c.drawPath(bolt, paint(INK, True, 7))
    # cara
    ey = body_y + 120
    for sx in (-62, 62):
        oval(c, sx, ey, 40, 48, fill=WHITE, line=INK, lw=8)
    px, py = 0, 0
    if mood == "sad":
        py = 14
    if mood == "yawn":
        py = 10
    if mood == "point":
        px = 10
    for sx in (-62, 62):
        if mood in ("happy", "wink") and not (mood == "wink" and sx == -62):
            # ojos felices (arco)
            c.drawArc(skia.Rect.MakeXYWH(sx - 30, ey - 12, 60, 50), 200, 140, False, paint(INK, True, 9))
        elif mood == "yawn":
            line(c, sx - 28, ey + 4, sx + 28, ey + 4, INK, 9)
        else:
            oval(c, sx + px, ey + py, 17, 22, fill=INK)
            oval(c, sx + px + 6, ey + py - 8, 6, 7, fill=WHITE)
    # cejas tristes
    if mood == "sad":
        line(c, -100, ey - 42, -30, ey - 64, INK, 9)
        line(c, 100, ey - 42, 30, ey - 64, INK, 9)
    # cachetes
    for sx in (-100, 100):
        oval(c, sx, ey + 62, 20, 12, fill=PINK_D)
    # boca
    my = ey + 82
    if mood == "sad":
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
    # brazos
    sh_y = body_y + 250
    wave = math.sin(t * 9) * 25
    if arm == "wave":
        line(c, 150, sh_y, 230, sh_y - 90 + wave, INK, 14)
        oval(c, 238, sh_y - 100 + wave, 26, 26, fill=WHITE, line=INK, lw=8)
        line(c, -150, sh_y, -205, sh_y + 60, INK, 14)
        oval(c, -212, sh_y + 70, 24, 24, fill=WHITE, line=INK, lw=8)
    elif arm == "point":
        line(c, 150, sh_y, 250, sh_y - 150, INK, 14)
        oval(c, 258, sh_y - 162, 26, 26, fill=WHITE, line=INK, lw=8)
        line(c, -150, sh_y, -205, sh_y + 60, INK, 14)
        oval(c, -212, sh_y + 70, 24, 24, fill=WHITE, line=INK, lw=8)
    else:
        line(c, 150, sh_y, 205, sh_y + 60, INK, 14)
        oval(c, 212, sh_y + 70, 24, 24, fill=WHITE, line=INK, lw=8)
        line(c, -150, sh_y, -205, sh_y + 60, INK, 14)
        oval(c, -212, sh_y + 70, 24, 24, fill=WHITE, line=INK, lw=8)
    c.restore()


# ---------------------------------------------------------------- celular
def phone(c, cx, cy, pct, t, shake=0.0, low=False, scale=1.0, charging=False):
    c.save()
    c.translate(cx + math.sin(t * 60) * shake, cy)
    c.scale(scale, scale)
    w, h = 340, 620
    rrect(c, -w / 2 + 10, -h / 2 + 12, w, h, 56, fill=INK)  # sombra dura
    rrect(c, -w / 2, -h / 2, w, h, 56, fill=0xFF2B2B38, line=INK, lw=10)
    rrect(c, -w / 2 + 16, -h / 2 + 16, w - 32, h - 32, 42, fill=0xFF14141C)
    rrect(c, -50, -h / 2 + 30, 100, 26, 13, fill=INK)  # notch
    # bateria grande
    bx, by, bw, bh = -100, -60, 200, 110
    rrect(c, bx, by, bw, bh, 24, line=WHITE, lw=8)
    rrect(c, bx + bw + 6, by + 30, 16, 50, 6, fill=WHITE)
    col = RED if pct < 25 else (YEL if pct < 60 else GREEN)
    fw = max(0, (bw - 20) * pct / 100)
    if fw > 0:
        rrect(c, bx + 10, by + 10, fw, bh - 20, 14, fill=col)
    # porcentaje
    s = f"{int(pct)}%"
    f = font(84)
    tw = f.measureText(s)
    draw_text(c, s, -tw / 2, 130, 84, WHITE)
    if low:
        rrect(c, -110, 190, 220, 56, 28, fill=RED)
        tw = text_w("BATERIA BAJA", 24)
        draw_text(c, "BATERIA BAJA", -tw / 2, 227, 24, WHITE)
    if charging:
        bolt = skia.Path()
        pts = [(12, by - 90), (-26, by - 36), (-2, by - 36), (-14, by + 6), (26, by - 50), (2, by - 50)]
        bolt.moveTo(*pts[0])
        for p in pts[1:]:
            bolt.lineTo(*p)
        bolt.close()
        c.drawPath(bolt, paint(YEL))
    c.restore()


def chip(c, cx, cy, label, color, tcol, size=64, pop=1.0, rot=-6):
    w = text_w(label, size) + 70
    h = size * 1.5
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(pop, pop)
    rrect(c, -w / 2 + 8, -h / 2 + 8, w, h, h / 2, fill=INK)
    rrect(c, -w / 2, -h / 2, w, h, h / 2, fill=color, line=INK, lw=7)
    draw_text(c, label, -text_w(label, size) / 2, size * 0.36, size, tcol)
    c.restore()


def sparkles(c, cx, cy, t, n=6, r=150):
    for i in range(n):
        a = i / n * math.tau + t * 3
        d = r + math.sin(t * 8 + i) * 18
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        s = 18 + 6 * math.sin(t * 10 + i)
        path = skia.Path()
        path.moveTo(x, y - s)
        path.lineTo(x + s * 0.3, y - s * 0.3)
        path.lineTo(x + s, y)
        path.lineTo(x + s * 0.3, y + s * 0.3)
        path.lineTo(x, y + s)
        path.lineTo(x - s * 0.3, y + s * 0.3)
        path.lineTo(x - s, y)
        path.lineTo(x - s * 0.3, y - s * 0.3)
        path.close()
        c.drawPath(path, paint(YEL))
        c.drawPath(path, paint(INK, True, 4))


def zzz(c, x, y, t):
    for i in range(3):
        k = (t * 0.9 + i * 0.33) % 1
        draw_text(c, "z", x + k * 60, y - k * 150 - i * 6, 46 + i * 18, INK)


def cable(c, x1, y1, x2, y2, t, draw=1.0, color=INK):
    path = skia.Path()
    path.moveTo(x1, y1)
    path.cubicTo(x1 + 150, y1 + 100, x2 - 40, y2 + 220, x2, y2)
    pm = skia.PathMeasure(path, False)
    length = pm.getLength()
    seg = skia.Path()
    pm.getSegment(0, length * draw, seg, True)
    c.drawPath(seg, paint(color, True, 18))
    c.drawPath(seg, paint(WHITE, True, 8))


# ---------------------------------------------------------------- escenas
DUR = [3.0, 3.0, 4.0, 4.0, 3.2, 3.5]


def scene1(c, t):
    background(c, t)
    p = ease_out_back(t / 0.35)
    centered_line(c, [("¿Tu celular carga", 'n')], 330, 64, p)
    centered_line(c, [("LENTO", 'h'), ("?", 'n')], 470, 110, ease_out_back((t - 0.15) / 0.35))
    phone(c, 720, 1010, 15, t, shake=3 * (1 if t % 1.2 < 0.4 else 0), low=True)
    mascot(c, 300, 1650, t, mood="sad")


def scene2(c, t):
    background(c, t)
    centered_line(c, [("Casi siempre el", 'n')], 320, 64, ease_out_back(t / 0.35))
    centered_line(c, [("culpable", 'n')], 450, 110, ease_out_back((t - 0.1) / 0.35))
    centered_line(c, [("es tu cargador", 'h')], 620, 82, ease_out_back((t - 1.0) / 0.35))
    phone(c, 720, 1070, 15, t, low=False, scale=0.8)
    mascot(c, 300, 1650, t, mood="wink", arm="point")


def scene3(c, t):
    background(c, t)
    centered_line(c, [("Uno de baja", 'n')], 320, 70, ease_out_back(t / 0.35))
    centered_line(c, [("potencia", 'h'), ("va", 'n')], 480, 100, ease_out_back((t - 0.12) / 0.35))
    centered_line(c, [("a paso de tortuga", 'n')], 640, 66, ease_out_back((t - 0.7) / 0.35))
    pct = 15 + 7 * clamp01(t / 4.0)
    phone(c, 720, 1070, pct, t, scale=0.8)
    chip(c, 760, 760, "5W", GRAY, INK, 60, ease_out_back((t - 0.5) / 0.35))
    mascot(c, 300, 1650, t, mood="yawn")
    zzz(c, 420, 1250, t)


def scene4(c, t):
    background(c, t)
    centered_line(c, [("Uno de", 'n'), ("20W", 'y')], 320, 80, ease_out_back(t / 0.35))
    centered_line(c, [("carga mucho", 'n')], 460, 80, ease_out_back((t - 0.12) / 0.35))
    centered_line(c, [("MÁS RÁPIDO", 'h')], 620, 90, ease_out_back((t - 0.25) / 0.35))
    pct = 15 + 75 * ease_out(clamp01((t - 0.5) / 3.0))
    phone(c, 720, 1070, pct, t, scale=0.8, charging=True)
    chip(c, 760, 760, "20W", YEL, INK, 60, ease_out_back((t - 0.4) / 0.35))
    sparkles(c, 720, 1070, t, 6, 260)
    mascot(c, 300, 1650, t, mood="happy", arm="wave")
    draw_text(c, "*ilustrativo", 720 - text_w("*ilustrativo", 28) / 2, 1380, 28, INK)


def scene5(c, t):
    background(c, t)
    centered_line(c, [("Y ojo:", 'n')], 320, 80, ease_out_back(t / 0.35))
    centered_line(c, [("el cable", 'h'), ("también", 'n')], 470, 90, ease_out_back((t - 0.12) / 0.35))
    centered_line(c, [("cuenta", 'n')], 620, 90, ease_out_back((t - 0.25) / 0.35))
    phone(c, 760, 1090, 90, t, scale=0.72, charging=True)
    cable(c, 452, 1500, 760, 1318, t, draw=ease_out(clamp01((t - 0.4) / 0.9)))
    chip(c, 790, 1590, "buen cable = OK", GREEN, WHITE, 40, ease_out_back((t - 1.2) / 0.35), rot=4)
    mascot(c, 300, 1650, t, mood="happy", arm="wave")


def scene6(c, t):
    background(c, t)
    centered_line(c, [("¿Cuál te", 'n')], 320, 80, ease_out_back(t / 0.35))
    centered_line(c, [("conviene?", 'h')], 490, 110, ease_out_back((t - 0.12) / 0.35))
    centered_line(c, [("Escríbenos por DM", 'n')], 690, 62, ease_out_back((t - 0.7) / 0.35))
    chip(c, 540, 850, "@inizitech", PINK, WHITE, 64, ease_out_back((t - 1.0) / 0.35), rot=-3)
    mascot(c, 540, 1650, t, mood="happy", arm="wave", scale=1.05)
    sparkles(c, 540, 1250, t, 7, 330)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]


def render_frame(fn, t):
    surface = skia.Surface.MakeRaster(INFO)
    canvas = surface.getCanvas()
    fn(canvas, t)
    img = surface.makeImageSnapshot()
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)
    return arr


def render_scene(idx, outpath):
    fn = SCENES[idx]
    n = int(round(DUR[idx] * FPS))
    tmp = outpath.replace(".mp4", "_tmp.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        arr = render_frame(fn, i / FPS)
        proc.stdin.write(np.ascontiguousarray(arr[:, :, :4]).tobytes())
    proc.stdin.close()
    rc = proc.wait()
    if rc == 0:
        os.replace(tmp, outpath)
    else:
        raise SystemExit(f"ffmpeg fallo en escena {idx+1}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        os.makedirs(os.path.join(os.environ.get("INIZI_OUT","/tmp/inizi_out"),"stills"), exist_ok=True)
        # momentos con mas cosas en pantalla
        picks = [(0, 1.0), (1, 2.2), (2, 2.0), (3, 2.5), (4, 2.4), (5, 2.5)]
        for idx, tt in picks:
            arr = render_frame(SCENES[idx], tt)
            skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType).save(
                os.path.join(os.environ.get("INIZI_OUT","/tmp/inizi_out"),"stills",f"s{idx+1}.png"), skia.kPNG)
        print("ok")
    else:
        for i in range(len(SCENES)):
            render_scene(i, os.path.join(os.environ.get("INIZI_OUT","/tmp/inizi_out"),f"scene{i+1}.mp4"))
        print("scenes ok")
