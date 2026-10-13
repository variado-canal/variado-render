#!/usr/bin/env python3
"""VARIADO render: imagenes con zoom + narracion + subtitulos + musica -> MP4 vertical 1080x1920.
Uso: python3 render.py jobs/<id>/job.json salida.mp4
"""
import base64
import json
import os
import subprocess
import sys

W, H, FPS = 1080, 1920, 30
NL = chr(10)
TAIL = 0.30  # pausa al final de cada escena (segundos)
SPEED = 1.3  # velocidad de la voz (sin cambiar el tono)


def run(cmd):
    print(' '.join(cmd[:6]), '...', flush=True)
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', path])
    return float(out.decode().strip())


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return '%d:%02d:%05.2f' % (h, m, s)


def chunks(text, max_words=3, max_chars=22):
    words = text.split()
    out, cur = [], []
    for w in words:
        trial = ' '.join(cur + [w])
        if cur and (len(cur) >= max_words or len(trial) > max_chars):
            out.append(' '.join(cur))
            cur = [w]
        else:
            cur.append(w)
        if w[-1:] in '.!?' and cur:
            out.append(' '.join(cur))
            cur = []
    if cur:
        out.append(' '.join(cur))
    return out


def write_ass(path, text, total):
    parts = chunks(text)
    weights = [max(len(p), 1) for p in parts]
    tw = float(sum(weights))
    head = NL.join([
        '[Script Info]',
        'ScriptType: v4.00+',
        'PlayResX: %d',
        'PlayResY: %d',
        '',
        '[V4+ Styles]',
        'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,'
        'Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,'
        'Alignment,MarginL,MarginR,MarginV,Encoding',
        'Style: Default,DejaVu Sans,84,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,'
        '1,0,0,0,100,100,0,0,1,7,2,2,60,60,470,1',
        '',
        '[Events]',
        'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text',
        '',
    ]) % (W, H)
    lines = []
    t = 0.0
    for p, wgt in zip(parts, weights):
        d = total * wgt / tw
        lines.append('Dialogue: 0,%s,%s,Default,,0,0,0,,%s' % (
            ass_time(t), ass_time(t + d), p.replace(NL, ' ')))
        t += d
    with open(path, 'w', encoding='utf-8') as f:
        f.write(head + NL.join(lines) + NL)


def main():
    job_path, out_path = sys.argv[1], sys.argv[2]
    with open(job_path, encoding='utf-8') as f:
        job = json.load(f)
    work = 'work_render'
    os.makedirs(work, exist_ok=True)
    escenas = job['escenas']
    clip_files = []
    for i, s in enumerate(escenas):
        img = '%s/i%02d.jpg' % (work, i)
        aud = '%s/a%02d.mp3' % (work, i)
        with open(img, 'wb') as f:
            f.write(base64.b64decode(s['imagen_b64']))
        with open(aud, 'wb') as f:
            f.write(base64.b64decode(s['audio_b64']))
        fast = '%s/a%02df.mp3' % (work, i)
        speed = float(job.get('velocidad', SPEED))
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', aud,
             '-filter:a', 'atempo=%.2f,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100' % speed, '-c:a', 'libmp3lame', '-q:a', '2', fast])
        aud = fast
        voice = duration(aud)
        total = voice + TAIL
        frames = max(int(total * FPS), 1)
        ass = '%s/s%02d.ass' % (work, i)
        write_ass(ass, s.get('texto', ''), voice)
        if i % 2 == 0:
            z = "1+0.14*on/%d" % frames
        else:
            z = "1.14-0.14*on/%d" % frames
        # recorte 9:16 centrado, sobre-escalado para que el zoom no tiemble
        vf = (
            "crop='min(iw,ih*9/16)':ih,scale=2160:-2:flags=lanczos,"
            "zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=%d:s=%dx%d:fps=%d,"
            "ass=%s,format=yuv420p"
        ) % (z, frames, W, H, FPS, ass)
        clip = '%s/c%02d.mp4' % (work, i)
        run([
            'ffmpeg', '-y', '-loglevel', 'error', '-i', img, '-i', aud,
            '-vf', vf, '-af', 'apad=pad_dur=%.2f,aresample=44100' % TAIL,
            '-t', '%.2f' % total, '-r', str(FPS),
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
            '-c:a', 'aac', '-b:a', '128k', '-ac', '2', clip])
        clip_files.append(clip)
    lst = '%s/list.txt' % work
    with open(lst, 'w') as f:
        for c in clip_files:
            f.write("file '%s'" % os.path.basename(c) + NL)
    joined = '%s/joined.mp4' % work
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', lst, '-c', 'copy', joined])
    add_ambience(joined, out_path, job.get('fondo', 'suave'))
    print('Duracion final: %.1f s' % duration(out_path))


import array
import math
import random
import wave

SR = 44100


def put_tone(buf, t0, dur, freq, amp, decay, harm=(1.0,), sweep=0.0, attack=0.005):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    ph = 0.0
    for k in range(n):
        j = i0 + k
        if j >= len(buf):
            break
        t = k / SR
        f = freq * (1.0 + sweep * math.exp(-t * 30.0))
        ph += 2.0 * math.pi * f / SR
        env = math.exp(-t * decay) * min(1.0, t / attack)
        v = 0.0
        for h, a in enumerate(harm):
            v += a * math.sin(ph * (h + 1))
        buf[j] += amp * env * v


def put_noise(buf, t0, dur, amp, decay, hp=0.8):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    prev = 0.0
    for k in range(n):
        j = i0 + k
        if j >= len(buf):
            break
        r = random.uniform(-1.0, 1.0)
        v = r - prev * hp
        prev = r
        buf[j] += amp * math.exp(-(k / SR) * decay) * v


def synth_music(path, mood, secs):
    random.seed(7)
    n = int(secs * SR)
    buf = [0.0] * n
    if mood == 'ritmo':
        bpm = 98.0
        eighth = 60.0 / bpm / 2.0
        steps = int(secs / eighth) + 8
        for st in range(steps):
            t = st * eighth
            bar = (st // 8) % 4
            idx = st % 8
            if idx in (0, 4, 7 if bar % 2 else 99):
                put_tone(buf, t, 0.12, 60.0, 0.9, 30.0, sweep=2.2)
            if idx in (2, 6):
                put_noise(buf, t, 0.14, 0.50, 26.0, hp=0.5)
            put_noise(buf, t, 0.05, 0.16 if idx % 2 else 0.10, 70.0, hp=0.95)
            if idx == 3 or (idx == 5 and bar % 2 == 1):
                put_noise(buf, t, 0.03, 0.22, 120.0, hp=0.9)
            if idx == 7 and bar == 3:
                put_noise(buf, t, 0.18, 0.18, 14.0, hp=0.95)
    elif mood == 'suave':
        bpm = 82.0
        eighth = 60.0 / bpm / 2.0
        steps = int(secs / eighth) + 8
        for st in range(steps):
            t = st * eighth
            idx = st % 8
            if idx in (0, 5):
                put_tone(buf, t, 0.12, 58.0, 0.7, 30.0, sweep=2.0)
            if idx in (2, 6):
                put_noise(buf, t, 0.10, 0.26, 34.0, hp=0.6)
            put_noise(buf, t, 0.04, 0.11 if idx % 2 else 0.07, 80.0, hp=0.95)
            if idx == 3:
                put_noise(buf, t, 0.03, 0.14, 120.0, hp=0.9)
    else:  # epico
        bpm = 72.0
        beat = 60.0 / bpm
        steps = int(secs / beat) + 8
        for st in range(steps):
            t = st * beat
            idx = st % 4
            if idx == 0:
                put_tone(buf, t, 0.30, 55.0, 1.0, 13.0, sweep=1.6)
                put_noise(buf, t, 0.30, 0.22, 10.0, hp=0.2)
            if idx == 1:
                put_noise(buf, t + beat / 2.0, 0.08, 0.20, 40.0, hp=0.6)
            if idx == 2:
                put_tone(buf, t, 0.25, 80.0, 0.60, 15.0, sweep=1.0)
                put_noise(buf, t, 0.16, 0.34, 24.0, hp=0.5)
            if idx == 3:
                for q in range(4):
                    put_noise(buf, t + q * beat / 4.0, 0.07, 0.16 + 0.03 * q, 45.0, hp=0.6)
                put_tone(buf, t + beat / 2.0, 0.22, 95.0, 0.45, 16.0, sweep=0.8)
    peak = max(1e-9, max(abs(x) for x in buf))
    scale = 0.85 / peak
    out = array.array('h', (int(max(-1.0, min(1.0, x * scale)) * 32767) for x in buf))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())


BEDS = {
    # misterio: zumbido grave y oscuro
    'misterio': (
        "sine=f=82.4:sample_rate=44100[a];"
        "sine=f=123.5:sample_rate=44100[b];"
        "sine=f=164.8:sample_rate=44100[c];"
        "anoisesrc=color=brown:sample_rate=44100:amplitude=0.5[n];"
        "[a]volume=0.55[a1];[b]volume=0.30,tremolo=f=0.15:d=0.6[b1];"
        "[c]volume=0.12,tremolo=f=0.1:d=0.8[c1];"
        "[n]lowpass=f=900,volume=0.50[n1];"
        "[a1][b1][c1][n1]amix=inputs=4:normalize=0,aformat=channel_layouts=stereo,"
        "volume=0.34"
    ),
    # impacto: casos reales con impacto en personas, zumbido muy bajito
    'impacto': (
        "sine=f=82.4:sample_rate=44100[a];"
        "sine=f=123.5:sample_rate=44100[b];"
        "sine=f=164.8:sample_rate=44100[c];"
        "anoisesrc=color=brown:sample_rate=44100:amplitude=0.5[n];"
        "[a]volume=0.55[a1];[b]volume=0.30,tremolo=f=0.15:d=0.6[b1];"
        "[c]volume=0.12,tremolo=f=0.1:d=0.8[c1];"
        "[n]lowpass=f=900,volume=0.50[n1];"
        "[a1][b1][c1][n1]amix=inputs=4:normalize=0,aformat=channel_layouts=stereo,"
        "volume=0.22"
    ),
}


def add_ambience(src, dst, mood):
    """Mezcla musica/fondo generado (sin derechos) bajo la voz.
    mood: misterio | impacto | suave | ritmo | epico | ninguno."""
    if mood not in ('misterio', 'impacto', 'suave', 'ritmo', 'epico'):
        run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-c', 'copy',
             '-movflags', '+faststart', dst])
        return
    total = duration(src)
    fade_out_at = max(total - 2.0, 0)
    if mood in ('ritmo', 'epico', 'suave'):
        wav = 'work_render/musica.wav'
        synth_music(wav, mood, total + 1.0)
        level = {'ritmo': '0.30', 'epico': '0.34', 'suave': '0.28'}[mood]
        graph = (
            "[1:a]aformat=channel_layouts=stereo,volume=%s,afade=t=in:d=1.0,"
            "afade=t=out:st=%.2f:d=2.0[m];"
            "[0:a]aresample=44100,aformat=channel_layouts=stereo,asplit=2[v][sc];"
            "[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];"
            "[v][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[out]"
        ) % (level, fade_out_at)
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-i', wav]
    else:
        graph = (
            BEDS[mood] + ",afade=t=in:d=1.5,afade=t=out:st=%.2f:d=2.0[bed];"
            "[0:a]aresample=44100,aformat=channel_layouts=stereo[v];"
            "[v][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[out]"
        ) % fade_out_at
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', src]
    run(cmd + ['-filter_complex', graph, '-map', '0:v', '-map', '[out]',
               '-t', '%.2f' % total, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
               '-movflags', '+faststart', dst])


if __name__ == '__main__':
    main()
