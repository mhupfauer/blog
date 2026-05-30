# LinkedIn one-shot poster

Posts a single markdown atom from `social/linkedin/posts/` to your own
LinkedIn feed, with optional image or video attachment, and an
auto-derived first-comment link. No scheduler, no campaign engine — you
run it the moment you would have copy-pasted into the LinkedIn UI.

Carousels (PDFs) are deliberately *not* supported. LinkedIn's document
upload endpoint is gated behind the Marketing Developer Platform partner
program and is not available to a personal developer account.

## One-time setup

### 1. Create the LinkedIn Developer App

1. Go to <https://www.linkedin.com/developers/apps> and click **Create app**.
2. Fill in the basics. The "verified company page" requirement can be
   satisfied by any LinkedIn Company page you administer — even a stub.
3. Open the app, switch to the **Products** tab, and add both:
   - **Sign In with LinkedIn using OpenID Connect** (auto-approved; gives
     you the `openid` and `profile` scopes plus `/v2/userinfo` so the
     script can fetch your person URN).
   - **Share on LinkedIn** (auto-approved as of late 2025; gives you the
     `w_member_social` scope for posting on your own behalf).
4. Open the **Auth** tab and add a redirect URL — `http://localhost:8765/callback`.
5. Copy the **Client ID** and **Client Secret**.

If "Share on LinkedIn" is greyed out and asks for review for your region,
that is the friction point. Personal accounts in some regions need to
file a brief request — usually approved within a few business days.

### 2. Drop the app credentials

```sh
mkdir -p ~/.config/linkedin-poster
cat > ~/.config/linkedin-poster/app.json <<EOF
{
  "client_id":     "<CLIENT_ID>",
  "client_secret": "<CLIENT_SECRET>",
  "redirect_uri":  "http://localhost:8765/callback"
}
EOF
chmod 600 ~/.config/linkedin-poster/app.json
```

### 3. Authenticate (browser one-time)

```sh
python3 social/linkedin/poster/linkedin-post.py auth
```

This opens your default browser, you click "Allow", the script captures
the redirect, exchanges the code, fetches your person URN via OIDC, and
stores everything at `~/.config/linkedin-poster/token.json`. Tokens are
valid for 60 days; re-run `auth` to refresh.

```sh
python3 social/linkedin/poster/linkedin-post.py whoami
# person: urn:li:person:XXXXXXXX
# token valid for: 59d 23h
```

## Firing a post

### Text-only (thesis)

```sh
python3 social/linkedin/poster/linkedin-post.py post \
  --file social/linkedin/posts/01-thesis.md \
  --lang en
```

### With an image (quote card)

```sh
python3 social/linkedin/poster/linkedin-post.py post \
  --file social/linkedin/posts/04-quote-shared-account.md \
  --lang en \
  --media social/linkedin/out/quotes/shared-account.png
```

### With a video (audiogram)

```sh
python3 social/linkedin/poster/linkedin-post.py post \
  --file social/linkedin/posts/03-audiogram.md \
  --lang en \
  --media social/linkedin/out/audiograms/bench-en.mp4
```

### Useful flags

| Flag | Effect |
| ---- | ------ |
| `--dry-run` | Print the post body and stop. Does not call the LinkedIn API. |
| `--no-comment` | Skip auto-posting the link as a first comment. |
| `--comment-link URL` | Override the first-comment link. |

## What the script does

1. Reads the chosen `## English` or `## Deutsch` section of the markdown,
   extracts the blockquote text, and looks up the **First comment** /
   **Erster Kommentar** URL right below it.
2. If a `--media` is given, calls LinkedIn's `images?action=initializeUpload`
   or `videos?action=initializeUpload`, PUTs the binary (multi-part for
   videos), and finalises the upload.
3. Creates the post via `POST /rest/posts` and prints the URN + feed URL.
4. If a first-comment link was found (or `--comment-link` was passed),
   posts that as a comment on the new post.

LinkedIn version pinned: `LinkedIn-Version: 202405`. Bump the constant
at the top of the script when LinkedIn deprecates that.

## What it does not do

- No scheduling. Run it at the exact moment you want the post to go live.
- No carousel (PDF document) uploads — gated by partner program.
- No edit or delete. Use the LinkedIn web UI for those.
- No reach analytics. Use the LinkedIn web UI.

## Files written

- `~/.config/linkedin-poster/app.json` — your LinkedIn Developer App
  credentials. Mode 600. Not in this repo.
- `~/.config/linkedin-poster/token.json` — access token, refresh token,
  expiry, cached person URN. Mode 600. Not in this repo.

Nothing the script writes ever lands inside the blog repository.
