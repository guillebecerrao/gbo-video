"""Reel de montaje musical (beat-synced): complemento de gbo_render.py, que está pensado para talking head.

    python edit/reel_render.py edit/edl.json --preview -o edit/reel_v1.mp4
    python edit/reel_render.py edit/edl.json -o edit/final_reel_v1.mp4
    python edit/reel_render.py edit/edl.json -o edit/final_reel_v1.mp4 --captions ass   # sin Remotion

Qué hace:
  - segmentos de voz (cortes por energía, cadena de limpieza) y de montaje: duración en beats con snap a la grilla
    de la música, velocidad por segmento o `src_span` (timelapse), audio ambiente con ganancia propia o mudo
  - música con licencia: intro opcional "apagada" (lowpass) que se abre en el drop, stop en un instante de un
    segmento (giro), outro con el final natural de la canción, ducking bajo la voz y bajadas puntuales
  - SFX ubicados por segmento o en el stop de la música
  - captions por energía: Whisper deriva 0.2–0.5 s en voz con ruido; se busca el desplazamiento que mejor calza las
    palabras con la envolvente del segmento (o se dan tiempos medidos a mano con `words`)
  - salida por Remotion (captions, tarjetas, zooms, flashes desde props) o, con --captions ass, captions quemadas
    con ffmpeg; además el sidecar <salida>.timeline.json para Frameback y work/timing.json con los tiempos resueltos

EDL (rutas relativas a la carpeta edit/, que por defecto es la del EDL):
{
  "fps": 24,
  "sources": "../RAW/{name}.mov",          # o {"C007": "../RAW/C007.mov", ...}: material del render final
  "proxies": "proxies/{name}.mp4",         # opcional (default = sources): video del preview y TODO el audio
  "voice_chain": "<filtro ffmpeg>",        # opcional; default: highpass + afftdn + presencia + compresión suave
  "color_chain": "<filtro ffmpeg>",        # opcional; conversión de fuente (HDR→SDR, LUT log), antes del grade
  "grade": "<filtro ffmpeg>",              # opcional; look
  "hflip": false,
  "music": {
    "file": "audio/tema.wav", "label": "Nombre del tema",   # label opcional (default: nombre del archivo)
    "bpm": 122, "phase": 0.2,              # phase: segundo del primer tiempo fuerte de un compás en el archivo
    "music_db": -10,
    "drop_at_segment": 2,                  # opcional: la canción arranca alineada al compás en este segmento;
    "muffled_lowpass_hz": 650,             #   antes suena apagada (si se da el lowpass) o normal
    "stop_at": {"segment": 14, "src_time": 7.62},   # opcional: corte seco de la música (se puede marcar con sfx)
    "outro_from_segment": 15, "outro_song_end": 169.2, # opcional: final natural de la canción bajo el cierre
    "end_fade": 1.0,                       # fade de la música al final del video si no hay stop ni outro
    "duck_db": -7, "duck_threshold_db": -38,
    "dips": [{"segment": 4, "db": -16, "start": 0, "end": 1.2}]
  },
  "segments": [
    {"label": "hook", "src": "C007", "in": 0.55, "out": 5.0, "audio": "voice", "captions": true,
     "caption_exclude": ["post"], "text_fix": {"he": "estaba"},
     "words": [{"text": "Bueno,", "start": 62.9, "end": 63.15}],   # opcional: tiempos medidos a mano
     "vsrc": "C018", "vin": 49.5},                                  # opcional: imagen de otra toma
    {"label": "montaje", "src": "C009", "in": 0.9, "beats": 4, "speed": 1.35, "audio": "amb", "gain_db": -14},
    {"label": "timelapse", "src": "C015", "in": 1.6, "beats": 8, "src_span": 18.6, "audio": "mute"}
  ],
  "emphasis": ["café"], "cta_word": "construyendo",
  "caption_style": {"paper_hex": "#FFFFFF", "paper_alpha": 0, "ink_hex": "#111111",
                    "accent_hex": "#4DA3FF", "cta_hex": "#FF8A3D", "font": "Inter", "size": 72},  # solo --captions ass
  "titles": [{"segment": 0, "dur": 2.0, "text": "..."}],                                    # solo --captions ass
  "sfx": [{"file": "audio/whoosh.wav", "segment": 3, "offset": -0.25, "db": -9},
          {"file": "audio/scratch.wav", "at_music_stop": true, "offset": -0.05, "db": -6,
           "from": 0.0, "dur": 1.0, "fade_out": 0.3}],
  "cards":   [{"segment": 2, "at": 0.1, "dur": 2.0, "kicker": "Misión", "title": "café", "side": "left"}],
  "zooms":   [{"segment": 4, "s0": 1.0, "s1": 1.18, "ox": 0.6, "oy": 0.55, "at": 0, "dur": 1.5}],
  "flashes": [{"segment": 4, "at": 1.68, "dur": 0.2, "peak": 0.75}],
  "remotion": {"composition": "MiReel", "props": {"captionY": 1340}}   # props extra para la composición
}
Segmentos con "beats" van después del drop (o en cualquier parte si no hay drop: la grilla parte en 0).

Remotion: la composición recibe {video, durationSec, captions, cards, zooms, flashes, ...remotion.props} y se
renderiza desde GBO_REMOTION_DIR, o $GBO_VIDEO_PROFILE/remotion, o la plantilla remotion/ de la skill.
Necesita chunk/norm/ass_time de gbo_render.py (misma carpeta) y numpy.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

_ff = os.environ.get("GBO_FFMPEG_DIR", "/opt/homebrew/opt/ffmpeg-full/bin")
if Path(_ff).is_dir():
    os.environ["PATH"] = _ff + os.pathsep + os.environ["PATH"]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gbo_render import chunk, norm, ass_time  # noqa: E402

SR = 48000
DEFAULT_VOICE_CHAIN = ("highpass=f=110,afftdn=nr=16:nf=-38:tn=1,"
                       "equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120")


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        sys.exit(f"falló:\n{' '.join(map(str, cmd))}\n{r.stderr.decode()[-2500:]}")
    return r


def load_audio(path, start=None, dur=None, mono=False, af=None):
    cmd = ["ffmpeg", "-v", "error"]
    if start is not None:
        cmd += ["-ss", f"{start:.4f}"]
    cmd += ["-i", str(path)]
    if dur is not None:
        cmd += ["-t", f"{dur:.4f}"]
    if af:
        cmd += ["-af", af]
    cmd += ["-vn", "-ac", "1" if mono else "2", "-ar", str(SR), "-f", "f32le", "-"]
    x = np.frombuffer(run(cmd).stdout, dtype=np.float32).copy()
    return x if mono else x.reshape(-1, 2)


def db(x):
    return 10 ** (x / 20)


def place(buf, x, t):
    i = int(round(t * SR))
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n]


def ass_color(h: str, alpha: int = 0) -> str:
    h = h.lstrip("#")
    return f"&H{alpha:02X}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def energy_shift(src_audio_mono, words, seg_in, seg_out):
    """Best shift (s) aligning Whisper word spans to the energy envelope of the segment."""
    hop = int(0.02 * SR)
    e = np.array([np.sqrt(np.mean(src_audio_mono[i:i + hop] ** 2) + 1e-12)
                  for i in range(0, len(src_audio_mono) - hop, hop)])
    if not len(e) or not words:
        return 0.0
    edb = 20 * np.log10(e)
    active = (edb > np.percentile(edb, 35) + 6).astype(float)
    best, best_s = -1, 0.0
    for s in np.arange(0.0, 0.81, 0.02):
        m = np.zeros_like(active)
        for w in words:
            a = int((w["start"] + s - seg_in) / 0.02)
            b = int((w["end"] + s - seg_in) / 0.02)
            m[max(a, 0):max(min(b, len(m)), 0)] = 1
        score = (m * active).sum() - 0.5 * (m * (1 - active)).sum()
        if score > best:
            best, best_s = score, float(s)
    return round(best_s, 2)


def source_resolver(spec, edit: Path, what: str):
    def resolve(name):
        if spec is None:
            sys.exit(f"el EDL necesita \"{what}\" (patrón con {{name}} o diccionario)")
        p = spec.format(name=name) if isinstance(spec, str) else spec.get(name)
        if p is None:
            sys.exit(f"\"{what}\" no tiene la fuente {name}")
        p = Path(p).expanduser()
        return p if p.is_absolute() else edit / p
    return resolve


def remotion_dir() -> Path:
    if os.environ.get("GBO_REMOTION_DIR"):
        return Path(os.environ["GBO_REMOTION_DIR"]).expanduser()
    if os.environ.get("GBO_VIDEO_PROFILE") and (Path(os.environ["GBO_VIDEO_PROFILE"]) / "remotion").is_dir():
        return Path(os.environ["GBO_VIDEO_PROFILE"]) / "remotion"
    return HERE.parent / "remotion"


def main():
    ap = argparse.ArgumentParser(description="Reel de montaje musical (beat-synced).")
    ap.add_argument("edl", type=Path)
    ap.add_argument("--preview", action="store_true", help="540×960, proxies, CRF 26")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--captions", choices=["remotion", "ass"], default="remotion",
                    help="remotion (default; también tarjetas, zooms y flashes) o ass (captions quemadas con ffmpeg)")
    ap.add_argument("--edit-dir", type=Path, help="carpeta edit/ del proyecto (default: la del EDL)")
    ap.add_argument("--work", type=Path, help="carpeta de intermedios (default: edit/work_preview|work_final)")
    a = ap.parse_args()

    edl = json.loads(a.edl.read_text())
    edit = (a.edit_dir or a.edl.resolve().parent).resolve()
    FPS = int(edl.get("fps", 24))
    W, H = (540, 960) if a.preview else (1080, 1920)
    work = (a.work or edit / ("work_preview" if a.preview else "work_final")).resolve()
    work.mkdir(parents=True, exist_ok=True)
    out = a.output.resolve()
    mus = edl["music"]
    bp = 60 / mus["bpm"]
    final_src = source_resolver(edl.get("sources"), edit, "sources")
    proxy_src = source_resolver(edl.get("proxies", edl.get("sources")), edit, "proxies")
    voice_chain = edl.get("voice_chain", DEFAULT_VOICE_CHAIN)
    look = ",".join(f for f in (edl.get("color_chain"), edl.get("grade")) if f)
    pre = "hflip," if edl.get("hflip") else ""

    def src_path(name):
        return proxy_src(name) if a.preview else final_src(name)

    # ---------- timing ----------
    segs = edl["segments"]
    drop = mus.get("drop_at_segment")
    t = 0.0
    T_m = None if drop is not None else 0.0
    for i, s in enumerate(segs):
        if i == drop:
            T_m = t
        if "beats" in s:
            if T_m is None:
                sys.exit("segmentos con beats deben ir después del drop")
            want = t + s["beats"] * bp
            n = round((want - T_m) / bp)
            end = T_m + n * bp
            if end - t < 0.5 * bp:
                end += bp
            frames = max(1, round((end - t) * FPS))
            dur = frames / FPS
            if "src_span" in s:
                s["speed"] = s["src_span"] / dur
            s.setdefault("speed", 1.0)
            s["out"] = s["in"] + dur * s["speed"]
        else:
            s.setdefault("speed", 1.0)
            frames = max(1, round((s["out"] - s["in"]) / s["speed"] * FPS))
            dur = frames / FPS
        s["_t0"], s["_dur"], s["_frames"] = t, dur, frames
        t += dur
    total = t
    print(f"duración total {total:.2f}s · música alineada en {T_m:.2f}s")

    # ---------- video segments ----------
    seg_files = []
    for i, s in enumerate(segs):
        p = work / f"seg_{i:02d}.mp4"
        span = s["_dur"] * s["speed"] + 0.2
        vf = (f"{pre}setpts=(PTS-STARTPTS)/{s['speed']:.5f},scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},setsar=1,{look + ',' if look else ''}fps={FPS}")
        enc = ["-c:v", "libx264", "-preset", "veryfast" if a.preview else "medium",
               "-crf", "26" if a.preview else "18", "-pix_fmt", "yuv420p"]
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s.get('vin', s['in']):.3f}", "-t", f"{span:.3f}",
             "-i", str(src_path(s.get("vsrc", s["src"]))), "-vf", vf, "-frames:v", str(s["_frames"]), "-an", *enc, str(p)])
        seg_files.append(p)
        print(f"  [{i:02d}] {s['_t0']:6.2f}s +{s['_dur']:.2f}  x{s['speed']:.2f}  {s['label']}", flush=True)
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in seg_files))
    base = work / "base.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])

    # ---------- audio stems ----------
    N = int(math.ceil(total * SR)) + SR
    voice = np.zeros((N, 2), np.float32)
    amb = np.zeros((N, 2), np.float32)
    fade = int(0.03 * SR)
    ramp = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
    for s in segs:
        if s["audio"] == "mute":
            continue
        src = proxy_src(s["src"])
        if s["audio"] == "voice":
            x = load_audio(src, s["in"], s["_dur"], af=voice_chain)
        else:
            af = f"atempo={s['speed']:.4f}" if abs(s["speed"] - 1) > 1e-3 else None
            x = load_audio(src, s["in"], s["_dur"] * s["speed"], af=af) * db(s.get("gain_db", -12))
        x = x[:int(s["_dur"] * SR)].copy()
        if len(x) > 2 * fade:
            x[:fade] *= ramp
            x[-fade:] *= ramp[::-1]
        place(voice if s["audio"] == "voice" else amb, x, s["_t0"])

    # ---------- music ----------
    song_file = edit / mus["file"]
    song_label = mus.get("label", Path(mus["file"]).stem)
    bar = 4 * bp
    k = math.ceil((T_m - mus.get("phase", 0.0)) / bar)
    S = mus.get("phase", 0.0) + k * bar - T_m          # segundo del archivo que suena en t=0 del video
    if mus.get("stop_at"):
        stop_seg = segs[mus["stop_at"]["segment"]]
        T_stop = stop_seg["_t0"] + (mus["stop_at"]["src_time"] - stop_seg["in"]) / stop_seg["speed"]
    else:
        T_stop = None
    T_c = segs[mus["outro_from_segment"]]["_t0"] if "outro_from_segment" in mus else None
    T_end = T_stop if T_stop is not None else (T_c if T_c is not None else total)
    song = load_audio(song_file, S, T_end + 0.2)
    music = np.zeros((N, 2), np.float32)
    iM, iE = int(T_m * SR), min(int(T_end * SR), len(song))
    music[:iE] = song[:iE]
    if drop is not None and mus.get("muffled_lowpass_hz"):
        lp = mus["muffled_lowpass_hz"]
        song_lp = load_audio(song_file, S, T_m + 0.2, af=f"lowpass=f={lp},lowpass=f={lp}") * db(-3)
        xf = int(0.12 * SR)
        music[:iM] = song_lp[:iM]
        music[iM - xf:iM] = (song_lp[iM - xf:iM] * np.linspace(1, 0, xf)[:, None] +
                             song[iM - xf:iM] * np.linspace(0, 1, xf)[:, None])
    if T_stop is not None:
        fo = int(0.06 * SR)
    elif T_c is not None:
        fo = int(0.25 * SR)
    else:
        fo = int(mus.get("end_fade", 1.0) * SR)
    music[iE - fo:iE] *= np.linspace(1, 0, fo)[:, None]
    fi0 = int(0.4 * SR)
    music[:fi0] *= np.linspace(0, 1, fi0)[:, None]
    if T_c is not None:
        Dc = total - T_c
        outro = load_audio(song_file, mus["outro_song_end"] - Dc, Dc)
        fi = int(0.25 * SR)
        outro[:fi] *= np.linspace(0, 1, fi)[:, None]
        place(music, outro, T_c)

    # ducking (sidechain sobre la voz)
    vm = np.abs(voice).mean(axis=1)
    hop = int(0.01 * SR)
    env = np.array([vm[i:i + hop].mean() for i in range(0, N, hop)])
    act = (20 * np.log10(env + 1e-9) > mus.get("duck_threshold_db", -38)).astype(float)
    g = np.zeros_like(act)
    for i in range(len(act)):  # attack 40 ms, release 450 ms
        prev = g[i - 1] if i else 0
        g[i] = prev + (act[i] - prev) * (0.25 if act[i] > prev else 0.022)
    duck = db(mus.get("duck_db", -7) * np.repeat(g, hop)[:N])
    music *= (duck * db(mus.get("music_db", -10)))[:, None]
    for dp in mus.get("dips", []):
        sg = segs[dp["segment"]]
        a0 = int((sg["_t0"] + dp.get("start", 0)) * SR)
        a1 = int((sg["_t0"] + dp.get("end", sg["_dur"])) * SR)
        r = int(0.15 * SR)
        g = np.ones(N, np.float32)
        g[a0:a1] = db(dp["db"])
        g[max(a0 - r, 0):a0] = np.linspace(1, db(dp["db"]), a0 - max(a0 - r, 0))
        g[a1:a1 + r] = np.linspace(db(dp["db"]), 1, len(g[a1:a1 + r]))
        music *= g[:, None]

    sfx = np.zeros((N, 2), np.float32)
    marks = []
    for fx in edl.get("sfx", []):
        if fx.get("at_music_stop") and T_stop is None:
            sys.exit("sfx con at_music_stop necesita music.stop_at")
        at = (T_stop if fx.get("at_music_stop") else segs[fx["segment"]]["_t0"]) + fx.get("offset", 0)
        x = load_audio(edit / fx["file"], fx.get("from"), fx.get("dur")) * db(fx.get("db", -10))
        if fx.get("fade_out"):
            n = int(fx["fade_out"] * SR)
            x[-n:] *= np.linspace(1, 0, n)[:, None]
        place(sfx, x, at)
        marks.append({"t": at, "label": Path(fx["file"]).stem})

    mix = voice * db(0) + amb + music + sfx
    mix = mix[:int(total * SR)]
    raw = work / "mix_raw.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    str(raw)], input=mix.astype(np.float32).tobytes(), check=True)
    # loudnorm dos pasadas (-14 LUFS / -1.5 dBTP)
    r = run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af",
             "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    txt = r.stderr.decode()
    m = json.loads(txt[txt.rfind("{"):txt.rfind("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    mixed = work / "mix.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", ln, "-ar", str(SR), str(mixed)])

    # ---------- captions ----------
    cst = edl.get("caption_style", {}) if isinstance(edl.get("caption_style"), dict) else {}
    PAPER = ass_color(cst.get("paper_hex", "#FFFFFF"), cst.get("paper_alpha", 0))
    INK = ass_color(cst.get("ink_hex", "#111111"))
    ACCENT = ass_color(cst.get("accent_hex", "#4DA3FF"))
    CTA = ass_color(cst.get("cta_hex", "#FF8A3D"))
    font, fsize = cst.get("font", "Inter"), cst.get("size", 72)
    emphasis = {norm(e) for e in edl.get("emphasis", [])}
    cta = norm(edl.get("cta_word", ""))
    used = set()
    events, cap_items, word_items, rchunks = [], [], [], []
    prev_closed = True
    for i, s in enumerate(segs):
        if not s.get("captions"):
            continue
        tr = json.loads((edit / "transcripts" / f"{s['src']}.json").read_text())
        excl = set(s.get("caption_exclude", []))
        words = [dict(w) for w in tr["words"] if w.get("type", "word") == "word"
                 and s["in"] - 0.6 <= w["start"] <= s["out"]]
        if "words" in s:   # tiempos manuales medidos en el audio (Whisper desfasado)
            words = [dict(w, type="word") for w in s["words"]]
            sh = 0.0
        else:
            src_mono = load_audio(proxy_src(s["src"]), s["in"], s["out"] - s["in"], mono=True)
            sh = energy_shift(src_mono, words, s["in"], s["out"])
        s["_cap_shift"] = sh
        words = [w for w in words if w["end"] + sh > s["in"] + 0.08 and w["start"] + sh < s["out"] - 0.05]
        for w in words:
            w["start"] += sh
            w["end"] += sh
        words = [w for w in words if w["text"].strip() not in excl]
        fixes = s.get("text_fix", {})
        for w in words:
            w["text"] = fixes.get(w["text"].strip(), w["text"])
        if not words:
            continue
        if prev_closed:
            w0 = words[0]["text"].strip()
            words[0]["text"] = w0[:1].upper() + w0[1:]

        def to_out(x, s=s):
            return s["_t0"] + min(max((x - s["in"]) / s["speed"], 0), s["_dur"])

        cks = chunk(words)
        seg_end = s["_t0"] + s["_dur"]
        for j, ck in enumerate(cks):
            st = to_out(ck[0]["start"])
            en = to_out(cks[j + 1][0]["start"]) if j + 1 < len(cks) else min(to_out(ck[-1]["end"]) + 0.3, seg_end)
            en = min(max(en, st + 0.4), seg_end)
            parts, hit, is_cta, eflags = [], False, False, []
            for w in ck:
                txt = w["text"].strip()
                key = norm(txt)
                if key == cta:
                    is_cta = True
                if not hit and key in emphasis and key not in used and key != cta:
                    parts.append(f"{{\\c{ACCENT}}}{txt}{{\\c{INK}}}")
                    used.add(key)
                    hit = True
                    eflags.append(True)
                else:
                    parts.append(txt)
                    eflags.append(False)
                word_items.append({"id": f"w:{i}:{len(word_items)}", "type": "word",
                                   "start": round(to_out(w["start"]), 3), "end": round(to_out(w["end"]), 3),
                                   "label": txt})
            text = " ".join(parts).rstrip(",;:.")
            style = "CTA" if is_cta else "Cap"
            events.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},{style},,0,0,0,,{{\\fad(80,0)}}{text}")
            rchunks.append({"start": round(st, 3), "end": round(en, 3), "cta": is_cta,
                            "words": [{"text": w["text"].strip().rstrip(",;:.") if k == len(ck) - 1 else w["text"].strip(),
                                       "start": round(to_out(w["start"]), 3), "end": round(to_out(w["end"]), 3),
                                       "emph": eflags[k]}
                                      for k, w in enumerate(ck)]})
            cap_items.append({"id": f"cap:{len(cap_items)}", "type": "caption", "start": round(st, 3),
                              "end": round(en, 3), "label": " ".join(w["text"].strip() for w in ck)})
        prev_closed = words[-1]["text"].rstrip()[-1:] in ".!?"

    for ti in edl.get("titles", []):
        st = segs[ti["segment"]]["_t0"]
        events.append(f"Dialogue: 1,{ass_time(st)},{ass_time(st + ti['dur'])},Title,,0,0,0,,"
                      f"{{\\fad(100,120)}}{ti['text']}")
    ass = work / "captions.ass"
    ass.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{fsize},{INK},{INK},{PAPER},&H00000000,-1,0,0,0,100,100,0,0,3,20,0,2,120,170,560,1
Style: CTA,{font},{fsize},{INK},{INK},{CTA},&H00000000,-1,0,0,0,100,100,0,0,3,20,0,2,120,170,560,1
Style: Title,{font},{round(fsize * 0.8)},{INK},{INK},{PAPER},&H00000000,-1,0,0,0,100,100,8,0,3,22,0,8,120,120,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n", encoding="utf-8")

    # ---------- final: audio mux + overlays ----------
    base_av = work / "base_av.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(base), "-i", str(mixed), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(base_av)])

    def seg_t(ref):
        return segs[ref["segment"]]["_t0"] + ref.get("at", 0)
    cards = [{"from": round(seg_t(c), 3), "to": round(seg_t(c) + c["dur"], 3), "kicker": c["kicker"],
              "title": c["title"], "side": c.get("side", "left")} for c in edl.get("cards", [])]
    zooms = []
    for zz in edl.get("zooms", []):
        sg = segs[zz["segment"]]
        a0 = sg["_t0"] + zz.get("at", 0)
        zooms.append({"from": round(a0, 3), "to": round(a0 + zz.get("dur", sg["_dur"] - zz.get("at", 0)), 3),
                      "s0": zz["s0"], "s1": zz["s1"], "ox": zz.get("ox", 0.5), "oy": zz.get("oy", 0.5)})
    flashes = [{"at": round(seg_t(f), 3), "dur": f.get("dur", 0.16), "peak": f.get("peak", 0.7)}
               for f in edl.get("flashes", [])]
    props = {"video": "base_av.mp4", "durationSec": round(total, 3), "fps": FPS, "captions": rchunks,
             "cards": cards, "zooms": zooms, "flashes": flashes}
    rem = edl.get("remotion", {})
    props.update(rem.get("props", {}))
    props_path = work / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False, indent=1))

    if a.captions == "ass":
        if cards or zooms or flashes:
            print("aviso: --captions ass ignora cards, zooms y flashes (solo Remotion)", file=sys.stderr)
        sub = str(ass).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(base_av), "-vf", f"subtitles='{sub}'",
             "-c:v", "libx264", "-preset", "veryfast" if a.preview else "medium",
             "-crf", "26" if a.preview else "18", "-pix_fmt", "yuv420p", "-c:a", "copy", str(out)])
    else:
        comp = rem.get("composition")
        if not comp:
            sys.exit("falta remotion.composition en el EDL (o usar --captions ass)")
        rdir = remotion_dir()
        cmd = ["npx", "remotion", "render", comp, str(out), f"--props={props_path}",
               f"--public-dir={work}", "--log=error"]
        cmd += ["--scale=0.5", "--crf=26"] if a.preview else ["--crf=18"]
        r = subprocess.run(cmd, cwd=rdir, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"remotion falló (en {rdir}):\n" + r.stderr[-3000:] + r.stdout[-2000:])

    # ---------- Frameback sidecar ----------
    cuts = [{"id": f"range:{i}", "type": "range", "start": round(s["_t0"], 3),
             "end": round(s["_t0"] + s["_dur"], 3),
             "label": f"{s['label']} · {s['src'][-4:]} {s['in']:.2f}–{s['out']:.2f}"
                      + (f" x{s['speed']:.2f}" if abs(s['speed'] - 1) > 1e-3 else ""),
             "source": {"name": s["src"], "start": round(s["in"], 3), "end": round(s["out"], 3)},
             "meta": {"audio": s["audio"], "speed": round(s["speed"], 3), "beats": s.get("beats"),
                      "captionShift": s.get("_cap_shift")}} for i, s in enumerate(segs)]
    trans = [{"id": f"cut:{i}", "type": "transition", "start": round(s["_t0"], 3),
              "label": f"cut range:{i - 1} → range:{i}"} for i, s in enumerate(segs) if i]
    music_items = []
    if drop is not None and mus.get("muffled_lowpass_hz") and T_m > 0:
        music_items.append({"id": "music:muffled", "type": "segment", "start": 0, "end": round(T_m, 3),
                            "label": "música apagada (lowpass)"})
    m0 = T_m if music_items else 0
    music_items.append({"id": "music:main", "type": "segment", "start": round(m0, 3), "end": round(T_end, 3),
                        "label": f"{song_label} · desde {S + m0:.2f}s"})   # segundo del archivo al entrar
    if T_c is not None:
        music_items.append({"id": "music:outro", "type": "segment", "start": round(T_c, 3), "end": round(total, 3),
                            "label": "outro canción"})
    sfx_items = [{"id": f"sfx:{j}", "type": "marker", "start": round(mk["t"], 3), "label": mk["label"]}
                 for j, mk in enumerate(marks)]
    fx_items = ([{"id": f"card:{j}", "type": "segment", "start": c["from"], "end": c["to"],
                  "label": f"{c['kicker']} · {c['title']}"} for j, c in enumerate(cards)] +
                [{"id": f"zoom:{j}", "type": "punch", "start": zz["from"], "end": zz["to"],
                  "label": f"zoom {zz['s0']}→{zz['s1']}"} for j, zz in enumerate(zooms)] +
                [{"id": f"flash:{j}", "type": "segment", "start": f["at"], "end": round(f["at"] + f["dur"], 3),
                  "label": "flash"} for j, f in enumerate(flashes)]) if a.captions == "remotion" else []
    tracks = [("cuts", "Cuts", "segments", cuts), ("transitions", "Transitions", "markers", trans),
              ("graphics", "Gráficos / efectos", "segments", fx_items),
              ("music", "Music", "segments", music_items), ("sfx", "SFX", "markers", sfx_items),
              ("captions", "Captions", "segments", cap_items), ("words", "Words", "segments", word_items)]
    side = {"schemaVersion": 1, "video": out.name, "duration": round(total, 3), "origin": "gbo-video",
            "tracks": [{"id": i, "label": l, "kind": k, "items": it} for i, l, k, it in tracks if it]}
    out.with_suffix(".timeline.json").write_text(json.dumps(side, ensure_ascii=False, indent=1))
    (work / "timing.json").write_text(json.dumps(segs, ensure_ascii=False, indent=1))
    print(f"caption shifts: {[s.get('_cap_shift') for s in segs if s.get('captions')]}")
    print(f"\nlisto: {out} ({total:.2f}s)")


if __name__ == "__main__":
    main()
