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

### 2b. Or build it with HyperFrames

Each reel also has a HyperFrames project in `hyperframes/`. Its hand-written scenes live in `compositions/`. On the data cards, the twin shrinks into a bubble and grows back for the call to action.

```bash
python3 tools/hf_reel.py reels/01-ai-coach-intervals --twin reels/01-ai-coach-intervals/twin.mp4 --auto-sync --render
```

This writes `out/reel_hyperframes.mp4`. To narrate with an AI voice and no presenter, use `--voice am_michael` (listen to the options in `voice-samples/`); this writes `out/reel_voiceover.mp4` when you pass `--out` with that name. The free local voice needs `pip install -r requirements.txt` in `.venv`, which `tools/setup.sh` does. Add `--footage your-clip.mp4` to play your own phone video under the reel: set the moments with your face for the hook and CTA under `footage` in `timeline.json`. This writes `out/reel_footage.mp4` when passed as `--out`. Use `--placeholder` in place of `--twin …` for a preview. To preview without rendering, run the script without `--render`, then `cd reels/01-ai-coach-intervals/hyperframes && npx hyperframes preview`. `REVIEW.md` in that folder records the design decisions.

### 3. Preview without a twin

```bash
python3 tools/build_reel.py reels/01-ai-coach-intervals --placeholder
```

## HeyGen inside Claude

HeyGen's official skills live in `.claude/skills/`, vendored from [heygen-com/skills](https://github.com/heygen-com/skills) (see `HEYGEN_SOURCE.txt`). Claude Code loads them automatically in this repo:

- `heygen-avatar` creates or finds your digital twin (avatar + voice).
- `heygen-video` generates a presenter video with that avatar.
- `heygen-translate` dubs a finished video into another language, for example an Arabic version of a reel.

The skills need one way to reach HeyGen. Pick one:

1. **HeyGen MCP connector (recommended).** Sign-in is by OAuth and it uses your HeyGen plan credits. In claude.ai go to Settings → Connectors → Add custom connector, enter `https://mcp.heygen.com/mcp/v1/` and sign in. `.mcp.json` registers the same server for Claude Code on your own machine.
2. **HeyGen CLI with an API key.** This is billed as API credits. Create a key at app.heygen.com/api, store it as the `HEYGEN_API_KEY` environment variable, and install the CLI with `curl -fsSL https://static.heygen.ai/cli/install.sh | bash`.

For Claude Code cloud sessions, the environment's network access must allow `api.heygen.com`, `static.heygen.ai` and `mcp.heygen.com`.

## Toolchain

`tools/setup.sh` installs everything on a fresh machine or cloud session, skips what's already there, and prints each version:

| Tool | Version | Where it comes from |
|------|---------|---------------------|
| ffmpeg | system (6.1.1 here) | OS package manager |
| yt-dlp | 2026.10.26 | `requirements.txt`, installed into `.venv/` and linked onto `PATH` |
| whisper.cpp (`whisper-cli`) | v1.9.5 (`482279b`) | built from source as a static binary; HyperFrames' `transcribe` uses it |
| HyperFrames | 0.8.227 | `package.json` |
| Remotion | 4.0.539 | `package.json` (with React 18.3.1) |

Notes:

- **Whisper models** download on first use from `huggingface.co` into `~/.cache/hyperframes/whisper/models/`, for example via `npx hyperframes transcribe <file> --model small.en`. To use `whisper-cli` directly, pass `-m <model file>`.
- **Remotion** normally downloads its own Chrome. When it can't, as in cloud sessions, `remotion.config.js` uses a headless Chrome already on the machine.
- **Remotion licence**: free for individuals and companies of up to 3 people. Larger companies need a company licence; see remotion.dev/license.
- **yt-dlp**: only download videos you have the rights to use, such as your own uploads or clips licensed for reuse.
- **Cloud sessions**: these hosts are blocked unless you add them to the environment's allowed domains:
  - `huggingface.co` for Whisper models
  - `remotion.media` for Remotion's own Chrome
  - the video sites you want yt-dlp to download from, such as `youtube.com`, `googlevideo.com` and `instagram.com`

  To have every new session ready, add `bash tools/setup.sh` to the environment's setup script.

## HyperFrames (HTML → video)

[HyperFrames](https://github.com/heygen-com/hyperframes) is HeyGen's open-source framework for writing videos as HTML and rendering them to MP4. It's installed here in two parts:

- **CLI:** pinned in `package.json` together with GSAP, the animation library its templates use.
- **Skills:** the four core skills (`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`) are in `.claude/skills/`. See `HYPERFRAMES_SOURCE.txt`.

Set up a fresh machine or cloud session:

```bash
npm install
npm run hf:setup        # downloads the headless Chrome used for rendering, then runs a health check
```

Then ask Claude to "use /hyperframes to …", or use the CLI directly: `npx hyperframes init <name> --resolution portrait`, then `npx hyperframes render`.

In Claude Code cloud sessions, `cdn.jsdelivr.net` is blocked, so the templates can't load GSAP from the CDN. Point the `<script>` at a local copy instead: copy `node_modules/gsap/dist/gsap.min.js` next to the project's `index.html`. Alternatively, allow `cdn.jsdelivr.net` in the environment's network settings.

HyperFrames sends usage telemetry. To turn it off, set `HYPERFRAMES_NO_TELEMETRY=1`.

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
