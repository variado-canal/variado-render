import math
import inspect

from PIL import Image, ImageDraw

import motion5 as _5
from motion5 import *
import motion4 as _4
import motion3 as _3


def _limbs(td, P_, t, mood, skin, sd, saco):
    acc = P_.get('accion', '')
    sw = math.sin(t * 9)
    T = _4._thick
    shoe = (60, 52, 70) if saco else (112, 84, 196)
    walk = acc in ('camina', 'corre')
    k = 34 if acc == 'corre' else 26
    lx = 338 + (k * sw if walk else 0)
    rx = 468 - (k * sw if walk else 0)
    ly = 745 - (16 * max(0, sw) if walk else 0)
    ry = 745 - (16 * max(0, -sw) if walk else 0)
    if walk:
        T(td, (345, 440), (300 - k * sw, 585), 40, sd)
        T(td, (455, 440), (500 + k * sw, 585), 40, sd)
    elif acc == 'paga':
        T(td, (345, 440), (300, 590), 40, sd)
        T(td, (455, 440), (570, 470), 40, sd)
        tx = 20 * math.sin(t * 5)
        td.ellipse([548 * S, 446 * S, 600 * S, 498 * S], fill=skin)
        td.rounded_rectangle([(590 + tx) * S, 440 * S, (676 + tx) * S, 492 * S], radius=10 * S, fill=(50, 100, 220))
        td.rectangle([(590 + tx) * S, 454 * S, (676 + tx) * S, 466 * S], fill=(20, 24, 60))
        td.rounded_rectangle([(602 + tx) * S, 474 * S, (622 + tx) * S, 486 * S], radius=3 * S, fill=(255, 205, 70))
    elif acc == 'piensa':
        T(td, (345, 440), (300, 590), 40, sd)
        T(td, (455, 440), (446, 398), 36, sd)
        td.ellipse([414 * S, 372 * S, 468 * S, 424 * S], fill=skin)
        for (bx, by, br) in ((540, 250, 14), (580, 200, 22), (640, 120, 62)):
            td.ellipse([(bx - br) * S, (by - br) * S, (bx + br) * S, (by + br) * S], fill=(255, 255, 255))
        td.text((640 * S, 122 * S), '?', font=pfont(80, True), fill=(40, 34, 20), anchor='mm')
    elif acc == 'cuenta':
        T(td, (345, 440), (330, 525), 40, sd)
        T(td, (455, 440), (470, 525), 40, sd)
        for i, a_ in enumerate((-16, 0, 16)):
            cx_ = 400 + a_ * 2
            td.polygon([((cx_ - 60) * S, 510 * S), ((cx_ + 60) * S, 510 * S), ((cx_ + 60 + a_) * S, 570 * S), ((cx_ - 60 + a_) * S, 570 * S)], fill=(90, 190, 120) if i != 1 else (120, 214, 150), outline=(30, 120, 70))
        td.ellipse([306 * S, 500 * S, 358 * S, 552 * S], fill=skin)
        td.ellipse([442 * S, 500 * S, 494 * S, 552 * S], fill=skin)
    elif mood == 'feliz':
        w = sw * 14
        T(td, (345, 430), (262 + w, 250), 40, sd)
        T(td, (455, 430), (538 - w, 250), 40, sd)
        for hx in (262 + w, 538 - w):
            td.ellipse([(hx - 28) * S, 222 * S, (hx + 28) * S, 278 * S], fill=skin)
    elif mood == 'senala':
        w = sw * 14
        T(td, (345, 440), (300, 590), 40, sd)
        T(td, (455, 430), (590, 300 + w), 40, sd)
        td.ellipse([562 * S, (272 + w) * S, 618 * S, (328 + w) * S], fill=skin)
    else:
        T(td, (345, 440), (300, 590), 40, sd)
        T(td, (455, 440), (500, 590), 40, sd)
    T(td, (368, 630), (lx, ly), 32, sd)
    T(td, (432, 630), (rx, ry), 32, sd)
    for (sx, sy) in ((lx, ly), (rx, ry)):
        td.ellipse([(sx - 38) * S, (sy - 45) * S, (sx + 38) * S, (sy + 31) * S], fill=shoe)
        if not saco:
            td.rounded_rectangle([(sx - 30) * S, (sy - 77) * S, (sx + 30) * S, (sy - 29) * S], radius=14 * S, fill=(238, 238, 240))


_src = inspect.getsource(_5.obj_persona2)
_a = _src.index('    w = math.sin')
_b = _src.index("    if estilo in ('largo', 'peluca'):\n        td.ellipse([282")
_src = _src[:_a] + '    _limbs(td, P_, t, mood, skin, sd, saco)\n' + _src[_b:]
_src = _src.replace('def obj_persona2', 'def obj_persona3')
_g = dict(vars(_5))
_g['_limbs'] = _limbs
exec(_src, _g)
obj_persona3 = _g['obj_persona3']


def _rr(ti, x0, y0, x1, y1, r, c1, c2=None):
    grad_rr(ti, x0, y0, x1, y1, r, c1, c2 or tuple(int(v * 0.8) for v in c1), diag=False)


def obj_tienda(ti, t):
    td = ImageDraw.Draw(ti)
    td.rectangle([180 * S, 360 * S, 620 * S, 660 * S], fill=(246, 240, 228))
    for i in range(8):
        td.polygon([((160 + i * 60) * S, 270 * S), ((220 + i * 60) * S, 270 * S), ((230 + i * 60) * S, 380 * S), ((150 + i * 60) * S, 380 * S)], fill=(226, 70, 70) if i % 2 == 0 else (250, 250, 252))
    td.rounded_rectangle([320 * S, 190 * S, 480 * S, 250 * S], radius=12 * S, fill=(40, 44, 60))
    td.text((400 * S, 220 * S), 'TIENDA', font=pfont(34, True), fill=(255, 255, 255), anchor='mm')
    td.rectangle([210 * S, 420 * S, 360 * S, 600 * S], fill=(150, 210, 240), outline=(255, 255, 255), width=int(6 * S))
    td.rectangle([410 * S, 470 * S, 580 * S, 660 * S], fill=(120, 80, 60))
    td.ellipse([555 * S, 560 * S, 569 * S, 574 * S], fill=(255, 210, 80))


def obj_cajero(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(ti, 220, 150, 580, 700, 36, (70, 84, 120))
    td.rounded_rectangle([260 * S, 200 * S, 540 * S, 360 * S], radius=18 * S, fill=(20, 28, 44))
    td.text((400 * S, 280 * S), '$ 0000', font=pfont(54, True), fill=(90, 230, 150), anchor='mm')
    td.rounded_rectangle([280 * S, 410 * S, 520 * S, 440 * S], radius=8 * S, fill=(14, 16, 24))
    for r in range(2):
        for c in range(3):
            td.rounded_rectangle([(290 + c * 70) * S, (480 + r * 60) * S, (340 + c * 70) * S, (520 + r * 60) * S], radius=8 * S, fill=(190, 196, 214))
    k = 20 * max(0, math.sin(t * 3))
    td.rounded_rectangle([300 * S, (610) * S, 500 * S, (640 + k) * S], radius=8 * S, fill=(90, 190, 120))


def obj_barco(ti, t):
    td = ImageDraw.Draw(ti)
    b = 8 * math.sin(t * 2)
    td.polygon([(130 * S, (500 + b) * S), (670 * S, (500 + b) * S), (590 * S, (620 + b) * S), (210 * S, (620 + b) * S)], fill=(226, 70, 70))
    td.rectangle([160 * S, (480 + b) * S, 640 * S, (510 + b) * S], fill=(240, 242, 248))
    td.rectangle([250 * S, (400 + b) * S, 550 * S, (480 + b) * S], fill=(246, 246, 250))
    td.rectangle([330 * S, (330 + b) * S, 470 * S, (400 + b) * S], fill=(240, 242, 248))
    td.rectangle([385 * S, (260 + b) * S, 415 * S, (330 + b) * S], fill=(190, 60, 60))
    for i in range(5):
        td.ellipse([(270 + i * 56) * S, (420 + b) * S, (300 + i * 56) * S, (450 + b) * S], fill=(120, 190, 240))
    td.rectangle([0, 0, 1, 1], fill=None)
    for i in range(6):
        td.arc([(100 + i * 100) * S, 590 * S, (200 + i * 100) * S, 650 * S], 200, 340, fill=(160, 220, 255), width=int(8 * S))


def obj_avion(ti, t):
    td = ImageDraw.Draw(ti)
    td.polygon([(120 * S, 420 * S), (620 * S, 380 * S), (700 * S, 420 * S), (620 * S, 460 * S), (160 * S, 470 * S)], fill=(240, 242, 248))
    td.polygon([(380 * S, 420 * S), (300 * S, 250 * S), (360 * S, 250 * S), (500 * S, 410 * S)], fill=(200, 206, 222))
    td.polygon([(380 * S, 450 * S), (300 * S, 600 * S), (360 * S, 600 * S), (500 * S, 460 * S)], fill=(176, 184, 204))
    td.polygon([(120 * S, 420 * S), (90 * S, 320 * S), (150 * S, 330 * S), (210 * S, 420 * S)], fill=(226, 70, 70))
    for i in range(5):
        td.ellipse([(450 + i * 30) * S, 408 * S, (470 + i * 30) * S, 428 * S], fill=(120, 190, 240))


def obj_hucha(ti, t):
    td = ImageDraw.Draw(ti)
    td.ellipse([180 * S, 300 * S, 600 * S, 640 * S], fill=(244, 150, 170))
    td.ellipse([540 * S, 380 * S, 680 * S, 500 * S], fill=(244, 150, 170))
    td.ellipse([620 * S, 420 * S, 640 * S, 440 * S], fill=(120, 40, 60))
    td.ellipse([650 * S, 420 * S, 670 * S, 440 * S], fill=(120, 40, 60))
    td.polygon([(300 * S, 320 * S), (340 * S, 250 * S), (390 * S, 320 * S)], fill=(230, 120, 146))
    td.ellipse([480 * S, 360 * S, 508 * S, 388 * S], fill=(60, 20, 34))
    td.rounded_rectangle([320 * S, 305 * S, 440 * S, 325 * S], radius=8 * S, fill=(120, 40, 60))
    for lx in (250, 460):
        td.rounded_rectangle([lx * S, 600 * S, (lx + 60) * S, 690 * S], radius=14 * S, fill=(230, 120, 146))
    d_ = (t * 1.2) % 1
    td.ellipse([350 * S, (170 + 140 * d_) * S, 410 * S, (230 + 140 * d_) * S], fill=(255, 205, 70), outline=(214, 150, 20), width=int(4 * S))


def obj_caja_fuerte(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(ti, 180, 200, 620, 660, 30, (96, 106, 130))
    _rr(ti, 220, 240, 580, 620, 22, (130, 142, 168))
    td.ellipse([340 * S, 340 * S, 500 * S, 500 * S], fill=(210, 214, 226), outline=(60, 66, 84), width=int(8 * S))
    a = t * 2
    td.line([(420 * S, 420 * S), ((420 + 60 * math.cos(a)) * S, (420 + 60 * math.sin(a)) * S)], fill=(60, 66, 84), width=int(10 * S))
    td.rectangle([250 * S, 300 * S, 290 * S, 340 * S], fill=(255, 205, 70))
    td.rectangle([250 * S, 520 * S, 290 * S, 560 * S], fill=(255, 205, 70))


def obj_calendario(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(ti, 170, 200, 630, 660, 30, (250, 250, 252), (226, 228, 236))
    td.rounded_rectangle([170 * S, 200 * S, 630 * S, 310 * S], radius=30 * S, fill=(226, 70, 70))
    td.rectangle([170 * S, 270 * S, 630 * S, 310 * S], fill=(226, 70, 70))
    for rx in (260, 540):
        td.rounded_rectangle([(rx - 12) * S, 170 * S, (rx + 12) * S, 240 * S], radius=10 * S, fill=(60, 66, 84))
    for r in range(4):
        for c in range(5):
            x = 205 + c * 78
            y = 345 + r * 78
            hot = (r, c) == (2, 3)
            td.rounded_rectangle([x * S, y * S, (x + 56) * S, (y + 56) * S], radius=10 * S, fill=(255, 205, 70) if hot else (236, 238, 246))
    td.ellipse([(205 + 3 * 78 - 8) * S, (345 + 2 * 78 - 8) * S, (205 + 3 * 78 + 64) * S, (345 + 2 * 78 + 64) * S], outline=(226, 70, 70), width=int(6 * S))


def obj_contrato(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(ti, 210, 160, 590, 690, 18, (250, 250, 252), (226, 228, 236))
    for i in range(7):
        w = 300 if i % 3 else 220
        td.rounded_rectangle([250 * S, (220 + i * 52) * S, (250 + w) * S, (236 + i * 52) * S], radius=6 * S, fill=(190, 196, 214))
    td.line([(270 * S, 640 * S), (330 * S, 600 * S), (380 * S, 650 * S), (440 * S, 590 * S)], fill=(50, 100, 220), width=int(8 * S), joint='curve')
    td.ellipse([480 * S, 560 * S, 560 * S, 640 * S], fill=(226, 70, 70))


def obj_balanza(ti, t):
    td = ImageDraw.Draw(ti)
    tilt = 10 * math.sin(t * 1.6)
    td.rectangle([390 * S, 200 * S, 410 * S, 640 * S], fill=(150, 156, 176))
    td.rounded_rectangle([300 * S, 630 * S, 500 * S, 670 * S], radius=14 * S, fill=(110, 116, 136))
    td.line([(180 * S, (280 - tilt) * S), (620 * S, (280 + tilt) * S)], fill=(214, 150, 20), width=int(14 * S))
    for (px, py, c) in ((180, 280 - tilt, (255, 205, 70)), (620, 280 + tilt, (90, 190, 120))):
        td.line([(px * S, py * S), ((px - 60) * S, (py + 190) * S)], fill=(190, 196, 214), width=int(5 * S))
        td.line([(px * S, py * S), ((px + 60) * S, (py + 190) * S)], fill=(190, 196, 214), width=int(5 * S))
        td.pieslice([(px - 90) * S, (py + 120) * S, (px + 90) * S, (py + 260) * S], 0, 180, fill=c)


def obj_trofeo(ti, t):
    td = ImageDraw.Draw(ti)
    td.arc([180 * S, 240 * S, 360 * S, 440 * S], 90, 270, fill=(214, 150, 20), width=int(18 * S))
    td.arc([440 * S, 240 * S, 620 * S, 440 * S], 270, 90, fill=(214, 150, 20), width=int(18 * S))
    td.pieslice([270 * S, 150 * S, 530 * S, 540 * S], 0, 180, fill=(255, 205, 70))
    td.rectangle([270 * S, 340 * S, 530 * S, 346 * S], fill=(255, 205, 70))
    td.rectangle([375 * S, 450 * S, 425 * S, 580 * S], fill=(214, 150, 20))
    td.rounded_rectangle([300 * S, 570 * S, 500 * S, 640 * S], radius=14 * S, fill=(120, 80, 60))
    td.rounded_rectangle([335 * S, 590 * S, 465 * S, 620 * S], radius=8 * S, fill=(255, 205, 70))


def obj_etiqueta(ti, t):
    td = ImageDraw.Draw(ti)
    td.polygon([(180 * S, 400 * S), (330 * S, 230 * S), (620 * S, 230 * S), (620 * S, 570 * S), (330 * S, 570 * S)], fill=(255, 205, 70))
    td.ellipse([290 * S, 370 * S, 350 * S, 430 * S], fill=(250, 250, 252))
    td.text((480 * S, 400 * S), '%', font=pfont(160, True), fill=(40, 34, 20), anchor='mm')


def obj_llama(ti, t):
    td = ImageDraw.Draw(ti)
    f = 14 * math.sin(t * 9)
    td.polygon([(400 * S, (150 + f) * S), (560 * S, 430 * S), (520 * S, 600 * S), (400 * S, 680 * S), (280 * S, 600 * S), (240 * S, 430 * S)], fill=(255, 130, 40))
    td.polygon([(400 * S, (270 + f) * S), (500 * S, 470 * S), (470 * S, 600 * S), (400 * S, 650 * S), (330 * S, 600 * S), (300 * S, 470 * S)], fill=(255, 205, 70))
    td.polygon([(400 * S, (420 + f) * S), (450 * S, 540 * S), (400 * S, 620 * S), (350 * S, 540 * S)], fill=(255, 244, 190))


def obj_rayo(ti, t):
    td = ImageDraw.Draw(ti)
    td.polygon([(460 * S, 130 * S), (250 * S, 430 * S), (390 * S, 430 * S), (320 * S, 690 * S), (570 * S, 360 * S), (430 * S, 360 * S)], fill=(255, 205, 70), outline=(214, 150, 20), width=int(8 * S))


def obj_ladron(ti, t):
    td = ImageDraw.Draw(ti)
    td.ellipse([260 * S, 160 * S, 540 * S, 440 * S], fill=(214, 150, 110))
    td.rounded_rectangle([250 * S, 270 * S, 550 * S, 360 * S], radius=20 * S, fill=(30, 30, 40))
    for ex in (340, 460):
        td.ellipse([(ex - 22) * S, 295 * S, (ex + 22) * S, 335 * S], fill=(250, 250, 252))
        td.ellipse([(ex - 8) * S, 306 * S, (ex + 8) * S, 326 * S], fill=(30, 30, 40))
    td.rectangle([270 * S, 170 * S, 530 * S, 215 * S], fill=(30, 30, 40))
    td.rounded_rectangle([200 * S, 440 * S, 600 * S, 700 * S], radius=60 * S, fill=(30, 30, 40))
    for i in range(5):
        td.rectangle([(230 + i * 70) * S, (470) * S, (260 + i * 70) * S, 700 * S], fill=(250, 250, 252) if i % 2 == 0 else (30, 30, 40))
    td.rounded_rectangle([330 * S, 560 * S, 470 * S, 640 * S], radius=14 * S, fill=(176, 120, 70))
    td.text((400 * S, 600 * S), '$', font=pfont(60, True), fill=(255, 238, 190), anchor='mm')


def obj_laptop(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(ti, 180, 230, 620, 540, 24, (60, 66, 86))
    td.rounded_rectangle([204 * S, 252 * S, 596 * S, 518 * S], radius=12 * S, fill=(20, 28, 44))
    pts = [(230, 460), (290, 420), (340, 440), (400, 360), (460, 380), (560, 290)]
    td.line([(x * S, y * S) for x, y in pts], fill=(90, 230, 150), width=int(8 * S), joint='curve')
    td.rounded_rectangle([130 * S, 540 * S, 670 * S, 580 * S], radius=14 * S, fill=(150, 156, 176))
    td.rounded_rectangle([330 * S, 540 * S, 470 * S, 556 * S], radius=6 * S, fill=(110, 116, 136))


def obj_lluvia(ti, t):
    td = ImageDraw.Draw(ti)
    for i in range(14):
        ph = (t * 0.7 + i * 0.137) % 1
        x = 120 + (i * 97) % 560
        y = 100 + ph * 620
        ang = math.sin(t * 3 + i) * 0.4
        if i % 2:
            td.ellipse([(x - 34) * S, (y - 34) * S, (x + 34) * S, (y + 34) * S], fill=(255, 205, 70), outline=(214, 150, 20), width=int(5 * S))
            td.text((x * S, y * S), '$', font=pfont(36, True), fill=(214, 150, 20), anchor='mm')
        else:
            c = math.cos(ang) * 52
            s = math.sin(ang) * 52
            td.polygon([((x - c) * S, (y - s - 28) * S), ((x + c) * S, (y + s - 28) * S), ((x + c) * S, (y + s + 28) * S), ((x - c) * S, (y - s + 28) * S)], fill=(90, 190, 120), outline=(30, 120, 70))
            td.ellipse([(x - 14) * S, (y - 14) * S, (x + 14) * S, (y + 14) * S], fill=(150, 230, 170))


def obj_globo(ti, t):
    td = ImageDraw.Draw(ti)
    td.ellipse([180 * S, 180 * S, 620 * S, 620 * S], fill=(70, 150, 240))
    for (x, y, w, h) in ((260, 260, 150, 100), (430, 330, 130, 150), (280, 440, 110, 90)):
        td.ellipse([x * S, y * S, (x + w) * S, (y + h) * S], fill=(90, 200, 130))
    td.arc([180 * S, 180 * S, 620 * S, 620 * S], 0, 360, fill=(220, 240, 255), width=int(8 * S))
    td.arc([260 * S, 180 * S, 540 * S, 620 * S], 0, 360, fill=(150, 200, 250), width=int(4 * S))
    td.line([(180 * S, 400 * S), (620 * S, 400 * S)], fill=(150, 200, 250), width=int(4 * S))


def obj_bitcoin(ti, t):
    td = ImageDraw.Draw(ti)
    k = abs(math.cos(t * 2.4)) * 0.7 + 0.3
    td.ellipse([(400 - 220 * k) * S, 180 * S, (400 + 220 * k) * S, 620 * S], fill=(247, 147, 26), outline=(200, 110, 10), width=int(10 * S))
    if k > 0.55:
        td.text((400 * S, 400 * S), 'B', font=pfont(int(260 * k), True), fill=(255, 244, 220), anchor='mm')


def obj_escudo(ti, t):
    td = ImageDraw.Draw(ti)
    td.polygon([(400 * S, 160 * S), (610 * S, 240 * S), (590 * S, 470 * S), (400 * S, 680 * S), (210 * S, 470 * S), (190 * S, 240 * S)], fill=(50, 100, 220), outline=(220, 232, 255), width=int(10 * S))
    td.line([(300 * S, 410 * S), (375 * S, 490 * S), (510 * S, 330 * S)], fill=(255, 255, 255), width=int(26 * S), joint='curve')


def obj_pastel(ti, t):
    td = ImageDraw.Draw(ti)
    td.ellipse([180 * S, 180 * S, 620 * S, 620 * S], fill=(240, 242, 248))
    td.pieslice([180 * S, 180 * S, 620 * S, 620 * S], -90, 30, fill=(226, 70, 70))
    td.pieslice([180 * S, 180 * S, 620 * S, 620 * S], 30, 150, fill=(255, 205, 70))
    td.pieslice([180 * S, 180 * S, 620 * S, 620 * S], 150, 270, fill=(50, 100, 220))


def obj_mapa(ti, t):
    td = ImageDraw.Draw(ti)
    _rr(ti, 140, 260, 660, 640, 20, (250, 244, 226), (232, 224, 196))
    td.line([(180 * S, 580 * S), (300 * S, 420 * S), (440 * S, 500 * S), (580 * S, 340 * S)], fill=(226, 70, 70), width=int(8 * S), joint='curve')
    td.text((580 * S, 330 * S), 'X', font=pfont(70, True), fill=(226, 70, 70), anchor='mm')
    td.ellipse([380 * S, 130 * S, 460 * S, 210 * S], fill=(226, 70, 70))
    td.polygon([(380 * S, 190 * S), (460 * S, 190 * S), (420 * S, 260 * S)], fill=(226, 70, 70))
    td.ellipse([408 * S, 158 * S, 432 * S, 182 * S], fill=(255, 255, 255))


_NUEVOS = {'persona': obj_persona3, 'tienda': obj_tienda, 'cajero': obj_cajero, 'barco': obj_barco, 'avion': obj_avion, 'hucha': obj_hucha,
           'caja_fuerte': obj_caja_fuerte, 'calendario': obj_calendario, 'contrato': obj_contrato, 'balanza': obj_balanza, 'trofeo': obj_trofeo,
           'etiqueta': obj_etiqueta, 'llama': obj_llama, 'rayo': obj_rayo, 'ladron': obj_ladron, 'laptop': obj_laptop, 'lluvia': obj_lluvia,
           'globo': obj_globo, 'bitcoin': obj_bitcoin, 'escudo': obj_escudo, 'pastel': obj_pastel, 'mapa': obj_mapa}
_3.OBJETOS.update(_NUEVOS)
_3.OBJETOS['personaje'] = obj_persona3
_3.ESTATICOS = tuple(_3.ESTATICOS) + ('tienda', 'contrato', 'trofeo', 'etiqueta', 'rayo', 'ladron', 'escudo', 'pastel', 'mapa')


def n_escena6(d, t, sc):
    capas = []
    for c in sc['p'].get('capas', []):
        m = c.get('mov')
        if m:
            t0 = cue(sc, c.get('cue'), 0.05)
            pr = e_out(prog(t, t0, t0 + float(m.get('dur', 2.0))))
            x0, y0 = m['de']
            x1, y1 = m['a']
            c = dict(c)
            c['x'] = x0 + (x1 - x0) * pr
            c['y'] = y0 + (y1 - y0) * pr
        capas.append(c)
    sc2 = dict(sc)
    sc2['p'] = dict(sc['p'])
    sc2['p']['capas'] = capas
    return _5.n_escena(d, t, sc2)


PLANTILLAS['escena'] = (n_escena6, _5.e_escena)

