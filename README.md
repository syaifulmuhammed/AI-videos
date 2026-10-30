# AI videos

Instagram reels presented by my AI digital twin, with animated cards built from my real training data.

Each reel lives in `reels/<name>/` and contains:

| File | What it's for |
|------|---------------|
| `script.md` | Beat sheet, on-screen text, where each number comes from, hook alternatives |
| `twin_script.txt` | Text to paste into your digital-twin tool (HeyGen, Synthesia, Captions, etc.) |
| `data.json` | Snapshot of the numbers the cards display |
| `timeline.json` | Beats, the captions shown in each, and where your face sits in the frame |
| `instagram_caption.md` | Post caption, hashtags and a pre-post checklist |
| `stills/` | Final frame of each card, for checking the design or using as a cover |
| `out/preview_placeholder.mp4` | Full preview with a stand-in presenter |

## Making a reel

### 1. Generate the twin video

In your digital-twin tool:

1. Choose your avatar and your cloned voice.
2. Set the format to **9:16 portrait (1080×1920)**, head and shoulders, plain background. Leave some headroom: the hook text sits in the top quarter of the frame.
3. Paste in `twin_script.txt`. Replace each `[PAUSE 1s]` line with the tool's own pause. In HeyGen that's the pause button in the script editor; many tools also accept `<break time="1s"/>`. The pauses tell the build script where each beat starts.
4. Export as MP4 and save it as, for example, `reels/01-ai-coach-intervals/twin.mp4`. Twin videos are gitignored.

### 2. Build the reel

```bash
python3 tools/build_reel.py reels/01-ai-coach-intervals --twin reels/01-ai-coach-intervals/twin.mp4 --auto-sync
```

This writes `reels/01-ai-coach-intervals/out/reel.mp4`, made of:

- your twin full screen for the hook and CTA, with text overlays
- full-screen data cards for the middle beats, with your twin in a circle at the bottom left
- burned-in captions, also written to `captions.srt`

Options:

- `--music track.mp3` mixes a quiet background track under your voice.
- `--no-captions` skips burned-in captions, for when you'd rather use Instagram's or CapCut's auto-captions.
- `--export-broll` also writes each card to `broll/` as a separate clip (`.mp4` for full cards, ProRes 4444 `.mov` with transparency for overlays), for editing in CapCut or Premiere.
- `--skip-render` reuses cards that were already rendered, so only the ffmpeg step runs again.

If the circle bubble cuts off your face, change `pip.center_x`, `pip.center_y` and `pip.size` in `timeline.json`. They're fractions of the frame. If `--auto-sync` can't find enough pauses, it says so and falls back to the `start` times in `timeline.json`, which you can edit by hand.

### 3. Preview without a twin

```bash
python3 tools/build_reel.py reels/01-ai-coach-intervals --placeholder
```

## Refreshing the numbers

Numbers live in `data.json`; the cards read from it every time they render. To update:

1. Pull a fresh weekly report from intervals.icu. I use the Montis ICU Coach connector in Claude.
2. Edit `data.json`.
3. Update the matching spoken numbers in `twin_script.txt` and the captions in `timeline.json`.
4. Rebuild.

## Requirements

- Python 3 with Pillow
- Node 18+ with Playwright and Chromium (`npm i playwright && npx playwright install chromium`)
- ffmpeg built with libass, for captions
- The Inter / Inter Display font. It's optional; without it the cards fall back to the system sans-serif.
