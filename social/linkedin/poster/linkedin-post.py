#!/usr/bin/env python3
"""
linkedin-post: one-shot LinkedIn poster for the content under
social/linkedin/posts/. Posts text + an optional PNG or MP4 attachment, then
optionally posts an auto-derived link as the first comment. Carousel PDFs
are NOT supported by this script — LinkedIn's document upload endpoint is
gated behind the Marketing Developer Platform partner program.

Subcommands:
  auth     One-time OAuth flow. Opens a browser, captures the redirect,
           exchanges for a member access token, stores it under
           ~/.config/linkedin-poster/.

  whoami   Prints the cached person URN and token expiry.

  post     Posts a markdown file. Options:
             --file PATH          markdown under social/linkedin/posts/
             --lang en|de         which section to post
             --media PATH         optional PNG/JPG/MP4 attachment
             --comment-link URL   override the first-comment link
             --no-comment         skip the first-comment step
             --dry-run            print what would be posted; do nothing

Setup: see README.md in this directory.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "linkedin-poster"
APP_CONFIG = CONFIG_DIR / "app.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

LI_VERSION = "202605"
LI_REST = "https://api.linkedin.com/rest"
LI_OAUTH = "https://www.linkedin.com/oauth/v2"
SCOPES = "openid profile w_member_social"

POST_MAX_CHARS = 3000  # LinkedIn share commentary cap


# --------------------------------------------------------------------- io ---
def die(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def load_app() -> dict:
    if not APP_CONFIG.exists():
        die(
            f"missing {APP_CONFIG}\n\n"
            "Create it with the JSON shape:\n"
            '  {\n'
            '    "client_id": "...",\n'
            '    "client_secret": "...",\n'
            '    "redirect_uri": "http://localhost:8765/callback"\n'
            '  }\n\n'
            "See README.md for how to provision the LinkedIn Developer App.",
        )
    return json.loads(APP_CONFIG.read_text())


def load_token() -> dict:
    if not TOKEN_FILE.exists():
        die("not authenticated. Run: linkedin-post.py auth")
    tok = json.loads(TOKEN_FILE.read_text())
    if tok.get("expires_at", 0) < time.time():
        die("token expired. Run: linkedin-post.py auth")
    return tok


def save_token(token_resp: dict, person_urn: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "access_token": token_resp["access_token"],
        "refresh_token": token_resp.get("refresh_token"),
        "expires_at": int(time.time()) + int(token_resp.get("expires_in", 60 * 86400)),
        "person_urn": person_urn,
    }
    TOKEN_FILE.write_text(json.dumps(payload, indent=2))
    os.chmod(TOKEN_FILE, 0o600)


def http_json(url: str, method: str = "GET", *, headers: Optional[dict] = None,
              body: Optional[bytes] = None) -> dict:
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            if not raw:
                return {"_headers": dict(r.headers)}
            data = json.loads(raw)
            data["_headers"] = dict(r.headers)
            return data
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        die(f"HTTP {e.code} {e.reason} for {method} {url}\n{body_text}")


# ----------------------------------------------------------------- auth ---
def cmd_auth(_args) -> int:
    app = load_app()
    state = secrets.token_urlsafe(16)
    auth_url = LI_OAUTH + "/authorization?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": app["client_id"],
        "redirect_uri": app["redirect_uri"],
        "state": state,
        "scope": SCOPES,
    })
    captured: dict = {}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass

        def do_GET(self):
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            captured.update(params)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<!doctype html><meta charset=utf-8>"
                             b"<title>OK</title><body style='font-family:sans-serif;"
                             b"background:#0c0c0d;color:#e9e6df;padding:3rem'>"
                             b"<h1>OK &mdash; you can close this tab.</h1></body>")

    parsed = urllib.parse.urlparse(app["redirect_uri"])
    port = parsed.port or 8765
    server = http.server.HTTPServer(("localhost", port), H)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Opening browser. Waiting on {app['redirect_uri']} …")
    webbrowser.open(auth_url)
    t0 = time.time()
    while "code" not in captured and "error" not in captured:
        if time.time() - t0 > 300:
            server.shutdown()
            die("timed out waiting for OAuth callback")
        time.sleep(0.4)
    server.shutdown()
    if "error" in captured:
        die(f"OAuth error: {captured.get('error')}: {captured.get('error_description', '')}")
    if captured.get("state") != state:
        die("state mismatch — possible CSRF, aborting")

    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": captured["code"],
        "redirect_uri": app["redirect_uri"],
        "client_id": app["client_id"],
        "client_secret": app["client_secret"],
    }).encode()
    token = http_json(
        LI_OAUTH + "/accessToken", "POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=body,
    )
    userinfo = http_json(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    person_urn = f"urn:li:person:{userinfo['sub']}"
    save_token(token, person_urn)
    print(f"\nAuthenticated as {person_urn}")
    print(f"Token expires in ~{token.get('expires_in', 0) // 86400} days")
    print(f"Stored at {TOKEN_FILE}")
    return 0


def cmd_whoami(_args) -> int:
    tok = load_token()
    remain = max(0, tok["expires_at"] - int(time.time()))
    print(f"person: {tok['person_urn']}")
    print(f"token valid for: {remain // 86400}d {remain % 86400 // 3600}h")
    if tok.get("refresh_token"):
        print("refresh_token: present")
    return 0


# ------------------------------------------------------- markdown parsing ---
LANG_HEADING = {"en": "English", "de": "Deutsch"}
LANG_COMMENT_LABEL = {"en": "First comment", "de": "Erster Kommentar"}


def parse_post_md(md_path: Path, lang: str) -> tuple[str, Optional[str]]:
    text = md_path.read_text()
    heading = LANG_HEADING[lang]
    m = re.search(
        rf"##\s+{re.escape(heading)}.*?\n(.*?)(?=\n---\s*\n|\n##\s|\Z)",
        text, re.DOTALL,
    )
    if not m:
        die(f"no '## {heading}' section in {md_path}")
    section = m.group(1)
    bq_lines: list[str] = []
    in_quote = False
    for line in section.split("\n"):
        s = line.rstrip()
        if s.startswith(">"):
            bq_lines.append(s[1:].lstrip())
            in_quote = True
        elif in_quote and not s.strip():
            bq_lines.append("")
        elif in_quote:
            break
    body = "\n".join(bq_lines).rstrip()
    # collapse leading/trailing blank lines and 3+ consecutive blanks
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    # LinkedIn renders markdown literally — strip *emphasis* and _emphasis_ so
    # the asterisks/underscores don't show up as typographic noise in the feed.
    body = re.sub(r"(?<!\w)\*([^\s*][^*]*?[^\s*]|\S)\*(?!\w)", r"\1", body)
    body = re.sub(r"(?<!\w)_([^\s_][^_]*?[^\s_]|\S)_(?!\w)", r"\1", body)

    label = LANG_COMMENT_LABEL[lang]
    cm = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(\S+)", section)
    first_comment = cm.group(1) if cm else None
    return body, first_comment


# ------------------------------------------------------------- uploads ---
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif"}
VID_EXT = {".mp4", ".mov"}


def _img_mime(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png",  ".gif": "image/gif",
    }.get(ext, "application/octet-stream")


def upload_image(token: str, person_urn: str, path: Path) -> str:
    init = http_json(
        LI_REST + "/images?action=initializeUpload", "POST",
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": LI_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        body=json.dumps({"initializeUploadRequest": {"owner": person_urn}}).encode(),
    )
    upload_url = init["value"]["uploadUrl"]
    image_urn = init["value"]["image"]
    binary = path.read_bytes()
    req = urllib.request.Request(
        upload_url, data=binary, method="PUT",
        headers={"Content-Type": _img_mime(path)},
    )
    try:
        with urllib.request.urlopen(req) as r:
            r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        die(f"image PUT failed: HTTP {e.code} {e.reason}\n{body[:400]}")
    return image_urn


def upload_video(token: str, person_urn: str, path: Path) -> str:
    size = path.stat().st_size
    init = http_json(
        LI_REST + "/videos?action=initializeUpload", "POST",
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": LI_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        body=json.dumps({
            "initializeUploadRequest": {
                "owner": person_urn,
                "fileSizeBytes": size,
                "uploadCaptions": False,
                "uploadThumbnail": False,
            }
        }).encode(),
    )
    val = init["value"]
    video_urn = val["video"]
    upload_token = val["uploadToken"]
    instructions = val["uploadInstructions"]
    etags: list[str] = []
    with path.open("rb") as f:
        for i, ins in enumerate(instructions, 1):
            first = int(ins["firstByte"])
            last = int(ins["lastByte"])
            f.seek(first)
            chunk = f.read(last - first + 1)
            req = urllib.request.Request(ins["uploadUrl"], data=chunk, method="PUT")
            try:
                with urllib.request.urlopen(req) as r:
                    r.read()
                    etag = r.headers.get("ETag") or r.headers.get("etag") or ""
            except urllib.error.HTTPError as e:
                die(f"video PUT part {i} failed: HTTP {e.code}\n{e.read().decode(errors='replace')}")
            print(f"  uploaded part {i}/{len(instructions)} ({last - first + 1} bytes)", flush=True)
            etags.append(etag.strip('"'))
    http_json(
        LI_REST + "/videos?action=finalizeUpload", "POST",
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": LI_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        body=json.dumps({
            "finalizeUploadRequest": {
                "video": video_urn,
                "uploadToken": upload_token,
                "uploadedPartIds": etags,
            }
        }).encode(),
    )
    return video_urn


# --------------------------------------------------------------- posting ---
def create_post(token: str, person_urn: str, text: str, media_urn: Optional[str]) -> str:
    body: dict = {
        "author": person_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if media_urn:
        body["content"] = {"media": {"id": media_urn}}
    raw = urllib.request.Request(
        LI_REST + "/posts",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": LI_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(raw) as r:
            r.read()
            post_urn = r.headers.get("x-restli-id") or r.headers.get("X-RestLi-Id")
    except urllib.error.HTTPError as e:
        die(f"post create failed: HTTP {e.code}\n{e.read().decode(errors='replace')}")
    if not post_urn:
        die("post create: no x-restli-id header in response")
    return post_urn


def post_comment(token: str, person_urn: str, post_urn: str, message: str) -> None:
    encoded = urllib.parse.quote(post_urn, safe="")
    body = {
        "actor": person_urn,
        "object": post_urn,
        "message": {"text": message},
    }
    http_json(
        f"{LI_REST}/socialActions/{encoded}/comments", "POST",
        headers={
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": LI_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
        body=json.dumps(body).encode(),
    )


# ----------------------------------------------------------------- main ---
def cmd_post(args) -> int:
    md = Path(args.file)
    if not md.exists():
        die(f"file not found: {md}")
    body, derived_link = parse_post_md(md, args.lang)
    if len(body) > POST_MAX_CHARS:
        print(f"warning: post is {len(body)} chars; LinkedIn cap is {POST_MAX_CHARS}", file=sys.stderr)

    media_path = Path(args.media) if args.media else None
    comment_link = args.comment_link or (derived_link if not args.no_comment else None)

    print(f"--- POST PREVIEW ({args.lang}) ---")
    print(body)
    print(f"--- end ({len(body)} chars) ---")
    if media_path:
        print(f"media: {media_path} ({media_path.stat().st_size // 1024} KB)")
    if comment_link:
        print(f"first comment link: {comment_link}")
    if args.dry_run:
        print("\n[dry-run] not posting.")
        return 0

    tok = load_token()
    media_urn = None
    if media_path:
        suffix = media_path.suffix.lower()
        if suffix in IMG_EXT:
            print(f"uploading image: {media_path.name} …", flush=True)
            media_urn = upload_image(tok["access_token"], tok["person_urn"], media_path)
        elif suffix in VID_EXT:
            print(f"uploading video: {media_path.name} ({media_path.stat().st_size // 1024} KB) …", flush=True)
            media_urn = upload_video(tok["access_token"], tok["person_urn"], media_path)
        else:
            die(f"unsupported media type: {suffix}. Use PNG/JPG/MP4. (PDFs require Marketing API.)")
        print(f"  media urn: {media_urn}")

    print("creating post …", flush=True)
    post_urn = create_post(tok["access_token"], tok["person_urn"], body, media_urn)
    encoded = urllib.parse.quote(post_urn, safe="")
    print(f"\nposted: {post_urn}")
    print(f"view:   https://www.linkedin.com/feed/update/{encoded}/")

    if comment_link:
        print("posting first-comment link …", flush=True)
        post_comment(tok["access_token"], tok["person_urn"], post_urn, comment_link)
        print("first-comment posted.")

    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="One-shot LinkedIn poster.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth").set_defaults(func=cmd_auth)
    sub.add_parser("whoami").set_defaults(func=cmd_whoami)
    post = sub.add_parser("post")
    post.add_argument("--file", required=True, help="markdown file under social/linkedin/posts/")
    post.add_argument("--lang", choices=["en", "de"], required=True)
    post.add_argument("--media", help="optional PNG/JPG/MP4 attachment")
    post.add_argument("--comment-link", help="override the first-comment URL")
    post.add_argument("--no-comment", action="store_true", help="skip first-comment posting")
    post.add_argument("--dry-run", action="store_true", help="print only; do not post")
    post.set_defaults(func=cmd_post)
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
