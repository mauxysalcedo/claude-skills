#!/usr/bin/env python3
"""Edita clips que graba Mauxy (o clips de recursos) a un Reel vertical 1080x1920 con subtitulos palabra por palabra.

Uso:  python3 -I editar_clips.py edicion.json

edicion.json
{
  "salida": "final.mp4",
  "clips":  [ {"archivo": "a.mp4", "ini": 0.0, "fin": 4.5, "zoom": 1.0}, ... ],   # corta y une en orden; zoom opcional (1.0-1.3)
  "palabras": [ ["Hola", 0.10, 0.42], ["mundo", 0.45, 0.90] ],                      # tiempos en el VIDEO FINAL (segundos)
  "gancho": "¿Tu celular carga lento?",                                           # texto grande los primeros 2.2 s (opcional)
  "marca": "inizitech",                                                             # pildora rosa arriba (opcional, "" para quitarla)
  "musica": "musica.mp3", "musica_vol": 0.10                                        # opcional, queda bajita bajo la voz
}
Los tiempos de "palabras" salen de transcribir el audio ya cortado (Speko audio_transcribe con timestamps por palabra).
Zona segura de Instagram: subtitulos entre y=1180 y y=1560; no se pone nada en los ultimos 250 px.
"""
import glob, json, math, os, subprocess, sys
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
PINK, INK, WHITE, LIME = 0xFFFF5FAE, 0xFF1A1A1A, 0xFFFFFFFF, 0xFFFFD93D
HERE = os.path.dirname(os.path.abspath(__file__))
_F = [os.environ.get("INIZI_FONT", ""), os.path.join(HERE, "Poppins-Bold.ttf")] + glob.glob("/usr/share/fonts/**/Poppins-Bold.ttf", recursive=True)
TF = skia.Typeface.MakeFromFile(next(f for f in _F if f and os.path.exists(f)))
INFO = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)


def font(size):
    f = skia.Font(TF, size)
    f.setSubpixel(True)
    return f


def tw(s, size):
    return font(size).measureText(s)


def paint(color, stroke=False, width=0):
    p = skia.Paint(AntiAlias=True, Color=color)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def word(c, s, x, y, size, color, outline=True):
    f = font(size)
    if outline:
        c.drawString(s, x, y, f, paint(INK, True, size * 0.16))
    c.drawString(s, x, y, f, paint(color))


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    return 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2


def chunks(palabras, size, maxw=900, maxn=5):
    """agrupa palabras en bloques de <=2 lineas; corta en puntuacion"""
    out, cur = [], []
    def fits(ws):
        lines, w = 1, 0
        for p in ws:
            ww = tw(p[0], size) + size * 0.34
            if w + ww > maxw:
                lines += 1; w = 0
            w += ww
        return lines <= 2
    for p in palabras:
        if cur and (len(cur) >= maxn or not fits(cur + [p])):
            out.append(cur); cur = []
        cur.append(p)
        if p[0].rstrip()[-1:] in ".?!,:;" and len(cur) >= 2:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def layout(ws, size, maxw=900):
    lines, cur, w = [], [], 0
    for p in ws:
        ww = tw(p[0], size)
        if cur and w + ww > maxw:
            lines.append(cur); cur, w = [], 0
        cur.append((p, ww)); w += ww + size * 0.34
    lines.append(cur)
    return lines


def dibujar_subs(c, CH, t, size=84, y0=1330):
    for ws in CH:
        a, b = ws[0][1], ws[-1][2] + 0.18
        if not (a <= t < b):
            continue
        lines = layout(ws, size)
        for li, ln in enumerate(lines):
            total = sum(ww for _, ww in ln) + size * 0.34 * (len(ln) - 1)
            x = (W - total) / 2
            y = y0 + li * size * 1.42
            for (p, ww) in ln:
                act = p[1] <= t < p[2] or (p is ws[-1] and t >= p[1])
                if act:
                    k = ease_out_back((t - p[1]) / 0.18)
                    c.save(); c.translate(x + ww / 2, y - size * 0.3); c.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
                    c.drawRoundRect(skia.Rect.MakeXYWH(-ww / 2 - 16, -size * 0.78, ww + 32, size * 1.15), 26, 26, paint(PINK))
                    c.drawRoundRect(skia.Rect.MakeXYWH(-ww / 2 - 16, -size * 0.78, ww + 32, size * 1.15), 26, 26, paint(INK, True, 6))
                    word(c, p[0], -ww / 2, size * 0.3, size, WHITE, outline=False)
                    c.restore()
                else:
                    word(c, p[0], x, y, size, WHITE)
                x += ww + size * 0.34
        return


def preparar_base(cfg, base):
    inputs, filt, labels = [], [], []
    for i, cl in enumerate(cfg["clips"]):
        inputs += ["-i", cl["archivo"]]
        z = float(cl.get("zoom", 1.0))
        cw, ch = int(W * z), int(H * z)
        filt.append(f"[{i}:v]trim=start={cl['ini']}:end={cl['fin']},setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=increase,"
                    f"crop={W}:{H},fps={FPS},setsar=1" + (f",scale={cw}:{ch},crop={W}:{H}" if z > 1.0 else "") + f"[v{i}]")
        filt.append(f"[{i}:a]atrim=start={cl['ini']}:end={cl['fin']},asetpts=PTS-STARTPTS,aresample=44100,"
                    f"pan=stereo|c0=c0|c1=c0[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    filt.append("".join(labels) + f"concat=n={len(cfg['clips'])}:v=1:a=1[v][a]")
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[v]", "-map", "[a]",
                           "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", base])


def main(path):
    cfg = json.load(open(path))
    salida = os.path.abspath(cfg.get("salida", "final.mp4"))
    work = os.path.splitext(salida)[0] + "_work"
    os.makedirs(work, exist_ok=True)
    base = f"{work}/base.mkv"
    preparar_base(cfg, base)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", base]))
    CH = chunks(cfg.get("palabras", []), 84)
    gancho, marca = cfg.get("gancho", ""), cfg.get("marca", "inizitech")
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
    tmp = f"{work}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = dec.stdout.read(W * H * 4)
        if len(buf) < W * H * 4:
            break
        t = n / FPS
        frame = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 4).copy()
        surf = skia.Surface.MakeRasterDirect(INFO, frame, W * 4)
        c = surf.getCanvas()
        g = skia.GradientShader.MakeLinear([(0, 1100), (0, H)], [0x00000000, 0xB0000000])
        p = skia.Paint(); p.setShader(g); c.drawRect(skia.Rect.MakeLTRB(0, 1100, W, H), p)
        if marca:
            w = tw(marca, 40) + 70
            c.drawRoundRect(skia.Rect.MakeXYWH(70, 290, w, 70), 35, 35, paint(PINK))
            c.drawRoundRect(skia.Rect.MakeXYWH(70, 290, w, 70), 35, 35, paint(INK, True, 6))
            word(c, marca, 105, 290 + 49, 40, WHITE, outline=False)
        if gancho and t < 2.2:
            k = ease_out_back(t / 0.3) * (1 if t < 1.9 else max(0.0, (2.2 - t) / 0.3))
            lines = layout([(w_, 0, 0) for w_ in gancho.split()], 92, 900)
            c.save(); c.translate(W / 2, 560); c.scale(max(k, 0.001), max(k, 0.001))
            for li, ln in enumerate(lines):
                total = sum(ww for _, ww in ln) + 92 * 0.34 * (len(ln) - 1)
                x = -total / 2
                for (pw, ww) in ln:
                    word(c, pw[0], x, li * 118, 92, WHITE if li else LIME)
                    x += ww + 92 * 0.34
            c.restore()
        dibujar_subs(c, CH, t)
        enc.stdin.write(frame.tobytes())
        n += 1
    enc.stdin.close(); dec.wait()
    if enc.wait() != 0:
        raise SystemExit("fallo el encoder")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", base]
    if cfg.get("musica"):
        cmd += ["-stream_loop", "-1", "-i", cfg["musica"], "-filter_complex",
                f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[v];[2:a]volume={cfg.get('musica_vol', 0.10)}[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", salida]
    subprocess.check_call(cmd)
    print("OK", salida, round(dur, 1), "s")


if __name__ == "__main__":
    main(sys.argv[1])
