#!/usr/bin/env python3
"""Assemble a reel's HyperFrames project from its timeline, data and twin video, then render.

  python3 tools/hf_reel.py reels/01-ai-coach-intervals --twin twin.mp4 --auto-sync --render
  python3 tools/hf_reel.py reels/01-ai-coach-intervals --placeholder --render
  python3 tools/hf_reel.py reels/01-ai-coach-intervals --voice am_michael --speed 1.2 --render
  python3 tools/hf_reel.py reels/01-ai-coach-intervals --voice am_michael --footage ride.mp4 --render

The scenes in <reel>/hyperframes/compositions/ are hand-written and never touched here.
This script writes only the parts that follow from data: assets/twin.mp4 or
assets/narration.wav, index.html (scene timings, the numbers each scene shows, the twin's
move into the bubble) and compositions/captions.html.

With --voice there is no presenter: a local Kokoro voice reads each beat's `say` line,
every card fills the screen, and each beat lasts exactly as long as its line. Add --footage
to play your own phone footage underneath: the hook and CTA show it full frame, and the data
cards sit on dark glass over it. timeline.json "footage" picks the moments, and can cut the
clip down to tracked segments, zoomed to keep you centred.
"""
import argparse
import hashlib
import html
import json
import os
import re
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
VOICE_LEAD, VOICE_GAP, VOICE_TAIL = 0.1, 0.3, 1.6  # seconds before the first line, between lines, after the last
PUNCH_IN = (2.4, 1.08)  # hard punch-in on the twin at "back off!": time, scale
# Sound effects on visible actions, from the HyperFrames media-use library (Pixabay licence):
# (seconds after the scene starts, file in assets/sfx, volume). Kept well under the voice.
SFX = {
    "hook": [(0.05, "impact-bass-1", 0.35)],
    "pipeline": [(0.0, "whoosh", 0.3), (4.85, "pop", 0.4)],
    "coach": [(2.2, "pop", 0.25)],
    "week": [(6.75, "ping", 0.3)],
    "verdict": [(5.7, "chime", 0.3)],
    "gains": [(2.25, "sparkle", 0.3)],
    "cta": [(-0.6, "whoosh-short", 0.3), (1.1, "pop", 0.45)],
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


def make_voiceover(project, build, tl, voice, speed=1.0):
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
        key = hashlib.sha1(f"{voice}|{speed}|{b['say']}".encode()).hexdigest()[:12]
        wav = cache / f"{b['id']}-{key}.wav"
        if not wav.exists():
            subprocess.run([HF, "tts", b["say"], "-v", voice, "-s", str(speed), "-o", wav, "--json"], env=env, check=True, capture_output=True)
        d = probe_duration(wav)
        b["start"] = 0.0 if not clips else round(t - VOICE_GAP / 2, 2)
        b["speech"] = (t, t + d)
        clips.append((wav, t))
        t += d + VOICE_GAP + b.get("hold", 0)  # an optional beat of silence after the line
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


def lerp_expr(track, i):
    """ffmpeg expression for column i of [[t, x, y], ...] keyframes, linear between them, in segment time `t`."""
    expr = f"{track[-1][i]}"
    for (t0, *a), (t1, *b) in reversed(list(zip(track, track[1:]))):
        v0, v1 = a[i - 1], b[i - 1]
        expr = f"if(lt(t,{t1}),{v0}+({v1}-{v0})*(t-{t0})/{t1 - t0},{expr})"
    return expr


def prepare_footage(src, dest, tl):
    """Upright, canvas-sized, silent, a keyframe every second (seeking never freezes).

    With footage.segments in the timeline, keep only those stretches and crop each one
    `zoom`x around the tracked subject, who lands at `subject_y` down the frame.
    """
    w, h, fps = tl["width"], tl["height"], tl["fps"]
    plan = tl.get("footage", {})
    enc = ["-c:v", "libx264", "-crf", "22", "-preset", "slow", "-g", str(fps), "-an", "-movflags", "+faststart", dest]
    if not plan.get("segments"):
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src,
             "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},format=yuv420p", *enc])
        return
    z, sy = plan.get("zoom", 1.0), plan.get("subject_y", 0.5)
    chains = []
    for i, seg in enumerate(plan["segments"]):
        cx, cy = lerp_expr(seg["track"], 1), lerp_expr(seg["track"], 2)
        cw, ch = f"trunc(iw/{z}/2)*2", f"trunc(iw/{z}*{h}/{w}/2)*2"
        chains.append(
            f"[0:v]trim={seg['from']}:{seg['to']},setpts=PTS-STARTPTS,"
            f"crop=w={cw}:h={ch}:x='clip(({cx})*iw-ow/2,0,iw-ow)':y='clip(({cy})*ih-oh*{sy},0,ih-oh)',"
            f"scale={w}:{h}:flags=lanczos,unsharp=5:5:0.5,fps={fps},format=yuv420p,setsar=1[s{i}]")
    n = len(chains)
    graph = ";".join(chains) + ";" + "".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-filter_complex", graph, "-map", "[v]", *enc])


def footage_tags(beats, tl, total, length):
    """One muted clip per overlay beat (its own moment) and one per run of data cards, slowed if the footage runs short."""
    plan = tl.get("footage", {})
    tags, script, runs, cur = [], [], [], None
    for b in beats:
        if LAYOUT.get(b["card"]) == "overlay":
            runs.append((b["card"], b["start"], b["end"], plan.get(b["card"], 0.0)))
            cur = None
        elif cur is None:
            cur = [f"cards{len(runs)}", b["start"], b["end"], plan.get("cards", 0.0)]
            runs.append(cur)
        else:
            cur[2] = b["end"]
    for name, start, end, media_start in runs:
        dur = end - start
        avail = length - media_start
        rate = max(0.6, min(1.0, avail / dur))
        rate_attr = f' data-playback-rate="{rate:.3f}"' if rate < 1 else ""
        # When even 0.6x can't cover the run, play the footage again from the top.
        pieces, t, k = [], start, 0
        while t < end - 0.01:
            piece = min(end - t, (avail if k == 0 else length) / rate)
            pieces.append((t, piece, media_start if k == 0 else 0.0))
            t, k = t + piece, k + 1
        clips = "\n".join(
            f'        <video id="ride-{name}{"-" + str(j) if j else ""}" class="clip" src="assets/ride.mp4" data-start="{ps:.2f}" data-duration="{pd:.2f}"\n'
            f'          data-media-start="{pm:.2f}"{rate_attr} data-track-index="{j % 2}" muted playsinline></video>'
            for j, (ps, pd, pm) in enumerate(pieces))
        tags.append(f'<div id="ride-{name}-wrap" class="ride-wrap">\n{clips}\n      </div>')
    if runs and runs[0][0] == "hook":
        script.append(f'tl.set("#ride-hook-wrap", {{ scale: {PUNCH_IN[1]}, transformOrigin: "50% 60%" }}, {PUNCH_IN[0]});')
    return tags, script


def make_music_bed(project, total, drop, level=-24.0):
    """Compose an original bed (tools/make_music.py) and duck it under the narration.

    The music sits at `level` LUFS (about 8 dB under the -16 LUFS voice) and dips a
    further ~10 dB whenever the narrator speaks, recovering in the pauses.
    """
    raw = project / "assets" / "music_raw.wav"
    run([ROOT / ".venv" / "bin" / "python", ROOT / "tools" / "make_music.py", raw,
         "--duration", f"{total:.2f}", "--drop", f"{drop:.2f}"])
    # Measure, then apply one fixed gain: loudnorm's look-ahead would drop the last ~3 s (the fade).
    meter = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    measured = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", meter)[-1])
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-i", project / "assets" / "narration.wav",
         "-filter_complex",
         f"[0:a]volume={level - measured:.2f}dB[m];[1:a]aformat=channel_layouts=stereo[k];"
         "[m][k]sidechaincompress=threshold=0.015:ratio=6:attack=15:release=350:makeup=1[out]",
         "-map", "[out]", "-t", f"{total:.2f}", "-ar", "48000", project / "assets" / "music.wav"])
    raw.unlink()


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
            if offset > 0:
                offset *= b.get("pace", 1)  # reveals (and their sounds) scale with the beat's pace
            at = b["start"] + offset
            if offset < b["end"] - b["start"] and 0 <= at < total - 0.5:
                length = min(probe_duration(SFX_DIR / f"{name}.mp3"), total - at)
                tags.append(f'<audio id="sfx-{len(tags)}" class="clip" src="assets/sfx/{name}.mp3" data-start="{at:.2f}" '
                            f'data-duration="{length:.2f}" data-track-index="{4 + len(tags) % 2}" data-volume="{volume}"></audio>')
    return tags


def write_index(project, beats, tl, data, total, voice=None, footage_len=None, music=False):
    values = scene_values(data)
    if voice and footage_len:
        # Your face carries the hook and CTA, so they keep the over-the-presenter layout.
        for card in LAYOUT:
            values[card]["tag"] = "AI-generated voiceover"
        values["cta"]["boxTop"] = 270  # keep the ask clear of the rider in the middle of the frame
        me = tl.get("footage", {}).get("me")
        if me:
            values["hook"].update(meLabel=me["label"], meX=me["x"], meY=me["y"])
    elif voice:
        for card in LAYOUT:
            values[card]["mode"] = "card"
    for b in beats:
        if "pace" in b:
            values.setdefault(b["card"], {})["pace"] = b["pace"]
        values.setdefault(b["card"], {}).update(b.get("values", {}))  # per-cut wording and numbers
    hosts = sfx_tags(beats, total, voice)
    for b in beats:
        overlay = LAYOUT.get(b["card"]) == "overlay"
        vv = html.escape(json.dumps(values.get(b["card"], {}), ensure_ascii=False), quote=True)
        hosts.append(
            f'<div id="{b["card"]}" data-composition-id="{b["card"]}" data-composition-src="compositions/{b["card"]}.html"\n'
            f'        data-start="{b["start"]:.2f}" data-duration="{b["end"] - b["start"]:.2f}" data-track-index="{2 if overlay else 1}"\n'
            f'        data-track-kind="graphics" data-width="{tl["width"]}" data-height="{tl["height"]}"\n'
            f'        data-variable-values="{vv}" style="z-index: {30 if overlay else 10}"></div>')
    footage, footage_script = footage_tags(beats, tl, total, footage_len) if footage_len else ([], [])
    if voice:
        presenter = (f'<audio id="narration" class="clip" src="assets/narration.wav" data-start="0" data-duration="{total:.2f}"\n'
                     f'        data-track-index="0" data-volume="1"></audio>')
        if music:
            presenter += (f'\n      <audio id="music" class="clip" src="assets/music.wav" data-start="0" data-duration="{total:.2f}"\n'
                          f'        data-track-index="6" data-volume="1"></audio>')
        presenter = "\n      ".join([presenter, *footage])
    else:
        presenter = (f'<div id="twin-frame">\n'
                     f'        <video id="twin" class="clip" src="assets/twin.mp4" data-start="0" data-duration="{total:.2f}"\n'
                     f'          data-track-index="0" data-has-audio="true" playsinline></video>\n'
                     f'        <div id="twin-ring"></div>\n'
                     f'      </div>')
    doc = f"""<!doctype html>
<!-- Written by tools/hf_reel.py from timeline.json and data.json: edit those, or the scenes in compositions/. -->
<html lang="en" data-resolution="portrait"{' class="footage"' if footage_len else ''}>
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
      .ride-wrap {{
        position: absolute;
        inset: 0;
        z-index: 5;
        overflow: hidden;
      }}
      .ride-wrap video {{
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
      {chr(10).join(footage_script) if voice else reframe_script(beats, tl, total)}
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


def write_captions(project, beats, tl, total, skip=()):
    """Caption groups for every beat except those in `skip` (cards that already show their line in big type)."""
    groups, tweens = [], []
    timed = [dict(b, start=b["speech"][0] - 0.1, end=b["speech"][1] + 0.25) if "speech" in b else b for b in beats]
    timed = [b for b in timed if b["card"] not in skip]
    for i, (a, b, text) in enumerate(caption_events(timed)):
        b = min(b, total)
        groups.append(
            f'<div id="cap-{i}" class="cap clip" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="0">'
            f'<span class="cap-t">{caption_markup(text)}</span></div>')
        # Social-style pop: each group lands from slightly small with a little overshoot.
        tweens.append(f'tl.fromTo("#cap-{i} .cap-t", {{ opacity: 0, scale: 0.82 }}, '
                      f'{{ opacity: 1, scale: 1, duration: 0.18, ease: "back.out(2.2)" }}, {a:.2f});')
    doc = f"""<!doctype html>
<!-- Written by tools/hf_reel.py: one caption group per spoken chunk of timeline.json. -->
<html lang="en" data-composition-id="captions">
  <body>
    <template>
      <div id="root" data-composition-id="captions" data-width="{tl['width']}" data-height="{tl['height']}">
        <style>
          /* Montserrat Black (SIL OFL, from Fontsource): the heavy all-caps caption look of CapCut-style reels. */
          @font-face {{
            font-family: "Montserrat";
            font-weight: 900;
            src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2");
          }}
          @font-face {{
            font-family: "Montserrat";
            font-weight: 800;
            src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2");
          }}
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
          /* No box: butter-yellow letters held off the footage by a dark outline and a soft drop shadow. */
          .cap-t {{
            display: inline-block;
            padding: 0 30px;
            font-family: "Montserrat", "Inter", system-ui, sans-serif;
            font-size: 64px;
            font-weight: 900;
            line-height: 1.1;
            letter-spacing: 0.01em;
            text-transform: uppercase;
            color: #ffe68f;
            -webkit-text-stroke: 9px #14110a;
            paint-order: stroke fill;
            text-shadow: 0 6px 18px rgba(0, 0, 0, 0.55);
            transform-origin: 50% 60%;
          }}
          .cap-k {{
            color: #ffffff;
          }}
        </style>
        {chr(10).join('        ' + g if i else g for i, g in enumerate(groups))}
        <script>
          (function () {{
            var fit = window.__hyperframes && window.__hyperframes.fitTextFontSize;
            if (fit) {{
              document.querySelectorAll("#root .cap-t").forEach(function (el) {{
                var size = fit(el.textContent.toUpperCase(), {{ fontFamily: "Montserrat", fontWeight: 900, maxWidth: 900, baseSize: 64, minSize: 40 }}).fontSize;
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
    ap.add_argument("--timeline", default="timeline.json", help="beats file inside the reel folder (e.g. timeline_25s.json for the short cut)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--twin", type=Path, help="9:16 video of your digital twin reading twin_script.txt")
    src.add_argument("--placeholder", action="store_true", help="use a stand-in presenter")
    src.add_argument("--voice", help="no presenter: narrate with this local Kokoro voice (e.g. am_michael)")
    ap.add_argument("--footage", type=Path, help="with --voice: your own video to play under the cards (hook and CTA show it full frame)")
    ap.add_argument("--music", action="store_true", help="with --voice: compose an original music bed and duck it under the voice")
    ap.add_argument("--speed", type=float, default=1.2, help="narration speed for --voice (default 1.2: reels want a brisk read)")
    ap.add_argument("--auto-sync", action="store_true", help="align beats to the pauses in the twin's audio")
    ap.add_argument("--render", action="store_true", help="check, then render the reel")
    ap.add_argument("--out", type=Path, help="render path (default <reel>/out/reel_hyperframes.mp4)")
    ap.add_argument("--quality", default="delivery", help="render quality: draft for quick previews, delivery for posting")
    a = ap.parse_args()

    reel = a.reel.resolve()
    project = reel / "hyperframes"
    build = reel / "build"
    build.mkdir(exist_ok=True)
    tl = json.loads((reel / a.timeline).read_text())
    data = json.loads((reel / "data.json").read_text())

    if a.voice:
        total = make_voiceover(project, build, tl, a.voice, a.speed)
        beats = tl["beats"]
        (project / "assets" / "twin.mp4").unlink(missing_ok=True)
        source = a.footage.resolve() if a.footage else (reel / tl["footage"]["source"] if tl.get("footage", {}).get("source") else None)
        if source:
            prepare_footage(source, project / "assets" / "ride.mp4", tl)
        elif (project / "assets" / "ride.mp4").exists() and not tl.get("footage"):
            (project / "assets" / "ride.mp4").unlink()
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

    ride = project / "assets" / "ride.mp4"
    footage_len = probe_duration(ride) if a.voice and (a.footage or tl.get("footage")) and ride.exists() else None
    music = bool(a.voice and a.music)
    if music:
        make_music_bed(project, total, drop=beats[0]["end"])
    else:
        (project / "assets" / "music.wav").unlink(missing_ok=True)
    write_index(project, beats, tl, data, total, a.voice, footage_len, music)
    write_captions(project, beats, tl, total, skip=LAYOUT if footage_len else ())
    print(f"wrote {project / 'index.html'} and compositions/captions.html ({total:.1f}s, {len(beats)} beats)")

    if a.render:
        env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1")
        subprocess.run([HF, "check"], cwd=project, env=env, check=True)
        out = (a.out or reel / "out" / "reel_hyperframes.mp4").resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([HF, "render", "-o", out, "-q", a.quality], cwd=project, env=env, check=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
