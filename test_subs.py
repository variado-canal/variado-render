import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())
import subs_pro as S

os.makedirs('previews', exist_ok=True)
W, H = 1080, 1920
head = S.cabecera(W, H)
lines = S.dialogos('Trabajos y relaciones comunicacion empezo a', 0, 6) + S.titulo_fijo('En 1998 el mundo se volvio mas cercano', 0, 6)
lines2 = S.dialogos('Comunicaci\u00f3n empez\u00f3 a', 0, 6)
open('t.ass', 'w', encoding='utf-8').write(head + '\n'.join(lines + lines2) + '\n')
info = ['fuente=%s' % S._fuente_sub(), subprocess.run(['fc-match', 'Barlow Condensed:bold'], capture_output=True, text=True).stdout]
m = S._Medidor(W)
info.append('medidor ok=%s em=%.1f cap=%.1f ass_size=%.1f ancho(TRABAJOS Y RELACIONES)=%.0f' % (m.ok, m.em, m.cap, m.ass_size, m.ancho('TRABAJOS Y RELACIONES')))
for name, t in (('a', 0.2), ('b', 3.1)):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'gradients=s=1080x1920:c0=0x6a8caf:c1=0xd9c9a3:d=6:n=2', '-vf', 'ass=t.ass', '-ss', str(t), '-frames:v', '1', 'previews/f_%s.png' % name], check=True)
S.set_paleta('fe')
open('t2.ass', 'w', encoding='utf-8').write(S.cabecera(W, H) + '\n'.join(S.dialogos('Senor ayudame a confiar hoy', 0, 6)) + '\n')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'gradients=s=1080x1920:c0=0x6a8caf:c1=0xd9c9a3:d=6:n=2', '-vf', 'ass=t2.ass', '-ss', '0.2', '-frames:v', '1', 'previews/f_fe.png'], check=True)
open('previews/info.txt', 'w').write('\n'.join(info) + '\n')
print('\n'.join(info))
