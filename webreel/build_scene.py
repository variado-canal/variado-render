import json,sys,os
job=json.load(open(sys.argv[1],encoding='utf8'))
H='<!doctype html><meta charset=utf-8><style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style><canvas id=c width=720 height=1280></canvas>'
v=job.get('video')
if v and os.path.exists(v):
    js=open('m2a.js',encoding='utf8').read()+chr(10)+open(v,encoding='utf8').read()+chr(10)+open('m2b.js',encoding='utf8').read()
    h=H+'<script>'+js+'</script>'
else:
    spec=json.dumps(job['spec'],ensure_ascii=False)
    js=open('motor.js',encoding='utf8').read()
    if os.path.exists('motor_patch.js'):js+=chr(10)+open('motor_patch.js',encoding='utf8').read()
    h=H+'<script>window.SPEC='+spec+';</script><script>'+js+'</script>'
open(sys.argv[2],'w',encoding='utf8').write(h)
print('scene ok',len(h))

