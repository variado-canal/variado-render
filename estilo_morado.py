import colorsys
import hashlib
import math
import random
import re
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import motion3 as _3
import motion4 as _4

ESTILO = {'modo': None}
_LISTO = {'ok': False}
_ORIG_SUBS = _4.draw_subs2
_ORIG_FONDO = {'f': None}


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(r * 255), int(g * 255), int(b * 255))


def fondo_morado(kind):
    # kind = 'mor:suave:<semilla>' | 'mor:negro:<semilla>'
    p = kind.split(':')
    modo, seed = p[1], int(p[2])
    rnd = random.Random(seed)
    W, H = _4.W, _4.H
    gy, gx = np.mgrid[0:H, 0:W]
    h = 268 + rnd.uniform(-7, 7)
    cx = W * (0.5 + rnd.uniform(-0.08, 0.08))
    cy = H * (0.44 + rnd.uniform(-0.05, 0.05))
    r = np.sqrt(((gx - cx) / (W * 0.80)) ** 2 + ((gy - cy) / (H * 0.58)) ** 2)
    k = np.clip(r, 0, 1) ** 1.15
    k = k[:, :, None]
    if modo == 'suave':
        c1 = np.array(_rgb(h, 0.56, 0.76 + rnd.uniform(-0.03, 0.04)), np.float32)
        c2 = np.array(_rgb(h + 8, 0.85, 0.24), np.float32)
    else:
        c1 = np.array(_rgb(h, 0.70, 0.17), np.float32)
        c2 = np.array(_rgb(h, 0.60, 0.035), np.float32)
    a = c1[None, None, :] * (1 - k) + c2[None, None, :] * k
    a = _4._vig(a, 0.30 if modo == 'suave' else 0.15)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if modo == 'suave':
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        sp = 44
        ox, oy = rnd.randint(0, sp), rnd.randint(0, sp)
        for j, y in enumerate(range(-sp, H + sp, sp)):
            for x in range(-sp, W + sp, sp):
                xx = x + ox + (sp // 2 if j % 2 else 0)
                d.ellipse([xx - 4, y + oy - 4, xx + 4, y + oy + 4], fill=(255, 255, 255, 0))
        im = im.convert('RGBA')
        im.alpha_composite(ov)
        im = im.convert('RGB')
    return im


def _fondo(kind):
    if isinstance(kind, str) and kind.startswith('mor:'):
        if kind not in _4._FX:
            _4._FX[kind] = fondo_azul(kind) if ':azul:' in kind else fondo_morado(kind)
        return _4._FX[kind]
    return _ORIG_FONDO['f'](kind)


def _tint_viejo(lay, k, glow):
    bb = lay.getchannel('A').getbbox()
    if not bb:
        return lay
    S = _3.S
    pad = int(30 * S)
    x0, y0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
    x1, y1 = min(lay.size[0], bb[2] + pad), min(lay.size[1], bb[3] + pad)
    c = lay.crop((x0, y0, x1, y1))
    a = np.asarray(c).astype(np.float32)
    rgb, al = a[:, :, :3], a[:, :, 3:4]
    L = (rgb[:, :, 0] * 0.299 + rgb[:, :, 1] * 0.587 + rgb[:, :, 2] * 0.114) / 255.0
    L = np.clip(0.16 + 0.84 * np.clip((L - 0.05) * 1.2, 0, 1), 0, 1)[:, :, None]
    lo = np.array((62, 22, 124), np.float32)
    mid = np.array((152, 94, 242), np.float32)
    hi = np.array((238, 224, 255), np.float32)
    t2 = np.clip(L * 2, 0, 1)
    t3 = np.clip(L * 2 - 1, 0, 1)
    pur = np.where(L < 0.5, lo + (mid - lo) * t2, mid + (hi - mid) * t3)
    out_rgb = rgb * (1 - k) + pur * k
    res = np.concatenate([out_rgb, al], axis=2)
    img = Image.fromarray(np.clip(res, 0, 255).astype(np.uint8), 'RGBA')
    if glow:
        A = img.getchannel('A')
        sm = A.resize((max(2, A.size[0] // 4), max(2, A.size[1] // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize(A.size, Image.BILINEAR)
        g = Image.new('RGBA', img.size, (178, 120, 255, 0))
        g.putalpha(sm.point(lambda v: int(v * 0.8)))
        g.alpha_composite(img)
        img = g
    out = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    out.paste(img, (x0, y0))
    return out


def _wrap_viejo(fn):
    def g(ti, t):
        modo = ESTILO['modo']
        if not modo:
            return fn(ti, t)
        lay = Image.new('RGBA', ti.size, (0, 0, 0, 0))
        fn(lay, t)
        ti.alpha_composite(_tint(lay, 1.0 if modo == 'negro' else 0.55, modo == 'negro'))
    g._morado = True
    return g


def fijar(sc):
    kind = str(sc.get('fondo') or '')
    modo = 'negro' if kind.startswith(('mor:negro', 'mor:azul')) else ('suave' if kind.startswith('mor:suave') else None); ESTILO['pal'] = 'azul' if kind.startswith('mor:azul') else 'mor'
    if modo != ESTILO['modo']:
        ESTILO['modo'] = modo; _3.PT = () if modo else _3.PT
        try:
            _3._TILE.clear()
        except Exception:
            pass
        try:
            _3._m.COLORES['oro'] = (214, 182, 255) if modo else (255, 209, 92)
        except Exception:
            pass


def draw_subs3(d, t, words, frases):
    if not ESTILO['modo']:
        return _ORIG_SUBS(d, t, words, frases)
    S, CW, H = _3.S, _3.CW, _3.H
    pfont = _4.pfont
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
    toks = [re.sub('["]', '', w[0]) for w in words[g0:g0 + n]]
    fs = 60
    sp = 16 * S
    maxw = CW * 0.86
    while True:
        fb, fm = pfont(fs, True), pfont(fs, False)
        ws = [d.textlength(x, font=fb) for x in toks]
        if sum(ws) + sp * (len(ws) - 1) <= maxw * 1.75 or fs < 40:
            break
        fs -= 2
    lines, cur, cw = [], [], 0.0
    tot = sum(ws) + sp * (len(ws) - 1)
    for j, x in enumerate(toks):
        if cur and (cw + sp + ws[j] > tot * 0.58 + 40 * S) and len(lines) == 0:
            lines.append(cur)
            cur, cw = [], 0.0
        cur.append(j)
        cw += (sp if len(cur) > 1 else 0) + ws[j]
    lines.append(cur)
    lh = fs * 1.34
    y = 0.178 * H
    for ln in lines:
        lw = sum(ws[j] for j in ln) + sp * (len(ln) - 1)
        x = (CW - lw) / 2
        for j in ln:
            gi = g0 + j
            active = gi == idx
            spoken = gi <= idx
            f = fb if spoken else fm
            if active:
                col_t = (255, 255, 255, 255)
                halos = ((11, 70), (8, 110), (5, 170), (3, 235))
            elif spoken:
                col_t = (236, 224, 255, 255)
                halos = ((9, 50), (6, 90), (3, 200))
            else:
                col_t = (190, 160, 250, 130)
                halos = ((6, 40), (3, 90))
            for rr, al in halos:
                d.text((x, y * S), toks[j], font=f, fill=(0, 0, 0, 0), anchor='lm', stroke_width=int(rr * S / 2), stroke_fill=(128, 70, 235, al))
            d.text((x, y * S), toks[j], font=f, fill=col_t, anchor='lm')
            x += ws[j] + sp
        y += lh


def instalar():
    if _LISTO['ok']:
        return
    _LISTO['ok'] = True
    for k, fn in list(_3.OBJETOS.items()):
        if not getattr(fn, '_morado', False):
            _3.OBJETOS[k] = _wrap(fn)
    _ORIG_FONDO['f'] = _4.fondo
    _4.fondo = _fondo
    _4.draw_subs2 = draw_subs3


def _tint(lay, k, glow):
    bb = lay.getchannel('A').getbbox()
    if not bb:
        return None
    S = _3.S
    pad = int(30 * S)
    x0, y0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
    x1, y1 = min(lay.size[0], bb[2] + pad), min(lay.size[1], bb[3] + pad)
    c = lay.crop((x0, y0, x1, y1))
    A = c.getchannel('A')
    g = c.convert('L').point(lambda v: int(40 + 0.84 * v))
    col = ImageOps.colorize(g, black=(100, 60, 182), white=(246, 238, 255), mid=(180, 136, 255), blackpoint=40, whitepoint=255, midpoint=140)
    if k < 1.0:
        col = Image.blend(c.convert('RGB'), col, k)
    col = col.convert('RGBA')
    col.putalpha(A)
    if glow:
        sm = A.resize((max(2, A.size[0] // 4), max(2, A.size[1] // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize(A.size, Image.BILINEAR)
        gl = Image.new('RGBA', col.size, (178, 120, 255, 0))
        gl.putalpha(sm.point(lambda v: int(v * 0.8)))
        gl.alpha_composite(col)
        col = gl
    return col, x0, y0


def _wrap(fn):
    def g(ti, t):
        modo = ESTILO['modo']
        if not modo:
            return fn(ti, t)
        lay = Image.new('RGBA', ti.size, (0, 0, 0, 0))
        fn(lay, t)
        r = _tint(lay, 1.0, True) if modo == 'negro' else (lay, 0, 0)
        if r:
            ti.alpha_composite(r[0], dest=(r[1], r[2]))
    g._morado = True
    return g


def variar(job):
    esc = job.get('escenas') or []
    opc = job.get('opciones') or {}
    txt = str(job.get('job_id', '')) + '|' + str(time.time_ns())
    rnd = random.Random(int(hashlib.md5(txt.encode('utf-8')).hexdigest()[:12], 16))
    modo = opc.get('modo_morado') or rnd.choice(['suave', 'negro', 'azul'])
    for sc in esc:
        f = sc.get('fondo')
        if f is None or not str(f).startswith(('mor:', 'gen:')):
            sc['fondo'] = 'mor:%s:%d' % (modo, rnd.randint(1, 10 ** 6))
    job['fondos_video'] = {'modo': modo, 'estilo': 'morado'}
    return job