// Acabado para los videos 2.5D: envuelve la escena sin tocar su animación.
import React, {useMemo} from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';

/* Grano de película: una sola textura que se desplaza en cada cuadro. */
const grano = () => {
  const el = document.createElement('canvas');
  el.width = el.height = 256;
  const c = el.getContext('2d') as CanvasRenderingContext2D;
  const img = c.createImageData(256, 256);
  let x = 12345;
  for (let i = 0; i < img.data.length; i += 4) {
    x = (x * 1103515245 + 12345) % 2147483648;
    const v = 96 + (x % 64);
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  c.putImageData(img, 0, 0);
  return el.toDataURL('image/png');
};

const mota = (i: number) => ({x: (i * 271) % 1080, y: (i * 419) % 1920, r: 5 + (i * 7) % 15, v: 10 + (i * 3) % 18, f: 1 + (i % 3)});

export const Acabado: React.FC<{cortes: number[]; children: React.ReactNode}> = ({cortes, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = frame / fps;
  const textura = useMemo(grano, []);

  /* Cámara en mano continua, para que nada quede quieto. */
  const mx = Math.sin(s * 0.9) * 7 + Math.sin(s * 2.3) * 3;
  const my = Math.cos(s * 0.7) * 9 + Math.sin(s * 1.9) * 2;
  const giro = Math.sin(s * 0.5) * 0.35;

  /* Antes de cada corte la cámara se mete en la escena; al otro lado llega desenfocada. */
  let z = 1;
  let borroso = 0;
  for (const c of cortes) {
    const d = s - c;
    if (d >= -0.3 && d < 0) {
      const k = (d + 0.3) / 0.3;
      z = 1 + 1.3 * k * k * k;
      borroso = 16 * k * k;
    }
    if (d >= 0 && d < 0.22) borroso = 12 * (1 - d / 0.22);
  }

  const luzX = 300 + Math.sin(s * 0.3) * 220;
  const luzY = 420 + Math.cos(s * 0.22) * 160;

  return (
    <AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
      <AbsoluteFill style={{transformOrigin: '540px 800px', transform: `translate(${mx}px, ${my}px) rotate(${giro}deg) scale(${1.04 * z})`, filter: `contrast(1.09) saturate(1.08)${borroso > 0.3 ? ` blur(${borroso}px)` : ''}`}}>
        {children}
      </AbsoluteFill>
      <AbsoluteFill style={{background: `radial-gradient(900px 1200px at ${luzX}px ${luzY}px, rgba(255,226,170,.85), rgba(255,226,170,0) 70%)`, mixBlendMode: 'soft-light'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,8,24,0) 70%, rgba(10,8,24,.3) 100%)', mixBlendMode: 'multiply'}} />
      {[...Array(24).keys()].map((i) => {
        const m = mota(i);
        const y = ((m.y - s * m.v) % 1980 + 1980) % 1980 - 30;
        const x = m.x + Math.sin(s * 0.5 + i) * 24 - mx * m.f;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: m.r * 2, height: m.r * 2, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,240,205,.5), rgba(255,240,205,0) 70%)'}} />;
      })}
      <AbsoluteFill style={{background: `radial-gradient(300px 480px at ${-60 - mx * 4}px ${1860 - my * 4}px, rgba(5,4,12,.7), rgba(5,4,12,0) 72%), radial-gradient(360px 520px at ${1130 - mx * 4}px ${130 - my * 4}px, rgba(5,4,12,.62), rgba(5,4,12,0) 72%)`}} />
      <AbsoluteFill style={{backgroundImage: `url(${textura})`, backgroundPosition: `${(frame * 73) % 256}px ${(frame * 131) % 256}px`, mixBlendMode: 'overlay', opacity: 0.2}} />
    </AbsoluteFill>
  );
};
