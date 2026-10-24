import math

from PIL import Image, ImageDraw, ImageFilter

import motion4 as _4
from motion4 import *
import motion3 as _3

_PAL = {
    'piel': {'claro': (238, 192, 152), 'medio': (214, 150, 100), 'moreno': (204, 112, 52), 'oscuro': (150, 92, 62)},
    'pelo': {'negro': (34, 26, 32), 'castano': (96, 54, 40), 'blanco': (238, 238, 242), 'gris': (176, 176, 186), 'rubio': (236, 194, 92), 'rojo': (196, 76, 44), 'marron': (74, 30, 42)},
    'ropa': {'verde': (24, 178, 146), 'azul': (50, 100, 220), 'rojo': (226, 70, 70), 'amarillo': (250, 200, 50), 'negro': (36, 38, 48), 'gris': (110, 116, 132), 'blanco': (240, 240, 244), 'morado': (120, 80, 200), 'naranja': (240, 130, 40), 'marino': (36, 46, 110)},
}


def _c(tab, v, dflt):
    if isinstance(v, (list, tuple)):
        return tuple(v)
    return _PAL[tab].get(v, dflt)


def _dk(c, k=0.82):
    return tuple(int(x * k) for x in c)


def obj_persona2(ti, t):
    P_ = _4._PP
    td = ImageDraw.Draw(ti)
    mood = P_.get('animo', 'feliz')
    skin = _c('piel', P_.get('piel'), (204, 112, 52))
    hair = _c('pelo', P_.get('pelo'), (74, 30, 42))
    top = _c('ropa', P_.get('camisa'), (24, 178, 146))
    pants = _c('ropa', P_.get('pantalon'), (36, 46, 110))
    estilo = P_.get('peinado', 'afro')
    saco = P_.get('ropa') == 'saco'
    sd = _dk(skin)
    w = math.sin(t * 6) * 14
    if mood == 'feliz':
        _4._thick(td, (345, 430), (262 + w, 250), 40, sd)
        _4._thick(td, (455, 430), (538 - w, 250), 40, sd)
        for hx in (262 + w, 538 - w):
            td.ellipse([(hx - 28) * S, 222 * S, (hx + 28) * S, 278 * S], fill=skin)
    elif mood == 'senala':
        _4._thick(td, (345, 440), (300, 590), 40, sd)
        _4._thick(td, (455, 430), (590, 300 + w), 40, sd)
        td.ellipse([562 * S, (272 + w) * S, 618 * S, (328 + w) * S], fill=skin)
    else:
        _4._thick(td, (345, 440), (300, 590), 40, sd)
        _4._thick(td, (455, 440), (500, 590), 40, sd)
    _4._thick(td, (368, 630), (338, 745), 32, sd)
    _4._thick(td, (432, 630), (468, 745), 32, sd)
    for sx in (336, 470):
        td.ellipse([(sx - 38) * S, 700 * S, (sx + 38) * S, 776 * S], fill=(60, 52, 70) if saco else (112, 84, 196))
        if not saco:
            td.rounded_rectangle([(sx - 30) * S, 668 * S, (sx + 30) * S, 716 * S], radius=14 * S, fill=(238, 238, 240))
    if estilo in ('largo', 'peluca'):
        td.ellipse([282 * S, 190 * S, 518 * S, 470 * S], fill=hair)
    jk = (44, 48, 66) if saco else top
    grad_rr(ti, 335, 400, 465, 540, 40, jk, _dk(jk, 0.8), diag=False)
    td.ellipse([308 * S, 396 * S, 372 * S, 470 * S], fill=_dk(jk, 0.94))
    td.ellipse([428 * S, 396 * S, 492 * S, 470 * S], fill=_dk(jk, 0.78))
    if saco:
        td.polygon([(372 * S, 400 * S), (428 * S, 400 * S), (400 * S, 470 * S)], fill=(244, 244, 248))
        td.polygon([(394 * S, 420 * S), (406 * S, 420 * S), (410 * S, 500 * S), (400 * S, 512 * S), (390 * S, 500 * S)], fill=(214, 64, 64))
    else:
        td.rectangle([338 * S, 534 * S, 462 * S, 556 * S], fill=(238, 84, 84))
    grad_rr(ti, 336, 552, 464, 640, 30, pants, _dk(pants, 0.8), diag=False)
    if estilo == 'afro':
        ov = Image.new('RGBA', ti.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.ellipse([(400 - 110) * S, 105 * S, (400 + 110) * S, 305 * S], fill=hair + (255,))
        for (hx, hy) in ((250, 160), (300, 110), (400, 85), (500, 110), (550, 160)):
            od.ellipse([(hx - 70) * S, (hy - 52) * S, (hx + 70) * S, (hy + 52) * S], fill=hair + (255,))
        ti.alpha_composite(ov)
        td = ImageDraw.Draw(ti)
    td.ellipse([(400 - 92) * S, (330 - 94) * S, (400 + 92) * S, (330 + 94) * S], fill=skin)
    if estilo in ('afro', 'corto', 'largo', 'peluca'):
        td.pieslice([(400 - 100) * S, (330 - 108) * S, (400 + 100) * S, (330 + 62) * S], 180, 360, fill=hair)
    if estilo in ('largo', 'peluca'):
        for cx_, cy_ in ((296, 400), (504, 400), (292, 450), (508, 450)):
            td.ellipse([(cx_ - 30) * S, (cy_ - 30) * S, (cx_ + 30) * S, (cy_ + 30) * S], fill=hair)
    ink = (60, 22, 30)
    for ex in (356, 444):
        if mood in ('feliz',):
            td.arc([(ex - 20) * S, 318 * S, (ex + 20) * S, 352 * S], 200, 340, fill=ink, width=int(7 * S))
        elif mood == 'triste':
            td.arc([(ex - 20) * S, 330 * S, (ex + 20) * S, 360 * S], 20, 160, fill=ink, width=int(7 * S))
        else:
            td.ellipse([(ex - 9) * S, 326 * S, (ex + 9) * S, 346 * S], fill=ink)
    for bx in (330, 470):
        td.ellipse([(bx - 22) * S, 346 * S, (bx + 22) * S, 380 * S], fill=(244, 98, 98) if mood in ('feliz', 'senala') else (206, 96, 76))
    if mood == 'feliz':
        td.ellipse([380 * S, 362 * S, 420 * S, 394 * S], fill=(80, 20, 44))
        td.ellipse([388 * S, 378 * S, 412 * S, 394 * S], fill=(240, 110, 130))
    elif mood == 'triste':
        td.arc([380 * S, 372 * S, 420 * S, 400 * S], 200, 340, fill=(80, 20, 44), width=int(6 * S))
        td.ellipse([462 * S, 372 * S, 478 * S, 400 * S], fill=(120, 190, 255))
    elif mood == 'sorpresa':
        td.ellipse([386 * S, 366 * S, 414 * S, 398 * S], fill=(80, 20, 44))
    else:
        td.arc([376 * S, 360 * S, 424 * S, 392 * S], 20, 160, fill=(80, 20, 44), width=int(6 * S))


def obj_pila(ti, t):
    td = ImageDraw.Draw(ti)
    for (cx_, n) in ((250, 4), (400, 7), (550, 5)):
        for i in range(n):
            y = 640 - i * 34
            td.ellipse([(cx_ - 80) * S, (y - 22) * S, (cx_ + 80) * S, (y + 22) * S], fill=(214, 150, 20))
            td.rectangle([(cx_ - 80) * S, (y - 4) * S, (cx_ + 80) * S, (y + 2) * S], fill=(214, 150, 20))
            td.ellipse([(cx_ - 80) * S, (y - 34) * S, (cx_ + 80) * S, (y + 10) * S], fill=(255, 205, 70), outline=(214, 150, 20), width=int(3 * S))
    td.text((400 * S, 410 * S), '$', font=pfont(70, True), fill=(214, 150, 20), anchor='mm')


def obj_bolsa(ti, t):
    td = ImageDraw.Draw(ti)
    td.polygon([(300 * S, 260 * S), (500 * S, 260 * S), (470 * S, 330 * S), (330 * S, 330 * S)], fill=(176, 120, 70))
    td.ellipse([200 * S, 310 * S, 600 * S, 700 * S], fill=(196, 140, 84))
    td.ellipse([240 * S, 330 * S, 420 * S, 520 * S], fill=(214, 160, 104))
    td.rounded_rectangle([320 * S, 300 * S, 480 * S, 340 * S], radius=14 * S, fill=(226, 84, 70))
    td.text((400 * S, 520 * S), '$', font=pfont(170, True), fill=(255, 238, 190), anchor='mm')


def obj_casa(ti, t):
    td = ImageDraw.Draw(ti)
    td.rectangle([200 * S, 380 * S, 600 * S, 660 * S], fill=(246, 240, 228))
    td.polygon([(160 * S, 390 * S), (400 * S, 190 * S), (640 * S, 390 * S)], fill=(214, 72, 64))
    td.rectangle([350 * S, 500 * S, 450 * S, 660 * S], fill=(120, 80, 60))
    td.ellipse([430 * S, 574 * S, 442 * S, 586 * S], fill=(255, 210, 80))
    for wx in (240, 480):
        td.rectangle([wx * S, 440 * S, (wx + 80) * S, 520 * S], fill=(120, 190, 240), outline=(255, 255, 255), width=int(6 * S))
    td.rectangle([520 * S, 230 * S, 560 * S, 330 * S], fill=(170, 60, 56))


def obj_auto(ti, t):
    td = ImageDraw.Draw(ti)
    td.rounded_rectangle([110 * S, 400 * S, 690 * S, 560 * S], radius=40 * S, fill=(226, 70, 70))
    td.polygon([(240 * S, 400 * S), (300 * S, 300 * S), (500 * S, 300 * S), (580 * S, 400 * S)], fill=(206, 56, 56))
    td.polygon([(268 * S, 392 * S), (314 * S, 320 * S), (390 * S, 320 * S), (390 * S, 392 * S)], fill=(170, 220, 250))
    td.polygon([(410 * S, 392 * S), (410 * S, 320 * S), (492 * S, 320 * S), (550 * S, 392 * S)], fill=(170, 220, 250))
    for wx in (240, 560):
        td.ellipse([(wx - 56) * S, 500 * S, (wx + 56) * S, 612 * S], fill=(34, 34, 40))
        td.ellipse([(wx - 26) * S, 530 * S, (wx + 26) * S, 582 * S], fill=(190, 192, 202))
    td.ellipse([650 * S, 430 * S, 690 * S, 470 * S], fill=(255, 226, 120))


def obj_carrito(ti, t):
    td = ImageDraw.Draw(ti)
    td.line([(110 * S, 250 * S), (200 * S, 250 * S), (270 * S, 500 * S), (600 * S, 500 * S)], fill=(230, 232, 240), width=int(16 * S), joint='curve')
    td.polygon([(228 * S, 320 * S), (680 * S, 320 * S), (620 * S, 500 * S), (270 * S, 500 * S)], fill=(60, 140, 240))
    for i in range(1, 4):
        td.line([((228 + i * 100) * S, 330 * S), ((270 + i * 85) * S, 490 * S)], fill=(150, 200, 255), width=int(6 * S))
    for wx in (320, 560):
        td.ellipse([(wx - 32) * S, 560 * S, (wx + 32) * S, 624 * S], fill=(34, 34, 40))


def obj_cohete(ti, t):
    td = ImageDraw.Draw(ti)
    f = 30 * math.sin(t * 18)
    td.polygon([(340 * S, 560 * S), (460 * S, 560 * S), (400 * S, (730 + f) * S)], fill=(255, 170, 40))
    td.polygon([(360 * S, 560 * S), (440 * S, 560 * S), (400 * S, (680 + f) * S)], fill=(255, 230, 110))
    td.polygon([(300 * S, 470 * S), (230 * S, 600 * S), (320 * S, 560 * S)], fill=(226, 70, 70))
    td.polygon([(500 * S, 470 * S), (570 * S, 600 * S), (480 * S, 560 * S)], fill=(226, 70, 70))
    td.ellipse([310 * S, 140 * S, 490 * S, 580 * S], fill=(240, 242, 248))
    td.polygon([(330 * S, 250 * S), (400 * S, 110 * S), (470 * S, 250 * S)], fill=(226, 70, 70))
    td.ellipse([356 * S, 330 * S, 444 * S, 418 * S], fill=(90, 170, 240), outline=(120, 124, 140), width=int(8 * S))


def obj_alerta(ti, t):
    td = ImageDraw.Draw(ti)
    k = 1 + 0.05 * math.sin(t * 8)
    td.polygon([(400 * S, (170 - 10 * k) * S), (660 * S, 620 * S), (140 * S, 620 * S)], fill=(255, 205, 40), outline=(40, 34, 20), width=int(14 * S))
    td.rounded_rectangle([382 * S, 300 * S, 418 * S, 480 * S], radius=14 * S, fill=(40, 34, 20))
    td.ellipse([380 * S, 510 * S, 420 * S, 550 * S], fill=(40, 34, 20))


def obj_burbuja(ti, t):
    td = ImageDraw.Draw(ti)
    r = 220 + 8 * math.sin(t * 3)
    td.ellipse([(400 - r) * S, (400 - r) * S, (400 + r) * S, (400 + r) * S], fill=(120, 200, 255, 90), outline=(220, 244, 255), width=int(8 * S))
    td.ellipse([(400 - r * 0.62) * S, (400 - r * 0.72) * S, (400 - r * 0.3) * S, (400 - r * 0.44) * S], fill=(255, 255, 255, 160))
    td.text((400 * S, 410 * S), '$', font=pfont(200, True), fill=(255, 255, 255, 220), anchor='mm')


def obj_baja(ti, t):
    td = ImageDraw.Draw(ti)
    for i, h in enumerate((420, 330, 250, 150)):
        x = 120 + i * 120
        grad_rr(ti, x, 700 - h, x + 80, 700, 10, (240, 90, 90), (190, 50, 50), diag=False)
    td.line([(130 * S, 250 * S), (300 * S, 330 * S), (420 * S, 420 * S), (560 * S, 560 * S)], fill=WHITE, width=int(12 * S), joint='curve')
    td.polygon([(610 * S, 610 * S), (500 * S, 590 * S), (590 * S, 510 * S)], fill=WHITE)


def obj_billetera(ti, t):
    td = ImageDraw.Draw(ti)
    td.rounded_rectangle([150 * S, 280 * S, 650 * S, 600 * S], radius=40 * S, fill=(140, 90, 56))
    td.rounded_rectangle([170 * S, 250 * S, 630 * S, 330 * S], radius=30 * S, fill=(80, 190, 120))
    td.rounded_rectangle([480 * S, 400 * S, 690 * S, 500 * S], radius=36 * S, fill=(176, 120, 76))
    td.ellipse([520 * S, 435 * S, 556 * S, 471 * S], fill=(255, 220, 110))


_3.OBJETOS.update({'personaje': obj_persona2, 'pila_monedas': obj_pila, 'bolsa': obj_bolsa, 'casa': obj_casa, 'auto': obj_auto,
                   'carrito': obj_carrito, 'cohete': obj_cohete, 'alerta': obj_alerta, 'burbuja': obj_burbuja, 'baja': obj_baja,
                   'billetera': obj_billetera})
_ANIM_STATIC = ('casa', 'auto', 'carrito', 'bolsa', 'billetera', 'pila_monedas', 'baja')
_3.ESTATICOS = tuple(_3.ESTATICOS) + _ANIM_STATIC


def _pill(d, x, y, s, fs=34, fill=(255, 255, 255), ink=(20, 20, 26), k=1.0):
    wpx = d.textlength(s, font=pfont(fs, True)) / S + 44
    rrect(d, x - wpx / 2 * k, y - 34 * k, x + wpx / 2 * k, y + 34 * k, 18, fill=fill)
    if k > 0.7:
        d.text((x * S, y * S), s, font=pfont(fs, True), fill=ink, anchor='mm')


def _icono(d, kind, x, y, s, color):
    r = s
    if kind == 'check':
        circle(d, x, y, r, fill=GREEN)
        d.line([P(x - r * .45, y), P(x - r * .1, y + r * .35), P(x + r * .5, y - r * .38)], fill=WHITE, width=int(r * .22 * S), joint='curve')
    elif kind == 'x':
        circle(d, x, y, r, fill=RED)
        d.line([P(x - r * .4, y - r * .4), P(x + r * .4, y + r * .4)], fill=WHITE, width=int(r * .22 * S))
        d.line([P(x + r * .4, y - r * .4), P(x - r * .4, y + r * .4)], fill=WHITE, width=int(r * .22 * S))
    elif kind == 'estrella':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append(P(x + math.cos(a) * rr, y + math.sin(a) * rr))
        d.polygon(pts, fill=GOLD)
    elif kind == 'corazon':
        circle(d, x - r * .3, y - r * .2, r * .42, fill=RED)
        circle(d, x + r * .3, y - r * .2, r * .42, fill=RED)
        d.polygon([P(x - r * .68, y - r * .02), P(x + r * .68, y - r * .02), P(x, y + r * .8)], fill=RED)
    else:
        circle(d, x, y, r, fill=GOLD)
        d.text((x * S, y * S), '?' if kind == 'pregunta' else '!', font=pfont(r * 1.3, True), fill=(40, 34, 20), anchor='mm')


_ORIG = _4.n_objeto


def n_obj(d, t, sc):
    _4._PP.clear()
    _4._PP.update(sc['p'])
    return _ORIG(d, t, sc)


PLANTILLAS['objeto'] = (n_obj, _3.e_objeto)


def _capa_t(c, sc):
    return cue(sc, c.get('cue'), 0.05)


def n_escena(d, t, sc):
    for c in sc['p'].get('capas', []):
        t0 = _capa_t(c, sc)
        a = prog(t, t0, t0 + 0.4)
        if a <= 0:
            continue
        kind = c.get('t', 'obj')
        k = e_back(a)
        x, y = float(c.get('x', 360)), float(c.get('y', 480))
        col_ = col(c.get('color', 'blanco'))
        if kind == 'obj':
            sc2 = {'p': c, 'dur': sc['dur'], 'words': sc['words'], 'start': sc['start']}
            n_obj(d, t, sc2)
        elif kind == 'txt':
            sz = float(c.get('tam', 84)) * (0.6 + 0.4 * k)
            rich(d, x, y, c['texto'], sz, float(c.get('ancho', 620)), hl=col(c.get('resalte', 'oro')), fill=col_, stroke=6)
        elif kind == 'pill':
            _pill(d, x, y, str(c['texto']), float(c.get('tam', 34)), k=k)
        elif kind == 'num':
            v = lerp(float(c.get('desde', 0)), float(c['valor']), e_out(prog(t, t0, t0 + 1.4)))
            s2 = fmt(v, int(c.get('decimales', 0)), c.get('prefijo', ''), c.get('sufijo', ''))
            fs = fit(d, s2, float(c.get('tam', 120)), 560)
            txt(d, x, y, s2, fs * (0.7 + 0.3 * k), col_, stroke=7, sfill=(0, 0, 0))
        elif kind == 'flecha':
            x0, y0 = c.get('de', [200, 600])
            x1, y1 = c.get('a', [500, 300])
            pr = e_out(prog(t, t0, t0 + 0.7))
            xe, ye = x0 + (x1 - x0) * pr, y0 + (y1 - y0) * pr
            wd = float(c.get('grosor', 16))
            d.line([P(x0, y0), P(xe, ye)], fill=col_ if c.get('color') else GOLD, width=int(wd * S))
            ang = math.atan2(y1 - y0, x1 - x0)
            hl = wd * 3.2
            pts = [P(xe + math.cos(ang) * hl * .5, ye + math.sin(ang) * hl * .5), P(xe + math.cos(ang + 2.5) * hl, ye + math.sin(ang + 2.5) * hl), P(xe + math.cos(ang - 2.5) * hl, ye + math.sin(ang - 2.5) * hl)]
            d.polygon(pts, fill=col_ if c.get('color') else GOLD)
        elif kind == 'forma':
            w_, h_ = float(c.get('w', 200)) * k, float(c.get('h', 200)) * k
            if c.get('f', 'circulo') == 'circulo':
                circle(d, x, y, w_ / 2, fill=col_)
            else:
                rrect(d, x - w_ / 2, y - h_ / 2, x + w_ / 2, y + h_ / 2, float(c.get('r', 24)), fill=col_)
        elif kind == 'icono':
            _icono(d, c.get('i', 'check'), x, y, float(c.get('tam', 70)) * k, col_)


def e_escena(sc):
    ev = []
    for c in sc['p'].get('capas', []):
        t0 = _capa_t(c, sc)
        ev.append((t0, 'pop'))
        if c.get('t') == 'num':
            ev.append((t0 + 1.4, 'ching'))
        if c.get('contador'):
            ev.append((cue(sc, c['contador'].get('cue'), 0.3 * sc['dur']) + 1.4, 'ching'))
    return ev


PLANTILLAS['escena'] = (n_escena, e_escena)
_4._DEF['escena'] = 'carbon'

