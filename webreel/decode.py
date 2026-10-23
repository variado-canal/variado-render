import glob,os
for f in glob.glob('webreel/enc/*.txt'):
    s=open(f,encoding='utf8').read().replace(chr(168),chr(34)).replace(chr(166),chr(92))
    open('webreel/'+os.path.basename(f)[:-4],'w',encoding='utf8').write(s)
