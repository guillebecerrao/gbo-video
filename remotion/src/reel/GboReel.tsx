import React from "react";
import {
  AbsoluteFill, Easing, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { Mark } from "../Overlays";
import { kicker, theme } from "../theme";
import { RChunk, ReelProps, Side } from "./types";

// Vertical reel 1080x1920 — v2 layout (less cognitive load, clear hierarchy, real margins).
// Grid: 64 px margins. Bands: TOP (thesis / topic) · INFO column on the gaze side · TAG · CAPTIONS.
// Three distinct voices:
//   thesis  = serif italic on paper (the idea)        -> top corner
//   info    = paper cards, numbered rows (the support) -> gaze-side column
//   speech  = dark bubble, light text (what is said)   -> lower third, centered
// Instagram safe zones: top ~220 px, bottom ~380 px, right ~140 px below y=1100.
const M = 64;
const TOP = 236;
const INFO_Y = 640;
const TAG_Y = 1060;
const CAP_Y = 1310;
const COL_W = 500;
const shadow = "0 14px 40px rgba(16,20,24,0.28), 0 2px 6px rgba(16,20,24,0.10)";
const paper: React.CSSProperties = { background: "rgba(250,250,247,0.95)", boxShadow: shadow };
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const useTime = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { t: frame / fps, frame, fps };
};
const useSpringAt = () => {
  const { frame, fps } = useTime();
  return (at: number, cfg: { damping?: number; stiffness?: number; mass?: number } = {}) =>
    spring({ frame: frame - Math.round(at * fps), fps, config: { damping: 18, stiffness: 150, mass: 0.8, ...cfg } });
};
const ramp = (t: number, a: number, b: number, ease = Easing.bezier(0.22, 1, 0.36, 1)) =>
  interpolate(t, [a, b], [0, 1], { ...clamp, easing: ease });
const anchor = (side: Side): React.CSSProperties => (side === "left" ? { left: M } : { right: M });
const sideSeg = (sides: ReelProps["sides"], t: number) =>
  sides.find((s) => t >= s.from && t < s.to) ?? sides[sides.length - 1];

// ---------------------------------------------------------- thesis (hook) ---
// Big, centered, cover-like: white grotesque caps on a dark scrim; the key phrase on an azul block.
const Hook: React.FC<{ h: ReelProps["hook"] }> = ({ h }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t > h.to + 0.6) return null;
  const exit = ramp(t, h.to, h.to + 0.5, Easing.bezier(0.65, 0, 0.35, 1));
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: `rgba(16,20,24,${0.74 * (1 - exit)})` }} />
      <div style={{ position: "absolute", left: M, right: M, top: 600, opacity: 1 - exit,
        transform: `translateY(${-90 * exit}px) scale(${1 - 0.1 * exit})`, transformOrigin: "top left" }}>
        <div style={{ ...kicker(26, "rgba(250,250,247,0.72)"), opacity: ramp(t, h.from, h.from + 0.4) }}>{h.kicker}</div>
        <div style={{ marginTop: 22 }}>
          {h.lines.map((line, li) => {
            const q = sp(h.from + 0.1 + 0.08 * li, { damping: 20, stiffness: 160 });
            return (
              <div key={li} style={{ overflow: "hidden", paddingBottom: 6 }}>
                <div style={{ transform: `translateY(${(1 - q) * 105}%)`, fontFamily: theme.sans, fontWeight: 800,
                  fontSize: 112, lineHeight: 0.98, letterSpacing: -3, color: theme.paper, textTransform: "uppercase",
                  whiteSpace: "nowrap" }}>
                  {line.map((s, si) => s.emph
                    ? <span key={si} style={{ background: theme.azul, borderRadius: 10, padding: "0 14px",
                        margin: "0 -6px" }}>{s.text}</span>
                    : <span key={si}>{s.text}</span>)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------- topic pill (persistent) --
const Topic: React.FC<{ p: NonNullable<ReelProps["topic"]>; sides: ReelProps["sides"] }> = ({ p, sides }) => {
  const { t } = useTime();
  if (t < p.from || t > p.to) return null;
  const seg = sideSeg(sides, t);
  const since = Math.max(t - Math.max(seg.from, p.from), 0);
  const a = ramp(since, 0, 0.4) * (1 - ramp(t, p.to - 0.3, p.to));
  return (
    <div style={{ position: "absolute", top: TOP, ...anchor(seg.side), opacity: a,
      transform: `translateY(${(1 - a) * -12}px)`, display: "flex", alignItems: "center", gap: 12,
      ...paper, borderRadius: 999, padding: "10px 24px 10px 10px" }}>
      <div style={{ background: theme.azul, borderRadius: 999, width: 38, height: 38, display: "flex",
        alignItems: "center", justifyContent: "center" }}><Mark size={18} color={theme.paper} slash={theme.paper} /></div>
      <div style={{ ...kicker(19, theme.ink), letterSpacing: "0.16em" }}>{p.text}</div>
    </div>
  );
};

// ---------------------------------------------------------------- info card -
const Panel: React.FC<{ p: ReelProps["panels"][number] }> = ({ p }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t < p.from || t > p.to) return null;
  const enter = sp(p.from, { damping: 17 });
  const out = 1 - ramp(t, p.to - 0.35, p.to, Easing.in(Easing.cubic));
  const dir = p.side === "left" ? -1 : 1;
  const shown = p.chips.filter((c) => t >= c.at - 0.05);
  return (
    <div style={{ position: "absolute", top: INFO_Y, ...anchor(p.side), width: COL_W,
      opacity: Math.min(enter * 1.4, 1) * out, transform: `translateX(${(1 - enter) * 50 * dir}px)` }}>
      <div style={{ ...paper, borderRadius: 22, padding: "22px 28px 26px" }}>
        <div style={kicker(18, theme.azul)}>{p.kicker}</div>
        <div style={{ height: 2, background: theme.azul, marginTop: 12, marginBottom: 4, opacity: 0.8,
          transform: `scaleX(${ramp(t, p.from + 0.1, p.from + 0.6)})`, transformOrigin: "left" }} />
        {shown.map((c, i) => {
          const q = sp(c.at, { damping: 15, stiffness: 190 });
          const n = p.chips.slice(0, i + 1).filter((x) => !x.struck).length;
          const strike = c.struck ? ramp(t, c.at + 0.35, c.at + 0.8) : 0;
          return (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 16, marginTop: 18,
              transform: `translateY(${(1 - q) * 20}px)`, opacity: Math.min(q * 1.6, 1) }}>
              <div style={{ flex: "0 0 auto", width: 34, height: 34, borderRadius: 17,
                background: c.struck ? "transparent" : theme.azul, border: c.struck ? `2px solid ${theme.inkMuted}` : "none",
                boxSizing: "border-box", color: c.struck ? theme.inkMuted : theme.paper, fontFamily: theme.sans,
                fontWeight: 800, fontSize: 18, display: "flex", alignItems: "center", justifyContent: "center",
                marginTop: 6, transform: `scale(${q})` }}>{c.struck ? "✓" : n}</div>
              <div>
                <div style={{ position: "relative", display: "inline-block", fontFamily: theme.sans, fontWeight: 800,
                  fontSize: 34, lineHeight: 1.1, color: c.struck ? theme.inkMuted : theme.ink, letterSpacing: -0.6 }}>
                  {c.label}
                  {c.struck && <div style={{ position: "absolute", left: -4, right: -4, top: "54%", height: 4,
                    borderRadius: 2, background: theme.azul, transform: `scaleX(${strike})`, transformOrigin: "left" }} />}
                </div>
                {c.sub && <div style={{ fontFamily: theme.sans, fontWeight: 500, fontSize: 24, lineHeight: 1.25,
                  color: theme.inkMuted, marginTop: 4 }}>{c.sub}</div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- name tag --
const NameTag: React.FC<ReelProps["tags"][number]> = ({ name, title, from, to, side }) => {
  const { t } = useTime();
  if (t < from || t > to) return null;
  const bar = ramp(t, from, from + 0.35);
  const nameIn = ramp(t, from + 0.12, from + 0.55);
  const titleIn = ramp(t, from + 0.35, from + 0.8);
  const out = 1 - ramp(t, to - 0.35, to, Easing.in(Easing.cubic));
  const right = side === "right";
  return (
    <div style={{ position: "absolute", top: TAG_Y, ...anchor(side), opacity: out, display: "flex", gap: 14,
      flexDirection: right ? "row-reverse" : "row" }}>
      <div style={{ width: 6, borderRadius: 3, background: theme.azul, transform: `scaleY(${bar})`,
        transformOrigin: "bottom" }} />
      <div style={{ display: "flex", flexDirection: "column", alignItems: right ? "flex-end" : "flex-start" }}>
        <div style={{ clipPath: `inset(0 ${(1 - nameIn) * 100}% 0 0)`, ...paper,
          borderRadius: 12, padding: "8px 18px", fontFamily: theme.sans, fontWeight: 800, fontSize: 36,
          color: theme.ink, letterSpacing: -0.6 }}>{name}</div>
        <div style={{ marginTop: 8, clipPath: `inset(0 ${(1 - titleIn) * 100}% 0 0)`,
          background: theme.azul, borderRadius: 10, padding: "6px 14px", fontFamily: theme.sans, fontWeight: 600,
          fontSize: 24, color: theme.paper }}>{title}</div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- captions --
const Captions: React.FC<{ chunks: RChunk[]; hideFrom: number }> = ({ chunks, hideFrom }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t >= hideFrom) return null;
  const c = chunks.find((k) => t >= k.start && t < k.end);
  if (!c) return null;
  const q = sp(c.start, { damping: 16, stiffness: 280, mass: 0.6 });
  return (
    <div style={{ position: "absolute", left: 130, width: 820, top: CAP_Y, display: "flex", justifyContent: "center",
      transform: `translateY(calc(-50% + ${(1 - q) * 10}px))`, opacity: Math.min(q * 2, 1) }}>
      <div style={{ background: "rgba(16,20,24,0.88)", borderRadius: 20, padding: "14px 28px 18px",
        textAlign: "center", fontFamily: theme.sans, fontWeight: 800, fontSize: 58, lineHeight: 1.18,
        letterSpacing: -0.8, color: theme.paper, boxShadow: "0 10px 30px rgba(16,20,24,0.35)" }}>
        {c.words.map((w, i) => {
          const said = t >= w.start - 0.03;
          return (
            <React.Fragment key={i}>
              <span style={{ opacity: said ? 1 : 0.42, ...(w.emph ? { background: theme.azul, borderRadius: 8,
                padding: "0 10px", margin: "0 -4px" } : {}) }}>{w.text}</span>
              {i < c.words.length - 1 ? " " : ""}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- end card --
const Cursor: React.FC = () => (
  <svg width="56" height="56" viewBox="0 0 24 24" style={{ filter: "drop-shadow(0 4px 8px rgba(16,20,24,0.35))" }}>
    <path d="M5 3l14 8.2-6.1 1.4 3.6 6.6-2.7 1.4-3.5-6.6L5 18.6z" fill={theme.ink} stroke={theme.paper}
      strokeWidth="1.4" strokeLinejoin="round" />
  </svg>
);
const Globe: React.FC<{ color: string }> = ({ color }) => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8">
    <circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c3 3.2 3 14.8 0 18M12 3c-3 3.2-3 14.8 0 18" />
  </svg>
);

export const EndCard: React.FC<{ e: ReelProps["end"] }> = ({ e }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t < e.from) return null;
  const wipe = ramp(t, e.from, e.from + 0.5, Easing.bezier(0.65, 0, 0.35, 1));
  const pop = sp(e.from + 0.6, { damping: 13, stiffness: 160 });
  const calm = ramp(t, e.typeAt - 0.45, e.typeAt - 0.05, Easing.bezier(0.65, 0, 0.35, 1)); // CTA hands the accent to the URL
  const field = sp(e.typeAt - 0.3, { damping: 18 });
  const typed = Math.max(0, Math.min(e.url.length, Math.floor((t - e.typeAt) / e.charDur) + 1));
  const typing = t >= e.typeAt && typed < e.url.length;
  const caretOn = t < e.clickAt && (typing || Math.floor(t * 2.4) % 2 === 0);
  const curIn = ramp(t, e.clickAt - 0.55, e.clickAt - 0.05, Easing.bezier(0.33, 1, 0.68, 1));
  const press = t >= e.clickAt ? 1 - ramp(t, e.clickAt, e.clickAt + 0.18) : 0;
  const lit = t >= e.clickAt;
  const words = e.title.split(" ");
  return (
    <AbsoluteFill style={{ background: theme.paper, clipPath: `inset(${(1 - wipe) * 100}% 0 0 0)` }}>
      <div style={{ position: "absolute", top: 500, left: 90, right: 90, display: "flex", flexDirection: "column",
        alignItems: "center" }}>
        <div style={{ opacity: ramp(t, e.from + 0.25, e.from + 0.6) }}><Mark size={44} /></div>
        <div style={{ marginTop: 40, textAlign: "center", display: "flex", flexWrap: "wrap", justifyContent: "center",
          columnGap: 16 }}>
          {words.map((w, i) => {
            const s = sp(e.from + 0.3 + i * 0.05, { damping: 20 });
            return (
              <span key={i} style={{ overflow: "hidden", display: "inline-block", paddingBottom: 6 }}>
                <span style={{ display: "inline-block", transform: `translateY(${(1 - s) * 100}%)`,
                  fontFamily: theme.serif, fontStyle: "italic", fontSize: 66, lineHeight: 1.1, color: theme.ink,
                  letterSpacing: -1 }}>{w}</span>
              </span>
            );
          })}
        </div>
        {/* CTA: loud first, then calm (the accent moves to the URL) */}
        <div style={{ marginTop: 56 - 16 * calm, background: `rgba(224,140,74,${1 - calm})`, color: theme.ink,
          fontFamily: theme.sans, fontWeight: 800, fontSize: 64 - 14 * calm, borderRadius: 30,
          padding: `${22 - 14 * calm}px ${52 - 40 * calm}px`, transform: `scale(${0.6 + 0.4 * pop})`,
          opacity: Math.min(pop * 2, 1), boxShadow: `0 18px 50px rgba(224,140,74,${0.28 * (1 - calm)})` }}>{e.cta}</div>
        {/* URL field: typed, then clicked */}
        <div style={{ position: "relative", marginTop: 34, opacity: Math.min(field * 1.5, 1),
          transform: `translateY(${(1 - field) * 30}px) scale(${1 - 0.03 * press})` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 18, width: 760, height: 124, boxSizing: "border-box",
            padding: "0 16px 0 30px", borderRadius: 62, background: theme.paper,
            border: `4px solid ${lit ? theme.naranjo : theme.ink}`,
            boxShadow: lit ? "0 16px 44px rgba(224,140,74,0.35)" : "0 16px 44px rgba(16,20,24,0.16)" }}>
            <Globe color={theme.inkMuted} />
            <div style={{ flex: 1, fontFamily: theme.mono, fontWeight: 500, fontSize: 54, color: theme.ink,
              letterSpacing: "-0.01em", whiteSpace: "nowrap" }}>
              {t >= e.typeAt ? e.url.slice(0, typed) : ""}
              <span style={{ display: "inline-block", width: 4, height: 56, marginLeft: 4, verticalAlign: "-8px",
                background: theme.azul, opacity: caretOn ? 1 : 0 }} />
            </div>
            <div style={{ width: 92, height: 92, borderRadius: 46, display: "flex", alignItems: "center",
              justifyContent: "center", background: lit ? theme.naranjo : theme.ink,
              transform: `scale(${1 - 0.12 * press})` }}>
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={lit ? theme.ink : theme.paper}
                strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </div>
          </div>
          {lit && <div style={{ position: "absolute", right: 2, top: 2, width: 120, height: 120, borderRadius: 60,
            border: `3px solid ${theme.naranjo}`, transform: `scale(${0.6 + ramp(t, e.clickAt, e.clickAt + 0.5)})`,
            opacity: 1 - ramp(t, e.clickAt, e.clickAt + 0.5) }} />}
          <div style={{ position: "absolute", right: 22 - 260 * (1 - curIn), top: 66 + 300 * (1 - curIn),
            opacity: curIn, transform: `scale(${1 - 0.15 * press})` }}><Cursor /></div>
        </div>
        {e.foot && <div style={{ marginTop: 64, ...kicker(22, theme.inkMuted), textAlign: "center",
          opacity: ramp(t, e.clickAt + 0.2, e.clickAt + 0.7) }}>{e.foot}</div>}
      </div>
    </AbsoluteFill>
  );
};

export const GboReel: React.FC<ReelProps> = (props) => {
  return (
    <AbsoluteFill style={{ backgroundColor: theme.ink }}>
      <OffthreadVideo src={staticFile(props.video)} muted style={{ width: 1080, height: 1920 }} />
      {props.topic && <Topic p={props.topic} sides={props.sides} />}
      {props.panels.map((p, i) => <Panel key={i} p={p} />)}
      {props.tags.map((g, i) => <NameTag key={i} {...g} />)}
      <Hook h={props.hook} />
      <Captions chunks={props.captions} hideFrom={props.end.from + 0.3} />
      <EndCard e={props.end} />
    </AbsoluteFill>
  );
};
