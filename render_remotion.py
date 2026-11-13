# Render con Remotion (estilo explicativo animado) para Variado y Dinero.
# Uso: python3 render_remotion.py jobs/<id>/job.json video-<id>.mp4
# Voz igual que render_motion.py: edge-tts por escena con voz/rate/pitch del job.
# 8-nov: se acortan los silencios de edge-tts (inicio, entre frases y entre escenas) para que suene
# hablado y no leído; los tiempos de cada palabra se corrigen con los cortes.
# La escena (TSX) viene en escenas[i].p.remotion_tsx del job; si falta o falla, sale con error
# y entra la reparación automática.
import array, asyncio, json, os, re, shutil, subprocess, sys, time, wave

import unicodedata


def _norm(x):
    s = unicodedata.normalize('NFD', str(x).lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s)


GAP = 0.4         # silencio entre escenas (fin de idea: deja asimilar)
MIN_DUR = 0.7
TAIL = 0.6
# Tope de cada pausa dentro de una escena según la puntuación del guion (edge-tts deja 0.5 a 0.8 s tras cada punto).
PAUSA_PUNTO = 0.4
PAUSA_COMA = 0.2
PAUSA_OTRA = 0.12
INICIO = 0.03     # silencio que se deja al empezar cada escena
SIL_DB = -40      # por debajo de esto es silencio
FF = os.environ.get('FFMPEG', 'ffmpeg')
AQUI = os.path.dirname(os.path.abspath(__file__))
RM = os.path.join(AQUI, 'remotion')


def sh(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def dur_audio(path, work):
    # Duración exacta pasando a wav (no depende de ffprobe)
    tmp = os.path.join(work, '_dur.wav')
    sh([FF, '-y', '-v', 'error', '-i', path, '-ar', '44100', '-ac', '1', tmp])
    with wave.open(tmp, 'rb') as w:
        return w.getnframes() / w.getframerate()


async def _tts(texto, voz, rate, pitch, mp3):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch, boundary='WordBoundary')
    ev = []
    with open(mp3, 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                ev.append((ch['offset'] / 1e7, ch['duration'] / 1e7))
    return ev


def tono(sc, campo, defecto, patron):
    # Tono por escena (p.voz: rate/pitch/pausa) para dar emoción; si viene mal, usa el del job.
    p = sc.get('p') if isinstance(sc.get('p'), dict) else {}
    tv = p.get('voz') if isinstance(p.get('voz'), dict) else {}
    v = str(tv.get(campo, ''))
    return v if re.match(patron, v) else defecto


def tts_seguro(texto, voz, rate, pitch, mp3):
    # edge-tts a veces no devuelve audio: se reintenta antes de fallar.
    for n in range(4):
        try:
            return asyncio.run(_tts(texto, voz, rate, pitch, mp3))
        except Exception:
            if n == 3:
                raise
            time.sleep(5 * (n + 1))


def tope_pausa(t, ev, ws):
    # La pausa que empieza en t sigue a la última palabra dicha antes: su puntuación decide el largo.
    if len(ev) != len(ws):
        return PAUSA_PUNTO if t > 0 else PAUSA_OTRA
    i = max([k for k, (o, d) in enumerate(ev) if o + d <= t + 0.06] or [-1])
    w = ws[i] if i >= 0 else ''
    if re.search(r'[.!?…]$', w):
        return PAUSA_PUNTO
    if re.search(r'[,;:]$', w):
        return PAUSA_COMA
    return PAUSA_OTRA


def compacta(mp3, ev, wav, texto=''):
    # Quita el silencio del inicio y del final y deja cada pausa interna en su tope según la puntuación.
    # Devuelve la duración nueva y los tiempos de palabra movidos según lo cortado.
    sh([FF, '-y', '-v', 'error', '-i', mp3, '-ar', '44100', '-ac', '1', '-sample_fmt', 's16', wav])
    with wave.open(wav, 'rb') as w:
        sr = w.getframerate()
        x = array.array('h', w.readframes(w.getnframes()))
    if sys.byteorder == 'big':
        x.byteswap()
    win = sr // 100
    n = len(x) // win
    if n < 5:
        return len(x) / sr, ev
    umbral = 32768 * 10 ** (SIL_DB / 20)
    sil = [max(x[i * win:(i + 1) * win]) < umbral and -min(x[i * win:(i + 1) * win]) < umbral for i in range(n)]
    total = len(x) / sr
    ws = texto.split()
    cortes, i = [], 0
    while i < n:
        if not sil[i]:
            i += 1
            continue
        j = i
        while j < n and sil[j]:
            j += 1
        ta, tb = i / 100, (total if j == n else j / 100)
        if i == 0:
            if tb - INICIO > 0:
                cortes.append((0.0, tb - INICIO))
        elif j == n:
            cortes.append((ta + 0.02, total))
        else:
            tope = tope_pausa(ta, ev, ws)
            if tb - ta > tope:
                cortes.append((ta + tope / 2, tb - tope / 2))
        i = j
    if not cortes:
        return total, ev
    y, a = array.array('h'), 0
    for c0, c1 in cortes:
        y.extend(x[a:int(c0 * sr)])
        a = int(c1 * sr)
    y.extend(x[a:])
    if sys.byteorder == 'big':
        y.byteswap()
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(y.tobytes())

    def mueve(t):
        q = 0.0
        for c0, c1 in cortes:
            if t >= c1:
                q += c1 - c0
            elif t > c0:
                q += t - c0
        return t - q
    ev2 = []
    for o, dd in ev:
        o2 = mueve(o)
        ev2.append((o2, max(0.05, mueve(o + dd) - o2)))
    return len(y) / sr, ev2


def alinea(texto, ev, d):
    # Palabras del texto (con su puntuación) con el tiempo de la voz; si no cuadran, reparte por largo.
    ws = texto.split()
    if not ev or abs(len(ev) - len(ws)) > max(2, len(ws) // 4):
        tot = sum(len(w) + 1 for w in ws) or 1
        out, t = [], 0.0
        for w in ws:
            dd = d * (len(w) + 1) / tot
            out.append((w, t, dd))
            t += dd
        return out
    out = []
    for i, w in enumerate(ws):
        j = min(int(round(i * (len(ev) - 1) / max(len(ws) - 1, 1))), len(ev) - 1) if len(ev) != len(ws) else i
        out.append((w, ev[j][0], ev[j][1]))
    return out


# Voz Gemini (13-nov): el guion entero en UNA toma con Achird para que las pausas salgan por intención.
# Clave en el secreto GEMINI_API_KEY del repo. Nivel gratis: 10 audios/día por modelo, por eso se prueban
# varios; si todos fallan (429, sin clave), sigue la voz edge de siempre.
G_MODELOS = ['gemini-3.8-flash-tts', 'gemini-3.1-flash-tts-preview', 'gemini-3.8-flash-lite-tts']
G_ESTILO = ('Narrador latinoamericano de un video corto, hablándole a un amigo. '
            'La primera frase ABRE el video: nadie le preguntó nada, así que no suena a respuesta ni a continuación; '
            'arranca arriba, con la seguridad de quien suelta un dato que sorprende. '
            'Dicción limpia de español neutro: pronuncia cada palabra completa, con todas sus eses '
            '(tres veces, nunca tre vece) y sin comerse sílabas finales. '
            'Natural y conversacional, nada de locutor. Ritmo vivo pero sin prisa. Pausas según la intención: '
            'muy cortas en la explicación, algo más largas antes de una revelación. Sin pausas en las comas del gancho.')


def _gemini(texto, voz_g, estilo, wav):
    import base64, urllib.request
    clave = os.environ.get('GEMINI_API_KEY', '')
    if not clave:
        return False
    for m in G_MODELOS:
        body = {'model': m, 'input': [{'type': 'user_input', 'content': [{'type': 'text', 'text': texto,
                'annotations': [{'type': 'speech_metadata', 'style': estilo}]}]}],
                'response_format': {'type': 'audio'}, 'generation_config': {'speech_config': [{'voice': voz_g}]}}
        req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/interactions',
                                     data=json.dumps(body).encode('utf-8'), method='POST',
                                     headers={'x-goog-api-key': clave, 'Content-Type': 'application/json'})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            data = next(c['data'] for s in r.get('steps', []) for c in (s.get('content') or []) if c.get('data'))
            raw = base64.b64decode(data)
            if raw[:4] != b'RIFF':
                with wave.open(wav, 'wb') as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)
            else:
                open(wav, 'wb').write(raw)
            print('voz gemini con', m)
            return True
        except Exception as e:
            print('voz gemini', m, 'falló:', str(e)[:120])
    return False


def _silencios(wav):
    # Silencios internos (inicio, fin) para cortar escenas donde la voz respira.
    p = subprocess.run([FF, '-v', 'info', '-i', wav, '-af', 'silencedetect=n=-38dB:d=0.12', '-f', 'null', '-'],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', p.stderr)]
    fin = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', p.stderr)]
    return list(zip(ini, fin))


def voz_gemini(job, work):
    escenas = job['escenas']
    crudo = os.path.join(work, 'g_crudo.wav')
    if not _gemini(' '.join(sc['texto'].strip() for sc in escenas), job.get('voz_gemini', 'Achird'),
                   job.get('estilo_voz', G_ESTILO), crudo):
        return None
    limpio = os.path.join(work, 'g.wav')
    sh([FF, '-y', '-v', 'error', '-i', crudo, '-ar', '44100', '-ac', '1', '-af',
        'silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse', limpio])
    total = dur_audio(limpio, work)
    sil = _silencios(limpio)
    # Corte entre escenas: el silencio más cercano a donde tocaría por largo de texto.
    largos = [len(sc['texto']) for sc in escenas]
    cortes, acum, prev = [0.0], 0, 0.0
    for L in largos[:-1]:
        acum += L
        est = total * acum / sum(largos)
        cand = [s for s in sil if (s[0] + s[1]) / 2 > prev + 0.3]
        c = min(cand, key=lambda s: abs((s[0] + s[1]) / 2 - est)) if cand else None
        corte = (c[0] + c[1]) / 2 if c and abs((c[0] + c[1]) / 2 - est) < 2.5 else est
        cortes.append(corte)
        prev = corte
    cortes.append(total)
    lista, palabras, t0 = [], [], 0.0
    for i, sc in enumerate(escenas):
        a, b = cortes[i], cortes[i + 1]
        d = b - a
        dur = max(MIN_DUR, d) + (TAIL if i == len(escenas) - 1 else 0)
        wav = os.path.join(work, 'v%02d.wav' % i)
        sh([FF, '-y', '-v', 'error', '-ss', '%.3f' % a, '-t', '%.3f' % d, '-i', limpio, '-ar', '44100', '-ac', '1',
            '-af', 'apad=whole_dur=%.3f' % dur, wav])
        lista.append(wav)
        primera = True
        for (w, aa, dd) in alinea(sc['texto'], [], d):
            palabras.append({'w': w, 't': round(t0 + aa, 3), 'd': round(dd, 3), 'f': primera})
            primera = bool(re.search(r'[.!?…]$', w))
        t0 += dur
    lst = os.path.join(work, 'lista.txt')
    with open(lst, 'w') as f:
        for w in lista:
            f.write("file '%s'\n" % w.replace('\\', '/'))
    sh([FF, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(RM, 'public', 'voz.wav')])
    return {'dur': round(t0, 3), 'words': palabras}


def voz(job, work):
    if job.get('voz_motor', 'gemini') == 'gemini':
        try:
            data = voz_gemini(job, work)
            if data:
                return data
        except Exception as e:
            print('voz gemini falló, sigo con edge:', str(e)[:160])
    voz_n = job.get('voz_edge', 'es-MX-JorgeNeural')
    rate = job.get('rate', '+8%')
    pitch = job.get('pitch', '+2Hz')
    escenas = job['escenas']
    lista, palabras, t0 = [], [], 0.0
    for i, sc in enumerate(escenas):
        mp3 = os.path.join(work, 'v%02d.mp3' % i)
        ev = tts_seguro(sc['texto'], voz_n, tono(sc, 'rate', rate, r'^[+-]\d{1,2}%$'), tono(sc, 'pitch', pitch, r'^[+-]\d{1,2}Hz$'), mp3)
        pausa = min(float(tono(sc, 'pausa', '0', r'^\d(\.\d+)?$')), 0.8)
        if not os.path.exists(mp3) or os.path.getsize(mp3) < 500:
            raise RuntimeError('sin audio en escena %d' % i)
        tr = os.path.join(work, 't%02d.wav' % i)
        d, ev = compacta(mp3, ev, tr, sc['texto'])
        dur = max(MIN_DUR, d + GAP + pausa) + (TAIL if i == len(escenas) - 1 else 0)
        wav = os.path.join(work, 'v%02d.wav' % i)
        sh([FF, '-y', '-v', 'error', '-i', tr, '-ar', '44100', '-ac', '1', '-af', 'apad=whole_dur=%.3f' % dur, wav])
        lista.append(wav)
        primera = True
        clave = _norm(sc['p'].get('key', '')) if isinstance(sc.get('p'), dict) else ''
        marcada = False
        for (w, a, dd) in alinea(sc['texto'], ev, d):
            k = bool(clave) and not marcada and _norm(w) == clave
            marcada = marcada or k
            palabras.append({'w': w, 't': round(t0 + a, 3), 'd': round(dd, 3), 'f': primera, 'k': k})
            primera = bool(re.search(r'[.!?…]$', w))
        t0 += dur
    lst = os.path.join(work, 'lista.txt')
    with open(lst, 'w') as f:
        for w in lista:
            f.write("file '%s'\n" % w.replace('\\', '/'))
    sh([FF, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', os.path.join(RM, 'public', 'voz.wav')])
    return {'dur': round(t0, 3), 'words': palabras}


def nivela_sfx():
    # Deja todos los efectos al mismo nivel, bajo, para que nunca tapen la voz.
    d = os.path.join(RM, 'public', 'sfx')
    if not os.path.isdir(d):
        return
    for n in sorted(os.listdir(d)):
        a = os.path.join(d, n)
        t = a + '.tmp.mp3'
        sh([FF, '-y', '-v', 'error', '-i', a, '-af', 'loudnorm=I=-24:TP=-6:LRA=7', '-ar', '44100', t])
        os.replace(t, a)


def kit_interpolate(tsx):
    # 8-nov: el interpolate de Remotion rompe si el rango sale desordenado; la escena usa el del kit, que lo ordena.
    def cambiar(m):
        nombres = [n.strip() for n in m.group(1).split(',') if n.strip()]
        if 'interpolate' not in nombres:
            return m.group(0)
        resto = [n for n in nombres if n != 'interpolate']
        antes = ('import {%s} from %sremotion%s;\n' % (', '.join(resto), m.group(2), m.group(2))) if resto else ''
        return antes + "import {interpolate} from './kit';"
    return re.sub(r"import\s*\{([^}]*)\}\s*from\s*(['\"])remotion\2;?", cambiar, tsx)


def main():
    job_path, out = sys.argv[1], os.path.abspath(sys.argv[2])
    job = json.load(open(job_path, encoding='utf-8'))
    tsx = next((sc.get('p', {}).get('remotion_tsx') for sc in job['escenas'] if isinstance(sc.get('p'), dict) and sc['p'].get('remotion_tsx')), None)
    if not tsx:
        raise SystemExit('El job no trae remotion_tsx')
    work = os.path.join(os.path.dirname(out), 'work_rm_' + str(job.get('job_id', 'x')))
    os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.join(RM, 'public'), exist_ok=True)
    nivela_sfx()
    data = voz(job, work)
    json.dump(data, open(os.path.join(RM, 'public', 'palabras.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(RM, 'src', 'Escena.tsx'), 'w', encoding='utf-8').write(kit_interpolate(tsx))
    npx = 'npx.cmd' if os.name == 'nt' else 'npx'
    if not os.path.isdir(os.path.join(RM, 'node_modules')):
        sh(['npm.cmd' if os.name == 'nt' else 'npm', 'ci', '--no-audit', '--no-fund'], cwd=RM)
    gl = []
    if '@remotion/three' in tsx:
        sh(['npm', 'i', '--no-save', '--no-audit', '--no-fund', '@remotion/three@4.0.300', 'three@0.170.0', '@react-three/fiber@8.17.10'], cwd=RM)
        gl = ['--gl=swangle', '--concurrency=2']
    sh([npx, 'remotion', 'render', 'src/index.ts', 'Video', out, '--log=error'] + gl, cwd=RM)
    shutil.rmtree(work, ignore_errors=True)
    print('listo', out, data['dur'], 's')


if __name__ == '__main__':
    main()
