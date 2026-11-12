import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Mark } from "../Overlays";
import { kicker, theme } from "../theme";

// Reel cover 1080x1920, one component with four layouts. Everything that matters sits inside the 4:5 grid crop
// (y 285..1635). Title: rendered uppercase; *text* = azul block.
//   duo    two portrait boxes side by side + text below          (left + right)
//   single one full-width portrait box + text below              (left, optional singleImg)
//   frame  a frame of the video itself, full bleed + gradient    (img, optional imgY) — a real frame often beats
//          a designed cover
//   split  two frames 50/50 with a vertical cut, full bleed      (left + right with x/y)
// When `layout` is omitted: img → frame; right.img → duo; otherwise single.
export type CoverLayout = "duo" | "single" | "frame" | "split";
type Side = { img: string; name?: string; x?: number; y?: number };
export type CoverProps = {
  layout?: CoverLayout;
  left?: Side;
  right?: Side;
  img?: string;                                               // frame
  imgY?: number;                                              // frame: vertical shift of the frame (px)
  singleImg?: { width?: number; top?: number; left?: number }; // single: how the frame sits in the 1048x712 box
  kicker: string;
  title: string;
  foot: string;
};
// Kept for props files written before the merge (2026-11-12).
export type CoverSoloProps = CoverProps;
export type CoverSplitProps = CoverProps;

export const coverLayout = (p: CoverProps): CoverLayout =>
  p.layout ?? (p.img ? "frame" : p.right?.img ? "duo" : "single");

const Title: React.FC<{ title: string; size: number; lineHeight: number }> = ({ title, size, lineHeight }) => (
  <div style={{ marginTop: 22, fontFamily: theme.sans, fontWeight: 800, fontSize: size, lineHeight,
    letterSpacing: -3, color: theme.paper, textTransform: "uppercase" }}>
    {title.split(/(\*[^*]+\*)/).map((s, i) => s.startsWith("*")
      ? <span key={i} style={{ background: theme.azul, padding: "0 14px", margin: "0 -6px", borderRadius: 10,
          boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>{s.slice(1, -1)}</span>
      : <span key={i}>{s}</span>)}
  </div>
);

const Portrait: React.FC<{ img: string; name?: string; width?: number;
  imgBox?: { width: number; top: number; left: number } }> = ({ img, name, width = 518,
  imgBox = { width: 600, top: -60, left: -41 } }) => (
  <div style={{ position: "relative", width, height: 712, overflow: "hidden", borderRadius: 18 }}>
    <Img src={staticFile(img)} style={{ position: "absolute", width: imgBox.width, height: imgBox.width * 16 / 9,
      left: imgBox.left, top: imgBox.top, objectFit: "cover" }} />
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 200,
      background: "linear-gradient(to top, rgba(16,20,24,0.85), rgba(16,20,24,0))" }} />
    {name ? <div style={{ position: "absolute", left: 24, bottom: 22, ...kicker(20, theme.paper),
      letterSpacing: "0.14em" }}>{name}</div> : null}
  </div>
);

const Half: React.FC<Side & { side: "left" | "right" }> = ({ img, x, y, side }) => (
  <div style={{ position: "absolute", top: 0, bottom: 0, width: 540, left: side === "left" ? 0 : 540,
    overflow: "hidden" }}>
    <Img src={staticFile(img)} style={{ position: "absolute", width: 1080, height: 1920,
      left: -(x ?? (side === "left" ? 0 : 540)), top: y ?? 0, objectFit: "cover" }} />
  </div>
);

// Text block for the boxed layouts (duo, single)
const BoxedText: React.FC<CoverProps> = (p) => (
  <div style={{ position: "absolute", top: 1050, left: 64, right: 64 }}>
    <div style={{ ...kicker(24, "rgba(250,250,247,0.6)") }}>{p.kicker}</div>
    <Title title={p.title} size={112} lineHeight={0.94} />
    <div style={{ marginTop: 36, display: "flex", alignItems: "center", gap: 22 }}>
      <Mark size={50} color={theme.paper} />
      <div style={{ fontFamily: theme.sans, fontWeight: 700, fontSize: 42, color: "rgba(250,250,247,0.85)",
        letterSpacing: -0.5 }}>{p.foot}</div>
    </div>
  </div>
);

// Gradient + text block for the full-bleed layouts (frame, split)
const BleedText: React.FC<CoverProps> = (p) => (<>
  <div style={{ position: "absolute", left: 0, right: 0, top: 860, bottom: 0,
    background: "linear-gradient(to bottom, rgba(16,20,24,0) 0%, rgba(16,20,24,0.78) 38%, rgba(16,20,24,0.92) 100%)" }} />
  <div style={{ position: "absolute", top: 1170, left: 64, right: 64 }}>
    <div style={{ ...kicker(26, "rgba(250,250,247,0.72)") }}>{p.kicker}</div>
    <Title title={p.title} size={118} lineHeight={0.96} />
    <div style={{ marginTop: 34, display: "flex", alignItems: "center", gap: 22 }}>
      <Mark size={46} color={theme.paper} />
      <div style={{ fontFamily: theme.mono, fontWeight: 500, fontSize: 40, color: "rgba(250,250,247,0.88)" }}>
        {p.foot}</div>
    </div>
  </div>
</>);

export const GboCover: React.FC<CoverProps> = (p) => {
  const layout = coverLayout(p);
  if (layout === "frame") return (
    <AbsoluteFill style={{ background: theme.ink }}>
      <Img src={staticFile(p.img ?? p.left?.img ?? "")} style={{ position: "absolute", width: 1080, height: 1920,
        left: 0, top: p.imgY ?? 0, objectFit: "cover" }} />
      <BleedText {...p} />
    </AbsoluteFill>
  );
  if (layout === "split") return (
    <AbsoluteFill style={{ background: theme.ink }}>
      <Half {...p.left!} side="left" />
      <Half {...p.right!} side="right" />
      <div style={{ position: "absolute", top: 0, bottom: 0, left: 537, width: 6, background: theme.paper }} />
      <BleedText {...p} />
    </AbsoluteFill>
  );
  return (
    <AbsoluteFill style={{ background: theme.ink }}>
      <div style={{ position: "absolute", top: 300, left: 16, right: 16, display: "flex", gap: 12 }}>
        {layout === "duo" ? (<>
          <Portrait {...p.left!} />
          <Portrait {...p.right!} />
        </>) : (
          <Portrait {...p.left!} width={1048} imgBox={{ width: p.singleImg?.width ?? 1048,
            top: p.singleImg?.top ?? -380, left: p.singleImg?.left ?? 0 }} />
        )}
      </div>
      <BoxedText {...p} />
    </AbsoluteFill>
  );
};

// Back-compat aliases for compositions registered before the merge
export const GboCoverSolo: React.FC<CoverProps> = (p) => <GboCover layout="frame" {...p} />;
export const GboCoverSplit: React.FC<CoverProps> = (p) => <GboCover layout="split" {...p} />;
