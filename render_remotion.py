# Render con Remotion (estilo explicativo animado) para Variado y Dinero.
# Uso: python3 render_remotion.py jobs/<id>/job.json video-<id>.mp4
# Voz igual que render_motion.py: edge-tts por escena con voz/rate/pitch del job,
# se recorta el silencio final de cada escena y se deja la misma pausa (GAP/MIN_DUR/TAIL).
# La escena (TSX) viene en escenas[i].p.remotion_tsx del job; si falta o falla, sale con error
# y render.yml cae al motor anterior (render_motion.py).
import asyncio, json, os, re, shutil, subprocess, sys, wave

import unicodedata


def _norm(x):
    s = unicodedata.normalize('NFD', str(x).lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s)


GAP = 0.06
MIN_DUR = 1.1
TAIL = 0.6
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
        ev = asyncio.run(_tts(sc['texto'], voz_n, rate, pitch, mp3))
        if not os.path.exists(mp3) or os.path.getsize(mp3) < 500:
            raise RuntimeError('sin audio en escena %d' % i)
        tr = os.path.join(work, 't%02d.mp3' % i)
        sh([FF, '-y', '-v', 'error', '-i', mp3, '-af', 'areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,areverse', tr])
        if os.path.getsize(tr) > 500:
            mp3 = tr
        d = dur_audio(mp3, work)
        dur = max(MIN_DUR, d + GAP) + (TAIL if i == len(escenas) - 1 else 0)
        wav = os.path.join(work, 'v%02d.wav' % i)
        sh([FF, '-y', '-v', 'error', '-i', mp3, '-ar', '44100', '-ac', '1', '-af', 'apad=whole_dur=%.3f' % dur, wav])
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


def main():
    job_path, out = sys.argv[1], os.path.abspath(sys.argv[2])
    job = json.load(open(job_path, encoding='utf-8'))
    tsx = next((sc.get('p', {}).get('remotion_tsx') for sc in job['escenas'] if isinstance(sc.get('p'), dict) and sc['p'].get('remotion_tsx')), None)
    if not tsx:
        raise SystemExit('El job no trae remotion_tsx')
    work = os.path.join(os.path.dirname(out), 'work_rm_' + str(job.get('job_id', 'x')))
    os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.join(RM, 'public'), exist_ok=True)
    data = voz(job, work)
    json.dump(data, open(os.path.join(RM, 'public', 'palabras.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(RM, 'src', 'Escena.tsx'), 'w', encoding='utf-8').write(tsx)
    npx = 'npx.cmd' if os.name == 'nt' else 'npx'
    if not os.path.isdir(os.path.join(RM, 'node_modules')):
        sh(['npm.cmd' if os.name == 'nt' else 'npm', 'ci', '--no-audit', '--no-fund'], cwd=RM)
    sh([npx, 'remotion', 'render', 'src/index.ts', 'Video', out, '--log=error'], cwd=RM)
    shutil.rmtree(work, ignore_errors=True)
    print('listo', out, data['dur'], 's')


if __name__ == '__main__':
    main()
