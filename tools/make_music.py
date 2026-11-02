#!/usr/bin/env python3
"""Compose a short, original, royalty-free electronic bed for a reel.

  .venv/bin/python tools/make_music.py out.wav --duration 24.8 --drop 4.63

Everything is synthesised here (no samples), seeded so the same arguments give the same
file. Driving and minor (A minor, i-VI-III-VII), with a quiet intro that drops into the
full groove at --drop. The tempo is chosen so the drop lands exactly on a bar line.
"""
import argparse

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
RNG = np.random.default_rng(31)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=SR, output="sos"), x)


def hp(x, hz, order=2):
    return sosfilt(butter(order, hz, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * freq * (1 + detune)) % 1.0) - 1


def env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay)


def place(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    click = hp(RNG.standard_normal(n), 3000) * np.exp(-t / 0.003) * 0.18
    return np.tanh(1.6 * (body + click))


def clap():
    n = int(0.3 * SR)
    noise = bp(RNG.standard_normal(n), 900, 2600)
    e = np.zeros(n)
    for k, d in enumerate((0.0, 0.011, 0.022)):
        e += np.roll(env(n, 0.0005, 0.012 if k < 2 else 0.09), int(d * SR))
    return noise * e * 0.9


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    return hp(RNG.standard_normal(n), 8000, 4) * env(n, 0.0005, 0.07 if open_ else 0.016) * 0.32


def compose(duration, drop, bpm=None):
    # Pick a tempo near 104 so that the drop sits exactly on a bar line.
    bars_before = max(1, round(drop / (4 * 60 / 104)))
    bpm = bpm or 240 * bars_before / drop
    beat = 60 / bpm
    bar = 4 * beat
    n = int(duration * SR)
    drums, bass, music, pad, fx = (np.zeros(n) for _ in range(5))
    chords = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]  # Am F C G
    roots = [45, 41, 48, 43]
    K, C, H, O = kick(), clap(), hat(), hat(True)
    total_bars = int(np.ceil(duration / bar))

    for b in range(total_bars):
        t0 = b * bar
        ch, root = chords[b % 4], roots[b % 4]
        full = t0 >= drop - 1e-3
        # pad: three detuned saws per note, slow attack, the whole bar
        pn = int(bar * SR)
        p = sum(saw(midi(m), pn, d) for m in ch for d in (-0.004, 0.0, 0.005))
        p = lp(p, 1400 if full else 700) * np.minimum(1, np.arange(pn) / (0.25 * SR)) * np.exp(-np.arange(pn) / SR / 6)
        place(pad, p * (0.075 if full else 0.08), t0)
        for s in range(16):  # sixteenth-note grid
            t = t0 + s * beat / 4
            if t >= duration:
                break
            # plucked arpeggio: chord tones up an octave, then the root
            seq = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
            note = seq[s % 4]
            pl_n = int(0.22 * SR)
            pl = lp(saw(midi(note), pl_n) + 0.5 * np.sign(np.sin(2 * np.pi * midi(note) * np.arange(pl_n) / SR)), 2600 if full else 1500)
            place(music, pl * env(pl_n, 0.002, 0.07) * (0.16 if full else 0.09) * (1.15 if s % 4 == 0 else 1.0), t)
            if not full:
                if b == bars_before - 1 and s % 2 == 0:
                    place(drums, H * 0.6, t)  # hats creep in on the bar before the drop
                continue
            if s % 4 == 0:
                place(drums, K, t)
            if s in (4, 12):
                place(drums, C, t)
            if s % 2 == 0:
                place(drums, H * (0.9 if s % 4 == 2 else 0.6), t)
            if s % 4 == 2:
                place(drums, O * 0.5, t)
            if s % 2 == 0:  # driving eighth-note bass
                bn = int(beat / 2 * SR * 0.9)
                bs = lp(saw(midi(root), bn) + 0.6 * np.sin(2 * np.pi * midi(root - 12) * np.arange(bn) / SR), 520)
                place(bass, bs * env(bn, 0.003, 0.16) * 0.32, t)

    # Sidechain: duck pad, bass and plucks under every kick after the drop.
    duck = np.ones(n)
    k = 0.0
    while k < duration:
        if k >= drop - 1e-3:
            i = int(k * SR)
            m = int(beat * SR)
            curve = 1 - 0.55 * np.exp(-np.arange(m) / SR / 0.09)
            duck[i:i + m] = np.minimum(duck[i:i + m], curve[: len(duck[i:i + m])])
        k += beat

    # Riser into the drop: noise sweeping up over the last bar of the intro.
    r0 = max(0.0, drop - bar)
    rn = int((drop - r0) * SR)
    if rn > 0:
        ramp = np.linspace(0, 1, rn) ** 2
        noise = RNG.standard_normal(rn)
        hi = np.zeros(rn)
        steps = 24
        for s in range(steps):
            a, b2 = s * rn // steps, (s + 1) * rn // steps
            hi[a:b2] = bp(noise, 400 + 5000 * s / steps, 600 + 7000 * s / steps)[a:b2]
        place(fx, hi * ramp * 0.25, r0)
        place(drums, K * 1.1, drop)  # the downbeat of the drop
        place(fx, hp(RNG.standard_normal(int(0.8 * SR)), 2000) * env(int(0.8 * SR), 0.001, 0.25) * 0.25, drop)

    mix = drums + bass * duck + music * duck + pad * duck + fx
    # Fade the last 1.2 s, with a final hit on the last downbeat.
    fade = int(1.2 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade) ** 1.5
    mix = np.tanh(1.2 * mix) / np.tanh(1.2)
    stereo = np.stack([mix, np.roll(mix, int(0.0007 * SR))], axis=1)  # slight width
    stereo *= 0.89 / max(1e-9, np.abs(stereo).max())  # peak at -1 dBFS
    return stereo, bpm


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--drop", type=float, default=4.6, help="seconds where the full groove starts")
    ap.add_argument("--bpm", type=float, help="force a tempo (default: near 104, snapped to the drop)")
    a = ap.parse_args()
    audio, bpm = compose(a.duration, a.drop, a.bpm)
    wavfile.write(a.out, SR, (audio * 32767).astype(np.int16))
    print(f"wrote {a.out}: {a.duration:.2f}s at {bpm:.1f} BPM, drop at {a.drop:.2f}s")


if __name__ == "__main__":
    main()
