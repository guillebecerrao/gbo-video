import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Chunk } from "./types";
import { easeOut, theme } from "./theme";

// estilo.md: 2–4 word chunks, sentence case, max 1 emphasized word, fade/slide ≤ 120 ms.
// Brand: paper bubble + ink text, emphasis in azul mar. The CTA chunk ("sígueme") is the
// one naranjo element on screen (manual: one CTA per screen, nothing else uses naranjo).
const isCta = (c: Chunk) =>
  c.words.some((w) => /^s[ií]gueme/i.test(w.text.normalize("NFC")));

export const Captions: React.FC<{ chunks: Chunk[]; yCenter: number }> = ({ chunks, yCenter }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const c = chunks.find((k) => t >= k.start && t < k.end);
  if (!c) return null;
  const p = easeOut((t - c.start) / 0.12);
  const cta = isCta(c);

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
