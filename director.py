import re
import unicodedata


def nm(s):
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower()


TOK = re.compile('[0-9]+[.,][0-9]+|[A-Za-zÁÉÍÓÚáéíóúÑñÜü]+|[0-9]+')

# (objeto, raices normalizadas). Una raiz que termina en '=' debe coincidir exacta.
LEX = [
    ('persona_x', ()),
    ('banco', ('banco', 'prestamo', 'hipotec', 'credito', 'deuda', 'financi', 'interes')),
    ('tarjeta', ('tarjeta', 'debito', 'visa', 'contactless')),
    ('hucha', ('ahorr', 'alcancia', 'cochinito')),
    ('caja_fuerte', ('caja=', 'fuerte=', 'reserva', 'fondo=', 'patrimonio')),
    ('pila_monedas', ('moneda', 'fortuna', 'riqueza', 'centavo', 'capital', 'dinero', 'plata=', 'efectivo')),
    ('billetera', ('billetera', 'cartera', 'gasto', 'gastar', 'gastas', 'gastos', 'sueldo', 'salario', 'ingreso', 'cobr')),
    ('bolsa', ('bolsa=', 'fondos=', 'inversion', 'invert', 'invier')),
    ('lluvia', ('lluvia', 'millon', 'millones', 'millonario', 'lluev')),
    ('crecimiento', ('sube', 'suben', 'subir', 'sub=', 'crece', 'crecen', 'crecer', 'acciones', 'ganancia', 'rendimiento', 'disparan', 'dispara', 'aument')),
    ('baja', ('cae=', 'caen', 'caer', 'cayo', 'desplom', 'perdio', 'pierde', 'pierden', 'perder', 'perdida', 'quiebra', 'quebr', 'crisis', 'pierdes', 'hundi')),
    ('burbuja', ('burbuja', 'moda', 'especul', 'hype', 'inflaba', 'todos=')),
    ('cohete', ('cohete', 'despeg', 'explot', 'viral', 'rapido')),
    ('alerta', ('cuidado', 'peligro', 'alerta', 'riesgo', 'ojo=', 'advert', 'trampa', 'error', 'errores')),
    ('ladron', ('estaf', 'ladron', 'robo', 'robar', 'fraude', 'engan', 'timo')),
    ('bombilla', ('idea', 'ideas', 'descubr', 'aprend', 'leccion', 'regla', 'truco', 'consejo', 'secreto', 'clave=', 'recuerda')),
    ('balanza', ('compar', 'decid', 'equilibr', 'justo', 'versus', 'opcion', 'elegir', 'elige')),
    ('contrato', ('contrato', 'firm', 'clausula', 'documento', 'letra=', 'legal', 'ley=', 'impuesto', 'factura', 'recibo')),
    ('trofeo', ('exito', 'ganador', 'logro', 'meta=', 'metas', 'campeon', 'premio')),
    ('etiqueta', ('precio', 'descuento', 'oferta', 'barato', 'caro=', 'cara=', 'costo', 'cuesta', 'costar', 'rebaja')),
    ('llama', ('quema', 'quemar', 'fuego', 'inflacion', 'arde')),
    ('laptop', ('internet', 'online', 'computadora', 'pantalla', 'trading', 'digital', 'pagina')),
    ('bitcoin', ('bitcoin', 'cripto', 'blockchain')),
    ('barco', ('barco', 'mar=', 'mares', 'navio', 'puerto', 'maritim')),
    ('avion', ('avion', 'vuelo', 'viaje', 'viajar', 'vacacion', 'aeropuerto')),
    ('globo', ('mundo', 'pais', 'paises', 'global', 'inglaterra', 'europa', 'america', 'planeta', 'historia')),
    ('pastel', ('porcentaje', 'reparto', 'repart', 'mitad', 'quinta', 'cuarta', 'tercera', 'parte=', 'partes')),
    ('mapa', ('camino', 'ruta', 'plan=', 'paso=', 'pasos', 'guia', 'destino')),
    ('escudo', ('proteg', 'seguro', 'seguros', 'defens', 'cuidar', 'blind')),
    ('candado', ('candado', 'bloque', 'contrasena', 'privad', 'clave=')),
    ('lupa', ('revis', 'investig', 'busca', 'buscar', 'detalle', 'analiz', 'verific', 'fijate', 'mira=')),
    ('reloj', ('hora=', 'horas', 'tiempo', 'minuto', 'espera', 'esperar', 'plazo', 'tarde=', 'rapido', 'ahora=', 'segundos')),
    ('calendario', ('dia=', 'dias', 'mes=', 'meses', 'ano=', 'anos', 'semana', 'fecha', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')),
    ('casa', ('casa=', 'casas', 'hogar', 'vivienda', 'renta=', 'alquiler', 'apartamento', 'inmueble', 'terreno')),
    ('auto', ('carro', 'coche', 'auto=', 'autos', 'vehiculo', 'motor=', 'camioneta')),
    ('carrito', ('comprar', 'compras', 'compra=', 'compro', 'compran', 'comprando', 'carrito', 'supermercado', 'mercado=')),
    ('tienda', ('tienda', 'negocio', 'comercio', 'local=', 'vendedor', 'vende', 'venden', 'vender', 'vendio')),
    ('cajero', ('cajero', 'retir', 'efectivo', 'sacar', 'deposit')),
    ('telefono', ('celular', 'telefono', 'movil', 'mensaje', 'app=', 'aplicacion', 'notifica', 'redes', 'llamada')),
    ('moneda', ('centavos', 'cambio=', 'moneda=')),
]
LEX_CUERPO = [('corazon', ('corazon', 'latid', 'cardi', 'arteria')), ('cerebro', ('cerebr', 'mentes', 'mente=', 'neurona', 'pensamiento', 'memoria')), ('ojo', ('ojos', 'ojo=', 'retina', 'vision')), ('hueso', ('hueso', 'esquelet', 'fractur')), ('craneo', ('craneo', 'calavera')), ('pulmon', ('pulmon', 'respir', 'oxigeno', 'aliento')), ('estomago', ('estomago', 'digest', 'intestin', 'hambre', 'comer=', 'comida')), ('adn', ('adn=', 'genes', 'genetic', 'cromosom')), ('celula', ('celula', 'tejido', 'organo')), ('bacteria', ('bacteri', 'microb')), ('virus', ('virus=', 'infecci', 'contagi')), ('microscopio', ('microscop', 'laboratorio', 'cientific', 'experiment', 'ciencia')), ('diente', ('diente', 'muela', 'dental')), ('gota', ('sangre', 'herida', 'sangr')), ('agua', ('agua', 'liquid', 'hidrat', 'beber', 'sudor', 'lagrim')), ('luna', ('dormir', 'duerm', 'sueno', 'insomnio', 'noche=', 'noches')), ('sol', ('sol=', 'solar', 'rayos')), ('arbol', ('arbol', 'bosque', 'planta=', 'plantas')), ('libro', ('libro', 'lectura', 'estudi')), ('taza', ('taza', 'cafe=', 'cafeina')), ('manzana', ('manzana', 'fruta', 'azucar', 'vitamina', 'dieta', 'verdura')), ('termometro', ('fiebre', 'temperatura', 'termometro')), ('pastilla', ('medicin', 'vacuna', 'pastilla', 'farmaco', 'medicament'))]; PERS = ('gente', 'persona', 'personas', 'amigo', 'amiga', 'amigos', 'vecino', 'vecinos', 'familia', 'hombre', 'mujer', 'jefe', 'cliente', 'clientes', 'nino', 'padre', 'madre', 'hijo', 'hija', 'esposo', 'esposa', 'pareja', 'compan', 'trabajador', 'empleado', 'banquero', 'inversionista', 'estafador', 'abuelo', 'abuela', 'vendedor', 'tu=', 'usted', 'alguien', 'nadie', 'quien', 'otros', 'cualquiera')
FORMAL = ('banquero', 'jefe', 'empresa', 'ejecutivo', 'abogado', 'inversionista', 'director', 'ministro', 'rey', 'cientifico', 'fisico')
STOPCAP = set(nm(x) for x in ('Año', 'Pero', 'Entonces', 'Si', 'Cuando', 'Y', 'El', 'La', 'Los', 'Las', 'Un', 'Una', 'Te', 'Tu', 'Tú', 'Ese', 'Esa', 'Esta', 'Este', 'Regla', 'Envíaselo', 'Sígueme', 'Guárdalo', 'Lo', 'Le', 'Les', 'Nadie', 'Todos', 'Cada', 'Hoy', 'Ayer', 'Mañana', 'Pero', 'Aquí', 'Ahí', 'Así', 'Solo', 'Sin', 'Con', 'Por', 'Para', 'Como', 'Que', 'Qué', 'Cómo', 'Por', 'Eso', 'Esto', 'Ahora', 'Después', 'Antes', 'Luego', 'Imagina', 'Mira', 'Piensa', 'Sabías', 'Esto', 'Dato', 'Primero', 'Segundo', 'Tercero', 'Vende', 'Vuelve', 'Dijo', 'Te', 'Tu', 'En', 'A', 'De', 'No', 'Sí', 'Hay', 'Fue', 'Era', 'Tenía', 'Había', 'Resultado', 'Moraleja', 'Conclusión', 'Atención', 'Ojo', 'Cuidado', 'Error', 'Verdad', 'Mentira', 'Mito', 'Realidad', 'Truco', 'Consejo', 'Dinero', 'Banco'))
NEG = ('perd', 'error', 'miedo', 'cay', 'caid', 'quiebr', 'deuda', 'pobre', 'fracas', 'estaf', 'enga', 'robo', 'peligro', 'riesgo', 'cuidado', 'trampa', 'arruin', 'desplom', 'crisis', 'ignor', 'culpa', 'mal=', 'tragedia', 'pesadilla', 'perdi')
POS = ('gan', 'exito', 'logr', 'rico', 'riqu', 'crec', 'sube', 'subir', 'ahorr', 'libre', 'gratis', 'mejor', 'feliz', 'aprend', 'celebr', 'millon')
ANIMO = (
    ('triste', ('perd', 'error', 'miedo', 'llor', 'quiebr', 'deuda', 'fracas', 'cay', 'arrepent', 'arruin', 'desplom', 'pobre', 'trist', 'no aguanta')),
    ('sorpresa', ('sorpr', 'descubr', 'increible', 'dispar', 'de repente', 'inesperad', 'impactad', 'todo lo', 'vuelve a compr')),
    ('feliz', ('gan', 'exito', 'logr', 'feliz', 'riqu', 'rico', 'celebr', 'content', 'aprend')),
)
ACCION = (
    ('paga', ('pag', 'compr', 'invert', 'invier', 'gast', 'tarjeta', 'cobr')),
    ('piensa', ('pens', 'duda', 'decid', 'pregunt', 'imagin', 'cree', 'creer', 'cuestion', 'sientes')),
    ('cuenta', ('cuent', 'ahorr', 'junt', 'sald', 'dinero', 'ingres')),
    ('corre', ('corr', 'apur', 'prisa', 'huye')),
    ('camina', ('camin', 'viaj', 'llega', 'sale', 'salio', 'va=', 'ir=')),
)
PESO = {'bombilla': 1, 'alerta': 1, 'etiqueta': 1, 'carrito': 1, 'pastel': 1, 'globo': 1, 'mapa': 1, 'balanza': 1, 'burbuja': 2, 'calendario': 1, 'lupa': 1}
TUYO = ('tu=', 'tus=', 'te=', 'puedes', 'tienes', 'estas=', 'usted', 'sientes', 'quieres', 'haces', 'eres=', 'vas=', 'sigueme', 'comparte', 'guarda', 'envia')
FONDOS = ['jean', 'noche', 'carbon', 'verde', 'naranja']
PIEL = ['claro', 'medio', 'moreno', 'oscuro']
PELO = ['negro', 'castano', 'rubio', 'marron', 'gris', 'rojo']
PEIN = ['corto', 'largo', 'afro', 'corto', 'largo']
CAMI = ['azul', 'verde', 'rojo', 'amarillo', 'morado', 'naranja', 'gris']
CTA = ('siguem', 'suscrib', 'comparte', 'envia', 'guarda', 'comenta', 'follow')


def _hit(tok, stems):
    for s in stems:
        if s.endswith('='):
            if tok == s[:-1]:
                return True
        elif len(s) >= 3 and tok.startswith(s):
            return True
    return False


def _hit_any(nms, stems):
    for n in nms:
        if _hit(n, stems):
            return True
    return False


def _any(text, stems):
    for s in stems:
        s = s.replace('=', '')
        if s in text:
            return True
    return False


def _look(key, st):
    h = sum(ord(c) * (i + 3) for i, c in enumerate(key))
    return {'piel': PIEL[h % 4], 'pelo': PELO[(h // 3) % 6], 'peinado': PEIN[(h // 5) % 5], 'camisa': CAMI[(h // 7) % 7], 'pantalon': 'marino' if h % 2 else 'negro'}


def _layout(person, objs):
    n = len(objs)
    if person and n == 0:
        return {'p': (360, 560, 1.15), 'o': []}
    if not person and n == 1:
        return {'o': [(360, 520, 1.15)]}
    if person and n == 1:
        return {'p': (215, 570, 0.85), 'o': [(540, 570, 0.8)]}
    if not person and n == 2:
        return {'o': [(190, 520, 0.75), (530, 580, 0.75)]}
    if person and n >= 2:
        return {'p': (215, 590, 0.8), 'o': [(545, 420, 0.55), (545, 760, 0.55)]}
    return {'o': [(360, 380, 0.65), (190, 740, 0.55), (530, 740, 0.55)]}


def dirigir_una(texto, st, es_primera=False, es_ultima=False):
    words = TOK.findall(texto)
    nms = [nm(w) for w in words]
    low = nm(texto)
    # cierre / llamado a la accion
    if es_ultima and _any(low, CTA):
        return {'plantilla': 'cierre', 'fondo': 'naranja', 'p': {'titulo': st.get('cta_titulo', 'Si te sirvió, compártelo'), 'acciones': st.get('cta_acciones', ['Envíaselo a un amigo', 'Guárdalo', 'Sígueme'])}}
    capas = []
    # nombres propios
    nombre = None
    for i, w in enumerate(words):
        if w[:1].isupper() and nm(w) not in STOPCAP and not w.isdigit():
            nxt = words[i + 1] if i + 1 < len(words) else ''
            if i > 0 or nxt[:1].isupper() or nm(w) in st['names']:
                nombre = w if not (nxt[:1].isupper() and nm(nxt) not in STOPCAP and i == 0) else w + ' ' + nxt
                break
    if nombre:
        st['names'].add(nm(nombre.split()[0]))
        st['names'].add(nm(nombre.split()[-1]))
        st['named'].add(nm(nombre.split()[0]))
        st['named'].add(nm(nombre.split()[-1]))
    # persona generica
    pers_tok = None
    for w, n in zip(words, nms):
        if _hit(n, PERS):
            pers_tok = w
            break
    if nombre:
        st['prota'] = nombre.split()[0]
    elif not pers_tok and st.get('prota') and not _hit_any(nms, TUYO):
        pers_tok = st['prota']
    person = bool(nombre or pers_tok)
    # objetos por palabra clave (orden de aparicion)
    objs = []
    for w, n in zip(words, nms):
        for kind, stems in st.get('LEX', LEX):
            if stems and _hit(n, stems):
                if kind not in [o[0] for o in objs]:
                    objs.append((kind, w))
                break
    # no repetir el objeto principal de la escena anterior si hay alternativa
    prev = st.get('prev_obj')
    if len(objs) > 1 and objs[0][0] == prev:
        objs = objs[1:] + objs[:1]
    maxo = 1 if person else 2
    if person and len(objs) >= 2:
        maxo = 2
    if len(objs) > maxo:
        keep = sorted(range(len(objs)), key=lambda i: (-PESO.get(objs[i][0], 2), i))[:maxo]
        objs = [objs[i] for i in sorted(keep)]
    st['prev_obj'] = objs[0][0] if objs else None
    # numeros
    y = re.search('(1[0-9]{3}|20[0-9]{2})', texto)
    pct = re.search('([0-9]+[.,]?[0-9]*) ?(%|por ciento)', texto)
    money = re.search('([$€£]) ?([0-9][0-9.,]*)|([0-9][0-9.,]*) ?(mil |millones |millon )?(dolares|dólares|pesos|euros|libras|usd|dop)', texto)
    dur = re.search('([0-9]+) (horas|días|dias|meses|años|anos|semanas|minutos|segundos)', texto)
    top = 130
    if y:
        capas.append({'t': 'txt', 'texto': y.group(1), 'x': 360, 'y': top, 'tam': 130, 'cue': y.group(1)})
    if money:
        if money.group(1):
            pre, val = money.group(1), money.group(2)
        else:
            val = money.group(3)
            cw = nm(money.group(5))
            pre = '£' if cw.startswith('libra') else ('€' if cw.startswith('euro') else '$')
        try:
            v = float(re.sub('[.,](?=[0-9][0-9][0-9]([^0-9]|$))', '', val).replace(',', '.').rstrip('.'))
        except Exception:
            v = None
        if v is not None:
            if y:
                capas.append({'t': 'pill', 'texto': pre + val.rstrip('.,'), 'x': 360, 'y': 270, 'tam': 46, 'cue': val.rstrip('.,')})
            else:
                capas.append({'t': 'num', 'valor': v, 'prefijo': pre, 'x': 360, 'y': top, 'tam': 120, 'cue': val.rstrip('.,')})
    if pct:
        neg = _any(low, NEG)
        capas.append({'t': 'pill', 'texto': ('-' if neg else '+') + pct.group(1) + '%', 'x': 560 if person else 200, 'y': 230, 'tam': 44, 'cue': pct.group(1)})
    if dur and not y:
        capas.append({'t': 'pill', 'texto': dur.group(0), 'x': 360, 'y': 860, 'tam': 40, 'cue': dur.group(1)})
    lay = _layout(person, objs)
    neg = _any(low, NEG)
    pos = _any(low, POS)
    # persona
    if person:
        key = nm((nombre or pers_tok or 'x').split()[0])
        if key not in st['looks']:
            st['looks'][key] = _look(key, st)
        lk = dict(st['looks'][key])
        animo = 'neutral'
        for a, stems in ANIMO:
            if _any(low, stems):
                animo = a
                break
        accion = ''
        for a, stems in ACCION:
            if _any(low, stems):
                accion = a
                break
        if animo == 'feliz' and accion in ('paga', 'cuenta'):
            accion = ''
        if animo in ('triste', 'sorpresa') and accion in ('camina', 'corre'):
            accion = ''
        px, py, pe = lay.get('p', (360, 540, 1.25))
        c = {'t': 'obj', 'objeto': 'persona', 'animo': animo, 'accion': accion, 'x': px, 'y': py, 'escala': pe, 'campo': False, 'cue': (nombre or pers_tok).split()[0]}
        c.update(lk)
        if _any(low, FORMAL) or (nombre and st.get('formal')):
            c['ropa'] = 'saco'
            c['peinado'] = c.get('peinado') if not st.get('peluca') else 'peluca'
        if nombre and nm(nombre.split()[0]) not in st['named_pill']:
            st['named_pill'].add(nm(nombre.split()[0]))
            st['named_pill'].add(nm(nombre.split()[-1]))
            capas.append({'t': 'pill', 'texto': nombre, 'x': px, 'y': min(930, py + 340 * pe + 30), 'tam': 38, 'cue': nombre.split()[0]})
        capas.append(c)
    for (kind, w), (ox, oy, oe) in zip(objs, lay.get('o', [])):
        capas.append({'t': 'obj', 'objeto': kind, 'escala': oe, 'x': ox, 'y': oy, 'cue': w, 'campo': False})
    if not person and not objs:
        # sin objeto reconocido: icono + frase clave destacada
        icono = 'pregunta' if '¿' in texto else ('alerta' if neg else ('check' if pos else 'estrella'))
        capas.append({'t': 'icono', 'i': icono, 'x': 360, 'y': 330, 'tam': 110, 'cue': words[0] if words else None})
        cont = [w for w, n in zip(words, nms) if len(n) > 4 and n not in STOPCAP]
        cont = sorted(cont, key=lambda s: -len(s))[:2]
        if cont:
            capas.append({'t': 'txt', 'texto': '*' + cont[0] + '*' + (' ' + cont[1] if len(cont) > 1 else ''), 'x': 360, 'y': 640, 'tam': 100, 'cue': cont[0]})
    # fondo
    if neg and not pos:
        fondo = 'noche' if st.get('prev_fondo') == 'carbon' else 'carbon'
    elif pos and not neg:
        fondo = 'verde' if st.get('prev_fondo') != 'verde' else 'naranja'
    else:
        k = st.get('fi', 0)
        fondo = FONDOS[k % len(FONDOS)]
        if fondo == st.get('prev_fondo'):
            fondo = FONDOS[(k + 1) % len(FONDOS)]
            k += 1
        st['fi'] = k + 1
    st['prev_fondo'] = fondo
    return {'plantilla': 'escena', 'fondo': fondo, 'p': {'capas': capas}}


def autocompletar(escenas, guion=None, opciones=None):
    # acepta: escenas con solo texto (se dirigen solas) o ya armadas (se respetan)
    st = {'names': set(), 'named': set(), 'named_pill': set(), 'looks': {}, 'prev_obj': None, 'prev_fondo': None, 'fi': 0}
    st.update(opciones or {}); st['LEX'] = (LEX_CUERPO + LEX) if st.get('lexico') == 'cuerpo' else (LEX + LEX_CUERPO)
    if guion and not escenas:
        txt = guion if isinstance(guion, str) else ' '.join(guion)
        partes = re.split('(?<=[.!?…])  *', txt.strip()) if isinstance(guion, str) else list(guion)
        escenas = [{'texto': p.strip()} for p in partes if p.strip()]
    n = len(escenas)
    out = []
    for i, sc in enumerate(escenas):
        if sc.get('plantilla'):
            out.append(sc)
            continue
        d = dirigir_una(sc['texto'], st, i == 0, i == n - 1)
        d['texto'] = sc['texto']
        out.append(d)
    return out

