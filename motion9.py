import math
from PIL import Image, ImageChops, ImageDraw
import estilo_morado as _E
from motion6 import S, prog
from motion8 import (C, PIEZAS, HUD, CX, CY, _ease, _out, _back, _g, _hsv, _smooth, _rot, _caps, _heart, _heart_pts, _T)
COL = {'rojo': (226, 62, 78), 'verde': (66, 178, 104), 'azul': (66, 118, 224), 'amarillo': (250, 206, 60), 'naranja': (250, 148, 48),
       'morado': (150, 92, 222), 'rosa': (248, 130, 178), 'blanco': (250, 250, 252), 'negro': (44, 44, 58), 'gris': (150, 156, 172),
       'oro': (255, 204, 58), 'marron': (140, 92, 58), 'piel': (252, 208, 168), 'celeste': (130, 200, 250), 'beige': (240, 214, 170)}
PIEL = (252, 208, 168)
def _col(v, d=(66, 118, 224)):
    if isinstance(v, (list, tuple)) and len(v) >= 3:
        return tuple(int(x) for x in v[:3])
    return COL.get(str(v), d)
def _dk(c, f=0.62):
    return tuple(int(x * f) for x in c[:3])
def _lt(c, f=0.4):
    return tuple(int(x + (255 - x) * f) for x in c[:3])
def _clip(c, fn, shape_fn):
    c.flush()
    c2 = c.clone(Image.new('RGBA', c.im.size, (0, 0, 0, 0)))
    fn(c2)
    c2.flush()
    m = Image.new('L', c.im.size, 0)
    shape_fn(ImageDraw.Draw(m), c)
    c2.im.putalpha(ImageChops.multiply(c2.im.getchannel('A'), m))
    c.im.alpha_composite(c2.im)
def _arm(c, sx, sy, a1, a2, col, l1=70, l2=64):
    a1, a2 = math.radians(a1), math.radians(a2)
    ex, ey = sx + math.cos(a1) * l1, sy + math.sin(a1) * l1
    wx, wy = ex + math.cos(a2) * l2, ey + math.sin(a2) * l2
    c.line([(sx, sy), (ex, ey)], col, 24)
    c.line([(ex, ey), (wx, wy)], PIEL, 20)
    c.ell(wx, wy, 13, fill=PIEL)
    return wx, wy
def _persona(c, t, p, lt, oa):
    pose = p.get('pose', 'parado')
    ropa = _col(p.get('ropa', 'azul'))
    pelo = _col(p.get('pelo', 'marron'))
    pant = _col(p.get('pantalon', 'negro'))
    acc = p.get('acc')
    run = pose == 'corre'
    bob = 10 * abs(math.sin(t * 9)) if run else 4 * math.sin(t * 3)
    sw = math.sin(t * (9 if run else 2.2))
    by = -bob
    if acc == 'capa':
        c.poly([(330, 400 + by), (390, 400 + by), (430 + 14 * sw, 640 + by), (290 - 14 * sw, 640 + by)], (214, 50, 70))
    for sgn, hx in ((-1, 342), (1, 378)):
        ph = sw * sgn
        fx = hx + (46 * ph if run else 6 * sgn)
        fy = 725 - (22 * max(0, ph) if run else 0)
        kx = (hx + fx) / 2 + (18 if run else 0)
        c.line([(hx, 560 + by), (kx, 645 + by * 0.5), (fx, fy)], pant, 28)
        c.ell(fx + 8, fy + 6, 22, 11, fill=(60, 52, 70))
    c.rr(318, 392 + by, 402, 568 + by, 28, ropa)
    c.rr(318, 392 + by, 402, 430 + by, 20, _lt(ropa, 0.18))
    sh = 404 + by
    wob = 14 * math.sin(t * 8)
    wR = None
    if pose in ('celebra', 'feliz'):
        _arm(c, 322, sh, -135 + wob, -105 - wob, ropa)
        wR = _arm(c, 398, sh, -45 - wob, -75 + wob, ropa)
    elif pose == 'señala' or pose == 'senala':
        _arm(c, 322, sh, 100, 96, ropa)
        wR = _arm(c, 398, sh, -12 + 4 * math.sin(t * 5), -12, ropa)
    elif pose == 'sorpresa':
        _arm(c, 322, sh, 160 + 6 * sw, 200, ropa)
        wR = _arm(c, 398, sh, 20 - 6 * sw, -20, ropa)
    elif pose == 'piensa':
        _arm(c, 322, sh, 98, 94, ropa)
        wR = _arm(c, 398, sh, 55, -105, ropa)
    elif pose == 'triste':
        _arm(c, 322, sh, 98, 96, ropa)
        wR = _arm(c, 398, sh, 82, 84, ropa)
    elif run:
        _arm(c, 322, sh, 90 + 50 * sw, 90 + 100 * sw, ropa)
        wR = _arm(c, 398, sh, 90 - 50 * sw, 90 - 100 * sw, ropa)
    else:
        _arm(c, 322, sh, 100 + 4 * sw, 96, ropa)
        wR = _arm(c, 398, sh, 80 - 4 * sw, 84, ropa)
    hy = 322 + by + (10 if pose == 'triste' else 0)
    c.rr(348, 372 + by, 372, 398 + by, 8, PIEL)
    c.ell(360, hy - 14, 56, 52, fill=pelo)
    c.ell(360, hy, 52, 54, fill=PIEL, outline=(214, 160, 120), w=3)
    c.ell(360, hy - 38, 54, 24, fill=pelo)
    blink = max(0.0, 1 - abs((t % 3.1) - 3.0) * 8)
    ey = 5 * (1 - 0.9 * blink)
    for ex in (342, 378):
        c.ell(ex, hy + 2, 6, ey + 0.6, fill=(40, 30, 40))
    if pose in ('feliz', 'celebra'):
        c.arc(360, hy + 14, 20, 15, 165, (150, 50, 60), 5)
    elif pose == 'triste':
        c.arc(360, hy + 34, 16, 200, 340, (150, 50, 60), 5)
        c.line([(332, hy - 12), (350, hy - 17)], (90, 60, 50), 4)
        c.line([(388, hy - 12), (370, hy - 17)], (90, 60, 50), 4)
        c.ell(344, hy + 26 + 18 * ((t * 1.5) % 1), 5, 8, fill=(120, 190, 255))
    elif pose == 'sorpresa':
        c.ell(360, hy + 28, 9, 12, fill=(120, 40, 50))
        c.line([(332, hy - 16), (350, hy - 12)], (90, 60, 50), 4)
        c.line([(388, hy - 16), (370, hy - 12)], (90, 60, 50), 4)
    else:
        c.line([(350, hy + 28), (370, hy + 28)], (150, 50, 60), 4)
    if pose in ('feliz', 'celebra', 'sorpresa'):
        for sx in (-1, 1):
            c.ell(360 + sx * 34, hy + 18, 10, 6, fill=(255, 150, 150, 160))
    if pose == 'piensa':
        for i, (bx, by2, r) in enumerate(((430, hy - 50, 7), (450, hy - 80, 11), (480, hy - 125, 34))):
            c.ell(bx, by2 - 4 * math.sin(t * 3 + i), r, fill=(255, 255, 255), outline=(120, 110, 150), w=3)
        c.text(480, hy - 125, '?', 40, (90, 70, 160))
    if acc == 'sombrero':
        c.rr(322, hy - 100, 398, hy - 48, 6, (36, 36, 48))
        c.rr(300, hy - 56, 420, hy - 40, 6, (36, 36, 48))
        c.rr(322, hy - 70, 398, hy - 58, 2, (210, 60, 70))
    elif acc == 'corona':
        pts = [(322, hy - 44), (322, hy - 92), (342, hy - 68), (360, hy - 100), (378, hy - 68), (398, hy - 92), (398, hy - 44)]
        c.poly(pts, COL['oro'], (190, 130, 20), 3)
        for x in (322, 360, 398):
            c.ell(x, hy - 94 if x != 360 else hy - 102, 6, fill=(226, 62, 78))
    elif acc == 'gorra':
        c.arc(360, hy - 22, 54, 180, 360, COL['rojo'], 22)
        c.rr(360, hy - 42, 440, hy - 30, 6, COL['rojo'])
    elif acc == 'lentes':
        for ex in (342, 378):
            c.ell(ex, hy + 2, 16, outline=(40, 40, 50), w=4)
        c.line([(358, hy + 2), (362, hy + 2)], (40, 40, 50), 4)
    elif acc == 'maletin' and wR:
        c.rr(wR[0] - 28, wR[1] + 4, wR[0] + 34, wR[1] + 52, 8, COL['marron'], (90, 55, 30), 3)
        c.rr(wR[0] - 8, wR[1] - 6, wR[0] + 14, wR[1] + 6, 4, outline=(90, 55, 30), w=3)
    elif acc == 'casco':
        c.arc(360, hy - 14, 56, 180, 360, COL['amarillo'], 26)
        c.rr(304, hy - 20, 416, hy - 8, 6, COL['amarillo'])
def _moneda(c, x, y, r, ph, col=COL['oro']):
    w = max(0.08, abs(math.cos(ph))) * r
    c.ell(x, y, w, r, fill=col, outline=_dk(col, 0.7), w=max(2.0, r * 0.1))
    if w > r * 0.4:
        c.ell(x, y, w * 0.72, r * 0.72, outline=_dk(col, 0.85), w=max(1.5, r * 0.05))
        c.push(x, y, w / r)
        c.text(x, y, '$', r * 1.1, _dk(col, 0.62))
        c.pop()
def _dinero(c, t, p, lt, oa):
    tp = p.get('tipo', 'pila')
    n = int(p.get('n', 8))
    if tp == 'moneda':
        _moneda(c, 360, 500 + 8 * math.sin(t * 2.5), 120, t * 3.2)
        for i in range(4):
            a = t * 1.5 + i * 1.57
            s = 0.5 + 0.5 * math.sin(t * 5 + i)
            c.line([(360 + 150 * math.cos(a) - 12 * s, 500 + 130 * math.sin(a)), (360 + 150 * math.cos(a) + 12 * s, 500 + 130 * math.sin(a))], (255, 255, 255), 4)
    elif tp == 'pila':
        for k, (x, fr) in enumerate(((250, 0.5), (360, 1.0), (470, 0.72))):
            cnt = int(max(1, n * fr) * prog(lt, 0.1 + 0.15 * k, 1.5 + 0.15 * k))
            for i in range(cnt):
                yy = 690 - i * 22
                c.ell(x, yy + 12, 78, 24, fill=_dk(COL['oro'], 0.78))
                c.rr(x - 78, yy - 4, x + 78, yy + 12, 2, _dk(COL['oro'], 0.78))
                c.ell(x, yy - 4, 78, 24, fill=COL['oro'], outline=(190, 130, 20), w=3)
            if cnt:
                top = 690 - (cnt - 1) * 22
                c.ell(x, top - 4, 46, 13, outline=(214, 160, 30), w=3)
    elif tp == 'bolsa':
        sq = 1 + 0.05 * math.sin(t * 4)
        c.push(360, 690, 1 / sq)
        c.poly(_smooth([(300, 560), (420, 560), (500, 650), (480, 700), (360, 716), (240, 700), (220, 650)], 6), (196, 150, 90), (120, 80, 40), 5)
        c.pop()
        c.poly([(318, 566), (342, 520), (378, 520), (402, 566)], (196, 150, 90), (120, 80, 40), 5)
        c.rr(316, 556, 404, 576, 8, (214, 60, 70))
        c.text(360, 650, '$', 120, (255, 236, 160), 4, (110, 70, 20))
        for i in range(5):
            u = (t * 0.8 + i / 5.0) % 1.0
            _moneda(c, 360 + 90 * math.sin(i * 2.4) * u, 520 - 220 * u + 120 * u * u, 22 * (1 - 0.3 * u), t * 8 + i)
    elif tp == 'billete':
        for k, ang in enumerate((-12, 0, 12)):
            if lt < 0.12 * k:
                continue
            a = ang + 4 * math.sin(t * 2 + k)
            bx, by = 360 + (k - 1) * 30, 520 + (1 - k) * 4 - 6 * k
            pts = [_rot(x, y, a, bx, by) for x, y in ((bx - 150, by - 78), (bx + 150, by - 78), (bx + 150, by + 78), (bx - 150, by + 78))]
            c.poly(pts, (92, 176, 108), (44, 110, 62), 5)
            inn = [_rot(x, y, a, bx, by) for x, y in ((bx - 134, by - 62), (bx + 134, by - 62), (bx + 134, by + 62), (bx - 134, by + 62))]
            c.poly(inn, outline=(180, 230, 190), w=3)
            q = _rot(bx, by, a, bx, by)
            c.ell(q[0], q[1], 42, fill=(120, 200, 134), outline=(44, 110, 62), w=4)
            c.text(q[0], q[1], '$', 56, (30, 90, 50))
    elif tp == 'lluvia':
        for i in range(max(10, n * 3)):
            sp = 0.25 + 0.15 * ((i * 7) % 5)
            u = (t * sp + (i * 0.618)) % 1.0
            x = 90 + (i * 137) % 540 + 14 * math.sin(t * 2 + i)
            y = 190 + 620 * u
            if i % 3 == 0:
                a = 20 * math.sin(t * 3 + i)
                pts = [_rot(x + dx, y + dy, a, x, y) for dx, dy in ((-30, -16), (30, -16), (30, 16), (-30, 16))]
                c.poly(pts, (92, 176, 108), (44, 110, 62), 3)
                c.text(x, y, '$', 20, (30, 90, 50))
            else:
                _moneda(c, x, y, 20, t * 7 + i)
    elif tp == 'lingotes':
        rows = [(3, 690), (2, 640), (1, 590)]
        k = 0
        for cnt, y in rows:
            for j in range(cnt):
                x = 360 + (j - (cnt - 1) / 2.0) * 150
                u = prog(lt, 0.15 * k, 0.15 * k + 0.4)
                k += 1
                if u <= 0:
                    continue
                yy = y - 120 * (1 - _out(u))
                pts = [(x - 62, yy + 20), (x + 62, yy + 20), (x + 44, yy - 20), (x - 44, yy - 20)]
                c.poly(pts, COL['oro'], (190, 130, 20), 4)
                c.poly([(x - 44, yy - 20), (x + 44, yy - 20), (x + 36, yy - 32), (x - 36, yy - 32)], (255, 232, 140), (190, 130, 20), 3)
                sh = (t * 1.2 + k * 0.3) % 1.6
                if sh < 0.5:
                    c.line([(x - 40 + 90 * sh * 2, yy - 16), (x - 20 + 90 * sh * 2, yy + 16)], (255, 255, 255, 190), 8)
def _grafica(c, t, p, lt, oa):
    tp = p.get('tipo', 'linea')
    x0, y0, x1, y1 = 110, 330, 610, 700
    c.rr(x0 - 30, y0 - 40, x1 + 30, y1 + 40, 26, (255, 255, 255, 235), (120, 110, 160), 4)
    c.line([(x0, y0), (x0, y1), (x1, y1)], (110, 104, 140), 5)
    for i in range(1, 4):
        yy = y1 - (y1 - y0) * i / 4
        c.line([(x0, yy), (x1, yy)], (225, 222, 238), 2)
    dur = float(p.get('dur', 2.0))
    u = _ease((lt - 0.2) / dur)
    if tp == 'linea':
        pts = p.get('pts') or [0.1, 0.25, 0.2, 0.45, 0.4, 0.7, 0.95]
        up = pts[-1] >= pts[0]
        col = _col(p.get('color', 'verde' if up else 'rojo'))
        n = len(pts)
        xs = [x0 + 20 + (x1 - x0 - 40) * i / (n - 1) for i in range(n)]
        ys = [y1 - 14 - (y1 - y0 - 40) * v for v in pts]
        full = u * (n - 1)
        seg = [(xs[0], ys[0])]
        for i in range(1, n):
            if full >= i:
                seg.append((xs[i], ys[i]))
            elif full > i - 1:
                f = full - (i - 1)
                seg.append((xs[i - 1] + (xs[i] - xs[i - 1]) * f, ys[i - 1] + (ys[i] - ys[i - 1]) * f))
        if len(seg) > 1:
            c.poly(seg + [(seg[-1][0], y1), (seg[0][0], y1)], col + (70,))
            c.line(seg, col, 11)
            ex, ey = seg[-1]
            c.ell(ex, ey, 15 + 3 * math.sin(t * 6), fill=(255, 255, 255), outline=col, w=6)
            if p.get('etiqueta') and u > 0.85:
                c.text(min(ex, 540), ey - 44, str(p['etiqueta']), 44, col, 3, (255, 255, 255))
    elif tp == 'barras':
        vals = p.get('vals') or [0.25, 0.4, 0.55, 0.8, 1.0]
        n = len(vals)
        bw = (x1 - x0 - 40) / n
        for i, v in enumerate(vals):
            uu = _back(prog(lt, 0.2 + 0.2 * i, 0.2 + 0.2 * i + 0.6))
            h = (y1 - y0 - 40) * v * uu
            col = _hsv(0.32 - 0.3 * v if p.get('arcoiris') else 0.58 - 0.08 * i / max(1, n - 1), 0.65, 0.95)
            if p.get('color'):
                col = _col(p['color'])
            bx = x0 + 30 + bw * i
            c.rr(bx, y1 - h, bx + bw * 0.78, y1 - 2, 10, col, _dk(col), 3)
            labs = p.get('etiquetas')
            if labs and i < len(labs):
                c.text(bx + bw * 0.39, y1 + 20, str(labs[i]), 22, (90, 84, 120))
    elif tp == 'pastel':
        parts = p.get('partes') or [0.6, 0.3, 0.1]
        cols = [COL['azul'], COL['naranja'], COL['verde'], COL['rosa'], COL['morado']]
        a0 = -90.0
        tot = sum(parts)
        for i, v in enumerate(parts):
            sweep = 360.0 * v / tot * u
            pts = [(360, 515)]
            for k in range(0, 41):
                a = math.radians(a0 + sweep * k / 40.0)
                pts.append((360 + 175 * math.cos(a), 515 + 175 * math.sin(a)))
            c.poly(pts, cols[i % 5], (255, 255, 255), 4)
            if u > 0.9:
                am = math.radians(a0 + sweep / 2)
                c.text(360 + 108 * math.cos(am), 515 + 108 * math.sin(am), '%d%%' % round(100.0 * v / tot), 34, (255, 255, 255), 3, _dk(cols[i % 5]))
            a0 += 360.0 * v / tot
def _i_casa(c, t, lt, o):
    for i in range(4):
        u = (t * 0.5 + i / 4.0) % 1.0
        c.ell(440 + 14 * math.sin(u * 6), 410 - 120 * u, 8 + 18 * u, fill=(235, 235, 245, int(200 * (1 - u))))
    c.rr(430, 420, 460, 500, 4, (170, 90, 80))
    c.rr(250, 500, 470, 690, 8, (244, 224, 186), (190, 160, 110), 4)
    c.poly([(220, 506), (500, 506), (360, 380)], (214, 76, 70), (140, 40, 40), 5)
    c.rr(334, 590, 388, 690, 8, COL['marron'], (90, 55, 30), 3)
    c.ell(374, 642, 4, fill=COL['oro'])
    lit = 0.6 + 0.4 * math.sin(t * 2)
    for x in (274, 410):
        c.rr(x, 540, x + 46, 590, 5, (130 + int(100 * lit), 200 + int(40 * lit), 255), (120, 90, 60), 4)
        c.line([(x + 23, 540), (x + 23, 590)], (120, 90, 60), 3)
def _i_edificio(c, t, lt, o):
    c.rr(260, 330, 460, 690, 6, (110, 126, 170), (70, 80, 120), 4)
    c.rr(240, 320, 480, 346, 4, (86, 98, 140))
    for r in range(8):
        for q in range(4):
            on = math.sin(r * 1.7 + q * 2.3 + t * 0.8) > -0.2
            c.rr(278 + q * 44, 362 + r * 38, 306 + q * 44, 388 + r * 38, 3, (255, 232, 140) if on else (80, 92, 134))
    c.rr(334, 640, 386, 690, 4, (60, 70, 110))
def _i_banco(c, t, lt, o):
    c.poly([(230, 440), (490, 440), (360, 340)], (236, 232, 244), (130, 124, 160), 5)
    c.text(360, 410, '$', 56, (90, 140, 100))
    for i in range(4):
        x = 270 + i * 60
        c.rr(x - 16, 450, x + 16, 630, 4, (248, 246, 252), (150, 144, 176), 3)
    c.rr(240, 630, 480, 654, 4, (214, 210, 226), (150, 144, 176), 3)
    c.rr(220, 654, 500, 686, 4, (190, 186, 206), (150, 144, 176), 3)
    for i in range(3):
        u = (t * 0.6 + i / 3.0) % 1.0
        _moneda(c, 360 + (i - 1) * 90, 330 - 120 * u, 18, t * 6 + i)
def _i_castillo(c, t, lt, o):
    c.rr(250, 540, 470, 690, 4, (214, 196, 168), (150, 130, 100), 4)
    for i in range(6):
        c.rr(254 + i * 38, 520, 280 + i * 38, 544, 2, (214, 196, 168), (150, 130, 100), 3)
    for x in (214, 430):
        c.rr(x, 430, x + 76, 690, 4, (200, 180, 150), (150, 130, 100), 4)
        c.poly([(x - 10, 436), (x + 86, 436), (x + 38, 350)], (206, 70, 80), (130, 40, 50), 4)
        c.rr(x + 28, 480, x + 48, 524, 8, (70, 60, 90))
    c.poly(_smooth([(330, 690), (330, 620), (360, 590), (390, 620), (390, 690)], 5), (90, 60, 50), (50, 30, 30), 4)
    c.line([(252, 350), (252, 300)], (110, 90, 70), 4)
    c.poly([(252, 300)] + [(252 + i * 6, 300 + 4 * math.sin(t * 6 - i)) for i in range(1, 9)] + [(300, 326), (252, 330)], COL['rojo'])
def _i_piramide(c, t, lt, o):
    c.ell(480, 360, 62 + 3 * math.sin(t * 2), fill=(255, 226, 120), outline=(255, 190, 60), w=4)
    c.poly([(190, 690), (530, 690), (360, 400)], (236, 200, 120), (170, 130, 70), 5)
    c.poly([(360, 400), (530, 690), (400, 690)], (214, 172, 98))
    for i in range(1, 6):
        y = 400 + i * 48
        hw = (y - 400) * 0.5
        c.line([(360 - hw, y), (360 + hw, y)], (190, 150, 90), 3)
def _i_barco(c, t, lt, o):
    tilt = 5 * math.sin(t * 1.6)
    by = 8 * math.sin(t * 1.6)
    def P(x, y):
        return _rot(x, y + by, tilt, 360, 640)
    c.line([P(360, 640), P(360, 380)], (110, 80, 50), 8)
    bil = 10 * math.sin(t * 2)
    c.poly([P(366, 392), P(366, 590), P(470 + bil, 580), P(430 + bil * 0.5, 480)], (250, 250, 252), (160, 160, 180), 4)
    c.poly([P(354, 410), P(354, 590), P(280 - bil, 580), P(300 - bil * 0.5, 480)], (240, 240, 248), (160, 160, 180), 4)
    c.poly([P(210, 610), P(510, 610), P(450, 690), P(270, 690)], (150, 96, 60), (90, 55, 30), 5)
    c.poly([P(360, 380), P(410, 396), P(360, 412)], COL['rojo'])
    for k in range(3):
        pts = [(110 + i * 20, 700 + 10 * math.sin(i * 0.8 + t * 3 + k) + k * 22) for i in range(0, 31)]
        c.line(pts, (120, 186, 240) if k % 2 == 0 else (90, 150, 224), 12)
def _i_avion(c, t, lt, o):
    y = 8 * math.sin(t * 2)
    for i in range(3):
        u = (t * 0.8 + i / 3.0) % 1.0
        c.ell(200 - 120 * u, 520 + y, 24 * (1 - u) + 6, fill=(255, 255, 255, int(200 * (1 - u))))
    c.poly(_smooth([(180, 500 + y), (240, 470 + y), (470, 470 + y), (560, 500 + y), (470, 540 + y), (240, 540 + y)], 5), (248, 250, 255), (140, 150, 190), 5)
    c.poly([(360, 500 + y), (300, 600 + y), (350, 604 + y), (430, 510 + y)], (200, 212, 240), (140, 150, 190), 4)
    c.poly([(360, 480 + y), (290, 380 + y), (340, 380 + y), (420, 480 + y)], (214, 224, 248), (140, 150, 190), 4)
    c.poly([(190, 490 + y), (170, 430 + y), (216, 430 + y), (260, 480 + y)], (226, 62, 78), (150, 40, 50), 3)
    for i in range(5):
        c.ell(300 + i * 36, 492 + y, 8, fill=(130, 200, 250))
    c.ell(520, 498 + y, 14, 10, fill=(130, 200, 250))
def _i_carro(c, t, lt, o):
    y = 3 * math.sin(t * 14)
    for i in range(6):
        x = (i * 140 - t * 300) % 840 - 60
        c.rr(x, 718, x + 70, 728, 4, (230, 230, 245))
    c.poly(_smooth([(190, 640 + y), (190, 570 + y), (260, 560 + y), (310, 500 + y), (440, 500 + y), (500, 560 + y), (540, 580 + y), (540, 640 + y)], 4), COL['azul'], (40, 70, 150), 5)
    c.poly([(322, 512 + y), (430, 512 + y), (478, 560 + y), (288, 560 + y)], (190, 226, 252), (40, 70, 150), 4)
    c.line([(380, 512 + y), (380, 560 + y)], (40, 70, 150), 4)
    for x in (270, 466):
        c.ell(x, 650, 44, fill=(50, 50, 64), outline=(30, 30, 40), w=4)
        c.ell(x, 650, 22, fill=(200, 204, 220))
        for k in range(5):
            a = t * 14 + k * 1.2566
            c.line([(x, 650), (x + 22 * math.cos(a), 650 + 22 * math.sin(a))], (120, 124, 144), 3)
    c.ell(536, 604 + y, 12, 8, fill=(255, 236, 140))
def _i_cohete(c, t, lt, o):
    sh = 4 * math.sin(t * 30)
    rise = 14 * math.sin(t * 2)
    for i in range(9):
        u = (t * 1.5 + i / 9.0) % 1.0
        c.ell(60 + (i * 83) % 600, 220 + 560 * u, 3, fill=(255, 255, 255, 200))
    fl = 1 + 0.25 * math.sin(t * 40)
    c.poly([(332, 650 + rise), (388, 650 + rise), (360, 700 + 90 * fl + rise)], (255, 150, 50))
    c.poly([(344, 650 + rise), (376, 650 + rise), (360, 680 + 50 * fl + rise)], (255, 232, 120))
    c.poly(_smooth([(290 + sh, 640 + rise), (290 + sh, 480 + rise), (330, 380 + rise), (360, 340 + rise), (390, 380 + rise), (430 + sh, 480 + rise), (430 + sh, 640 + rise)], 5), (248, 250, 255), (140, 150, 190), 5)
    c.poly(_smooth([(318, 400 + rise), (360, 330 + rise), (402, 400 + rise), (360, 420 + rise)], 4), COL['rojo'], (150, 40, 50), 4)
    c.ell(360, 500 + rise, 34, fill=(130, 200, 250), outline=(90, 110, 170), w=6)
    c.poly([(290, 560 + rise), (240, 660 + rise), (292, 640 + rise)], COL['rojo'], (150, 40, 50), 4)
    c.poly([(430, 560 + rise), (480, 660 + rise), (428, 640 + rise)], COL['rojo'], (150, 40, 50), 4)
def _i_reloj(c, t, lt, o):
    c.ell(360, 500, 190, fill=(250, 250, 255), outline=(60, 60, 90), w=14)
    for i in range(12):
        a = i * math.pi / 6
        r1 = 156 if i % 3 else 140
        c.line([(360 + r1 * math.sin(a), 500 - r1 * math.cos(a)), (360 + 170 * math.sin(a), 500 - 170 * math.cos(a))], (60, 60, 90), 8 if i % 3 == 0 else 4)
    am = t * 2.4
    ah = am / 12
    c.line([(360, 500), (360 + 100 * math.sin(ah), 500 - 100 * math.cos(ah))], (50, 50, 80), 14)
    c.line([(360, 500), (360 + 148 * math.sin(am), 500 - 148 * math.cos(am))], (50, 50, 80), 9)
    asx = t * 14
    c.line([(360 - 30 * math.sin(asx), 500 + 30 * math.cos(asx)), (360 + 156 * math.sin(asx), 500 - 156 * math.cos(asx))], COL['rojo'], 4)
    c.ell(360, 500, 12, fill=COL['rojo'])
def _i_calendario(c, t, lt, o):
    c.rr(220, 340, 500, 680, 22, (252, 252, 255), (110, 104, 150), 6)
    c.rr(220, 340, 500, 420, 22, COL['rojo'], (150, 40, 50), 6)
    for x in (290, 430):
        c.rr(x - 8, 316, x + 8, 366, 8, (70, 70, 96))
    for r in range(4):
        for q in range(5):
            n = r * 5 + q
            x, y = 262 + q * 48, 458 + r * 54
            c.text(x, y, str(n + 1), 24, (90, 84, 120))
            if lt > 0.3 + 0.12 * n and n < 14:
                u = _back(prog(lt, 0.3 + 0.12 * n, 0.3 + 0.12 * n + 0.3))
                c.line([(x - 16 * u, y - 16 * u), (x + 16 * u, y + 16 * u)], COL['rojo'], 5)
                c.line([(x + 16 * u, y - 16 * u), (x - 16 * u, y + 16 * u)], COL['rojo'], 5)
def _i_libro(c, t, lt, o):
    c.poly([(360, 440), (210, 420), (210, 660), (360, 680)], (250, 246, 236), (130, 100, 70), 5)
    c.poly([(360, 440), (510, 420), (510, 660), (360, 680)], (246, 242, 230), (130, 100, 70), 5)
    for i in range(6):
        c.line([(232, 460 + i * 30), (338, 472 + i * 30)], (190, 184, 200), 4)
    fl = (t * 0.5) % 1.0
    w = math.cos(fl * math.pi)
    if fl < 0.9:
        c.poly([(360, 440), (360 + 150 * w, 420 - 14 * math.sin(fl * math.pi)), (360 + 150 * w, 660 - 14 * math.sin(fl * math.pi)), (360, 680)], (255, 252, 244), (130, 100, 70), 4)
    c.poly([(204, 664), (360, 690), (516, 664), (516, 676), (360, 704), (204, 676)], COL['rojo'], (130, 40, 50), 3)
def _i_bombilla(c, t, lt, o):
    g = 0.5 + 0.5 * math.sin(t * 4)
    for i in range(10):
        a = i * math.pi / 5 + t * 0.4
        c.line([(360 + 160 * math.cos(a), 470 + 160 * math.sin(a)), (360 + (200 + 14 * g) * math.cos(a), 470 + (200 + 14 * g) * math.sin(a))], (255, 214, 70), 8)
    c.ell(360, 470, 120, fill=(255, 238, 140), outline=(230, 170, 40), w=7)
    c.ell(330, 430, 30, 18, fill=(255, 255, 230))
    c.poly(_smooth([(320, 560), (400, 560), (390, 610), (330, 610)], 4), (255, 238, 140), (230, 170, 40), 5)
    c.rr(326, 606, 394, 626, 6, (160, 164, 184), (100, 104, 128), 4)
    c.rr(334, 628, 386, 646, 6, (130, 134, 156), (100, 104, 128), 4)
    c.line([(340, 540), (350, 480), (360, 510), (370, 480), (380, 540)], (230, 120, 30), 5)
def _i_candado(c, t, lt, o):
    op = max(0.0, math.sin(t * 1.2))
    off = 40 * op
    c.arc(360, 480 - off, 84, 180, 360, (170, 176, 196), 24)
    c.line([(276, 480 - off), (276, 520)], (170, 176, 196), 24)
    c.line([(444, 480 - off), (444, 520)], (170, 176, 196), 24)
    c.rr(240, 510, 480, 700, 34, COL['oro'], (190, 130, 20), 7)
    c.ell(360, 586, 26, fill=(110, 70, 20))
    c.poly([(350, 590), (370, 590), (378, 650), (342, 650)], (110, 70, 20))
    c.line([(264, 530), (264, 560)], (255, 240, 170), 8)
def _i_escudo(c, t, lt, o):
    pts = _smooth([(240, 400), (480, 400), (480, 540), (440, 640), (360, 710), (280, 640), (240, 540)], 6)
    c.poly(pts, COL['azul'], (30, 60, 140), 8)
    c.poly(_smooth([(262, 420), (458, 420), (458, 536), (426, 622), (360, 680), (294, 622), (262, 536)], 6), outline=(200, 220, 255), w=5)
    s = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 74 if i % 2 == 0 else 32
        s.append((360 + r * math.cos(a), 540 + r * math.sin(a)))
    c.poly(s, COL['oro'], (190, 130, 20), 4)
    u = (t * 0.7) % 1.6
    if u < 0.8:
        c.line([(250 + 240 * u, 410), (210 + 240 * u, 700)], (255, 255, 255, 120), 22)
def _i_corona(c, t, lt, o):
    c.poly([(230, 640), (230, 440), (300, 540), (360, 410), (420, 540), (490, 440), (490, 640)], COL['oro'], (190, 130, 20), 7)
    c.rr(230, 620, 490, 670, 8, COL['oro'], (190, 130, 20), 7)
    for x, y, col in ((230, 436, 'rojo'), (360, 404, 'azul'), (490, 436, 'verde')):
        c.ell(x, y, 20, fill=COL[col], outline=(255, 255, 255), w=4)
    for i, x in enumerate((290, 360, 430)):
        c.ell(x, 645, 12, fill=COL[('rojo', 'azul', 'verde')[i]])
    for i in range(3):
        u = (t * 1.1 + i / 3.0) % 1.0
        sx, sy = 260 + 200 * ((i * 0.37 + 0.1) % 1), 450 + 160 * ((i * 0.61) % 1)
        s = math.sin(u * math.pi)
        c.line([(sx - 16 * s, sy), (sx + 16 * s, sy)], (255, 255, 255), 5)
        c.line([(sx, sy - 16 * s), (sx, sy + 16 * s)], (255, 255, 255), 5)
def _i_tierra(c, t, lt, o):
    R = 190
    def draw(c2):
        c2.ell(360, 500, R, fill=(70, 150, 230))
        for k in range(2):
            off = (t * 40 + k * 440) % 880 - 220
            for (bx, by, bw, bh) in ((60, -60, 110, 70), (150, 40, 70, 90), (-30, 70, 90, 50), (230, -20, 60, 50)):
                pts = [(360 - R + off + bx + bw * math.cos(a), 500 + by + bh * math.sin(a) * (1 + 0.15 * math.sin(3 * a))) for a in [i * math.pi / 8 for i in range(16)]]
                c2.poly(pts, (88, 186, 110), (60, 140, 80), 3)
    _clip(c, draw, lambda m, cc: m.ellipse([cc.P(360 - R, 500 - R), cc.P(360 + R, 500 + R)], fill=255))
    c.ell(360, 500, R, outline=(40, 90, 170), w=8)
    c.ell(300, 430, 60, 34, fill=(255, 255, 255, 60))
def _i_sol(c, t, lt, o):
    for i in range(14):
        a = i * 2 * math.pi / 14 + t * 0.5
        L = 40 + 14 * math.sin(t * 3 + i)
        c.line([(360 + 150 * math.cos(a), 500 + 150 * math.sin(a)), (360 + (150 + L) * math.cos(a), 500 + (150 + L) * math.sin(a))], (255, 190, 50), 14)
    c.ell(360, 500, 130, fill=(255, 218, 70), outline=(255, 170, 40), w=8)
    c.ell(320, 460, 40, 24, fill=(255, 245, 170))
def _crescent():
    A, ra, B, rb = (340.0, 500.0), 170.0, (415.0, 475.0), 142.0
    ao, bi = [], []
    for i in range(0, 361, 2):
        a = math.radians(i)
        x, y = A[0] + ra * math.cos(a), A[1] + ra * math.sin(a)
        if math.hypot(x - B[0], y - B[1]) > rb:
            ao.append((x, y))
        x, y = B[0] + rb * math.cos(a), B[1] + rb * math.sin(a)
        if math.hypot(x - A[0], y - A[1]) < ra:
            bi.append((x, y))
    return ao + bi[::-1]
def _i_luna(c, t, lt, o):
    c.poly(_crescent(), (250, 240, 200), (210, 190, 120), 5)
    for i in range(6):
        x, y = 120 + (i * 97) % 480, 240 + (i * 151) % 440
        s = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
        c.line([(x - 10 * s, y), (x + 10 * s, y)], (255, 255, 255), 4)
        c.line([(x, y - 10 * s), (x, y + 10 * s)], (255, 255, 255), 4)
def _i_estrella(c, t, lt, o):
    k = 1 + 0.08 * math.sin(t * 4)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5 + 0.15 * math.sin(t * 1.3)
        r = (190 if i % 2 == 0 else 80) * k
        pts.append((360 + r * math.cos(a), 500 + r * math.sin(a)))
    c.poly(pts, COL['amarillo'], (230, 160, 30), 8)
    c.ell(330, 460, 20, 12, fill=(255, 250, 200))
def _i_nube(c, t, lt, o):
    dx = 12 * math.sin(t * 1.2)
    for (x, y, r) in ((290, 520, 70), (370, 470, 90), (450, 520, 74), (350, 540, 80)):
        c.ell(x + dx, y, r, fill=(228, 234, 246), outline=(160, 170, 200), w=5)
    for (x, y, r) in ((290, 520, 66), (370, 470, 86), (450, 520, 70), (350, 540, 76)):
        c.ell(x + dx, y, r, fill=(236, 240, 250))
    if o.get('lluvia', True):
        for i in range(12):
            u = (t * 1.6 + i * 0.37) % 1.0
            x = 250 + (i * 37) % 230
            c.line([(x, 610 + 140 * u), (x - 8, 630 + 140 * u)], (90, 150, 230, int(255 * (1 - u))), 6)
def _i_rayo(c, t, lt, o):
    fl = 0.6 + 0.4 * (1 if math.sin(t * 17) > -0.3 else 0)
    c.ell(360, 520, 170, fill=(255, 238, 120, int(70 * fl)))
    c.poly([(400, 330), (270, 540), (350, 540), (310, 700), (460, 470), (376, 470)], (255, 220, 60), (230, 150, 20), 7)
def _i_fuego(c, t, lt, o):
    def fl(sx, sy, s, col, ph):
        h = 1 + 0.12 * math.sin(t * 9 + ph)
        pts = _smooth([(sx - 70 * s, sy), (sx - 80 * s, sy - 100 * s), (sx - 20 * s + 10 * math.sin(t * 7 + ph), sy - 210 * s * h), (sx + 30 * s, sy - 130 * s), (sx + 70 * s, sy - 190 * s * h), (sx + 90 * s, sy - 80 * s), (sx + 70 * s, sy)], 5)
        c.poly(pts, col)
    fl(360, 690, 1.0, (255, 120, 40), 0)
    fl(360, 690, 0.72, (255, 190, 60), 1.3)
    fl(360, 690, 0.4, (255, 240, 150), 2.1)
    c.line([(250, 706), (470, 676)], (110, 70, 40), 20)
    c.line([(250, 676), (470, 706)], (90, 56, 34), 20)
def _i_arbol(c, t, lt, o):
    sw = 6 * math.sin(t * 1.4)
    c.poly([(336, 700), (384, 700), (376, 520), (344, 520)], (130, 90, 60), (90, 60, 36), 4)
    for (x, y, r) in ((300, 470, 84), (420, 470, 84), (360, 400, 98), (360, 500, 90)):
        c.ell(x + sw * (1 - (y - 380) / 200.0), y, r, fill=(78, 176, 96), outline=(44, 120, 68), w=5)
    for (x, y) in ((310, 460), (400, 430), (370, 510)):
        c.ell(x + sw * 0.6, y, 12, fill=COL['rojo'])
    c.ell(360, 706, 120, 14, fill=(90, 160, 90, 150))
def _i_volcan(c, t, lt, o):
    for i in range(10):
        u = (t * 0.9 + i / 10.0) % 1.0
        a = -math.pi / 2 + 0.9 * math.sin(i * 2.7)
        c.ell(360 + 170 * u * math.cos(a), 440 + 330 * u * math.sin(a) + 260 * u * u, 12 * (1 - 0.5 * u), fill=(255, 150 + int(80 * u), 50, int(255 * (1 - u * 0.7))))
    for i in range(4):
        u = (t * 0.3 + i / 4.0) % 1.0
        c.ell(360 + 40 * math.sin(u * 5 + i), 400 - 200 * u, 34 + 50 * u, fill=(150, 150, 168, int(170 * (1 - u))))
    c.poly([(150, 700), (310, 440), (410, 440), (570, 700)], (130, 96, 80), (90, 64, 52), 6)
    c.poly([(310, 440), (410, 440), (390, 480), (360, 450), (330, 485)], (255, 120, 40), (210, 70, 20), 4)
    c.poly([(360, 450), (354, 520), (330, 640), (376, 640), (366, 520)], (255, 150, 50))
def _i_telefono(c, t, lt, o):
    wg = 3 * math.sin(t * 22) if (t % 2.0) < 0.5 else 0
    c.rr(260 + wg, 330, 460 + wg, 700, 36, (50, 52, 72), (30, 30, 50), 6)
    c.rr(274 + wg, 360, 446 + wg, 668, 14, (190, 226, 252))
    for i in range(3):
        y = 392 + i * 76
        c.rr(288 + wg, y, 432 + wg, y + 56, 12, (255, 255, 255))
        c.ell(312 + wg, y + 28, 16, fill=_hsv(0.1 + 0.25 * i, 0.5, 0.95))
        c.rr(340 + wg, y + 14, 420 + wg, y + 26, 5, (200, 206, 224))
    u = _back(prog(lt, 0.4, 0.8))
    c.ell(456, 340, 30 * u, fill=COL['rojo'], outline=(255, 255, 255), w=4)
    if u > 0.6:
        c.text(456, 340, '1', 30 * u, (255, 255, 255))
def _i_compu(c, t, lt, o):
    c.rr(240, 400, 480, 600, 14, (60, 62, 84), (40, 40, 60), 6)
    c.rr(254, 414, 466, 586, 6, (30, 36, 70))
    pts = [(268 + i * 22, 560 - 18 * i + 10 * math.sin(i * 1.5)) for i in range(9)]
    k = int(2 + 7 * _ease(lt / 2.0))
    c.line(pts[:k], (110, 240, 170), 6)
    c.rr(200, 600, 520, 628, 8, (170, 176, 198), (110, 114, 140), 4)
    c.rr(320, 612, 400, 620, 3, (120, 124, 146))
def _i_lupa(c, t, lt, o):
    dx, dy = 20 * math.sin(t * 1.5), 14 * math.cos(t * 1.5)
    c.line([(440 + dx, 610 + dy), (550 + dx, 720 + dy)], (130, 90, 60), 34)
    c.ell(340 + dx, 480 + dy, 140, fill=(200, 232, 255, 110), outline=(150, 156, 180), w=22)
    c.arc(340 + dx, 480 + dy, 100, 200, 270, (255, 255, 255, 220), 12)
def _i_balanza(c, t, lt, o):
    tl = 8 * math.sin(t * 1.2)
    c.rr(346, 380, 374, 700, 6, (150, 156, 176), (100, 104, 128), 4)
    c.rr(270, 690, 450, 716, 8, (130, 134, 156), (100, 104, 128), 4)
    L = _rot(220, 410, tl, 360, 410)
    R = _rot(500, 410, tl, 360, 410)
    c.line([L, R], COL['oro'], 14)
    c.ell(360, 410, 22, fill=COL['oro'], outline=(190, 130, 20), w=4)
    for (x, y) in (L, R):
        c.line([(x, y), (x - 60, y + 130)], (190, 190, 210), 4)
        c.line([(x, y), (x + 60, y + 130)], (190, 190, 210), 4)
        c.poly(_smooth([(x - 74, y + 130), (x + 74, y + 130), (x + 50, y + 170), (x - 50, y + 170)], 4), COL['oro'], (190, 130, 20), 5)
def _i_tesoro(c, t, lt, o):
    op = _ease((lt - 0.2) / 0.7)
    c.rr(220, 520, 500, 700, 18, (150, 96, 60), (90, 55, 30), 6)
    c.line([(220, 580), (500, 580)], COL['oro'], 10)
    for x in (260, 460):
        c.line([(x, 520), (x, 700)], COL['oro'], 10)
    for i in range(14):
        _moneda(c, 270 + (i * 53) % 190, 520 - 14 * (i % 3) - 8, 24, t * 4 + i)
    c.poly(_smooth([(220, 520), (500, 520), (500, 470 - 70 * op), (360, 440 - 90 * op), (220, 470 - 70 * op)], 5), (170, 112, 70), (90, 55, 30), 6)
    if lt > 0.5:
        for i in range(8):
            u = (t * 0.9 + i / 8.0) % 1.0
            c.line([(360 + 140 * math.cos(i * 0.8) * u - 10, 470 - 200 * u), (360 + 140 * math.cos(i * 0.8) * u + 10, 470 - 200 * u)], (255, 255, 255, int(255 * (1 - u))), 5)
def _i_bandera(c, t, lt, o):
    col = _col(o.get('color', 'rojo'), COL['rojo'])
    c.line([(250, 720), (250, 320)], (150, 156, 176), 14)
    c.ell(250, 316, 14, fill=COL['oro'])
    top = [(260 + i * 14, 340 + 14 * math.sin(i * 0.5 - t * 5)) for i in range(0, 21)]
    bot = [(260 + i * 14, 340 + 200 + 14 * math.sin(i * 0.5 - t * 5)) for i in range(0, 21)]
    c.poly(top + bot[::-1], col, _dk(col), 5)
    c.ell(400 + 6 * math.sin(t * 5 - 3), 440 + 14 * math.sin(3 - t * 5), 38, fill=(255, 255, 255, 220))
def _i_pergamino(c, t, lt, o):
    c.rr(240, 360, 480, 680, 10, (244, 226, 184), (170, 130, 80), 5)
    for x in (240, 480):
        c.rr(x - 18, 340, x + 18, 700, 18, (214, 180, 120), (150, 110, 60), 5)
    for i in range(6):
        w = 150 if i % 3 else 110
        c.line([(280, 410 + i * 44), (280 + w * prog(lt, 0.2 + 0.2 * i, 0.5 + 0.2 * i), 410 + i * 44)], (130, 100, 70), 6)
    c.ell(430, 640, 28, fill=COL['rojo'], outline=(140, 40, 50), w=4)
def _i_espada(c, t, lt, o):
    a = -45 + 4 * math.sin(t * 2)
    pts = [_rot(x, y, a, 360, 500) for x, y in ((345, 250), (375, 250), (378, 560), (360, 590), (342, 560))]
    c.poly(pts, (214, 222, 238), (130, 140, 170), 5)
    c.line([_rot(360, 260, a, 360, 500), _rot(360, 560, a, 360, 500)], (240, 244, 252), 6)
    c.line([_rot(300, 580, a, 360, 500), _rot(420, 580, a, 360, 500)], COL['oro'], 22)
    c.line([_rot(360, 590, a, 360, 500), _rot(360, 680, a, 360, 500)], (140, 90, 60), 22)
    q = _rot(360, 700, a, 360, 500)
    c.ell(q[0], q[1], 20, fill=COL['oro'])
    u = (t * 0.8) % 1.5
    if u < 0.8:
        p0 = _rot(360, 260 + 300 * u / 0.8, a, 360, 500)
        c.line([(p0[0] - 12, p0[1]), (p0[0] + 12, p0[1])], (255, 255, 255), 6)
def _i_llave(c, t, lt, o):
    a = 20 * math.sin(t * 2)
    pts = lambda l: [_rot(x, y, a - 30, 360, 500) for x, y in l]
    c.line(pts([(260, 500), (560, 500)]), COL['oro'], 28)
    for x in (480, 530):
        c.line(pts([(x, 500), (x, 560)]), COL['oro'], 24)
    q = _rot(240, 500, a - 30, 360, 500)
    c.ell(q[0], q[1], 76, fill=COL['oro'], outline=(190, 130, 20), w=8)
    c.ell(q[0], q[1], 30, fill=(255, 255, 255, 0), outline=(190, 130, 20), w=8)
ICONOS = {'casa': _i_casa, 'edificio': _i_edificio, 'banco': _i_banco, 'castillo': _i_castillo, 'piramide': _i_piramide, 'barco': _i_barco,
          'avion': _i_avion, 'carro': _i_carro, 'cohete': _i_cohete, 'reloj': _i_reloj, 'calendario': _i_calendario, 'libro': _i_libro,
          'bombilla': _i_bombilla, 'candado': _i_candado, 'escudo': _i_escudo, 'corona': _i_corona, 'tierra': _i_tierra, 'sol': _i_sol,
          'luna': _i_luna, 'estrella': _i_estrella, 'nube': _i_nube, 'rayo': _i_rayo, 'fuego': _i_fuego, 'arbol': _i_arbol, 'volcan': _i_volcan,
          'telefono': _i_telefono, 'compu': _i_compu, 'lupa': _i_lupa, 'balanza': _i_balanza, 'tesoro': _i_tesoro, 'bandera': _i_bandera,
          'pergamino': _i_pergamino, 'espada': _i_espada, 'llave': _i_llave}
def _icono(c, t, p, lt, oa):
    fn = ICONOS.get(str(p.get('nombre', 'estrella')))
    if not fn:
        return
    an = p.get('anim', 'flota')
    if an == 'late':
        c.push(360, 500, 1.25 * (1 + 0.07 * math.sin(t * 6) ** 2))
    elif an == 'flota':
        c.push(360, 500 + 7 * math.sin(t * 1.8), 1.25)
    else:
        c.push(360, 500, 1.25)
    fn(c, t, lt, p)
    c.pop()
def _flecha(c, t, p, lt, oa):
    d = str(p.get('dir', 'arriba'))
    col = _col(p.get('color', 'verde' if d in ('arriba', 'derecha') else 'rojo'))
    ang = {'arriba': -90, 'abajo': 90, 'derecha': 0, 'izquierda': 180}.get(d, -90)
    mv = 18 * abs(math.sin(t * 4))
    pts = [(-120, -42), (30, -42), (30, -92), (150, 0), (30, 92), (30, 42), (-120, 42)]
    out = [_rot(360 + x + mv, 500 + y, ang, 360, 500) for x, y in pts]
    c.poly(out, col, _dk(col), 8)
    c.poly([_rot(360 + x * 0.78 + mv - 6, 500 + y * 0.42 - 20, ang, 360, 500) for x, y in ((-110, -18), (30, -18), (30, 18), (-110, 18))], (255, 255, 255, 70))
    if p.get('texto'):
        c.text(360, 500 + (170 if d == 'arriba' else -170), str(p['texto']), 64, col, 4, (255, 255, 255))
def _tiempo(c, t, p, lt, oa):
    hitos = p.get('hitos') or [['2000', ''], ['2010', ''], ['2020', '']]
    n = len(hitos)
    x0, x1 = 100, 620
    y = 520
    seg = float(p.get('dur', 2.4))
    u = _ease((lt - 0.1) / seg)
    c.line([(x0, y), (x0 + (x1 - x0) * u, y)], (255, 255, 255), 12)
    c.line([(x0, y), (x0 + (x1 - x0) * u, y)], (120, 110, 170), 6)
    for i, h in enumerate(hitos):
        x = x0 + (x1 - x0) * i / max(1, n - 1)
        if u * (n - 1) < i - 0.05:
            continue
        a = _back(prog(u * (n - 1), i - 0.05, i + 0.4))
        c.ell(x, y, 24 * a, fill=COL['oro'], outline=(190, 130, 20), w=5)
        up = i % 2 == 0
        c.line([(x, y), (x, y + (-70 if up else 70) * a)], (255, 255, 255), 5)
        c.text(x, y + (-100 if up else 100) * a, str(h[0]), 44 * a, (255, 255, 255), 4, (90, 70, 160))
        if len(h) > 1 and h[1]:
            c.text(x, y + (-148 if up else 148) * a, str(h[1]), 28 * a, (255, 240, 190), 3, (90, 70, 160))
    mx = x0 + (x1 - x0) * u
    c.ell(mx, y, 14, fill=(255, 255, 255), outline=COL['rojo'], w=5)
def _lista(c, t, p, lt, oa):
    items = p.get('items') or []
    for i, tx in enumerate(items):
        a = _back(prog(lt, 0.15 + 0.45 * i, 0.15 + 0.45 * i + 0.4))
        if a <= 0:
            continue
        y = 360 + i * 110
        x = 80 - 300 * (1 - _out(a))
        c.rr(x, y - 40, x + 560, y + 40, 24, (255, 255, 255, 235), (140, 120, 200), 4)
        c.ell(x + 44, y, 24, fill=COL['verde'])
        c.line([(x + 34, y), (x + 42, y + 9), (x + 56, y - 8)], (255, 255, 255), 6)
        c.text(x + 310, y, str(tx), 34, (60, 50, 100))
def _vs(c, t, p, lt, oa):
    a = _back(prog(lt, 0.0, 0.5))
    for sgn, key, cn in ((-1, 'a', 'azul'), (1, 'b', 'rojo')):
        x = 360 + sgn * 170 * a
        c.rr(x - 140, 440, x + 140, 560, 30, _col(cn), _dk(_col(cn)), 6)
        c.text(x, 500, str(p.get(key, '')), 40, (255, 255, 255), 3, _dk(_col(cn)))
    c.ell(360, 500, 48 * a, fill=COL['oro'], outline=(190, 130, 20), w=6)
    c.text(360, 500, 'VS', 40 * a, (110, 60, 10))
def _part(c, t, p, lt, oa):
    tp = p.get('tipo', 'confeti')
    n = int(p.get('n', 28))
    for i in range(n):
        sp = 0.2 + 0.1 * ((i * 5) % 7)
        u = (t * sp + i * 0.381) % 1.0
        x = 40 + (i * 211) % 640 + 18 * math.sin(t * 2 + i)
        if tp in ('monedas',):
            _moneda(c, x, 160 + 700 * u, 16, t * 7 + i)
        elif tp == 'confeti':
            col = _hsv((i * 0.137) % 1.0, 0.7, 1.0)
            a = t * 6 + i
            c.poly([_rot(x + dx, 160 + 700 * u + dy, a * 40, x, 160 + 700 * u) for dx, dy in ((-9, -5), (9, -5), (9, 5), (-9, 5))], col)
        elif tp in ('estrellas', 'chispas'):
            y = 780 - 600 * u if tp == 'chispas' else 200 + (i * 97) % 580
            s = math.sin(u * math.pi) if tp == 'chispas' else 0.5 + 0.5 * math.sin(t * 3 + i)
            c.line([(x - 12 * s, y), (x + 12 * s, y)], (255, 240, 170), 5)
            c.line([(x, y - 12 * s), (x, y + 12 * s)], (255, 240, 170), 5)
        elif tp == 'burbujas':
            c.ell(x, 800 - 620 * u, 8 + (i % 5) * 4, outline=(255, 255, 255, int(230 * (1 - u))), w=3)
        elif tp == 'lluvia':
            y = 190 + 640 * u
            c.line([(x, y), (x - 6, y + 26)], (150, 200, 255, 220), 4)
        elif tp == 'nieve':
            c.ell(x, 190 + 640 * u, 5 + (i % 3) * 2, fill=(255, 255, 255, 230))
        elif tp == 'humo':
            c.ell(x * 0.3 + 250 + 30 * math.sin(u * 6 + i), 780 - 560 * u, 20 + 60 * u, fill=(180, 180, 196, int(160 * (1 - u))))
        elif tp == 'corazones':
            c.push(x, 800 - 620 * u, 0.5 + 0.5 * (1 - u))
            _heart(c, x, 800 - 620 * u, 16, (255, 100, 140, int(255 * min(1, 2 * (1 - u)))), (200, 40, 80, int(255 * min(1, 2 * (1 - u)))))
            c.pop()
def _escenario(c, t, p, lt, oa):
    tp = p.get('tipo', 'ciudad')
    if tp == 'ciudad':
        c.rr(-100, 700, 820, 820, 0, (90, 96, 140))
        import random
        r = random.Random(7)
        x = -10
        while x < 740:
            w, h = r.randint(70, 120), r.randint(160, 420)
            col = (96 + r.randint(0, 40), 108 + r.randint(0, 30), 160 + r.randint(0, 30))
            c.rr(x, 700 - h, x + w, 702, 4, col, _dk(col, 0.8), 3)
            for yy in range(int(700 - h + 20), 680, 34):
                for xx in range(int(x + 12), int(x + w - 20), 26):
                    on = math.sin(xx * 0.7 + yy * 1.3 + t * 0.6) > -0.1
                    c.rr(xx, yy, xx + 14, yy + 18, 2, (255, 232, 140) if on else _dk(col, 0.85))
            x += w + 6
    elif tp == 'montañas' or tp == 'montanas':
        c.poly([(-40, 780), (180, 450), (330, 780)], (140, 150, 190), (100, 110, 150), 4)
        c.poly([(200, 780), (440, 380), (700, 780)], (120, 132, 176), (90, 100, 140), 4)
        c.poly([(440, 380), (400, 460), (440, 440), (470, 470), (500, 440)], (255, 255, 255))
        c.poly([(480, 780), (620, 560), (780, 780)], (150, 160, 200), (100, 110, 150), 4)
    elif tp == 'mar':
        for k in range(4):
            pts = [(-20 + i * 24, 620 + k * 52 + 12 * math.sin(i * 0.6 + t * 2 + k)) for i in range(0, 32)]
            c.poly(pts + [(740, 820), (-20, 820)], (60 + 25 * k, 130 + 22 * k, 220 - 5 * k))
    elif tp == 'espacio':
        for i in range(36):
            x, y = (i * 173) % 700, 200 + (i * 331) % 640
            s = 0.5 + 0.5 * math.sin(t * 2 + i)
            c.ell(x + 10, y, 2 + 2 * s, fill=(255, 255, 255, 220))
        c.ell(580, 330, 46, fill=(240, 160, 90))
        c.ell(100, 700, 70, fill=(120, 150, 230))
    elif tp == 'campo':
        c.poly(_smooth([(-60, 700), (200, 630), (460, 680), (800, 620), (800, 820), (-60, 820)], 6), (110, 190, 110), (70, 150, 80), 4)
        for i in range(10):
            x = 40 + i * 70
            c.line([(x, 740 + (i % 3) * 20), (x + 6 * math.sin(t * 2 + i), 700 + (i % 3) * 20)], (70, 150, 80), 4)
    elif tp == 'desierto':
        c.poly(_smooth([(-60, 720), (200, 640), (480, 700), (800, 650), (800, 820), (-60, 820)], 6), (240, 206, 140), (200, 160, 90), 4)
        c.ell(560, 380, 56, fill=(255, 220, 110))
def _formas(c, t, p, lt, oa):
    for i, f in enumerate(p.get('lista') or []):
        tp = f.get('f', 'circ')
        t0 = float(f.get('en') or 0.0) if not isinstance(f.get('en'), str) else 0.0
        u = prog(lt, t0, t0 + 0.4)
        if u <= 0:
            continue
        x, y = float(f.get('x', 360)), float(f.get('y', 500))
        if f.get('mov'):
            mu = _ease((lt - t0) / float(f.get('dur', 1.2)))
            x += (float(f['mov'][0]) - x) * mu
            y += (float(f['mov'][1]) - y) * mu
        s = float(f.get('esc', 1.0))
        if f.get('pulsa'):
            s *= 1 + 0.12 * math.sin(t * 6 + i)
        s *= 0.5 + 0.5 * _back(u)
        col = _col(f.get('c', 'azul'))
        r = float(f.get('r', 40)) * s
        gi = float(f.get('gira', 0)) * (lt - t0)
        if tp == 'circ':
            c.ell(x, y, r, fill=col, outline=_dk(col), w=4)
        elif tp == 'rect':
            w_, h_ = float(f.get('w', 100)) * s, float(f.get('h', 60)) * s
            c.poly([_rot(x + dx, y + dy, gi, x, y) for dx, dy in ((-w_ / 2, -h_ / 2), (w_ / 2, -h_ / 2), (w_ / 2, h_ / 2), (-w_ / 2, h_ / 2))], col, _dk(col), 4)
        elif tp == 'tri':
            c.poly([_rot(x + dx * s, y + dy * s, gi, x, y) for dx, dy in ((0, -r / s), (r / s, r / s), (-r / s, r / s))], col, _dk(col), 4)
        elif tp == 'linea':
            c.line([(x, y), (float(f.get('x2', x + 100)), float(f.get('y2', y)))], col, float(f.get('w', 8)))
        elif tp == 'texto':
            c.text(x, y, str(f.get('t', '')), float(f.get('tam', 60)) * s, col if f.get('c') else (255, 255, 255), 4, (60, 40, 120))
def _azul():
    return _E.ESTILO.get('pal') == 'azul'
def _holo(c, t, p, lt, oa):
    pose = p.get('pose', 'parado')
    run = pose == 'corre'
    by = -(10 * abs(math.sin(t * 9)) if run else 4 * math.sin(t * 2.4))
    sw = math.sin(t * (9 if run else 2.2))
    WH = (255, 255, 255)
    fl = (255, 255, 255, 24)
    ang = {'parado': (92, 88), 'feliz': (-125, -55), 'celebra': (-125, -55), 'señala': (92, -15), 'senala': (92, -15),
           'sorpresa': (160, 20), 'piensa': (92, -40), 'triste': (96, 84), 'corre': (90 + 55 * sw, 90 - 55 * sw)}.get(pose, (92, 88))
    wob = 10 * math.sin(t * 7) if pose in ('feliz', 'celebra') else 0
    for (sx, a) in ((278, ang[0] + wob), (442, ang[1] - wob)):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        cx, cy = sx + ca * 78, 432 + by + sa * 78
        pts = _caps(cx, cy, 168, 36, math.radians(a))
        c.poly(pts, fl, WH, 5)
    c.rr(282, 392 + by, 438, 660 + by, 62, fl, WH, 5)
    c.ell(360, 318 + by + (8 if pose == 'triste' else 0), 54, fill=fl, outline=WH, w=5)
    for yy in range(300, 650, 15):
        yy2 = yy + by
        if yy < 372:
            hw = math.sqrt(max(0, 54 * 54 - (yy - 318) ** 2))
            if hw > 6:
                c.line([(360 - hw + 8, yy2), (360 + hw - 8, yy2)], (255, 255, 255, 30), 2)
        elif yy > 410:
            c.line([(292, yy2), (428, yy2)], (255, 255, 255, 30), 2)
    if pose in ('feliz', 'celebra'):
        c.arc(360, 336 + by, 22, 15, 165, (255, 255, 255, 170), 4)
    elif pose == 'triste':
        c.arc(360, 360 + by, 18, 200, 340, (255, 255, 255, 170), 4)
def _persona_sel(c, t, p, lt, oa):
    if _azul():
        _holo(c, t, p, lt, oa)
    else:
        _persona(c, t, p, lt, oa)
def _marca(c, t, p, lt, oa):
    tx = str(p.get('texto', '!'))
    col = _col(p.get('color', 'naranja'), (252, 132, 70))
    k = 1 + 0.1 * math.sin(t * 6)
    c.push(360, 500, k)
    if tx == '!':
        c.poly(_smooth([(338, 400), (382, 400), (372, 540), (348, 540)], 5), col)
        c.ell(360, 590, 24, fill=col)
    elif tx == '✓':
        c.line([(300, 510), (350, 570), (430, 430)], col, 36)
    else:
        c.text(360, 500, tx, 230, col, 0)
    c.pop()
def fondo_azul(kind):
    import random
    import numpy as np
    from PIL import Image as _I
    import motion4 as m4
    p = kind.split(':')
    rnd = random.Random(int(p[2]) if len(p) > 2 else 1)
    W, H = getattr(m4, 'W', 720), getattr(m4, 'H', 1280)
    gy, gx = np.mgrid[0:H, 0:W]
    cx, cy = W * 0.5, H * 0.5
    r = np.sqrt(((gx - cx) / (W * 0.9)) ** 2 + ((gy - cy) / (H * 0.62)) ** 2)
    k = (np.clip(r, 0, 1) ** 1.1)[:, :, None]
    c1 = np.array((12, 62, 112), np.float32)
    c2 = np.array((2, 11, 30), np.float32)
    a = c1[None, None, :] * (1 - k) + c2[None, None, :] * k
    im = _I.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')
    ov = _I.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y0 = int(H * 0.768)
    for gl in range(26, 0, -1):
        d.rectangle([0, y0 - gl * 2, W, y0 - gl * 2 + 2], fill=(40, 150, 230, int(2 + (26 - gl) * 0.9)))
    d.line([0, y0, W, y0], fill=(80, 200, 255, 110), width=2)
    n = 14
    for i in range(-n, n + 1):
        d.line([(W / 2 + i * 36, y0), (W / 2 + i * 150, H)], fill=(80, 195, 255, 100), width=2)
    for j in range(1, 14):
        y = y0 + (H - y0) * (j / 13.0) ** 1.8
        d.line([(0, y), (W, y)], fill=(80, 195, 255, 90), width=2)
    for _ in range(70):
        x, y = rnd.randint(0, W), rnd.randint(0, int(H * 0.8))
        rr_ = rnd.choice((1, 1, 2))
        d.ellipse([x - rr_, y - rr_, x + rr_, y + rr_], fill=(150, 220, 255, rnd.randint(40, 130)))
    im.alpha_composite(ov)
    return im.convert('RGB')
def _tint_azul(lay, k, glow):
    from PIL import ImageFilter, ImageOps
    bb = lay.getchannel('A').getbbox()
    if not bb:
        return None
    pad = int(30 * S)
    x0, y0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
    x1, y1 = min(lay.size[0], bb[2] + pad), min(lay.size[1], bb[3] + pad)
    cr = lay.crop((x0, y0, x1, y1))
    A = cr.getchannel('A')
    g = cr.convert('L').point(lambda v: int(60 + 0.76 * v))
    col = ImageOps.colorize(g, black=(8, 52, 112), white=(214, 250, 255), mid=(52, 190, 244), blackpoint=60, whitepoint=255, midpoint=170)
    col = col.convert('RGBA')
    col.putalpha(A)
    if glow:
        sm = A.resize((max(2, A.size[0] // 4), max(2, A.size[1] // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize(A.size, Image.BILINEAR)
        gl = Image.new('RGBA', col.size, (30, 170, 255, 0))
        gl.putalpha(sm.point(lambda v: int(v * 0.9)))
        gl.alpha_composite(col)
        col = gl
    return col, x0, y0
def _instalar_azul():
    if getattr(_E, '_azul_ok', False):
        return
    _E._azul_ok = True
    _E.fondo_azul = fondo_azul
    t_old = _E._tint
    _E._tint = lambda lay, k, glow: _tint_azul(lay, k, glow) if _azul() else t_old(lay, k, glow)
    f_old = _E.fijar
    def fijar2(sc):
        f_old(sc)
        k = str(sc.get('fondo') or '')
        if k.startswith('mor:azul'):
            _E.ESTILO['modo'] = 'negro'
            _E.ESTILO['pal'] = 'azul'
            try:
                _E._3._m.COLORES['oro'] = (96, 214, 250)
            except Exception:
                pass
        else:
            _E.ESTILO['pal'] = 'mor'
    _E.fijar = fijar2
    try:
        prev3 = _E.draw_subs3
        import re as _re
        _3, _4 = _E._3, _E._4
        def subs_azul(d, t, words, frases):
            if not _azul():
                return prev3(d, t, words, frases)
            Sx, CW, Hh = _3.S, _3.CW, _3.H
            idx = None
            for i, (w, a, b) in enumerate(words):
                if a <= t:
                    idx = i
                else:
                    break
            if idx is None or t > words[idx][2] + 0.45:
                return
            g0, n = 0, 1
            for (gs, gn) in frases:
                if gs <= idx < gs + gn:
                    g0, n = gs, gn
                    break
            toks = [_re.sub('["]', '', w[0]).upper() for w in words[g0:g0 + n]]
            fs = 60
            sp = 14 * Sx
            while True:
                fb = _4.pfont(fs, True)
                ws = [d.textlength(x, font=fb) for x in toks]
                if sum(ws) + sp * (len(ws) - 1) <= CW * 0.86 * 1.75 or fs < 40:
                    break
                fs -= 2
            lines, cur, cw = [], [], 0.0
            tot = sum(ws) + sp * (len(ws) - 1)
            for j, x in enumerate(toks):
                if cur and (cw + sp + ws[j] > tot * 0.58 + 40 * Sx) and len(lines) == 0:
                    lines.append(cur)
                    cur, cw = [], 0.0
                cur.append(j)
                cw += (sp if len(cur) > 1 else 0) + ws[j]
            lines.append(cur)
            lh = fs * 1.3
            y = 0.178 * Hh
            for ln in lines:
                lw = sum(ws[j] for j in ln) + sp * (len(ln) - 1)
                x = (CW - lw) / 2
                for j in ln:
                    gi = g0 + j
                    if gi == idx:
                        col, halo = (84, 226, 255, 255), ((10, 60), (6, 110), (3, 190))
                    elif gi < idx:
                        col, halo = (255, 255, 255, 255), ((6, 40), (3, 90))
                    else:
                        col, halo = (120, 170, 215, 120), ()
                    for rr_, al in halo:
                        d.text((x, y * Sx), toks[j], font=fb, fill=(0, 0, 0, 0), anchor='lm', stroke_width=int(rr_ * Sx / 2), stroke_fill=(30, 150, 255, al))
                    d.text((x, y * Sx), toks[j], font=fb, fill=col, anchor='lm')
                    x += ws[j] + sp
                y += lh
        _E.draw_subs3 = subs_azul
        if getattr(_4, 'draw_subs2', None) is prev3:
            _4.draw_subs2 = subs_azul
    except Exception:
        pass
def _esc(fn, k):
    def g(c, t, p, lt, oa):
        c.push(360, 500, k)
        fn(c, t, p, lt, oa)
        c.pop()
    return g
def _guion_acentos(d, t, sc):
    import motion8 as _m8
    _instalar_azul()
    p = sc['p']
    if not str(sc.get('fondo') or '').startswith('mor:azul'):
        return _n8(d, t, sc)
    pz = p.get('piezas', [])
    ac = [q for q in pz if q.get('k') == 'marca' or q.get('acento')]
    cam = []
    for kf in p.get('camara') or []:
        k2 = dict(kf)
        if k2.get('foco') is not None and not isinstance(k2['foco'], (list, tuple)):
            k2['foco'] = list(_m8._ancla(sc, p, k2['foco']))
        cam.append(k2)
    sc1 = dict(sc)
    p1 = dict(p)
    p1['piezas'] = [q for q in pz if q not in ac]
    p1['camara'] = cam
    sc1['p'] = p1
    _n8(d, t, sc1)
    if ac:
        sc2 = dict(sc)
        p2 = dict(p)
        p2['piezas'] = ac
        p2['camara'] = cam
        sc2['p'] = p2
        sc2['fondo'] = 'mor:suave:1'
        _n8(d, t, sc2)
        _E.fijar(sc)
from motion8 import n_guion as _n8, e_guion as _e8
PIEZAS.update({'persona': _esc(_persona_sel, 1.2), 'dinero': _esc(_dinero, 1.2), 'grafica': _grafica, 'icono': _icono, 'flecha': _flecha,
               'tiempo': _tiempo, 'lista': _lista, 'vs': _vs, 'part': _part, 'escenario': _escenario, 'formas': _formas, 'marca': _marca})
PLANTILLAS = __import__('motion6').PLANTILLAS
PLANTILLAS['guion'] = (_guion_acentos, _e8)
_instalar_azul()
