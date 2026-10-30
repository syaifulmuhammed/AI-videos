#!/usr/bin/env python3
"""Assemble an Instagram reel from a digital-twin video plus animated data cards.

  python3 tools/build_reel.py reels/01-ai-coach-intervals --twin twin.mp4 --auto-sync
  python3 tools/build_reel.py reels/01-ai-coach-intervals --placeholder   # preview without a twin

Steps: render cards (Playwright) -> write captions (.srt + .ass) -> ffmpeg composite.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PIP_SIZE = 300
PIP_POS = (60, 1190)
CAPTION_Y = 1110


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd[:6]), "..." if len(cmd) > 6 else "")
    return subprocess.run(cmd, check=True, **kw)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True).stdout
    return float(out.strip())


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout
    return bool(out.strip())


def beat_windows(tl, total=None):
    beats = tl["beats"]
    for i, b in enumerate(beats):
        nxt = beats[i + 1]["start"] if i + 1 < len(beats) else b.get("end", total)
        b["end"] = nxt if nxt is not None else b["start"] + 5
    if total is not None:
        beats[-1]["end"] = total
    return beats


def auto_sync(tl, twin):
    """Move beat starts onto the longest pauses in the twin's audio (one pause per beat boundary)."""
    res = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(twin), "-af", "silencedetect=noise=-35dB:d=0.3", "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", res.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", res.stderr)]
    gaps = [(e - s, s, e) for s, e in zip(starts, ends) if s > 0.5]
    need = len(tl["beats"]) - 1
    if len(gaps) < need:
        print(f"auto-sync: found {len(gaps)} pauses, need {need}; keeping timeline.json timings")
        return
    chosen = sorted(sorted(gaps, reverse=True)[:need], key=lambda g: g[1])
    for b, (_, s, e) in zip(tl["beats"][1:], chosen):
        b["start"] = round(max(s, e - 0.15), 2)
    print("auto-sync starts:", [b["start"] for b in tl["beats"]])


def caption_chunks(text, max_chars=24):
    words, chunks, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            chunks.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
        if cur.endswith((".", "?", "!")):
            chunks.append(cur)
            cur = ""
    if cur:
        chunks.append(cur)
    return chunks


def caption_events(beats):
    events = []
    for b in beats:
        chunks = caption_chunks(b["caption"])
        t0, t1 = b["start"] + 0.1, b["end"] - 0.25
        total = sum(len(c) + 6 for c in chunks)
        t = t0
        for c in chunks:
            d = (t1 - t0) * (len(c) + 6) / total
            events.append((t, t + d, c))
            t += d
    return events


def ts(t, sep):
    h, m = int(t // 3600), int(t % 3600 // 60)
    s = t % 60
    if sep == ",":
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
    return f"{h}:{m:02d}:{s:05.2f}"


def write_captions(events, srt_path, ass_path, tl):
    with open(srt_path, "w") as f:
        for i, (a, b, c) in enumerate(events, 1):
            f.write(f"{i}\n{ts(a, ',')} --> {ts(b, ',')}\n{c}\n\n")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {tl['width']}
PlayResY: {tl['height']}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display ExtraBold,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,7,0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ass_path, "w") as f:
        f.write(head)
        for a, b, c in events:
            f.write(f"Dialogue: 0,{ts(a, '.')},{ts(b, '.')},Cap,,0,0,0,,{{\\pos({tl['width'] // 2},{CAPTION_Y})}}{c}\n")


def make_pip_assets(build):
    s = PIP_SIZE
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse((2, 2, s - 3, s - 3), fill=255)
    mask.save(build / "pip_mask.png")
    ring = Image.new("RGBA", (s + 16, s + 16), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, s + 15, s + 15), outline=(198, 244, 50, 255), width=8)
    ring.save(build / "pip_ring.png")


def make_placeholder(build, tl, beats, total):
    """Stand-in for the twin: a still 'presenter' frame plus noise bursts shaped like speech with pauses."""
    w, h = tl["width"], tl["height"]
    img = Image.new("RGB", (w, h), (52, 60, 72))
    d = ImageDraw.Draw(img)
    for y in range(h):
        c = int(70 - 30 * y / h)
        d.line([(0, y), (w, y)], fill=(c, c + 8, c + 20))
    d.ellipse((380, 380, 700, 780), fill=(196, 150, 120))
    d.rounded_rectangle((200, 820, 880, 1920), radius=200, fill=(30, 36, 46))
    d.text((w // 2, 300), "YOUR DIGITAL TWIN HERE", fill=(255, 255, 255), anchor="mm", font_size=56)
    img.save(build / "placeholder.png")
    speech = "+".join(f"between(t,{b['start'] + 0.05:.2f},{b['end'] - 0.6:.2f})" for b in beats)
    out = build / "placeholder.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-framerate", str(tl["fps"]), "-i", build / "placeholder.png",
         "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude=0.25:d={total}",
         "-af", f"volume='if({speech},1,0)':eval=frame",
         "-t", str(total), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", out])
    return out


def export_broll(reel, tl, beats, manifest):
    out = reel / "broll"
    out.mkdir(exist_ok=True)
    for b in beats:
        m = manifest[b["card"]]
        dur = b["end"] - b["start"]
        hold = max(0.0, dur - m["frames"] / tl["fps"])
        src = reel / "build" / "cards" / b["card"] / "%04d.png"
        if m["layout"] == "full":
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(tl["fps"]), "-i", src,
                 "-vf", f"tpad=stop_mode=clone:stop_duration={hold:.2f}", "-c:v", "libx264", "-crf", "18",
                 "-pix_fmt", "yuv420p", out / f"{b['id']}.mp4"])
        else:
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(tl["fps"]), "-i", src,
                 "-vf", f"tpad=stop_mode=clone:stop_duration={hold:.2f}", "-c:v", "prores_ks", "-profile:v", "4444",
                 "-pix_fmt", "yuva444p10le", out / f"{b['id']}_overlay.mov"])


def compose(reel, tl, beats, twin, manifest, out_path, music, captions):
    build = reel / "build"
    W, H, fps = tl["width"], tl["height"], tl["fps"]
    total = beats[-1]["end"]
    pip = tl["pip"]
    crop = int(pip["size"] * W)
    cx = int(pip["center_x"] * W - crop / 2)
    cy = int(pip["center_y"] * H - crop / 2)

    inputs = ["-i", twin, "-loop", "1", "-i", build / "pip_mask.png", "-loop", "1", "-i", build / "pip_ring.png"]
    idx = 3
    fc = [
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},setsar=1,split=2[base0][pipsrc]",
        f"[pipsrc]crop={crop}:{crop}:max(0\\,min(iw-{crop}\\,{cx})):max(0\\,min(ih-{crop}\\,{cy})),scale={PIP_SIZE}:{PIP_SIZE},format=rgba[pipv]",
        f"[1:v]format=gray,scale={PIP_SIZE}:{PIP_SIZE}[pipm]",
        "[pipv][pipm]alphamerge[pipc]",
        "[2:v]format=rgba[ring]",
    ]
    last = "base0"
    full_windows = []
    for i, b in enumerate(beats):
        m = manifest[b["card"]]
        dur = b["end"] - b["start"]
        hold = max(0.0, dur - m["frames"] / fps)
        inputs += ["-framerate", str(fps), "-i", build / "cards" / b["card"] / "%04d.png"]
        en = f"between(t,{b['start']:.3f},{b['end']:.3f})"
        fc.append(f"[{idx}:v]format=rgba,tpad=stop_mode=clone:stop_duration={hold:.3f},setpts=PTS-STARTPTS+{b['start']:.3f}/TB[c{i}]")
        fc.append(f"[{last}][c{i}]overlay=0:0:enable='{en}':eof_action=pass[v{i}]")
        last = f"v{i}"
        idx += 1
        if m["layout"] == "full":
            full_windows.append(en)
    if full_windows:
        en = "+".join(full_windows)
        x, y = PIP_POS
        fc.append(f"[{last}][pipc]overlay={x}:{y}:enable='{en}':shortest=1[vp]")
        fc.append(f"[vp][ring]overlay={x - 8}:{y - 8}:enable='{en}':shortest=1[vr]")
        last = "vr"
    if captions:
        ass = str(build / "captions.ass").replace(":", "\\:")
        fc.append(f"[{last}]ass='{ass}'[vout]")
        last = "vout"

    amap = []
    if has_audio(twin):
        if music:
            inputs += ["-stream_loop", "-1", "-i", music]
            fc.append(f"[{idx}:a]volume=0.12[mus];[0:a][mus]amix=inputs=2:duration=first:normalize=0[aout]")
            amap = ["-map", "[aout]"]
        else:
            amap = ["-map", "0:a"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(fc), "-map", f"[{last}]", *amap,
         "-t", f"{total:.3f}", "-r", str(fps), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_path])
    print(f"wrote {out_path} ({total:.1f}s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reel", type=Path, help="reel folder containing data.json and timeline.json")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--twin", type=Path, help="9:16 video of your digital twin reading twin_script.txt")
    src.add_argument("--placeholder", action="store_true", help="build a preview with a stand-in presenter")
    ap.add_argument("--auto-sync", action="store_true", help="align beats to the pauses in the twin's audio")
    ap.add_argument("--music", type=Path, help="optional background track, mixed quietly under the voice")
    ap.add_argument("--no-captions", action="store_true", help="skip burned-in captions (captions.srt is still written)")
    ap.add_argument("--skip-render", action="store_true", help="reuse previously rendered cards")
    ap.add_argument("--export-broll", action="store_true", help="also export each card as a clip for CapCut/Premiere")
    ap.add_argument("--out", type=Path, help="output file (default <reel>/out/reel.mp4)")
    a = ap.parse_args()

    reel = a.reel.resolve()
    build = reel / "build"
    build.mkdir(exist_ok=True)
    tl = json.loads((reel / "timeline.json").read_text())

    manifest_path = build / "cards" / "manifest.json"
    if not a.skip_render or not manifest_path.exists():
        run(["node", ROOT / "tools" / "render_cards.js", reel])
    manifest = json.loads(manifest_path.read_text())

    if a.twin:
        twin = a.twin.resolve()
        if a.auto_sync:
            auto_sync(tl, twin)
        beats = beat_windows(tl, total=probe_duration(twin))
        out = a.out or reel / "out" / "reel.mp4"
    else:
        beats = beat_windows(tl)
        twin = make_placeholder(build, tl, beats, beats[-1]["end"])
        out = a.out or reel / "out" / "preview_placeholder.mp4"

    write_captions(caption_events(beats), reel / "captions.srt", build / "captions.ass", tl)
    make_pip_assets(build)
    compose(reel, tl, beats, twin, manifest, out.resolve(), a.music, not a.no_captions)
    if a.export_broll:
        export_broll(reel, tl, beats, manifest)


if __name__ == "__main__":
    sys.exit(main())
