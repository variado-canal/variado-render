import math
import random
import wave

import numpy as np

PENTA = (523.25, 587.33, 659.25, 783.99, 880.0, 987.77)


def _env(n, sr, att=0.006, dec=0.12):
    t = np.arange(n) / sr
    return np.minimum(t / att, 1.0) * np.exp(-t / dec)


def _blip(sr, rnd):
    f = rnd.choice(PENTA)
    n = int(0.16 * sr)
    t = np.arange(n) / sr
    ph = 2 * np.pi * (f * t - 70 * t * t)
    return np.sin(ph) * _env(n, sr, 0.006, 0.05) * 0.8


def _bubble(sr, rnd):
    f0 = rnd.choice((300.0, 350.0, 420.0))
    n = int(0.14 * sr)
    t = np.arange(n) / sr
    ph = 2 * np.pi * (f0 * t + 1100 * t * t)
    return np.sin(ph) * _env(n, sr, 0.008, 0.04) * 0.8


def _tick(sr, rnd):
    n = int(0.06 * sr)
    x = np.random.RandomState(rnd.randint(1, 10 ** 6)).randn(n)
    x = np.convolve(x, np.ones(6) / 6.0, mode='same')
    return x * _env(n, sr, 0.002, 0.012) * 1.2


def _chime(sr, rnd, base=None):
    f = base or rnd.choice(PENTA)
    n = int(0.5 * sr)
    t = np.arange(n) / sr
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 9) + 0.15 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t * 14)
    return x * _env(n, sr, 0.006, 0.16) * 0.6


def _whoosh(sr, rnd):
    n = int(0.36 * sr)
    x = np.random.RandomState(rnd.randint(1, 10 ** 6)).randn(n)
    k = 40
    x = np.convolve(x, np.ones(k) / k, mode='same') * 3
    t = np.arange(n) / sr
    env = np.sin(np.pi * np.clip(t / 0.36, 0, 1)) ** 2
    return x * env * 0.8


def _put(buf, snd, at, sr, vol):
    a = int(at * sr)
    if a < 0 or a >= len(buf):
        return
    b = min(len(buf), a + len(snd))
    buf[a:b] += snd[:b - a] * vol


def build_sfx(scenes, total, path):
    import motion2 as M
    sr = M.SR
    n = int((total + 1) * sr)
    buf = np.zeros(n)
    r = random.Random(11)
    for si, sc in enumerate(scenes):
        t0 = sc['start']
        if si > 0:
            _put(buf, _whoosh(sr, r), max(0.0, t0 - 0.06), sr, 0.16)
        try:
            ev = M.PLANTILLAS[sc['plantilla']][1](sc)
        except Exception:
            ev = []
        last = -9.0
        for k, e in enumerate(ev):
            te, nombre = e[0], e[1]
            if te - last < 0.18:
                continue
            last = te
            if nombre == 'ching':
                snd = _chime(sr, r, base=r.choice((1046.5, 1318.5, 1568.0)))
                vol = 0.17
            else:
                pick = (si + k) % 4
                snd = (_blip, _bubble, _tick, _chime)[pick](sr, r)
                vol = (0.16, 0.16, 0.12, 0.13)[pick]
            _put(buf, snd, t0 + te, sr, vol)
    pk = np.abs(buf).max()
    if pk > 0.4:
        buf = buf / pk * 0.4
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())