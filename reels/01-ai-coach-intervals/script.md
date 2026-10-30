# Reel 01: "My AI coach told me to stop"

**Format:** Instagram Reel, 9:16, about 50 seconds
**Presenter:** your AI digital twin, speaking to camera
**Story:** the AI coach, reading Garmin and Strava data through intervals.icu, tells you to back off 8 days before your A race. Then it shows why: you'll arrive at the race fresh, and your power is going up.
**Data:** your real intervals.icu numbers for 24–30 Oct 2026 (see `data.json`).

> **Post by 6 Nov.** The hook says "eight days before my race" and the race is on 7 Nov. If you post later than 31 Oct, change "Eight" in `twin_script.txt` and `days_to_go` in `data.json` so they match the day you post.

## Beat sheet

| # | Time | Twin says | On screen |
|---|------|-----------|-----------|
| 1 · Hook | 0:00–0:05 | "My AI coach just told me to stop training. Eight days before my race." | Twin full frame. Top box: **My AI coach told me to STOP.** · "8 days before my A race" |
| 2 · Setup | 0:05–0:14 | "Here's the setup. My Garmin and Strava both feed into intervals.icu, which turns every ride into fitness, fatigue and form." | Flow diagram: Garmin + Strava → intervals.icu → AI coach. Twin in a circle, bottom left |
| 3 · The coach | 0:14–0:21 | "Then I connected an AI coach to it. It reads my power, heart rate and training load every single day." | What it reads: Power, Heart rate, Training load, Fitness, Fatigue, Form, Race calendar |
| 4 · The week | 0:21–0:30 | "This week I rode 11 hours and 372 km. Fitness 77. Fatigue 116. Form minus 39." | Count-up: **11.1 h · 372 km · 795 TSS**, then tiles: Fitness 77 / Fatigue 116 / Form −39 |
| 5 · Verdict | 0:30–0:41 | "The verdict? Reduce load. Prioritise recovery. If I back off now, I start my race on 7 November at +13 form. Right in the sweet spot." | **Reduce load. Prioritise recovery.** Form gauge: the marker moves from −39 today to +13 on race day, inside the +8 to +18 target band |
| 6 · Payoff | 0:41–0:46 | "And the work is paying off. My one-hour power is up 10% in three months." | 60-min power **+10.1%** (219 W), 20-min **+3.6%** (256 W) |
| 7 · CTA | 0:46–0:52 | "Garmin, Strava, intervals, and an AI coach on top. Comment COACH and I'll send you my exact setup." | Twin full frame. Lime box: **Comment "COACH"** |

The timings are estimates. Run `build_reel.py` with `--auto-sync` and it moves each beat to the pauses in your twin's audio.

## Where each number comes from

All numbers come from the intervals.icu weekly report pulled on 30 Oct 2026:

- **11.1 h, 372 km, 795 TSS:** 7-day training volume, 24–30 Oct
- **Fitness 77 / Fatigue 116 / Form −39:** CTL 76.9, ATL 115.6, TSB −38.7
- **"Reduce load and prioritise recovery":** the coach's directive. Phase: taper, because your A race is 8 days away
- **+13 on race day, target +8 to +18:** projected race-day TSB 12.6. Readiness: READY
- **+10.1% 60-min power, +3.6% 20-min power:** best efforts in the last 85 days compared with the previous 85

"Three months" in the voiceover is a rounding of 85 days. The card states the exact window.

## Hook alternatives (A/B test these)

1. "My AI coach just told me to stop training. Eight days before my race." *(current)*
2. "I gave an AI my Garmin data. Its first instruction? Do less."
3. "Form: minus 39. My AI coach saw this before I did."

## Disclosure

The presenter is an AI-generated version of you. The hook and CTA cards carry a small "AI-generated digital twin" tag. When you post, also turn on Instagram's **AI info** label (Advanced settings → "Add AI label"). Meta asks for this on realistic AI-generated video.
