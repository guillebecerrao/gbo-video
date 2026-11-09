import { IconName } from "../types";

export type LWord = { text: string; start: number; end: number; emph?: boolean };
export type LChunk = { start: number; end: number; words: LWord[] };

export type Chapter = { id: string; n: number; title: string; start: number; end: number };

export type BandChip = { label: string; at: number; icon?: IconName };
export type Band = {
  kind: "band";
  inset?: number;
  from: number; to: number;
  side: "left" | "right";
  kicker?: string;
  chips: BandChip[];
};
export type Stat = {
  inset?: number;
  kind: "stat";
  from: number; to: number;
  side: "left" | "right";
  kicker?: string;
  big: string;        // e.g. "10 → 1"
  caption?: string;
};
export type Quote = {     // phrase card for a key concept
  inset?: number;
  kind: "quote";
  from: number; to: number;
  side: "left" | "right";
  kicker?: string;
  text: string;
  sub?: string;
};
export type Book = {
  inset?: number;
  kind: "book";
  from: number; to: number;
  side: "left" | "right";
  kicker?: string;
  title: string;
  author: string;
};
export type Beat = Band | Stat | Quote | Book;

export type Card =
  | { kind: "title"; from: number; to: number; kicker: string; title: string; sub: string }
  | { kind: "chapter"; from: number; to: number; n: number; total: number; title: string }
  | { kind: "outro"; from: number; to: number; cta: string; sub: string }
  | { kind: "tag"; from: number; to: number; text: string };

export type LongProps = {
  video: string;
  durationSec: number;
  captions: LChunk[];
  chapters: Chapter[];
  cards: Card[];
  beats: Beat[];
  lowerThirds: { name: string; title: string; from: number; to: number; side: "left" | "right" }[];
};
