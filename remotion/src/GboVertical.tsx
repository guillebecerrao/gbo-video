import React from "react";
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { GboProps } from "./types";
import { Captions } from "./Captions";
import { LowerThird, SplitPanel, TitleCard, envelope } from "./Overlays";
import { EndCard } from "./reel/GboReel";

// Composes graphics + captions over a cut ALREADY made by video-use.
// Split screen: the video slides into the top half (face kept), panel fills the bottom.
export const GboVertical: React.FC<GboProps> = (props) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const split = props.splits.find((s) => t >= s.from && t <= s.to);
  const k = split ? envelope(t, split.from, split.to, 0.3) : 0; // 0 = full, 1 = split

  const videoH = 1920 - 960 * k;
  return (
    <AbsoluteFill style={{ backgroundColor: "#101418" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: videoH,
        overflow: "hidden" }}>
        <OffthreadVideo src={staticFile(props.video)} style={{
          width: 1080, height: 1920, position: "absolute", left: 0,
          // keep the face: shift the frame up a little while the window shrinks
          top: -80 * k,
        }} />
      </div>
      {split && <SplitPanel split={split} />}
      {props.lowerThird && <LowerThird {...props.lowerThird} />}
      {props.titleCard && <TitleCard {...props.titleCard} />}
      {/* captions LAST; ride the seam during split screens */}
      {!(props.titleCard && t >= props.titleCard.from && t <= props.titleCard.to) &&
        !(props.end && t >= props.end.from + 0.3) && (
        <Captions chunks={props.captions} yCenter={split ? 960 + 110 * k : 1340}
          variant={props.captionStyle ?? "paper"} />
      )}
      {props.end && <EndCard e={props.end} />}
    </AbsoluteFill>
  );
};
