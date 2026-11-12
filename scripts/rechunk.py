"""Re-chunk captions at phrase boundaries.

`gbo_render.py` chunks captions by word count, which can cross a sentence end ("tarde. Así que ahí") or leave a
one-word chunk. This takes its `edit/captions.json` (same chunks, output timeline) plus a plain-text file with ONE CAPTION
CHUNK PER LINE, in spoken order, and writes new chunks with the original word timings (for Remotion props).

    python edit/rechunk.py edit/captions.json edit/frases.txt -o edit/captions_v2.json
    python edit/rechunk.py edit/captions.json --dump > edit/frases.txt   # start from the current chunks

Lines are matched word by word against the transcript (case, accents and trailing punctuation ignored), so the text
in the file can fix capitalization or punctuation but not the words themselves. On a mismatch it stops and shows
where. Emphasis flags (`emph`) are kept.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

TRAIL = ",;:."


def key(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.strip("¿?¡!" + TRAIL + "\"'«»")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("captions", type=Path, help="chunks JSON written by gbo_render.py (edit/captions.json)")
    ap.add_argument("phrases", type=Path, nargs="?", help="text file, one caption chunk per line")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--tail", type=float, default=0.6, help="hold of the last chunk after its last word (s)")
    ap.add_argument("--dump", action="store_true", help="print the current chunks as a phrases file and exit")
    a = ap.parse_args()

    chunks = json.loads(a.captions.read_text())
    words = [w for c in chunks for w in c["words"]]
    if a.dump:
        print("\n".join(" ".join(w["text"] for w in c["words"]) for c in chunks))
        return
    if not a.phrases or not a.output:
        ap.error("phrases and -o are required (or use --dump)")

    lines = [ln.split() for ln in a.phrases.read_text().splitlines() if ln.strip()]
    out, i = [], 0
    for n, line in enumerate(lines, 1):
        seg = words[i:i + len(line)]
        if [key(w["text"]) for w in seg] != [key(t) for t in line]:
            got = " ".join(w["text"] for w in words[i:i + len(line) + 2])
            sys.exit(f"line {n}: expected {' '.join(line)!r}, transcript has {got!r}")
        new = [dict(w, text=t.rstrip(TRAIL)) for w, t in zip(seg, line)]
        out.append({"start": round(seg[0]["start"], 3), "words": new})
        i += len(line)
    if i != len(words):
        rest = " ".join(w["text"] for w in words[i:i + 8])
        sys.exit(f"{len(words) - i} words left without a line, starting at {rest!r}")
    for k, c in enumerate(out):
        c["end"] = round(out[k + 1]["start"], 3) if k + 1 < len(out) else round(c["words"][-1]["end"] + a.tail, 3)

    a.output.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    singles = [" ".join(w["text"] for w in c["words"]) for c in out if len(c["words"]) == 1]
    print(f"{len(chunks)} → {len(out)} chunks → {a.output}")
    if singles:
        print("one-word chunks (fine if intended):", ", ".join(singles))


if __name__ == "__main__":
    main()
