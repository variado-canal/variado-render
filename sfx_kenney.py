# Baja packs CC0 de Kenney.nl y deja los sonidos nuevos en remotion/public/sfx (13-nov).
import io, os, re, subprocess, urllib.request, zipfile, http.cookiejar, json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36'
SFX = 'remotion/public/sfx'
X = '/tmp/kenney'
os.makedirs(X, exist_ok=True)
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def get(url, ref):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': ref})
    return op.open(req, timeout=60).read()

for p in ['interface-sounds', 'impact-sounds', 'casino-audio']:
    pag = 'https://kenney.nl/assets/' + p
    get(pag, 'https://kenney.nl/')
    link = json.loads(get('https://kenney.nl/download-link/' + ('assets/' + p).encode().hex(), pag))['url']
    zipfile.ZipFile(io.BytesIO(get(link, pag))).extractall(os.path.join(X, p))

def src(pack, name):
    for raiz, _, fs in os.walk(os.path.join(X, pack)):
        if name + '.ogg' in fs:
            return os.path.join(raiz, name + '.ogg')
    raise SystemExit('falta ' + name)

MAPA = {
    'zoomin': [('interface-sounds', f'maximize_00{i}') for i in (1, 3, 5, 7)],
    'zoomout': [('interface-sounds', f'minimize_00{i}') for i in (1, 3, 5, 7)],
    'golpe': [('impact-sounds', f'impactSoft_heavy_00{i}') for i in range(4)],
    'punch': [('impact-sounds', f'impactPunch_medium_00{i}') for i in range(3)],
    'aparece': [('interface-sounds', f'drop_00{i}') for i in range(1, 5)],
    'clic': [('interface-sounds', f'select_00{i}') for i in (1, 3, 5, 7)],
    'tick': [('interface-sounds', f'tick_00{i}') for i in (1, 2, 4)],
    'moneda': [('casino-audio', f'chips-collide-{i}') for i in range(1, 5)],
    'monedas': [('casino-audio', f'chips-stack-{i}') for i in range(1, 4)],
    'billete': [('casino-audio', f'card-slide-{i}') for i in range(1, 5)],
    'error': [('interface-sounds', f'error_00{i}') for i in (1, 4, 6)],
    'acierto': [('interface-sounds', f'confirmation_00{i}') for i in range(1, 4)],
    'cristal': [('impact-sounds', f'impactGlass_light_00{i}') for i in range(3)],
    'glitch': [('interface-sounds', f'glitch_00{i}') for i in (1, 3)],
    'metal': [('impact-sounds', f'impactMetal_light_00{i}') for i in range(3)],
}
# sintetizados con ffmpeg: aire (cámara), swish (corte), subida, bajo
SINT = {
    'aire_01': "anoisesrc=d=0.9:c=pink:seed=7:a=0.6,highpass=f=300,lowpass=f=3000,afade=t=in:d=0.35,afade=t=out:st=0.45:d=0.45",
    'aire_02': "anoisesrc=d=1.3:c=pink:seed=7:a=0.6,bandpass=f=900:w=800,afade=t=in:d=0.6,afade=t=out:st=0.7:d=0.6",
    'aire_03': "anoisesrc=d=0.7:c=brown:seed=7:a=0.9,highpass=f=150,afade=t=in:d=0.3,afade=t=out:st=0.35:d=0.35",
    'swish_01': "anoisesrc=d=0.28:c=white:seed=7:a=0.7,bandpass=f=2500:w=2000,afade=t=in:d=0.08,afade=t=out:st=0.1:d=0.18",
    'swish_02': "anoisesrc=d=0.35:c=pink:seed=7:a=0.8,bandpass=f=1600:w=1400,afade=t=in:d=0.12,afade=t=out:st=0.15:d=0.2",
    'swish_03': "anoisesrc=d=0.22:c=white:seed=7:a=0.7,highpass=f=1200,afade=t=in:d=0.05,afade=t=out:st=0.07:d=0.15",
    'subida_01': "aevalsrc='0.5*sin(2*PI*(200*t+400*t*t))':d=1.0,afade=t=in:d=0.8,afade=t=out:st=0.9:d=0.1",
    'bajo_01': "aevalsrc='0.9*sin(2*PI*(90*t-30*t*t))*exp(-3*t)':d=1.0",
    'bajo_02': "aevalsrc='0.9*sin(2*PI*(60*t-15*t*t))*exp(-4*t)':d=0.8",
}

def medir(args):
    r = subprocess.run(['ffmpeg', '-hide_banner'] + args + ['-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.search(r'max_volume: (-?[\d.]+)', r)
    return float(m.group(1)) if m else None

def hacer(args, out, sint):
    g = -6.0 - medir(args)
    af = f'volume={g}dB' if sint else f'silenceremove=start_periods=1:start_threshold=-55dB,volume={g}dB'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args + ['-ac', '1', '-ar', '44100', '-af', af, '-b:a', '128k', out], check=True)
    pk = medir(['-i', out])
    if pk is None or pk > -1.5:
        os.remove(out)
        print('descartado', out, pk)

for fam, lista in MAPA.items():
    for n, (p, name) in enumerate(lista, 1):
        hacer(['-i', src(p, name)], f'{SFX}/{fam}_{n:02d}.mp3', False)
for nombre, f in SINT.items():
    hacer(['-f', 'lavfi', '-i', f], f'{SFX}/{nombre}.mp3', True)
print(len(os.listdir(SFX)), 'sonidos en', SFX)