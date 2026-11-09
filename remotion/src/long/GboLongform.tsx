import React from "react";
import {
  AbsoluteFill, Easing, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import { Mark } from "../Overlays";
import { kicker, theme } from "../theme";
import { Band, Beat, Book, Card, Chapter, LChunk, LongProps, Quote, Stat } from "./types";

// Long form 16:9 — v2 motion system (feedback: "more standard editing language").
// Paper & ink surfaces, azul = structure/emphasis, naranjo ONLY for the CTA.
// Motion: springs for entrances, masked wipes for text, stagger per word/item,
// chapter separator collapses into the persistent chapter pill (one gesture, always in sync).

const SIDE_X = 76;
const shadow = "0 18px 50px rgba(16,20,24,0.28), 0 2px 8px rgba(16,20,24,0.12)";
const glass: React.CSSProperties = {
  background: "rgba(250,250,247,0.84)", backdropFilter: "blur(18px) saturate(1.2)",
  WebkitBackdropFilter: "blur(18px) saturate(1.2)", boxShadow: shadow,
};
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const useTime = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { t: frame / fps, frame, fps };
};
// spring that starts at time `at` (seconds)
const useSpringAt = () => {
  const { frame, fps } = useTime();
  return (at: number, cfg: { damping?: number; stiffness?: number; mass?: number } = {}) =>
    spring({ frame: frame - Math.round(at * fps), fps, config: { damping: 18, stiffness: 140, mass: 0.9, ...cfg } });
};
const ramp = (t: number, a: number, b: number, ease = Easing.bezier(0.22, 1, 0.36, 1)) =>
  interpolate(t, [a, b], [0, 1], { ...clamp, easing: ease });
// 0→1 in, 1→0 out
const inOut = (t: number, from: number, to: number, din = 0.45, dout = 0.35) =>
  Math.min(ramp(t, from, from + din), 1 - ramp(t, to - dout, to, Easing.in(Easing.cubic)));

// ------------------------------------------------------------ chapter pill --
const Pill: React.FC<{ n: number; total: number; title: string; style?: React.CSSProperties }> = (
  { n, total, title, style },
) => (
  <div style={{ display: "flex", alignItems: "center", gap: 14, ...glass, borderRadius: 999,
    padding: "9px 22px 9px 10px", transformOrigin: "left center", ...style }}>
    <div style={{ fontFamily: theme.sans, fontWeight: 800, fontSize: 19, color: theme.paper,
      background: theme.azul, borderRadius: 999, width: 36, height: 36, display: "flex",
      alignItems: "center", justifyContent: "center" }}>{n}</div>
    <div>
      <div style={{ ...kicker(16, theme.ink), letterSpacing: "0.16em", whiteSpace: "nowrap" }}>{title}</div>
      <div style={{ display: "flex", gap: 3, marginTop: 6 }}>
        {Array.from({ length: total }, (_, i) => (
          <div key={i} style={{ width: 14, height: 3, borderRadius: 2,
            background: i + 1 < n ? "rgba(16,20,24,0.35)" : i + 1 === n ? theme.azul : "rgba(16,20,24,0.12)" }} />
        ))}
      </div>
    </div>
  </div>
);

const ChapterPill: React.FC<{ chapters: Chapter[]; hidden: boolean }> = ({ chapters, hidden }) => {
  const { t } = useTime();
  const ch = chapters.find((c) => t >= c.start && t < c.end);
  if (!ch || hidden) return null;
  const out = 1 - ramp(t, ch.end - 0.25, ch.end);
  return <div style={{ position: "absolute", left: 48, top: 40, opacity: out }}>
    <Pill n={ch.n} total={chapters.length} title={ch.title} /></div>;
};

// ---------------------------------------------------------- chapter separator --
const ChapterCard: React.FC<{ card: Extract<Card, { kind: "chapter" }>; total: number; pillTitle: string }> = (
  { card, total, pillTitle },
) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t < card.from || t > card.to) return null;
  const OUT = 0.55;
  const wipeIn = ramp(t, card.from, card.from + 0.42, Easing.bezier(0.65, 0, 0.35, 1));
  const wipeOut = ramp(t, card.to - OUT, card.to - 0.05, Easing.bezier(0.65, 0, 0.35, 1));
  const num = sp(card.from + 0.12);
  const words = card.title.split(" ");
  const morph = sp(card.to - OUT, { damping: 20, stiffness: 120 });
  // title block position -> pill position (top-left)
  const px = interpolate(morph, [0, 1], [700, 48]);
  const py = interpolate(morph, [0, 1], [600, 40]);
  const ps = interpolate(morph, [0, 1], [1.9, 1]);
  return (
    <>
      <AbsoluteFill style={{ clipPath: `inset(0 ${(1 - wipeIn) * 100}% 0 ${wipeOut * 100}%)`,
        background: theme.paper }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 14, background: theme.azul }} />
        <div style={{ position: "absolute", left: 230, top: 0, bottom: 0, display: "flex",
          alignItems: "center", gap: 56, opacity: 1 - ramp(t, card.to - OUT, card.to - OUT + 0.2) }}>
          <div style={{ overflow: "hidden", height: 250 }}>
            <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 250, lineHeight: 1,
              color: theme.azul, transform: `translateY(${(1 - num) * 250}px)` }}>
              {String(card.n).padStart(2, "0")}</div>
          </div>
          <div>
            <div style={{ ...kicker(24, theme.inkMuted), opacity: ramp(t, card.from + 0.2, card.from + 0.5),
              letterSpacing: `${0.4 - 0.16 * ramp(t, card.from + 0.2, card.from + 0.7)}em` }}>
              Capítulo {card.n} de {total}</div>
            <div style={{ display: "flex", flexWrap: "wrap", maxWidth: 1180, marginTop: 14, columnGap: 20 }}>
              {words.map((w, i) => {
                const q = sp(card.from + 0.28 + i * 0.05);
                return (
                  <div key={i} style={{ overflow: "hidden", paddingBottom: 8 }}>
                    <div style={{ fontFamily: theme.serif, fontSize: 82, color: theme.ink, letterSpacing: -1.2,
                      lineHeight: 1.05, transform: `translateY(${(1 - q) * 100}%)` }}>{w}</div>
                  </div>
                );
              })}
            </div>
            <div style={{ height: 4, background: theme.azul, marginTop: 18, borderRadius: 2,
              width: 240 * ramp(t, card.from + 0.45, card.from + 1.0) }} />
          </div>
        </div>
      </AbsoluteFill>
      {t >= card.to - OUT && (
        <div style={{ position: "absolute", left: px, top: py, transform: `scale(${ps})`,
          transformOrigin: "left top", opacity: ramp(t, card.to - OUT, card.to - OUT + 0.12) }}>
          <Pill n={card.n} total={total} title={pillTitle} />
        </div>
      )}
    </>
  );
};

// --------------------------------------------------------- title / outro ----
const TitleCard: React.FC<{ card: Extract<Card, { kind: "title" }> }> = ({ card }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t < card.from || t > card.to) return null;
  const a = inOut(t, card.from, card.to, 0.3, 0.45);
  const words = card.title.split(" ");
  return (
    <AbsoluteFill style={{ background: theme.ink, opacity: a, display: "flex", alignItems: "center",
      justifyContent: "center" }}>
      <div style={{ textAlign: "center", maxWidth: 1500 }}>
        <div style={{ ...kicker(24, "#8DA4B2"), opacity: ramp(t, card.from + 0.1, card.from + 0.5) }}>{card.kicker}</div>
        <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", columnGap: 26, marginTop: 26 }}>
          {words.map((w, i) => {
            const q = sp(card.from + 0.25 + i * 0.07);
            return (
              <div key={i} style={{ overflow: "hidden", paddingBottom: 10 }}>
                <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 96, lineHeight: 1.05,
                  color: theme.paper, letterSpacing: -1.5, transform: `translateY(${(1 - q) * 105}%)` }}>{w}</div>
              </div>
            );
          })}
        </div>
        <div style={{ height: 3, background: theme.azul, margin: "26px auto 0", borderRadius: 2,
          width: 320 * ramp(t, card.from + 0.9, card.from + 1.6) }} />
        <div style={{ fontFamily: theme.sans, fontWeight: 500, fontSize: 32, color: "#8DA4B2", marginTop: 26,
          opacity: ramp(t, card.from + 1.1, card.from + 1.6) }}>{card.sub}</div>
      </div>
    </AbsoluteFill>
  );
};

const OutroCard: React.FC<{ card: Extract<Card, { kind: "outro" }> }> = ({ card }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  if (t < card.from || t > card.to) return null;
  const a = inOut(t, card.from, card.to, 0.35, 0.5);
  const q = sp(card.from + 0.35, { damping: 13, stiffness: 160 });
  return (
    <AbsoluteFill style={{ background: theme.ink, opacity: a, display: "flex", alignItems: "center",
      justifyContent: "center", flexDirection: "column" }}>
      <div style={{ opacity: ramp(t, card.from + 0.1, card.from + 0.5) }}><Mark size={38} color={theme.paper} /></div>
      <div style={{ marginTop: 38, background: theme.naranjo, color: theme.ink, fontFamily: theme.sans,
        fontWeight: 800, fontSize: 68, borderRadius: 28, padding: "22px 52px", transform: `scale(${0.6 + 0.4 * q})`,
        opacity: Math.min(q * 2, 1), boxShadow: "0 18px 50px rgba(224,140,74,0.25)" }}>{card.cta}</div>
      <div style={{ fontFamily: theme.mono, fontWeight: 500, fontSize: 36, color: theme.paper, marginTop: 30,
        letterSpacing: "0.02em", clipPath: `inset(0 ${(1 - ramp(t, card.from + 0.8, card.from + 1.4)) * 100}% 0 0)` }}>
        {card.sub}</div>
    </AbsoluteFill>
  );
};

const Tag: React.FC<{ card: Extract<Card, { kind: "tag" }> }> = ({ card }) => {
  const { t } = useTime();
  if (t < card.from || t > card.to) return null;
  return (
    <div style={{ position: "absolute", left: 48, top: 40, opacity: inOut(t, card.from, card.to),
      ...kicker(18, theme.paper), background: theme.azul, borderRadius: 999, padding: "10px 22px" }}>{card.text}</div>
  );
};

// ------------------------------------------------------------ lower third ---
const LowerThird: React.FC<{ name: string; title: string; from: number; to: number; side: "left" | "right" }> = (
  { name, title, from, to, side },
) => {
  const { t } = useTime();
  if (t < from || t > to) return null;
  const bar = ramp(t, from, from + 0.35);
  const nameIn = ramp(t, from + 0.15, from + 0.6);
  const titleIn = ramp(t, from + 0.4, from + 0.85);
  const out = 1 - ramp(t, to - 0.4, to, Easing.in(Easing.cubic));
  return (
    <div style={{ position: "absolute", [side]: SIDE_X, bottom: 110, opacity: out, display: "flex",
      flexDirection: side === "left" ? "row" : "row-reverse", alignItems: "stretch", gap: 18 }}>
      <div style={{ width: 6, borderRadius: 3, background: theme.azul, transform: `scaleY(${bar})`,
        transformOrigin: "bottom" }} />
      <div style={{ textAlign: side }}>
        <div style={{ clipPath: `inset(0 ${(1 - nameIn) * 100}% 0 0)`, ...glass, borderRadius: 14,
          padding: "10px 22px", fontFamily: theme.sans, fontWeight: 800, fontSize: 44, color: theme.ink,
          letterSpacing: -0.8 }}>{name}</div>
        <div style={{ marginTop: 8, display: "inline-block", clipPath: `inset(0 ${(1 - titleIn) * 100}% 0 0)`,
          background: theme.ink, borderRadius: 10, padding: "7px 16px", fontFamily: theme.sans, fontWeight: 600,
          fontSize: 24, color: theme.paper }}>{title}</div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------- key points -----
const KeyPoints: React.FC<{ b: Band }> = ({ b }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  const enter = sp(b.from);
  const out = 1 - ramp(t, b.to - 0.35, b.to, Easing.in(Easing.cubic));
  const dir = b.side === "left" ? -1 : 1;
  const visible = b.chips.filter((c) => t >= c.at - 0.08);
  const active = visible.length - 1;
  const ITEM = 78;
  return (
    <div style={{ position: "absolute", [b.side]: b.inset ?? SIDE_X, top: 0, bottom: 60, display: "flex", alignItems: "center",
      opacity: Math.min(enter * 1.4, 1) * out,
      transform: `translateX(${dir * (1 - enter) * 60}px) perspective(1400px) rotateY(${dir * -(1 - enter) * 14}deg)` }}>
      <div style={{ ...glass, borderRadius: 26, padding: "26px 34px 28px 30px", width: 610 }}>
        {b.kicker && (
          <div>
            <div style={{ ...kicker(17, theme.azul) }}>{b.kicker}</div>
            <div style={{ height: 3, background: theme.azul, borderRadius: 2, marginTop: 10, marginBottom: 18,
              width: `${100 * ramp(t, b.from + 0.15, b.from + 0.7)}%`, opacity: 0.85 }} />
          </div>
        )}
        <div style={{ position: "relative" }}>
          {/* timeline rail */}

          <div style={{ position: "absolute", left: 21, top: 22, width: 3, borderRadius: 2, background: theme.azul,
            height: Math.max(0, active) * ITEM * (active > 0 ? sp(b.chips[active].at - 0.08) : 0)
              + Math.max(0, active - 1) * 0 }} />
          {b.chips.map((c, i) => {
            const on = t >= c.at - 0.08;
            if (!on) return null;
            const grow = sp(c.at - 0.08, { damping: 20, stiffness: 170 });
            const pop = sp(c.at - 0.08, { damping: 12, stiffness: 180 });
            const wipe = ramp(t, c.at - 0.02, c.at + 0.38);
            const isActive = i === active;
            return (
              <div key={i} style={{ height: i === 0 ? ITEM : ITEM * grow, display: "flex", alignItems: "center", gap: 20,
                position: "relative", overflow: "visible" }}>
                <div style={{ width: 45, height: 45, borderRadius: 999, flexShrink: 0, display: "flex",
                  alignItems: "center", justifyContent: "center", fontFamily: theme.sans, fontWeight: 800, fontSize: 20,
                  background: on ? (isActive ? theme.azul : theme.paper) : "rgba(16,20,24,0.06)",
                  color: on ? (isActive ? theme.paper : theme.azul) : "rgba(16,20,24,0.25)",
                  border: `2px solid ${on ? theme.azul : "rgba(16,20,24,0.12)"}`,
                  transform: `scale(${on ? 0.7 + 0.3 * pop : 0.85})`,
                  boxShadow: isActive ? "0 0 0 8px rgba(26,92,134,0.14)" : "none" }}>{i + 1}</div>
                <div style={{ clipPath: `inset(-10px ${(1 - wipe) * 100}% -10px 0)`, fontFamily: theme.sans,
                  fontWeight: isActive ? 700 : 600, fontSize: 34, letterSpacing: -0.5, lineHeight: 1.1,
                  color: isActive ? theme.ink : theme.inkMuted, transform: `translateX(${(1 - wipe) * 14}px)` }}>
                  {c.label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ stat ----
const StatView: React.FC<{ s: Stat }> = ({ s }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  const [a, b] = s.big.split("→").map((x) => x.trim());
  const A = parseInt(a, 10), B = parseInt(b, 10);
  const enter = sp(s.from);
  const out = 1 - ramp(t, s.to - 0.35, s.to);
  const draw = ramp(t, s.from + 0.45, s.from + 0.95);
  const count = ramp(t, s.from + 0.85, s.from + 1.6, Easing.out(Easing.cubic));
  const val = Number.isFinite(A) && Number.isFinite(B) ? Math.round(A + (B - A) * count) : b;
  const land = sp(s.from + 1.55, { damping: 10, stiffness: 200 });
  const dir = s.side === "left" ? -1 : 1;
  return (
    <div style={{ position: "absolute", [s.side]: s.inset ?? SIDE_X, top: 0, bottom: 60, display: "flex", alignItems: "center",
      opacity: Math.min(enter * 1.4, 1) * out, transform: `translateX(${dir * (1 - enter) * 50}px)` }}>
      <div style={{ ...glass, borderRadius: 28, padding: "26px 40px 30px" }}>
        {s.kicker && <div style={kicker(17, theme.azul)}>{s.kicker}</div>}
        <div style={{ display: "flex", alignItems: "center", gap: 26, marginTop: 8 }}>
          <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 150, lineHeight: 1,
            color: theme.inkMuted, letterSpacing: -3 }}>{a}</div>
          <svg width={120} height={60} viewBox="0 0 120 60">
            <path d="M6 30 H104 M86 12 L106 30 L86 48" fill="none" stroke={theme.azul} strokeWidth={6}
              strokeLinecap="round" strokeLinejoin="round" strokeDasharray={170} strokeDashoffset={170 * (1 - draw)} />
          </svg>
          <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 150, lineHeight: 1, color: theme.azul,
            letterSpacing: -3, minWidth: 150, opacity: count > 0 ? 1 : 0,
            transform: `scale(${count >= 1 ? 0.85 + 0.15 * land : 1})` }}>{val}</div>
        </div>
        {s.caption && <div style={{ fontFamily: theme.sans, fontWeight: 600, fontSize: 28, color: theme.ink,
          marginTop: 10, clipPath: `inset(0 ${(1 - ramp(t, s.from + 1.6, s.from + 2.2)) * 100}% 0 0)` }}>{s.caption}</div>}
      </div>
    </div>
  );
};

// ----------------------------------------------------------------- quote ----
const QuoteView: React.FC<{ s: Quote }> = ({ s }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  const enter = sp(s.from);
  const out = 1 - ramp(t, s.to - 0.35, s.to);
  const words = s.text.split(" ");
  const sweep = ramp(t, s.from + 0.35 + words.length * 0.06, s.from + 0.85 + words.length * 0.06);
  const dir = s.side === "left" ? -1 : 1;
  return (
    <div style={{ position: "absolute", [s.side]: s.inset ?? SIDE_X, top: 0, bottom: 60, width: 680, display: "flex",
      alignItems: "center", opacity: Math.min(enter * 1.4, 1) * out, transform: `translateX(${dir * (1 - enter) * 50}px)` }}>
      <div style={{ ...glass, borderRadius: 28, padding: "24px 40px 34px", position: "relative" }}>
        <div style={{ position: "absolute", left: 26, top: -36, fontFamily: theme.serif, fontSize: 190, lineHeight: 1,
          color: theme.azul, transform: `scale(${sp(s.from + 0.1, { damping: 11 })})`, transformOrigin: "left bottom" }}>“</div>
        {s.kicker && <div style={{ ...kicker(17, theme.azul), marginTop: 40 }}>{s.kicker}</div>}
        <div style={{ position: "relative", marginTop: 12 }}>
          <div style={{ position: "absolute", left: -8, right: -8, top: "52%", bottom: "4%", borderRadius: 6,
            background: "rgba(26,92,134,0.16)", transform: `scaleX(${sweep})`, transformOrigin: "left" }} />
          <div style={{ position: "relative", display: "flex", flexWrap: "wrap", columnGap: 16 }}>
            {words.map((w, i) => {
              const q = sp(s.from + 0.25 + i * 0.06);
              return (
                <div key={i} style={{ overflow: "hidden", paddingBottom: 6 }}>
                  <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 64, color: theme.ink,
                    lineHeight: 1.08, letterSpacing: -1, transform: `translateY(${(1 - q) * 105}%)` }}>{w}</div>
                </div>
              );
            })}
          </div>
        </div>
        {s.sub && <div style={{ fontFamily: theme.sans, fontWeight: 600, fontSize: 26, color: theme.inkMuted,
          marginTop: 12, opacity: ramp(t, s.from + 0.9, s.from + 1.3) }}>{s.sub}</div>}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ book ----
const BookView: React.FC<{ s: Book }> = ({ s }) => {
  const { t } = useTime();
  const sp = useSpringAt();
  const enter = sp(s.from, { damping: 16, stiffness: 90 });
  const out = 1 - ramp(t, s.to - 0.4, s.to);
  const rot = interpolate(enter, [0, 1], [-75, -22]);
  const W = 230, H = 340, D = 34;
  const dir = s.side === "left" ? -1 : 1;
  return (
    <div style={{ position: "absolute", [s.side]: s.inset ?? SIDE_X, top: 0, bottom: 60, display: "flex", alignItems: "center",
      gap: 34, flexDirection: s.side === "left" ? "row" : "row-reverse", opacity: Math.min(enter * 1.5, 1) * out }}>
      <div style={{ perspective: 1100, transform: `translateX(${dir * (1 - enter) * 80}px)` }}>
        <div style={{ width: W, height: H, position: "relative", transformStyle: "preserve-3d",
          transform: `rotateY(${dir * rot}deg) rotateX(4deg)` }}>
          <div style={{ position: "absolute", inset: 0, background: theme.azul, borderRadius: "4px 10px 10px 4px",
            boxShadow: "0 30px 60px rgba(16,20,24,0.45)", padding: "34px 24px", display: "flex",
            flexDirection: "column", justifyContent: "space-between",
            backgroundImage: "linear-gradient(90deg, rgba(0,0,0,0.25) 0, rgba(0,0,0,0) 14px)" }}>
            <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 38, lineHeight: 1.05,
              color: theme.paper }}>{s.title}</div>
            <div>
              <div style={{ height: 2, width: 60, background: theme.paper, opacity: 0.6, marginBottom: 12 }} />
              <div style={{ fontFamily: theme.sans, fontWeight: 600, fontSize: 15, color: theme.paper, opacity: 0.85,
                letterSpacing: "0.04em" }}>{s.author}</div>
            </div>
          </div>
          <div style={{ position: "absolute", top: 4, bottom: 4, right: -D + 2, width: D, background: "#F1EFE8",
            transform: `rotateY(90deg)`, transformOrigin: "left", backgroundImage:
              "repeating-linear-gradient(0deg, #E6E3DA 0 2px, #F4F2EC 2px 4px)" }} />
        </div>
      </div>
      <div style={{ ...glass, borderRadius: 22, padding: "18px 26px 20px", maxWidth: 380,
        opacity: ramp(t, s.from + 0.45, s.from + 0.85), transform: `translateY(${(1 - ramp(t, s.from + 0.45, s.from + 0.9)) * 16}px)` }}>
        {s.kicker && <div style={kicker(16, theme.azul)}>{s.kicker}</div>}
        <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontSize: 40, color: theme.ink, lineHeight: 1.08,
          marginTop: 8 }}>{s.title}</div>
        <div style={{ fontFamily: theme.sans, fontWeight: 600, fontSize: 22, color: theme.inkMuted, marginTop: 8 }}>{s.author}</div>
      </div>
    </div>
  );
};

const Beats: React.FC<{ beats: Beat[] }> = ({ beats }) => {
  const { t } = useTime();
  return (
    <>
      {beats.filter((b) => t >= b.from && t <= b.to).map((b, i) => {
        switch (b.kind) {
          case "band": return <KeyPoints key={i} b={b} />;
          case "stat": return <StatView key={i} s={b} />;
          case "quote": return <QuoteView key={i} s={b} />;
          case "book": return <BookView key={i} s={b} />;
        }
      })}
    </>
  );
};

// ------------------------------------------------------------- captions -----
const Captions: React.FC<{ chunks: LChunk[]; hidden: boolean }> = ({ chunks, hidden }) => {
  const { t } = useTime();
  if (hidden || !chunks.length) return null;
  const c = chunks.find((k) => t >= k.start && t < k.end);
  if (!c) return null;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 64, display: "flex", justifyContent: "center" }}>
      <div style={{ ...glass, borderRadius: 18, padding: "10px 26px", fontFamily: theme.sans, fontWeight: 700,
        fontSize: 44, color: theme.ink }}>{c.words.map((w) => w.text).join(" ")}</div>
    </div>
  );
};

// ------------------------------------------------------------- composition --
export const GboLongform: React.FC<LongProps> = (props) => {
  const { t } = useTime();
  const covering = props.cards.find((c) => c.kind !== "tag" && t >= c.from && t <= c.to);
  const fullDark = props.cards.find((c) => (c.kind === "title" || c.kind === "outro") && t >= c.from && t <= c.to);
  const total = props.chapters.length;
  const chTitle = (n: number) => props.chapters.find((c) => c.n === n)?.title ?? "";
  return (
    <AbsoluteFill style={{ backgroundColor: theme.ink }}>
      <OffthreadVideo src={staticFile(props.video)} style={{ width: 1920, height: 1080 }} muted />
      <Beats beats={props.beats} />
      {props.lowerThirds.map((l, i) => <LowerThird key={i} {...l} />)}
      <ChapterPill chapters={props.chapters} hidden={!!fullDark} />
      {props.cards.map((c, i) => {
        switch (c.kind) {
          case "chapter": return <ChapterCard key={i} card={c} total={total} pillTitle={chTitle(c.n)} />;
          case "title": return <TitleCard key={i} card={c} />;
          case "outro": return <OutroCard key={i} card={c} />;
          case "tag": return <Tag key={i} card={c} />;
        }
      })}
      <Captions chunks={props.captions} hidden={!!covering} />
    </AbsoluteFill>
  );
};
