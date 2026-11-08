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


GAP = 0.2         # silencio entre escenas (respiro natural entre frases)
MIN_DUR = 0.7
TAIL = 0.6
PAUSA_MAX = 0.2   # tope de cada pausa dentro de una escena (edge-tts deja 0.5 a 0.8 s tras cada punto)
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


def compacta(mp3, ev, wav):
    # Quita el silencio del inicio y del final y deja cada pausa interna en PAUSA_MAX como mucho.
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
        elif tb - ta > PAUSA_MAX:
            cortes.append((ta + PAUSA_MAX / 2, tb - PAUSA_MAX / 2))
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


def voz(job, work):
    voz_n = job.get('voz_edge', 'es-MX-JorgeNeural')
    rate = job.get('rate', '+8%')
    pitch = job.get('pitch', '+2Hz')
    escenas = job['escenas']
    lista, palabras, t0 = [], [], 0.0
    for i, sc in enumerate(escenas):
        mp3 = os.path.join(work, 'v%02d.mp3' % i)
        ev = tts_seguro(sc['texto'], voz_n, tono(sc, 'rate', rate, r'^[+-]\d{1,2}%$'), tono(sc, 'pitch', pitch, r'^[+-]\d{1,2}Hz$'), mp3)
        pausa = min(float(tono(sc, 'pausa', '0', r'^\d(\.\d+)?$')), 0.4)
        if not os.path.exists(mp3) or os.path.getsize(mp3) < 500:
            raise RuntimeError('sin audio en escena %d' % i)
        tr = os.path.join(work, 't%02d.wav' % i)
        d, ev = compacta(mp3, ev, tr)
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
