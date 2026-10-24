import asyncio
import json
import os
import re
import subprocess
import sys
import wave
from multiprocessing import Pool

import numpy as np

import motion2 as M

GAP = 0.14
MIN_DUR = 1.7
TAIL = 0.9
PITCH = '+0Hz'
SR = M.SR

def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def dur_audio(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)

async def _tts(texto, voz, rate, mp3):
    import edge_tts
    com = edge_tts.Communicate(texto, voz, rate=rate, pitch=PITCH, boundary='WordBoundary')
    words = []
    with open(mp3, 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                a = ch['offset'] / 1e7
                words.append((ch['text'], a, a + ch['duration'] / 1e7))
    return words

def reparte(texto, dur):
    ws = texto.split()
    tot = sum(len(w) + 1 for w in ws) or 1
    out, t = [], 0.0
    for w in ws:
        d = dur * (len(w) + 1) / tot
        out.append((w, t, t + d))
        t += d
    return out

def alinea(texto, ev, dur):
    ws = texto.split()
    if not ev or abs(len(ev) - len(ws)) > max(2, len(ws) // 4):
        return reparte(texto, dur)
    out = []
    for i, w in enumerate(ws):
        j = min(int(round(i * (len(ev) - 1) / max(len(ws) - 1, 1))), len(ev) - 1) if len(ev) != len(ws) else i
        out.append((w, ev[j][1], ev[j][2]))
    return out

def voz(job, work):
    voz_n = job.get('voz_edge', 'es-MX-JorgeNeural')
    global PITCH
    rate = job.get('rate', '+8%')
    PITCH = job.get('pitch', '+2Hz')
    escenas = job['escenas']
    clips, info = [], []
    for i, sc in enumerate(escenas):
        mp3 = os.path.join(work, 'v%02d.mp3' % i)
        wav = os.path.join(work, 'v%02d.wav' % i)
        ev = []
        try:
            if os.environ.get('MOTION_MOCK'):
                sh(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t',
                    '%.2f' % (len(sc['texto'].split()) / 2.7), '-q:a', '9', mp3])
            else:
                ev = asyncio.run(_tts(sc['texto'], voz_n, rate, mp3))
        except Exception as e:
            print('TTS fallo', i, e, file=sys.stderr)
        if not os.path.exists(mp3) or os.path.getsize(mp3) < 500:
            raise RuntimeError('sin audio en escena %d' % i)
        d = dur_audio(mp3)
        dur = max(MIN_DUR, d + GAP) + (TAIL if i == len(escenas) - 1 else 0)
        sh(['ffmpeg', '-y', '-i', mp3, '-ar', str(SR), '-ac', '1', '-af', 'apad=whole_dur=%.3f' % dur, wav])
        clips.append(wav)
        info.append((alinea(sc['texto'], ev, d), dur))
    return clips, info

def leer_wav(p):
    with wave.open(p, 'rb') as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def musica(total, path):
    n = int((total + 1) * SR)
    t = np.arange(n) / SR
    acordes = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 261.6, 329.6], [196.0, 246.9, 293.7]]
    out = np.zeros(n)
    seg = 3.0
    for k in range(int(total / seg) + 2):
        a, b = int(k * seg * SR), min(n, int((k + 1) * seg * SR))
        if a >= n:
            break
        tt = t[a:b] - k * seg
        env = np.minimum(tt / 0.6, 1) * np.minimum((seg - tt) / 0.6, 1)
        for fr in acordes[k % 4]:
            out[a:b] += np.sin(2 * np.pi * fr * tt) * env * 0.11 + np.sin(2 * np.pi * fr * 2 * tt) * env * 0.03
        bass = np.sin(2 * np.pi * acordes[k % 4][0] / 2 * tt) * env * 0.18
        out[a:b] += bass
        for beat in range(6):
            bt = beat * 0.5
            m = tt >= bt
            tb = np.where(m, tt - bt, 0)
            out[a:b] += np.where(m, np.sin(2 * np.pi * 880 * tb) * np.exp(-tb * 14) * 0.035, 0)
    out = out / max(1e-9, np.abs(out).max()) * 0.5
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

_G = {}

def _init(scenes, words, total, grupos, linea):
    _G.update(scenes=scenes, words=words, total=total, grupos=grupos, linea=linea)

def _fr(i):
    im = M.frame(i / M.FPS, _G['scenes'], _G['words'], _G['total'], _G['grupos'], _G['linea'])
    return im.tobytes()

def main():
    job = json.load(open(sys.argv[1], encoding='utf-8'))
    out = sys.argv[2]
    work = os.path.join(os.path.dirname(os.path.abspath(out)), 'work_' + str(job.get('job_id', 'x')))
    os.makedirs(work, exist_ok=True)
    M.PALETA['n'] = job.get('paleta', 'rojo')
    clips, info = voz(job, work)
    scenes, words, t = [], [], 0.0
    for sc, (ws, dur) in zip(job['escenas'], info):
        s = dict(sc)
        s.update(start=t, dur=dur, words=ws)
        scenes.append(s)
        words += [(w, a + t, b + t) for (w, a, b) in ws]
        t += dur
    total = t
    voice = np.concatenate([leer_wav(c) for c in clips])
    mus = os.path.join(work, 'mus.wav')
    sfx = os.path.join(work, 'sfx.wav')
    musica(total, mus)
    M.build_sfx(scenes, total, sfx)
    n = int((total + 1) * SR)
    mix = np.zeros(n)
    mix[:len(voice)] += voice[:n] * 1.0
    mx = leer_wav(mus)
    mix[:len(mx)] += mx[:n] * 0.16
    sx = leer_wav(sfx)
    mix[:len(sx)] += sx[:n] * 0.45
    mix = np.clip(mix / max(1.0, np.abs(mix).max()) * 0.92, -1, 1)
    mixw = os.path.join(work, 'mix.wav')
    with wave.open(mixw, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    grupos = M.phrases_de(words)
    nfr = int(total * M.FPS)
    only = int(os.environ.get('MOTION_FRAMES', '0'))
    if only:
        nfr = min(nfr, only)
    p = subprocess.Popen(['ffmpeg', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (M.W, M.H),
                          '-r', str(M.FPS), '-i', '-', '-i', mixw, '-c:v', 'libx264', '-preset', 'veryfast',
                          '-crf', '22', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest',
                          '-movflags', '+faststart', out], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    with Pool(max(1, os.cpu_count() or 2), initializer=_init,
              initargs=(scenes, words, total, grupos, job.get('linea_titulo', ''))) as pool:
        for k, b in enumerate(pool.imap(_fr, range(nfr), chunksize=6)):
            p.stdin.write(b)
            if k % 150 == 0:
                print('frame', k, '/', nfr, flush=True)
    p.stdin.close()
    p.wait()
    print('listo', out, round(total, 1), 's')

if __name__ == '__main__':
    main()
