# Review: reel 01 in HyperFrames

## Creative calls
- **Single video file:** the twin plays as one `<video>`. For the data beats it shrinks into a bubble at the bottom left, ringed in lime, and for the CTA it grows back into the full frame. The one video element carries both the voice and the picture.
- **Week beat:** shows one number at a time on a single stage (11.1 h → 372 km → form −39), with fitness and fatigue arriving as they are spoken. The original version used a grid of stat tiles, which HyperFrames' guidance lists as a sign of auto-generated design.
- **Verdict chart:** builds in reading order: frame, zero line, target band, today's marker, then the marker travels to race day.
- **Sources:** every data scene has a source line. The hook frame 0 already shows the headline, so the thumbnail is never empty.
- **Registry:** reviewed `count-up`, `chart-story`, `mk-progress-stat`, `caption-highlight` and `number-pop-in`. They are all landscape or fixed-key blocks, so I kept `count-up`'s frame-exact counting technique (in `assets/reel.js`) and wrote portrait scenes.
- **Not built:** no alternative storylines. The script was already approved.

## Measured vs looked at
- **Checks:** `hyperframes check` passes. Snapshots were taken at every beat, every cut and phone width (360 px).
- **Rendered with the placeholder twin only:** the real twin's framing hasn't been seen. If the face doesn't sit at about 30% of the frame height, adjust `pip` in `timeline.json`.
- **Sound not heard:** the placeholder audio is noise bursts.

## Weakest shot
The hook. The box covers the top of the placeholder's head. With a real HeyGen framing (head lower, more headroom) it should clear the face. If not, move `#hook-box` up or shrink it.

## Warnings kept on purpose
- **`timeline_track_too_dense` on captions:** HyperFrames' guidance asks for one captions host holding every group.
- **`contrast_aa_failure` on the coach title:** the words are mid-reveal (grey to white) at the sampled instant. They land white within 0.7 s.

## Regenerating
`python3 tools/hf_reel.py reels/01-ai-coach-intervals --twin twin.mp4 --auto-sync --render` rewrites `index.html`, `compositions/captions.html` and `assets/twin.mp4` from `timeline.json` and `data.json`. It never touches the scene files.
