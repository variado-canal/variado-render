// La cámara entra a un objeto: se acerca al punto (x,y) y por ahí se abre lo que hay dentro.
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

export const Entrar: React.FC<{t: number; x: number; y: number; dur?: number; zoom?: number; fuera: React.ReactNode; dentro: React.ReactNode}> = ({t, x, y, dur = 1.1, zoom = 16, fuera, dentro}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const k = Math.max(0, Math.min(1, (frame / fps - t) / dur));
  if (k >= 1) return <>{dentro}</>;
  const e = k * k * (3 - 2 * k);
  const z = Math.pow(zoom, e);
  const a = Math.max(0, (e - 0.5) / 0.5);
  const id = 'entrar' + Math.round(t * 1000);
  const dz = 0.55 + 0.45 * e;
  return (
    <g>
      <g transform={`translate(${x} ${y}) scale(${z}) translate(${-x} ${-y})`}>{fuera}</g>
      {a > 0 && (
        <g>
          <defs><clipPath id={id}><circle cx={x} cy={y} r={a * a * 2300} /></clipPath></defs>
          <g clipPath={`url(#${id})`}><g transform={`translate(${x} ${y}) scale(${dz}) translate(${-x} ${-y})`}>{dentro}</g></g>
        </g>
      )}
    </g>
  );
};
