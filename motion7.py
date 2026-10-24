import math

from PIL import Image, ImageDraw

import motion3 as _3
import motion5 as _5
import estilo_morado as _E
from motion6 import *
from motion6 import n_escena6, PLANTILLAS, cue, prog, S, pfont


def _poly(td, pts, fill, outline=None, w=0):
    td.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline, width=int(w * S) if outline else 0)


def _ell(td, cx, cy, rx, ry, fill, outline=None, w=0):
    td.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill, outline=outline, width=int(w * S) if outline else 0)


def _rr(td, x0, y0, x1, y1, r, fill, outline=None, w=0):
    td.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=fill, outline=outline, width=int(w * S) if outline else 0)


def _ln(td, pts, fill, w):
    td.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint='curve')


def _spark(td, x, y, r, fill=(255, 255, 255)):
    _poly(td, [(x, y - r), (x + r * .25, y - r * .25), (x + r, y), (x + r * .25, y + r * .25), (x, y + r), (x - r * .25, y + r * .25), (x - r, y), (x - r * .25, y - r * .25)], fill)


def _rot(ti, draw_fn, deg, cx=400, cy=430):
    lay = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    lay = lay.rotate(deg, center=(cx * S, cy * S), resample=Image.BICUBIC)
    ti.alpha_composite(lay)


def obj_corazon(ti, t):
    td = ImageDraw.Draw(ti)
    beat = max(0.0, math.sin(t * 7.0)) ** 3
    k = 17.5 * (1 + 0.07 * beat)
    pts = []
    for i in range(96):
        a = i / 96 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((400 + x * k, 450 - y * k))
    _poly(td, [(x + 10, y + 12) for x, y in pts], (140, 18, 48))
    _poly(td, pts, (232, 52, 84), (255, 140, 165), 7)
    _ell(td, 318, 348, 50, 26, (255, 176, 196))
    if beat > 0.12:
        r = 230 + 110 * beat
        td.ellipse([(400 - r) * S, (440 - r) * S, (400 + r) * S, (440 + r) * S], outline=(255, 130, 160, int(150 * (1 - beat))), width=int(7 * S))


def obj_cerebro(ti, t):
    td = ImageDraw.Draw(ti)
    _ell(td, 400, 430, 270, 230, (255, 120, 170, 40))
    _rr(td, 365, 560, 435, 690, 28, (226, 140, 164))
    _ell(td, 295, 430, 118, 170, (246, 170, 192), (214, 110, 140), 6)
    _ell(td, 505, 430, 118, 170, (246, 170, 192), (214, 110, 140), 6)
    f = (214, 110, 140)
    for sx in (1, -1):
        def X(v):
            return 400 + sx * (v - 400)
        for (a, b, c, d, s0, e0) in ((230, 300, 350, 410, 190, 350), (250, 390, 380, 520, 10, 170), (215, 440, 320, 560, 180, 330), (300, 270, 390, 340, 200, 340)):
            x0, x1 = sorted((X(a), X(c)))
            td.arc([x0 * S, b * S, x1 * S, d * S], s0 if sx == 1 else 180 - e0, e0 if sx == 1 else 180 - s0, fill=f, width=int(8 * S))
    _ln(td, [(400, 270), (400, 590)], (200, 90, 120), 7)
    for i in range(7):
        a = t * 2.5 + i * 1.9
        if math.sin(a) > 0.2:
            _ell(td, 400 + 150 * math.cos(i * 2.1) * (0.5 + 0.5 * math.sin(i)), 430 + 130 * math.sin(i * 1.7), 11, 11, (255, 240, 170))


def obj_ojo(ti, t):
    b = max(0.0, 1 - abs((t % 3.4) - 3.2) * 6)
    h = 125 * (1 - 0.92 * b)
    top = []
    bot = []
    for i in range(41):
        u = i / 40
        x = 150 + 500 * u
        yy = h * math.sin(math.pi * u) ** 0.9
        top.append((x, 430 - yy))
        bot.append((x, 430 + yy * 0.85))
    shape = top + bot[::-1]
    m = Image.new('L', ti.size, 0)
    _poly(ImageDraw.Draw(m), shape, 255)
    lay = Image.new('RGBA', ti.size, (250, 250, 252, 255))
    ld = ImageDraw.Draw(lay)
    dx = 24 * math.sin(t * 1.4)
    _ell(ld, 400 + dx, 430, 104, 104, (70, 150, 220), (30, 90, 160), 8)
    _ell(ld, 400 + dx, 430, 50 * (1 + 0.15 * math.sin(t * 2)), 50 * (1 + 0.15 * math.sin(t * 2)), (14, 16, 30))
    _ell(ld, 372 + dx, 398, 18, 18, (255, 255, 255))
    ti.paste(lay, (0, 0), m)
    td = ImageDraw.Draw(ti)
    _poly(td, shape, None, (50, 36, 46), 10)
    for i in range(3, 38, 5):
        x, y = top[i]
        _ln(td, [(x, y), (x - 6, y - 26)], (50, 36, 46), 7)


def obj_hueso(ti, t):
    ang = -38 + 4 * math.sin(t * 1.5)

    def dr(d):
        for (c, g) in (((205, 190, 160), 8), ((246, 238, 216), 0)):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    _ell(d, 400 + sx * 215, 430 + sy * 36, 46 + g, 46 + g, c)
            _rr(d, 230, 430 - 33 - g, 570, 430 + 33 + g, 20, c)
        _rr(d, 250, 405, 550, 417, 6, (255, 252, 240))
    _rot(ti, dr, ang)


def obj_craneo(ti, t):
    td = ImageDraw.Draw(ti)
    k = 4 * math.sin(t * 2)
    _ell(td, 400, 380 + k, 165, 170, (240, 238, 230), (190, 186, 176), 8)
    _rr(td, 315, 470 + k, 485, 580 + k, 34, (240, 238, 230), (190, 186, 176), 8)
    _ell(td, 340, 390 + k, 42, 48, (30, 30, 42))
    _ell(td, 460, 390 + k, 42, 48, (30, 30, 42))
    _poly(td, [(400, 440 + k), (378, 490 + k), (422, 490 + k)], (60, 58, 70))
    for i in range(5):
        _ln(td, [(348 + i * 26, 535 + k), (348 + i * 26, 580 + k)], (190, 186, 176), 5)


def obj_pulmon(ti, t):
    td = ImageDraw.Draw(ti)
    k = 1 + 0.06 * math.sin(t * 2.2)
    _rr(td, 386, 190, 414, 400, 12, (214, 218, 228))
    _ln(td, [(400, 390), (310, 450)], (214, 218, 228), 16)
    _ln(td, [(400, 390), (490, 450)], (214, 218, 228), 16)
    for sx in (-1, 1):
        cx = 400 + sx * 120 * k
        _ell(td, cx, 500, 118 * k, 190 * k, (240, 124, 150), (196, 80, 110), 7)
        _ell(td, cx - sx * 20, 470, 60 * k, 110 * k, (250, 160, 182))
        for j in range(3):
            _ln(td, [(400 + sx * 60, 440 + j * 40), (cx + sx * 20, 470 + j * 50)], (196, 80, 110), 6)


def obj_estomago(ti, t):
    td = ImageDraw.Draw(ti)
    k = 1 + 0.03 * math.sin(t * 2.6)
    _ln(td, [(345, 200), (350, 300), (370, 350)], (226, 112, 96), 44)
    _ln(td, [(520, 520), (620, 470), (660, 420)], (232, 150, 110), 34)
    _ell(td, 410, 480, 170 * k, 150 * k, (242, 150, 122), (200, 96, 78), 8)
    _ell(td, 340, 420, 100 * k, 110 * k, (246, 168, 140))
    for (a, b, c, d) in ((300, 430, 440, 520), (330, 470, 500, 560)):
        td.arc([a * S, b * S, c * S, d * S], 200, 340, fill=(200, 96, 78), width=int(7 * S))
    for i in range(4):
        ph = (t * 0.5 + i * 0.25) % 1
        _ell(td, 360 + i * 38 + 10 * math.sin(t * 3 + i), 560 - 170 * ph, 11, 11, (255, 255, 255, int(220 * (1 - ph))))


def obj_adn(ti, t):
    td = ImageDraw.Draw(ti)
    nodes = []
    for y in range(170, 700, 12):
        a = y / 55.0 + t * 2.2
        s = math.sin(a)
        c = math.cos(a)
        if (y // 12) % 3 == 0:
            _ln(td, [(400 + 130 * s, y), (400 - 130 * s, y)], (210, 226, 255, 170), 6)
        nodes.append((c, 400 + 130 * s, y, (255, 104, 150)))
        nodes.append((-c, 400 - 130 * s, y, (90, 200, 255)))
    nodes.sort(key=lambda n: n[0])
    for (z, x, y, col) in nodes:
        r = 11 + 4 * z
        _ell(td, x, y, r, r, col)


def obj_celula(ti, t):
    td = ImageDraw.Draw(ti)
    w = 6 * math.sin(t * 2)
    _ell(td, 400, 430, 215 + w, 195 - w, (110, 210, 140), (60, 150, 90), 10)
    _ell(td, 400, 430, 190 + w, 170 - w, (150, 232, 170))
    _ell(td, 405 + 8 * math.sin(t * 1.6), 425, 86, 80, (134, 92, 204), (96, 60, 160), 7)
    _ell(td, 420 + 8 * math.sin(t * 1.6), 410, 30, 28, (70, 40, 120))
    for (x, y, a) in ((270, 360, 0.5), (545, 500, -0.4), (300, 520, 0.9), (520, 340, -0.8)):
        _ell(td, x, y + 4 * math.sin(t * 2 + a), 38, 17, (250, 168, 70), (200, 110, 30), 4)
    for i in range(7):
        _ell(td, 260 + i * 46, 580 - 20 * math.sin(i * 1.3 + t), 7, 7, (240, 250, 200))


def obj_bacteria(ti, t):
    td = ImageDraw.Draw(ti)
    y = 430 + 10 * math.sin(t * 2.2)
    _rr(td, 210, y - 78, 560, y + 78, 78, (130, 206, 92), (66, 138, 54), 8)
    for (x, dy, r) in ((290, -20, 13), (370, 24, 17), (450, -18, 12), (500, 22, 14)):
        _ell(td, x, y + dy, r, r, (74, 130, 50))
    pts = [(560 + i * 8, y + 22 * math.sin(i * 0.5 - t * 7) * (i / 18)) for i in range(19)]
    _ln(td, pts, (66, 138, 54), 8)
    for i in range(8):
        a = i / 8 * 2 * math.pi
        x0 = 385 + 190 * math.cos(a) * 0.92
        y0 = y + 78 * math.sin(a) * 0.95
        _ln(td, [(x0, y0), (x0 + 22 * math.cos(a), y0 + 22 * math.sin(a))], (66, 138, 54), 5)


def obj_virus(ti, t):
    td = ImageDraw.Draw(ti)
    for i in range(16):
        a = i / 16 * 2 * math.pi + t * 0.5
        x0, y0 = 400 + 130 * math.cos(a), 430 + 130 * math.sin(a)
        x1, y1 = 400 + 188 * math.cos(a), 430 + 188 * math.sin(a)
        _ln(td, [(x0, y0), (x1, y1)], (255, 150, 100), 9)
        _ell(td, x1, y1, 16, 16, (255, 190, 90))
    _ell(td, 400, 430, 135, 135, (206, 60, 96), (140, 30, 60), 8)
    _ell(td, 355, 385, 44, 30, (240, 120, 150))
    for (x, y) in ((420, 470), (450, 400), (370, 480)):
        _ell(td, x, y, 14, 14, (150, 36, 70))


def obj_microscopio(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(td, 230, 640, 570, 692, 18, (90, 104, 140))
    td.arc([210 * S, 250 * S, 560 * S, 650 * S], 270, 95, fill=(70, 90, 160), width=int(38 * S))

    def tube(d):
        _rr(d, 360, 190, 440, 520, 14, (210, 216, 232), (120, 130, 160), 6)
        _rr(d, 372, 150, 428, 215, 10, (60, 66, 90))
        _rr(d, 380, 520, 420, 580, 8, (90, 100, 130))
    _rot(ti, tube, -18, 400, 430)
    td = ImageDraw.Draw(ti)
    _rr(td, 300, 585, 520, 605, 8, (120, 130, 160))
    _ell(td, 310, 540, 42, 42, (150, 160, 190), (80, 90, 120), 6)
    a = t * 3
    _ln(td, [(310, 540), (310 + 30 * math.cos(a), 540 + 30 * math.sin(a))], (60, 66, 90), 6)
    _ell(td, 445, 604, 9, 9, (255, 236, 150))


def obj_diente(ti, t):
    td = ImageDraw.Draw(ti)
    pts = [(300, 270), (360, 240), (400, 270), (440, 240), (500, 270), (545, 340), (525, 450), (505, 630), (455, 650), (428, 510), (400, 490), (372, 510), (345, 650), (295, 630), (275, 450), (255, 340)]
    _poly(td, pts, (252, 252, 254), (176, 190, 214), 9)
    td.arc([300 * S, 290 * S, 420 * S, 420 * S], 200, 290, fill=(214, 226, 244), width=int(10 * S))
    k = 0.5 + 0.5 * math.sin(t * 4)
    _spark(td, 540, 270, 14 + 18 * k)
    _spark(td, 270, 330, 8 + 12 * (1 - k))


def _gota(ti, t, col, dk):
    td = ImageDraw.Draw(ti)
    dy = 14 * math.sin(t * 3)
    pts = [(400, 190 + dy)]
    for i in range(0, 61):
        a = math.radians(-23.2 + 226.4 * i / 60)
        pts.append((400 + 135 * math.cos(a), 530 + dy + 135 * math.sin(a)))
    _poly(td, pts, col, dk, 8)
    _ell(td, 350, 500 + dy, 24, 44, (255, 255, 255, 150))


def obj_gota(ti, t):
    _gota(ti, t, (226, 36, 66), (150, 16, 40))


def obj_agua(ti, t):
    _gota(ti, t, (70, 160, 240), (30, 100, 190))


def obj_luna(ti, t):
    td = ImageDraw.Draw(ti)
    _ell(td, 400, 430, 190, 190, (255, 240, 170))
    _ell(td, 480, 390, 168, 168, (0, 0, 0, 0))
    for i, (x, y) in enumerate(((560, 250), (610, 400), (520, 560))):
        _spark(td, x, y, 10 + 8 * (0.5 + 0.5 * math.sin(t * 3 + i * 2)))
    for i in range(3):
        ph = (t * 0.4 + i * 0.33) % 1
        td.text(((470 + 50 * i) * S, (360 - 120 * ph) * S), 'Z', font=pfont(40 + 14 * i, True), fill=(255, 255, 255, int(255 * (1 - ph))), anchor='mm')


def obj_sol(ti, t):
    td = ImageDraw.Draw(ti)
    for i in range(12):
        a = i / 12 * 2 * math.pi + t * 0.6
        r0 = 150
        r1 = 205 + 14 * math.sin(t * 3 + i)
        _ln(td, [(400 + r0 * math.cos(a), 430 + r0 * math.sin(a)), (400 + r1 * math.cos(a), 430 + r1 * math.sin(a))], (255, 190, 40), 15)
    _ell(td, 400, 430, 125, 125, (255, 205, 60), (240, 160, 20), 8)
    _ell(td, 400, 430, 95, 95, (255, 232, 120))


def obj_arbol(ti, t):
    td = ImageDraw.Draw(ti)
    s = 6 * math.sin(t * 1.5)
    _ell(td, 400, 700, 190, 26, (60, 90, 70, 120))
    _poly(td, [(370, 700), (385, 470), (415, 470), (430, 700)], (132, 92, 62))
    for (x, y, r, c) in ((400, 330, 150, (70, 170, 100)), (300, 430, 105, (60, 156, 90)), (500, 430, 105, (60, 156, 90)), (400, 440, 120, (84, 186, 112))):
        _ell(td, x + s * (1 + (440 - y) / 200), y, r, r * 0.92, c)
    _ell(td, 350 + s, 300, 38, 24, (130, 214, 150))


def obj_libro(ti, t):
    td = ImageDraw.Draw(ti)
    _poly(td, [(160, 310), (400, 350), (640, 310), (640, 660), (400, 700), (160, 660)], (70, 100, 190))
    _poly(td, [(180, 300), (400, 340), (400, 640), (180, 600)], (250, 250, 252), (200, 204, 220), 4)
    _poly(td, [(400, 340), (620, 300), (620, 600), (400, 640)], (244, 244, 248), (200, 204, 220), 4)
    for i in range(6):
        _rr(td, 215, 380 + i * 36, 370, 392 + i * 36, 6, (190, 196, 214))
        _rr(td, 430, 372 + i * 36, 585, 384 + i * 36, 6, (190, 196, 214))
    c = math.cos((t * 1.1) % (2 * math.pi))
    _poly(td, [(400, 340), (400 + 220 * c, 300 + 10 * (1 - abs(c))), (400 + 220 * c, 600 + 10 * (1 - abs(c))), (400, 640)], (255, 255, 255), (200, 204, 220), 3)


def obj_taza(ti, t):
    td = ImageDraw.Draw(ti)
    _ell(td, 400, 650, 210, 36, (226, 222, 212))
    td.ellipse([500 * S, 440 * S, 630 * S, 570 * S], outline=(250, 245, 235), width=int(24 * S))
    _poly(td, [(250, 400), (550, 400), (520, 630), (280, 630)], (250, 245, 235), (210, 200, 186), 6)
    _ell(td, 400, 402, 150, 30, (110, 70, 50), (210, 200, 186), 6)
    for i in range(3):
        pts = []
        for j in range(20):
            pts.append((340 + i * 60 + 14 * math.sin(j * 0.6 + t * 3 + i), 380 - j * 9))
        _ln(td, pts, (255, 255, 255, 150), 9)


def obj_manzana(ti, t):
    td = ImageDraw.Draw(ti)
    b = 8 * abs(math.sin(t * 2.4))
    _ell(td, 340, 470 - b, 130, 160, (226, 60, 60), (160, 30, 40), 6)
    _ell(td, 460, 470 - b, 130, 160, (226, 60, 60), (160, 30, 40), 6)
    _ell(td, 400, 470 - b, 110, 150, (232, 70, 70))
    _ell(td, 330, 400 - b, 28, 52, (255, 150, 150))
    _ln(td, [(400, 330 - b), (412, 250 - b)], (120, 80, 50), 14)
    _poly(td, [(414, 280 - b), (490, 232 - b), (508, 284 - b), (440, 306 - b)], (80, 180, 96))


def obj_termometro(ti, t):
    td = ImageDraw.Draw(ti)
    lv = 0.5 + 0.5 * math.sin(t * 1.5)
    _rr(td, 365, 190, 435, 600, 35, (244, 246, 252), (150, 160, 186), 8)
    _ell(td, 400, 640, 78, 78, (230, 50, 70), (150, 20, 40), 7)
    y0 = 560 - 300 * lv
    _rr(td, 388, y0, 412, 620, 12, (230, 50, 70))
    for i in range(7):
        _ln(td, [(445, 240 + i * 52), (480 if i % 2 == 0 else 466, 240 + i * 52)], (150, 160, 186), 6)


def obj_pastilla(ti, t):
    def dr(d):
        _rr(d, 230, 360, 570, 500, 70, (250, 250, 252))
        _rr(d, 230, 360, 400, 500, 70, (226, 60, 70))
        d.rectangle([330 * S, 360 * S, 400 * S, 500 * S], fill=(226, 60, 70))
        _rr(d, 250, 378, 540, 396, 9, (255, 255, 255, 120))
    _rot(ti, dr, -35 + 6 * math.sin(t * 2))


_NUEVOS7 = {'corazon': obj_corazon, 'cerebro': obj_cerebro, 'ojo': obj_ojo, 'hueso': obj_hueso, 'craneo': obj_craneo, 'pulmon': obj_pulmon,
            'estomago': obj_estomago, 'adn': obj_adn, 'celula': obj_celula, 'bacteria': obj_bacteria, 'virus': obj_virus,
            'microscopio': obj_microscopio, 'diente': obj_diente, 'gota': obj_gota, 'agua': obj_agua, 'luna': obj_luna, 'sol': obj_sol,
            'arbol': obj_arbol, 'libro': obj_libro, 'taza': obj_taza, 'manzana': obj_manzana, 'termometro': obj_termometro,
            'pastilla': obj_pastilla}
_3.OBJETOS.update(_NUEVOS7)


def n_escena7(d, t, sc):
    _E.fijar(sc)
    # los objetos flotan suave despues de entrar (mas vida, sin zoom)
    capas = []
    for i, c in enumerate(sc['p'].get('capas', [])):
        if c.get('t', 'obj') in ('obj', 'icono', 'forma') and not c.get('mov') and c.get('objeto') != 'persona':
            t0 = cue(sc, c.get('cue'), 0.05)
            a = prog(t, t0 + 0.4, t0 + 1.0)
            ph = i * 1.7
            c = dict(c)
            c['x'] = float(c.get('x', 360)) + 5 * math.sin(t * 1.3 + ph) * a
            c['y'] = float(c.get('y', 480)) + 9 * math.sin(t * 1.9 + ph) * a
        capas.append(c)
    sc2 = dict(sc)
    sc2['p'] = dict(sc['p'])
    sc2['p']['capas'] = capas
    return n_escena6(d, t, sc2)


PLANTILLAS['escena'] = (n_escena7, _5.e_escena)