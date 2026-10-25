import React from 'react';
import {AbsoluteFill, Audio, Composition, staticFile} from 'remotion';
import {DUR, Subtitulos} from './kit';
import * as E from './Escena';

const FPS = 60;

// Video completo: escena escrita por Claude + voz + subtítulos encima.
const Video: React.FC = () => {
  const subs = (E as {SUBS?: {arriba?: number; size?: number; acento?: string}}).SUBS || {};
  return (
    <AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
      <E.Escena />
      <Subtitulos {...subs} />
      <Audio src={staticFile('voz.wav')} />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => <Composition id="Video" component={Video} durationInFrames={Math.ceil(DUR * FPS)} fps={FPS} width={1080} height={1920} />;
