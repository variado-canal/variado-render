# Fondos generados: cada video estrena paleta, degradado y patron propios.
# Las referencias solo dan formato/movimiento; nunca colores ni fondos fijos.
import colorsys, hashlib, math, random, time
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import motion4 as _4

W, H = _4.W, _4.H
PRESETS = ('carbon', 'jean', 'naranja', 'noche', 'verde')
PATRONES = ['puntos', 'cuadricula', 'diagonales', 'anillos', 'olas', 'manchas', 'estrellas', 'rayos', 'hexagonos', 'nada']


def _rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, max(0, min(1, s)), max(0, min(1, v)))
    return (int(r * 255), int(g * 255), int(b * 255))


def _lim(h, v):
    # amarillos/verdes muy claros no dejan leer el texto blanco
    if 40 <= h % 360 <= 80:
        return min(v, 0.80)
    return v


def _degradado(c1, c2, tipo):
    if tipo == 'r':
        gy, gx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((gx - W / 2) / (W * 0.75)) ** 2 + ((gy - H * 0.45) / (H * 0.55)) ** 2)
        k = np.clip(r, 0, 1)[:, :, None]
    elif tipo == 'd':
        gy, gx = np.mgrid[0:H, 0:W]
        k = np.clip((gx / W * 0.55 + gy / H * 0.75), 0, 1)[:, :, None]
    else:
        k = np.linspace(0, 1, H)[:, None, None] * np.ones((1, W, 1))
    a = np.array(c1)[None, None, :] * (1 - k) + np.array(c2)[None, None, :] * k
    return a.astype(np.float32)


def _patron(im, pat, rnd, claro, tinte):
    if pat == 'nada':
        return im
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    base = (255, 255, 255) if claro else tinte
    def col(a):
        return base + (a,)
    if pat == 'puntos':
        sp = rnd.choice((40, 52, 64)); r = sp // 9
        ox, oy = rnd.randint(0, sp), rnd.randint(0, sp)
        for j, y in enumerate(range(-sp, H + sp, sp)):
            for x in range(-sp, W + sp, sp):
                xx = x + ox + (sp // 2 if j % 2 else 0)
                d.ellipse([xx - r, y + oy - r, xx + r, y + oy + r], fill=col(34))
    elif pat == 'cuadricula':
        sp = rnd.choice((60, 80, 100)); ox, oy = rnd.randint(0, sp), rnd.randint(0, sp)
        for x in range(-sp, W + sp, sp):
            d.line([(x + ox, 0), (x + ox, H)], fill=col(26), width=3)
        for y in range(-sp, H + sp, sp):
            d.line([(0, y + oy), (W, y + oy)], fill=col(26), width=3)
    elif pat == 'diagonales':
        sp = rnd.choice((56, 74, 96)); sgn = rnd.choice((-1, 1)); o = rnd.randint(0, sp)
        for k in range(-H, W + H, sp):
            x0 = k + o
            d.line([(x0, 0), (x0 + sgn * H * 0.6, H)], fill=col(24), width=rnd.choice((14, 22, 30)) // 2)
    elif pat == 'anillos':
        cx, cy = rnd.randint(0, W), rnd.randint(200, H - 200)
        st = rnd.choice((70, 90, 120))
        for r in range(st, 1800, st):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col(34), width=4)
    elif pat == 'olas':
        sp = rnd.choice((80, 100, 120)); amp = rnd.randint(18, 34); fr = rnd.uniform(0.012, 0.02); ph = rnd.uniform(0, 6)
        for y in range(-sp, H + sp, sp):
            pts = [(x, y + math.sin(x * fr + ph + y * 0.01) * amp) for x in range(0, W + 20, 12)]
            d.line(pts, fill=col(36), width=6, joint='curve')
    elif pat == 'manchas':
        for i in range(rnd.randint(6, 10)):
            x, y, r = rnd.uniform(-80, W + 80), rnd.uniform(0, H), rnd.uniform(90, 260)
            d.ellipse([x - r, y - r, x + r, y + r], fill=col(rnd.choice((40, 55, 70))))
        ov = ov.filter(ImageFilter.GaussianBlur(38))
    elif pat == 'estrellas':
        for i in range(rnd.randint(34, 56)):
            x, y, s = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice((6, 9, 13, 18))
            d.polygon([(x, y - s), (x + s * .2, y - s * .2), (x + s, y), (x + s * .2, y + s * .2), (x, y + s), (x - s * .2, y + s * .2), (x - s, y), (x - s * .2, y - s * .2)], fill=col(rnd.choice((90, 140, 190))))
    elif pat == 'rayos':
        cx, cy = rnd.randint(120, W - 120), rnd.randint(300, 900)
        n = rnd.choice((14, 18, 22)); a0 = rnd.uniform(0, math.pi)
        for i in range(0, n, 2):
            a = a0 + i * 2 * math.pi / n; b = a + math.pi / n
            R = 2200
            d.polygon([(cx, cy), (cx + math.cos(a) * R, cy + math.sin(a) * R), (cx + math.cos(b) * R, cy + math.sin(b) * R)], fill=col(22))
    elif pat == 'hexagonos':
        r = rnd.choice((46, 60, 76)); dx, dy = r * 1.732, r * 1.5
        ox, oy = rnd.randint(0, int(dx)), rnd.randint(0, int(dy))
        for j in range(-1, int(H / dy) + 2):
            for i in range(-1, int(W / dx) + 2):
                cx = i * dx + (dx / 2 if j % 2 else 0) + ox; cy = j * dy + oy
                d.polygon([(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)], outline=col(34))
    im = im.convert('RGBA')
    im.alpha_composite(ov)
    return im.convert('RGB')


def generar(kind):
    # kind = 'gen:h:s:v:h2:s2:v2:patron:grad:semilla'
    p = kind.split(':')
    h, s, v, h2, s2, v2 = (float(x) for x in p[1:7])
    pat, grad, seed = p[7], p[8], int(p[9])
    rnd = random.Random(seed)
    c1, c2 = _rgb(h, s, v), _rgb(h2, s2, v2)
    a = _degradado(c1, c2, grad)
    a = _4._vig(a, 0.42)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    claro = v > 0.6
    tinte = _rgb(h, min(1.0, s + 0.1), min(1.0, v + 0.35)) if not claro else (255, 255, 255)
    return _patron(im, pat, rnd, claro, tinte)


_orig = _4.fondo


def fondo(kind):
    if isinstance(kind, str) and kind.startswith('gen:'):
        if kind not in _4._FX:
            _4._FX[kind] = generar(kind)
        return _4._FX[kind]
    return _orig(kind)


_4.fondo = fondo


def paleta_video(rnd, opc=None):
    opc = opc or {}
    h0 = opc.get('hue', rnd.uniform(0, 360))
    modo = opc.get('modo') or rnd.choices(['oscuro', 'vivo', 'medio'], [35, 40, 25])[0]
    esquema = rnd.choice(['mono', 'analogo', 'complemento', 'analogo'])
    pat = opc.get('patron') or rnd.choice(PATRONES)
    ini = rnd.randint(0, 2)
    return {'h0': h0, 'modo': modo, 'esquema': esquema, 'pat': pat, 'ini': ini}


def fondo_escena(pv, i, rnd, tono=0):
    esq = pv['esquema']
    if esq == 'mono':
        h = pv['h0'] + rnd.uniform(-8, 8)
    elif esq == 'analogo':
        h = pv["h0"] + 16 * ((i % 3) - 1) + rnd.uniform(-6, 6)
    else:
        h = pv['h0'] + (120 if i % 2 else 0) + rnd.uniform(-8, 8)
    h2 = h + rnd.choice((-1, 1)) * rnd.uniform(18, 46)
    m = pv['modo']
    if m == 'oscuro':
        s, v, s2, v2 = rnd.uniform(.55, .85), rnd.uniform(.20, .30), rnd.uniform(.5, .8), rnd.uniform(.38, .52)
    elif m == 'vivo':
        s, v, s2, v2 = rnd.uniform(.65, .9), rnd.uniform(.80, .95), rnd.uniform(.7, .95), rnd.uniform(.55, .72)
    else:
        s, v, s2, v2 = rnd.uniform(.45, .65), rnd.uniform(.55, .68), rnd.uniform(.5, .7), rnd.uniform(.35, .45)
    v = _lim(h, v + tono); v2 = _lim(h2, v2 + tono)
    grad = ['v', 'd', 'r'][(pv['ini'] + i) % 3]
    seed = rnd.randint(1, 10 ** 6)
    return 'gen:%d:%.2f:%.2f:%d:%.2f:%.2f:%s:%s:%d' % (h % 360, s, v, h2 % 360, s2, v2, pv['pat'], grad, seed)


def variar(job):
    # reemplaza fondos fijos por fondos nuevos de este video (solo si no pide fondo propio)
    esc = job.get('escenas') or []
    opc = job.get('opciones') or {}
    if opc.get('fondo_fijo'):
        return job
    txt = str(job.get('job_id', '')) + '|' + str(job.get('guion', '')) + '|' + str(time.time_ns())
    rnd = random.Random(int(hashlib.md5(txt.encode('utf-8')).hexdigest()[:12], 16))
    pv = paleta_video(rnd, opc.get('fondos') if isinstance(opc.get('fondos'), dict) else None)
    for i, sc in enumerate(esc):
        f = sc.get('fondo')
        if f is None or f in PRESETS:
            tono = -0.08 if f in ('carbon', 'noche') else (0.06 if f in ('verde', 'naranja') else 0)
            sc['fondo'] = fondo_escena(pv, i, rnd, tono)
    job['fondos_video'] = {k: pv[k] for k in ('modo', 'esquema', 'pat')}
    return job

