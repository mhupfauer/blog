#!/usr/bin/env python3
"""
Render the LinkedIn carousel — nine 1080x1080 PNG slides plus a single PDF
bundle suitable for LinkedIn's "document" upload.

Slide content is parsed out of `social/linkedin/posts/02-carousel.md`. Edit
the slide section in that file, then re-run this script.

Outputs:
  social/linkedin/out/carousel/slide-01.png .. slide-09.png
  social/linkedin/out/carousel/carousel.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INK = (12, 12, 13)
PANEL = (21, 21, 23)
PAPER = (233, 230, 223)
RUST = (194, 90, 46)
MUTED = (141, 141, 138)
LINE = (42, 42, 46)

SIZE = (1080, 1080)
PAD = 90

SERIF_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS_PATH = "/System/Library/Fonts/Helvetica.ttc"

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "posts" / "02-carousel.md"
OUT_DIR = ROOT / "out" / "carousel"


def parse_slides(md_text: str) -> list[dict]:
    """Parse `### slide-NN · kind` blocks into structured dicts."""
    blocks = re.split(r"^### slide-(\d+) · (.+)$", md_text, flags=re.MULTILINE)
    # split returns: [prefix, num, kind, body, num, kind, body, ...]
    slides: list[dict] = []
    for i in range(1, len(blocks), 3):
        num = blocks[i].strip()
        kind = blocks[i + 1].strip()
        body = blocks[i + 2]
        fields: dict[str, str] = {"num": num, "kind": kind}
        for key in ("EYEBROW", "TITLE", "SUBTITLE", "BODY", "FOOTER"):
            m = re.search(rf"^{key}:\s*(.+?)$", body, flags=re.MULTILINE)
            if m:
                fields[key.lower()] = m.group(1).strip()
        slides.append(fields)
    return slides


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    out: list[str] = []
    for raw in text.split("\n"):
        words = raw.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_w:
                line = trial
            else:
                if line:
                    out.append(line)
                line = word
        if line:
            out.append(line)
    return out


def fit(draw, text, path, max_w, max_h, start, min_size, italic=False, line_h_factor=1.18):
    p = SERIF_ITALIC_PATH if italic else path
    for size in range(start, min_size - 1, -2):
        font = ImageFont.truetype(p, size=size)
        lines = wrap(draw, text, font, max_w)
        line_h = int(size * line_h_factor)
        if line_h * len(lines) <= max_h:
            return font, lines, line_h
    font = ImageFont.truetype(p, size=min_size)
    return font, wrap(draw, text, font, max_w), int(min_size * line_h_factor)


def render_text_block(d, x, y, lines, font, line_h, fill):
    for line in lines:
        d.text((x, y), line, fill=fill, font=font)
        y += line_h
    return y


def render_slide(slide: dict, index: int, total: int) -> Image.Image:
    img = Image.new("RGB", SIZE, INK)
    d = ImageDraw.Draw(img)

    # subtle 1px border so the slide reads as a card when scrolled
    d.rectangle([0, 0, SIZE[0] - 1, SIZE[1] - 1], outline=LINE)

    # top-left rust accent
    d.rectangle([PAD, PAD, PAD + 80, PAD + 4], fill=RUST)

    # slide counter top-right
    counter_font = ImageFont.truetype(SANS_PATH, size=20)
    counter = f"{index:02d} / {total:02d}"
    d.text((SIZE[0] - PAD, PAD), counter, fill=MUTED, font=counter_font, anchor="ra")

    # eyebrow under accent
    y = PAD + 30
    if "eyebrow" in slide:
        eyebrow_font = ImageFont.truetype(SANS_PATH, size=22)
        d.text((PAD, y), slide["eyebrow"].upper(), fill=RUST, font=eyebrow_font)
        y += 50

    # title
    title_text = slide.get("title", "")
    title_max_w = SIZE[0] - 2 * PAD
    title_font, title_lines, title_lh = fit(
        d, title_text, SERIF_PATH, title_max_w,
        max_h=int(SIZE[1] * 0.45),
        start=78, min_size=42, line_h_factor=1.14,
    )
    y = render_text_block(d, PAD, y + 10, title_lines, title_font, title_lh, PAPER)

    # subtitle (cover slide only)
    if "subtitle" in slide:
        sub_font = ImageFont.truetype(SERIF_ITALIC_PATH, size=34)
        sub_lines = wrap(d, slide["subtitle"], sub_font, title_max_w)
        y = render_text_block(d, PAD, y + 20, sub_lines, sub_font, int(34 * 1.3), MUTED)

    # body
    if "body" in slide:
        body_font_size_start = 32
        body_font, body_lines, body_lh = fit(
            d, slide["body"], SANS_PATH, title_max_w,
            max_h=SIZE[1] - y - PAD - 120,
            start=body_font_size_start, min_size=22, line_h_factor=1.45,
        )
        y = render_text_block(d, PAD, y + 40, body_lines, body_font, body_lh, PAPER)

    # footer (cover + closing slide)
    footer = slide.get("footer", "hupfauer.one")
    footer_font = ImageFont.truetype(SANS_PATH, size=22)
    d.text((PAD, SIZE[1] - PAD - 26), footer, fill=MUTED, font=footer_font)

    return img


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_text = MD_PATH.read_text()
    slides = parse_slides(md_text)
    if not slides:
        print(f"no slides parsed from {MD_PATH}")
        return 1

    images: list[Image.Image] = []
    for i, slide in enumerate(slides, 1):
        img = render_slide(slide, i, len(slides))
        png_path = OUT_DIR / f"slide-{i:02d}.png"
        img.save(png_path, "PNG", optimize=True)
        images.append(img)
        print(f"wrote {png_path.relative_to(OUT_DIR.parent.parent.parent.parent)}")

    pdf_path = OUT_DIR / "carousel.pdf"
    images[0].save(
        pdf_path, "PDF", resolution=144,
        save_all=True, append_images=images[1:],
    )
    print(f"wrote {pdf_path.relative_to(OUT_DIR.parent.parent.parent.parent)} "
          f"({pdf_path.stat().st_size // 1024} KB, {len(images)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
