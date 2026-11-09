import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Mark } from "../Overlays";
import { kicker, theme } from "../theme";

// YouTube thumbnail 1280x720. Text column left, two portraits right.
// Bottom-right corner (~170x60) is covered by YouTube's duration badge: keep it free of meaning.
export type ThumbPortrait = { img: string; name: string; x: number; y: number; scale?: number };
export type ThumbProps = {
  left: ThumbPortrait;
  right: ThumbPortrait;
  kicker: string;
  title: string;           // uppercase; *text* = azul highlight
  titleSize?: number;
  foot: string;
};

const PW = 268, PH = 664;

const Portrait: React.FC<ThumbPortrait> = ({ img, name, x, y, scale = 1 }) => (
  <div style={{ position: "relative", width: PW, height: PH, overflow: "hidden", borderRadius: 16 }}>
    <Img src={staticFile(img)} style={{ position: "absolute", width: 600 * scale, height: 1067 * scale,
      left: -x, top: -y }} />
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 150,
      background: "linear-gradient(to top, rgba(16,20,24,0.85), rgba(16,20,24,0))" }} />
    <div style={{ position: "absolute", left: 18, right: 12, bottom: 18, ...kicker(15, theme.paper),
      letterSpacing: "0.12em", lineHeight: 1.3 }}>{name}</div>
  </div>
);

export const GboThumb: React.FC<ThumbProps> = (p) => (
  <AbsoluteFill style={{ background: theme.ink }}>
    <div style={{ position: "absolute", top: 28, right: 28, display: "flex", gap: 10 }}>
      <Portrait {...p.left} />
      <Portrait {...p.right} />
    </div>
    <div style={{ position: "absolute", top: 0, bottom: 0, left: 56, width: 640, display: "flex",
      flexDirection: "column", justifyContent: "center" }}>
      <div style={{ ...kicker(22, "rgba(250,250,247,0.6)") }}>{p.kicker}</div>
      <div style={{ marginTop: 18, fontFamily: theme.sans, fontWeight: 800, fontSize: p.titleSize ?? 104,
        lineHeight: 0.95, letterSpacing: -3, color: theme.paper, textTransform: "uppercase" }}>
        {p.title.split(/(\*[^*]+\*)/).map((s, i) => s.startsWith("*")
          ? <span key={i} style={{ background: theme.azul, padding: "0 12px", margin: "0 -4px", borderRadius: 10,
              boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>{s.slice(1, -1)}</span>
          : <span key={i}>{s}</span>)}
      </div>
      <div style={{ marginTop: 30, display: "flex", alignItems: "center", gap: 16 }}>
        <Mark size={40} color={theme.paper} />
        <div style={{ fontFamily: theme.sans, fontWeight: 700, fontSize: 32, color: "rgba(250,250,247,0.85)",
          letterSpacing: -0.5 }}>{p.foot}</div>
      </div>
    </div>
  </AbsoluteFill>
);
