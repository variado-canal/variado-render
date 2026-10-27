#!/usr/bin/env python3
"""STAGE 1 -- Generate and LOCK voice before creating or rendering any visuals.
Produces remotion/public/voz.wav, palabras.json, shot_timeline.json and audio.sha256.
Uses original Edge voice/rate/pitch defined in the job. All scenes are based on actual
word-event timing, never first-global-occurrence guesses.
"""
import hashlib,json,os,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from render_remotion import voz

def norm(w):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD',w.lower()) if unicodedata.category(c)!='Mn' and (c.isalnum() or c=='ñ'))

def main():
    filename=sys.argv[1]
    job=json.load(open(filename,encoding='utf-8'))
    assert job['voz_edge']=='es-MX-JorgeNeural' and job['rate']=='+14%' and job['pitch']=='+2Hz', 'Voice parameters changed'
    wd=pathlib.Path('work_audio_locked_'+job['job_id']).resolve()
    wd.mkdir(exist_ok=True)
    public=pathlib.Path('remotion/public')
    public.mkdir(exist_ok=True,parents=True)
    data=voz(job,str(wd))
    rows=data['words']
    scenes=job['escenas']
    offset=0
    segment=[]
    total=float(data['dur'])
    for idx,sc in enumerate(scenes):
        tokens=sc['texto'].split()
        piece=rows[offset:offset+len(tokens)]
        if len(piece)!=len(tokens):
            raise ValueError('Words missing in scene '+str(idx))
        for expected, actual in zip(tokens,piece):
            if norm(expected)!=norm(actual['w']):
                raise ValueError('Transcript mismatch in scene '+str(idx)+': '+expected+' != '+actual['w'])
        starts=[float(w['t']) for w in piece]
        if any(b<a-0.02 for a,b in zip(starts,starts[1:])):
            raise ValueError('Non-monotonic timestamps in scene '+str(idx))
        if not piece:
            raise ValueError('Empty scene '+str(idx))
        segment.append({
          'id':idx,
          'text':sc['texto'],
          'start':float(piece[0]['t']),
          'words':[{'text':w['w'],'t':w['t'],'d':w['d'],'index':n} for n,w in enumerate(piece)]
        })
        offset+=len(tokens)
    if offset!=len(rows):
        raise ValueError('Voice token count differs from script: %d vs %d'%(offset,len(rows)))
    for i,seg in enumerate(segment):
        seg['end']=segment[i+1]['start'] if i+1<len(segment) else total
        if seg['end']-seg['start'] < .5:
            raise ValueError('Shot too short or non-sequential: '+str(i))
    wav=public/'voz.wav'
    digest=hashlib.sha256(wav.read_bytes()).hexdigest()
    out={'job_id':job['job_id'],'duration':total,'audio_sha256':digest,'fps':30,'voice':job['voz_edge'],
         'rate':job['rate'],'pitch':job['pitch'],'scenes':segment}
    (public/'palabras.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    (public/'shot_timeline.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    (public/'audio.sha256').write_text(digest,encoding='utf-8')
    print('AUDIO LOCKED: %.3f sec, %d scenes, %d words, SHA256 %s'%(total,len(segment),len(rows),digest),flush=True)
if __name__=='__main__':main()
