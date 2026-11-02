# Review: reel 01 in HyperFrames

## Clean look: one font, no boxes (2 Nov)
- **One type system:** every word on screen is Montserrat (400–900, SIL OFL, `assets/fonts/`, declared in `reel.css`), in butter yellow (`--ink` and `--lime` are both #FFE68F). Highlights (Stay fresh., +4.3%, caption numbers) are white. Form keeps its meaning colours: red, amber and green.
- **No dark layers:** in footage mode the scrim, panels, disclosure tag background, box borders and caption outline are all gone. The butter pills (the 381/183 pill, THAT'S ME, AI coach, Comment COACH) stay, as they aren't dark.
- **Legibility without boxes:** a three-layer soft text shadow, bold full-strength secondary lines, and a gentle footage grade (`footage.grade`: `eq=brightness=-0.07:contrast=1.08:saturation=1.05`). HyperFrames still reports 19 contrast warnings (median about 2.1:1 against bright sky). They're kept on purpose because they come with the no-box look, and the snapshots read on a phone-width check. If any line doesn't read on your phone, the fix is a darker grade or bringing back a soft scrim.
- **Hook type:** the line is set at 52 px with a deliberate break, and the slam word at 136 px, so the hook clears your helmet.

## Caption style (2 Nov)
- **The look:** no background box. Butter yellow (#FFE68F) in Montserrat Black, all caps, with a 9 px dark outline painted behind the fill and a soft drop shadow, so it reads over bright road and sky. That's the heavy-caps style popular in CapCut and on creator reels. Numbers and SHOUTED words switch to white.
- **Entrance:** each group pops in (scale 0.82 → 1, 0.18 s, slight overshoot) in place of the earlier blur-in.
- **Font:** Montserrat 800/900 woff2 from the Fontsource npm package (SIL OFL), in `assets/fonts/` with its licence, loaded by `@font-face` in the captions composition, because HyperFrames can't fetch Google Fonts here.

## Music removed (2 Nov)
- **Your call:** both hook previews are rendered without the music bed. Music goes on in Instagram instead. `--music` and `tools/make_music.py` stay available. The look-ahead truncation fix (fixed gain in place of loudnorm) still applies if it's used again.

## Music (2 Nov)
- **Source:** every music source is blocked here (HeyGen catalogue, Pixabay, Openverse, Hugging Face for MusicGen), so `tools/make_music.py` composes an original track from scratch, with no samples. It's seeded, so it's reproducible. Kick, clap, hats, an eighth-note bass, a plucked i–VI–III–VII arpeggio and a pad, with kick sidechain pumping. The tempo is snapped (103.7 BPM) so the drop and a riser land on the hook→setup cut.
- **Mix:** the music is normalised to −24 LUFS, then sidechain-compressed by the narration (about 10 dB more under speech, recovering in pauses). It plays as `<audio id="music">` on track 6. The rendered reel measures −16.4 LUFS integrated, −1.5 dBFS true peak, LRA 2.2.
- **Measured, not heard:** I checked the waveform, spectrogram and levels. Nobody has listened to it yet. If it doesn't suit, rebuild without `--music` and use Instagram's trending audio.

## Focus on you (2 Nov)
- **Correction:** you are the rider in white *ahead* of the camera, not the camera holder. Earlier versions opened and closed on his selfie and called it "your face". That is now fixed in both cuts.
- **The focus clip:** `footage.segments` in the timelines keeps only the shots of you (0–6.5 s and 26.2–29.8 s of the original), cut from the 720p original in `footage/`. Each is cropped 1.5× around a keyframed track of your position, so you sit centred and 66% down the frame, below the hook box. `assets/ride.mp4` is that 10.4 s clip.
- **Hook:** opens on the second stretch at 0.79× with a "THAT'S ME" marker (0.4–2.6 s) pointing at you. Behind the cards the clip runs at 0.67× in the 25 s cut. The 42 s cut repeats it rather than slowing below 0.6×. The CTA uses the first stretch.
- **Measured, not tracked automatically:** your position was read off gridded frames, about one per 0.6–0.8 s. If you shift between keyframes you can drift about 5% off centre.

## 25-second cut (2 Nov)
- **Beats:** `timeline_25s.json` keeps hook, setup, verdict, payoff and CTA, with shorter lines. Pauses after the verdict, payoff and CTA bring it to 24.8 s.
- **Pace:** the setup and verdict scenes take a `pace` variable (0.6 and 0.75 here) that scales their reveal times, and their sound effects with them. The 42-second version keeps pace 1.
- **Which version is loaded:** `index.html` is whichever cut was built last. Rebuild with `--timeline` to switch.

## Your ride footage (2 Nov, superseded by "Focus on you" above)
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
