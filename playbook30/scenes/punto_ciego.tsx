import React from 'react';
import {AbsoluteFill,useS,DUR,FONT,interpolate,clamp} from './kit';
import timeline from '../public/shot_timeline.json';
const C='#72e6ff', Y='#ffdb86', V='#b6a4ff', W='#eefaff';
const a=(s:number,t:number,u:number)=>interpolate(s,[t,Math.max(t+.001,u)],[0,1],clamp);
const smooth=(s:number,t:number,u:number)=>{const x=a(s,t,u);return x*x*(3-2*x)};
const lines=timeline.scenes;
const Scene:React.FC<{i:number;s:number}>=({i,s})=>{
 const sh=lines[i],p=a(s,sh.start,sh.end),smoothP=smooth(s,sh.start,sh.end);
 const word=(n:number)=>sh.words[Math.min(n,sh.words.length-1)].t;
 const pulse=(n:number)=>a(s,word(n),word(n)+.32);
 const r=230, cx=540,cy=815;
 const pupil=150+Math.sin(s*3)*4;
 const waves=Array.from({length:28},(_,k)=>k);
 const Glyph=({x,y,rad=14,col=C}:{x:number;y:number;rad?:number;col?:string})=><circle cx={x} cy={y} r={rad} fill={col}/>;
 const Eye=({big=false,cut=false}:{big?:boolean;cut?:boolean})=><g transform={'translate(540 820) scale('+(big?1.25:1)+')'}>
  <path d="M -410 0 Q -210 -250 0 -255 Q 235 -260 410 0 Q 200 265 0 255 Q -230 255 -410 0" fill="#efc3a7" stroke="#f7e7c7" strokeWidth="18"/>
  <ellipse rx="224" ry="242" fill="#f2faff" stroke="#bddfeb" strokeWidth="8"/>
  <circle r="178" fill="#6bcbd8" stroke="#255978" strokeWidth="17"/>
  {waves.slice(0,24).map(k=><path key={k} d={'M '+Math.sin(k*.2618)*105+' '+Math.cos(k*.2618)*105+' L '+Math.sin(k*.2618)*173+' '+Math.cos(k*.2618)*173} stroke="#2b8fac" strokeWidth="8" opacity=".7"/>)}
  <circle r={93+6*Math.sin(s)} fill="#081023"/>
  <circle cx="-58" cy="-80" r="37" fill="#fff" opacity=".75"/>
  <ellipse cx="0" cy="-260" rx="250" ry="45" fill="#e2b19a" opacity=".7"/>
 </g>;
 const anatomy=()=> <g transform={'translate(95 360) scale(.96)'}>
  <path d="M 135 445 Q 85 330 175 215 Q 340 35 615 180 Q 805 275 785 520 Q 780 755 530 825 Q 250 835 135 650Z" fill="#623253" stroke="#f6b4d6" strokeWidth="20"/>
  <path d="M 190 475 Q 185 250 365 201 Q 603 126 710 336 Q 760 525 632 694 Q 414 835 237 628Z" fill="#e48ca8" stroke="#ffd6b4" strokeWidth="10"/>
  <path d="M 170 415 Q 130 480 186 554" fill="none" stroke="#e3fbff" strokeWidth="55"/>
  <circle cx="520" cy="470" r="205" fill="#fcbf8e" opacity=".54" stroke="#fff0cb" strokeWidth="10"/>
  <circle cx="575" cy="450" r="92" fill="none" stroke="#ffd676" strokeWidth="16"/>
  <path d="M 715 480 Q 870 460 960 520" fill="none" stroke={Y} strokeWidth="62" strokeLinecap="round"/>
  <text x="820" y="630" textAnchor="middle" fill="#fff" fontSize="31" fontFamily={FONT} fontWeight="900">NERVIO ÓPTICO</text>
  <circle cx="733" cy="483" r="33" fill={Y} opacity={.9}/>
 </g>;
 const Stars=()=> <g>{waves.map((k)=><circle key={k} cx={(k*211+40)%1080} cy={(k*367+100)%1900} r={1+k%3} fill={k%2?C:Y} opacity={.16+.12*Math.sin(s*2+k)}/>)}</g>;
 let graphic:React.ReactNode;
 if(i===0){ // immediate visual demonstration and glitch
  graphic=<><Eye/><g transform={'translate('+((p-.2)*80)+' 0)'}><circle cx={756} cy={820} r={80+4*Math.sin(s*8)} fill={Y} opacity={1-smooth(s,word(3),word(5))}/><circle cx={756} cy={820} r={80} fill="#4d7085" opacity={smooth(s,word(3),word(5))}/></g>
   <path d={'M 235 1260 L '+(235+600*p)+' 1260'} stroke={Y} strokeWidth="12" strokeLinecap="round"/>
   <text x="540" y="1410" textAnchor="middle" fill={Y} fontSize="62" fontFamily={FONT} fontWeight="900">UN PUNTO DESAPARECE</text></>;
 } else if(i===1){ // step by step test: two markers stable and instructional
  graphic=<><g><circle cx="250" cy="760" r="58" stroke={Y} strokeWidth="18" fill="none"/><path d="M 680 760 H 910 M 795 645 V 875" stroke={C} strokeWidth="26" strokeLinecap="round"/></g>
  <path d={'M 100 1100 H '+(100+880*p)} stroke={C} strokeWidth="10" fill="none"/>
  <text x="540" y="1300" textAnchor="middle" fill={W} fontSize="60" fontFamily={FONT} fontWeight="800">MIRA LA CRUZ</text>
  <text x="540" y="1375" textAnchor="middle" fill={Y} fontSize="35" fontFamily={FONT}>TAPA TU OJO IZQUIERDO</text></>;
 } else if(i===2){ // simulated vanish as dot approaches
  const move=130*p;const fade=smooth(s,word(2),word(6));
  graphic=<><path d="M 680 760 H 910 M 795 645 V 875" stroke={C} strokeWidth="24" strokeLinecap="round"/>
    <circle cx={250+move} cy={760} r="61" fill={Y} opacity={1-fade}/>
    <circle cx={250+move} cy={760} r="78" stroke={Y} strokeWidth="4" fill="none" strokeDasharray="20 12" opacity={(1-fade)*.6}/>
    <text x="540" y="1330" textAnchor="middle" fill={Y} fontSize="48" fontFamily={FONT}>SIMULACIÓN DEL PUNTO CIEGO</text>
    <text x="540" y="1390" textAnchor="middle" fill={W} fontSize="34" fontFamily={FONT}>EN LA PRUEBA REAL, AJUSTA LA DISTANCIA</text></>;
 } else if(i===3){ // physically fly into eyeball and section
  graphic=<><g style={{transform:'translate(0px,'+(-220*p)+'px) scale('+(1+.08*p)+')',transformOrigin:'540px 800px'}}><Eye big/></g>
   <circle cx="540" cy="820" r={100+700*p} fill="none" stroke={C} strokeWidth={12} opacity={1-p}/>
   <path d="M 540 1110 Q 540 1200 700 1250" stroke={Y} strokeWidth="8" fill="none"/>
   <text x="540" y="1430" textAnchor="middle" fontFamily={FONT} fontSize="55" fontWeight="900" fill={C}>ENTRAMOS AL OJO</text></>;
 } else if(i===4){ // retina cross section and location of nerve exit
  graphic=<><g style={{transform:'translateX('+(-100*p)+'px) scale('+(1+.12*p)+')',transformOrigin:'550px 850px'}}>{anatomy()}</g>
  <path d="M 650 1110 L 760 1230 L 870 1230" stroke={Y} strokeWidth="9" fill="none"/>
  <rect x="475" y="1370" width="550" height="92" rx="25" fill="#07172e" stroke={Y} strokeWidth="4"/>
  <text x="750" y="1432" textAnchor="middle" fontFamily={FONT} fontWeight="900" fontSize="43" fill={Y}>SIN FOTORRECEPTORES</text></>;
 } else if(i===5){ // signal reaches brain and fill happens
  const fill=smooth(s,word(2),word(5));
  graphic=<><g><path d="M 110 850 C 240 500 540 500 560 800 C 580 1200 870 1190 960 850" fill="none" stroke="#5983a2" strokeWidth="120" opacity=".4"/>
  {waves.slice(0,18).map(k=><circle key={k} cx={180+k*42} cy={800-190*Math.sin(Math.PI*k/18)} r="14" fill={k/18<p?Y:C} opacity=".7"/>)}
  <path d="M 650 700 C 750 490 880 480 935 660 Q 1050 820 895 1050 L 740 1000" fill="#785cb5" stroke="#ccb8ff" strokeWidth="15" opacity=".9"/></g>
  <text x="540" y="1350" textAnchor="middle" fill={W} fontWeight="900" fontFamily={FONT} fontSize="49">TU CEREBRO COMPLETA</text>
  <rect x="230" y="1170" width={620*fill} height="28" rx="14" fill={Y}/>
  </>;
 } else if(i===6){ // gap is filled by brain
  graphic=<><rect x="155" y="460" width="770" height="780" rx="40" fill="#132c45" stroke="#4e8aa9" strokeWidth="8"/>
   {waves.slice(0,26).map(k=><path key={k} d={'M 160 '+(480+k*31)+' Q '+(490+60*Math.sin(k*.4+s*.9))+' '+(490+k*31)+' 920 '+(480+k*31)} stroke={k%4===0?Y:C} strokeWidth="7" fill="none" opacity=".3"/>)}
   <circle cx="540" cy="850" r="135" fill="#071124" opacity={1-smooth(s,word(2),word(6))}/>
   <path d="M 200 850 Q 540 800 890 850" fill="none" stroke={Y} strokeWidth="8" opacity={smooth(s,word(2),word(6))}/>
   <text x="540" y="1370" fill={Y} fontFamily={FONT} fontSize="62" fontWeight="900" textAnchor="middle">NO VES EL HUECO</text></>;
 } else { // loop back to same demonstration
  graphic=<><g><circle cx="250" cy="780" r={60+8*Math.sin(s*3)} stroke={Y} strokeWidth="14" fill="none"/><path d="M 680 780 H 910 M 795 660 V 900" stroke={C} strokeWidth="24" strokeLinecap="round"/></g>
   <text x="540" y="1190" fill={W} fontFamily={FONT} fontSize="49" fontWeight="900" textAnchor="middle">PRUÉBALO CON ALGUIEN</text>
   <text x="540" y="1290" fill={Y} fontFamily={FONT} fontSize="36" textAnchor="middle">¿EN QUÉ DISTANCIA DESAPARECE?</text></>;
 }
 return <AbsoluteFill style={{background:'radial-gradient(circle at 45% 36%,#152c4b,#081327 65%,#03060f)'}}>
 <svg width="1080" height="1920" viewBox="0 0 1080 1920"><Stars/>{graphic}</svg>
 <div style={{position:'absolute',top:90,left:65,right:65,display:'flex',justifyContent:'space-between',fontFamily:FONT,color:'#add7e8',fontSize:27,fontWeight:800,letterSpacing:4}}>
 <span>VARIADO / CIENCIA</span><span>{i+1} / 8</span></div>
 <div style={{position:'absolute',top:250,left:90,right:90,color:W,fontFamily:FONT,textAlign:'center',fontSize:56,fontWeight:900,textShadow:'0px 5px 20px #020713'}}>{['TIENES UN PUNTO INVISIBLE','HAZ ESTA PRUEBA','OBSERVA EL PUNTO','DENTRO DE TU OJO','LA SALIDA DEL NERVIO','EL CEREBRO INTERPRETA','EL HUECO SE RELLENA','AHORA COMPRUÉBALO'][i]}</div>
 </AbsoluteFill>;
};
export const SUBS={arriba:1575,size:49,acento:Y};
export const Escena:React.FC=()=>{const {s}=useS();let k=lines.findIndex((x:any)=>s>=x.start&&s<x.end);if(k<0)k=s>=lines[lines.length-1].start?lines.length-1:0;
 return <AbsoluteFill><Scene i={k} s={s}/><div style={{position:'absolute',bottom:135,left:72,right:72,height:6,background:'#224365',borderRadius:6}}><div style={{height:6,width:(100*s/DUR)+'%',background:Y,borderRadius:6}}/></div></AbsoluteFill>;
};
