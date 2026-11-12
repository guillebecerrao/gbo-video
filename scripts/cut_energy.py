"""Check cut points by audio energy (RMS), not by Whisper timestamps.

Whisper drifts 0.1–0.6 s at segment edges (more with wind or music), so cuts placed from its timestamps can clip a
syllable or leave too little air. This reads the source audio directly.

    python edit/cut_energy.py check edit/edl.json            # air before/after the voice in every range
    python edit/cut_energy.py islands <source> 12.0 20.5 --edl edit/edl.json   # speech islands in a span

`check` prints, per range, a strip of the energy around IN and OUT ('#' voice, '+' low, '.' silence; one char =
30 ms, centred on the cut) and the measured air: from IN to the first voiced frame, and from the last voiced frame
to OUT. It flags air below --min-air (default 0.15 s, see references/estilo.md § Ritmo y cortes) and voice touching
the cut. `islands` lists voiced stretches separated by gaps ≥ --gap, to find where a phrase really starts and ends.

Threshold: by default, each source's noise floor (10th percentile of its frames) + 10 dB, so it works with a quiet
lavalier and with a noisy location alike. --db fixes an absolute value instead (≈ -40 dBFS for lavalier in a quiet room).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

import numpy as np

_ff = os.environ.get("GBO_FFMPEG_DIR", "/opt/homebrew/opt/ffmpeg-full/bin")
if Path(_ff).is_dir():
    os.environ["PATH"] = _ff + os.pathsep + os.environ["PATH"]

SR, HOP = 16000, 160   # 10 ms frames


def envelope(src: Path) -> np.ndarray:
    """RMS in dBFS per 10 ms frame (mono 16 kHz, decoded with ffmpeg)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    n = len(x) // HOP
    x = x[:n * HOP].reshape(n, HOP)
    return 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)


def threshold(e: np.ndarray, db: float | None) -> float:
    return db if db is not None else float(np.percentile(e, 10)) + 10.0


def strip(e: np.ndarray, t: float, db: float) -> str:
    i = int(t * 100)
    seg = e[max(0, i - 60):i + 60:3]
    return "".join("#" if v > db else ("+" if v > db - 10 else ".") for v in seg)


def sources(edl_path: Path) -> dict[str, Path]:
    edl = json.loads(edl_path.read_text())
    base = edl_path.parent
    return {k: (Path(v) if Path(v).is_absolute() else (base / v)).resolve() for k, v in edl["sources"].items()}


def check(a: argparse.Namespace) -> None:
    edl = json.loads(a.edl.read_text())
    srcs, cache, bad = sources(a.edl), {}, 0
    for i, r in enumerate(edl["ranges"]):
        e = cache.setdefault(r["source"], envelope(srcs[r["source"]]))
        db = threshold(e, a.db)
        lo, hi = int(r["start"] * 100), int(r["end"] * 100)
        voiced = np.nonzero(e[lo:hi] > db)[0]
        if len(voiced) == 0:
            print(f"[{i:02d}] {r['source']} {r['start']:.2f}–{r['end']:.2f}  no voice above {db:.0f} dB")
            continue
        air_in, air_out = voiced[0] / 100, (hi - lo - 1 - voiced[-1]) / 100
        flags = [f"IN air {air_in:.2f}s" if air_in < a.min_air else "",
                 f"OUT air {air_out:.2f}s" if air_out < a.min_air else ""]
        flags = [f for f in flags if f]
        bad += bool(flags)
        print(f"[{i:02d}] {r['source']} {r['start']:6.2f}–{r['end']:6.2f}  air in {air_in:.2f} / out {air_out:.2f}"
              + (f"   ⚠ {'; '.join(flags)}" if flags else ""))
        if a.verbose or flags:
            print(f"      IN  {strip(e, r['start'], db)}   (threshold {db:.0f} dB)")
            print(f"      OUT {strip(e, r['end'], db)}")
    print(f"\n{bad} range(s) under {a.min_air:.2f} s of air" if bad else "\nall cuts have enough air")


def islands(a: argparse.Namespace) -> None:
    src = sources(a.edl)[a.source] if a.edl else Path(a.source)
    e = envelope(src)
    s = e[int(a.start * 100):int(a.end * 100)] > threshold(e, a.db)
    gap_frames, out, st, gap, en = int(a.gap * 100), [], None, 0, 0
    for i, v in enumerate(s):
        if v:
            st = i if st is None else st
            gap, en = 0, i
        elif st is not None:
            gap += 1
            if gap >= gap_frames:
                out.append((st, en))
                st = None
    if st is not None:
        out.append((st, en))
    print(" ".join(f"[{a.start + x / 100:.2f}-{a.start + y / 100 + 0.01:.2f}]" for x, y in out) or "no voice")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="air before/after the voice in every EDL range")
    c.add_argument("edl", type=Path)
    c.add_argument("--min-air", type=float, default=0.15)
    c.add_argument("-v", "--verbose", action="store_true", help="show energy strips for every range")
    s = sub.add_parser("islands", help="voiced stretches in a span of one source")
    s.add_argument("source", help="source key in the EDL (with --edl) or a media file path")
    s.add_argument("start", type=float)
    s.add_argument("end", type=float)
    s.add_argument("--edl", type=Path)
    s.add_argument("--gap", type=float, default=0.08, help="minimum silence that separates islands (s)")
    for p in (c, s):
        p.add_argument("--db", type=float, default=None, help="absolute voice threshold in dBFS (default: auto)")
    a = ap.parse_args()
    check(a) if a.cmd == "check" else islands(a)


if __name__ == "__main__":
    main()
