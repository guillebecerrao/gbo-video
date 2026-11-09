"""Mix voice (from the rendered video) + ducked ambient music + SFX, then loudnorm.

    python edit/mix_audio.py <video_in> <video_out> [--music-db -11] [--sfx-db -12]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# ffmpeg with libass/drawtext: GBO_FFMPEG_DIR, or Homebrew's keg-only ffmpeg-full if present.
_ff = os.environ.get("GBO_FFMPEG_DIR", "/opt/homebrew/opt/ffmpeg-full/bin")
if Path(_ff).is_dir():
    os.environ["PATH"] = _ff + os.pathsep + os.environ["PATH"]
# video-use checkout (its helpers/render.py is reused): VIDEO_USE_DIR, default ~/Developer/video-use.
sys.path.insert(0, str(Path(os.environ.get("VIDEO_USE_DIR", Path.home() / "Developer/video-use")) / "helpers"))
import render  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_in", type=Path)
    ap.add_argument("video_out", type=Path)
    ap.add_argument("--music-db", type=float, default=-11.0)
    ap.add_argument("--sfx-db", type=float, default=-12.0)
    a = ap.parse_args()

    tmp = a.video_out.with_suffix(".premix.mp4")
    fc = (
        "[0:a]asplit=2[v][sc];"
        f"[1:a]volume={a.music_db}dB[mus];"
        # duck music under speech (~6 dB extra), smooth release so it breathes in pauses
        "[mus][sc]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=600[duck];"
        f"[2:a]volume={a.sfx_db}dB[fx];"
        "[v][duck][fx]amix=inputs=3:normalize=0:duration=first[mix]"
    )
    cmd = ["ffmpeg", "-y", "-i", str(a.video_in),
           "-i", str(HERE / "audio/music_ambient.wav"),
           "-i", str(HERE / "audio/sfx_track.wav"),
           "-filter_complex", fc, "-map", "0:v", "-map", "[mix]",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(tmp)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    render.apply_loudnorm_two_pass(tmp, a.video_out.resolve(), preview=False)
    tmp.unlink(missing_ok=True)
    print("done:", a.video_out)


if __name__ == "__main__":
    main()
