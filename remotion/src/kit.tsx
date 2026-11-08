// Kit compartido para los videos Remotion de Variado y Dinero.
// La escena de cada video (src/Escena.tsx) la escribe Claude y usa estas piezas.
// Todo se ata a la voz: T(i) y en('palabra') dan el segundo exacto en que se dice.
import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate as interpolarRemotion, spring, Easing} from 'remotion';
import data from '../public/palabras.json';

export type Palabra = {w: string; t: number; d: number; f?: boolean; k?: boolean};
export const DUR: number = (data as {dur: number}).dur;
export const words: Palabra[] = (data as {words: Palabra[]}).words;
export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
// 8-nov: con la voz real el rango puede salir desordenado y Remotion rompe; aqui se ordena solo.
export const interpolate: typeof interpolarRemotion = (x, ent, sal, op) => {
  const e = ent.map((v) => (Number.isFinite(v) ? v : 0));
  for (let i = 1; i < e.length; i++) if (e[i] <= e[i - 1]) e[i] = e[i - 1] + 0.001;
  return interpolarRemotion(Number.isFinite(x) ? x : 0, e, sal, op);
};
export {Easing, spring, AbsoluteFill};
export {Entrar} from './Entrar';

export const FONT = 'Poppins, "Segoe UI", Arial, sans-serif';
export const MANO = '"Patrick Hand", "Segoe Print", cursive';

const norm = (x: string) => x.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9ñ]/g, '');

/** Segundo en que empieza la palabra número i (0 = primera palabra del guion). */
export const T = (i: number) => words[Math.max(0, Math.min(words.length - 1, i))].t;

/** Índice de la n-ésima vez que aparece `palabra` (desde el índice `desde`). Lanza error si no existe. */
export const idx = (palabra: string, n = 1, desde = 0) => {
  const p = norm(palabra);
  let c = 0;
  for (let i = desde; i < words.length; i++) if (norm(words[i].w) === p && ++c === n) return i;
  throw new Error('Palabra no encontrada en el guion: ' + palabra + ' #' + n);
};

/** Segundo en que se dice `palabra` (n-ésima aparición). */
export const en = (palabra: string, n = 1, desde = 0) => T(idx(palabra, n, desde));

/** Segundo en que termina de decirse `palabra`. */
export const fin = (palabra: string, n = 1, desde = 0) => {
  const i = idx(palabra, n, desde);
  return words[i].t + words[i].d;
};

/** Reloj de la escena: s = segundo actual; spr = resorte desde t0; lin = transición t0→t1 de a a b. */
export const useS = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = frame / fps;
  const spr = (t0: number, damping = 13, stiffness = 140) => spring({frame: frame - Math.round(t0 * fps), fps, config: {damping, stiffness}});
  const lin = (t0: number, t1: number, a: number, b: number, ease: (x: number) => number = Easing.inOut(Easing.cubic)) =>
    interpolate(s, [t0, Math.max(t1, t0 + 0.001)], [a, b], {...clamp, easing: ease});
  return {s, frame, fps, spr, lin};
};

/** Rebote amortiguado desde t0 (hipos, golpes, temblores). Vale 0 antes de t0. */
export const golpe = (s: number, t0: number, freq = 25, decay = 7) => (s < t0 ? 0 : Math.exp(-(s - t0) * decay) * Math.sin((s - t0) * freq));

/** Desplazamiento de sacudida de pantalla por varios golpes. */
export const sacudida = (s: number, tiempos: number[], fuerza = 16) => {
  const k = tiempos.reduce((a, t) => a + Math.max(0, golpe(s, t, 60, 9)), 0);
  return {x: Math.sin(s * 80) * fuerza * k, y: Math.cos(s * 70) * fuerza * 0.8 * k};
};

/** Visible entre t0 y t1 con fundido corto (devuelve 0..1). */
export const ventana = (s: number, t0: number, t1: number, fade = 0.25) =>
  Math.min(interpolate(s, [t0 - fade, t0], [0, 1], clamp), interpolate(s, [t1, t1 + fade], [1, 0], clamp));

/** Fondo con degradado, manchas desenfocadas (bokeh) y partículas que suben. */
export const Fondo: React.FC<{colores?: [string, string, string]; manchas?: string[]; particulas?: string; cantidad?: number}> = ({
  colores = ['#3a1d6e', '#1c0f3d', '#0b0620'],
  manchas = ['rgba(170,120,255,0.18)', 'rgba(255,143,177,0.14)'],
  particulas = '#ffffff',
  cantidad = 30,
}) => {
  const {s} = useS();
  return (
    <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, ${colores[0]} 0%, ${colores[1]} 55%, ${colores[2]} 100%)`}}>
      {Array.from({length: 14}).map((_, i) => {
        const r = 60 + ((i * 53) % 140);
        const x = ((i * 271) % 1180) - 50 + Math.sin(s * 0.3 + i) * 40;
        const y = ((i * 419) % 2000) - 40 + Math.cos(s * 0.25 + i * 2) * 50;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: r, height: r, borderRadius: r, background: manchas[i % manchas.length], filter: 'blur(14px)'}} />;
      })}
      {Array.from({length: cantidad}).map((_, i) => {
        const x = (i * 137) % 1080;
        const y = 1920 - ((i * 251 + s * (20 + (i % 4) * 15)) % 2000);
        return <div key={'p' + i} style={{position: 'absolute', left: x, top: y, width: 5, height: 5, borderRadius: 3, background: particulas, opacity: 0.25}} />;
      })}
      <AbsoluteFill style={{background: 'radial-gradient(circle, transparent 50%, rgba(0,0,0,0.6) 100%)'}} />
    </AbsoluteFill>
  );
};

// Método V2: si alguna palabra trae k (la key de su escena), los subtítulos van al estilo V2 (blanco grueso y la key en caja de acento).
const CONCLAVE = words.some((w) => w.k);

/** Subtítulos arriba: hasta 3 palabras por bloque sin mezclar frases; la palabra dicha va seleccionada. */
export const Subtitulos: React.FC<{arriba?: number; size?: number; acento?: string}> = ({arriba = 210, size = 64, acento = '#7fb2ff'}) => {
  const {s, spr} = useS();
  const grupos: number[][] = [];
  let actual: number[] = [];
  words.forEach((w, i) => {
    if ((w.f && actual.length) || actual.length === 3) {
      grupos.push(actual);
      actual = [];
    }
    actual.push(i);
  });
  if (actual.length) grupos.push(actual);
  const k = grupos.findIndex((g, n) => s >= T(g[0]) - 0.05 && (n === grupos.length - 1 || s < T(grupos[n + 1][0]) - 0.05));
  if (k < 0) return null;
  const g = grupos[k];
  const pop = spr(T(g[0]) - 0.05, 15, 240);
  return (
    <div style={{position: 'absolute', top: arriba, left: 40, right: 40, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 18, opacity: pop, transform: `translateY(${(1 - pop) * 20}px)`}}>
      {g.map((j) => {
        const act = s >= T(j) && (j + 1 >= words.length || s < T(j + 1));
        if (CONCLAVE) {
          const esK = !!words[j].k && s >= T(j) - 0.05;
          const pulso = esK ? 1 + 0.08 * Math.max(0, 1 - (s - T(j)) * 4) : 1;
          return (
            <div key={j} style={{position: 'relative', fontFamily: FONT, fontWeight: 800, fontSize: size, color: esK ? '#111' : '#fff', padding: '2px 14px', borderRadius: 14, background: esK ? acento : 'transparent', transform: `scale(${pulso})`, textShadow: esK ? 'none' : '0 3px 0 rgba(0,0,0,0.55), 0 6px 18px rgba(0,0,0,0.6)'}}>
              {words[j].w}
            </div>
          );
        }
        return (
          <div key={j} style={{position: 'relative', fontFamily: FONT, fontWeight: act ? 800 : 600, fontSize: size, color: act ? '#fff' : 'rgba(255,255,255,0.55)', padding: '0 12px', textShadow: '0 4px 18px rgba(0,0,0,0.6)'}}>
            {words[j].w}
            {act && (
              <div style={{position: 'absolute', inset: -2, border: `3px solid ${acento}`, background: 'rgba(127,178,255,0.14)'}}>
                {[0, 1, 2, 3].map((c) => (
                  <div key={c} style={{position: 'absolute', width: 12, height: 12, background: '#fff', border: `2px solid ${acento}`, left: c % 2 ? undefined : -7, right: c % 2 ? -7 : undefined, top: c < 2 ? -7 : undefined, bottom: c < 2 ? undefined : -7}} />
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

/** Rótulo de escena escrito a mano arriba a la izquierda: items = [[desde, hasta, texto], ...]. */
export const Rotulo: React.FC<{items: [number, number, string][]}> = ({items}) => {
  const {s} = useS();
  const it = items.find(([a, b]) => s >= a && s < b);
  if (!it) return null;
  const vis = interpolate(s, [it[0], it[0] + 0.3], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', left: 60, top: 120, fontFamily: MANO, fontSize: 38, color: 'rgba(255,255,255,0.75)', opacity: vis}}>
      {it[2].slice(0, Math.ceil(it[2].length * vis))}
      <div style={{height: 2, width: 260 * vis, background: 'rgba(255,255,255,0.4)', marginTop: 4}} />
    </div>
  );
};

/** Etiqueta con línea que apunta a algo. (x,y) = caja; (px,py) = punto señalado. Aparece en t0. */
export const Etiqueta: React.FC<{texto: string; x: number; y: number; px: number; py: number; t0: number; size?: number; color?: string}> = ({texto, x, y, px, py, t0, size = 32, color = '#fff'}) => {
  const {lin} = useS();
  const a = lin(t0, t0 + 0.35, 0, 1);
  if (a <= 0) return null;
  return (
    <>
      <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <line x1={px} y1={py} x2={px + (x - px) * a} y2={py + (y - py) * a} stroke={color} strokeWidth={3} />
        <circle cx={px} cy={py} r={7} fill={color} />
      </svg>
      <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) scale(${0.8 + 0.2 * a})`, opacity: a, background: 'rgba(10,6,30,0.85)', border: `2px solid ${color}`, borderRadius: 10, padding: '6px 16px', fontFamily: FONT, fontWeight: 800, fontSize: size, color, whiteSpace: 'nowrap'}}>
        {texto}
      </div>
    </>
  );
};

/** Contador animado dentro de una píldora (▶ 1,000). Cuenta de `desde` a `hasta` entre t0 y t1. */
export const Contador: React.FC<{desde?: number; hasta: number; t0: number; t1: number; x?: number; y: number; prefijo?: string; sufijo?: string; decimales?: number; color?: string; size?: number; flecha?: boolean}> = ({
  desde = 0, hasta, t0, t1, x = 540, y, prefijo = '', sufijo = '', decimales = 0, color = '#ffd84d', size = 84, flecha = true,
}) => {
  const {spr, lin} = useS();
  const pop = spr(t0 - 0.05, 10, 200);
  if (pop <= 0.001) return null;
  const v = lin(t0, t1, desde, hasta, Easing.out(Easing.cubic));
  const txt = v.toLocaleString('en-US', {minimumFractionDigits: decimales, maximumFractionDigits: decimales});
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) scale(${pop})`, background: 'rgba(8,10,20,0.9)', border: `3px solid ${color}`, borderRadius: 80, padding: '10px 40px', fontFamily: FONT, fontWeight: 800, fontSize: size, color, whiteSpace: 'nowrap', boxShadow: `0 0 40px ${color}55`}}>
      {flecha ? '▶ ' : ''}
      {prefijo}
      {txt}
      {sufijo}
    </div>
  );
};

/** Personaje redondo con cara (la "carita"). hipos/saltos = segundos en que da un brinco. */
export const Carita: React.FC<{x?: number; y?: number; size?: number; color?: [string, string, string]; saltos?: number[]; boca?: 'o' | 'feliz' | 'triste'; texto?: string}> = ({
  x = 540, y = 1120, size = 440, color = ['#ffe0a3', '#ffb347', '#e0782a'], saltos = [], boca = 'o', texto,
}) => {
  const {s} = useS();
  const k = saltos.reduce((a, b) => a + golpe(s, b), 0);
  const parpadeo = s % 3.1 < 0.12 ? 0.1 : 1;
  const u = size / 440;
  return (
    <div style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size, transform: `translateY(${-70 * u * Math.abs(k)}px) scale(${1 - 0.06 * k}, ${1 + 0.12 * k})`}}>
      <div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: `radial-gradient(circle at 35% 30%, ${color[0]}, ${color[1]} 55%, ${color[2]} 100%)`, boxShadow: `0 30px 80px rgba(0,0,0,0.5), 0 0 80px ${color[1]}55`}} />
      {[150, 290].map((ex) => (
        <div key={ex} style={{position: 'absolute', left: (ex - 22) * u, top: (160 + 28 * (1 - parpadeo)) * u, width: 44 * u, height: 56 * u * parpadeo, borderRadius: 30 * u, background: '#2a1640'}} />
      ))}
      <div style={{position: 'absolute', left: 90 * u, top: 250 * u, width: 60 * u, height: 30 * u, borderRadius: 30 * u, background: 'rgba(255,100,120,0.45)'}} />
      <div style={{position: 'absolute', left: 290 * u, top: 250 * u, width: 60 * u, height: 30 * u, borderRadius: 30 * u, background: 'rgba(255,100,120,0.45)'}} />
      {boca === 'o' && <div style={{position: 'absolute', left: 190 * u, top: 285 * u, width: 60 * u, height: (40 + 30 * Math.abs(k)) * u, borderRadius: '50%', background: '#2a1640'}} />}
      {boca !== 'o' && (
        <svg width={size} height={size} style={{position: 'absolute', left: 0, top: 0}} viewBox="0 0 440 440">
          <path d={boca === 'feliz' ? 'M 170 290 Q 220 345 270 290' : 'M 170 320 Q 220 270 270 320'} stroke="#2a1640" strokeWidth={14} fill="none" strokeLinecap="round" />
        </svg>
      )}
      {texto &&
        saltos.map((b, i) =>
          s > b && s < b + 0.9 ? (
            <div key={i} style={{position: 'absolute', left: i % 2 ? size * 0.8 : -size * 0.1, top: -30 - (s - b) * 160, fontFamily: FONT, fontWeight: 800, fontSize: 70 * u, color: '#ffd84d', opacity: 1 - (s - b) / 0.9, transform: `rotate(${i % 2 ? 12 : -12}deg) scale(${Math.min(1, (s - b) * 8)})`}}>
              {texto}
            </div>
          ) : null,
        )}
    </div>
  );
};

/** Cámara: mueve y acerca a sus hijos según paradas [{t, x, y, zoom}] (x,y = punto que queda al centro). */
export const Camara: React.FC<{paradas: {t: number; x: number; y: number; zoom: number}[]; children: React.ReactNode; centroY?: number}> = ({paradas, children, centroY = 1000}) => {
  const {s} = useS();
  const ts = paradas.map((p) => p.t);
  const val = (k: 'x' | 'y' | 'zoom') => (paradas.length === 1 ? paradas[0][k] : interpolate(s, ts, paradas.map((p) => p[k]), {...clamp, easing: Easing.inOut(Easing.cubic)}));
  const z = val('zoom');
  return <AbsoluteFill style={{transformOrigin: '0 0', transform: `translate(${540 - val('x') * z}px, ${centroY - val('y') * z}px) scale(${z})`}}>{children}</AbsoluteFill>;
};

/** Estela de movimiento: dibuja copias del objeto en tiempos pasados mientras s está entre t0 y t1. */
export const Estela: React.FC<{t0: number; t1: number; copias?: number; paso?: number; render: (s: number, alpha: number) => React.ReactNode}> = ({t0, t1, copias = 4, paso = 0.035, render}) => {
  const {s} = useS();
  if (s < t0 || s > t1) return null;
  return <>{Array.from({length: copias}).map((_, i) => <React.Fragment key={i}>{render(s - (copias - i) * paso, 0.12 * (i + 1))}</React.Fragment>)}</>;
};

/** Destello blanco de pantalla completa en t0. */
export const Destello: React.FC<{t0: number; fuerza?: number}> = ({t0, fuerza = 0.5}) => {
  const {s} = useS();
  const a = Math.max(0, 1 - Math.abs(s - t0 - 0.03) * 10) * fuerza;
  return a > 0 ? <AbsoluteFill style={{background: '#fff', opacity: a}} /> : null;
};

/** Ondas expansivas desde (x,y) en t0. */
export const Ondas: React.FC<{x: number; y: number; t0: number; color?: string; radio?: number}> = ({x, y, t0, color = '#fff', radio = 420}) => {
  const {s} = useS();
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
      {[0, 0.12, 0.24].map((d, i) => {
        const t = s - t0 - d;
        if (t < 0 || t > 0.7) return null;
        return <circle key={i} cx={x} cy={y} r={40 + t * radio} stroke={color} strokeWidth={6} fill="none" opacity={1 - t / 0.7} />;
      })}
    </svg>
  );
};

/** Texto de impacto tipo cómic (¡HIP!, ¡PUM!) con estrella detrás. */
export const Impacto: React.FC<{texto: string; t0: number; t1: number; color?: string; tinta?: string; size?: number}> = ({texto, t0, t1, color = '#ffd84d', tinta = '#2a1640', size = 230}) => {
  const {s, spr} = useS();
  if (s < t0 || s > t1) return null;
  const e = spr(t0, 8, 260);
  const fuera = interpolate(s, [t1 - 0.3, t1], [1, 0], clamp);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: fuera}}>
      <svg width={900} height={900} viewBox="-450 -450 900 900" style={{position: 'absolute', transform: `scale(${e}) rotate(${s * 20}deg)`}}>
        <polygon points={Array.from({length: 28}).map((_, i) => {
          const r = i % 2 ? 230 : 400;
          const a = (i / 28) * Math.PI * 2;
          return `${Math.cos(a) * r},${Math.sin(a) * r}`;
        }).join(' ')} fill={color} opacity={0.92} />
      </svg>
      <div style={{fontFamily: FONT, fontWeight: 800, fontSize: size, color: tinta, transform: `scale(${e}) rotate(-8deg)`}}>{texto}</div>
    </AbsoluteFill>
  );
};
