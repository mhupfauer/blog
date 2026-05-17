# CLAUDE.md

Project memory for this repo. Read once at the start of every session — most of what's here is the result of corrections from prior sessions, not preferences I'd want to re-derive.

## What this is

Personal blog at <https://hupfauer.one>, built with Hugo + PaperMod theme (vendored as a git submodule at `themes/PaperMod`). Source on GitHub at `mhupfauer/blog`, deployed to a VPS via a cron-pulled rebuild script — there is no CI, the cron is the deploy. New posts go live within minutes of `git push origin main` landing in the cron window.

## Voice and content rules

These are durable preferences. Do not violate them without explicit per-task instruction.

- **Lowkey.** Personal site, personal opinions. No grand titles, no employer name, no "Head of AI Security at KPMG." The home tagline is deliberately understated.
- **KPMG is off-limits in body copy.** It appears in the Klardenker links on `content/elsewhere.md` because the article URLs contain it — that's unavoidable. Don't reintroduce it elsewhere.
- **Writing register:** direct, technical, willing to make a contrarian claim and defend it. Editorial more than corporate. Comfortable cutting throat-clearing. No bullet lists where a paragraph would do.
- **No emojis anywhere unless explicitly asked** (true site-wide, not just in markdown).

## The trilogy

The three posts under `content/posts/` form a deliberate trilogy with a single thesis: probabilistic recognizers (input-side detection, defensive prompt injection, auto-mode classifiers) are sensors, not controls; identity scoping, sandboxing, and human-in-the-loop on irreversible actions are the actual controls. If you write a fourth post in this thread, it should advance the thesis or call out a new instance — do not just restate.

- `identity-is-the-control-plane.md` — the foundational post
- `salting-your-own-well.md` — the symmetric case (defender side)
- `auto-mode-is-a-sensor-too.md` — the developer-tool case

## Posting workflow norms

When asked to write a new post, the established workflow is:

1. Draft in `content/posts/<slug>.md`.
2. Set frontmatter `cover.image: "/covers/<slug>.png"` and reserve the cover.
3. Dispatch parallel critique agents against the draft. The user's preferred reviewer set is `gpt-5.5`, `gpt-5.4`, and `gpt-5.3-chat-latest` via the OpenAI Chat Completions API. Run all three in parallel. Their critiques converge sharply — treat unanimous feedback as binding, 2-of-3 as strong, individual as suggestion.
4. Revise based on the consolidated critique. Do *not* push between draft and revision — the user sees the result, not the iterations.
5. Generate a cover image via `./scripts/gen-cover.py <slug> "<concept>" "<alt>"` (gitignored local script with the OpenAI key hardcoded; bakes in the style guide and writes to `static/covers/<slug>.png`). Style guide for covers, applied across all posts so the site reads coherent:
   - Deep ink black background (`#0A0A0A`)
   - Off-white geometric forms, thin precise strokes
   - One muted accent: warm rust / clay orange (`~#C25A2E`)
   - No text, no logos, no faces, no real-world objects
   - Single calm motif, generous negative space, vector-illustration aesthetic
6. Commit and push to `main`.

## Backdating gotcha (LEARNED THE HARD WAY)

`hugo.toml` has `buildFuture = false` and `timeZone = "Europe/Berlin"`. A post dated `2026-05-18` with no time is parsed as midnight Berlin (= 22:00 UTC the day before). If the cron rebuild runs after that moment, fine. If the post's intent is "right now" and the local wall clock is just past midnight Berlin, the post is several hours in the *future* UTC and Hugo will silently skip it — the file builds without errors, just produces no output page.

**Rule:** if the post is meant to be live immediately and the current Berlin wall clock is between 00:00 and ~02:00, either backdate it to the previous day or include an explicit time at least a few hours in the past.

## SEO and frontmatter conventions

Every post frontmatter must carry:
- `title`, `date`, `draft: false`, `tags`, `keywords`, `description`, `summary`, `canonicalURL`, `cover` block (with `image`, `alt`, `hidden`, `relative`)

The site-wide config in `hugo.toml` handles the rest (sitemap, robots.txt at `layouts/robots.txt`, OG card defaults via `params.images`, breadcrumbs, schema.org `Person`).

## History rewrites are allowed

The user has previously asked me to rewrite git history to scrub specific content (`AADS` mentions, in that case). For a personal repo with no other contributors, force-pushing a rewritten history is acceptable when explicitly requested. Do not do it unprompted — but do not refuse when asked.

GitHub keeps orphaned commits reachable by direct SHA for ~90 days after a force-push. Mention this when rewriting; if the user wants immediate purge, point them at GitHub support.

## File layout

```
content/
  posts/                    # the trilogy and future posts
  elsewhere.md              # writing, speaking, recognition, profiles
  imprint.md                # German Impressum (TMG §5)
  search.md                 # PaperMod fuse.js search page
hugo.toml                   # all site config (SEO, menu, params)
layouts/robots.txt          # custom robots.txt with sitemap pointer
static/
  covers/                   # per-post cover images
  og-default.png            # fallback OG card
  favicon.ico / .png / apple-touch-icon.png
themes/PaperMod/            # submodule, do not modify directly
archetypes/default.md       # `hugo new` template
```

## What not to do

- **Do not install Hugo locally** to test builds. The user has explicitly declined. If you need to diagnose a build problem, read frontmatter and config carefully or ask the user to share the deploy script output.
- **Do not write planning, decision, or analysis documents** in the repo. Work from conversation context. CLAUDE.md is the exception — it is for the next agent, not for the user.
- **Do not over-explain in commit messages.** One concise line stating what changed and why. The user reads diffs, not git log essays.
