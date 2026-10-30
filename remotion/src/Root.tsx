import React from 'react';
import {AbsoluteFill, Audio, Composition, Sequence, staticFile} from 'remotion';
import {DUR, Subtitulos} from './kit';
import * as E from './Escena';

const FPS = 60;
const VOL_SFX = 0.4; // sfx nivelados por render_remotion.py: siempre por debajo de la voz

// Video completo: escena escrita por Claude + voz + subtítulos encima.
const Video: React.FC = () => {
  const subs = (E as {SUBS?: {arriba?: number; size?: number; acento?: string}}).SUBS || {};
  return (
    <AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
      <E.Escena />
      <Subtitulos {...subs} />
      <Audio src={staticFile('voz.wav')} />
      {((E as {SFX?: {t: number; s: string}[]}).SFX || []).map((x, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(x.t * FPS))} layout="none">
          <Audio src={staticFile('sfx/' + x.s + '.mp3')} volume={VOL_SFX} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => <Composition id="Video" component={Video} durationInFrames={Math.ceil(DUR * FPS)} fps={FPS} width={1080} height={1920} />;
