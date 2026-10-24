import colorsys
import math

from PIL import Image, ImageChops, ImageDraw

import estilo_morado as _E
import motion4 as _4
from motion6 import PLANTILLAS, S, cue, prog

CX, CY = 360.0, 500.0
SK = (176, 214, 255)
SKO = (70, 120, 205)

def _ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)

def _out(u):
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 3

def _back(u):
    u = max(0.0, min(1.0, u))
    c = 2.0
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

def _g(u, c, w, a):
    return a * math.exp(-((u - c) / w) ** 2)

def _beat(t, bpm=74.0):
    ph = (t * bpm / 60.0) % 1.0
    return _g(ph, 0.10, 0.055, 1.0) + _g(ph, 0.30, 0.08, 0.55), ph

def _hsv(h, s=0.8, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def _smooth(pts, n=6):
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for j in range(n):
            u = j / n
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u3) for k in (0, 1)))
    return out

def _rot(x, y, ang, cx=CX, cy=CY):
    a = math.radians(ang)
    dx, dy = x - cx, y - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))

class C:
    def __init__(s, img, z=1.0, fx=CX, fy=CY):
        s.im = img
        s.d = ImageDraw.Draw(img)
        s.z, s.fx, s.fy = z, fx, fy
        s.t = (0.0, 0.0, CX, CY, 1.0)
        s.stk = []
        s.hud = False
        s.ov = None
        s.box = None

    def clone(s, img):
        c = C(img, s.z, s.fx, s.fy)
        c.t, c.stk, c.hud = s.t, list(s.stk), s.hud
        return c

    def place(s, ox, oy, k=1.0, hud=False):
        s.t = (ox, oy, CX, CY, max(0.03, k))
        s.stk = []
        s.hud = hud

    def push(s, cx, cy, k):
        s.stk.append((cx, cy, max(0.03, k)))

    def pop(s):
        s.stk.pop()

    def P(s, x, y):
        for cx, cy, k in reversed(s.stk):
            x = cx + (x - cx) * k
            y = cy + (y - cy) * k
        ox, oy, ax, ay, k = s.t
        x = ox + (x - ax) * k
        y = oy + (y - ay) * k
        if not s.hud:
            x = (x - s.fx) * s.z + 360.0
            y = (y - s.fy) * s.z + 500.0
        return (x * S, y * S)

    def K(s):
        k = s.t[4]
        for _, _, kk in s.stk:
            k *= kk
        return k * (1.0 if s.hud else s.z)

    def L(s, v):
        return max(1, int(round(v * s.K() * S)))

    def flush(s):
        if s.ov is not None and s.box:
            w, h = s.im.size
            x0, y0, x1, y1 = s.box
            box = (max(0, int(x0)), max(0, int(y0)), min(w, int(x1) + 1), min(h, int(y1) + 1))
            if box[2] > box[0] and box[3] > box[1]:
                s.im.alpha_composite(s.ov.crop(box), dest=(box[0], box[1]))
                s.ov.paste((0, 0, 0, 0), box)
        s.box = None

    def _dr(s, fill, outline, pts, pad):
        tr = (fill is not None and len(fill) == 4 and fill[3] < 250) or (outline is not None and len(outline) == 4 and outline[3] < 250)
        if not tr:
            s.flush()
            return s.d
        if s.ov is None:
            s.ov = Image.new('RGBA', s.im.size, (0, 0, 0, 0))
            s.od = ImageDraw.Draw(s.ov)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        b = (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
        s.box = b if s.box is None else (min(s.box[0], b[0]), min(s.box[1], b[1]), max(s.box[2], b[2]), max(s.box[3], b[3]))
        return s.od

    def poly(s, pts, fill=None, outline=None, w=3):
        p = [s.P(x, y) for x, y in pts]
        d = s._dr(fill, outline, p, s.L(w) + 2)
        if fill:
            d.polygon(p, fill=fill)
        if outline:
            d.line(p + [p[0]], fill=outline, width=s.L(w), joint='curve')

    def ell(s, cx, cy, rx, ry=None, fill=None, outline=None, w=3):
        ry = rx if ry is None else ry
        a, b = s.P(cx - rx, cy - ry), s.P(cx + rx, cy + ry)
        if b[0] <= a[0] or b[1] <= a[1]:
            return
        d = s._dr(fill, outline, [a, b], s.L(w) + 2)
        d.ellipse([a, b], fill=fill, outline=outline, width=s.L(w) if outline else 0)

    def line(s, pts, fill, w=4):
        p = [s.P(x, y) for x, y in pts]
        wd = s.L(w)
        d = s._dr(fill, None, p, wd + 2)
        d.line(p, fill=fill, width=wd, joint='curve')
        r = wd / 2.0
        for q in (p[0], p[-1]):
            d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=fill)

    def arc(s, cx, cy, r, a0, a1, fill, w=4):
        a, b = s.P(cx - r, cy - r), s.P(cx + r, cy + r)
        d = s._dr(fill, None, [a, b], s.L(w) + 2)
        d.arc([a, b], a0, a1, fill=fill, width=s.L(w))

    def rr(s, x0, y0, x1, y1, r, fill=None, outline=None, w=3):
        a, b = s.P(x0, y0), s.P(x1, y1)
        if b[0] <= a[0] or b[1] <= a[1]:
            return
        d = s._dr(fill, outline, [a, b], s.L(w) + 2)
        d.rounded_rectangle([a, b], radius=r * s.K() * S, fill=fill, outline=outline, width=s.L(w) if outline else 0)

    def text(s, x, y, txt, size, fill, stroke=0, sfill=(40, 20, 80)):
        s.flush()
        f = _4.pfont(max(4.0, size * s.K()), True)
        s.d.text(s.P(x, y), txt, font=f, fill=fill, anchor='mm', stroke_width=int(stroke * s.K() * S), stroke_fill=sfill)

def _caps(x, y, ln, wd, ang):
    pts = []
    for i in range(9):
        u = -math.pi / 2 + math.pi * i / 8
        pts.append((ln / 2 + math.cos(u) * wd / 2, math.sin(u) * wd / 2))
    for i in range(9):
        u = math.pi / 2 + math.pi * i / 8
        pts.append((-ln / 2 + math.cos(u) * wd / 2, math.sin(u) * wd / 2))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]

def _heart_pts(cx, cy, sz):
    k = sz / 16.0
    pts = []
    for i in range(72):
        a = i / 72 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * k, cy - y * k))
    return pts

def _heart(c, cx, cy, sz, col=(232, 52, 84), ol=(140, 18, 48)):
    if _E.ESTILO['modo'] == 'negro' and len(col) == 3:
        col, ol = (255, 125, 155), (255, 226, 236)
    c.poly(_heart_pts(cx, cy, sz), col, ol, max(2.0, sz * 0.12))
    c.ell(cx - sz * 0.45, cy - sz * 0.38, sz * 0.26, sz * 0.14, fill=(255, 160, 178))

def _brain(c, cx, cy, w, h, glow=0.0):
    pts = []
    for i in range(28):
        a = i / 28 * 2 * math.pi
        r = 1 + 0.07 * math.sin(7 * a)
        pts.append((cx + w * math.cos(a) * r, cy + h * math.sin(a) * r))
    c.poly(_smooth(pts, 3), (246, 166, 190), (200, 96, 130), max(2.0, w * 0.06))
    c.line([(cx, cy - h * 0.95), (cx + w * 0.04, cy), (cx, cy + h * 0.7)], (206, 104, 138), max(2.0, w * 0.05))
    for sx in (-1, 1):
        for j, (ax, ay, rr_) in enumerate(((0.45, -0.25, 0.32), (0.5, 0.25, 0.3), (0.2, 0.05, 0.22))):
            c.arc(cx + sx * w * ax, cy + h * ay, w * rr_, 200 if sx > 0 else 300, 340 if sx > 0 else 80, (214, 112, 144), max(2.0, w * 0.04))
    if glow > 0:
        c.ell(cx, cy, w * (1.25 + 0.1 * glow), h * (1.3 + 0.1 * glow), outline=(255, 222, 90, int(190 * glow)), w=max(3.0, w * 0.08))

def _lungs(c, cx, cy, kk=1.0, rx=34, ry=58, sep=40):
    c.line([(cx, cy - ry * 1.15), (cx, cy - ry * 0.2)], (225, 226, 236), max(3.0, rx * 0.22))
    for sx in (-1, 1):
        x = cx + sx * sep
        c.ell(x, cy + ry * 0.1, rx * kk, ry * kk, (250, 168, 190), (214, 100, 130), max(2.0, rx * 0.1))
        c.ell(x - sx * rx * 0.25, cy - ry * 0.1, rx * 0.3 * kk, ry * 0.4 * kk, fill=(255, 205, 218))
        for j in range(3):
            c.line([(cx, cy - ry * 0.25 + j * 6), (x - sx * rx * 0.1, cy + ry * (0.05 + 0.3 * j))], (232, 120, 150), max(2.0, rx * 0.08))

def _stomach_pts(cx, cy, sx=1.0, sy=1.0):
    base = [(-34, -22), (-4, -32), (26, -20), (42, 6), (30, 32), (0, 36), (-26, 22), (-42, -4)]
    return _smooth([(cx + x * sx, cy + y * sy) for x, y in base], 5)

ANCLAS = {'corazon': (378, 420), 'cerebro': (360, 215), 'cabeza': (360, 225), 'pulmones': (360, 395),
          'estomago': (392, 505), 'intestino': (360, 580), 'cuerpo': (360, 500)}

def _cuerpo(c, t, p, lt, oa):
    neg = _E.ESTILO['modo'] == 'negro'
    sk, sko, ski = ((32, 40, 96), (176, 204, 255), (56, 70, 132)) if neg else (SK, SKO, (205, 231, 255))
    for col, ex in ((sko, 8), (sk, 0)):
        c.line([(272, 332), (238, 470), (228, 604)], col, 36 + ex)
        c.line([(448, 332), (482, 470), (492, 604)], col, 36 + ex)
        c.line([(326, 612), (320, 760), (314, 905)], col, 46 + ex)
        c.line([(394, 612), (400, 760), (406, 905)], col, 46 + ex)
        tor = [(268, 306), (452, 306), (448, 420), (424, 560), (414, 626), (306, 626), (296, 560), (272, 420)]
        c.poly(tor, col, col if ex else None, ex or 1)
        c.rr(344 - ex / 2, 270, 376 + ex / 2, 314, 10, col)
        c.ell(360, 225, 52 + ex / 2, 60 + ex / 2, col)
    c.poly([(284, 320), (436, 320), (432, 420), (410, 558), (402, 612), (318, 612), (310, 558), (288, 420)], ski)
    org = p.get('organos') or []
    names = [o if isinstance(o, str) else o[0] for o in org]
    bt, ph = _beat(t, p.get('bpm', 74))
    if 'pulmones' in names:
        c.push(360, 395, oa.get('pulmones', 1))
        _lungs(c, 360, 395, 1 + 0.04 * math.sin(t * 2.4))
        c.pop()
    if 'estomago' in names:
        c.push(392, 505, oa.get('estomago', 1))
        c.poly(_stomach_pts(392, 505, 0.95, 0.9), (246, 160, 128), (196, 96, 70), 3)
        c.pop()
    if 'intestino' in names:
        c.push(360, 580, oa.get('intestino', 1))
        pts = [(318 + i * 6, 574 + 14 * math.sin(i * 0.9 + (0 if i % 2 else 3))) for i in range(15)]
        c.line(pts, (255, 190, 160), 9)
        c.pop()
    if 'corazon' in names:
        k = oa.get('corazon', 1)
        c.push(378, 420, k * (1 + 0.14 * bt))
        _heart(c, 378, 420, 22)
        c.pop()
        if p.get('sangre'):
            for i in range(6):
                u = (t * 0.8 + i / 6.0) % 1.0
                c.ell(372 - 14 * u, 402 - 78 * u, 3.4, fill=(255, 70, 90, int(255 * min(1, 3 * (1 - u)))))
            c.line([(372, 402), (368, 330)], (225, 60, 80), 6)
            c.line([(358, 402), (344, 340)], (70, 110, 230), 6)
        if p.get('anillos'):
            for j in range(3):
                u = (ph + j / 3.0) % 1.0
                r = 18 + 70 * u
                c.ell(378, 420, r, outline=(255, 90, 120, int(210 * (1 - u))), w=3)
    if 'cerebro' in names:
        c.push(360, 215, oa.get('cerebro', 1))
        _brain(c, 360, 215, 34, 27, 0.5 + 0.5 * math.sin(t * 5) if p.get('chispas') else 0)
        c.pop()
    res = p.get('resalta')
    if res:
        for nm in (res if isinstance(res, list) else [res]):
            ax, ay = ANCLAS.get(nm, (360, 500))
            a = oa.get('_res', 1)
            pu = 1 + 0.18 * math.sin(t * 6)
            c.ell(ax, ay, 46 * pu * a, 46 * pu * a if nm != 'pulmones' else 70 * pu * a, outline=(255, 214, 60), w=5)
    if p.get('latidos_icono'):
        pass

def _ecg(c, t, p, lt, oa):
    py = p.get('y', 760)
    x0, y0, w, h = 80, py - 55, 560, 110
    c.rr(x0, y0, x0 + w, y0 + h, 18, (16, 18, 40), (90, 230, 150), 3)
    bpm = p.get('bpm', 74)
    pts = []
    for i in range(0, 121):
        x = i / 120.0
        s_ = t * bpm / 60.0 - (1 - x) * 2.0
        u = s_ % 1.0
        v = _g(u, 0.15, 0.04, 0.14) - _g(u, 0.26, 0.012, 0.16) + _g(u, 0.30, 0.014, 1.0) - _g(u, 0.335, 0.014, 0.28) + _g(u, 0.55, 0.05, 0.26)
        pts.append((x0 + 14 + x * (w - 28), y0 + h * 0.62 - v * h * 0.5))
    c.line(pts, (90, 240, 160), 5)
    c.ell(pts[-1][0], pts[-1][1], 7, fill=(255, 255, 255))

def _contador(c, t, p, lt, oa):
    a, b = float(p.get('desde', 0)), float(p.get('hasta', 100))
    v = a + (b - a) * _out(lt / float(p.get('dur', 1.8)))
    txt = ('{:,}'.format(int(v))).replace(',', '.') + p.get('sufijo', '')
    sz = float(p.get('tam', 86))
    wpx = 70 + len(txt) * sz * 0.56
    x, y = p.get('x', 360), p.get('y', 215)
    hh = 70 if not p.get('etiqueta') else 96
    c.rr(x - wpx / 2, y - hh, x + wpx / 2, y + hh * 0.9 if p.get('etiqueta') else y + hh, 30, (22, 18, 46), (255, 214, 60), 4)
    c.text(x, y - (14 if p.get('etiqueta') else 0), txt, sz, (255, 255, 255))
    if p.get('etiqueta'):
        c.text(x, y + 56, p['etiqueta'], 34, (255, 226, 120))

def _pill(c, t, p, lt, oa):
    txt = str(p.get('texto', ''))
    sz = float(p.get('tam', 70))
    x, y = p.get('x', 360), p.get('y', 215)
    wpx = 70 + len(txt) * sz * 0.56
    c.rr(x - wpx / 2, y - sz * 0.85, x + wpx / 2, y + sz * 0.85, 30, (22, 18, 46), (255, 214, 60), 4)
    c.text(x, y, txt, sz, (255, 255, 255))

def _texto(c, t, p, lt, oa):
    c.text(p.get('x', 360), p.get('y', 500), str(p.get('texto', '')), float(p.get('tam', 110)), (255, 255, 255), 6)

def _bebe(c, t, p, lt, oa):
    bt, ph = _beat(t, 140)
    c.ell(360, 500, 190, fill=(255, 226, 238), outline=(240, 140, 180), w=10)
    c.ell(360, 500, 160, fill=(255, 205, 222))
    c.ell(352, 540, 78, 58, (252, 200, 168), (214, 140, 110), 4)
    c.ell(300, 470, 48, fill=(252, 204, 172), outline=(214, 140, 110), w=4)
    c.arc(300, 466, 14, 20, 160, (120, 70, 60), 4)
    c.line([(400, 560), (450, 520), (440, 470)], (252, 200, 168), 22)
    c.line([(392, 590), (440, 610)], (252, 200, 168), 24)
    c.push(352, 530, 1 + 0.35 * bt)
    _heart(c, 352, 530, 14)
    c.pop()
    for i in range(5):
        u = (t * 0.3 + i / 5.0) % 1.0
        c.ell(250 + i * 55, 650 - 220 * u, 6 + 4 * (i % 2), outline=(255, 255, 255, int(220 * (1 - u))), w=3)

def _cerebro_det(c, t, p, lt, oa):
    pu = 0.5 + 0.5 * math.sin(t * 5)
    nodes = [(360 + 175 * math.cos(a), 500 + 135 * math.sin(a) * 1.0) for a in [i * 2 * math.pi / 10 + 0.3 for i in range(10)]]
    edges = [(i, (i + 3) % 10) for i in range(10)] + [(i, (i + 1) % 10) for i in range(0, 10, 2)]
    for (i, j) in edges:
        c.line([nodes[i], nodes[j]], (255, 255, 255, 110), 3)
    c.push(360, 500, 1.0)
    _brain(c, 360, 500, 150, 118, pu)
    c.pop()
    for k, (i, j) in enumerate(edges):
        u = (t * 0.9 + k * 0.37) % 1.0
        x = nodes[i][0] + (nodes[j][0] - nodes[i][0]) * u
        y = nodes[i][1] + (nodes[j][1] - nodes[i][1]) * u
        c.ell(x, y, 8, fill=(255, 232, 90))
    for n_ in nodes:
        c.ell(n_[0], n_[1], 11, fill=(255, 214, 60), outline=(255, 255, 255), w=3)

def _bateria(c, t, p, lt, oa):
    x, y = p.get('x', 360), p.get('y', 700)
    c.rr(x - 210, y - 60, x + 210, y + 60, 24, (240, 240, 250), (44, 40, 70), 8)
    c.rr(x + 210, y - 24, x + 236, y + 24, 8, (44, 40, 70))
    for i in range(5):
        cx = x - 176 + i * 76
        on = i == 0
        pu = 0.7 + 0.3 * math.sin(t * 6) if on else 1
        col = (255, int(205 * pu + 30), 60) if on else (205, 208, 224)
        c.rr(cx, y - 40, cx + 64, y + 40, 12, col)
    c.text(x, y - 108, '20%', 76, (255, 232, 120), 5)

def _ojo(c, t, p, lt, oa):
    b = max(0.0, 1 - abs((t % 3.4) - 3.2) * 6)
    hh = 118 * (1 - 0.92 * b)
    top, bot = [], []
    for i in range(41):
        u = i / 40.0
        x = 360 - 220 + 440 * u
        yy = hh * math.sin(math.pi * u) ** 0.85
        top.append((x, 500 - yy))
        bot.append((x, 500 + yy * 0.85))
    shape = top + bot[::-1]
    c.poly(shape, (250, 250, 253), (60, 50, 80), 8)
    c.flush()
    m = Image.new('L', c.im.size, 0)
    c2 = c.clone(Image.new('RGBA', c.im.size, (0, 0, 0, 0)))
    ImageDraw.Draw(m).polygon([c.P(x, y) for x, y in shape], fill=255)
    hue = (t * 0.25) % 1.0
    dx = 24 * math.sin(t * 1.4)
    c2.ell(360 + dx, 500, 98, fill=_hsv(hue, 0.85, 0.95), outline=_hsv(hue + 0.1, 0.9, 0.55), w=7)
    c2.ell(360 + dx, 500, 66, fill=_hsv(hue + 0.12, 0.7, 1.0))
    c2.ell(360 + dx, 500, 38 * (1 + 0.15 * math.sin(t * 2)), fill=(14, 16, 30))
    c2.ell(334 + dx, 470, 15, fill=(255, 255, 255))
    c2.flush()
    c2.im.putalpha(ImageChops.multiply(c2.im.getchannel('A'), m))
    c.im.alpha_composite(c2.im)
    n = min(16, 4 + int(lt * 5))
    for i in range(n):
        a = t * 0.8 + i * 2 * math.pi / 16
        c.ell(360 + 270 * math.cos(a), 500 + 190 * math.sin(a), 17, fill=_hsv(i / 16.0 + t * 0.1, 0.85, 1.0), outline=(255, 255, 255), w=3)

def _estomago_int(c, t, p, lt, oa):
    outer = _smooth([(360 + x * 5.6, 500 + y * 5.2) for x, y in [(-34, -22), (-4, -32), (26, -20), (42, 6), (30, 32), (0, 36), (-26, 22), (-42, -4)]], 6)
    inner = _smooth([(360 + x * 4.9, 500 + y * 4.5) for x, y in [(-34, -22), (-4, -32), (26, -20), (42, 6), (30, 32), (0, 36), (-26, 22), (-42, -4)]], 6)
    c.poly(outer, (236, 130, 112), (170, 70, 60), 8)
    c.poly(inner, (252, 198, 172))
    for i in range(7):
        a = i / 7.0 * 2 * math.pi + t * 0.15
        c.line([(360 + 190 * math.cos(a), 500 + 150 * math.sin(a)), (360 + 150 * math.cos(a + 0.12), 500 + 120 * math.sin(a + 0.12))], (236, 160, 136), 7)
    for i in range(5):
        u = (t * 0.2 + i / 5.0) % 1.0
        c.ell(260 + i * 50, 620 - 200 * u, 8 + 5 * (i % 3), outline=(255, 255, 255, int(230 * (1 - u))), w=3)
    shrink = 1 - 0.4 * _ease((lt - 1.0) / 3.0)
    for i, (fx, fy) in enumerate(((300, 540), (430, 600), (380, 450))):
        c.poly(_smooth([(fx + r * math.cos(a) * shrink + 4 * math.sin(t * 2 + i), fy + r * math.sin(a) * shrink) for a, r in [(j * math.pi / 3 + t * 0.3 * (1 if i % 2 else -1), 26 + 8 * (j % 2)) for j in range(6)]], 3), (196, 140, 80), (140, 90, 50), 3)
    n = int(p.get('n', 14))
    for i in range(n):
        ph = i * 1.7
        fx_, fy_ = 0.7 + 0.13 * (i % 5), 0.6 + 0.11 * (i % 4)
        x = 360 + 150 * math.sin(t * fx_ + ph)
        y = 500 + 100 * math.cos(t * fy_ + ph * 1.3)
        vx = 150 * fx_ * math.cos(t * fx_ + ph)
        vy = -100 * fy_ * math.sin(t * fy_ + ph * 1.3)
        ang = math.atan2(vy, vx)
        fl = [(x - math.cos(ang) * (26 + j * 5) + math.sin(j * 1.2 - t * 9) * 5 * math.sin(ang + 1.57), y - math.sin(ang) * (26 + j * 5) + math.sin(j * 1.2 - t * 9) * 5 * math.cos(ang + 1.57)) for j in range(7)]
        c.line(fl, (90, 160, 70), 3)
        c.poly(_caps(x, y, 46, 20, ang), (126, 206, 94), (52, 140, 62), 3)
        c.ell(x + math.cos(ang) * 8, y + math.sin(ang) * 8, 4, fill=(60, 120, 60, 200))
        if i % 3 == 0:
            su = (t * 0.9 + i * 0.3) % 1.0
            c.ell(x, y - 20 - 24 * su, 6 * (1 - su) + 2, fill=(255, 226, 90, int(255 * (1 - su))))

def _hueso(c, t, p, lt, oa):
    ang = -35

    def bone(col, ol, alpha=255):
        sh = [_rot(240, 474, ang), _rot(480, 474, ang), _rot(480, 526, ang), _rot(240, 526, ang)]
        c.poly(sh, col + (alpha,), None)
        for ex in (240, 480):
            for dy in (-34, 34):
                px, py = _rot(ex, 500 + dy, ang)
                c.ell(px, py, 40, fill=col + (alpha,), outline=ol + (alpha,), w=5)
    bone((214, 196, 156), (150, 126, 90))
    for (x0, y0, x1, y1) in ((330, 470, 350, 505), (400, 500, 420, 534), (440, 476, 452, 508)):
        a, b = _rot(x0, y0, ang), _rot(x1, y1, ang)
        c.line([a, ((a[0] + b[0]) / 2 + 8, (a[1] + b[1]) / 2 - 6), b], (96, 70, 48), 5)
    u = _ease((lt - 0.8) / 2.4)
    if u > 0:
        tmp = Image.new('RGBA', c.im.size, (0, 0, 0, 0))
        c3 = c.clone(tmp)
        cl = c
        cl.flush()
        c = c3
        bone((252, 250, 242), (170, 190, 230))
        c3.flush()
        tmp.putalpha(tmp.getchannel('A').point(lambda v: int(v * u)))
        cl.im.alpha_composite(tmp)
        c = cl
        for i in range(6):
            a = t * 2 + i
            px, py = _rot(360 + 150 * math.sin(a * 0.7 + i), 500, ang)
            c.ell(px + 10 * math.cos(a), py + 40 * math.sin(a), 7 + 5 * math.sin(a + i), fill=(255, 255, 255, int(220 * u)))
    a0 = (t * 110) % 360
    c.arc(360, 500, 250, a0, a0 + 250, (255, 206, 70), 14)
    ex_, ey_ = 360 + 250 * math.cos(math.radians(a0 + 250)), 500 + 250 * math.sin(math.radians(a0 + 250))
    th = math.radians(a0 + 250 + 90)
    c.poly([(ex_ + 30 * math.cos(th), ey_ + 30 * math.sin(th)), (ex_ - 24 * math.cos(th) + 20 * math.cos(th - 1.57), ey_ - 24 * math.sin(th) + 20 * math.sin(th - 1.57)), (ex_ - 24 * math.cos(th) - 20 * math.cos(th - 1.57), ey_ - 24 * math.sin(th) - 20 * math.sin(th - 1.57))], (255, 206, 70))

def _pulmon(c, t, p, lt, oa):
    kk = 1 + 0.10 * math.sin(t * 2.4)
    _lungs(c, 360, 520, kk, 100, 170, 108)
    for i in range(14):
        s_ = (i / 14.0 + t * 0.4) % 1.0
        down = math.cos(t * 2.4) > 0
        y = 250 + 200 * (s_ if down else 1 - s_)
        c.ell(360 + 18 * math.sin(i * 2.3 + t * 3), y, 7, outline=(120, 190, 255, int(255 * (1 - abs(s_ - 0.5) * 1.4))), w=3)

def _engranajes(c, t, p, lt, oa):
    for (x, y, r, n, d) in p.get('gs', [(190, 380, 70, 10, 1), (540, 640, 90, 12, -1), (170, 720, 54, 8, -1)]):
        a0 = t * 40 * d
        pts = []
        for i in range(n * 4):
            a = math.radians(a0 + i * 360.0 / (n * 4))
            rr_ = r * (1.22 if (i % 4) in (0, 1) else 1.0)
            pts.append((x + rr_ * math.cos(a), y + rr_ * math.sin(a)))
        c.poly(pts, (126, 148, 200), (66, 84, 140), 4)
        c.ell(x, y, r * 0.55, fill=(196, 210, 240), outline=(66, 84, 140), w=4)
        c.ell(x, y, r * 0.22, fill=(66, 84, 140))

def _check(c, t, p, lt, oa):
    x, y = p.get('x', 360), p.get('y', 500)
    c.ell(x, y, 80, fill=(60, 200, 120), outline=(255, 255, 255), w=8)
    c.line([(x - 36, y + 2), (x - 8, y + 30), (x + 40, y - 30)], (255, 255, 255), 18)

def _corazones(c, t, p, lt, oa):
    for i in range(7):
        u = (t * 0.3 + i / 7.0) % 1.0
        x = 150 + (i * 89) % 420 + 12 * math.sin(t * 2 + i)
        c.push(x, 700 - 420 * u, 0.5 + 0.5 * (1 - u))
        _heart(c, x, 700 - 420 * u, 20, (255, 90, 130, int(255 * min(1, 2 * (1 - u)))), (200, 40, 80, int(255 * min(1, 2 * (1 - u)))))
        c.pop()

PIEZAS = {'cuerpo': _cuerpo, 'ecg': _ecg, 'contador': _contador, 'pill': _pill, 'texto': _texto, 'bebe': _bebe,
          'cerebro': _cerebro_det, 'bateria': _bateria, 'ojo': _ojo, 'estomago': _estomago_int, 'hueso': _hueso,
          'pulmon': _pulmon, 'engranajes': _engranajes, 'check': _check, 'corazones': _corazones}
HUD = ('ecg', 'contador', 'pill', 'texto', 'bateria')

def _T(sc, v, d=0.05):
    if v is None:
        return d
    if isinstance(v, (int, float)):
        return float(v)
    return cue(sc, v, d)

def _ancla(sc, p, nom):
    if isinstance(nom, (list, tuple)):
        return float(nom[0]), float(nom[1])
    for pc in p.get('piezas', []):
        if pc.get('k') == 'cuerpo' and nom in ANCLAS:
            ox, oy, k = float(pc.get('x', 360)), float(pc.get('y', 500)), float(pc.get('esc', 1.0))
            ax, ay = ANCLAS[nom]
            return ox + (ax - 360) * k, oy + (ay - 500) * k
    return CX, CY

def _camara(sc, p, t):
    z, f = 1.0, (CX, CY)
    kfs = sorted(p.get('camara') or [], key=lambda k: _T(sc, k.get('en'), 0.0))
    for kf in kfs:
        t0 = _T(sc, kf.get('en'), 0.0)
        if t <= t0:
            break
        dur = float(kf.get('dur', 0.8))
        zt = float(kf.get('zoom', 1.0))
        ft = _ancla(sc, p, kf.get('foco', (CX, CY)))
        u = _ease((t - t0) / dur) if dur > 0 else 1.0
        z2 = z * (zt / z) ** u
        f2 = (f[0] + (ft[0] - f[0]) * u, f[1] + (ft[1] - f[1]) * u)
        if u >= 1.0:
            z, f = zt, ft
        else:
            z, f = z2, f2
            break
    return z * (1 + 0.012 * math.sin(t * 0.9)), (f[0] + 5 * math.sin(t * 0.7), f[1] + 4 * math.cos(t * 0.6))

def n_guion(d, t, sc):
    _E.fijar(sc)
    p = sc['p']
    img = d._image
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    z, (fx, fy) = _camara(sc, p, t)
    c = C(lay, z, fx, fy)
    for pc in p.get('piezas', []):
        kd = pc.get('k')
        fn = PIEZAS.get(kd)
        if not fn:
            continue
        en = _T(sc, pc.get('en'), 0.05)
        a = prog(t, en, en + 0.4)
        if a <= 0:
            continue
        ao = 0.0
        if pc.get('sal') is not None:
            s0 = _T(sc, pc.get('sal'), 99.0)
            ao = prog(t, s0, s0 + 0.35)
            if ao >= 1:
                continue
        hud = kd in HUD or bool(pc.get('hud'))
        esc = float(pc.get('esc', 1.0))
        k = esc * (0.55 + 0.45 * _back(a))
        oa = {}
        for o in pc.get('organos') or []:
            if not isinstance(o, str):
                oa[o[0]] = _back(prog(t, _T(sc, o[1], 0.05), _T(sc, o[1], 0.05) + 0.45))
        if pc.get('resalta_en') is not None:
            oa['_res'] = _out(prog(t, _T(sc, pc.get('resalta_en')), _T(sc, pc.get('resalta_en')) + 0.4))
        elif pc.get('resalta'):
            oa['_res'] = 1.0
        alpha = min(1.0, a * 1.8) * (1 - ao)
        lt = t - en
        lupa = pc.get('lupa')
        if alpha > 0.98 and not lupa:
            c.place(CX if hud else float(pc.get('x', 360)), CY if hud else float(pc.get('y', 500)), 1.0 if hud else k, hud)
            fn(c, t, pc, lt, oa)
            c.flush()
        else:
            tmp = Image.new('RGBA', lay.size, (0, 0, 0, 0))
            c2 = c.clone(tmp)
            if lupa:
                x0, y0, x1, y1, R = [float(v) for v in lupa]
                e = _out(a)
                lx, ly, R2 = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e, R * e
                c2.hud = True
                c2.t = (lx, ly, CX, CY, max(0.05, R2 / 300.0 * esc))
                fn(c2, t, pc, lt, oa)
                c2.flush()
                m = Image.new('L', lay.size, 0)
                ImageDraw.Draw(m).ellipse([(lx - R2) * S, (ly - R2) * S, (lx + R2) * S, (ly + R2) * S], fill=255)
                tmp.putalpha(ImageChops.multiply(tmp.getchannel('A'), m))
                ImageDraw.Draw(tmp, 'RGBA').ellipse([(lx - R2) * S, (ly - R2) * S, (lx + R2) * S, (ly + R2) * S], outline=(255, 214, 60, 255), width=int(10 * S))
                alpha = (1 - ao)
            else:
                c2.place(CX if hud else float(pc.get('x', 360)), CY if hud else float(pc.get('y', 500)), 1.0 if hud else k, hud)
                fn(c2, t, pc, lt, oa)
                c2.flush()
            if alpha < 0.98:
                tmp.putalpha(tmp.getchannel('A').point(lambda v, al=alpha: int(v * al)))
            lay.alpha_composite(tmp)
    r = None
    if _E.ESTILO['modo'] == 'negro':
        r = _E._tint(lay, 1.0, True)
    if r:
        img.alpha_composite(r[0], dest=(r[1], r[2]))
    elif _E.ESTILO['modo'] != 'negro':
        img.alpha_composite(lay)

def e_guion(sc):
    ev = []
    for pc in sc['p'].get('piezas', []):
        en = _T(sc, pc.get('en'), 0.05)
        ev.append((en, 'pop'))
        if pc.get('k') == 'contador':
            ev.append((en + float(pc.get('dur', 1.8)) * 0.8, 'ching'))
    return ev

PLANTILLAS['guion'] = (n_guion, e_guion)
