import json,sys
if sys.argv[1]=='info':
    d=json.load(open('/tmp/voz.json'))
    print('voz_r%s_v%s_t%s'%(d['rate_pct'],d['sylps_voiced'],d['sylps_total']))
else:
    d=json.load(open(sys.argv[1]))
    print('ID=%s HTML=%s'%(d['id'],d['html']))
