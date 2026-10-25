// EJEMPLO APROBADO (hipo). Cada video reemplaza este archivo con su propia escena.
// Guion: "Cada vez que te da hipo, tu cuerpo hace algo muy raro. Aquí abajo tienes un músculo llamado diafragma.
// Sube y baja tranquilo para que respires. Pero a veces se irrita y da un tirón. El aire entra de golpe.
// Y en menos de una décima de segundo, tus cuerdas vocales se cierran. Ese portazo es el hip que escuchas.
// Envíaselo a alguien que siempre tiene hipo."
import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, clamp, useS, en, golpe, sacudida, Fondo, Rotulo, Carita, Camara, Estela, Etiqueta, Destello, Ondas, Impacto, FONT} from './kit';

const ROSA = '#ff8fb1';
const CIELO = '#9fe3ff';
const AMARILLO = '#ffd84d';
const VF_Y = 540; // altura de las cuerdas vocales dentro del pecho

// Momentos clave atados a palabras
const A_PECHO = en('Aquí');
const SUBE = en('Sube');
const BAJA = en('baja');
const CALMA_FIN = en('respires');
const IRRITA = en('irrita');
const TIRON = en('tirón');
const AIRE = en('aire');
const GARGANTA = en('menos');
const DECIMA = en('décima');
const CUERDAS = en('cuerdas');
const CIERRAN = en('cierran');
const HIP = en('hip');
const FINAL = en('Envíaselo');

// Posición del diafragma en cada instante (respira, se irrita, da el tirón y vuelve)
const diafragma = (s: number) => {
  const calma = interpolate(s, [SUBE - 0.2, SUBE + 0.3, CALMA_FIN, CALMA_FIN + 0.5], [15, 45, 45, 15], clamp);
  let dy = Math.sin(s * (2 * Math.PI) / 1.7) * calma;
  const tiron = spring({frame: Math.round((s - TIRON + 0.05) * 60), fps: 60, config: {damping: 9, stiffness: 320}});
  const vuelve = interpolate(s, [GARGANTA, GARGANTA + 2], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  dy += 120 * tiron * (1 - vuelve);
  const enojo = interpolate(s, [IRRITA - 0.1, IRRITA + 0.3], [0, 1], clamp) * (1 - vuelve);
  dy += enojo * (s < TIRON ? Math.sin(s * 95) * 7 : 0);
  return {dy, enojo};
};

const Diafragma: React.FC<{s: number; alpha?: number}> = ({s, alpha = 1}) => {
  const {dy, enojo} = diafragma(s);
  const y = 1330 + dy;
  const color = `rgb(255, ${Math.round(143 - 90 * enojo)}, ${Math.round(177 - 120 * enojo)})`;
  return (
    <g opacity={alpha}>
      <path d={`M 170 ${y + 90} Q 540 ${y - 170} 910 ${y + 90}`} stroke={color} strokeWidth={46} fill="none" strokeLinecap="round" />
      {alpha === 1 && (
        <g>
          <ellipse cx={500} cy={y - 32} rx={9} ry={12} fill="#2a1640" />
          <ellipse cx={580} cy={y - 32} rx={9} ry={12} fill="#2a1640" />
          <line x1={482} y1={y - 58 + 10 * enojo} x2={515} y2={y - 52 - 4 * enojo} stroke="#2a1640" strokeWidth={6 * enojo} strokeLinecap="round" />
          <line x1={598} y1={y - 58 + 10 * enojo} x2={565} y2={y - 52 - 4 * enojo} stroke="#2a1640" strokeWidth={6 * enojo} strokeLinecap="round" />
          <path d={`M 522 ${y - 8} Q 540 ${y - 8 + 14 * (1 - 2 * enojo)} 558 ${y - 8}`} stroke="#2a1640" strokeWidth={5} fill="none" strokeLinecap="round" />
        </g>
      )}
    </g>
  );
};

const Pulmon: React.FC<{x: number; inflado: number; flip?: boolean}> = ({x, inflado, flip}) => (
  <g transform={`translate(${x} 1000) scale(${(flip ? -1 : 1) * inflado} ${inflado})`}>
    <path d="M 40 -260 C 150 -260 190 -80 180 80 C 170 230 90 260 0 250 C -60 245 -80 200 -70 120 L -60 -200 C -55 -245 -10 -262 40 -260 Z" fill={ROSA} stroke="#e0607f" strokeWidth={6} />
    <ellipse cx={30} cy={-20} rx={9} ry={12} fill="#2a1640" />
    <ellipse cx={90} cy={-20} rx={9} ry={12} fill="#2a1640" />
    <path d="M 45 20 Q 60 34 75 20" stroke="#2a1640" strokeWidth={5} fill="none" strokeLinecap="round" />
    <ellipse cx={120} cy={-130} rx={30} ry={60} fill="rgba(255,255,255,0.25)" />
  </g>
);

const Pecho: React.FC = () => {
  const {s, spr, lin} = useS();
  const {dy} = diafragma(s);
  const golpeAire = spr(AIRE, 8, 160) * (1 - lin(GARGANTA, GARGANTA + 2, 0, 1));
  const inflado = 0.92 - dy * 0.0012 + 0.14 * golpeAire;
  const abierto = 34 * (1 - spr(CIERRAN - 0.05, 11, 420));
  // aire: una ola entra de golpe; la segunda choca con las cuerdas ya cerradas
  const aire = Array.from({length: 46}).map((_, i) => {
    const ola = i < 26 ? AIRE - 0.1 : DECIMA;
    const p = (s - ola) * (i < 26 ? 1.6 : 0.9) - (i % 26) * 0.045;
    if (p < 0 || p > 1) return null;
    let y = 400 + p * 620;
    const lado = i % 2 ? 1 : -1;
    let x = 540 + Math.sin(i * 7.3) * 30 + (y > 780 ? lado * (y - 780) * 0.75 : 0);
    if (i >= 26 && s > CIERRAN && y > VF_Y - 30) {
      y = VF_Y - 40 - ((i * 13) % 70);
      x = 540 + Math.sin(i * 3.1 + s * 30) * 34;
    }
    const largo = i < 26 ? 34 : 12;
    return <rect key={i} x={x - 4} y={y - largo} width={8} height={largo} rx={4} fill={CIELO} opacity={0.85} />;
  });
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute'}}>
        <path d="M 440 420 L 440 560 C 300 580 150 640 120 820 L 100 1650 L 980 1650 L 960 820 C 930 640 780 580 640 560 L 640 420" stroke="rgba(255,255,255,0.35)" strokeWidth={5} fill="rgba(255,255,255,0.04)" />
        <path d="M 480 400 L 480 790 M 600 400 L 600 790" stroke="#c9a7ff" strokeWidth={10} />
        <path d="M 480 790 Q 440 840 380 880 M 600 790 Q 640 840 700 880" stroke="#c9a7ff" strokeWidth={10} fill="none" />
        {Array.from({length: 9}).map((_, i) => <line key={i} x1={484} x2={596} y1={600 + i * 22} y2={600 + i * 22} stroke="rgba(201,167,255,0.35)" strokeWidth={6} />)}
        <Pulmon x={330} inflado={inflado} flip />
        <Pulmon x={750} inflado={inflado} />
        {aire}
        <polygon points={`484,${VF_Y - 40} 484,${VF_Y + 40} ${540 - abierto},${VF_Y + 6}`} fill="#ffd1dc" stroke="#e0607f" strokeWidth={4} />
        <polygon points={`596,${VF_Y - 40} 596,${VF_Y + 40} ${540 + abierto},${VF_Y + 6}`} fill="#ffd1dc" stroke="#e0607f" strokeWidth={4} />
        <Estela t0={TIRON - 0.05} t1={TIRON + 0.45} render={(t, a) => <Diafragma s={t} alpha={a} />} />
        <Diafragma s={s} />
        {s > SUBE && s < CALMA_FIN + 0.4 && (
          <g opacity={lin(SUBE, SUBE + 0.3, 0, 1) * lin(CALMA_FIN, CALMA_FIN + 0.4, 1, 0)} fill="#fff">
            <polygon points="950,1180 925,1220 975,1220" opacity={s < BAJA ? 1 : 0.3} />
            <polygon points="950,1420 925,1380 975,1380" opacity={s >= BAJA ? 1 : 0.3} />
          </g>
        )}
      </svg>
      <Ondas x={540} y={VF_Y} t0={CIERRAN} />
      <Etiqueta texto="diafragma" x={830} y={1530} px={700} py={1330} t0={en('diafragma')} />
      <Etiqueta texto="cuerdas vocales" x={420} y={VF_Y + 95} px={484} py={VF_Y + 20} t0={CUERDAS} size={16} />
    </AbsoluteFill>
  );
};

const Cronometro: React.FC = () => {
  const {s, spr, lin} = useS();
  const t0 = DECIMA - 0.1;
  const t1 = en('Ese');
  if (s < t0 || s > t1 + 0.3) return null;
  const e = spr(t0, 12, 200) * lin(t1, t1 + 0.3, 1, 0);
  const ang = ((s - t0) * 900 * Math.PI) / 180;
  const valor = Math.min(0.1, ((s - t0) / (CIERRAN - t0)) * 0.1);
  return (
    <div style={{position: 'absolute', left: 760, top: 420, transform: `scale(${e})`, opacity: e}}>
      <svg width={220} height={220} viewBox="0 0 220 220">
        <circle cx={110} cy={120} r={88} stroke="#fff" strokeWidth={8} fill="rgba(10,6,30,0.75)" />
        <rect x={98} y={12} width={24} height={20} rx={4} fill="#fff" />
        <line x1={110} y1={120} x2={110 + 70 * Math.sin(ang)} y2={120 - 70 * Math.cos(ang)} stroke={AMARILLO} strokeWidth={8} strokeLinecap="round" />
        <circle cx={110} cy={120} r={10} fill={AMARILLO} />
      </svg>
      <div style={{textAlign: 'center', marginTop: 6, fontFamily: FONT, fontWeight: 800, fontSize: 52, color: AMARILLO, background: 'rgba(10,6,30,0.85)', borderRadius: 40, padding: '4px 18px'}}>
        ▶ {valor.toFixed(2).replace('.', ',')} s
      </div>
    </div>
  );
};

const Avion: React.FC = () => {
  const {lin} = useS();
  const p = lin(FINAL + 0.1, FINAL + 1.4, 0, 1, Easing.in(Easing.quad));
  if (p <= 0 || p >= 1) return null;
  return (
    <svg width={140} height={140} viewBox="0 0 100 100" style={{position: 'absolute', left: 600 + p * 520, top: 1000 - p * 700 - Math.sin(p * Math.PI) * 150, transform: `rotate(-30deg) scale(${1 - p * 0.4})`}}>
      <polygon points="5,50 95,10 60,90 48,58" fill="#fff" />
      <polygon points="48,58 95,10 40,70" fill="#c9d6ff" />
    </svg>
  );
};

export const Escena: React.FC = () => {
  const {s, lin} = useS();
  // A: carita con hipo; la cámara entra a su pecho
  const opA = lin(A_PECHO - 0.55, A_PECHO - 0.1, 1, 0);
  const scA = lin(A_PECHO - 0.65, A_PECHO - 0.1, 1, 4.5, Easing.in(Easing.cubic));
  // B: pecho; entra desde cerca, luego la cámara baja a la garganta y al final se aleja
  const opB = lin(A_PECHO - 0.35, A_PECHO, 0, 1) * lin(FINAL - 0.45, FINAL - 0.1, 1, 0);
  const entra = lin(A_PECHO - 0.35, A_PECHO + 0.5, 1.8, 1, Easing.out(Easing.cubic));
  const sale = lin(FINAL - 0.5, FINAL - 0.1, 1, 0.4, Easing.in(Easing.cubic));
  const sh = sacudida(s, [TIRON, CIERRAN, HIP]);
  // C: vuelve la carita (el final conecta con el inicio)
  const opC = lin(FINAL - 0.3, FINAL + 0.1, 0, 1);
  const scC = lin(FINAL - 0.3, FINAL + 0.5, 0.6, 1, Easing.out(Easing.back(1.4)));
  return (
    <AbsoluteFill>
      <Fondo />
      <AbsoluteFill style={{transform: `translate(${sh.x}px, ${sh.y}px)`}}>
        {opA > 0 && (
          <AbsoluteFill style={{opacity: opA, transform: `scale(${scA})`, transformOrigin: '540px 1180px'}}>
            <Carita saltos={[en('hipo'), 2.0, 2.95]} texto="hip" />
          </AbsoluteFill>
        )}
        {opB > 0 && (
          <AbsoluteFill style={{opacity: opB, transform: `scale(${entra * sale})`}}>
            <Camara paradas={[{t: GARGANTA - 0.25, x: 540, y: 960, zoom: 1}, {t: GARGANTA + 0.6, x: 540, y: VF_Y, zoom: 2.6}]}>
              <Pecho />
            </Camara>
          </AbsoluteFill>
        )}
        {opC > 0 && (
          <AbsoluteFill style={{opacity: opC, transform: `scale(${scC})`}}>
            <Carita saltos={[FINAL + 0.35, en('tiene'), en('hipo', 2) + 0.1]} texto="hip" />
            <Avion />
          </AbsoluteFill>
        )}
        <Cronometro />
        <Impacto texto="¡HIP!" t0={HIP - 0.05} t1={FINAL - 0.3} />
      </AbsoluteFill>
      <Destello t0={CIERRAN} />
      <Rotulo items={[[0, A_PECHO - 0.3, 'tú, con hipo'], [A_PECHO - 0.3, GARGANTA - 0.2, 'dentro de tu pecho'], [GARGANTA - 0.2, FINAL - 0.4, 'garganta · cámara lenta'], [FINAL - 0.4, 999, 'tú, otra vez']]} />
    </AbsoluteFill>
  );
};
