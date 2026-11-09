export type Word = { text: string; start: number; end: number; emph: boolean };
export type Chunk = { start: number; end: number; words: Word[] };
export type Item = { label: string; icon: IconName; at: number };
export type IconName =
  | "clock" | "coins" | "people" | "server" | "globe" | "briefcase" | "chart" | "speech";

export type Split = {
  from: number;
  to: number;
  title?: string;
  layout: "cards" | "chips";
  items: Item[];
};

export type GboProps = {
  video: string;          // path relative to --public-dir
  durationSec: number;
  captions: Chunk[];
  lowerThird?: { name: string; title: string; from: number; to: number };
  splits: Split[];
  titleCard?: { text: string; kicker?: string; from: number; to: number };
};
