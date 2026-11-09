import type React from "react";
// EXAMPLE BRAND: these are the author's brand tokens, shipped as a working example.
// Replace them with the values of your own marca.md (local profile) on first use.
import { loadFont as loadArchivo } from "@remotion/google-fonts/Archivo";
import { loadFont as loadNewsreader } from "@remotion/google-fonts/Newsreader";
import { loadFont as loadMono } from "@remotion/google-fonts/SplineSansMono";

// Brand logic of the example:
// base paper + ink, accents "in grams" with fixed roles. Never #000 / #FFF.
//   azul    = the sea: structure, emphasis
//   naranjo = action: ONE CTA per screen, nothing else uses it
//   sakura / verde: not used in video yet
const archivo = loadArchivo("normal", { weights: ["500", "600", "700", "800"], subsets: ["latin", "latin-ext"] });
const newsreader = loadNewsreader("normal", { weights: ["400", "500"], subsets: ["latin", "latin-ext"] });
loadNewsreader("italic", { weights: ["400"], subsets: ["latin", "latin-ext"] });
const mono = loadMono("normal", { weights: ["500"], subsets: ["latin"] });

export const theme = {
  ink: "#101418",
  inkMuted: "#5E676E",
  paper: "#FAFAF7",
  paperSoft: "rgba(250, 250, 247, 0.95)",
  line: "rgba(16, 20, 24, 0.14)",
  azul: "#1A5C86",
  naranjo: "#E08C4A",
  sakura: "#E8A3B3",
  verde: "#7FC04E",
  sans: archivo.fontFamily, // system: captions, UI, kickers
  serif: newsreader.fontFamily, // the voice: titles, italics
  mono: mono.fontFamily, // the technical: monogram
  monogram: "gbo", // short mark shown as /<monogram> in lower thirds, cards and thumbnails
};

// kicker = Archivo 600, tracking 0.24em, uppercase (manual §04)
export const kicker = (size: number, color: string): React.CSSProperties => ({
  fontFamily: theme.sans, fontWeight: 600, fontSize: size, letterSpacing: "0.24em",
  textTransform: "uppercase", color,
});

// cubic easings (never linear — video-use/gbo rule)
export const easeOut = (t: number) => 1 - Math.pow(1 - Math.min(Math.max(t, 0), 1), 3);
export const easeInOut = (t: number) => {
  const x = Math.min(Math.max(t, 0), 1);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
