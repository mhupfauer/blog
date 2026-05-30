#!/usr/bin/env python3
"""
Render the three quote cards at 1080x1080 PNG.

Quotes are defined inline below — keep them in sync with the corresponding
`social/linkedin/posts/04-quote-*.md` files.

Output: social/linkedin/out/quotes/<slug>.png
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- palette (matches the blog covers and the audio/diagram shortcodes) ---
INK = (12, 12, 13)
PAPER = (233, 230, 223)
RUST = (194, 90, 46)
MUTED = (141, 141, 138)

SIZE = (1080, 1080)
PAD = 90

# macOS system fonts. Adjust if you ever run this elsewhere.
SERIF_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS_PATH = "/System/Library/Fonts/Helvetica.ttc"

QUOTES = [
    {
        "slug": "shared-account",
        "text": "A shared account with an LLM bolted onto it.",
        "attrib": "hupfauer.one  ·  which agent bricked prod?",
    },
    {
        "slug": "living-off-chatbot",
        "text": "Living off the chatbot, not the land.",
        "attrib": "hupfauer.one  ·  which agent bricked prod?",
    },
    {
        "slug": "setpoint-vs-jira",
        "text": (
            "A misrouted write to a Jira ticket is an email. "
            "A misrouted write to a setpoint moves actuators."
        ),
        "attrib": "hupfauer.one  ·  which agent bricked prod?",
    },
]

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "quotes"


def wrap_for_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word-wrap; honor explicit newlines."""
    out: list[str] = []
    for raw in text.split("\n"):
        words = raw.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            w = draw.textlength(trial, font=font)
            if w <= max_w:
                line = trial
            else:
                if line:
                    out.append(line)
                line = word
        if line:
            out.append(line)
    return out


def fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: str, max_w: int, max_h: int,
             start: int = 96, min_size: int = 40) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Find the largest font size for which the wrapped text fits in (max_w, max_h)."""
    for size in range(start, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size=size)
        lines = wrap_for_width(draw, text, font, max_w)
        line_h = int(size * 1.18)
        total_h = line_h * len(lines)
        if total_h <= max_h:
            return font, lines, line_h
    font = ImageFont.truetype(font_path, size=min_size)
    lines = wrap_for_width(draw, text, font, max_w)
    return font, lines, int(min_size * 1.18)


def render(quote: dict) -> Path:
    img = Image.new("RGB", SIZE, INK)
    d = ImageDraw.Draw(img)

    # rust accent — a short horizontal stroke above the quote
    accent_x0 = PAD
    accent_y = 240
    d.rectangle([accent_x0, accent_y, accent_x0 + 100, accent_y + 4], fill=RUST)

    # the quote itself
    quote_top = accent_y + 60
    quote_max_w = SIZE[0] - 2 * PAD
    quote_max_h = SIZE[1] - quote_top - 220  # leave room for attribution
    font, lines, line_h = fit_font(d, quote["text"], SERIF_ITALIC_PATH, quote_max_w, quote_max_h, start=110, min_size=46)
    y = quote_top
    for line in lines:
        d.text((PAD, y), line, fill=PAPER, font=font)
        y += line_h

    # attribution at the bottom, sans, muted
    attrib_font = ImageFont.truetype(SANS_PATH, size=24)
    d.text((PAD, SIZE[1] - PAD - 30), quote["attrib"], fill=MUTED, font=attrib_font)

    # tiny corner mark — small rust square top-right
    d.rectangle([SIZE[0] - PAD - 18, PAD, SIZE[0] - PAD, PAD + 18], fill=RUST)

    out_path = OUT_DIR / f"{quote['slug']}.png"
    img.save(out_path, "PNG", optimize=True)
    return out_path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for q in QUOTES:
        p = render(q)
        print(f"wrote {p.relative_to(OUT_DIR.parent.parent.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
