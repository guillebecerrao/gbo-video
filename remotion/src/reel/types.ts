export type RWord = { text: string; start: number; end: number; emph: boolean };
export type RChunk = { start: number; end: number; spk: "G" | "J"; words: RWord[] };
export type Side = "left" | "right";

export type ReelProps = {
  video: string;            // relative to --public-dir
  durationSec: number;      // includes the end card
  captions: RChunk[];
  sides: { from: number; to: number; side: Side }[];   // gaze side of the shot on screen (where text lives)
  hook: { kicker: string; lines: { text: string; emph?: boolean }[][]; from: number; to: number };
  topic?: { text: string; from: number; to: number };
  tags: { name: string; title: string; from: number; to: number; side: Side }[];
  panels: { kicker: string; from: number; to: number; side: Side;
    chips: { label: string; sub?: string; at: number; struck?: boolean }[] }[];
  end: { from: number; title: string; cta: string; url: string; foot?: string;
    typeAt: number; charDur: number; clickAt: number };
};
