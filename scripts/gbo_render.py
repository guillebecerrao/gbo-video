"""GBO vertical render — project script on top of video-use helpers.

Adds what render.py doesn't cover for gbo-video:
  - punch-ins per range (hard cut 1.00 → punch_scale, via zoompan on `it`)
  - B-roll inserts (silent video over the talking head; voice continues)
  - ASS captions per estilo.md: 2–4 word chunks, sentence case, 1 emphasis word
    per chunk in an accent color, lower third inside the safe zone, 80 ms fade-in
Reuses render.py: concat_segments, build_final_composite (subtitles LAST),
apply_loudnorm_two_pass (-14 LUFS / -1 dBTP).

Usage (run with video-use's venv):
    python edit/gbo_render.py edit/edl.json --preview   # 540×960, fast
    python edit/gbo_render.py edit/edl.json             # 1080×1920 final
"""

from __future__ import annotations

import argparse
import json
import os
import re
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

FPS = "24"
def hex_to_ass(h: str) -> str:
    h = h.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}&".upper().replace("&H00", "&H00", 1)


# Defaults for burned-in captions; override per project in the EDL (caption_style.accent_hex) or via env.
ACCENT_ASS = hex_to_ass(os.environ.get("GBO_CAPTION_ACCENT", "#4DA3FF"))   # never yellow
FONT = os.environ.get("GBO_CAPTION_FONT", "Inter")  # must be installed system-wide (libass)
DANGLING = {"un", "una", "el", "la", "los", "las", "de", "del", "a", "al", "en", "y", "que",
            "su", "sus", "con", "por", "para", "o", "e", "se", "lo", "te", "mi"}


# ---------------------------------------------------------------- video ----

def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n{r.stderr[-2000:]}")


def encode_args(preview: bool) -> list[str]:
    if preview:
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"]
    return ["-c:v", "libx264", "-preset", "slow", "-crf", "18"]


def extract_range(src: Path, start: float, end: float, punches: list[list[float]],
                  scale: float, W: int, H: int, out: Path, preview: bool,
                  voice_chain: str = "") -> None:
    dur = end - start
    if punches:
        cond = "+".join(f"between(it,{a - start:.3f},{b - start:.3f})" for a, b in punches)
        vf = (f"scale={W * 2}:{H * 2},setsar=1,"
              f"zoompan=z='if({cond},{scale},1)':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*0.08'"
              f":d=1:s={W}x{H}:fps={FPS}")
    else:
        vf = f"scale={W}:{H},setsar=1"
    af = (voice_chain + "," if voice_chain else "") + f"afade=t=in:st=0:d=0.03,afade=t=out:st={max(0, dur - 0.03):.3f}:d=0.03"
    run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{dur:.3f}",
         "-vf", vf, "-af", af, *encode_args(preview), "-pix_fmt", "yuv420p", "-r", FPS,
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)])


def extract_broll(src: Path, start: float, dur: float, W: int, H: int, out: Path,
                  preview: bool) -> None:
    run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{dur:.3f}",
         "-vf", f"scale={W}:{H},setsar=1", "-an", *encode_args(preview),
         "-pix_fmt", "yuv420p", "-r", FPS, str(out)])


def probe_duration(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


# -------------------------------------------------------------- captions ----

def norm(w: str) -> str:
    return re.sub(r"[^\wáéíóúñü]", "", w.lower())


def chunk(words: list[dict]) -> list[list[dict]]:
    """2–4 words; break after punctuation or a ≥0.3 s pause; prefer 3."""
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        punct = w["text"].rstrip()[-1:] in ".,;:!?"
        pause = nxt is not None and nxt["start"] - w["end"] >= 0.3
        if nxt is None or len(cur) >= 4 or (len(cur) >= 2 and (punct or pause)) or \
                (len(cur) >= 3 and nxt is not None and len(nxt["text"]) > 9):
            chunks.append(cur)
            cur = []
    if cur:
        if chunks and len(cur) == 1 and len(chunks[-1]) < 4:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    # never end a chunk on a dangling function word ("…tienen un" / "…construyendo la")
    for i in range(len(chunks) - 1):
        while len(chunks[i]) > 1 and norm(chunks[i][-1]["text"]) in DANGLING \
                and len(chunks[i + 1]) < 5:
            chunks[i + 1].insert(0, chunks[i].pop())
    return [c for c in chunks if c]


def ass_time(t: float) -> str:
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(edl: dict, edit_dir: Path, seg_durs: list[float], out: Path) -> int:
    emphasis = {norm(e) for e in edl.get("emphasis", [])}
    cs = edl.get("caption_style", {})
    accent = hex_to_ass(cs["accent_hex"]) if cs.get("accent_hex") else ACCENT_ASS
    used: set[str] = set()
    events = []
    json_chunks = []   # same chunks, for Remotion (output-timeline seconds)
    offset = 0.0
    prev_closed = True
    for r, sdur in zip(edl["ranges"], seg_durs):
        tr = json.loads((edit_dir / "transcripts" / f"{r['source']}.json").read_text())
        lo, hi = r["caption_words"]
        words = [dict(w) for w in tr["words"] if w["type"] == "word" and lo <= w["start"] <= hi]
        if words and prev_closed:  # previous range ended a sentence → this one opens one
            words[0]["text"] = words[0]["text"].strip()[:1].upper() + words[0]["text"].strip()[1:]

        def to_out(t: float) -> float:
            return offset + min(max(t - r["start"], 0.0), sdur)

        cks = chunk(words)
        for i, ck in enumerate(cks):
            a = to_out(ck[0]["start"])
            b = to_out(cks[i + 1][0]["start"]) if i + 1 < len(cks) else to_out(ck[-1]["end"] + 0.25)
            b = max(b, a + 0.4)
            parts, hit, jw = [], False, []
            for w in ck:
                txt = w["text"].strip()
                key = norm(txt)
                emph = False
                if not hit and key in emphasis and key not in used:
                    parts.append(f"{{\\c{accent}}}{txt}{{\\c&H00FFFFFF&}}")
                    used.add(key)
                    hit = emph = True
                else:
                    parts.append(txt)
                jw.append({"text": txt, "start": round(to_out(w["start"]), 3),
                           "end": round(to_out(w["end"]), 3), "emph": emph})
            if jw:
                jw[-1]["text"] = jw[-1]["text"].rstrip(",;:.")
            json_chunks.append({"start": round(a, 3), "end": round(b, 3), "words": jw})
            text = " ".join(parts).rstrip(",;:.")
            text = re.sub(r"[,;:.](\{\\c&H00FFFFFF&\})$", r"\1", text)
            events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{{\\fad(80,0)}}{text}")
        prev_closed = bool(words) and words[-1]["text"].rstrip()[-1:] in ".!?"
        offset += sdur

    out.with_suffix(".json").write_text(json.dumps(json_chunks, indent=1, ensure_ascii=False))
    if cs.get("box"):   # BorderStyle 3 = opaque box; OutlineColour = box color, Outline = padding
        style_line = (f"Style: Cap,{FONT},70,&H00FFFFFF,&H00FFFFFF,&H50101010,&H00000000,"
                      "-1,0,0,0,100,100,0,0,3,18,0,2,120,160,540,1")
    else:
        style_line = (f"Style: Cap,{FONT},72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,"
                      "-1,0,0,0,100,100,0,0,1,0,3,2,120,160,540,1")
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_line}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    out.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return len(events)


# ------------------------------------------------------ frameback sidecar ----

def write_frameback_timeline(edl: dict, edit_dir: Path, seg_durs: list[float], out: Path,
                             captions_json: Path | None = None) -> Path:
    """Emit `<out stem>.timeline.json` (Frameback timeline sidecar, schemaVersion 1).

    Optional and additive: lets Frameback (local review UI, `npx frameback`) show cuts, transitions,
    speaker changes, B-roll, punch-ins, captions and words on its timeline with exact output times.
    Nothing in the render depends on it; failures are reported and ignored.
    """
    def dominant_speaker(words: list[dict]) -> str | None:
        counts: dict[str, int] = {}
        for w in words:
            sp = w.get("speaker_id")
            if sp:
                counts[sp] = counts.get(sp, 0) + 1
        return max(counts, key=counts.get) if counts else None

    cuts, transitions, motion, words_track, speakers = [], [], [], [], []
    offset, prev_speaker = 0.0, None
    for i, (r, sdur) in enumerate(zip(edl["ranges"], seg_durs)):
        tr_file = edit_dir / "transcripts" / f"{r['source']}.json"
        words = []
        if tr_file.exists():
            tr = json.loads(tr_file.read_text())
            words = [w for w in tr["words"] if w.get("type") == "word" and r["start"] <= w["start"] < r["end"]]
        to_out = lambda t: round(offset + min(max(t - r["start"], 0.0), sdur), 3)  # noqa: E731
        beat = r.get("beat", "")
        cuts.append({"id": f"range:{i}", "type": "range", "start": round(offset, 3), "end": round(offset + sdur, 3),
                     "label": f"{beat} · {r['source']} {r['start']:.2f}–{r['end']:.2f}".strip(" ·"),
                     "source": {"name": r["source"], "start": r["start"], "end": r["end"]},
                     "meta": {"beat": beat, "punch": r.get("punch", [])}})
        speaker = dominant_speaker(words)
        if i > 0:
            change = bool(speaker and prev_speaker and speaker != prev_speaker)
            gap_after = round(words[0]["start"] - r["start"], 3) if words else None
            transitions.append({"id": f"cut:{i}", "type": "transition", "start": round(offset, 3),
                                "label": f"cut range:{i - 1} → range:{i}" + (" · speaker change" if change else ""),
                                "meta": {"speakerChange": change, "gapAfter": gap_after}})
        for a, b in r.get("punch", []):
            motion.append({"id": f"punch:{i}:{a:.2f}", "type": "punch", "start": to_out(a), "end": to_out(b),
                           "label": f"punch-in x{edl.get('punch_scale', 1.08)}"})
        for k, w in enumerate(words):
            words_track.append({"id": f"w:{i}:{k}", "type": "word", "start": to_out(w["start"]), "end": to_out(w["end"]),
                                "label": w["text"].strip(), "meta": {"speaker": w.get("speaker_id")}})
        if speaker:
            if speakers and speakers[-1]["label"] == speaker:
                speakers[-1]["end"] = round(offset + sdur, 3)
            else:
                speakers.append({"id": f"spk:{i}", "type": "speaker", "start": round(offset, 3),
                                 "end": round(offset + sdur, 3), "label": speaker})
        prev_speaker = speaker or prev_speaker
        offset += sdur

    broll = [{"id": f"broll:{j}", "type": "broll", "start": b["start_in_output"],
              "end": round(b["start_in_output"] + b["duration"], 3),
              "label": f"{b['source']} {b['src_start']:.2f}s",
              "source": {"name": b["source"], "start": b["src_start"], "end": b["src_start"] + b["duration"]}}
             for j, b in enumerate(edl.get("broll", []))]

    captions = []
    if captions_json and captions_json.exists():   # chunks en tiempo de salida, escritos por build_ass
        for k, ck in enumerate(json.loads(captions_json.read_text())):
            captions.append({"id": f"cap:{k}", "type": "caption", "start": ck["start"], "end": ck["end"],
                             "label": " ".join(w["text"] for w in ck["words"])})

    tracks = [("cuts", "Cuts", "segments", cuts), ("transitions", "Transitions", "markers", transitions),
              ("speakers", "Speakers", "segments", speakers), ("motion", "Motion", "segments", motion),
              ("broll", "B-roll", "segments", broll), ("captions", "Captions", "segments", captions),
              ("words", "Words", "segments", words_track)]
    sidecar = {"schemaVersion": 1, "video": out.name, "duration": round(sum(seg_durs), 3), "origin": "gbo-video",
               "tracks": [{"id": i, "label": l, "kind": k, "items": it} for i, l, k, it in tracks if it]}
    path = out.with_suffix(".timeline.json")
    path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=1))
    return path


# ------------------------------------------------------------------ main ----

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("edl", type=Path)
    ap.add_argument("--preview", action="store_true", help="540×960 CRF 28")
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--no-timeline", action="store_true",
                    help="no escribir el sidecar <salida>.timeline.json (Frameback, opcional)")
    args = ap.parse_args()

    edl_path = args.edl.resolve()
    edit_dir = edl_path.parent
    edl = json.loads(edl_path.read_text())
    W, H = (540, 960) if args.preview else (1080, 1920)
    tag = "preview" if args.preview else "final"
    work = edit_dir / f"work_{tag}"
    work.mkdir(exist_ok=True)
    out = (args.output or edit_dir / f"{tag}_vertical.mp4").resolve()

    seg_paths, seg_durs = [], []
    for i, r in enumerate(edl["ranges"]):
        src = render.resolve_path(edl["sources"][r["source"]], edit_dir)
        p = work / f"seg_{i:02d}.mp4"
        print(f"  [{i:02d}] {r['beat']:<12} {r['source'][-4:]} {r['start']:6.2f}-{r['end']:6.2f}"
              f"{'  punch' if r.get('punch') else ''}", flush=True)
        extract_range(src, r["start"], r["end"], r.get("punch", []), edl.get("punch_scale", 1.08),
                      W, H, p, args.preview, edl.get("voice_chain", ""))
        seg_paths.append(p)
        seg_durs.append(probe_duration(p))

    base = work / "base.mp4"
    render.concat_segments(seg_paths, base, work)

    overlays = []
    for j, b in enumerate(edl.get("broll", [])):
        p = work / f"broll_{j}.mp4"
        extract_broll(render.resolve_path(edl["sources"][b["source"]], edit_dir),
                      b["src_start"], b["duration"], W, H, p, args.preview)
        overlays.append({"file": str(p), "start_in_output": b["start_in_output"],
                         "duration": b["duration"]})

    subs = None
    if not args.no_captions:
        subs = edit_dir / "captions.ass"
        n = build_ass(edl, edit_dir, seg_durs, subs)
        print(f"captions → {subs.name} ({n} cues)")

    render.SUB_FORCE_STYLE = "Alignment=2"   # keep our ASS style; render.py's default is Helvetica 18 caps
    tmp = out.with_suffix(".prenorm.mp4")
    render.build_final_composite(base, overlays, subs, tmp, edit_dir)
    render.apply_loudnorm_two_pass(tmp, out, preview=False)
    tmp.unlink(missing_ok=True)
    if not args.no_timeline:
        try:
            tl = write_frameback_timeline(edl, edit_dir, seg_durs, out,
                                          subs.with_suffix(".json") if subs else None)
            print(f"timeline → {tl.name} (Frameback, opcional)")
        except Exception as e:  # el sidecar nunca debe romper un render
            print(f"aviso: no se escribió el timeline de Frameback: {e}", file=sys.stderr)
    print(f"\ndone: {out}  ({sum(seg_durs):.2f}s, {out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
