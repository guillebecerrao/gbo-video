import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Captions } from "../Captions";
import { Chunk } from "../types";
import { easeInOut, easeOut, kicker, theme } from "../theme";

// Montage reel (music-led, often with an object as protagonist). Props come from scripts/reel_render.py.
// Over a cut already made: captions (paper style, same as GboVertical / pilot), spec cards
// (kicker Archivo 600 + Newsreader italic title on a paper card), eased punch-zooms and
// short white flashes on hits. Effects are props, so each one has a reason in the EDL.
export type SpecCard = { from: number; to: number; kicker: string; title: string; side?: "left" | "right" };
export type Zoom = { from: number; to: number; s0: number; s1: number; ox?: number; oy?: number };
export type Flash = { at: number; dur?: number; peak?: number };
export type MontageProps = {
  video: string;
  durationSec: number;
  fps?: number;            // output fps (reel_render.py passes the EDL fps)
  captions: Chunk[];
  cards: SpecCard[];
  zooms: Zoom[];
  flashes: Flash[];
  captionY?: number;
  captionStyle?: "paper" | "dark";
};

const Card: React.FC<{ c: SpecCard; t: number }> = ({ c, t }) => {
  if (t < c.from || t > c.to) return null;
  const pin = easeOut((t - c.from) / 0.18);
  const pout = easeOut((c.to - t) / 0.15);
  const p = Math.min(pin, pout);
  const right = c.side === "right";
  return (
    <div style={{
      position: "absolute", top: 250, [right ? "right" : "left"]: 70, opacity: p,
      transform: `translateX(${(right ? 1 : -1) * (1 - p) * 40}px)`,
    }}>
      <div style={{
        background: theme.paperSoft, borderRadius: 22, padding: "26px 40px 30px",
        boxShadow: "0 12px 34px rgba(16,20,24,0.30)", borderLeft: right ? undefined : `8px solid ${theme.azul}`,
        borderRight: right ? `8px solid ${theme.azul}` : undefined, textAlign: right ? "right" : "left",
      }}>
        <div style={kicker(30, theme.inkMuted)}>{c.kicker}</div>
        <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 84, lineHeight: 1.02,
          color: theme.ink, marginTop: 8 }}>{c.title}</div>
      </div>
    </div>
  );
};

export const GboMontage: React.FC<MontageProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const z = props.zooms.find((k) => t >= k.from && t < k.to);
  const scale = z ? z.s0 + (z.s1 - z.s0) * easeInOut((t - z.from) / (z.to - z.from)) : 1;
  const origin = z ? `${(z.ox ?? 0.5) * 100}% ${(z.oy ?? 0.5) * 100}%` : "50% 50%";

  let flash = 0;
  for (const f of props.flashes) {
    const d = f.dur ?? 0.16;
    if (t >= f.at && t < f.at + d) flash = Math.max(flash, (f.peak ?? 0.7) * (1 - (t - f.at) / d));
  }

  return (
    <AbsoluteFill style={{ backgroundColor: theme.ink }}>
      <AbsoluteFill style={{ transform: `scale(${scale})`, transformOrigin: origin }}>
        <OffthreadVideo src={staticFile(props.video)} style={{ width: 1080, height: 1920 }} />
      </AbsoluteFill>
      {flash > 0 && <AbsoluteFill style={{ backgroundColor: theme.paper, opacity: flash }} />}
      {props.cards.map((c, i) => <Card key={i} c={c} t={t} />)}
      <Captions chunks={props.captions} yCenter={props.captionY ?? 1340} variant={props.captionStyle ?? "dark"} />
    </AbsoluteFill>
  );
};
