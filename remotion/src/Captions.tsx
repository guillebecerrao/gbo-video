import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Chunk } from "./types";
import { easeOut, theme } from "./theme";

// estilo.md: 2–4 word chunks, sentence case, max 1 emphasized word, fade/slide ≤ 120 ms.
// Brand: paper bubble + ink text, emphasis in azul mar. The CTA chunk ("sígueme") is the
// one naranjo element on screen ("créate" also counts as CTA) (manual: one CTA per screen, nothing else uses naranjo).
const isCta = (c: Chunk) =>
  !!c.cta || c.words.some((w) => /^(s[ií]gueme|cr[eé]ate)/i.test(w.text.normalize("NFC")));

export const Captions: React.FC<{ chunks: Chunk[]; yCenter: number; variant?: "paper" | "dark" }> = (
  { chunks, yCenter, variant = "paper" },
) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const c = chunks.find((k) => t >= k.start && t < k.end);
  if (!c) return null;
  const p = easeOut((t - c.start) / 0.12);
  const cta = isCta(c);
  if (variant === "dark") return <DarkBubble c={c} t={t} p={p} cta={cta} yCenter={yCenter} />;

  return (
    <div style={{
      position: "absolute", left: 0, right: 0, top: yCenter, display: "flex",
      justifyContent: "center", transform: `translateY(calc(-50% + ${(1 - p) * 14}px))`,
      opacity: p,
    }}>
      <div style={{
        background: cta ? theme.naranjo : theme.paperSoft, borderRadius: 28, padding: "18px 36px",
        maxWidth: 860, textAlign: "center", fontFamily: theme.sans, fontWeight: 700,
        fontSize: 60, lineHeight: 1.15, color: theme.ink, letterSpacing: -0.5,
        boxShadow: "0 10px 30px rgba(16,20,24,0.28)",
      }}>
        {c.words.map((w, i) => (
          <span key={i} style={{ color: w.emph && !cta ? theme.azul : theme.ink }}>
            {w.text}{i < c.words.length - 1 ? " " : ""}
          </span>
        ))}
      </div>
    </div>
  );
};

// Reel style (same as GboReel captions): ink bubble, paper text, Archivo 800, emphasis on an
// azul block, words not yet said at 42% opacity. CTA chunk keeps the single naranjo bubble.
const DarkBubble: React.FC<{ c: Chunk; t: number; p: number; cta: boolean; yCenter: number }> = (
  { c, t, p, cta, yCenter },
) => (
  <div style={{
    position: "absolute", left: 130, width: 820, top: yCenter, display: "flex", justifyContent: "center",
    transform: `translateY(calc(-50% + ${(1 - p) * 10}px))`, opacity: p,
  }}>
    <div style={{
      background: cta ? theme.naranjo : "rgba(16,20,24,0.88)", borderRadius: 20, padding: "14px 28px 18px",
      textAlign: "center", fontFamily: theme.sans, fontWeight: 800, fontSize: 58, lineHeight: 1.18,
      letterSpacing: -0.8, color: cta ? theme.ink : theme.paper, boxShadow: "0 10px 30px rgba(16,20,24,0.35)",
    }}>
      {c.words.map((w, i) => {
        const said = t >= w.start - 0.03;
        return (
          <React.Fragment key={i}>
            <span style={{ opacity: said ? 1 : 0.42, ...(w.emph && !cta ? { background: theme.azul,
              borderRadius: 8, padding: "0 10px", margin: "0 -4px" } : {}) }}>{w.text}</span>
            {i < c.words.length - 1 ? " " : ""}
          </React.Fragment>
        );
      })}
    </div>
  </div>
);
