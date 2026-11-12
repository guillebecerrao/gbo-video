# Changelog

## 0.2.0 — 2026-11-12
Learnings from four more edits (event recap, a shop promo, a product-launch reel, a montage reel), consolidated.

- Ingest checklist (phase 3): color by metadata (HLG/PQ → SDR, log → LUT), mirrored footage, rotation, mixed fps
- Cuts: minimum air measured by energy (≥ 0.15 s; 0.4–0.5 s on take change), verify cuts on the music-free base,
  cut (never speed up) hesitations
- Versioning: one counter per piece from previews to final; never re-render over a number the creator opened
- `gbo_render.py`: `hflip`, `grade`, `color_chain`, `fps`, per-range `speed` / `mute`, b-roll and card anchors
  `[range, source_time]` resolved to output time (`<out>.cards.json`), rounded caption box
  (`caption_style.rounded`), captions never spill into the next range
- `mix_audio.py`: licensed music track with `--music`, `--music-offset` and its own fade-out; `--no-sfx`
- New `cut_energy.py`: air before/after the voice in every EDL range (adaptive noise-floor threshold) and voiced islands
- New `rechunk.py`: re-segment captions at phrase boundaries from a one-phrase-per-line file, keeping word timings
- Music: the track's ending never lands under the CTA; lower library masters before ducking
- Remotion: `Captions` `dark` variant (reel style), `EndCard` (typed URL) in `GboVertical`, `cardWidth`, new icons,
  `GboCover` with four layouts (`duo`, `single`, `frame`, `split`)
- Covers: face choice (eyes open, intentional expression), record 3–4 s of "photo" per session, text that
  invites without revealing

## 0.1.0 — 2026-11-09
First public release. Extracted from the author's private editing skill after a pilot of
vertical reels and a two-camera long-form conversation.

- 10-phase workflow with checkpoints, model-per-phase guidance and deliverable versioning
- Local profile (`~/.config/gbo-video/`) for brand, glossary, style overrides and learnings
- First-use dependency check that asks before installing anything
- Production plan mode for scripts written here or in an external system
- Local transcription adapter for video-use (mlx-whisper, word timestamps)
- Render, audio and mix scripts with env-configurable paths
- Remotion template (captions, lower third, panels, reel, long form, cover, thumbnail)
- Optional Frameback review loop
- Optional web teleprompter for recording (bilingual README, Spanish first)
