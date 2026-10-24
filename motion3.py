import math
import os
import random
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

import motion as _m

_m.BG1, _m.BG2 = (18, 19, 22), (5, 5, 6)
_m.GOLD, _m.GOLD_D, _m.GOLD_L = (255, 209, 92), (229, 161, 20), (255, 232, 160)
_m.GREEN, _m.GREEN_D = (29, 215, 91), (18, 150, 66)
_m.RED, _m.RED_D = (229, 62, 62), (160, 40, 40)
_m.BLUE = (47, 128, 237)
_m.INK, _m.CARD, _m.CARD_L, _m.MUTED = (8, 8, 10), (24, 25, 29), (52, 54, 63), (150, 154, 166)
_m.COLORES = {'oro': _m.GOLD, 'verde': _m.GREEN, 'rojo': _m.RED, 'azul': _m.BLUE, 'blanco': (255, 255, 255)}

from motion import *

_FONT_PATH = _m._FONT_PATH
SUB_DIRS = _m.SUB_DIRS


def card(d, x0, y0, x1, y1, r=30, fill=None, outline=None):
    rrect(d, x0, y0 + 16, x1, y1 + 16, r, fill=(0, 0, 0, 120))
    rrect(d, x0, y0 + 8, x1, y1 + 8, r, fill=(0, 0, 0, 150))
    rrect(d, x0, y0, x1, y1, r, fill=fill or CARD, outline=outline or CARD_L, width=2)


_m.card = card


def txt(d, x, y, s, sz, fill=WHITE, anchor='mm', stroke=0, sfill=INK):
    d.text((x * S, y * S), str(s), font=_m.font(sz), fill=fill, anchor=anchor,
           stroke_width=int(stroke * S), stroke_fill=sfill)


_m.txt = txt


def grad_img(w, h, c1, c2, diag=True):
    gx = np.linspace(0, 1, w)[None, :]
    gy = np.linspace(0, 1, h)[:, None]
    k = (gx * 0.35 + gy * 0.65) if diag else (gy + gx * 0)
    arr = np.array(c1)[None, None, :] * (1 - k[:, :, None]) + np.array(c2)[None, None, :] * k[:, :, None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')


def grad_rr(ti, x0, y0, x1, y1, r, c1, c2, diag=True, outline=None, ow=2):
    w, h = int((x1 - x0) * S), int((y1 - y0) * S)
    if w < 2 or h < 2:
        return
    g = grad_img(w, h, c1, c2, diag)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(r * S), fill=255)
    ti.paste(g, (int(x0 * S), int(y0 * S)), m)
    if outline:
        ImageDraw.Draw(ti).rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, outline=outline, width=int(ow * S))


def rim(ti, x0, y0, x1, y1, r, alpha=90):
    ov = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, outline=(255, 255, 255, alpha), width=int(2 * S))
    ti.alpha_composite(ov)


def gloss(ti, pts, alpha=26):
    ov = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(x * S, y * S) for x, y in pts], fill=(255, 255, 255, alpha))
    ti.alpha_composite(ov)


def glow(ti, box, color, alpha=70, blur=18):
    ov = Image.new('RGBA', ti.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse([v * S for v in box], fill=color + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(blur * S))
    ti.alpha_composite(ov)


def obj_tarjeta(ti, t):
    td = ImageDraw.Draw(ti)
    glow(ti, (140, 240, 660, 560), GOLD, 40, 40)
    grad_rr(ti, 120, 224, 680, 576, 32, (40, 46, 62), (14, 17, 25), outline=(86, 94, 116), ow=2)
    rim(ti, 122, 226, 678, 574, 30, 50)
    gloss(ti, [(120, 224), (400, 224), (250, 576), (120, 576)], 18)
    grad_rr(ti, 170, 330, 250, 392, 10, (255, 217, 110), (214, 150, 24))
    for yy in (345, 361, 377):
        td.line([(170 * S, yy * S), (250 * S, yy * S)], fill=(120, 80, 10), width=int(1.5 * S))
    td.line([(210 * S, 330 * S), (210 * S, 392 * S)], fill=(120, 80, 10), width=int(1.5 * S))
    for k in range(3):
        r = 22 + 16 * k
        td.arc([(600 - r) * S, (320 - r) * S, (600 + r) * S, (320 + r) * S], -50, 50, fill=GOLD, width=int(4 * S))
    td.text((170 * S, 480 * S), (chr(8226) * 4 + '  ') * 3 + '4821', font=pfont(32, False), fill=(190, 196, 210), anchor='lm')


def obj_telefono(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 250, 110, 550, 690, 46, (44, 46, 54), (16, 17, 21), outline=(96, 100, 114), ow=3)
    grad_rr(ti, 262, 124, 538, 676, 36, (10, 12, 18), (6, 8, 12))
    td.rounded_rectangle([350 * S, 138 * S, 450 * S, 160 * S], radius=11 * S, fill=(0, 0, 0))
    td.text((400 * S, 262 * S), '3,40 ' + chr(8364), font=pfont(54, True), fill=WHITE, anchor='mm')
    td.text((400 * S, 314 * S), 'IMPORTE', font=pfont(22, False), fill=MUTED, anchor='mm')
    pulse = 1 + 0.06 * math.sin(t * 5)
    glow(ti, (300, 360, 500, 560), GREEN, 70, 20)
    r = 70 * pulse
    td.ellipse([(400 - r) * S, (460 - r) * S, (400 + r) * S, (460 + r) * S], fill=GREEN)
    td.line([(368 * S, 462 * S), (392 * S, 488 * S), (436 * S, 432 * S)], fill=(6, 30, 14), width=int(13 * S), joint='curve')
    td.text((400 * S, 590 * S), 'APROBADA', font=pfont(28, True), fill=GREEN, anchor='mm')
    gloss(ti, [(250, 110), (390, 110), (290, 690), (250, 690)], 14)


def obj_reloj(ti, t):
    td = ImageDraw.Draw(ti)
    glow(ti, (160, 160, 640, 640), GOLD, 46, 36)
    td.ellipse([170 * S, 170 * S, 630 * S, 630 * S], fill=(20, 22, 28), outline=GOLD, width=int(10 * S))
    td.ellipse([192 * S, 192 * S, 608 * S, 608 * S], outline=(60, 62, 72), width=int(2 * S))
    for k in range(12):
        a = k * math.pi / 6
        r0, r1 = (182, 204) if k % 3 else (170, 204)
        td.line([((400 + math.sin(a) * r0) * S, (400 - math.cos(a) * r0) * S), ((400 + math.sin(a) * r1) * S, (400 - math.cos(a) * r1) * S)], fill=WHITE if k % 3 == 0 else MUTED, width=int((6 if k % 3 == 0 else 3) * S))
    am = t * 2.2
    ah = am / 12
    td.line([(400 * S, 400 * S), ((400 + math.sin(am) * 170) * S, (400 - math.cos(am) * 170) * S)], fill=GOLD, width=int(6 * S))
    td.line([(400 * S, 400 * S), ((400 + math.sin(ah) * 110) * S, (400 - math.cos(ah) * 110) * S)], fill=WHITE, width=int(11 * S))
    td.ellipse([388 * S, 388 * S, 412 * S, 412 * S], fill=GOLD)
    gloss(ti, [(190, 230), (400, 200), (330, 420), (200, 420)], 14)


def obj_candado(ti, t):
    td = ImageDraw.Draw(ti)
    glow(ti, (200, 360, 600, 660), GOLD, 40, 30)
    td.arc([270 * S, 150 * S, 530 * S, 430 * S], 180, 360, fill=(150, 156, 172), width=int(30 * S))
    td.line([(270 * S, 290 * S), (270 * S, 400 * S)], fill=(150, 156, 172), width=int(30 * S))
    td.line([(530 * S, 290 * S), (530 * S, 400 * S)], fill=(150, 156, 172), width=int(30 * S))
    grad_rr(ti, 220, 380, 580, 640, 34, (255, 215, 105), (200, 140, 24), outline=(255, 236, 160), ow=2)
    td.ellipse([368 * S, 456 * S, 432 * S, 520 * S], fill=(40, 28, 6))
    td.polygon([(390 * S, 505 * S), (410 * S, 505 * S), (418 * S, 580 * S), (382 * S, 580 * S)], fill=(40, 28, 6))
    gloss(ti, [(220, 380), (380, 380), (320, 640), (220, 640)], 30)


def obj_lupa(ti, t):
    td = ImageDraw.Draw(ti)
    td.line([(500 * S, 500 * S), (640 * S, 640 * S)], fill=(60, 64, 78), width=int(54 * S))
    td.ellipse([190 * S, 170 * S, 510 * S, 490 * S], fill=(22, 32, 52), outline=GOLD, width=int(22 * S))
    gloss(ti, [(230, 230), (380, 200), (260, 360)], 50)


def obj_banco(ti, t):
    td = ImageDraw.Draw(ti)
    glow(ti, (150, 200, 650, 620), GOLD, 26, 40)
    grad_rr(ti, 150, 560, 650, 610, 8, (70, 74, 88), (36, 38, 46), diag=False, outline=(110, 116, 134), ow=2)
    grad_rr(ti, 180, 520, 620, 560, 6, (76, 80, 96), (42, 44, 54), diag=False, outline=(110, 116, 134), ow=2)
    for k in range(4):
        x = 215 + k * 112
        grad_rr(ti, x, 330, x + 58, 520, 6, (96, 102, 120), (40, 43, 53), diag=False)
        td.line([((x + 4) * S, 340 * S), ((x + 4) * S, 510 * S)], fill=(150, 156, 176), width=int(2 * S))
    td.polygon([(140 * S, 330 * S), (400 * S, 190 * S), (660 * S, 330 * S)], fill=(84, 88, 104), outline=(130, 136, 156))
    td.polygon([(190 * S, 320 * S), (400 * S, 215 * S), (610 * S, 320 * S)], fill=(52, 55, 66))
    glow(ti, (370, 250, 430, 320), GOLD, 120, 10)
    td.ellipse([376 * S, 262 * S, 424 * S, 310 * S], fill=GOLD)


def obj_persona(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 220, 430, 580, 700, 120, (92, 100, 124), (36, 40, 54), diag=False, outline=(130, 138, 160), ow=2)
    td.ellipse([310 * S, 180 * S, 490 * S, 360 * S], fill=(106, 114, 138), outline=(150, 158, 180), width=int(2 * S))
    gloss(ti, [(320, 200), (400, 190), (340, 330)], 40)


def obj_bombilla(ti, t):
    td = ImageDraw.Draw(ti)
    g = 0.5 + 0.5 * math.sin(t * 4)
    glow(ti, (120, 80, 680, 640), GOLD, int(60 + 50 * g), 50)
    td.ellipse([240 * S, 170 * S, 560 * S, 490 * S], fill=(255, 222, 110), outline=(255, 244, 190), width=int(5 * S))
    grad_rr(ti, 320, 480, 480, 560, 14, (130, 134, 148), (60, 62, 72), diag=False)
    grad_rr(ti, 336, 566, 464, 610, 14, (110, 114, 128), (50, 52, 62), diag=False)
    gloss(ti, [(270, 220), (360, 190), (300, 340)], 70)


def obj_cruz(ti, t):
    td = ImageDraw.Draw(ti)
    glow(ti, (200, 200, 600, 620), GOLD, 70, 46)
    for k in range(16):
        a = k * math.pi / 8 + t * 0.3
        r0, r1 = 150, 340 + 40 * math.sin(t * 2 + k)
        td.line([((400 + math.cos(a) * r0) * S, (400 + math.sin(a) * r0) * S), ((400 + math.cos(a) * r1) * S, (400 + math.sin(a) * r1) * S)], fill=(255, 226, 150, 150), width=int(3 * S))
    grad_rr(ti, 368, 200, 432, 620, 12, (255, 236, 160), (222, 160, 40), diag=False)
    grad_rr(ti, 250, 300, 550, 364, 12, (255, 236, 160), (222, 160, 40), diag=False)


def obj_billete(ti, t):
    td = ImageDraw.Draw(ti)
    glow(ti, (130, 250, 670, 550), GREEN, 36, 40)
    grad_rr(ti, 130, 250, 670, 550, 20, (24, 86, 58), (10, 40, 28), outline=(70, 200, 130), ow=2)
    td.rounded_rectangle([158 * S, 278 * S, 642 * S, 522 * S], radius=12 * S, outline=(60, 160, 108), width=int(2 * S))
    td.ellipse([320 * S, 290 * S, 480 * S, 510 * S], fill=(14, 62, 42), outline=(70, 200, 130), width=int(3 * S))
    td.text((400 * S, 400 * S), '$', font=pfont(110, True), fill=(120, 240, 168), anchor='mm')
    gloss(ti, [(130, 250), (340, 250), (240, 550), (130, 550)], 20)


def obj_moneda(ti, t):
    sq = abs(math.cos(t * 1.4)) * 0.35 + 0.65
    td = ImageDraw.Draw(ti)
    glow(ti, (200, 200, 600, 600), GOLD, 60, 40)
    rx, ry = 190 * sq, 190
    td.ellipse([(400 - rx) * S, (400 - ry) * S, (400 + rx) * S, (400 + ry) * S], fill=GOLD_D)
    td.ellipse([(400 - rx * 0.88) * S, (400 - ry * 0.88) * S, (400 + rx * 0.88) * S, (400 + ry * 0.88) * S], fill=GOLD)
    td.ellipse([(400 - rx * 0.66) * S, (400 - ry * 0.66) * S, (400 + rx * 0.66) * S, (400 + ry * 0.66) * S], outline=GOLD_L, width=int(5 * S))
    if sq > 0.55:
        td.text((400 * S, 404 * S), '$', font=pfont(190 * sq, True), fill=GOLD_D, anchor='mm')


def obj_onda(ti, t):
    td = ImageDraw.Draw(ti)
    grad_rr(ti, 80, 230, 720, 570, 22, (16, 18, 26), (10, 12, 18), outline=(120, 100, 50), ow=2)
    for k in range(1, 6):
        td.line([(100 * S, (230 + k * 56.6) * S), (700 * S, (230 + k * 56.6) * S)], fill=(34, 36, 46), width=int(1 * S))
    pts = []
    for i in range(121):
        x = 100 + i * 5
        mod = 1.0 if (int(t * 1.5) + i // 30) % 2 == 0 else 0.35
        y = 400 - math.sin(i * 0.55 - t * 8) * 110 * mod
        pts.append((x * S, y * S))
    td.line(pts, fill=GOLD, width=int(4 * S), joint='curve')
    td.text((100 * S, 252 * S), 'CAMPO', font=pfont(22, True), fill=MUTED, anchor='lm')


_TILE = {}
ESTATICOS = ('tarjeta', 'lupa', 'banco', 'persona', 'candado', 'billete')
OBJETOS = {'tarjeta': obj_tarjeta, 'telefono': obj_telefono, 'reloj': obj_reloj, 'candado': obj_candado, 'lupa': obj_lupa,
           'banco': obj_banco, 'persona': obj_persona, 'bombilla': obj_bombilla, 'cruz': obj_cruz, 'billete': obj_billete,
           'moneda': obj_moneda, 'onda': obj_onda}


def campo(d, cx, cy, t, a, n=7, w=310, h=250):
    for i in range(n):
        k = (i + 1) / n
        ww, hh = w * (0.3 + 0.7 * k), h * (0.35 + 0.8 * k)
        pts = []
        for j in range(41):
            u = j / 40.0
            x = (1 - u) ** 2 * (cx - ww) + 2 * u * (1 - u) * cx + u * u * (cx + ww)
            y = (1 - u) ** 2 * (cy + 90) + 2 * u * (1 - u) * (cy - hh * 2.0) + u * u * (cy + 90)
            pts.append((x * S, y * S))
        al = int(235 * a * (0.18 + 0.5 * (0.5 + 0.5 * math.sin(t * 2.6 - i * 0.9))))
        d.line(pts, fill=GOLD + (al,), width=int(2.4 * S), joint='curve')


def n_objeto(d, t, sc):
    p = sc['p']
    cx, cy = float(p.get('x', 360)), float(p.get('y', 480))
    kind = p.get('objeto', 'tarjeta')
    t0 = cue(sc, p.get('cue'), 0.05)
    a = prog(t, t0, t0 + 0.5)
    if p.get('campo', True) and a > 0:
        campo(d, cx, cy, t, a)
    if a > 0:
        if kind in ESTATICOS and kind in _TILE:
            ti = _TILE[kind]
        else:
            ti = Image.new('RGBA', (800 * S, 800 * S), (0, 0, 0, 0))
            OBJETOS[kind](ti, t)
            bb = ti.getchannel('A').getbbox()
            if bb:
                ti = ti.crop(bb)
            if kind in ESTATICOS:
                _TILE[kind] = ti
        ang = float(p.get('angulo', 0)) + math.sin(t * 1.6) * 2.5
        k = float(p.get('escala', 0.8)) * (0.55 + 0.45 * e_back(a))
        sz = (max(2, int(ti.size[0] * k)), max(2, int(ti.size[1] * k)))
        ti = ti.resize(sz, Image.BILINEAR)
        if abs(ang) > 0.05:
            ti = ti.rotate(ang, resample=Image.BILINEAR, expand=True)
        bob = math.sin(t * 2.2) * 7
        d._image.paste(ti, (int(cx * S - ti.size[0] / 2), int((cy + bob) * S - ti.size[1] / 2)), ti)
    for i, lb in enumerate(p.get('etiquetas') or []):
        tl = cue(sc, lb.get('cue'), evenly(sc, i, len(p['etiquetas']), 0.2, 0.7))
        aa = prog(t, tl, tl + 0.35)
        if aa <= 0:
            continue
        lx, ly = cx + float(lb.get('dx', 200)), cy + float(lb.get('dy', -200))
        tx = str(lb['texto']).upper()
        wpx = d.textlength(tx, font=pfont(24, True)) / S + 40
        sx, sy = cx + (lx - cx) * 0.3, cy + (ly - cy) * 0.3
        d.line([P(sx, sy), P(lx, ly)], fill=GOLD, width=int(2 * S))
        circle(d, sx, sy, 6, fill=GOLD)
        k = e_back(aa)
        rrect(d, lx - wpx / 2 * k, ly - 26 * k, lx + wpx / 2 * k, ly + 26 * k, 10, fill=(14, 16, 22), outline=GOLD, width=2)
        if k > 0.7:
            d.text((lx * S, ly * S), tx, font=pfont(24, True), fill=WHITE, anchor='mm')
    ct = p.get('contador')
    if ct:
        tc = cue(sc, ct.get('cue'), 0.3 * sc['dur'])
        ac = prog(t, tc, tc + 0.3)
        if ac > 0:
            v = lerp(float(ct.get('desde', 0)), float(ct['valor']), e_out(prog(t, tc, tc + 1.4)))
            s2 = fmt(v, int(ct.get('decimales', 0)), ct.get('prefijo', ''), ct.get('sufijo', ''))
            y = float(ct.get('y', 800))
            rrect(d, 70, y - 78, 650, y + 78, 22, fill=(12, 13, 18), outline=CARD_L, width=2)
            txt(d, 360, y - 4, s2, fit(d, s2, 100, 540), col(ct.get('color', 'blanco')), stroke=0)
    ru = p.get('cota')
    if ru:
        tr = cue(sc, ru.get('cue'), 0.4 * sc['dur'])
        ar = prog(t, tr, tr + 0.6)
        if ar > 0:
            y = float(ru.get('y', 790))
            x1 = 120 + (600 - 120) * e_out(ar)
            d.line([P(120, y), P(x1, y)], fill=WHITE, width=int(2 * S))
            for xx in (120, x1):
                d.line([P(xx, y - 14), P(xx, y + 14)], fill=WHITE, width=int(2 * S))
            if ar > 0.8:
                d.text((360 * S, (y + 40) * S), str(ru['texto']).upper(), font=pfont(26, True), fill=GOLD, anchor='mm')


def e_objeto(sc):
    p = sc['p']
    ev = [(cue(sc, p.get('cue'), 0.05), 'pop')]
    n = len(p.get('etiquetas') or [])
    for i, lb in enumerate(p.get('etiquetas') or []):
        ev.append((cue(sc, lb.get('cue'), evenly(sc, i, n, 0.2, 0.7)), 'pop'))
    if p.get('contador'):
        ev.append((cue(sc, p['contador'].get('cue'), 0.3 * sc['dur']) + 1.4, 'ching'))
    return ev


def phrases_de(words):
    out, i = [], 0
    while i < len(words):
        n, ln = 1, len(words[i][0])
        while n < 6 and i + n < len(words) and not re.search('[.?!:;,]$', words[i + n - 1][0]):
            ln2 = ln + 1 + len(words[i + n][0])
            if ln2 > 36:
                break
            ln = ln2
            n += 1
        out.append((i, n))
        i += n
    return out


_PF = {}


def pfont(sz, bold):
    k = (int(round(sz * S)), bold)
    if k not in _PF:
        import glob
        nm = 'Poppins-Bold.ttf' if bold else 'Poppins-Medium.ttf'
        path = None
        for dd in SUB_DIRS + ['/usr/share/fonts/truetype/google-fonts']:
            for q in glob.glob(os.path.join(dd, '**', nm), recursive=True):
                path = q
                break
            if path:
                break
        path = path or _FONT_PATH
        _PF[k] = ImageFont.truetype(path, k[0]) if path else ImageFont.load_default()
    return _PF[k]


BLUE_SEL = (47, 128, 237)


def draw_subs2(d, t, words, frases):
    idx = None
    for i, (w, a, b) in enumerate(words):
        if a <= t:
            idx = i
        else:
            break
    if idx is None or t > words[idx][2] + 0.45:
        return
    for (gs, gn) in frases:
        if gs <= idx < gs + gn:
            g0, n = gs, gn
            break
    toks = [re.sub('[' + chr(34) + ']', '', w[0]) for w in words[g0:g0 + n]]
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
            col_t = WHITE if spoken else (255, 255, 255, 120)
            if active:
                pad = 9 * S
                x0, x1 = x - pad, x + ws[j] + pad
                y0, y1 = (y - fs * 0.64) * S, (y + fs * 0.62) * S
                d.rectangle([x0, y0, x1, y1], fill=(47, 128, 237, 34), outline=BLUE_SEL, width=int(2.2 * S))
                for (hx, hy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0)):
                    d.ellipse([hx - 5.5 * S, hy - 5.5 * S, hx + 5.5 * S, hy + 5.5 * S], fill=WHITE, outline=BLUE_SEL, width=int(2 * S))
            d.text((x + 2 * S, y * S + 3 * S), toks[j], font=f, fill=(0, 0, 0, 170), anchor='lm')
            d.text((x + 1 * S, y * S + 1.5 * S), toks[j], font=f, fill=(0, 0, 0, 200), anchor='lm')
            d.text((x, y * S), toks[j], font=f, fill=col_t, anchor='lm', stroke_width=int(2 * S), stroke_fill=(0, 0, 0, 110))
            x += ws[j] + sp
        y += lh


_gy, _gx = np.mgrid[0:H, 0:W]
_r2 = np.sqrt(((_gx - W / 2) / (W * 0.62)) ** 2 + ((_gy - H * 0.5) / (H * 0.62)) ** 2)
_k = np.clip(_r2, 0, 1.2)[:, :, None]
_bgf = np.array((20, 21, 25))[None, None, :] * (1 - np.clip(_k, 0, 1)) + np.array((5, 5, 6))[None, None, :] * np.clip(_k, 0, 1)
BG_S1 = Image.fromarray(np.clip(_bgf, 0, 255).astype(np.uint8))
_NOISE = np.random.RandomState(3).randint(-3, 4, size=(6, H, W, 1)).astype(np.int16)
random.seed(11)
PT = [(random.random(), random.random(), random.uniform(0.2, 0.9), random.choice((1.2, 1.6, 2.2, 3.0, 9.0)), random.uniform(0.5, 1.0)) for _ in range(46)]


def frame(t, scenes, words, total, grupos=None, linea=''):
    base = BG_S1.copy()
    pl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dp = ImageDraw.Draw(pl)
    for (px, py, sp, sz, br) in PT:
        y = (py - t * sp * 0.03) % 1.0
        x = px + math.sin(t * sp + px * 9) * 0.01
        al = int((26 if sz > 5 else 70) * br)
        dp.ellipse([x * W - sz, y * H - sz, x * W + sz, y * H + sz], fill=(235, 235, 240, al))
    pl = pl.filter(ImageFilter.GaussianBlur(0.6))
    base.paste(pl, (0, 0), pl)
    sc = scenes[-1]
    for s in scenes:
        if s['start'] <= t < s['start'] + s['dur']:
            sc = s
            break
    lt = t - sc['start']
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
    sh = sh.point(lambda v: int(v * 0.6))
    base.paste(Image.new('RGB', (W, H), (0, 0, 0)), (0, 14), sh)
    base.paste(full, (0, 0), full)
    small = full.convert('RGB').resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    bloom = small.resize((W, H), Image.BILINEAR).point(lambda v: int(v * 0.42))
    base = ImageChops.screen(base, bloom)
    th = int(0.30 * CH)
    tile = Image.new('RGBA', (CW, th), (0, 0, 0, 0))
    draw_subs2(ImageDraw.Draw(tile), t, words, grupos or phrases_de(words))
    tile = tile.resize((W, th // S), Image.LANCZOS)
    base.paste(tile, (0, 0), tile)
    arr = np.asarray(base).astype(np.int16) + _NOISE[int(t * 30) % 6]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


PLANTILLAS['objeto'] = (n_objeto, e_objeto)

