import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Mark } from "../Overlays";
import { kicker, theme } from "../theme";

// Reel cover 1080x1920. Everything that matters sits inside the 4:5 grid crop (y 285..1635).
export type CoverProps = {
  left: { img: string; name: string };
  right: { img: string; name: string };
  kicker: string;
  title: string;            // rendered uppercase
  foot: string;
};

const Portrait: React.FC<{ img: string; name: string }> = ({ img, name }) => (
  <div style={{ position: "relative", width: 518, height: 712, overflow: "hidden", borderRadius: 18 }}>
    <Img src={staticFile(img)} style={{ position: "absolute", width: 600, height: 1067, left: -41, top: -60,
      objectFit: "cover" }} />
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 200,
      background: "linear-gradient(to top, rgba(16,20,24,0.85), rgba(16,20,24,0))" }} />
    <div style={{ position: "absolute", left: 24, bottom: 22, ...kicker(20, theme.paper), letterSpacing: "0.14em" }}>
      {name}</div>
  </div>
);

export const GboCover: React.FC<CoverProps> = (p) => (
  <AbsoluteFill style={{ background: theme.ink }}>
    <div style={{ position: "absolute", top: 300, left: 16, right: 16, display: "flex", gap: 12 }}>
      <Portrait {...p.left} />
      <Portrait {...p.right} />
    </div>
    <div style={{ position: "absolute", top: 1050, left: 64, right: 64 }}>
      <div style={{ ...kicker(24, "rgba(250,250,247,0.6)") }}>{p.kicker}</div>
      <div style={{ marginTop: 22, fontFamily: theme.sans, fontWeight: 800, fontSize: 112, lineHeight: 0.94,
        letterSpacing: -3, color: theme.paper, textTransform: "uppercase" }}>
        {p.title.split(/(\*[^*]+\*)/).map((s, i) => s.startsWith("*")
          ? <span key={i} style={{ background: theme.azul, padding: "0 14px", margin: "0 -6px", borderRadius: 10,
              boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>{s.slice(1, -1)}</span>
          : <span key={i}>{s}</span>)}
      </div>
      <div style={{ marginTop: 36, display: "flex", alignItems: "center", gap: 22 }}>
        <Mark size={50} color={theme.paper} />
        <div style={{ fontFamily: theme.sans, fontWeight: 700, fontSize: 42, color: "rgba(250,250,247,0.85)",
          letterSpacing: -0.5 }}>
          {p.foot}</div>
      </div>
    </div>
  </AbsoluteFill>
);
