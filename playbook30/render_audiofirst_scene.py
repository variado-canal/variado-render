#!/usr/bin/env python3
"""Remotion native 30 fps from AUDIO-LOCKED source, with separately maintained TSX shots."""
import hashlib,json,pathlib,subprocess,sys
jobfile,out=sys.argv[1:3]
job=json.load(open(jobfile,encoding='utf-8'))
pub=pathlib.Path('remotion/public')
timeline=json.loads((pub/'shot_timeline.json').read_text(encoding='utf-8'))
assert timeline['job_id']==job['job_id']
audio=pub/'voz.wav'
assert audio.is_file() and audio.stat().st_size>10000
assert hashlib.sha256(audio.read_bytes()).hexdigest()==timeline['audio_sha256'],'Voice changed after audio lock'
assert len(timeline['scenes'])==len(job['escenas'])>=6
assert abs(timeline['duration']-json.loads((pub/'palabras.json').read_text())['dur'])<.001
source=job['scene_file']
assert source.startswith('playbook30/scenes/') and source.endswith('.tsx') and '..' not in source
tsx=pathlib.Path(source).read_text(encoding='utf-8')
assert 'shot_timeline.json' in tsx, 'Animation MUST be based on locked voice timeline'
root=pathlib.Path('remotion/src/Root.tsx')
old=root.read_text(encoding='utf-8')
assert 'const FPS = 60;' in old
pathlib.Path('remotion/src/Escena.tsx').write_text(tsx,encoding='utf-8')
root.write_text(old.replace('const FPS = 60;','const FPS = 30;'),encoding='utf-8')
try:
 subprocess.run(['npx','remotion','render','src/index.ts','Video',str(pathlib.Path(out).resolve()),'--log=error'],cwd='remotion',check=True)
finally:
 root.write_text(old,encoding='utf-8')
assert hashlib.sha256(audio.read_bytes()).hexdigest()==timeline['audio_sha256'],'Voice modified during render'
assert pathlib.Path(out).stat().st_size>100000
print('Verified 30fps locked-audio reel',job['job_id'],round(timeline['duration'],2),'seconds')
