# social/

Distribution material for posts on this blog. Tracked in git for versioning and re-use; **not** picked up by the Hugo build, so nothing in here is ever published to <https://hupfauer.one>.

Currently scoped to LinkedIn — see `linkedin/`.

## Cadence calendar — "Which agent bricked prod?"

Spread across roughly two weeks. Never two long-form posts back to back. Alternate language. The link to the full post goes in the first comment, never the post body.

| Day  | Atom                                 | Language | Format            | File                                          |
| ---- | ------------------------------------ | -------- | ----------------- | --------------------------------------------- |
| 1    | Thesis post (the two-question test)  | EN       | text              | `linkedin/posts/01-thesis.md`                 |
| 3    | Thesis post                          | DE       | text              | `linkedin/posts/01-thesis.md`                 |
| 5    | Audiogram — OT trajectory            | EN       | native video      | `linkedin/posts/03-audiogram.md` + mp4        |
| 7    | Quote — *shared account with an LLM* | EN       | image + paragraph | `linkedin/posts/04-quote-shared-account.md`   |
| 8    | Audiogram — OT trajectory            | DE       | native video      | `linkedin/posts/03-audiogram.md` + mp4        |
| 10   | Carousel — three identity collapses  | EN       | document carousel | `linkedin/posts/02-carousel.md` + PDF         |
| 12   | Quote — *living off the chatbot*     | EN       | image + paragraph | `linkedin/posts/04-quote-living-off-chatbot.md` |
| 14   | Quote — *setpoint vs. Jira*          | EN/DE    | image + paragraph | `linkedin/posts/04-quote-setpoint-vs-jira.md` |

Tuesday and Thursday mornings (≈ 08:30 CET) are the highest-reach slots for B2B/security content. Avoid Mondays and Fridays.

## Per-post discipline

For each post: read it once aloud before posting — anything that sounds like a press release goes. The link in the first comment, not in the post body. Reply to substantive comments within the first 60–90 minutes; the LinkedIn algorithm treats early author engagement as a strong relevance signal. Do not seed reactions, do not run a pod.

## Building the visuals

The visual assets (PNG quote cards, PDF carousel, MP4 audiograms) are committed under `linkedin/out/` so they are ready to upload without re-running anything. To regenerate (e.g. after a copy tweak) the build scripts in `linkedin/build/` will redo them in place. Each script is idempotent and has no external dependencies beyond Pillow and ffmpeg.

```sh
python3 social/linkedin/build/build-quotes.py
python3 social/linkedin/build/build-carousel.py
python3 social/linkedin/build/build-audiograms.py
```

## Creatives

Square 1080×1080 feed images at `linkedin/out/creative/<post-slug>.png`, built by `linkedin/build/build-creative.py` like every other visual here — Pillow only, no credentials, deterministic, safe to re-run.

**Make the creative a chart, not an illustration.** The first attempt at this used image generation, and it looked like stock AI art: a handsome motif that carried no information. A feed image has room for exactly one idea, and the idea should be a number you can defend. The current creative is a unit chart — one square per CVE in KB5122871, 679 of them, with the single square that is under active exploitation ringed in rust. The insight is the picture.

Rules that came out of building it:

- **Numbers come from primary data.** The figures are counted from Microsoft's MSRC CVRF feed, not from press coverage. Anything on a public graphic gets verified first — the release-wide "966" is not the same as the 679 in one package, and putting the wrong one on a card invites a correction in the comments.
- **Check it at feed size before shipping.** Downscale to 500 / 300 / 160px and look. Headline must survive 300px; the accent mark must stay findable.
- **Validate the mark colours, don't eyeball them.** The grid grey was chosen with a palette validator against the rust accent: the first pick looked better but scored ΔE 7.9 under protanopia, which leaves a colourblind reader nothing but the ring. `#ABA79E` scores 15.8 and reads brighter anyway.
- **Give the accent a second cue.** The exploited cell is rust *and* ringed *and* named in the legend, so identity never rests on colour alone.

Typography and palette follow the quote cards: ink black ground, Georgia Italic headline in cream, Helvetica for kicker and legend, rust rule and corner mark.
