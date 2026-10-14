#!/usr/bin/env python3
"""DINERO render: igual que render.py (voz continua, zoom, subtitulos, musica) y ademas:
- texto del gancho en pantalla los primeros segundos (job.texto_gancho)
- fuente en pantalla al final (job.fuente_pantalla)
- reencuadres distintos cuando una imagen se reutiliza (sin gastar imagenes nuevas)
- efectos de sonido: subida antes de la revelacion y golpe en el giro
  (job.escena_giro y job.escena_revelacion, numeros de escena empezando en 1)
Uso: python3 render_dinero.py jobs/<id>/job.json salida.mp4
Este archivo importa funciones de render.py y no cambia el comportamiento de ese.
"""
import array
import base64
import hashlib
import json
import math
import os
import random
import sys
import wave

import render as R

W, H, FPS, NL, TAIL, SR = R.W, R.H, R.FPS, R.NL, R.TAIL, R.SR


def limpiar(t):
    return ' '.join(str(t).replace('{', '(').replace('}', ')').replace(chr(92), ' ').split())


def envolver(texto, ancho):
    palabras = texto.split()
    lineas, cur = [], ''
    for p in palabras:
        prueba = (cur + ' ' + p).strip()
        if cur and len(prueba) > ancho:
            lineas.append(cur)
            cur = p
        else:
            cur = prueba
    if cur:
        lineas.append(cur)
    return lineas


def escribir_ass(path, texto, hablar, hook=None, hook_hasta=0.0, fuente=None, fuente_desde=0.0, fuente_hasta=0.0):
    """Subtitulos con el estilo de referencia compartido (subs_pro.py): mayusculas, recuadro rojo en la palabra activa."""
    import subs_pro as S
    cabecera = S.cabecera(W, H)
    lineas = S.dialogos(texto, 0.0, hablar, 'Default', 3, 22)
    if hook and hook_hasta > 0.3:
        txt = '\\N'.join(envolver(limpiar(hook).upper(), 15))
        lineas.append('Dialogue: 1,%s,%s,Hook,,0,0,0,,{\\fad(120,300)}%s' % (
            R.ass_time(0.0), R.ass_time(hook_hasta), txt))
    if fuente and fuente_hasta - fuente_desde > 0.5:
        txt = '\\N'.join(envolver(limpiar(fuente), 40))
        lineas.append('Dialogue: 1,%s,%s,Fuente,,0,0,0,,{\\fad(250,250)}%s' % (
            R.ass_time(fuente_desde), R.ass_time(fuente_hasta), txt))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cabecera + NL.join(lineas) + NL)



def sonidos(path, secs, eventos):
    """eventos: lista de (tipo, tiempo). tipo: 'subida' (termina en tiempo) | 'golpe' (empieza en tiempo)."""
    random.seed(11)
    n = int(secs * SR)
    buf = [0.0] * n
    for tipo, t in eventos:
        if tipo == 'golpe':
            R.put_tone(buf, t, 0.45, 52.0, 1.0, 9.0, sweep=1.6)
            R.put_noise(buf, t, 0.30, 0.45, 16.0, hp=0.4)
        elif tipo == 'subida':
            dur = 1.1
            t0 = max(t - dur, 0.0)
            i0 = int(t0 * SR)
            m = int(dur * SR)
            prev = 0.0
            ph = 0.0
            for k in range(m):
                j = i0 + k
                if j >= n:
                    break
                x = k / float(m)
                r = random.uniform(-1.0, 1.0)
                v = r - prev * 0.85
                prev = r
                f = 180.0 + 900.0 * x * x
                ph += 2.0 * math.pi * f / SR
                buf[j] += (0.35 * v + 0.35 * math.sin(ph)) * (x ** 2.2)
            R.put_tone(buf, t, 0.5, 45.0, 1.0, 8.0, sweep=1.8)
            R.put_noise(buf, t, 0.35, 0.40, 14.0, hp=0.5)
    peak = max(1e-9, max(abs(x) for x in buf))
    escala = 0.8 / peak
    salida = array.array('h', (int(max(-1.0, min(1.0, x * escala)) * 32767) for x in buf))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(salida.tobytes())


def main():
    job_path, out_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding='utf-8') as f:
        job = json.load(f)
    if not job.get('audio_b64'):
        raise SystemExit('DINERO: el job necesita audio_b64 (voz continua).')
    work = 'work_render'
    os.makedirs(work, exist_ok=True)
    escenas = job['escenas']
    n = len(escenas)
    raw = '%s/voz.mp3' % work
    with open(raw, 'wb') as f:
        f.write(base64.b64decode(job['audio_b64']))
    voz = '%s/voz_f.mp3' % work
    velocidad = float(job.get('velocidad', R.SPEED))
    R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-filter:a',
           'silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,'
           'atempo=%.2f,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100' % velocidad,
           '-c:a', 'libmp3lame', '-q:a', '2', voz])
    voice = R.duration(voz)
    total = voice + TAIL
    pesos = [float(max(R.peso(s.get('texto', '')), 1)) for s in escenas]
    tw = sum(pesos)
    hook = limpiar(job.get('texto_gancho', '') or '')
    fuente = limpiar(job.get('fuente_pantalla', '') or '')
    if fuente and not fuente.lower().startswith('fuente'):
        fuente = 'Fuente: ' + fuente
    vistas = {}
    inicios = []
    t_acum = 0.0
    clip_files = []
    pan_reuso = [0.0, 1.0, 0.2, 0.8]
    for i, s in enumerate(escenas):
        d = total * pesos[i] / tw
        inicios.append(t_acum)
        t_acum += d
        datos = base64.b64decode(s['imagen_b64'])
        huella = hashlib.md5(datos).hexdigest()
        veces = vistas.get(huella, 0)
        vistas[huella] = veces + 1
        img = '%s/i%02d.jpg' % (work, i)
        with open(img, 'wb') as f:
            f.write(datos)
        habla = d - (TAIL if i == n - 1 else 0.0)
        ass = '%s/s%02d.ass' % (work, i)
        kwargs = {}
        if i == 0 and hook:
            kwargs['hook'] = hook
            kwargs['hook_hasta'] = min(3.0, d - 0.15)
        if i == n - 1 and fuente:
            kwargs['fuente'] = fuente
            kwargs['fuente_desde'] = max(d - 2.8, 0.2)
            kwargs['fuente_hasta'] = d - 0.1
        escribir_ass(ass, s.get('texto', ''), max(habla, 0.5), **kwargs)
        frames = max(int(d * FPS), 1)
        fx = 0.5
        if veces == 0:
            if i % 2 == 0:
                z = "1+0.14*on/%d" % frames
            else:
                z = "1.14-0.14*on/%d" % frames
        elif i == n - 1 and veces > 0 and huella == hashlib.md5(base64.b64decode(escenas[0]['imagen_b64'])).hexdigest():
            # el cierre vuelve al encuadre inicial del video para que el bucle sea continuo
            z = "1.14-0.14*on/%d" % frames
        else:
            fx = pan_reuso[(veces - 1) % len(pan_reuso)]
            if i % 2 == 0:
                z = "1.10+0.20*on/%d" % frames
            else:
                z = "1.30-0.20*on/%d" % frames
        vf = (
            "crop='min(iw,ih*9/16)':ih:'(iw-ow)*%.2f':0,scale=2160:-2:flags=lanczos,"
            "zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=%d:s=%dx%d:fps=%d,"
            "ass=%s,format=yuv420p"
        ) % (fx, z, frames, W, H, FPS, ass)
        clip = '%s/c%02d.mp4' % (work, i)
        R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', img, '-vf', vf, '-an',
               '-t', '%.3f' % d, '-r', str(FPS),
               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', clip])
        clip_files.append(clip)
    lst = '%s/list.txt' % work
    with open(lst, 'w') as f:
        for c in clip_files:
            f.write("file '%s'" % os.path.basename(c) + NL)
    video = '%s/joined_v.mp4' % work
    R.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
           '-i', lst, '-c', 'copy', video])
    joined = '%s/joined.mp4' % work
    R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', voz,
           '-af', 'apad=pad_dur=%.2f,aresample=44100' % TAIL,
           '-map', '0:v', '-map', '1:a', '-t', '%.3f' % total,
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-ac', '2', joined])
    con_fondo = '%s/con_fondo.mp4' % work
    R.add_ambience(joined, con_fondo, job.get('fondo', 'suave'))
    # efectos de sonido
    giro = int(job.get('escena_giro') or max(2, n - 2))
    revel = int(job.get('escena_revelacion') or (n - 1))
    eventos = []
    if 2 <= giro <= n:
        eventos.append(('golpe', inicios[giro - 1] + 0.05))
    if 2 <= revel <= n:
        eventos.append(('subida', inicios[revel - 1]))
    if eventos:
        wav = '%s/sfx.wav' % work
        sonidos(wav, total + 1.0, eventos)
        R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', con_fondo, '-i', wav,
               '-filter_complex',
               '[1:a]aformat=channel_layouts=stereo,volume=0.32[fx];'
               '[0:a]aresample=44100,aformat=channel_layouts=stereo[v];'
               '[v][fx]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[out]',
               '-map', '0:v', '-map', '[out]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
               '-movflags', '+faststart', out_path])
    else:
        R.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', con_fondo, '-c', 'copy',
               '-movflags', '+faststart', out_path])
    print('Duracion final: %.1f s' % R.duration(out_path))


if __name__ == '__main__':
    main()
