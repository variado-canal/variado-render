import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

import motion3 as _3
from motion3 import *

_FX = {}
_OUT = {}


def _outfit():
    if 'p' not in _OUT:
        _OUT['p'] = None
        for dd in (os.path.expanduser('~/.fonts'), '/usr/share/fonts', '/tmp', '.'):
            if os.path.isdir(dd):
                for fn in os.listdir(dd):
                    if fn.startswith('Outfit') and fn.endswith('.ttf'):
                        _OUT['p'] = os.path.join(dd, fn)
    return _OUT['p']


def _mk(sz, bold):
    p = _outfit()
    if p:
        try:
            f = ImageFont.truetype(p, sz)
            f.set_variation_by_axes([700 if bold else 500])
            return f
        except Exception:
            pass
    return None


_PF4 = {}
_PFO = _3.pfont


def pfont(sz, bold):
    k = (int(round(sz * S)), bold)
    if k not in _PF4:
        _PF4[k] = _mk(k[0], bold) or _PFO(sz, bold)
    return _PF4[k]


_3.pfont = pfont
_FB = {}
_FO = _3._m.font


def font(sz):
    k = max(6, int(round(sz * S / 2.0)) * 2)
    if k not in _FB:
        _FB[k] = _mk(k, True) or _FO(sz)
    return _FB[k]


_3._m.font = font


def _vig(arr, k=0.55):
    gy, gx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((gx - W / 2) / (W * 0.62)) ** 2 + ((gy - H * 0.5) / (H * 0.62)) ** 2)
    return arr * (1.0 - k * np.clip(r - 0.45, 0, 1) ** 1.4)[:, :, None]


def _dash(d, pts, color, dash=26, gap=16, width=5):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L // (dash + gap)))
        for i in range(n + 1):
            a = i * (dash + gap) / max(L, 1)
            b = min(1.0, (i * (dash + gap) + dash) / max(L, 1))
            if a >= 1:
                break
            d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=color, width=width)


def _grad(c1, c2, vertical=True):
    k = np.linspace(0, 1, H if vertical else W)[:, None, None] if vertical else np.linspace(0, 1, W)[None, :, None]
    a = np.array(c1)[None, None, :] * (1 - k) + np.array(c2)[None, None, :] * k
    return np.broadcast_to(a, (H, W, 3)).astype(np.float32).copy()


def fondo(kind):
    if kind in _FX:
        return _FX[kind]
    gy, gx = np.mgrid[0:H, 0:W]
    random.seed(5)
    if kind == 'jean':
        a = _grad((52, 90, 158), (30, 58, 116))
        a += (((gx + gy) % 5) < 2)[:, :, None] * 5.0
        a += (((gx - gy) % 7) < 1)[:, :, None] * 3.0
        a = _vig(a, 0.5)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        g = (226, 170, 60)
        _dash(d, [(0, 300), (W, 300)], g)
        _dash(d, [(30, 640), (690, 640), (690, 1180), (360, 1260), (30, 1180), (30, 640)], g)
        _dash(d, [(30, 700), (360, 770), (690, 700)], g, 22, 14, 4)
        d.rounded_rectangle([330, 170, 392, 296], radius=8, outline=(30, 52, 100), width=3)
        d.ellipse([60, 330, 660, 930], outline=(120, 160, 230), width=3)
    elif kind == 'naranja':
        r = np.sqrt(((gx - W / 2) / (W * 0.7)) ** 2 + ((gy - H * 0.42) / (H * 0.5)) ** 2)
        k = np.clip(r, 0, 1)[:, :, None]
        a = np.array((255, 218, 70))[None, None, :] * (1 - k) + np.array((244, 150, 22))[None, None, :] * k
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for i in range(10):
            x0, y0 = random.uniform(-80, W), random.uniform(0, H)
            pts = []
            for j in range(18):
                u = j / 17.0
                pts.append((x0 + math.sin(u * 3 + i) * 120 + u * 160 * (1 if i % 2 else -1), y0 + u * 360))
            d.line(pts, fill=(238, 122, 24, 190), width=int(random.uniform(40, 90)), joint='curve')
        for i in range(12):
            x, y, rr = random.uniform(0, W), random.uniform(0, H), random.uniform(20, 70)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 244, 170, 70))
        ov = ov.filter(ImageFilter.GaussianBlur(1.5))
        im.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(im)
        d.ellipse([20, 220, 700, 900], outline=(255, 236, 160), width=6)
    elif kind == 'noche':
        a = _grad((22, 18, 58), (82, 44, 124))
        a = _vig(a, 0.4)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        for i in range(70):
            x, y, rr = random.uniform(0, W), random.uniform(0, H), random.choice((1, 1.5, 2, 3))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(230, 226, 255))
    elif kind == 'verde':
        a = _grad((12, 62, 50), (24, 128, 88))
        a = _vig(a, 0.5)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        for i in range(14):
            x, y, rr = random.uniform(0, W), random.uniform(0, H), random.uniform(30, 90)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(60, 170, 120), width=3)
    else:
        a = np.zeros((H, W, 3), np.float32) + np.array((46, 46, 49))
        a += (((gx % 36) == 0) | ((gy % 36) == 0))[:, :, None] * 7.0
        a = _vig(a, 0.6)
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    _FX[kind] = im
    return im


def _sparkle(d, x, y, s, a):
    c = (255, 255, 255, int(255 * a))
    d.polygon([(x, y - s), (x + s * 0.18, y - s * 0.18), (x + s, y), (x + s * 0.18, y + s * 0.18), (x, y + s), (x - s * 0.18, y + s * 0.18), (x - s, y), (x - s * 0.18, y - s * 0.18)], fill=c)


def _pt(ti, x, y):
    return (x * S, y * S)


def _thick(td, p0, p1, w, color):
    td.line([_pt(0, *p0), _pt(0, *p1)], fill=color, width=int(w * S))
    for q in (p0, p1):
        td.ellipse([(q[0] - w / 2) * S, (q[1] - w / 2) * S, (q[0] + w / 2) * S, (q[1] + w / 2) * S], fill=color)


_PP = {}


def obj_personaje(ti, t):
    td = ImageDraw.Draw(ti)
    mood = _PP.get('mood', 'feliz')
    skin, skin_d = (204, 112, 52), (176, 92, 40)
    w = math.sin(t * 6) * 14
    if mood == 'feliz':
        _thick(td, (345, 430), (262 + w, 250), 40, skin_d)
        _thick(td, (455, 430), (538 - w, 250), 40, skin_d)
        td.ellipse([(262 + w - 28) * S, (250 - 28) * S, (262 + w + 28) * S, (250 + 28) * S], fill=(196, 104, 46))
        td.ellipse([(538 - w - 28) * S, (250 - 28) * S, (538 - w + 28) * S, (250 + 28) * S], fill=(196, 104, 46))
    else:
        _thick(td, (345, 440), (300, 590), 40, skin_d)
        _thick(td, (455, 440), (500, 590), 40, skin_d)
    _thick(td, (368, 630), (338, 745), 32, skin_d)
    _thick(td, (432, 630), (468, 745), 32, skin_d)
    for sx in (336, 470):
        td.ellipse([(sx - 38) * S, 700 * S, (sx + 38) * S, 776 * S], fill=(112, 84, 196))
        td.rounded_rectangle([(sx - 30) * S, 668 * S, (sx + 30) * S, 716 * S], radius=14 * S, fill=(238, 238, 240))
    grad_rr(ti, 335, 400, 465, 540, 40, (24, 178, 146), (16, 140, 118), diag=False)
    td.ellipse([308 * S, 396 * S, 372 * S, 470 * S], fill=(20, 160, 132))
    td.ellipse([428 * S, 396 * S, 492 * S, 470 * S], fill=(12, 130, 106))
    td.rectangle([338 * S, 534 * S, 462 * S, 556 * S], fill=(238, 84, 84))
    grad_rr(ti, 336, 552, 464, 640, 30, (40, 52, 150), (30, 38, 116), diag=False)
    ov = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([(400 - 110) * S, (205 - 100) * S, (400 + 110) * S, (205 + 100) * S], fill=(74, 30, 42, 255))
    for k, (hx, hy) in enumerate(((250, 160), (300, 110), (400, 85), (500, 110), (550, 160))):
        od.ellipse([(hx - 70) * S, (hy - 52) * S, (hx + 70) * S, (hy + 52) * S], fill=(74, 30, 42, 255))
    ti.alpha_composite(ov)
    td = ImageDraw.Draw(ti)
    td.ellipse([(400 - 92) * S, (330 - 94) * S, (400 + 92) * S, (330 + 94) * S], fill=skin)
    od = ImageDraw.Draw(ti)
    od.pieslice([(400 - 100) * S, (330 - 108) * S, (400 + 100) * S, (330 + 60) * S], 180, 360, fill=(74, 30, 42))
    for ex in (356, 444):
        if mood == 'feliz':
            td.arc([(ex - 20) * S, 318 * S, (ex + 20) * S, 352 * S], 200, 340, fill=(60, 22, 30), width=int(7 * S))
        else:
            td.arc([(ex - 20) * S, 330 * S, (ex + 20) * S, 360 * S], 20, 160, fill=(60, 22, 30), width=int(7 * S))
    for bx in (330, 470):
        td.ellipse([(bx - 22) * S, 346 * S, (bx + 22) * S, 380 * S], fill=(244, 98, 98) if mood == 'feliz' else (200, 90, 70))
    if mood == 'feliz':
        td.ellipse([380 * S, 362 * S, 420 * S, 394 * S], fill=(80, 20, 44))
        td.ellipse([388 * S, 378 * S, 412 * S, 394 * S], fill=(240, 110, 130))
    else:
        td.arc([380 * S, 372 * S, 420 * S, 400 * S], 200, 340, fill=(80, 20, 44), width=int(6 * S))
        td.ellipse([462 * S, 372 * S, 478 * S, 400 * S], fill=(120, 190, 255))


def obj_iphone(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 230, 40, 570, 770, 56, (210, 212, 222), (120, 124, 140))
    grad_rr(ti, 238, 48, 562, 762, 50, (14, 14, 20), (8, 8, 12))
    sc = grad_img(int(308 * S), int(698 * S), (66, 70, 168), (128, 76, 150), diag=False)
    m = Image.new('L', sc.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, sc.size[0] - 1, sc.size[1] - 1], radius=44 * S, fill=255)
    ti.paste(sc, (int(246 * S), int(56 * S)), m)
    td.rounded_rectangle([340 * S, 70 * S, 460 * S, 106 * S], radius=18 * S, fill=(6, 6, 10))
    td.text((400 * S, 190 * S), 'martes, 14 de octubre', font=pfont(20, True), fill=(235, 235, 255), anchor='mm')
    td.text((400 * S, 262 * S), '21:30', font=pfont(84, True), fill=WHITE, anchor='mm')
    pulse = 1 + 0.05 * math.sin(t * 5)
    r = 66 * pulse
    td.ellipse([(400 - r) * S, (470 - r) * S, (400 + r) * S, (470 + r) * S], outline=(120, 170, 255), width=int(7 * S))
    for cx in (292, 508):
        td.ellipse([(cx - 28) * S, 664 * S, (cx + 28) * S, 720 * S], fill=(60, 56, 120))
    td.rounded_rectangle([340 * S, 742 * S, 460 * S, 748 * S], radius=3 * S, fill=(230, 230, 245))


def obj_mira(ti, t):
    td = ImageDraw.Draw(ti)
    R = (229, 62, 62)
    for r, w in ((150, 14), (90, 14), (36, 30)):
        td.ellipse([(400 - r) * S, (400 - r) * S, (400 + r) * S, (400 + r) * S], outline=R, width=int(w * S))
    td.line([(400 * S, 200 * S), (400 * S, 600 * S)], fill=R, width=int(10 * S))
    td.line([(200 * S, 400 * S), (600 * S, 400 * S)], fill=R, width=int(10 * S))
    td.ellipse([380 * S, 380 * S, 420 * S, 420 * S], fill=WHITE)


def obj_grafico_flecha(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 120, 560, 200, 700, 10, (46, 214, 110), (24, 160, 80), diag=False)
    grad_rr(ti, 240, 480, 320, 700, 10, (46, 214, 110), (24, 160, 80), diag=False)
    grad_rr(ti, 360, 380, 440, 700, 10, (46, 214, 110), (24, 160, 80), diag=False)
    grad_rr(ti, 480, 260, 560, 700, 10, (46, 214, 110), (24, 160, 80), diag=False)
    td.line([(130 * S, 520 * S), (280 * S, 400 * S), (400 * S, 300 * S), (560 * S, 160 * S)], fill=WHITE, width=int(12 * S), joint='curve')
    td.polygon([(600 * S, 120 * S), (610 * S, 220 * S), (520 * S, 170 * S)], fill=WHITE)


_3.OBJETOS.update({'personaje': obj_personaje, 'iphone': obj_iphone, 'mira': obj_mira, 'crecimiento': obj_grafico_flecha})


def n_objeto(d, t, sc):
    p = sc['p']
    cx, cy = float(p.get('x', 360)), float(p.get('y', 480))
    kind = p.get('objeto', 'tarjeta')
    _PP['mood'] = p.get('animo', 'feliz')
    t0 = cue(sc, p.get('cue'), 0.05)
    a = prog(t, t0, t0 + 0.45)
    if p.get('campo', False) and a > 0:
        _3.campo(d, cx, cy, t, a)
    if a > 0:
        if kind in _3.ESTATICOS and kind in _3._TILE:
            ti = _3._TILE[kind]
        else:
            ti = Image.new('RGBA', (800 * S, 800 * S), (0, 0, 0, 0))
            _3.OBJETOS[kind](ti, t)
            bb = ti.getchannel('A').getbbox()
            if bb:
                ti = ti.crop(bb)
            if kind in _3.ESTATICOS:
                _3._TILE[kind] = ti
        ang = float(p.get('angulo', 0)) + math.sin(t * 1.6) * 2.0
        k = float(p.get('escala', 1.0)) * (0.5 + 0.5 * e_back(a))
        sz = (max(2, int(ti.size[0] * k)), max(2, int(ti.size[1] * k)))
        ti = ti.resize(sz, Image.BILINEAR)
        if abs(ang) > 0.05:
            ti = ti.rotate(ang, resample=Image.BILINEAR, expand=True)
        bob = math.sin(t * 2.2) * 7
        sh = Image.new('RGBA', ti.size, (0, 0, 0, 0))
        sh.paste((0, 0, 0, 110), (0, 0), ti.getchannel('A'))
        sh = sh.filter(ImageFilter.GaussianBlur(10 * S))
        px, py = int(cx * S - ti.size[0] / 2), int((cy + bob) * S - ti.size[1] / 2)
        d._image.paste(sh, (px + 10 * S, py + 26 * S), sh)
        d._image.paste(ti, (px, py), ti)
    for i, lb in enumerate(p.get('etiquetas') or []):
        tl = cue(sc, lb.get('cue'), evenly(sc, i, len(p['etiquetas']), 0.2, 0.7))
        aa = prog(t, tl, tl + 0.35)
        if aa <= 0:
            continue
        lx, ly = cx + float(lb.get('dx', 200)), cy + float(lb.get('dy', -200))
        tx = str(lb['texto'])
        fs = 34
        wpx = d.textlength(tx, font=pfont(fs, True)) / S + 44
        k = e_back(aa)
        rrect(d, lx - wpx / 2 * k, ly - 34 * k, lx + wpx / 2 * k, ly + 34 * k, 18, fill=(255, 255, 255), outline=None)
        if k > 0.7:
            d.text((lx * S, ly * S), tx, font=pfont(fs, True), fill=(20, 20, 26), anchor='mm')
    ct = p.get('contador')
    if ct:
        tc = cue(sc, ct.get('cue'), 0.3 * sc['dur'])
        ac = prog(t, tc, tc + 0.3)
        if ac > 0:
            v = lerp(float(ct.get('desde', 0)), float(ct['valor']), e_out(prog(t, tc, tc + 1.4)))
            s2 = fmt(v, int(ct.get('decimales', 0)), ct.get('prefijo', ''), ct.get('sufijo', ''))
            y = float(ct.get('y', 800))
            fs = fit(d, s2, 120, 470)
            wtx = d.textlength(s2, font=_3._m.font(fs)) / S
            half = (wtx + 140) / 2 * e_back(ac)
            rrect(d, 360 - half, y - 82, 360 + half, y + 82, 82, fill=(18, 18, 22, 235))
            if ac > 0.6:
                x0 = 360 - half + 52
                d.polygon([P(x0, y - 26), P(x0, y + 26), P(x0 + 46, y)], fill=WHITE)
                d.text(((360 + 36) * S, y * S), s2, font=_3._m.font(fs), fill=col(ct.get('color', 'blanco')), anchor='mm')
    ru = p.get('cota')
    if ru:
        tr = cue(sc, ru.get('cue'), 0.4 * sc['dur'])
        ar = prog(t, tr, tr + 0.6)
        if ar > 0:
            y = float(ru.get('y', 790))
            x1 = 120 + 480 * e_out(ar)
            d.line([P(120, y), P(x1, y)], fill=WHITE, width=int(5 * S))
            for xx in (120, x1):
                d.line([P(xx, y - 16), P(xx, y + 16)], fill=WHITE, width=int(5 * S))
            if ar > 0.8:
                d.text((360 * S, (y + 46) * S), str(ru['texto']), font=pfont(34, True), fill=WHITE, anchor='mm', stroke_width=int(4 * S), stroke_fill=(0, 0, 0))


PLANTILLAS['objeto'] = (n_objeto, _3.e_objeto)

_DEF = {'objeto': 'carbon', 'texto_golpe': 'noche', 'lista_cartas': 'jean', 'numero_gigante': 'carbon', 'linea': 'carbon',
        'barras': 'carbon', 'versus': 'jean', 'cierre': 'naranja'}


def frame(t, scenes, words, total, grupos=None, linea=''):
    sc = scenes[-1]
    for s in scenes:
        if s['start'] <= t < s['start'] + s['dur']:
            sc = s
            break
    lt = t - sc['start']
    kind = sc.get('fondo') or _DEF.get(sc['plantilla'], 'carbon')
    base = fondo(kind).copy()
    pl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dp = ImageDraw.Draw(pl)
    if kind == 'naranja':
        for i, (sx, sy, ss) in enumerate(((120, 560, 22), (610, 380, 16), (80, 1000, 18), (640, 860, 26), (360, 240, 14))):
            _sparkle(dp, sx, sy, ss * (0.6 + 0.4 * math.sin(t * 4 + i * 1.7)), 0.5 + 0.5 * math.sin(t * 3 + i))
    else:
        for (px, py, spd, sz, br) in _3.PT:
            y = (py - t * spd * 0.03) % 1.0
            x = px + math.sin(t * spd + px * 9) * 0.01
            al = int((20 if sz > 5 else 60) * br)
            dp.ellipse([x * W - sz, y * H - sz, x * W + sz, y * H + sz], fill=(235, 235, 245, al))
    base.paste(pl, (0, 0), pl)
    layer = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    PLANTILLAS[sc['plantilla']][0](dl, lt, sc)
    intro = e_out(prog(lt, 0.0, 0.25))
    scale = 0.94 * (1.0 + 0.05 * prog(lt, 0.0, sc['dur'])) * (1.07 - 0.07 * intro)
    sz = (max(2, int(W * scale)), max(2, int(H * scale)))
    lay = layer.resize(sz, Image.LANCZOS)
    full = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    full.paste(lay, (int(W / 2 - 360 * scale), int(790 - 520 * scale)))
    al = full.getchannel('A').point(lambda v: int(v * (0.25 + 0.75 * intro)))
    full.putalpha(al)
    sh = al.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)
    sh = sh.point(lambda v: int(v * 0.5))
    base.paste(Image.new('RGB', (W, H), (0, 0, 0)), (0, 12), sh)
    base.paste(full, (0, 0), full)
    th = int(0.30 * CH)
    tile = Image.new('RGBA', (CW, th), (0, 0, 0, 0))
    draw_subs2(ImageDraw.Draw(tile), t, words, grupos or phrases_de(words))
    tile = tile.resize((W, th // S), Image.LANCZOS)
    base.paste(tile, (0, 0), tile)
    arr = np.asarray(base).astype(np.int16) + _3._NOISE[int(t * 30) % 6]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

