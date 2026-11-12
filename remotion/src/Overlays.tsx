import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Split } from "./types";
import { Icon } from "./Icon";
import { easeInOut, easeOut, kicker, theme } from "./theme";

const sec = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};

// in/out envelope: 0→1 over `d` s after `from`, 1→0 over `d` s before `to`
export const envelope = (t: number, from: number, to: number, d = 0.3) =>
  Math.min(easeInOut((t - from) / d), easeInOut((to - t) / d));

// /<monogram> mark (theme.monogram), mono voice. Slash in azul (naranjo is reserved for the CTA).
export const Mark: React.FC<{ size: number; color?: string; slash?: string }> = (
  { size, color = theme.ink, slash = theme.azul },
) => (
  <span style={{ fontFamily: theme.mono, fontWeight: 500, fontSize: size, letterSpacing: "-0.06em",
    color, lineHeight: 1 }}><span style={{ color: slash }}>/</span>{theme.monogram}</span>
);

export const LowerThird: React.FC<{ name: string; title: string; from: number; to: number }> = (
  { name, title, from, to },
) => {
  const t = sec();
  if (t < from || t > to) return null;
  const p = envelope(t, from, to, 0.35);
  return (
    <div style={{ position: "absolute", left: 64, top: 300, opacity: p,
      transform: `translateX(${(1 - p) * -40}px)` }}>
      <div style={{ background: theme.paperSoft, borderRadius: 22, padding: "24px 34px 26px",
        boxShadow: "0 10px 30px rgba(16,20,24,0.25)" }}>
        <Mark size={30} />
        <div style={{ fontFamily: theme.sans, color: theme.ink, fontSize: 52, fontWeight: 800,
          letterSpacing: -1, marginTop: 12 }}>{name}</div>
        <div style={{ fontFamily: theme.sans, color: theme.inkMuted, fontSize: 32, fontWeight: 500,
          marginTop: 4 }}>{title}</div>
      </div>
    </div>
  );
};

// Bottom half of the split screen: paper surface, ink text, azul structure.
export const SplitPanel: React.FC<{ split: Split }> = ({ split }) => {
  const t = sec();
  const p = envelope(t, split.from, split.to, 0.3);
  const cards = split.layout === "cards";
  return (
    <div style={{
      position: "absolute", left: 0, right: 0, top: 960, height: 960,
      background: theme.paper, transform: `translateY(${(1 - p) * 960}px)`,
      borderTop: `4px solid ${theme.azul}`,
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", paddingTop: 120,
    }}>
      {split.title && (
        <div style={{ ...kicker(36, theme.inkMuted), marginBottom: 46,
          opacity: easeOut((t - split.from - 0.15) / 0.3) }}>{split.title}</div>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center",
        gap: cards ? 36 : 26, maxWidth: 980 }}>
        {split.items.map((it) => {
          const q = easeOut((t - it.at + 0.05) / 0.25);
          const active = t >= it.at - 0.05;
          return (
            <div key={it.label} style={{
              opacity: q, transform: `translateY(${(1 - q) * 24}px) scale(${0.92 + 0.08 * q})`,
              display: "flex", flexDirection: cards ? "column" : "row",
              alignItems: "center", gap: cards ? 18 : 16,
              width: cards ? (split.cardWidth ?? 300) : undefined,
              padding: cards ? "44px 18px" : "24px 34px",
              borderRadius: 28, background: "#FFFFFF00",
              border: `2px solid ${active ? theme.azul : theme.line}`,
              color: theme.ink, fontFamily: theme.sans,
            }}>
              <div style={{ color: theme.azul }}>
                <Icon name={it.icon} size={cards ? 104 : 60} />
              </div>
              <div style={{ fontSize: cards ? 50 : 44, fontWeight: 700,
                letterSpacing: -0.5 }}>{it.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Title card in the serif voice (manual: Newsreader for titles, italics for emphasis).
export const TitleCard: React.FC<{ text: string; kicker?: string; from: number; to: number }> = (
  { text, kicker: k, from, to },
) => {
  const t = sec();
  if (t < from || t > to) return null;
  const p = envelope(t, from, to, 0.25);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 780, display: "flex",
      justifyContent: "center", opacity: p }}>
      <div style={{ background: theme.paperSoft, borderRadius: 36, padding: "38px 72px 44px",
        textAlign: "center", transform: `scale(${0.9 + 0.1 * easeOut((t - from) / 0.35)})`,
        boxShadow: "0 14px 40px rgba(16,20,24,0.3)" }}>
        {k && <div style={{ ...kicker(30, theme.inkMuted), marginBottom: 14 }}>{k}</div>}
        <div style={{ fontFamily: theme.serif, fontStyle: "italic", fontWeight: 400, color: theme.azul,
          fontSize: 128, lineHeight: 1, letterSpacing: -2 }}>{text}</div>
      </div>
    </div>
  );
};
