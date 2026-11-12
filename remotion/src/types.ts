export type Word = { text: string; start: number; end: number; emph: boolean };
export type Chunk = { start: number; end: number; words: Word[]; cta?: boolean };
export type Item = { label: string; icon: IconName; at: number };
export type IconName =
  | "clock" | "coins" | "people" | "server" | "globe" | "briefcase" | "chart" | "speech"
  | "box" | "play" | "user";

export type Split = {
  from: number;
  to: number;
  title?: string;
  layout: "cards" | "chips";
  cardWidth?: number;     // cards only; e.g. 420 for a 2×2 grid
  items: Item[];
};

export type GboProps = {
  video: string;          // path relative to --public-dir
  durationSec: number;
  captions: Chunk[];
  lowerThird?: { name: string; title: string; from: number; to: number };
  splits: Split[];
  titleCard?: { text: string; kicker?: string; from: number; to: number };
  // "paper" = light bubble (default). "dark" = reel style (same as GboReel):
  // ink bubble, paper text, emphasis on an azul block, unsaid words dimmed.
  captionStyle?: "paper" | "dark";
  // End card with typed URL + click (GboReel EndCard). Captions hide 0.3 s after it starts.
  end?: { from: number; title: string; cta: string; url: string; foot?: string;
    typeAt: number; charDur: number; clickAt: number };
};
