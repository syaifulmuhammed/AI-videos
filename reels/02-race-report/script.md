# Reel 02: "Did the AI save my race?" (Part 2 race report)

**Status:** template, waiting for the race (Masters TT, Saturday 7 Nov). `data.json` → `result` holds **sample numbers for layout only**.

**Format:** about 20–25 s, 9:16. Same look as Part 1: Montserrat in butter yellow, no boxes, the "Michael" AI voiceover at 1.2×, your ride footage, no music (add trending audio in Instagram).

## Beats (`timeline_part2.json`)

| # | Narrator (finalised after the race) | On screen |
|---|-------------------------------------|-----------|
| 1 · Hook | "Last week I rode double my taper. My AI coach said back off. Did it save my race?" | "I rode double my taper. / The AI said back off." **RESULT?** · "Part 2 · race day", plus the THAT'S ME marker |
| 2 · Form | "Form: minus 39, then minus 5, and on the start line, plus [actual]." | The form chart moves −39 (30 Oct) → −5 (2 Nov) → actual race-day form in the sweet spot |
| 3 · Result | "[time]. [avg] watts average." plus one honest line on how it went | **Finish time**, avg power (% of FTP), normalised power, start-line form against the AI's +14 |
| 4 · CTA | "Want the AI setup that got me here? Comment COACH!" | **Comment "COACH"** over you riding |

## After the race (Sunday 8 Nov)

1. Pull the race from intervals.icu: the race activity (moving time, avg and normalised power, HR) and wellness on 7 Nov (TSB on the start line).
2. Fill `data.json` → `result` and the race-day form, and replace every "[after race]" line in `timeline_part2.json`.
3. Pick the story that's true:
   - **It worked** (form in the +8 to +18 band and a good ride): "Did it save my race? Yes." Hook word: "IT WORKED."
   - **Mixed** (good form but a so-so result, or the reverse): say what happened. "Fresh legs, tough day" still makes a reel worth posting.
   - **It didn't** (flat, or form off target): own it. Honest reels earn trust, and "what I'd change" is a strong Part 3.
4. Render, review, and update the caption and the DM reply.

**Footage:** this uses the 31 Oct clip of you until race footage arrives. A race clip (start line, on course, finish) makes Part 2 much stronger. Upload it and I'll cut and track it the same way.

## Build

`python3 tools/hf_reel.py reels/02-race-report --timeline timeline_part2.json --voice am_michael --render --out reels/02-race-report/out/reel_part2.mp4`
