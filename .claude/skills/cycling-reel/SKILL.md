---
name: cycling-reel
description: Make an Instagram reel (9:16, 20–45 s) about Syaiful's cycling training from real intervals.icu data — AI coach verdicts, form/TSB, taper, power gains, race reports — with an AI voiceover over his own ride footage, plus the caption, hooks, COACH DM reply and posting checklist. Use for "make a reel", "new reel about…", "Part 2/3", "write the caption", "give me hooks", "fix this caption", or reusing this look on a new story.
---

# Cycling reel (AI coach × intervals.icu)

The proven format from `reels/01-ai-coach-intervals` (final: `out/reel_25s.mp4`) and the
Part 2 template in `reels/02-race-report`. Copy one of these folders for a new reel; never
hand-write a new pipeline.

## 1. Story from real data only

- Pull from the Montis ICU Coach MCP (athlete `i773595`): `run_weekly`, `get_wellness`
  (CTL/ATL/TSB per day), `get_calendar`/`get_training_plan` (planned TSS, A race),
  `get_power_curves` (best efforts, window vs previous window), `get_activity` for one ride.
- Every number on screen, in the voiceover and in the caption must trace to a source.
  Record the source and date in `data.json` (`_source`, `as_of`) and in the timeline `_note`.
- Name metrics exactly: "best 60-min power in the last 85 days" not "FTP"; TSB = "form".
  Re-check the value when asked ("where did 214 come from?" → it was 219 W: verify, don't defend).
- Form changes daily: a reel with "today" numbers is stale tomorrow. Re-pull before rendering
  and say the as-of date in the checklist.
- Pick the story that is *true*, including the unflattering one. Surprise beats routine:
  "I rode DOUBLE my taper" > "I'm tapering". A bad result is still a reel (and a Part 3).

## 2. Structure (25 s cut)

| Beat | Card | Job |
|------|------|-----|
| hook (0–4 s) | `hook`, overlay on footage | A confession / surprising number + "THAT'S ME" marker. Must stop the scroll in 1.5 s |
| pipeline | `pipeline` | Garmin + Strava → intervals.icu → AI coach (one line) |
| verdict | `verdict` | The coach's call + form journey (−39 → −5 → +14, sweet spot band) |
| proof | `gains` / `result` | One hard number that pays off the hook |
| cta | `cta`, overlay on footage | "Want my setup? Comment COACH!" |

Voice lines: short, spoken numbers ("minus thirty nine"), exclamations, questions
("Its call? Back off!"). Captions use digits and SHOUT the key word (it turns butter-yellow bold).

## 3. Look (locked — keep it consistent across the series)

- Montserrat 900/800/700, everything butter yellow `#FFE68F`, highlight `#FFF`, uppercase captions.
- No boxes, no dark panels, no outlines: soft 3-layer text-shadow + a slight footage grade
  (`eq=brightness=-0.07:contrast=1.08:saturation=1.05`) carry contrast.
- Meaning colours stay on the form chart only: red < −30, amber, green sweet-spot band.
- The subject is **Syaiful, the rider in white ahead of the camera**, not the camera holder.
  Footage is cut to tracked segments with him centred (zoom 1.5, `subject_y` 0.66).
- Text inside IG safe zone: 168–1330 px vertically; captions ≈1192 px.
- AI voice: Kokoro `am_michael` at 1.2×. No music in the file — he adds trending audio in IG.

## 4. Build → review → render

See `references/build.md` for commands, timeline fields and known pitfalls. Always:
snapshot the edited moments and show a draft (`--quality draft`) before the delivery render;
verify with ffprobe (1080×1920, 30 fps, H.264, AAC) and loudness (≈ −16 LUFS, peak ≤ −1 dBFS).

## 5. Caption, hooks, DM

See `references/captions.md` (caption formula, hook types, POV fixes, hashtags, the COACH DM).

## 6. Posting checklist (put it under every caption file)

- Numbers' as-of date still true on posting day?
- IG AI label on (Advanced settings → Add AI label); "🤖 AI-generated voiceover" line in caption.
- Trending audio added in IG at 15–25 %, original audio 100 %.
- Riders who appear tagged or OK with it.
- COACH DM reply ready; reply to comments in the first hour.
- Tease the next part only if it will actually be posted.

## Rules

- Branch/commit rules from the session apply; commit reel sources, timelines and the final MP4.
- Never ask for API keys in chat. Never invent data, placings or times — leave `[after race]`
  placeholders and ask.
