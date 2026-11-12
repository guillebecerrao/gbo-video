"""Mix voice (from the rendered video) + ducked music + SFX, then loudnorm.

    python edit/mix_audio.py <video_in> <video_out> [--music-db -11] [--sfx-db -12]
        [--music <track.wav>] [--music-offset 28.3] [--fade 1.2] [--no-sfx]

Music defaults to the synthesized edit/audio/music_ambient.wav (make_audio.py). With --music, a licensed track
is used instead: it starts at --music-offset (pick the section that matches the hook) and gets its own fade-out
that ends with the video, so the track's own ending never lands under the CTA. Library masters are loud
(~-9 LUFS): start around --music-db -14 and adjust by ear.
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
    ap.add_argument("--music", type=Path, help="external (licensed) music file instead of music_ambient.wav")
    ap.add_argument("--music-offset", type=float, default=0.0, help="seconds into the track where the video starts")
    ap.add_argument("--fade", type=float, default=1.2, help="own fade-out, ending with the video (s)")
    ap.add_argument("--no-sfx", action="store_true", help="mix without edit/audio/sfx_track.wav")
    a = ap.parse_args()

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(a.video_in)], capture_output=True, text=True).stdout)
    music = a.music or HERE / "audio/music_ambient.wav"
    sfx = HERE / "audio/sfx_track.wav"
    use_sfx = not a.no_sfx and sfx.exists()
    music_in = ["-ss", f"{a.music_offset:.3f}", "-i", str(music)] if a.music else ["-i", str(music)]
    mus_fx = f"afade=t=out:st={max(0.0, dur - a.fade):.3f}:d={a.fade},apad," if a.music else ""

    tmp = a.video_out.with_suffix(".premix.mp4")
    fc = (
        "[0:a]asplit=2[v][sc];"
        f"[1:a]{mus_fx}volume={a.music_db}dB[mus];"
        # duck music under speech (~6 dB extra), smooth release so it breathes in pauses
        "[mus][sc]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=600[duck];"
        + (f"[2:a]volume={a.sfx_db}dB[fx];[v][duck][fx]amix=inputs=3:normalize=0:duration=first[mix]"
           if use_sfx else "[v][duck]amix=inputs=2:normalize=0:duration=first[mix]")
    )
    cmd = ["ffmpeg", "-y", "-i", str(a.video_in), *music_in,
           *(["-i", str(sfx)] if use_sfx else []),
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
