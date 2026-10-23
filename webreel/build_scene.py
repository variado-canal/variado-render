import json,sys
job=json.load(open(sys.argv[1],encoding='utf8'))
spec=json.dumps(job['spec'],ensure_ascii=False)
js=open('motor.js',encoding='utf8').read()
h='<!doctype html><meta charset=utf-8><style>html,body{margin:0;background:#04101f;overflow:hidden}canvas{display:block}</style><canvas id=c width=720 height=1280></canvas><script>window.SPEC='+spec+';</script><script>'+js+'</script>'
open(sys.argv[2],'w',encoding='utf8').write(h)
print('scene ok',len(h))
