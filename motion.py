import math
import os
import random
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
S = int(os.environ.get('MOTION_S', '2'))
CW, CH = W * S, H * S
FPS = 30

FONT_CANDIDATES = [
    'Poppins-Bold.ttf', os.path.expanduser('~/.fonts/Poppins-Bold.ttf'), '/tmp/Poppins-Bold.ttf',
    '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
]
_FONT_PATH = None
for _p in FONT_CANDIDATES:
    try:
        if os.path.exists(_p) and os.path.getsize(_p) > 20000:
            _FONT_PATH = _p
            break
    except OSError:
        pass
_fc = {}

def font(sz):
    k = max(6, int(round(sz * S / 2.0)) * 2)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(_FONT_PATH, k) if _FONT_PATH else ImageFont.load_default()
    return _fc[k]

BG1, BG2 = (10, 20, 46), (8, 84, 96)
GOLD, GOLD_D, GOLD_L = (255, 196, 36), (214, 140, 10), (255, 232, 140)
GREEN, GREEN_D = (46, 204, 113), (28, 150, 82)
RED, RED_D = (255, 84, 84), (190, 50, 50)
BLUE = (80, 160, 255)
WHITE = (255, 255, 255)
INK = (12, 20, 38)
CARD = (18, 40, 76)
CARD_L = (30, 60, 104)
MUTED = (170, 190, 222)
COLORES = {'oro': GOLD, 'verde': GREEN, 'rojo': RED, 'azul': BLUE, 'blanco': WHITE}

def col(name, default=GOLD):
    return COLORES.get(str(name), default) if not isinstance(name, tuple) else name

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / (t1 - t0))

def e_out(x):
    return 1 - (1 - x) ** 3

def e_in_out(x):
    return 3 * x * x - 2 * x ** 3

def e_back(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def e_bounce(x):
    n1, d1 = 7.5625, 2.75
    if x < 1 / d1:
        return n1 * x * x
    if x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + .75
    if x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + .9375
    x -= 2.625 / d1
    return n1 * x * x + .984375

def lerp(a, b, k):
    return a + (b - a) * k

def mix(c1, c2, k):
    return tuple(int(lerp(c1[i], c2[i], k)) for i in range(3))

def P(x, y):
    return (x * S, y * S)

def fmt(v, dec=0, pref='', suf=''):
    s = ('{:,.%df}' % dec).format(v)
    s = s.replace(',', '#').replace('.', ',').replace('#', '.')
    return pref + s + suf

def norm(w):
    return re.sub('[^0-9a-zA-Záéíóúñü_]', '', str(w).lower())

_yy = np.linspace(0, 1, CH)[:, None, None]
_bg = (np.array(BG1) * (1 - _yy) + np.array(BG2) * _yy)
_bg = np.repeat(_bg, CW, axis=1)
_gy, _gx = np.mgrid[0:CH, 0:CW]
_r = np.sqrt(((_gx - CW / 2) / (CW * 0.75)) ** 2 + ((_gy - CH * 0.42) / (CH * 0.5)) ** 2)
_glow = np.clip(1 - _r, 0, 1)[:, :, None] ** 2 * 26
BG = Image.fromarray(np.clip(_bg + _glow * np.array([0.3, 0.9, 1.0]), 0, 255).astype(np.uint8))
del _yy, _bg, _gy, _gx, _r, _glow

random.seed(7)
PART = [(random.random(), random.random(), random.uniform(0.15, 0.5), random.uniform(2, 7)) for _ in range(30)]

def circle(d, cx, cy, r, fill=None, outline=None, width=2):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill, outline=outline,
              width=int(width * S))

def rrect(d, x0, y0, x1, y1, r, fill=None, outline=None, width=3):
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=fill, outline=outline,
                        width=int(width * S))

def card(d, x0, y0, x1, y1, r=34, fill=CARD, outline=None):
    rrect(d, x0 + 5, y0 + 9, x1 + 5, y1 + 9, r, fill=(6, 14, 30))
    rrect(d, x0, y0, x1, y1, r, fill=fill, outline=outline, width=4)

def txt(d, x, y, s, sz, fill=WHITE, anchor='mm', stroke=0, sfill=INK):
    d.text((x * S, y * S), str(s), font=font(sz), fill=fill, anchor=anchor,
           stroke_width=int(stroke * S), stroke_fill=sfill)

def fit(d, s, sz, maxw):
    while sz > 18 and d.textlength(str(s), font=font(sz)) > maxw * S:
        sz -= 4
    return sz

def wrap_rich(d, s, sz, maxw):
    toks, hl = [], False
    for part in re.split('([*])', s):
        if part == '*':
            hl = not hl
            continue
        for w in part.split():
            toks.append((w, hl))
    f = font(sz)
    sp = d.textlength(' ', font=f)
    lines, cur, cw = [], [], 0.0
    for w, h in toks:
        wl = d.textlength(w, font=f)
        if cur and cw + sp + wl > maxw * S:
            lines.append(cur)
            cur, cw = [], 0.0
        cur.append((w, h, wl))
        cw += (sp if len(cur) > 1 else 0) + wl
    if cur:
        lines.append(cur)
    return lines

def rich(d, cx, cy, s, sz, maxw, hl=GOLD, fill=WHITE, stroke=5):
    lines = wrap_rich(d, s, sz, maxw)
    f = font(sz)
    sp = d.textlength(' ', font=f)
    lh = sz * 1.22
    y = cy - lh * (len(lines) - 1) / 2
    for ln in lines:
        tw = sum(w[2] for w in ln) + sp * (len(ln) - 1)
        x = cx * S - tw / 2
        for w, h, wl in ln:
            d.text((x, y * S), w, font=f, fill=(hl if h else fill), anchor='lm',
                   stroke_width=int(stroke * S), stroke_fill=INK)
            x += wl + sp
        y += lh
    return lh * len(lines)

def coin(d, cx, cy, r, squash=1.0, sym='$'):
    rx, ry = max(r * squash, 1), max(r, 1)
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=GOLD_D)
    k = 0.86
    d.ellipse([(cx - rx * k) * S, (cy - ry * k) * S, (cx + rx * k) * S, (cy + ry * k) * S], fill=GOLD)
    k2 = 0.64
    d.ellipse([(cx - rx * k2) * S, (cy - ry * k2) * S, (cx + rx * k2) * S, (cy + ry * k2) * S],
              outline=GOLD_L, width=int(max(2, r * 0.06) * S))
    if squash > 0.4 and r > 14:
        d.text((cx * S, (cy + r * 0.04) * S), sym, font=font(r * 1.05 * max(squash, 0.5)), fill=GOLD_D, anchor='mm')
    d.ellipse([(cx - rx * 0.62) * S, (cy - ry * 0.7) * S, (cx - rx * 0.30) * S, (cy - ry * 0.38) * S], fill=GOLD_L)

def sparkle(d, cx, cy, r, a):
    if a <= 0:
        return
    r = r * a
    pts = []
    for i in range(8):
        ang = i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append(((cx + math.cos(ang) * rr) * S, (cy + math.sin(ang) * rr) * S))
    d.polygon(pts, fill=WHITE)

def arrow(d, cx, cy, size, up=True, fill=GREEN):
    s = size
    dy = -1 if up else 1
    pts = [(cx, cy + dy * s), (cx + s * 0.9, cy - dy * s * 0.1), (cx + s * 0.38, cy - dy * s * 0.1),
           (cx + s * 0.38, cy - dy * s), (cx - s * 0.38, cy - dy * s), (cx - s * 0.38, cy - dy * s * 0.1),
           (cx - s * 0.9, cy - dy * s * 0.1)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

def icono(d, kind, cx, cy, size, t, t0):
    a = prog(t, t0, t0 + 0.4)
    if a <= 0:
        return
    sz = size * e_back(a)
    bob = math.sin(t * 3) * 6
    if kind == 'pregunta':
        txt(d, cx, cy + bob, '?', sz * 1.6, GOLD, stroke=0)
    elif kind == 'alerta':
        pts = [(cx, cy - sz * 0.8 + bob), (cx + sz * 0.8, cy + sz * 0.6 + bob), (cx - sz * 0.8, cy + sz * 0.6 + bob)]
        d.polygon([(x * S, y * S) for x, y in pts], fill=RED)
        txt(d, cx, cy + sz * 0.15 + bob, '!', sz * 1.0, WHITE)
    elif kind == 'moneda':
        coin(d, cx, cy + bob, sz * 0.8, squash=abs(math.cos(t * 1.4)) * 0.2 + 0.8)
    elif kind == 'arriba':
        arrow(d, cx, cy + bob, sz * 0.8, True, GREEN)
    elif kind == 'abajo':
        arrow(d, cx, cy - bob, sz * 0.8, False, RED)
    elif kind == 'burbuja':
        circle(d, cx, cy + bob, sz * 0.8, fill=None, outline=BLUE, width=8)
        circle(d, cx - sz * 0.3, cy - sz * 0.3 + bob, sz * 0.14, fill=WHITE)

def cue(sc, spec, default):
    if spec is None:
        return default
    if isinstance(spec, (int, float)):
        return float(spec) * sc['dur']
    key = norm(spec)
    for (w, a, b) in sc['words']:
        if norm(w) == key:
            return a
    return default

def evenly(sc, i, n, start=0.12, end=0.82):
    if n <= 1:
        return start * sc['dur']
    return (start + (end - start) * i / (n - 1)) * sc['dur']

def draw_titulo(d, p, t, y=235, t0=0.0):
    y = max(y, 215)
    s = p.get('titulo')
    if not s:
        return
    a = prog(t, t0, t0 + 0.35)
    if a <= 0:
        return
    rich(d, 360, y + (1 - e_out(a)) * -30, s, 50, 640, hl=GOLD)

def n_num(d, t, sc):
    p = sc['p']
    draw_titulo(d, p, t)
    t0 = cue(sc, p.get('cue'), 0.15)
    t1 = t0 + clamp(sc['dur'] - t0 - 0.4, 0.6, 1.6)
    v0, v1 = float(p.get('desde', 0)), float(p['valor'])
    v = lerp(v0, v1, e_out(prog(t, t0, t1)))
    s = fmt(v, int(p.get('decimales', 0)), p.get('prefijo', ''), p.get('sufijo', ''))
    c = col(p.get('color', 'oro'))
    a = prog(t, t0 - 0.05, t0 + 0.4)
    fin = prog(t, t1, t1 + 0.35)
    size = 200 * (0.7 + 0.3 * e_back(a)) * (1 + 0.08 * math.sin(fin * math.pi))
    size = fit(d, s, size, 650)
    shake = (math.sin(t * 90) * 5 * (1 - fin)) if 0 < fin < 1 else 0
    txt(d, 360 + shake, 560, s, size, c, stroke=8)
    if p.get('etiqueta'):
        a2 = prog(t, t1 - 0.2, t1 + 0.25)
        if a2 > 0:
            rich(d, 360, 720 + (1 - e_out(a2)) * 30, p['etiqueta'], 46, 620, hl=GOLD)
    if 0 < fin < 1:
        r = 150 + 330 * fin
        circle(d, 360, 560, r, outline=mix(c, BG2, fin), width=7 * (1 - fin) + 1)
    if p.get('monedas', True):
        for k, (cx, cy, r) in enumerate([(90, 400, 44), (640, 430, 38), (110, 800, 36), (630, 790, 46)]):
            aa = prog(t, t1 + 0.05 * k, t1 + 0.05 * k + 0.45)
            if aa > 0:
                coin(d, cx, cy - math.sin(t * 2 + k) * 8, r * e_back(aa), squash=abs(math.cos(t * 1.3 + k)) * 0.25 + 0.75)
                sparkle(d, cx + r, cy - r, 24, math.sin(aa * math.pi))

def e_num(sc):
    p = sc['p']
    t0 = cue(sc, p.get('cue'), 0.15)
    t1 = t0 + clamp(sc['dur'] - t0 - 0.4, 0.6, 1.6)
    ev = [(t0 + 0.12 * k, 'tick') for k in range(int((t1 - t0) / 0.12))]
    ev.append((t1, 'ching'))
    return ev

def n_texto(d, t, sc):
    p = sc['p']
    lineas = p.get('lineas') or [sc['texto']]
    n = len(lineas)
    cues = p.get('cues') or []
    icon = p.get('icono')
    top = 330 if icon else 420
    if icon:
        icono(d, icon, 360, 270, 105, t, 0.05)
    total_h = 0
    heights = []
    for ln in lineas:
        sz = int(p.get('tam', 74))
        heights.append(len(wrap_rich(d, ln, sz, 640)) * sz * 1.22)
    total_h = sum(heights) + 24 * (n - 1)
    y = top + (500 - total_h) / 2 if not icon else top
    for i, ln in enumerate(lineas):
        t0 = cue(sc, cues[i] if i < len(cues) else None, evenly(sc, i, n, 0.08, 0.7))
        a = prog(t, t0, t0 + 0.28)
        sz = int(p.get('tam', 74))
        h = heights[i]
        if a > 0:
            k = 0.55 + 0.45 * e_back(a)
            rich(d, 360, y + h / 2 + (1 - e_out(a)) * -50, ln, sz * k, 640, hl=col(p.get('color', 'oro')))
        y += h + 24

def e_texto(sc):
    p = sc['p']
    n = len(p.get('lineas') or [1])
    cues = p.get('cues') or []
    return [(cue(sc, cues[i] if i < len(cues) else None, evenly(sc, i, n, 0.08, 0.7)), 'thud') for i in range(n)]

def n_lista(d, t, sc):
    p = sc['p']
    draw_titulo(d, p, t, y=210)
    items = p['items']
    n = len(items)
    ch = 150 if n >= 3 else 190
    gap = 22
    y0 = 300
    for i, it in enumerate(items):
        t0 = cue(sc, it.get('cue'), evenly(sc, i, n, 0.12, 0.75))
        t0 = min(t0, 0.15 + i * 0.35 * sc['dur'] / max(n, 1) + 0.3) if i == 0 else t0
        a = prog(t, t0, t0 + 0.4)
        if a <= 0:
            continue
        x = lerp(760, 0, e_back(a)) if a < 1 else 0
        y = y0 + i * (ch + gap)
        card(d, 50 + x, y, 670 + x, y + ch, fill=CARD, outline=CARD_L)
        fl = prog(t, t0 + 0.25, t0 + 0.55)
        sx = abs(math.cos(fl * math.pi)) if fl < 1 else 1.0
        bw = 50 * max(sx, 0.08)
        d.ellipse([(120 + x - bw) * S, (y + ch / 2 - 50) * S, (120 + x + bw) * S, (y + ch / 2 + 50) * S], fill=GOLD)
        if sx > 0.5:
            nn = str(it.get('n', i + 1))
            txt(d, 120 + x, y + ch / 2, nn, (56 if len(nn) < 2 else 38) * sx, INK)
        txt(d, 190 + x, y + ch / 2 - (22 if it.get('detalle') else 0), it['titulo'], fit(d, it['titulo'], 42, 440),
            WHITE, anchor='lm')
        if it.get('detalle'):
            txt(d, 190 + x, y + ch / 2 + 32, it['detalle'], fit(d, it['detalle'], 32, 440), MUTED, anchor='lm')

def e_lista(sc):
    items = sc['p']['items']
    n = len(items)
    return [(cue(sc, it.get('cue'), evenly(sc, i, n, 0.12, 0.75)), 'pop') for i, it in enumerate(items)]

def n_barras(d, t, sc):
    p = sc['p']
    pa = e_out(prog(t, 0.0, 0.4))
    oy = (1 - pa) * 120
    card(d, 40, 190 + oy, 680, 850 + oy, 40)
    if pa < 0.4:
        return
    txt(d, 360, 262, p.get('titulo', ''), fit(d, p.get('titulo', ''), 44, 580), WHITE)
    barras = p['barras']
    n = len(barras)
    mx = float(p.get('max') or max(b['valor'] for b in barras))
    y0, y1 = 770, 380
    for g in range(4):
        gy = y0 - (y0 - y1) * g / 3
        d.line([P(70, gy), P(650, gy)], fill=(40, 66, 104), width=int(3 * S))
    d.line([P(70, y0), P(650, y0)], fill=(150, 170, 200), width=int(5 * S))
    bw = min(150, 480 / n - 24)
    span = 580 / n
    for i, b in enumerate(barras):
        t0 = cue(sc, b.get('cue'), evenly(sc, i, n, 0.12, 0.68))
        a = e_out(prog(t, t0, t0 + 1.0))
        x = 70 + span * i + (span - bw) / 2
        h = (y0 - y1) * (float(b['valor']) / mx) * a
        c = col(b.get('color', 'verde' if i < n - 1 else 'oro'))
        if a > 0.01:
            rrect(d, x, y0 - h, x + bw, y0 + 10, 14, fill=c)
            d.rectangle([x * S, y0 * S, (x + bw) * S, (y0 + 10) * S], fill=CARD)
            val = float(b['valor']) * a
            txt(d, x + bw / 2, y0 - h - 36, fmt(val, int(p.get('decimales', 0)), p.get('prefijo', ''), p.get('sufijo', '')),
                fit(d, '000.000', 44, bw + 40), WHITE, stroke=5)
        txt(d, x + bw / 2, y0 + 48, b['etiqueta'], fit(d, b['etiqueta'], 32, span - 8), MUTED)
    if p.get('insignia'):
        tl = cue(sc, p.get('cue_insignia'), 0.75 * sc['dur'])
        a = prog(t, tl, tl + 0.5)
        if a > 0:
            r = 74 * e_back(a)
            circle(d, 150, 450, r, fill=GOLD)
            txt(d, 150, 450, p['insignia'], 46 * e_back(a), INK)

def e_barras(sc):
    p = sc['p']
    n = len(p['barras'])
    ev = [(cue(sc, b.get('cue'), evenly(sc, i, n, 0.12, 0.68)), 'whoosh') for i, b in enumerate(p['barras'])]
    ev.append((cue(sc, p['barras'][-1].get('cue'), evenly(sc, n - 1, n, 0.12, 0.68)) + 0.9, 'ching'))
    return ev

def n_linea(d, t, sc):
    p = sc['p']
    pa = e_out(prog(t, 0.0, 0.35))
    oy = (1 - pa) * 120
    card(d, 40, 190 + oy, 680, 850 + oy, 40)
    if pa < 0.4:
        return
    txt(d, 360, 262, p.get('titulo', ''), fit(d, p.get('titulo', ''), 44, 580), WHITE)
    pts = [float(x) for x in p['puntos']]
    n = len(pts)
    lo, hi = min(pts), max(pts)
    x0, x1, y0, y1 = 90, 640, 780, 390
    for g in range(4):
        gy = y0 - (y0 - y1) * g / 3
        d.line([P(x0 - 20, gy), P(x1 + 10, gy)], fill=(40, 66, 104), width=int(3 * S))
    t0 = cue(sc, p.get('cue'), 0.2)
    t1 = t0 + clamp(sc['dur'] - t0 - 0.3, 0.8, 2.6)
    k = e_in_out(prog(t, t0, t1)) * (n - 1)
    xy = [(x0 + (x1 - x0) * i / (n - 1), y0 - (y0 - y1) * (v - lo) / max(hi - lo, 1e-9)) for i, v in enumerate(pts)]
    pico = pts.index(hi)
    base = col(p.get('color', 'verde'))
    for i in range(n - 1):
        if k <= i:
            break
        f = min(1.0, k - i)
        ax, ay = xy[i]
        bx, by = xy[i + 1]
        ex, ey = lerp(ax, bx, f), lerp(ay, by, f)
        c = RED if (p.get('caida') and i >= pico) else base
        d.line([P(ax, ay), P(ex, ey)], fill=mix(c, BG1, 0.55), width=int(22 * S))
        d.line([P(ax, ay), P(ex, ey)], fill=c, width=int(11 * S))
        circle(d, ax, ay, 5.5, fill=c)
    i = min(int(k), n - 2)
    f = clamp(k - i)
    hx, hy = lerp(xy[i][0], xy[i + 1][0], f), lerp(xy[i][1], xy[i + 1][1], f)
    pulse = 1 + 0.18 * math.sin(t * 9)
    circle(d, hx, hy, 17 * pulse, fill=WHITE)
    circle(d, hx, hy, 10, fill=(RED if (p.get('caida') and k > pico) else base))
    if p.get('valores'):
        vals = [float(v) for v in p['valores']]
        vv = lerp(vals[i], vals[i + 1], f)
        lab = fmt(vv, int(p.get('decimales', 0)), p.get('prefijo', ''), p.get('sufijo', ''))
        lx = clamp(hx, 150, 570)
        txt(d, lx, hy - 52, lab, 42, WHITE, stroke=5)
    if p.get('etiquetas'):
        txt(d, x0, y0 + 40, p['etiquetas'][0], 30, MUTED)
        txt(d, x1, y0 + 40, p['etiquetas'][-1], 30, MUTED)
    if p.get('caida') and k > pico + 0.3:
        a = prog(t, t0 + (t1 - t0) * 0.75, t0 + (t1 - t0) * 0.75 + 0.4)
        if a > 0:
            arrow(d, 560, 470, 46 * e_back(a), up=False, fill=RED)

def e_linea(sc):
    p = sc['p']
    t0 = cue(sc, p.get('cue'), 0.2)
    t1 = t0 + clamp(sc['dur'] - t0 - 0.3, 0.8, 2.6)
    ev = [(t0, 'rise')]
    if p.get('caida'):
        ev.append((t0 + (t1 - t0) * 0.78, 'thud'))
    else:
        ev.append((t1, 'ching'))
    return ev

def n_versus(d, t, sc):
    p = sc['p']
    draw_titulo(d, p, t, y=200)
    izq, der = p['izq'], p['der']
    for j, (it, side) in enumerate(((izq, -1), (der, 1))):
        t0 = cue(sc, it.get('cue'), 0.1 + 0.25 * j)
        a = prog(t, t0, t0 + 0.45)
        if a <= 0:
            continue
        x = (1 - e_back(a)) * 420 * side
        cx = 360 + side * 152 + x
        c = col(it.get('color', 'verde' if side < 0 else 'rojo'))
        glow = 0.5 + 0.5 * math.sin(t * 6) if p.get('ganador') == ('izq' if side < 0 else 'der') and a >= 1 else 0
        card(d, cx - 138, 300, cx + 138, 800, fill=CARD, outline=mix(c, WHITE, glow * 0.6))
        txt(d, cx, 380, it['titulo'], fit(d, it['titulo'], 38, 240), WHITE)
        d.line([P(cx - 90, 420), P(cx + 90, 420)], fill=c, width=int(6 * S))
        txt(d, cx, 560, it['valor'], fit(d, it['valor'], 104, 230), c, stroke=6)
        if it.get('sub'):
            rich(d, cx, 700, it['sub'], 32, 230, hl=GOLD, fill=MUTED, stroke=0)
    tv = cue(sc, p.get('cue_vs'), 0.4 * sc['dur'])
    a = prog(t, tv, tv + 0.4)
    if a > 0:
        circle(d, 360, 300, 46 * e_back(a), fill=GOLD, outline=INK, width=5)
        txt(d, 360, 300, 'VS', 40 * e_back(a), INK)

def e_versus(sc):
    p = sc['p']
    return [(cue(sc, p['izq'].get('cue'), 0.1), 'pop'), (cue(sc, p['der'].get('cue'), 0.35), 'pop'),
            (cue(sc, p.get('cue_vs'), 0.4 * sc['dur']), 'ching')]

def n_monedas(d, t, sc):
    p = sc['p']
    draw_titulo(d, p, t, y=210)
    n = int(p.get('cantidad', 8))
    modo = p.get('modo', 'sube')
    t0 = cue(sc, p.get('cue'), 0.15)
    span = clamp(sc['dur'] - t0 - 0.5, 0.8, 2.4)
    base_y = 800
    r = 105
    d.ellipse([(360 - 190) * S, (base_y + 20) * S, (360 + 190) * S, (base_y + 60) * S], fill=(6, 40, 52))
    for i in range(n):
        st = t0 + span * i / max(n, 1)
        a = prog(t, st, st + 0.5)
        if a <= 0:
            continue
        ty = base_y - i * r * 0.34
        fall = e_bounce(a)
        y = ty - (1 - fall) * 700
        if modo == 'explota' and t > t0 + span + 0.35:
            q = prog(t, t0 + span + 0.35, t0 + span + 1.2)
            ang = i * 2.4
            y = ty - 380 * q * math.sin(ang * 0.5 + 1.2) + 500 * q * q
            xx = 360 + math.cos(ang) * 420 * q
        else:
            xx = 360
        d.ellipse([(xx - r) * S, (y - r * 0.32) * S, (xx + r) * S, (y + r * 0.32) * S], fill=GOLD_D)
        d.ellipse([(xx - r) * S, (y - r * 0.32 - r * 0.16) * S, (xx + r) * S, (y + r * 0.32 - r * 0.16) * S], fill=GOLD)
        d.ellipse([(xx - r * 0.7) * S, (y - r * 0.2 - r * 0.16) * S, (xx + r * 0.7) * S, (y + r * 0.2 - r * 0.16) * S],
                  outline=GOLD_L, width=int(2 * S))
    if p.get('etiqueta'):
        a = prog(t, t0 + span, t0 + span + 0.4)
        if a > 0:
            rich(d, 360, 925 + (1 - e_out(a)) * 30, p['etiqueta'], 50, 620)

def e_monedas(sc):
    p = sc['p']
    n = int(p.get('cantidad', 8))
    t0 = cue(sc, p.get('cue'), 0.15)
    span = clamp(sc['dur'] - t0 - 0.5, 0.8, 2.4)
    ev = [(t0 + span * i / max(n, 1) + 0.28, 'tick') for i in range(n)]
    if p.get('modo') == 'explota':
        ev.append((t0 + span + 0.35, 'thud'))
    return ev

def n_cierre(d, t, sc):
    p = sc['p']
    draw_titulo(d, {'titulo': p.get('titulo', '')}, t, y=260)
    acc = p.get('acciones') or ['Guárdalo', 'Compártelo', 'Sígueme']
    n = len(acc)
    for i, s in enumerate(acc):
        t0 = cue(sc, None, evenly(sc, i, n, 0.15, 0.7))
        a = prog(t, t0, t0 + 0.4)
        if a <= 0:
            continue
        y = 430 + i * 150
        pulse = 1 + 0.03 * math.sin(t * 5 + i)
        w = 280 * pulse
        rrect(d, 360 - w, y - 55, 360 + w, y + 55, 55, fill=GOLD if i == n - 1 else CARD_L)
        txt(d, 360, y, s, 52 * e_back(a), INK if i == n - 1 else WHITE)

def e_cierre(sc):
    n = len(sc['p'].get('acciones') or [1, 2, 3])
    return [(cue(sc, None, evenly(sc, i, n, 0.15, 0.7)), 'pop') for i in range(n)]

PLANTILLAS = {
    'numero_gigante': (n_num, e_num), 'texto_golpe': (n_texto, e_texto), 'lista_cartas': (n_lista, e_lista),
    'barras': (n_barras, e_barras), 'linea': (n_linea, e_linea), 'versus': (n_versus, e_versus),
    'monedas_pila': (n_monedas, e_monedas), 'cierre': (n_cierre, e_cierre),
}

def bg_particles(d, t):
    for (px, py, sp, sz) in PART:
        y = (py - t * sp * 0.05) % 1.0
        x = px + math.sin(t * sp + px * 9) * 0.01
        circle(d, x * W, y * H, sz, fill=(34, 112, 124))

def band(d, ts):
    a = prog(ts, 0.0, 0.2)
    if a <= 0 or a >= 1:
        return
    x = lerp(-260, W + 260, e_in_out(a))
    pts = [(x - 130, -20), (x + 10, -20), (x - 120 + 160, H + 20), (x - 260 + 160, H + 20)]
    d.polygon([(px * S, py * S) for px, py in pts], fill=GOLD)

_SUBF = {}
SUB_CANDS = ['BarlowCondensed-Bold.ttf', 'DejaVuSansCondensed-Bold.ttf']
SUB_DIRS = [os.path.expanduser('~/.fonts'), '/usr/local/share/fonts', '/usr/share/fonts', os.path.dirname(os.path.abspath(__file__))]
PALETAS = {'rojo': ((255, 56, 73), (209, 26, 35)), 'fe': ((232, 184, 109), (184, 137, 63))}
PALETA = {'n': 'rojo'}

def _subfont_path():
    import glob
    for nm in SUB_CANDS:
        for dd in SUB_DIRS:
            for q in glob.glob(os.path.join(dd, '**', nm), recursive=True):
                return q, (1.0 if nm.startswith('Barlow') else 0.8)
    return _FONT_PATH, 0.7

def subfont(sz):
    k = int(round(sz * S))
    if k not in _SUBF:
        p, fac = _subfont_path()
        _SUBF[k] = ImageFont.truetype(p, max(8, int(k * fac))) if p else ImageFont.load_default()
    return _SUBF[k]

def grupos_de(words):
    out, i = [], 0
    while i < len(words):
        n, ln = 1, len(words[i][0])
        while n < 3 and i + n < len(words) and not re.search('[.?!:;]$', words[i + n - 1][0]):
            ln2 = ln + 1 + len(words[i + n][0])
            if ln2 > 22:
                break
            ln = ln2
            n += 1
        out.append((i, n))
        i += n
    return out

def limpia(w):
    return re.sub('[¿¡«»“”.,;:?!()' + chr(34) + '-]', '', w).upper()

def draw_subs(d, t, words, grupos):
    idx = None
    for i, (w, a, b) in enumerate(words):
        if a <= t < b + 0.04:
            idx = i
            break
    if idx is None:
        return
    for (gs, gn) in grupos:
        if gs <= idx < gs + gn:
            g0, n = gs, gn
            break
    grp = [limpia(w[0]) for w in words[g0:g0 + n]]
    fs = 46
    while True:
        f = subfont(fs)
        sp = 13 * S
        widths = [d.textlength(w, font=f) for w in grp]
        total = sum(widths) + sp * (len(grp) - 1)
        if total < CW * 0.88 or fs < 30:
            break
        fs -= 2
    fill, border = PALETAS.get(PALETA['n'], PALETAS['rojo'])
    cy = 0.727 * CH
    x = (CW - total) / 2
    capb = int(fs * 0.50 * S)
    for j, w in enumerate(grp):
        act = (g0 + j) == idx
        if act:
            px, py = 8 * S, 10 * S
            d.rounded_rectangle([x - px, cy - capb - py, x + widths[j] + px, cy + capb + py], radius=9 * S,
                                fill=fill, outline=border, width=int(2 * S))
        d.text((x + 2 * S, cy + 3 * S), w, font=f, fill=(0, 0, 0), anchor='lm')
        d.text((x, cy), w, font=f, fill=WHITE, anchor='lm', stroke_width=int(3 * S), stroke_fill=(0, 0, 0))
        d.text((x, cy), w, font=f, fill=WHITE, anchor='lm')
        x += widths[j] + sp

def titulo_fijo(d, s):
    if not s:
        return
    f = font(38)
    lines = []
    cur = ''
    for w in s.split():
        if len(cur) + len(w) + 1 > 34 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    y = 100 - 20 * (len(lines) - 1)
    for ln in lines[:2]:
        d.text((CW / 2 + 2 * S, y * S + 2 * S), ln, font=f, fill=(0, 0, 0), anchor='mm')
        d.text((CW / 2, y * S), ln, font=f, fill=WHITE, anchor='mm', stroke_width=int(2 * S), stroke_fill=(0, 0, 0))
        y += 46

def frame(t, scenes, words, total, grupos=None, linea=''):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    bg_particles(d, t)
    sc = scenes[-1]
    for s in scenes:
        if s['start'] <= t < s['start'] + s['dur']:
            sc = s
            break
    lt = t - sc['start']
    PLANTILLAS[sc['plantilla']][0](d, lt, sc)
    band(d, lt)
    d.rectangle([0, 0, CW * clamp(t / total), 10 * S], fill=GOLD)
    titulo_fijo(d, linea)
    draw_subs(d, t, words, grupos or grupos_de(words))
    return img.resize((W, H), Image.LANCZOS)

SR = 44100

def _env(n, k):
    return np.exp(-np.arange(n) / SR * k)

def sfx_clip(kind):
    t = np.arange(int(SR * 1.0)) / SR
    if kind == 'pop':
        n = int(SR * 0.22)
        tt = t[:n]
        return 0.55 * np.sin(2 * np.pi * (520 + 900 * tt) * tt) * _env(n, 22)
    if kind == 'tick':
        n = int(SR * 0.05)
        tt = t[:n]
        return 0.35 * np.sin(2 * np.pi * 1700 * tt) * _env(n, 90)
    if kind == 'ching':
        n = int(SR * 0.9)
        tt = t[:n]
        return 0.32 * (np.sin(2 * np.pi * 1568 * tt) + np.sin(2 * np.pi * 2093 * tt)) * _env(n, 5)
    if kind == 'thud':
        n = int(SR * 0.4)
        tt = t[:n]
        return 0.8 * np.sin(2 * np.pi * (90 - 60 * tt) * tt) * _env(n, 10)
    if kind == 'whoosh':
        n = int(SR * 0.5)
        tt = t[:n]
        noise = np.random.RandomState(1).randn(n)
        k = np.convolve(noise, np.ones(60) / 60, 'same')
        return 0.22 * k * np.sin(np.pi * tt / 0.5)
    if kind == 'rise':
        n = int(SR * 1.2)
        tt = t[:n] if n <= len(t) else np.arange(n) / SR
        return 0.25 * np.sin(2 * np.pi * (240 + 520 * tt) * tt) * np.minimum(tt / 0.2, 1) * np.exp(-np.maximum(tt - 0.9, 0) * 12)
    return np.zeros(10)

def build_sfx(scenes, total, path):
    import wave
    n = int((total + 1.0) * SR)
    buf = np.zeros(n)

    def put(at, kind, vol=1.0):
        c = sfx_clip(kind) * vol
        i = int(at * SR)
        if i < 0 or i >= n:
            return
        j = min(n, i + len(c))
        buf[i:j] += c[:j - i]

    for k, sc in enumerate(scenes):
        if k > 0:
            put(sc['start'] + 0.02, 'whoosh', 0.9)
        for (tt, kind) in PLANTILLAS[sc['plantilla']][1](sc):
            put(sc['start'] + tt, kind)
    peak = max(1e-9, float(np.abs(buf).max()))
    pcm = (np.clip(buf / peak * 0.85, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
