# Build reference

## Commands

```bash
bash tools/setup.sh                                   # once per container: npm, .venv, whisper-cli, browser
export HYPERFRAMES_PYTHON=.venv/bin/python            # Kokoro TTS runs from the venv

# draft (fast), then delivery
python3 tools/hf_reel.py reels/<reel> --timeline timeline_25s_confess.json \
  --voice am_michael --speed 1.2 --render --quality draft --out reels/<reel>/out/draft.mp4
python3 tools/hf_reel.py reels/<reel> --timeline timeline_25s_confess.json \
  --voice am_michael --speed 1.2 --render --out reels/<reel>/out/reel_25s.mp4

# look before rendering
cd reels/<reel>/hyperframes && npx hyperframes check && npx hyperframes snapshot --at 1,4,9,15,22

# verify
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 out.mp4
ffmpeg -i out.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
```

`--music` synthesises a ducked bed (`tools/make_music.py`) — only if asked; default is none.
`hf_reel.py` writes only `index.html`, `compositions/captions.html`, `assets/narration.wav`,
`assets/ride.mp4`. The scene files in `compositions/` are hand-written: edit those for looks.

## Timeline (`timeline_*.json`)

- `beats[]`: `id`, `card` (composition name), `layout` (`overlay` = over footage, `full`),
  `say` (spoken; numbers in words), `caption` (on screen; digits, SHOUTED keyword),
  `pace` (<1 = faster reveals for short cuts), `hold` (extra seconds after the line),
  `values` (per-beat overrides of the composition variables, e.g. hook `line`, `word`, `pill`;
  verdict `line1`, `line2`, `fromForm`, `fromLabel`).
- Beat length = TTS length + `hold`; card numbers come from `data.json[card]`.
- `footage`: `source`, `zoom`, `subject_y`, `segments[{from,to,track:[[t,x,y],…]}]`
  (subject centre as frame fractions, keyframed ~every 0.6–0.8 s → piecewise-linear crop),
  `hook`/`cards`/`cta` start offsets, `me` marker {label,x,y}, `grade`.
- Find track points by extracting frames (`ffmpeg -ss t -i src -frames:v 1`) and reading them;
  confirm which rider is the subject before cutting.

## Compositions

`hook`, `pipeline`, `verdict`, `coach`, `week`, `gains`, `cta`, `result` (Part 2).
Shared style: `hyperframes/assets/reel.css` (tokens `--ink/--lime #ffe68f`, `--hi #fff`,
`--muted #c9b97c`), helpers `assets/reel.js` (`reel.format` with sign, `reel.count`, word reveals).
Animations use `fromTo` only, paused timeline on `window.__timelines[id]`, reveal times wrapped in `P()`.

## Pitfalls already solved — don't reintroduce

- CDNs, HuggingFace, HeyGen, music/SFX sites are blocked: GSAP is vendored, fonts come from
  Fontsource npm, voice is local Kokoro, SFX in `assets/sfx`.
- GSAP drops a leading "+" on counted numbers: `reel.format` prefixes U+2060.
- loudnorm look-ahead truncated the music tail: use a measured fixed gain.
- SFX clips need `data-duration` = file length and alternating tracks (4/5).
- `line_unread` warnings → add `hold` or reveal earlier; `check` exit code no longer blocks render.
- Phone footage may carry rotation metadata: re-encode upright first.
- Long hook lines orphan a word: break with `\n` deliberately.
