# Reel 01: "My AI coach told me to back off"

**Format:** Instagram Reel, 9:16, about 50 seconds
**Presenter:** your AI digital twin, speaking to camera
**Story:** the AI coach reads your Garmin and Strava data through intervals.icu. Five days before your A race, it tells you to keep the load low. Then it shows why: you'll arrive at the race fresh, and your power is going up.
**Data:** your real intervals.icu numbers for 27 Oct–2 Nov 2026, pulled on 2 Nov (see `data.json`).

> **Post on 2 Nov, or update the day count.** The hook says "five days before my race", and the race is on 7 Nov. If you post on another day, change "Five" in `twin_script.txt` and `days_to_go` in `data.json`. Then re-pull the numbers, because form changes daily.

## Beat sheet

| # | Time | Twin says | On screen |
|---|------|-----------|-----------|
| 1 · Hook | 0:00–0:05 | "My AI coach just told me to back off. Five days before my race." | Twin full frame with a punch-in on "Five days". Top box: **My AI coach told me to BACK OFF.** · "5 days before my A race" |
| 2 · Setup | 0:05–0:14 | "Here's the setup. My Garmin and Strava both feed into intervals.icu, which turns every ride into fitness, fatigue and form." | Flow diagram: Garmin + Strava → intervals.icu → AI coach. The twin shrinks into a bubble, bottom left |
| 3 · The coach | 0:14–0:21 | "Then I connected an AI coach to it. It reads my power, heart rate and training load every single day." | What it reads: Power, Heart rate, Training load, Fitness, Fatigue, Form, Race calendar |
| 4 · The week | 0:21–0:30 | "This week I rode 7 hours and 239 km. Fitness 72. Fatigue 77. Form minus 5." | One number at a time: **7.1 h** → **239 km** → **−5** ("form — almost fresh"), with Fitness 72 / Fatigue 77 |
| 5 · Verdict | 0:30–0:41 | "The verdict? Keep it light. Stay fresh. If I hold back now, I start my race on 7 November at +14 form. Right in the sweet spot." | **Keep it light. Stay fresh.** Form gauge: the marker moves from −5 today to +14 on race day, inside the +8 to +18 target band |
| 6 · Payoff | 0:41–0:46 | "And the work is paying off. My one-hour power is up 4% in three months." | 60-min power **+4.3%** (219 W); 1-min power +4.0% |
| 7 · CTA | 0:46–0:52 | "Garmin, Strava, intervals, and an AI coach on top. Comment COACH and I'll send you my exact setup." | The twin grows back to full frame. Lime box: **Comment "COACH"** |

The timings are estimates. Building with `--auto-sync` moves each beat to the pauses in your twin's audio.

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

## Sound

Subtle effects mark visible actions:
- a bass hit on "BACK OFF."
- a whoosh as the twin shrinks
- pops for the AI coach pill, the first chip and the CTA
- a ping when form lands
- a chime when the marker reaches the sweet spot
- a sparkle on the power gain

They come from the HyperFrames sound library (Pixabay licence, no attribution needed). There's no music yet: HyperFrames' music catalogue needs a HeyGen sign-in.

## Disclosure

The presenter is an AI-generated version of you. The hook and CTA cards carry a small "AI-generated digital twin" tag. When you post, also turn on Instagram's **AI info** label (Advanced settings → "Add AI label"). Meta asks for this on realistic AI-generated video.
