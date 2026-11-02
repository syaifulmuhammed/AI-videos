# Reel 01: "My AI coach told me to back off"

**Format:** Instagram Reel, 9:16, about 50 seconds
**Presenter:** an AI voiceover (Kokoro voice "Michael") over full-screen cards. The digital-twin version is still buildable with `--twin`
**Story:** the AI coach reads your Garmin and Strava data through intervals.icu. Five days before your A race, it tells you to keep the load low. Then it shows why: you'll arrive at the race fresh, and your power is going up.
**Data:** your real intervals.icu numbers for 27 Oct–2 Nov 2026, pulled on 2 Nov (see `data.json`).

> **Post on 2 Nov, or update the day count.** The hook says "five days before my race", and the race is on 7 Nov. If you post on another day, change "Five" in `twin_script.txt` and `days_to_go` in `data.json`. Then re-pull the numbers, because form changes daily.

## Beat sheet (voiceover version, about 42 s)

Narrated by the local AI voice "Michael" (`am_michael`) at 1.2× speed. Lines are short and punchy, with questions and exclamations, which this voice reads with more energy. Each card lasts exactly as long as its line.

| # | Narrator says | On screen |
|---|---------------|-----------|
| 1 · Hook | "Five days before my race, my AI coach told me to back off!" | Full-screen card: **My AI coach told me to BACK OFF.** · "5 days before my A race", tightening on "back off!" |
| 2 · Setup | "Here's my setup. Garmin and Strava sync every ride into intervals.icu. It tracks fitness, fatigue and form." | Flow: Garmin + Strava → intervals.icu → AI coach |
| 3 · The coach | "Then I plugged in an AI coach. It reads my power, heart rate and training load. Every single day!" | What it reads: Power, Heart rate, Training load, Fitness, Fatigue, Form, Race calendar |
| 4 · The week | "This week? Seven hours. 239 K. Fitness 72, fatigue 77, form minus 5." | One number at a time: **7.1 h** → **239 km** → **−5**, with Fitness 72 / Fatigue 77 |
| 5 · Verdict | "So the verdict? Keep it light, stay fresh! Hold back now, and I hit race day at +14 form. Right in the sweet spot." | **Keep it light. Stay fresh.** The form marker moves from −5 to +14, into the +8 to +18 band |
| 6 · Payoff | "And it's working! My one-hour power is up 4% in three months." | **+4.3%** 1-hour power; 1-min power +4.0% |
| 7 · CTA | "Want my exact setup? Comment COACH and I'll send it to you!" | Garmin + Strava + intervals.icu + AI coach, then the lime **Comment "COACH"** box |

The same lines are in `twin_script.txt` for the digital-twin version.

## 25-second cut (`timeline_25s.json` → `out/reel_25s.mp4`)

Five beats, built for cold viewers: the coach and week beats (the most jargon) are gone.

| # | Narrator says | On screen |
|---|---------------|-----------|
| 1 · Hook | "Five days before my race, my AI coach told me to back off!" | Your selfie footage, with **My AI coach told me to BACK OFF.** at the top |
| 2 · Setup | "Garmin and Strava sync to intervals.icu. An AI coach reads it every day." | Garmin + Strava → intervals.icu → AI coach, over the ride |
| 3 · Verdict | "The verdict? Keep it light! Hold back now, and I hit race day at +14 form. Sweet spot." | **Keep it light. Stay fresh.** The marker goes from −5 to +14 in the sweet spot |
| 4 · Payoff | "And it's working! One hour power, up four percent." | **+4.3%** 1-hour power |
| 5 · CTA | "Want my setup? Comment COACH!" | Your selfie footage, with the **Comment "COACH"** box at the top |

Build: `python3 tools/hf_reel.py reels/01-ai-coach-intervals --timeline timeline_25s.json --voice am_michael --render --out reels/01-ai-coach-intervals/out/reel_25s.mp4`

## Where each number comes from

All numbers come from the intervals.icu weekly report pulled on 2 Nov 2026:

- **7.1 h, 239 km, 481 TSS:** 7-day training volume, 27 Oct–2 Nov
- **Fitness 72 / Fatigue 77 / Form −5:** CTL 71.6, ATL 76.9, TSB −5.3
- **"Keep it light. Stay fresh.":** a plain-English version of the coach's directive. The directive reads "Maintain training structure", with the taper adjustment "maintain reduced load and freshness"
- **+14 on race day, target +8 to +18:** projected race-day TSB 13.7. Readiness: READY
- **+4.3% 60-min power, +4.0% 1-min power:** best efforts in the last 85 days compared with the previous 85. 20-min power is unchanged (0.0%), so the reel shows 1-min power instead

"Three months" in the voiceover is a rounding of 85 days. The card states the exact window.

### What changed since the 30 Oct version

Form went from −39 to −5 after the lighter days. The coach's call moved from "reduce load, prioritise recovery" to "maintain low load, stay fresh", so the hook says "back off" rather than "stop".

## Hook alternatives (A/B test these)

1. "My AI coach just told me to back off. Five days before my race." *(current)*
2. "I gave an AI my Garmin data. Its instruction five days before my race? Do less."
3. "Form: minus 5. Race in five days. Here's what my AI coach said."

## Sound and music

- **Sound effects:** quiet effects mark visible actions: a bass hit on "BACK OFF.", pops, a ping when form lands, a chime at the sweet spot and a sparkle on the power gain. They come from the HyperFrames library (Pixabay licence).
- **No music in the file:** add a trending song in the Instagram editor (Add audio → pick a track → Mix audio). Set the music to about 15–25% and leave the original audio at 100%, so the voice stays on top. Trending audio also helps reach.

## Disclosure

The narration is an AI-generated voice. The hook and CTA cards carry a small "AI-generated voiceover" tag (or "AI-generated digital twin" in the twin version). When you post, also turn on Instagram's **AI info** label (Advanced settings → "Add AI label"). Meta asks for this on realistic AI-generated video.
