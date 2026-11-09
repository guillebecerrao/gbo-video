"""Synthesize an ad-hoc ambient bed + 4 SFX for the pilot (license-free: generated here).

Outputs (48 kHz mono WAV, float → 16-bit):
  edit/audio/music_ambient.wav   — soft pad + sparse bell tones, fades in/out
  edit/audio/sfx_track.wav       — SFX placed on the output timeline
  edit/audio/sfx_*.wav           — individual one-shots (reusable library seeds)

SFX placement follows estilo.md: only on graphic appearances/reveal, same family,
≤ 3–5 per minute.
"""

from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
rng = np.random.default_rng(7)
OUT = Path(__file__).resolve().parent / "audio"


def write(path: Path, x: np.ndarray) -> None:
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def lp(x, f, order=4):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def reverb(x, seconds=2.8, wet=0.35):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = fftconvolve(x, ir)[: len(x)]
    return (1 - wet) * x + wet * y


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------------ music ----

def pad_voice(freq, dur):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for det in (-0.12, 0.0, 0.11):           # slight detune chorus (cents-ish)
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * np.pi)
        x += np.sin(2 * np.pi * f * t + ph) + 0.25 * np.sin(4 * np.pi * f * t + ph)
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t + rng.uniform(0, 6))
    return x * lfo / 3


def music(total):
    # Dmaj9 → Bm9 → Gmaj9 → Asus2, 6 s each, overlapping swells
    chords = [[50, 57, 62, 66, 69, 76], [47, 54, 62, 66, 69, 73],
              [43, 50, 59, 62, 66, 69], [45, 52, 59, 61, 64, 71]]
    seg = 6.0
    y = np.zeros(int((total + 12) * SR))
    k, start = 0, 0.0
    while start < total:
        notes = chords[k % len(chords)]
        dur = seg + 2.5
        env_t = np.linspace(0, 1, int(dur * SR))
        env = np.minimum(env_t / 0.35, 1) * np.minimum((1 - env_t) / 0.35, 1)
        env = np.clip(env, 0, 1) ** 1.5
        chord = sum(pad_voice(midi(n), dur) * (0.6 if n < 48 else 1.0) for n in notes)
        a = int(start * SR)
        y[a:a + len(chord)] += chord * env
        # sparse bell tones from the chord, upper register
        for b in range(3):
            bt = start + 0.6 + b * 2.0 + rng.uniform(-0.2, 0.2)
            f = midi(rng.choice(notes[3:]) + 12)
            n = int(2.5 * SR)
            tt = np.arange(n) / SR
            bell = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2.01 * f * tt)) \
                * np.exp(-tt * 2.2) * 0.35
            i = int(bt * SR)
            y[i:i + n] += bell[: max(0, min(n, len(y) - i))]
        start += seg
        k += 1
    y = y[: int(total * SR)]
    y = hp(lp(y, 3200), 60)
    y = reverb(y, 3.2, 0.45)
    fade_in, fade_out = int(1.5 * SR), int(2.5 * SR)
    y[:fade_in] *= np.linspace(0, 1, fade_in)
    y[-fade_out:] *= np.linspace(1, 0, fade_out)
    return 0.5 * y / np.max(np.abs(y))


# -------------------------------------------------------------------- sfx ----

def whoosh(dur=0.55):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    # time-varying one-pole lowpass: cutoff sweeps 300 Hz → 4 kHz → 1 kHz
    fc = 300 + 3700 * np.sin(np.pi * np.minimum(t * 1.3, 1)) ** 2
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty(n); s = 0.0
    for i in range(n):
        s = a[i] * s + (1 - a[i]) * noise[i]
        y[i] = s
    env = np.sin(np.pi * t) ** 2
    return reverb(hp(y * env, 150), 0.8, 0.25) / 0.35 * 0.5


def pop(dur=0.12):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 950 * np.exp(-tt * 18) + 280
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-tt * 38)
    return reverb(y, 0.5, 0.2) * 0.8


def riser(dur=1.2):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    tt = np.arange(n) / SR
    f = 220 * 2 ** (2.3 * t)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    noise = hp(rng.standard_normal(n), 800) * 0.5
    y = (tone + noise * t) * (t ** 2.2)
    y[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR))
    return lp(reverb(y, 1.0, 0.3), 6000) * 0.6


def main():
    props = json.loads((Path(__file__).parent / "remotion_props.json").read_text())
    total = float(props["durationSec"])
    OUT.mkdir(exist_ok=True)

    m = music(total)
    write(OUT / "music_ambient.wav", m)

    shots = {"whoosh": whoosh(), "pop": pop(), "riser": riser()}
    for k, v in shots.items():
        write(OUT / f"sfx_{k}.wav", v / np.max(np.abs(v)) * 0.8)

    # placement: (name, time the transient/peak should land, peak offset inside the file)
    sp = props["splits"]; tc = props["titleCard"]
    cues = [("whoosh", sp[0]["from"] + 0.15, 0.30), ("whoosh", sp[1]["from"] + 0.15, 0.30),
            ("riser", tc["from"], 1.2), ("pop", tc["from"] + 0.05, 0.0)]
    track = np.zeros(int(total * SR))
    for name, at, peak in cues:
        x = shots[name] / np.max(np.abs(shots[name])) * 0.8
        i = int((at - peak) * SR)
        track[i:i + len(x)] += x[: len(track) - i]
    write(OUT / "sfx_track.wav", track)
    print("cues:", [(c[0], round(c[1], 2)) for c in cues])
    print("written:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    sys.exit(main())
