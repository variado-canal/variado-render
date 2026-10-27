import subprocess,sys,re,os
p=sys.argv[1]
assert os.path.getsize(p)>100000
ff=os.path.expanduser('~/.local/bin/ffmpeg')
r=subprocess.run([ff,'-v','error','-i',p,'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0, r.stderr[-1800:]
print('VIDEO DECODE PASSED',p,os.path.getsize(p))
