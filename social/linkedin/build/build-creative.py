#!/usr/bin/env python3
"""
Render the LinkedIn creative for "You can't triage a bundle" at 1080x1080 PNG.

A unit chart: one square per CVE fixed by KB5122871, the September 2026
cumulative update for Windows Server 2025. 679 squares, exactly one of which
is under active exploitation — and no mechanism exists to install only it.

Every number here is counted from Microsoft's own machine-readable release
data (MSRC CVRF for 2026-Sep), not from press coverage:

    679  CVEs whose remediation list cites KB5122871
      1  of those with the MSRC threat string "Exploited:Yes"
           -> CVE-2026-81963, Windows Update Stack elevation of privilege

Drawn at 2x and downsampled so the grid and the ring come out crisp.

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
DIM = (171, 167, 158)  # #ABA79E — chosen with the dataviz palette validator:
                       # vs RUST it scores CVD deltaE 15.8 (deutan) and 19.5
                       # normal-vision, both comfortably above the floors. A
                       # darker grey looked better but collapsed to deltaE 7.9
                       # under protanopia, leaving the ring as the only cue.

S = 2  # supersample factor
W = H = 1080 * S
PAD = 93 * S

SERIF_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS_PATH = "/System/Library/Fonts/Helvetica.ttc"

# --- the data ---
TOTAL = 679
EXPLOITED_INDEX = 302  # arbitrary cell; position carries no meaning
COLS = 40
CELL = 16 * S
GAP = 6 * S
PITCH = CELL + GAP

HEADLINE = "One of these is under active attack. You install all 679, or none."
KICKER = "KB5122871  ·  WINDOWS SERVER 2025  ·  8 SEPTEMBER 2026"
ATTRIB = "hupfauer.one  ·  you can't triage a bundle"

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "creative"


def track(draw: ImageDraw.ImageDraw, xy, text, font, fill, spacing):
    """Draw text with manual letter-spacing."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def main() -> int:
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    f_head = ImageFont.truetype(SERIF_ITALIC_PATH, 56 * S)
    f_kick = ImageFont.truetype(SANS_PATH, 17 * S)
    f_legend = ImageFont.truetype(SANS_PATH, 19 * S)
    f_attrib = ImageFont.truetype(SANS_PATH, 19 * S)

    # rust corner mark, matching the quote cards
    d.rectangle([W - PAD - 18 * S, 90 * S, W - PAD, 108 * S], fill=RUST)

    # short rust rule above the headline
    d.rectangle([PAD, 150 * S, PAD + 100 * S, 154 * S], fill=RUST)

    # kicker
    track(d, (PAD, 178 * S), KICKER, f_kick, MUTED, 1.6 * S)

    # headline
    y = 228 * S
    for line in wrap(d, HEADLINE, f_head, W - 2 * PAD):
        d.text((PAD, y), line, font=f_head, fill=PAPER)
        y += 68 * S

    # --- the unit chart ---
    grid_w = COLS * PITCH - GAP
    x0 = (W - grid_w) // 2
    y0 = int(y) + 40 * S

    for i in range(TOTAL):
        r, c = divmod(i, COLS)
        cx = x0 + c * PITCH
        cy = y0 + r * PITCH
        if i == EXPLOITED_INDEX:
            d.rectangle([cx, cy, cx + CELL, cy + CELL], fill=RUST)
        else:
            d.rectangle([cx, cy, cx + CELL, cy + CELL], fill=DIM)

    # ring around the exploited cell — secondary encoding, so identity is
    # never carried by colour alone (and so it survives feed downscaling)
    er, ec = divmod(EXPLOITED_INDEX, COLS)
    ecx = x0 + ec * PITCH + CELL / 2
    ecy = y0 + er * PITCH + CELL / 2
    rad = 23 * S
    d.ellipse([ecx - rad, ecy - rad, ecx + rad, ecy + rad], outline=RUST, width=3 * S)

    rows = -(-TOTAL // COLS)
    grid_bottom = y0 + rows * PITCH - GAP

    # --- legend ---
    ly = grid_bottom + 52 * S
    sw = 14 * S
    d.rectangle([x0, ly, x0 + sw, ly + sw], fill=RUST)
    d.text((x0 + sw + 14 * S, ly - 4 * S),
           "1  ·  CVE-2026-81963, exploitation detected",
           font=f_legend, fill=PAPER)

    ly2 = ly + 34 * S
    d.rectangle([x0, ly2, x0 + sw, ly2 + sw], fill=DIM)
    d.text((x0 + sw + 14 * S, ly2 - 4 * S),
           "678  ·  everything else in the same package",
           font=f_legend, fill=MUTED)

    # --- attribution ---
    d.text((PAD, H - 112 * S), ATTRIB, font=f_attrib, fill=MUTED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "you-cant-triage-a-bundle.png"
    img.resize((1080, 1080), Image.LANCZOS).save(out, format="PNG", optimize=True)
    print(f"✓ wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
