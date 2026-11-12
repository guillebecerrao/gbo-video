import React from "react";
import { Composition } from "remotion";
import { GboVertical } from "./GboVertical";
import { GboProps } from "./types";
import { GboLongform } from "./long/GboLongform";
import { LongProps } from "./long/types";
import { GboReel } from "./reel/GboReel";
import { ReelProps } from "./reel/types";
import { CoverProps, GboCover, GboCoverSolo, GboCoverSplit } from "./reel/GboCover";
import { GboThumb, ThumbProps } from "./long/GboThumb";
import { Still } from "remotion";

const LFPS = 30000 / 1001;
const longDefaults: LongProps = { video: "preview_cut_v2.mp4", durationSec: 5, captions: [], chapters: [], cards: [], beats: [], lowerThirds: [] };

const FPS = 24;
const reelDefaults: ReelProps = { video: "clips/example/cut_video.mp4", durationSec: 5, captions: [], sides: [],
  hook: { kicker: "", lines: [], from: 0, to: 1 }, tags: [], panels: [],
  end: { from: 99, title: "", cta: "", url: "", typeAt: 0, charDur: 0.07, clickAt: 0 } };

const defaultProps: GboProps = {
  video: "work_final/base_nocaps.mp4",
  durationSec: 5,
  captions: [],
  splits: [],
};

export const RemotionRoot: React.FC = () => (
  <>
  <Composition
    id="GboLongform"
    component={GboLongform}
    fps={LFPS}
    width={1920}
    height={1080}
    durationInFrames={150}
    defaultProps={longDefaults}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.round(props.durationSec * LFPS),
    })}
  />
  <Still id="GboThumb" component={GboThumb} width={1280} height={720}
    defaultProps={{ left: { img: "", name: "", x: 0, y: 0 }, right: { img: "", name: "", x: 0, y: 0 }, kicker: "", title: "", foot: "" } as ThumbProps} />
  <Still id="GboCover" component={GboCover} width={1080} height={1920}
    defaultProps={{ left: { img: "", name: "" }, right: { img: "", name: "" }, kicker: "", title: "", foot: "" } as CoverProps} />
  <Still id="GboCoverSolo" component={GboCoverSolo} width={1080} height={1920}
    defaultProps={{ layout: "frame", img: "", kicker: "", title: "", foot: "" } as CoverProps} />
  <Still id="GboCoverSplit" component={GboCoverSplit} width={1080} height={1920}
    defaultProps={{ layout: "split", left: { img: "" }, right: { img: "" }, kicker: "", title: "", foot: "" } as CoverProps} />
  <Composition
    id="GboReel"
    component={GboReel}
    fps={LFPS}
    width={1080}
    height={1920}
    durationInFrames={150}
    defaultProps={reelDefaults}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.round(props.durationSec * LFPS),
    })}
  />
  <Composition
    id="GboVertical"
    component={GboVertical}
    fps={FPS}
    width={1080}
    height={1920}
    durationInFrames={FPS * 5}
    defaultProps={defaultProps}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.round(props.durationSec * FPS),
    })}
  />
  </>
);
