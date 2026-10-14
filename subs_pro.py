"""Subtitulos modernos compartidos (Fe, Dinero con Historia y Variado).
Palabra activa resaltada en dorado, 3 a 4 palabras por bloque, fuente Inter (si no esta, DejaVu Sans),
sombra suave en vez de contorno grueso. Cada canal usa este mismo estilo.
"""
NL = chr(10)
ACENTO = '&H003AC8FF&'   # dorado (ASS usa orden BGR)
BLANCO = '&H00FFFFFF&'
FUENTE = 'Inter'


def ass_time(t):
    t = max(float(t), 0.0)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return '%d:%02d:%05.2f' % (h, m, s)


def limpiar(t):
    return ' '.join(str(t).replace('{', '(').replace('}', ')').replace(chr(92), ' ').split())


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


def cabecera(W, H, margen_v=470):
    f = FUENTE
    return NL.join([
        '[Script Info]', 'ScriptType: v4.00+', 'PlayResX: %d' % W, 'PlayResY: %d' % H, 'WrapStyle: 0', '',
        '[V4+ Styles]',
        'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,'
        'Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,'
        'Alignment,MarginL,MarginR,MarginV,Encoding',
        'Style: Default,%s,88,&H00FFFFFF,&H000000FF,&H00141414,&H8C000000,1,0,0,0,100,100,0.5,0,1,3,3,2,70,70,%d,1' % (f, margen_v),
        'Style: Cierre,%s,92,&H003AC8FF,&H000000FF,&H00141414,&H8C000000,1,0,0,0,100,100,0.5,0,1,3,3,2,70,70,%d,1' % (f, margen_v + 40),
        'Style: Hook,%s,92,&H003AC8FF,&H000000FF,&H00141414,&H96000000,1,0,0,0,100,100,1,0,1,4,4,8,70,70,330,1' % f,
        'Style: Titulo,%s,72,&H00FFFFFF,&H000000FF,&H00141414,&H96000000,1,0,0,0,100,100,1,0,1,3,4,8,80,80,300,1' % f,
        'Style: Fuente,%s,38,&H00E8E8E8,&H000000FF,&H00141414,&H64000000,1,0,0,0,100,100,0.5,0,1,2,2,2,80,80,330,1' % f,
        '', '[Events]',
        'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text', '',
    ])


def dialogos(texto, ini, fin, estilo='Default', max_words=3, max_chars=22, mayusculas=False):
    """Devuelve lineas 'Dialogue' (palabra activa en dorado) repartidas entre ini y fin."""
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
                if k == j and estilo != 'Cierre':
                    partes.append('{\\c%s}%s{\\c%s}' % (ACENTO, x, BLANCO))
                else:
                    partes.append(x)
            efecto = ''
            if j == 0:
                efecto = '{\\fad(90,0)}'
            fin_w = c + dw
            lineas.append('Dialogue: 0,%s,%s,%s,,0,0,0,,%s%s' % (
                ass_time(c), ass_time(fin_w + (0.04 if j == len(b) - 1 else 0.0)), estilo, efecto, ' '.join(partes)))
            c = fin_w
        t += db
    return lineas
