#!/usr/bin/env python3
"""
Render the LinkedIn creative for "You can't triage a bundle" at 1080x1080 PNG.

Scroll-stopper, not a document. One sentence and two words, at a size that
lands before anyone has decided whether to read. Everything that qualifies,
sources or attributes the claim lives in the post copy and the article — an
earlier version carried footnotes and an attribution line on the card itself
and that is exactly the wrong instinct for a feed: nobody reads a card.

Deliberately absent, do not add back:
  * asterisks and footnotes
  * the hupfauer.one attribution line
  * any decorative corner mark

The one supporting line at the foot is the whole argument compressed, and it
is the only thing on the card allowed to be small.

Figures are counted from Microsoft's own machine-readable release data (MSRC
CVRF for 2026-Sep), not from press coverage:

    679  CVEs whose remediation list cites KB5122871 (Windows Server 2025 only)
      1  of those with the MSRC threat string "Exploited:Yes"
           -> CVE-2026-81963, Windows Update Stack elevation of privilege

The release-wide September 2026 count is 966-974 across all Microsoft
products. That is NOT this number and must never be used on this card.

Drawn at 2x and downsampled so the type comes out crisp.

Output: social/linkedin/out/creative/you-cant-triage-a-bundle.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- palette (matches build-quotes.py and the blog covers) ---
INK = (12, 12, 13)
PAPER = (233, 230, 223)
RUST = (194, 90, 46)
MUTED = (141, 141, 138)

S = 2  # supersample factor
W = H = 1080 * S
PAD = 96 * S

SERIF_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS = "/System/Library/Fonts/Helvetica.ttc"

KICKER = "MICROSOFT SEPTEMBER 2026 UPDATE  ·  WINDOWS SERVER"
HEADLINE = "Tough luck if you run RDS."
LEFT_LABEL = "INSTALL IT"
LEFT_VERDICT = "BROKEN"
RIGHT_LABEL = "ROLL IT BACK"
RIGHT_VERDICT = "INSECURE"
FOOT = "679 security fixes ship in one package. You take all of them, or none."

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "creative"


def track(d, xy, text, font, fill, spacing):
    """Draw text with manual letter-spacing. Returns the end x."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing
    return x


def main() -> int:
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    f_kick = ImageFont.truetype(SANS, 17 * S)
    f_head = ImageFont.truetype(SERIF_ITALIC, 60 * S)
    f_label = ImageFont.truetype(SANS, 17 * S)
    f_verdict = ImageFont.truetype(SANS, 150 * S, index=1)  # Helvetica Bold
    f_or = ImageFont.truetype(SERIF_ITALIC, 40 * S)
    f_foot = ImageFont.truetype(SANS, 24 * S)

    # single rust rule — the only ornament left
    d.rectangle([PAD, 172 * S, PAD + 100 * S, 176 * S], fill=RUST)

    track(d, (PAD, 200 * S), KICKER, f_kick, MUTED, 1.6 * S)

    d.text((PAD, 248 * S), HEADLINE, font=f_head, fill=PAPER)

    # --- the two outcomes, stacked so they read top-to-bottom on a phone ---
    track(d, (PAD, 368 * S), LEFT_LABEL, f_label, MUTED, 1.8 * S)
    track(d, (PAD, 398 * S), LEFT_VERDICT, f_verdict, PAPER, -2.0 * S)

    d.text((PAD, 580 * S), "or", font=f_or, fill=RUST)

    track(d, (PAD, 656 * S), RIGHT_LABEL, f_label, MUTED, 1.8 * S)
    track(d, (PAD, 686 * S), RIGHT_VERDICT, f_verdict, PAPER, -2.0 * S)

    d.text((PAD, 902 * S), FOOT, font=f_foot, fill=MUTED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "you-cant-triage-a-bundle.png"
    img.resize((1080, 1080), Image.LANCZOS).save(out, format="PNG", optimize=True)
    print(f"✓ wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
