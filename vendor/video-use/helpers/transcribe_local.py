"""Transcribe videos locally (Apple Silicon, no API key). Two engines:

  - whisper  (default) mlx-whisper + whisper-large-v3-turbo, language forced
             to Spanish, word timestamps. Recommended for GBO.
  - parakeet parakeet-mlx + Parakeet TDT 0.6B v3. Very fast, but it auto-detects
             language and on Spanish with English tech terms it drifts into
             English / translates (tested 2026-11-05). Kept for comparison.

Drop-in replacement for transcribe.py / transcribe_batch.py that needs no
ElevenLabs key. Writes the SAME schema Scribe produced, so pack_transcripts.py,
timeline_view.py and render.py work unchanged:

    {"language_code": "es", "text": "...", "engine": "parakeet-tdt-0.6b-v3",
     "words": [
        {"text": "Hola", "start": 0.12, "end": 0.40, "type": "word",
         "speaker_id": "speaker_0", "logprob": -0.03},
        {"text": " ", "start": 0.40, "end": 0.55, "type": "spacing",
         "speaker_id": "speaker_0"},
        ...
     ]}

Differences vs. Scribe (by design):
  - Single speaker: every word is speaker_0 (no diarization).
  - No audio events ((laughs), (applause)...).
  - Both engines tend to drop filler sounds ("eh", "mm") that Scribe kept verbatim.
    Silence gaps still show up as spacing entries, so cut detection works.

Cached per output file, same paths as transcribe.py (edit/transcripts/<stem>.json).
Kept as a separate file so video-use can still be updated from upstream.

Usage:
    python helpers/transcribe_local.py <video_or_dir> [more ...]
    python helpers/transcribe_local.py <video> --clip 0 30 -o /tmp/test.json   # quick test
    python helpers/transcribe_local.py <videos_dir> --edit-dir /custom/edit
    python helpers/transcribe_local.py <video> --engine parakeet
    python helpers/transcribe_local.py <videos_dir> --prompt "Claude Code, Remotion, prompt"
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transcribe import count_audio_tracks, extract_audio, peak_dbfs, transcript_path  # noqa: E402

MODEL_ID = "mlx-community/parakeet-tdt-0.6b-v3"
WHISPER_ID = "mlx-community/whisper-large-v3-turbo"
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".m4v"}
CONTROL_TOKEN = re.compile(r"<unk>|<pad>|<\|[^|>]*\|>")
CHUNK_S = 120.0     # long takes are processed in 2-min windows
OVERLAP_S = 15.0

_model = None


def get_model():
    global _model
    if _model is None:
        from parakeet_mlx import from_pretrained
        print(f"loading {MODEL_ID} (first run downloads ~2.5 GB)", flush=True)
        _model = from_pretrained(MODEL_ID)
    return _model


def tokens_to_words(tokens) -> list[dict]:
    """Merge Parakeet sub-word tokens into words.

    A token whose text starts with a space opens a new word; anything else
    (word pieces, punctuation) is glued to the current word.
    """
    words: list[dict] = []
    cur: dict | None = None
    for t in tokens:
        text = t.text
        if not text or CONTROL_TOKEN.fullmatch(text.strip()):
            continue
        if cur is None or text.startswith(" "):
            if cur is not None:
                words.append(cur)
            cur = {"text": text.strip(), "start": t.start, "end": t.end, "confs": [t.confidence]}
        else:
            cur["text"] += text
            cur["end"] = max(cur["end"], t.end)
            cur["confs"].append(t.confidence)
    if cur is not None:
        words.append(cur)
    return [w for w in words if w["text"]]


def to_scribe_schema(result, offset: float = 0.0) -> dict:
    import math
    words = tokens_to_words(result.tokens)
    out: list[dict] = []
    prev_end: float | None = None
    for w in words:
        start = round(w["start"] + offset, 3)
        end = round(w["end"] + offset, 3)
        if prev_end is not None and start > prev_end:
            out.append({"text": " ", "start": prev_end, "end": start,
                        "type": "spacing", "speaker_id": "speaker_0"})
        conf = min(w["confs"]) if w["confs"] else 1.0
        out.append({"text": w["text"], "start": start, "end": end, "type": "word",
                    "speaker_id": "speaker_0",
                    "logprob": round(math.log(max(conf, 1e-6)), 4)})
        prev_end = end
    return {
        "language_code": "es",
        "language_probability": None,
        "text": result.text,
        "engine": "parakeet-tdt-0.6b-v3",
        "words": out,
    }


def whisper_wav(wav: Path, offset: float, language: str, prompt: str | None) -> dict:
    import math
    import mlx_whisper
    r = mlx_whisper.transcribe(
        str(wav), path_or_hf_repo=WHISPER_ID, language=language,
        word_timestamps=True, condition_on_previous_text=False,
        initial_prompt=prompt, hallucination_silence_threshold=2.0,
    )
    out: list[dict] = []
    prev_end: float | None = None
    for seg in r.get("segments", []):
        for w in seg.get("words", []):
            text = (w.get("word") or "").strip()
            if not text:
                continue
            start = round(w["start"] + offset, 3)
            end = round(max(w["end"], w["start"]) + offset, 3)
            if prev_end is not None and start > prev_end:
                out.append({"text": " ", "start": prev_end, "end": start,
                            "type": "spacing", "speaker_id": "speaker_0"})
            out.append({"text": text, "start": start, "end": end, "type": "word",
                        "speaker_id": "speaker_0",
                        "logprob": round(math.log(max(w.get("probability", 1.0), 1e-6)), 4)})
            prev_end = max(end, prev_end or end)
    return {"language_code": language, "language_probability": None,
            "text": (r.get("text") or "").strip(),
            "engine": "whisper-large-v3-turbo", "words": out}


def transcribe_wav(wav: Path, offset: float = 0.0, engine: str = "whisper",
                   language: str = "es", prompt: str | None = None) -> dict:
    if engine == "whisper":
        return whisper_wav(wav, offset, language, prompt)
    model = get_model()
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
        capture_output=True, text=True).stdout.strip() or 0)
    kwargs = {}
    if dur > CHUNK_S:
        kwargs = {"chunk_duration": CHUNK_S, "overlap_duration": OVERLAP_S}
    result = model.transcribe(str(wav), **kwargs)
    return to_scribe_schema(result, offset)


def transcribe_video(video: Path, out_path: Path, audio_track: int = 0,
                     clip: tuple[float, float] | None = None, engine: str = "whisper",
                     language: str = "es", prompt: str | None = None) -> Path:
    if out_path.exists():
        print(f"cached: {out_path.name}")
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_tracks = count_audio_tracks(video)
    if n_tracks > 1:
        print(f"  note: {video.name} has {n_tracks} audio tracks, using track {audio_track + 1}")
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{video.stem}.wav"
        if clip:
            src = Path(tmp) / "clip.wav"
            extract_audio(video, src, audio_track)
            subprocess.run(["ffmpeg", "-y", "-ss", str(clip[0]), "-t", str(clip[1] - clip[0]),
                            "-i", str(src), "-c:a", "pcm_s16le", str(wav)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            extract_audio(video, wav, audio_track)
        peak = peak_dbfs(wav)
        if peak < -60.0:
            raise RuntimeError(f"audio track {audio_track + 1} of {video.name} is silent "
                               f"(peak {peak:.1f} dBFS)")
        payload = transcribe_wav(wav, offset=clip[0] if clip else 0.0, engine=engine,
                                 language=language, prompt=prompt)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    n = sum(1 for w in payload["words"] if w["type"] == "word")
    print(f"  saved: {out_path.name}  ({n} words, {time.time() - t0:.1f}s)", flush=True)
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Local transcription, Whisper or Parakeet (Scribe-compatible JSON)")
    ap.add_argument("inputs", type=Path, nargs="+", help="Video files and/or directories")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output dir (default: <first input's folder>/edit)")
    ap.add_argument("--audio-track", type=int, default=0)
    ap.add_argument("--engine", choices=["whisper", "parakeet"], default="whisper")
    ap.add_argument("--language", default="es", help="Whisper only (default: es)")
    ap.add_argument("--prompt", default=None,
                    help="Whisper only: vocabulary hint, e.g. brand names and English terms")
    ap.add_argument("--clip", type=float, nargs=2, metavar=("START", "END"),
                    help="Only transcribe this range (testing). Requires -o.")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Explicit output JSON (single video only)")
    args = ap.parse_args()

    videos: list[Path] = []
    for p in args.inputs:
        p = p.resolve()
        if p.is_dir():
            videos += sorted(v for v in p.iterdir() if v.is_file() and v.suffix.lower() in VIDEO_EXTS)
        elif p.is_file():
            videos.append(p)
        else:
            sys.exit(f"not found: {p}")
    if not videos:
        sys.exit("no videos found")
    if (args.clip or args.output) and len(videos) != 1:
        sys.exit("--clip / -o work with exactly one video")
    if args.clip and not args.output:
        sys.exit("--clip requires -o (a partial transcript must not land in the cache)")

    edit_dir = (args.edit_dir or (videos[0].parent / "edit")).resolve()
    t0 = time.time()
    errors = []
    for i, v in enumerate(videos, 1):
        out = args.output.resolve() if args.output else transcript_path(edit_dir, v, args.audio_track)
        print(f"[{i}/{len(videos)}] {v.name}", flush=True)
        try:
            transcribe_video(v, out, args.audio_track, tuple(args.clip) if args.clip else None,
                             engine=args.engine, language=args.language, prompt=args.prompt)
        except Exception as e:  # keep going on the rest of the batch
            errors.append((v.name, str(e)))
            print(f"  x FAILED: {e}", flush=True)
    print(f"\ndone in {time.time() - t0:.1f}s")
    if errors:
        for name, msg in errors:
            print(f"  {name}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
