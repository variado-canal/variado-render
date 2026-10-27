import json,sys,pathlib
job=json.load(open(sys.argv[1],encoding='utf-8'))
d=json.loads(pathlib.Path('remotion/public/shot_timeline.json').read_text())
assert len(d['scenes'])==len(job['escenas'])>=7
assert d['duration']>18
for i,shot in enumerate(d['scenes']):
 assert shot['end']>shot['start'] and len(shot['words'])>=4
 assert shot['words'][0]['t']<=shot['words'][-1]['t']
 print('SHOT',i,round(shot['start'],2),round(shot['end'],2),len(shot['words']),shot['text'])
