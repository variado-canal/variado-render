// Piezas de cine (13-nov): textura, profundidad, pasos entre sitios, recorridos, paleta por sentido, regla y chip.
// Son herramientas, no escenas: cada video dibuja lo suyo encima. Todo sale del tiempo (sin azar).
import React from 'react';
import {AbsoluteFill, interpolateColors} from 'remotion';
import {useS, clamp, interpolate, Easing, FONT} from './kit';

/** Número fijo entre 0 y 1 para el índice i (reemplaza al azar). */
export const h = (i: number) => {
  const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
};

/** Color que cambia con el sentido: en cada tiempo de `tiempos` toma el color de `colores` (mismo largo). */
export const tono = (s: number, tiempos: number[], colores: string[], fundido = 0.6) => {
  if (tiempos.length < 2) return colores[0];
  const ent: number[] = [];
  const sal: string[] = [];
  tiempos.forEach((t, i) => {
    if (i > 0) { ent.push(t - fundido / 2); sal.push(colores[i - 1]); }
    ent.push(i === 0 ? t : t + fundido / 2);
    sal.push(colores[i]);
  });
  for (let i = 1; i < ent.length; i++) if (ent[i] <= ent[i - 1]) ent[i] = ent[i - 1] + 0.001;
  return interpolateColors(Math.max(ent[0], Math.min(ent[ent.length - 1], s)), ent, sal);
};

/** Superficie con materia (piel, células, fibra, papel) para que ningún fondo sea color plano. Estática y barata. */
export const Textura: React.FC<{tipo?: 'piel' | 'celulas' | 'fibra' | 'papel'; base: string; linea: string; luz?: string; semilla?: number; escala?: number; opacidad?: number}> = ({
  tipo = 'piel', base, linea, luz = 'rgba(255,255,255,0.18)', semilla = 1, escala = 1, opacidad = 1,
}) => {
  const n = tipo === 'fibra' ? 26 : tipo === 'papel' ? 0 : 70;
  const formas: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const a = h(i + semilla * 101), b = h(i * 3 + semilla * 7), c = h(i * 7 + semilla * 13);
    const x = (a * 1300 - 110) * 1, y = b * 2140 - 110;
    if (tipo === 'piel') {
      const r = (70 + c * 90) * escala;
      const p = Array.from({length: 6}).map((_, k) => {
        const ang = (k / 6) * Math.PI * 2 + c;
        const rr = r * (0.75 + 0.45 * h(i * 11 + k));
        return `${(x + Math.cos(ang) * rr).toFixed(0)},${(y + Math.sin(ang) * rr).toFixed(0)}`;
      });
      formas.push(<polygon key={i} points={p.join(' ')} fill="none" stroke={linea} strokeWidth={3 + c * 3} strokeLinejoin="round" opacity={0.55} />);
    } else if (tipo === 'celulas') {
      const r = (45 + c * 70) * escala;
      formas.push(<g key={i}><ellipse cx={x} cy={y} rx={r} ry={r * (0.75 + a * 0.3)} fill={luz} stroke={linea} strokeWidth={5} /><circle cx={x + r * 0.2} cy={y - r * 0.1} r={r * 0.28} fill={linea} opacity={0.6} /></g>);
    } else {
      const y2 = y + (c - 0.5) * 300;
      formas.push(<path key={i} d={`M -40 ${y} C 300 ${y - 120 * c} 700 ${y2 + 90} 1120 ${y2}`} stroke={i % 3 ? linea : luz} strokeWidth={6 + c * 14} fill="none" opacity={0.5} />);
    }
  }
  return (
    <AbsoluteFill style={{background: base, opacity: opacidad}}>
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        {formas}
        {Array.from({length: 160}).map((_, i) => (
          <circle key={'g' + i} cx={h(i + semilla * 31) * 1080} cy={h(i * 5 + semilla) * 1920} r={1.5 + h(i * 9) * 3.5} fill={i % 2 ? linea : luz} opacity={0.35} />
        ))}
      </svg>
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 40% 35%, ${luz} 0%, transparent 60%)`}} />
    </AbsoluteFill>
  );
};

/** Tres profundidades: manchas grandes desenfocadas delante (pasan más rápido) y bokeh lejano. Máximo 6 manchas. */
export const Profundidad: React.FC<{color?: string; lejos?: string; manchas?: number; semilla?: number; deriva?: number}> = ({
  color = 'rgba(20,8,20,0.55)', lejos = 'rgba(255,255,255,0.10)', manchas = 3, semilla = 1, deriva = 1,
}) => {
  const {s} = useS();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {Array.from({length: 8}).map((_, i) => {
        const r = 30 + h(i + semilla * 17) * 50;
        return <div key={'l' + i} style={{position: 'absolute', left: h(i * 3 + semilla) * 1080 + Math.sin(s * 0.2 + i) * 20 * deriva, top: h(i * 7 + semilla) * 1920, width: r, height: r, borderRadius: r, background: lejos, filter: 'blur(8px)'}} />;
      })}
      {Array.from({length: Math.min(6, manchas)}).map((_, i) => {
        const r = 260 + h(i * 13 + semilla) * 260;
        const lado = i % 2 ? 1080 - r * 0.45 : -r * 0.55;
        const y = h(i * 5 + semilla * 3) * 1700 - 100 - s * 22 * deriva * (0.6 + h(i) * 0.8);
        return <div key={'c' + i} style={{position: 'absolute', left: lado, top: ((y % 2200) + 2200) % 2200 - 300, width: r, height: r, borderRadius: r, background: `radial-gradient(circle, ${color} 0%, transparent 70%)`, filter: 'blur(22px)'}} />;
      })}
    </AbsoluteFill>
  );
};

/** Luz suave (bloom) detrás de lo que brilla. */
export const Brillo: React.FC<{x: number; y: number; r?: number; color?: string; t0?: number}> = ({x, y, r = 260, color = 'rgba(255,240,200,0.55)', t0}) => {
  const {s, spr} = useS();
  const a = t0 === undefined ? 1 : spr(t0, 14, 120);
  if (a <= 0.001) return null;
  const late = 1 + Math.sin(s * 2.2) * 0.04;
  return <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: r * 2, opacity: a, transform: `scale(${late})`, background: `radial-gradient(circle, ${color} 0%, transparent 65%)`, mixBlendMode: 'screen'}} />;
};

/** Paso entre dos sitios en el segundo t (pon t = en('palabra')). Tipos:
 *  entrar: la cámara entra por (x,y) y el nuevo sitio se abre desde ese punto.
 *  forma: un círculo en (x,y) crece y dentro ya está el nuevo sitio (poro → cráter, moneda → planeta).
 *  barrido: la cámara gira rápido hacia un lado y llega al nuevo sitio (lugares en paralelo).
 *  alejar: el sitio viejo se encoge hasta (x,y) dentro del nuevo (revela tamaño o contexto). */
export const Paso: React.FC<{t: number; tipo: 'entrar' | 'forma' | 'barrido' | 'alejar'; x?: number; y?: number; dur?: number; antes: React.ReactNode; despues: React.ReactNode}> = ({
  t, tipo, x = 540, y = 960, dur, antes, despues,
}) => {
  const {s} = useS();
  const d = dur ?? (tipo === 'barrido' ? 0.35 : tipo === 'forma' ? 0.6 : 0.8);
  const t0 = t - d * 0.6;
  const k = Math.max(0, Math.min(1, (s - t0) / d));
  if (k <= 0) return <AbsoluteFill>{antes}</AbsoluteFill>;
  if (k >= 1) return <AbsoluteFill>{despues}</AbsoluteFill>;
  const e = Easing.inOut(Easing.cubic)(k);
  const o = `${x}px ${y}px`;
  if (tipo === 'barrido') {
    const dx = e * 1300;
    return (
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <AbsoluteFill style={{transform: `translateX(${-dx}px) skewX(${-Math.sin(e * Math.PI) * 8}deg)`, filter: `blur(${Math.sin(e * Math.PI) * 10}px)`}}>{antes}</AbsoluteFill>
        <AbsoluteFill style={{transform: `translateX(${1300 - dx}px) skewX(${-Math.sin(e * Math.PI) * 8}deg)`, filter: `blur(${Math.sin(e * Math.PI) * 10}px)`}}>{despues}</AbsoluteFill>
      </AbsoluteFill>
    );
  }
  if (tipo === 'alejar') {
    return (
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <AbsoluteFill style={{transformOrigin: o, transform: `scale(${2.6 - 1.6 * e})`, opacity: Math.min(1, e * 3)}}>{despues}</AbsoluteFill>
        <AbsoluteFill style={{transformOrigin: o, transform: `scale(${1 - 0.92 * e})`, opacity: 1 - e, clipPath: `circle(${(1 - e) * 1200 + 40}px at ${x}px ${y}px)`}}>{antes}</AbsoluteFill>
      </AbsoluteFill>
    );
  }
  const r = tipo === 'forma' ? 40 + e * 2200 : Math.max(0, (e - 0.35) / 0.65) ** 2 * 2300;
  const z = tipo === 'entrar' ? Math.pow(9, e) : 1 + e * 0.25;
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill style={{transformOrigin: o, transform: `scale(${z})`}}>{antes}</AbsoluteFill>
      <AbsoluteFill style={{clipPath: `circle(${r}px at ${x}px ${y}px)`, transformOrigin: o, transform: `scale(${0.6 + 0.4 * e})`}}>{despues}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Punto a lo largo de un camino [[x,y],...] entre t0 y t1 (para procesos: boca → estómago → sangre → pulmón). */
export const enCamino = (s: number, puntos: [number, number][], t0: number, t1: number) => {
  const largos = puntos.slice(1).map((p, i) => Math.hypot(p[0] - puntos[i][0], p[1] - puntos[i][1]));
  const total = largos.reduce((a, b) => a + b, 0) || 1;
  const p = interpolate(s, [t0, t1], [0, 1], {...clamp, easing: Easing.inOut(Easing.sin)});
  let falta = p * total;
  for (let i = 0; i < largos.length; i++) {
    if (falta <= largos[i] || i === largos.length - 1) {
      const k = largos[i] ? Math.min(1, falta / largos[i]) : 0;
      const [ax, ay] = puntos[i], [bx, by] = puntos[i + 1];
      return {x: ax + (bx - ax) * k, y: ay + (by - ay) * k, ang: Math.atan2(by - ay, bx - ax) * 180 / Math.PI, p};
    }
    falta -= largos[i];
  }
  return {x: puntos[0][0], y: puntos[0][1], ang: 0, p};
};

/** Paradas de Camara que siguen el mismo camino (la cámara acompaña al objeto). */
export const seguir = (puntos: [number, number][], t0: number, t1: number, zoom = 1.6, pasos = 6) =>
  Array.from({length: pasos + 1}).map((_, i) => {
    const t = t0 + ((t1 - t0) * i) / pasos;
    const q = enCamino(t, puntos, t0, t1);
    return {t, x: q.x, y: q.y, zoom};
  });

/** El objeto viaja por el camino y deja rastro. render(x, y, ang) dibuja el objeto. Va dentro de un svg 1080x1920. */
export const Recorrido: React.FC<{puntos: [number, number][]; t0: number; t1: number; color?: string; rastro?: boolean; render: (x: number, y: number, ang: number) => React.ReactNode}> = ({
  puntos, t0, t1, color = 'rgba(231,255,0,0.8)', rastro = true, render,
}) => {
  const {s} = useS();
  if (s < t0 - 0.3) return null;
  const q = enCamino(s, puntos, t0, t1);
  const hechos: [number, number][] = [];
  for (let i = 0; i <= 24; i++) {
    const r = enCamino(t0 + ((Math.min(s, t1) - t0) * i) / 24, puntos, t0, t1);
    hechos.push([r.x, r.y]);
  }
  return (
    <g>
      {rastro && s > t0 && <polyline points={hechos.map((p) => p.join(',')).join(' ')} fill="none" stroke={color} strokeWidth={10} strokeLinecap="round" strokeDasharray="2 22" opacity={0.85} />}
      {render(q.x, q.y, q.ang)}
    </g>
  );
};

/** Regla de medida que se dibuja con su cifra ("0,3 mm") para dar tamaño con referencia. */
export const Regla: React.FC<{x: number; y: number; largo: number; t0: number; texto: string; vertical?: boolean; color?: string}> = ({x, y, largo, t0, texto, vertical = true, color = '#E7FF00'}) => {
  const {lin} = useS();
  const a = lin(t0, t0 + 0.45, 0, 1, Easing.out(Easing.cubic));
  if (a <= 0) return null;
  const L = largo * a;
  const [x2, y2] = vertical ? [x, y + L] : [x + L, y];
  const tick = (px: number, py: number, k: number) => vertical
    ? <line key={k} x1={px - 22} y1={py} x2={px + 22} y2={py} stroke={color} strokeWidth={5} strokeLinecap="round" />
    : <line key={k} x1={px} y1={py - 22} x2={px} y2={py + 22} stroke={color} strokeWidth={5} strokeLinecap="round" />;
  return (
    <>
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <line x1={x} y1={y} x2={x2} y2={y2} stroke={color} strokeWidth={5} />
        {tick(x, y, 0)}
        {a > 0.95 && tick(x2, y2, 1)}
      </svg>
      <div style={{position: 'absolute', left: vertical ? x - 24 : x + L / 2, top: vertical ? y + L / 2 : y - 34, transform: vertical ? 'translate(-100%, -50%)' : 'translate(-50%, -100%)', opacity: a, fontFamily: FONT, fontWeight: 800, fontSize: 46, color: '#111', background: color, borderRadius: 10, padding: '2px 14px', whiteSpace: 'nowrap'}}>{texto}</div>
    </>
  );
};

/** Chip de dato (un año, una cifra corta) que entra con brillo. */
export const Chip: React.FC<{texto: string; x: number; y: number; t0: number; t1?: number; color?: string; size?: number}> = ({texto, x, y, t0, t1 = 9999, color = '#E7FF00', size = 76}) => {
  const {s, spr} = useS();
  const a = spr(t0 - 0.05, 12, 200) * interpolate(s, [t1, t1 + 0.3], [1, 0], clamp);
  if (a <= 0.001) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) scale(${a})`, fontFamily: FONT, fontWeight: 800, fontSize: size, color: '#fff', padding: '6px 30px', borderRadius: 22, background: 'linear-gradient(180deg, rgba(40,48,80,0.92), rgba(12,14,30,0.92))', border: `3px solid ${color}`, boxShadow: `0 0 ${40 * a}px ${color}88, inset 0 2px 0 rgba(255,255,255,0.25)`}}>
      {texto}
    </div>
  );
};