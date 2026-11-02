# Review: reel 01 in HyperFrames

## Your ride footage (2 Nov)
- **The footage:** your 31 Oct group-ride clip (`assets/ride.mp4`, made upright, 1080×1920, a keyframe every second, muted) plays under the whole reel. The hook opens on the steady selfie stretch (from 20.3 s), so your real face is the thumbnail. The data cards sit on a dark scrim with glass panels over the ride, at 0.91× so the 29.8 s clip covers all 32.8 s of cards. The CTA returns to the selfie (from 8.6 s).
- **Layout around your face:** the hook and CTA keep the over-the-presenter layout. The CTA box moves to the top (270 px), and those two beats have no captions, because the face fills the lower half and their cards already show the line in big type.
- **Tag:** "AI-generated voiceover" (the footage is real). The ride's own audio is wind noise, so it is left out.
- **Punch-in:** the hook punch-in (1.08×) now lands on the footage at "back off!".
- **Size:** `out/reel_footage.mp4` is about 35 MB at delivery quality, fine for Instagram.

## Punchier voiceover (2 Nov)
- **Feedback:** the first narration felt flat for a reel. The script is rewritten into short lines with questions and exclamations, and read faster (`--speed 1.2`). The gaps between lines are cut to 0.3 s, plus a 0.6 s beat after the hook so its card meets the reading floor. The reel went from 58 s to 42.5 s.
- **Retimed scenes:** week, verdict, gains, CTA and the hook punch-in are retimed to the faster read, so every number lands while it is spoken (checked against the caption timing on a phone-width review sheet).
- **Music:** none in the file, because every music source is blocked here. You chose to add trending audio in the Instagram app at 15–25% under the voice.

## Voiceover version (2 Nov)
- **Narrator:** no presenter. The free local Kokoro voice `am_michael` reads each beat's `say` line. You chose it from four samples in `voice-samples/`. HeyGen voices needed a sign-in and are blocked in this environment.
- **Timing:** each beat lasts exactly as long as its line (0.45 s gaps, 1.6 s tail). Captions run inside each line's measured window, not estimates. Without word timestamps, the timing within a line is still proportional to character count.
- **Hook and CTA:** both have a `mode: card` layout: a full-screen ground, a label, and the four tools listing in as they're named. The CTA box lands at 3.6 s to meet "Comment COACH".
- **Measured, not heard:** narration is loudness-normalised to −16 LUFS. Michael is slower than the twin estimates, so some reveals in the week and pipeline scenes lead the words by about a second.
- **Labels:** `.r-label` now sets its own font, so labels outside the data scenes no longer fall back to serif.

## 2 Nov update
- **Numbers:** refreshed from intervals.icu: form −5 (was −39), race in 5 days, +14 on race day, 60-min power +4.3%. The coach's call is now "maintain reduced load and freshness", so the hook says "BACK OFF." and the verdict reads "Keep it light. Stay fresh."
- **Colours follow the data:** form uses intervals.icu's bands (red only under −30). The verdict hides its "0" label when today's marker sits next to it. The second power result is 1-min power, because 20-min power was flat.
- **Sound effects:** added from the media-use library (Pixabay licence) on visible actions, quiet under the voice, alternating between two audio lanes. Placed, not heard. Music was offered, not added, because it needs a HeyGen sign-in.
- **Punch-in:** a hard punch-in on the twin (1.08×) at "Five days before my race" ends the hook's static hold.
- **Captions:** numbers and shouted words (BACK OFF, COACH) are coloured lime.

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
