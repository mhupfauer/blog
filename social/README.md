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

## Creatives (AI-generated)

Square 1080x1080 feed images live in `linkedin/out/creative/<post-slug>.png`. Unlike the quote cards and carousel, these are **not** rebuildable from `linkedin/build/` — they come from `scripts/gen-social-creative.py`, which is gitignored because it carries an API key, and image generation is not deterministic. The committed PNG is the master; re-running produces a different image.

```sh
./scripts/gen-social-creative.py <post-slug> "<visual concept>" --variants 2
```

Two things that matter, both learned by getting them wrong first:

- Use `gpt-image-2.5-flare`, not `gpt-image-2.5-sunburst`. Sunburst draws much finer line work, which moires into a flat grey block the moment LinkedIn rescales the image to feed width — the motif disappears entirely.
- The script's `FRAMING` prompt block forces the motif to fill ~70% of the frame and to survive being scaled to 300px. Without it you get an elegant small motif with lots of negative space that reads as nothing in a feed. The blog *cover* style guide optimises for a wide hero image on a white page; a feed creative has a different job and needs the accent colour to carry at thumbnail size.

