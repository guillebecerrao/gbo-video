"""Build an SFX track from a cue list anchored to the Remotion props (or to plain seconds).

Each cue places one sound so that its transient ("peak") lands on a time of the output timeline. Anchors can point
into the props JSON ("titleCard.from", "splits.0.from", "end.clickAt"), so the SFX follow the graphics when the edit
is re-timed and the props are regenerated.

    python edit/sfx_track.py edit/sfx.json            # → edit/audio/sfx_track.wav (mono 48 kHz)

sfx.json (paths relative to that file):
    {
      "props": "remotion_props.json",      # optional: enables string anchors; its durationSec is the default length
      "duration": 49.74,                   # optional if props has durationSec
      "out": "audio/sfx_track.wav",        # default
      "cues": [
        {"sound": "whoosh", "at": "splits.0.from", "offset": 0.15},
        {"sound": "riser",  "at": "titleCard.from"},
        {"sound": "pop",    "at": "titleCard.from", "offset": 0.05},
        {"sound": "audio/typing.wav", "at": "end.typeAt", "dur": 0.85, "fade_out": 0.05, "db": -3.1},
        {"sound": "audio/click.wav",  "at": 45.6}
      ]
    }

Cue keys:
    sound     "whoosh" | "riser" | "pop" (synthesized by make_audio.py, license-free) or a path to any audio file
              (decoded with ffmpeg to mono 48 kHz, so stereo/44.1 kHz library files work as they come)
    at        seconds, or a dotted path into the props ("end.clickAt", "splits.1.from")
    offset    seconds added to `at` (default 0)
    peak      seconds inside the sound where its transient is (default: whoosh 0.30, riser = its length, pop/files 0)
    dur       keep only the first N seconds of the sound
    fade_out  seconds of linear fade at the end (after `dur`)
    db        gain after peak-normalizing every sound to 0.8 (default 0)
Synth sounds are generated in cue order with make_audio's fixed seed: the same cue list gives the same track.
Mix the result with mix_audio.py (it reads edit/audio/sfx_track.wav).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

_ff = os.environ.get("GBO_FFMPEG_DIR", "/opt/homebrew/opt/ffmpeg-full/bin")
if Path(_ff).is_dir():
    os.environ["PATH"] = _ff + os.pathsep + os.environ["PATH"]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_audio as ma  # noqa: E402

SR = ma.SR
SYNTH = {"whoosh": (ma.whoosh, 0.30), "pop": (ma.pop, 0.0), "riser": (ma.riser, None)}  # None → peak at the end


def resolve(anchor, props: dict | None) -> float:
    if isinstance(anchor, (int, float)):
        return float(anchor)
    if props is None:
        sys.exit(f"ancla '{anchor}' necesita \"props\" en el archivo de cues")
    node = props
    for k in str(anchor).split("."):
        try:
            node = node[int(k)] if isinstance(node, list) else node[k]
        except (KeyError, IndexError, ValueError):
            sys.exit(f"ancla '{anchor}': no existe '{k}' en los props")
    return float(node)


def load_file(path: Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        sys.exit(f"no se pudo leer {path}:\n{r.stderr.decode()[-800:]}")
    return np.frombuffer(r.stdout, dtype=np.float32).astype(float)


def build(spec: dict, base: Path) -> tuple[np.ndarray, list[tuple[str, float]]]:
    props = json.loads((base / spec["props"]).read_text()) if spec.get("props") else None
    total = spec.get("duration") or (props or {}).get("durationSec")
    if not total:
        sys.exit("falta \"duration\" (o \"props\" con durationSec)")
    track = np.zeros(int(float(total) * SR))
    placed = []
    for c in spec["cues"]:
        name = c["sound"]
        if name in SYNTH:
            fn, peak = SYNTH[name]
            x = np.asarray(fn(), float)
            peak = len(x) / SR if peak is None else peak
        else:
            x, peak = load_file(base / name), 0.0
        peak = c.get("peak", peak)
        if c.get("dur"):
            x = x[:int(c["dur"] * SR)]
        if c.get("fade_out"):
            n = min(int(c["fade_out"] * SR), len(x))
            x = x * np.r_[np.ones(len(x) - n), np.linspace(1, 0, n)]
        m = np.max(np.abs(x))
        if m > 0:
            x = x / m * 0.8
        x = x * 10 ** (c.get("db", 0) / 20)
        at = resolve(c["at"], props) + c.get("offset", 0)
        i = int((at - peak) * SR)
        if i < 0:
            x, i = x[-i:], 0
        n = min(len(x), len(track) - i)
        if n > 0:
            track[i:i + n] += x[:n]
        placed.append((Path(name).stem, round(at, 2)))
    return track, placed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cues", type=Path, help="sfx.json")
    ap.add_argument("-o", "--output", type=Path, help="default: \"out\" of the cue file, or audio/sfx_track.wav")
    a = ap.parse_args()
    base = a.cues.resolve().parent
    spec = json.loads(a.cues.read_text())
    track, placed = build(spec, base)
    out = (a.output or base / spec.get("out", "audio/sfx_track.wav")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    ma.write(out, track)
    print("sfx:", ", ".join(f"{n}@{t}" for n, t in placed))
    print(f"listo: {out} ({len(track) / SR:.2f}s)")


if __name__ == "__main__":
    main()
