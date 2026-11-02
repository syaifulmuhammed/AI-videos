#!/usr/bin/env python3
"""Assemble a reel's HyperFrames project from its timeline, data and twin video, then render.

  python3 tools/hf_reel.py reels/01-ai-coach-intervals --twin twin.mp4 --auto-sync --render
  python3 tools/hf_reel.py reels/01-ai-coach-intervals --placeholder --render
  python3 tools/hf_reel.py reels/01-ai-coach-intervals --voice am_michael --render

The scenes in <reel>/hyperframes/compositions/ are hand-written and never touched here.
This script writes only the parts that follow from data: assets/twin.mp4 or
assets/narration.wav, index.html (scene timings, the numbers each scene shows, the twin's
move into the bubble) and compositions/captions.html.

With --voice there is no presenter: a local Kokoro voice reads each beat's `say` line,
every card fills the screen, and each beat lasts exactly as long as its line.
"""
import argparse
import hashlib
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_reel import auto_sync, beat_windows, caption_events, make_placeholder, probe_duration, run  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HF = ROOT / "node_modules" / ".bin" / "hyperframes"
SFX_DIR = ROOT / ".claude" / "skills" / "media-use" / "audio" / "assets" / "sfx"
BUBBLE = (200, 1470, 130)  # centre x, centre y, radius of the twin bubble over full-screen cards
LAYOUT = {"hook": "overlay", "cta": "overlay"}  # every other scene is a full-screen card
VOICE_LEAD, VOICE_GAP, VOICE_TAIL = 0.15, 0.45, 1.6  # seconds before the first line, between lines, after the last
PUNCH_IN = (2.75, 1.08)  # hard punch-in on the twin at "Five days before my race": time, scale
# Sound effects on visible actions, from the HyperFrames media-use library (Pixabay licence):
# (seconds after the scene starts, file in assets/sfx, volume). Kept well under the voice.
SFX = {
    "hook": [(0.05, "impact-bass-1", 0.35)],
    "pipeline": [(0.0, "whoosh", 0.3), (4.85, "pop", 0.4)],
    "coach": [(2.2, "pop", 0.25)],
    "week": [(8.25, "ping", 0.3)],
    "verdict": [(7.6, "chime", 0.3)],
    "gains": [(3.05, "sparkle", 0.3)],
    "cta": [(-0.6, "whoosh-short", 0.3), (2.6, "pop", 0.45)],  # voiceover cards move the pop to 3.6 (see sfx_tags)
}


def scene_values(data):
    race, load, gains, coach = data["race"], data["load"], data["power_gains"], data["coach"]
    hour, second = gains["items"][0], gains["items"][1]
    line1, _, line2 = coach["directive"].partition(". ")
    return {
        "hook": {"days": race["days_to_go"], "word": coach["hook_word"]},
        "week": {
            "range": data["week"]["range"].replace(" 2026", "").replace("-", "–"),
            "hours": data["week"]["hours"],
            "km": data["week"]["distance_km"],
            "fitness": load["fitness_ctl"],
            "fatigue": load["fatigue_atl"],
            "form": load["form_tsb"],
        },
        "verdict": {
            "line1": line1 + "." if line2 else line1,
            "line2": line2,
            "today": load["form_tsb"],
            "raceForm": race["race_day_form_tsb"],
            "targetMin": race["target_form_min"],
            "targetMax": race["target_form_max"],
            "race": f"{race['name']} · {race['date_label']} · {race['priority']} race",
        },
        "gains": {
            "window": gains["window"],
            "hourPct": hour["delta_pct"],
            "hourW": hour["watts"],
            "secondLabel": second["label"],
            "secondPct": second["delta_pct"],
        },
        "cta": {"keyword": "COACH"},
    }


def prepare_twin(src, dest, tl):
    """Re-encode to the canvas size with a keyframe every second, so seeking never freezes."""
    w, h, fps = tl["width"], tl["height"], tl["fps"]
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src,
         "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps}",
         "-c:v", "libx264", "-crf", "18", "-g", str(fps), "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dest])


def make_voiceover(project, build, tl, voice):
    """Speak each beat's line with Kokoro, lay the lines end to end, and time the beats to them.

    Returns the total length; sets each beat's start and end, plus `speech` (start, end) for captions.
    """
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1")
    venv_python = ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        env.setdefault("HYPERFRAMES_PYTHON", str(venv_python))
    cache = build / "vo"
    cache.mkdir(parents=True, exist_ok=True)
    t, clips = VOICE_LEAD, []
    for b in tl["beats"]:
        key = hashlib.sha1(f"{voice}|{b['say']}".encode()).hexdigest()[:12]
        wav = cache / f"{b['id']}-{key}.wav"
        if not wav.exists():
            subprocess.run([HF, "tts", b["say"], "-v", voice, "-o", wav, "--json"], env=env, check=True, capture_output=True)
        d = probe_duration(wav)
        b["start"] = 0.0 if not clips else round(t - VOICE_GAP / 2, 2)
        b["speech"] = (t, t + d)
        clips.append((wav, t))
        t += d + VOICE_GAP
    total = round(t - VOICE_GAP + VOICE_TAIL, 2)
    for i, b in enumerate(tl["beats"]):
        b["end"] = tl["beats"][i + 1]["start"] if i + 1 < len(tl["beats"]) else total

    inputs, chains = [], []
    for i, (wav, at) in enumerate(clips):
        inputs += ["-i", wav]
        chains.append(f"[{i}:a]adelay={int(at * 1000)}:all=1[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(clips)))
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex",
         ";".join(chains) + f";{mix}amix=inputs={len(clips)}:normalize=0,apad,loudnorm=I=-16:TP=-1.5:LRA=11[out]",
         "-map", "[out]", "-t", f"{total:.2f}", "-ar", "48000", "-ac", "1", project / "assets" / "narration.wav"])
    return total


def reframe_script(beats, tl, total):
    """Root-timeline tweens: the twin shrinks into the bubble for each run of full-screen cards."""
    pip = tl["pip"]
    fx, fy = pip["center_x"] * tl["width"], pip["center_y"] * tl["height"]
    r = pip["size"] * tl["width"] / 2
    bx, by, br = BUBBLE
    k = br / r
    big = f"circle(2400px at {fx:.0f}px {fy:.0f}px)"
    small = f"circle({r:.0f}px at {fx:.0f}px {fy:.0f}px)"
    lines = [
        f'gsap.set("#twin-frame", {{ transformOrigin: "{fx:.0f}px {fy:.0f}px", clipPath: "{big}" }});',
        f'gsap.set("#twin-ring", {{ left: {fx - r:.0f}, top: {fy - r:.0f}, width: {2 * r:.0f}, height: {2 * r:.0f}, opacity: 0 }});',
    ]
    if LAYOUT.get(beats[0]["card"]) == "overlay" and beats[0]["end"] > PUNCH_IN[0] + 0.5:
        lines.append(f'tl.set("#twin-frame", {{ scale: {PUNCH_IN[1]} }}, {PUNCH_IN[0]});')
    runs, cur = [], None
    for b in beats:
        if LAYOUT.get(b["card"]) == "overlay":
            cur = None
            continue
        if cur is None:
            cur = [b["start"], b["end"]]
            runs.append(cur)
        else:
            cur[1] = b["end"]
    for s, e in runs:
        lines.append(f'tl.fromTo("#twin-frame", {{ x: 0, y: 0, scale: 1, clipPath: "{big}" }}, '
                     f'{{ x: {bx - fx:.0f}, y: {by - fy:.0f}, scale: {k:.4f}, clipPath: "{small}", duration: 0.65, ease: "power2.inOut" }}, {s:.2f});')
        lines.append(f'tl.fromTo("#twin-ring", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, {s + 0.45:.2f});')
        if e < total - 0.01:
            # The bubble grows back into the frame over the last moments of the card.
            lines.append(f'tl.to("#twin-ring", {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, {e - 0.65:.2f});')
            lines.append(f'tl.to("#twin-frame", {{ x: 0, y: 0, scale: 1, clipPath: "{big}", duration: 0.65, ease: "power3.in" }}, {e - 0.65:.2f});')
    return "\n      ".join(lines)


def sfx_tags(beats, total, voice):
    """Timed <audio> clips for SFX, each lasting exactly its file."""
    tags = []
    for b in beats:
        for offset, name, volume in SFX.get(b["card"], []):
            if voice and offset < 0:
                continue  # that whoosh belongs to the twin growing back, which has no voiceover equivalent
            if voice and b["card"] == "cta" and name == "pop":
                offset = 3.6  # the CTA box lands later when narrated (compositions/cta.html)
            at = b["start"] + offset
            if offset < b["end"] - b["start"] and 0 <= at < total - 0.5:
                length = min(probe_duration(SFX_DIR / f"{name}.mp3"), total - at)
                tags.append(f'<audio id="sfx-{len(tags)}" class="clip" src="assets/sfx/{name}.mp3" data-start="{at:.2f}" '
                            f'data-duration="{length:.2f}" data-track-index="{4 + len(tags) % 2}" data-volume="{volume}"></audio>')
    return tags


def write_index(project, beats, tl, data, total, voice=None):
    values = scene_values(data)
    if voice:
        for card in LAYOUT:
            values[card]["mode"] = "card"
    hosts = sfx_tags(beats, total, voice)
    for b in beats:
        overlay = LAYOUT.get(b["card"]) == "overlay"
        vv = html.escape(json.dumps(values.get(b["card"], {}), ensure_ascii=False), quote=True)
        hosts.append(
            f'<div id="{b["card"]}" data-composition-id="{b["card"]}" data-composition-src="compositions/{b["card"]}.html"\n'
            f'        data-start="{b["start"]:.2f}" data-duration="{b["end"] - b["start"]:.2f}" data-track-index="{2 if overlay else 1}"\n'
            f'        data-track-kind="graphics" data-width="{tl["width"]}" data-height="{tl["height"]}"\n'
            f'        data-variable-values="{vv}" style="z-index: {30 if overlay else 10}"></div>')
    if voice:
        presenter = (f'<audio id="narration" class="clip" src="assets/narration.wav" data-start="0" data-duration="{total:.2f}"\n'
                     f'        data-track-index="0" data-volume="1"></audio>')
    else:
        presenter = (f'<div id="twin-frame">\n'
                     f'        <video id="twin" class="clip" src="assets/twin.mp4" data-start="0" data-duration="{total:.2f}"\n'
                     f'          data-track-index="0" data-has-audio="true" playsinline></video>\n'
                     f'        <div id="twin-ring"></div>\n'
                     f'      </div>')
    doc = f"""<!doctype html>
<!-- Written by tools/hf_reel.py from timeline.json and data.json: edit those, or the scenes in compositions/. -->
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={tl['width']}, height={tl['height']}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <script src="assets/reel.js"></script>
    <link rel="stylesheet" href="assets/reel.css" />
    <style>
      html,
      body {{
        margin: 0;
        width: {tl['width']}px;
        height: {tl['height']}px;
        overflow: hidden;
        background: #0b0f14;
      }}
      #twin-frame {{
        position: absolute;
        inset: 0;
        z-index: 20;
      }}
      #twin {{
        position: absolute;
        left: 0;
        top: 0;
        width: {tl['width']}px;
        height: {tl['height']}px;
        object-fit: cover;
      }}
      #twin-ring {{
        position: absolute;
        box-sizing: border-box;
        border-radius: 50%;
        border: 20px solid #c6f432;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}"
      data-width="{tl['width']}" data-height="{tl['height']}" data-fps="{tl['fps']}">
      {presenter}

      {chr(10).join('      ' + h if i else h for i, h in enumerate(hosts))}

      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{total:.2f}" data-track-index="3" data-track-kind="captions"
        data-width="{tl['width']}" data-height="{tl['height']}" style="z-index: 40"></div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {"" if voice else reframe_script(beats, tl, total)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (project / "index.html").write_text(doc)


def caption_markup(text):
    """Escape a caption, colouring numbers and SHOUTED words (STOP, COACH) in the accent."""
    out = []
    for word in text.split():
        core = word.strip(".,!?")
        key = any(c.isdigit() for c in core) or (len(core) > 2 and core.isupper())
        out.append(f'<span class="cap-k">{html.escape(word)}</span>' if key else html.escape(word))
    return " ".join(out)


def write_captions(project, beats, tl, total):
    groups, tweens = [], []
    timed = [dict(b, start=b["speech"][0] - 0.1, end=b["speech"][1] + 0.25) if "speech" in b else b for b in beats]
    for i, (a, b, text) in enumerate(caption_events(timed)):
        b = min(b, total)
        groups.append(
            f'<div id="cap-{i}" class="cap clip" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="0">'
            f'<span class="cap-t">{caption_markup(text)}</span></div>')
        tweens.append(f'tl.fromTo("#cap-{i} .cap-t", {{ opacity: 0, filter: "blur(6px)" }}, '
                      f'{{ opacity: 1, filter: "blur(0px)", duration: 0.12, ease: "power2.out" }}, {a:.2f});')
    doc = f"""<!doctype html>
<!-- Written by tools/hf_reel.py: one caption group per spoken chunk of timeline.json. -->
<html lang="en" data-composition-id="captions">
  <body>
    <template>
      <div id="root" data-composition-id="captions" data-width="{tl['width']}" data-height="{tl['height']}">
        <style>
          #root {{
            position: absolute;
            inset: 0;
            background: transparent;
          }}
          .cap {{
            position: absolute;
            left: 0;
            right: 0;
            top: 1192px;
            text-align: center;
            overflow: visible;
          }}
          .cap-t {{
            display: inline-block;
            padding: 8px 26px 12px;
            border-radius: 20px;
            background: rgba(11, 15, 20, 0.6);
            font-family: "Inter", system-ui, sans-serif;
            font-size: 66px;
            font-weight: 900;
            letter-spacing: -0.01em;
            color: #ffffff;
          }}
          .cap-k {{
            color: #c6f432;
          }}
        </style>
        {chr(10).join('        ' + g if i else g for i, g in enumerate(groups))}
        <script>
          (function () {{
            var fit = window.__hyperframes && window.__hyperframes.fitTextFontSize;
            if (fit) {{
              document.querySelectorAll("#root .cap-t").forEach(function (el) {{
                var size = fit(el.textContent, {{ fontFamily: "Inter", fontWeight: 900, maxWidth: 900, baseSize: 66, minSize: 42 }}).fontSize;
                el.style.fontSize = size + "px";
              }});
            }}
            var tl = gsap.timeline({{ paused: true }});
            {chr(10).join('            ' + t if i else t for i, t in enumerate(tweens))}
            window.__timelines["captions"] = tl;
          }})();
        </script>
      </div>
    </template>
  </body>
</html>
"""
    (project / "compositions" / "captions.html").write_text(doc)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reel", type=Path)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--twin", type=Path, help="9:16 video of your digital twin reading twin_script.txt")
    src.add_argument("--placeholder", action="store_true", help="use a stand-in presenter")
    src.add_argument("--voice", help="no presenter: narrate with this local Kokoro voice (e.g. am_michael)")
    ap.add_argument("--auto-sync", action="store_true", help="align beats to the pauses in the twin's audio")
    ap.add_argument("--render", action="store_true", help="check, then render the reel")
    ap.add_argument("--out", type=Path, help="render path (default <reel>/out/reel_hyperframes.mp4)")
    a = ap.parse_args()

    reel = a.reel.resolve()
    project = reel / "hyperframes"
    build = reel / "build"
    build.mkdir(exist_ok=True)
    tl = json.loads((reel / "timeline.json").read_text())
    data = json.loads((reel / "data.json").read_text())

    if a.voice:
        total = make_voiceover(project, build, tl, a.voice)
        beats = tl["beats"]
        (project / "assets" / "twin.mp4").unlink(missing_ok=True)
    else:
        if a.twin:
            source = a.twin.resolve()
            if a.auto_sync:
                auto_sync(tl, source)
        else:
            planned = beat_windows(tl)
            source = make_placeholder(build, tl, planned, planned[-1]["end"])
        twin = project / "assets" / "twin.mp4"
        prepare_twin(source, twin, tl)
        total = probe_duration(twin)
        beats = beat_windows(tl, total=total)
        (project / "assets" / "narration.wav").unlink(missing_ok=True)

    sfx_out = project / "assets" / "sfx"
    sfx_out.mkdir(parents=True, exist_ok=True)
    for name in {n for cues in SFX.values() for _, n, _ in cues} | {"CREDITS"}:
        src_file = SFX_DIR / (f"{name}.md" if name == "CREDITS" else f"{name}.mp3")
        if not (sfx_out / src_file.name).exists():
            shutil.copy(src_file, sfx_out / src_file.name)

    write_index(project, beats, tl, data, total, a.voice)
    write_captions(project, beats, tl, total)
    print(f"wrote {project / 'index.html'} and compositions/captions.html ({total:.1f}s, {len(beats)} beats)")

    if a.render:
        env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1")
        subprocess.run([HF, "check"], cwd=project, env=env, check=True)
        out = (a.out or reel / "out" / "reel_hyperframes.mp4").resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([HF, "render", "-o", out, "-q", "delivery"], cwd=project, env=env, check=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
