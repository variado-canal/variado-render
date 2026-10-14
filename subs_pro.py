"""Subtitulos compartidos (Fe, Dinero con Historia y Variado), estilo de referencia de Ferlyn (14 oct 2026).

Estilo "Default": MAYUSCULAS, letra condensada en negrita (Barlow Condensed Bold; si no esta, Inter Bold),
blanco con contorno negro y sombra suave, 2 a 4 palabras por bloque, sin signos de puntuacion, centrado a ~73% de la
altura. La palabra que se esta diciendo va dentro de un recuadro redondeado: rojo (FF3849) en Variado y Dinero, dorado suave en Fe (set_paleta('fe')).
Estilo "Cierre": igual pero sin recuadro. Los estilos Hook, Titulo y Fuente no cambian (Inter).
`titulo_fijo()` dibuja la linea de titulo fija de arriba (blanca, tamano medio) que usa Variado.
El recuadro se calcula midiendo el texto con PIL y la escala de libass (OS/2 winAscent+winDescent).
Si algo falla al medir, se dibuja solo el texto (sin recuadro) y el video se renderiza igual.
"""
import glob
import os
import re

NL = chr(10)
BLANCO = '&H00FFFFFF&'
ROJO = '&H004938FF&'        # FF3849 (ASS usa orden BGR)
ROJO_BORDE = '&H00231AD1&'  # D11A23
ORO = '&H003AC8FF&'
# colores del recuadro por canal (BGR): rojo para Variado y Dinero; dorado suave para Fe (paz, como la cruz dorada)
PALETAS = {
    'rojo': ('&H004938FF&', '&H00231AD1&'),
    'fe': ('&H006DB8E8&', '&H003F89B8&'),   # E8B86D relleno (dorado suave), B8893F borde
}
_PAL = {'n': 'rojo'}


def set_paleta(nombre):
    _PAL['n'] = nombre if nombre in PALETAS else 'rojo'
FUENTE = 'Inter'            # estilos Hook, Titulo y Fuente

# ---- geometria del estilo de referencia, para un video de 1080 px de ancho ----
CAP_PX = 46.0         # altura de las mayusculas
PAD_X = 10.0          # margen del recuadro a cada lado del texto
PAD_Y = 14.0          # margen del recuadro arriba y abajo de las mayusculas
ACENTO_PX = 13.0      # lo que sube el recuadro si la palabra lleva acento o tilde
RADIO = 12.0          # esquinas del recuadro
Y_SUB = 0.727         # centro vertical de las mayusculas (fraccion de la altura)
Y_TITULO = 0.177      # centro vertical de la linea de titulo fija
ANCHO_MAX = 0.90      # el bloque de subtitulos no pasa de este ancho

_CANDIDATAS = [
    # (ruta, familia en libass, negrita, factor de tamano si no es la fuente de referencia)
    ('BarlowCondensed-Bold.ttf', 'Barlow Condensed', 1, 1.0),
    ('BarlowCondensed-SemiBold.ttf', 'Barlow Condensed SemiBold', 0, 1.0),
    ('Inter-Bold.otf', 'Inter', 1, 0.82),
    ('DejaVuSansCondensed-Bold.ttf', 'DejaVu Sans', 1, 0.90),
]
_DIRS = [os.path.expanduser('~/.fonts'), '/usr/local/share/fonts', '/usr/share/fonts', os.path.dirname(os.path.abspath(__file__))]
_cache = {}


def _buscar(nombre):
    for d in _DIRS:
        p = os.path.join(d, nombre)
        if os.path.isfile(p):
            return p
        for q in glob.glob(os.path.join(d, '**', nombre), recursive=True):
            return q
    return None


def _fuente_sub():
    if 'sub' in _cache:
        return _cache['sub']
    res = None
    for nombre, familia, bold, factor in _CANDIDATAS:
        ruta = _buscar(nombre)
        if ruta:
            res = {'ruta': ruta, 'familia': familia, 'bold': bold, 'factor': factor}
            break
    _cache['sub'] = res
    return res


def _metricas(ruta):
    """(unitsPerEm, ascent, descent, capHeight) en unidades de la fuente; descent positivo."""
    clave = 'm:' + ruta
    if clave in _cache:
        return _cache[clave]
    upem, asc, desc, cap = 1000.0, 900.0, 250.0, 700.0
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(ruta, fontNumber=0, lazy=True)
        upem = float(f['head'].unitsPerEm)
        os2 = f['OS/2']
        asc = float(os2.usWinAscent)
        desc = float(os2.usWinDescent)
        cap = float(getattr(os2, 'sCapHeight', 0) or 0.7 * upem)
        if asc + desc <= 0:
            asc, desc = float(f['hhea'].ascent), float(-f['hhea'].descent)
    except Exception:
        try:
            from PIL import ImageFont
            fp = ImageFont.truetype(ruta, 1000)
            a, d = fp.getmetrics()
            asc, desc, upem = float(a), float(d), 1000.0
        except Exception:
            pass
    _cache[clave] = (upem, asc, desc, cap)
    return _cache[clave]


class _Medidor:
    """Mide texto con PIL al tamano 'em' y da el Fontsize de ASS equivalente."""

    def __init__(self, W):
        self.ok = False
        self.W = W
        f = _fuente_sub()
        self.f = f
        if not f:
            return
        upem, asc, desc, cap = _metricas(f['ruta'])
        k = W / 1080.0
        self.em = (CAP_PX * k) / (cap / upem) * f['factor']
        self.cap = cap / upem * self.em
        self.asc = asc / upem * self.em
        self.desc = desc / upem * self.em
        self.ass_size = self.em * (asc + desc) / upem   # libass: Fontsize = em * (winAscent+winDescent)/unitsPerEm
        try:
            from PIL import ImageFont
            self.pil = ImageFont.truetype(f['ruta'], max(int(round(self.em * 4)), 8))   # 4x para precision
            self.ok = True
        except Exception:
            self.ok = False

    def ancho(self, texto):
        return self.pil.getlength(texto) / 4.0


def ass_time(t):
    t = max(float(t), 0.0)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return '%d:%02d:%05.2f' % (h, m, s)


def limpiar(t):
    return ' '.join(str(t).replace('{', '(').replace('}', ')').replace(chr(92), ' ').split())


def para_pantalla(t):
    """Mayusculas y sin signos de puntuacion (como en el video de referencia)."""
    t = limpiar(t).upper()
    t = re.sub(r'(?<=\d)[.,](?=\d)', '\u0001', t)             # decimales y miles se conservan
    t = re.sub(r'[.,;:!?¡¿"“”«»()…—–‘’\']', ' ', t)
    t = t.replace('\u0001', ',')
    t = re.sub(r'\s+-\s+|\s+-|-\s+', ' ', t)
    return ' '.join(t.split())


def envolver(texto, ancho):
    lineas, cur = [], ''
    for p in texto.split():
        prueba = (cur + ' ' + p).strip()
        if cur and len(prueba) > ancho:
            lineas.append(cur)
            cur = p
        else:
            cur = prueba
    if cur:
        lineas.append(cur)
    return lineas


def trozos(texto, max_words=3, max_chars=22):
    out, cur = [], []
    for w in texto.split():
        prueba = ' '.join(cur + [w])
        if cur and (len(cur) >= max_words or len(prueba) > max_chars):
            out.append(cur)
            cur = [w]
        else:
            cur.append(w)
        if w[-1:] in '.!?;:' and cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def peso_palabra(w):
    p = len(w) + 2
    if w[-1:] in ',;:':
        p += 3
    if w[-1:] in '.!?':
        p += 5
    return p


_ESTADO = {'W': 1080, 'H': 1920}


def cabecera(W, H, margen_v=470):
    _ESTADO['W'], _ESTADO['H'] = W, H
    f = FUENTE
    med = _Medidor(W)
    if med.ok:
        fam, bold, size = med.f['familia'], med.f['bold'], med.ass_size
    else:
        fam, bold, size = f, 1, 80 * W / 1080.0
    k = W / 1080.0
    borde = 4.5 * k
    sombra = 2.5 * k
    ref = ('Style: Default,%s,%.2f,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,%d,0,0,0,100,100,0,0,1,%.2f,%.2f,2,40,40,%d,1'
           % (fam, size, -1 if bold else 0, borde, sombra, int(H * (1 - Y_SUB) - 40 * k)))
    cierre = ref.replace('Style: Default,', 'Style: Cierre,')
    tit = ('Style: LineaTitulo,Inter Medium,%.2f,&H00FFFFFF,&H000000FF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,1.2,2.2,8,40,40,%d,1'
           % (52.0 * k, int(H * Y_TITULO - 30 * k)))
    return NL.join([
        '[Script Info]', 'ScriptType: v4.00+', 'PlayResX: %d' % W, 'PlayResY: %d' % H, 'WrapStyle: 2', 'ScaledBorderAndShadow: yes', '',
        '[V4+ Styles]',
        'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,'
        'Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,'
        'Alignment,MarginL,MarginR,MarginV,Encoding',
        ref,
        cierre,
        'Style: Hook,%s,92,&H003AC8FF,&H000000FF,&H00141414,&H96000000,1,0,0,0,100,100,1,0,1,4,4,8,70,70,330,1' % f,
        'Style: Titulo,%s,72,&H00FFFFFF,&H000000FF,&H00141414,&H96000000,1,0,0,0,100,100,1,0,1,3,4,8,80,80,300,1' % f,
        'Style: Fuente,%s,38,&H00E8E8E8,&H000000FF,&H00141414,&H64000000,1,0,0,0,100,100,0.5,0,1,2,2,2,80,80,330,1' % f,
        tit,
        '', '[Events]',
        'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text', '',
    ])


def _rect_redondeado(w, h, r):
    r = min(r, w / 2.0, h / 2.0)
    c = r * 0.4477
    f = lambda v: '%.1f' % v
    p = ['m', f(r), '0', 'l', f(w - r), '0',
         'b', f(w - c), '0', f(w), f(c), f(w), f(r),
         'l', f(w), f(h - r),
         'b', f(w), f(h - c), f(w - c), f(h), f(w - r), f(h),
         'l', f(r), f(h),
         'b', f(c), f(h), '0', f(h - c), '0', f(h - r),
         'l', '0', f(r),
         'b', '0', f(c), f(c), '0', f(r), '0']
    return ' '.join(p)


def _dialogos_ref(texto, ini, fin, estilo, max_words, max_chars):
    W, H = _ESTADO['W'], _ESTADO['H']
    k = W / 1080.0
    texto = para_pantalla(texto)
    bloques = trozos(texto, max_words, max_chars)
    if not bloques or fin - ini < 0.2:
        return []
    med = _Medidor(W)
    pesos_b = [sum(peso_palabra(w) for w in b) for b in bloques]
    tw = float(sum(pesos_b))
    lineas = []
    t = ini
    ycap = H * Y_SUB            # centro vertical de las mayusculas
    for b, pb in zip(bloques, pesos_b):
        db = (fin - ini) * pb / tw
        ws = [float(peso_palabra(w)) for w in b]
        sw = sum(ws)
        linea = ' '.join(b)
        # posicion de cada palabra (si se puede medir)
        cajas = None
        if med.ok:
            try:
                total = med.ancho(linea)
                esp = med.ancho(' ')
                if total > ANCHO_MAX * W:
                    raise ValueError('muy ancho')
                x0 = W / 2.0 - total / 2.0
                cajas = []
                for j, w in enumerate(b):
                    previo = ' '.join(b[:j]) + (' ' if j else '')
                    xw = x0 + med.ancho(previo)
                    cajas.append((xw, med.ancho(w)))
            except Exception:
                cajas = None
        # texto del bloque (una sola linea para todo el bloque)
        # centro de la linea (\an5) -> el centro de las mayusculas queda en ycap
        if med.ok:
            y_linea = ycap + med.cap / 2.0 + (med.desc - med.asc) / 2.0
            pos = '{\\an5\\pos(%.1f,%.1f)}' % (W / 2.0, y_linea)
        else:
            pos = ''
        lineas.append('Dialogue: 1,%s,%s,%s,,0,0,0,,%s%s' % (ass_time(t), ass_time(t + db), estilo, pos, linea))
        if estilo == 'Cierre' or cajas is None:
            t += db
            continue
        c = t
        for j, w in enumerate(b):
            dw = db * ws[j] / sw
            xw, ancho = cajas[j]
            alto_extra = ACENTO_PX * k if re.search(r'[ÁÉÍÓÚÜÑ]', w) else 0.0
            bw = ancho + 2 * PAD_X * k
            bh = med.cap + 2 * PAD_Y * k + alto_extra
            bx = xw - PAD_X * k
            by = ycap - med.cap / 2.0 - PAD_Y * k - alto_extra
            forma = _rect_redondeado(bw, bh, RADIO * k)
            fin_w = c + dw
            lineas.append('Dialogue: 0,%s,%s,%s,,0,0,0,,{\\an7\\pos(%.1f,%.1f)\\p1\\1c%s\\3c%s\\bord%.1f\\shad0\\blur0.5}%s{\\p0}' % (
                ass_time(c), ass_time(fin_w), estilo, bx, by, PALETAS[_PAL['n']][0], PALETAS[_PAL['n']][1], 1.5 * k, forma))
            c = fin_w
        t += db
    return lineas


def dialogos(texto, ini, fin, estilo='Default', max_words=3, max_chars=22, mayusculas=False):
    """Devuelve lineas 'Dialogue' repartidas entre ini y fin.
    Default y Cierre usan el estilo de referencia (mayusculas, recuadro rojo en la palabra activa).
    Otros estilos (Hook, Titulo, Fuente) conservan el diseno anterior."""
    if estilo in ('Default', 'Cierre'):
        return _dialogos_ref(texto, ini, fin, estilo, max_words, max_chars)
    texto = limpiar(texto)
    if mayusculas:
        texto = texto.upper()
    bloques = trozos(texto, max_words, max_chars)
    if not bloques or fin - ini < 0.2:
        return []
    pesos_b = [sum(peso_palabra(w) for w in b) for b in bloques]
    tw = float(sum(pesos_b))
    lineas = []
    t = ini
    for bi, (b, pb) in enumerate(zip(bloques, pesos_b)):
        db = (fin - ini) * pb / tw
        ws = [float(peso_palabra(w)) for w in b]
        sw = sum(ws)
        c = t
        for j, w in enumerate(b):
            dw = db * ws[j] / sw
            partes = []
            for k, x in enumerate(b):
                if k == j:
                    partes.append('{\\c%s}%s{\\c%s}' % (ORO, x, BLANCO))
                else:
                    partes.append(x)
            efecto = '{\\fad(90,0)}' if j == 0 else ''
            fin_w = c + dw
            lineas.append('Dialogue: 0,%s,%s,%s,,0,0,0,,%s%s' % (
                ass_time(c), ass_time(fin_w + (0.04 if j == len(b) - 1 else 0.0)), estilo, efecto, ' '.join(partes)))
            c = fin_w
        t += db
    return lineas


def titulo_fijo(texto, ini, fin, max_chars=44):
    """Linea de titulo fija de arriba (blanca, tamano medio), como en los videos de referencia (Variado)."""
    texto = limpiar(texto)
    if not texto or fin - ini < 0.1:
        return []
    W, H = _ESTADO['W'], _ESTADO['H']
    lineas_txt = envolver(texto, max_chars)[:2]
    pos = '{\\an5\\pos(%.1f,%.1f)}' % (W / 2.0, H * Y_TITULO)
    return ['Dialogue: 2,%s,%s,LineaTitulo,,0,0,0,,%s%s' % (ass_time(ini), ass_time(fin), pos, '\\N'.join(lineas_txt))]
