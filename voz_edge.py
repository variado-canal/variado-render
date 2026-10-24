#!/usr/bin/env python3
# Voz gratis (edge-tts, Jorge) escena por escena, sin pausas largas + cortes de imagen mas rapidos.
# Uso: RENDER_SCRIPT=render|render_dinero python3 voz_edge.py jobs/<id>/job.json salida.mp4
import asyncio
import base64
import importlib
import json
import os
import sys

R = importlib.import_module('render')
D = importlib.import_module(os.environ.get('RENDER_SCRIPT', 'render'))

VOZ = 'es-MX-JorgeNeural'
RATE = '+8%'
PITCH = '+2Hz'
GAP = 0.05
CORTE = 54  # frames entre cortes de imagen (1.8 s a 30 fps)
LIMPIA = ('silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:'
          'stop_duration=0.14:stop_threshold=-45dB:stop_silence=0.04,'
          'apad=pad_dur=%.2f,aresample=44100' % GAP)


def parchear(modulo):
    """Cortes de imagen mas seguidos: zoom que se reinicia y cambia de encuadre cada 1.8 s."""
    ruta = modulo.__file__
    with open(ruta, encoding='utf-8') as f:
        t = f.read()
    cambios = [
        ('"1+0.14*on/%d" % frames', '"1.03+0.05*mod(on,%d)/%d+0*%%d" %% frames' % (CORTE, CORTE)),
        ('"1.14-0.14*on/%d" % frames', '"1.08-0.05*mod(on,%d)/%d+0*%%d" %% frames' % (CORTE, CORTE)),
        ("x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'",
         "x='iw/2-iw/zoom/2+(mod(floor(on/%d),2)*2-1)*iw*0.012':y='ih/2-ih/zoom/2+(mod(floor(on/%d)+1,2)*2-1)*ih*0.008'" % (CORTE, CORTE)),
    ]
    n = 0
    for a, b in cambios:
        if a in t:
            n += t.count(a)
            t = t.replace(a, b)
    os.makedirs('work_voz', exist_ok=True)
    nuevo = os.path.join('work_voz', os.path.basename(ruta))
    with open(nuevo, 'w', encoding='utf-8') as f:
        f.write(t)
    print('parche cortes %s: %d cambios' % (os.path.basename(ruta), n))
    return nuevo


async def _tts(texto, path):
    import edge_tts
    await edge_tts.Communicate(texto, VOZ, rate=RATE, pitch=PITCH).save(path)


def generar(job, work):
    os.makedirs(work, exist_ok=True)
    partes, durs = [], []
    for i, s in enumerate(job['escenas']):
        p = '%s/e%02d.mp3' % (work, i)
        ok = False
        for intento in range(3):
            try:
                asyncio.run(_tts(' '.join(str(s['texto']).split()), p))
                if os.path.getsize(p) > 1000:
                    ok = True
                    break
            except Exception as e:
                print('edge-tts fallo escena %d intento %d: %s' % (i + 1, intento + 1, e), file=sys.stderr)
        if not ok:
            raise SystemExit('edge-tts no pudo generar la voz de la escena %d' % (i + 1))
        w = '%s/e%02d.wav' % (work, i)
        R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p, '-af', LIMPIA, '-ac', '1', w])
        partes.append(w)
        durs.append(R.duration(w))
    lst = work + '/voz_list.txt'
    with open(lst, 'w') as f:
        for w in partes:
            f.write('file ' + os.path.basename(w) + chr(10))
    mp3 = work + '/voz_edge.mp3'
    R.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
           '-c:a', 'libmp3lame', '-q:a', '2', mp3])
    return mp3, durs


def main():
    job_path, out_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding='utf-8') as f:
        job = json.load(f)
    if job.get('audio_b64') or not job.get('escenas'):
        return D.main()
    mp3, durs = generar(job, 'work_voz')
    textos = [s.get('texto', '') for s in job['escenas']]
    mapa = {}
    for t, d in zip(textos, durs):
        mapa[t] = d
    mapa[textos[-1]] = mapa[textos[-1]] + R.TAIL
    R.peso = lambda texto: mapa.get(texto, 3.0)
    with open(mp3, 'rb') as f:
        job['audio_b64'] = base64.b64encode(f.read()).decode()
    job['velocidad'] = 1.0
    with open('job_edge.json', 'w', encoding='utf-8') as f:
        json.dump(job, f)
    sys.argv = [sys.argv[0], 'job_edge.json', out_path]
    D.main()


if __name__ == '__main__':
    # Parchear copias (no el repositorio) y ponerlas primero en el path
    for nombre in ('render', os.environ.get('RENDER_SCRIPT', 'render')):
        try:
            m = importlib.import_module(nombre)
            parchear(m)
        except Exception as e:
            print('sin parche en', nombre, e)
    sys.path.insert(0, os.path.abspath('work_voz'))
    for nombre in ('render', os.environ.get('RENDER_SCRIPT', 'render')):
        sys.modules.pop(nombre, None)
    R = importlib.import_module('render')
    D = importlib.import_module(os.environ.get('RENDER_SCRIPT', 'render'))
    main()

