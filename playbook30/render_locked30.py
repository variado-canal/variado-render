#!/usr/bin/env python3
"""STAGE 2: render from a LOCKED, already generated voice and timeline.
Never re-synthesize, never modify the WAV or word timestamps.
"""
import hashlib,json,os,pathlib,subprocess,sys
jobfile,out=sys.argv[1:3]
job=json.load(open(jobfile,encoding='utf-8'))
pub=pathlib.Path('remotion/public')
timeline=json.loads((pub/'shot_timeline.json').read_text(encoding='utf-8'))
assert timeline['job_id']==job['job_id']
audio=pub/'voz.wav'
assert hashlib.sha256(audio.read_bytes()).hexdigest()==timeline['audio_sha256'],'AUDIO WAS MODIFIED AFTER LOCK'
root=pathlib.Path('remotion/src/Root.tsx')
old=root.read_text(encoding='utf-8')
assert 'const FPS = 60;' in old
tsx=next((s.get('p',{}).get('remotion_tsx') for s in job['escenas'] if s.get('p',{}).get('remotion_tsx')),None)
assert tsx
(pathlib.Path('remotion/src/Escena.tsx')).write_text(tsx,encoding='utf-8')
root.write_text(old.replace('const FPS = 60;','const FPS = 30;'),encoding='utf-8')
try:
    subprocess.run(['npx','remotion','render','src/index.ts','Video',str(pathlib.Path(out).resolve()),'--log=error'],cwd='remotion',check=True)
finally:
    root.write_text(old,encoding='utf-8')
assert hashlib.sha256(audio.read_bytes()).hexdigest()==timeline['audio_sha256'],'AUDIO CHANGED WHILE RENDERING'
assert pathlib.Path(out).stat().st_size>50000
print('30FPS OUTPUT OK, LOCKED AUDIO SHA256',timeline['audio_sha256'])
