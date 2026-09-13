#!/usr/bin/env python3
"""
Render the LinkedIn creative for "You can't triage a bundle" at 1080x1080 PNG.

Concept: ONE SEALED PACKAGE, TWO BAD EXITS.

A single uninterrupted bone block holds 679 and states that it cannot be
subdivided. A rust fork leaves the block and splits into two consequences drawn
with identical weight, because neither option is the safe one. The composition
*is* the argument: the reader should understand the trap before reading the
thesis line at the foot.

Art direction from a senior art director (gpt-6-astra). The useful part was the
diagnosis of the previous attempt: it named the dilemma without designing the
mechanism that causes it, so "BROKEN / or / INSECURE" could have described any
security trade-off, while the distinctive fact — 679 fixes welded into one
package — had been demoted to small print.

Rules that keep this from drifting back into a template:
  * one dominant inverse mass (the bone block interrupting the black field)
  * three clearly separated type scales: 172 / 82 / 64
  * the block has NO internal division — subdividing it contradicts the story
  * rust carries causality only (it seals the block and carries both exits),
    roughly 1-2% of the canvas, never a large orange panel
  * no containers around the outcomes, or it reads as a SaaS comparison table
  * flat fills only: no gradients, shadows, bevels, grain or rounded corners

All typography is composited here with the real Georgia and Helvetica faces
rather than generated: the number is the focal point and has to be exact.
Drawn at 2x and downsampled once.

Figures counted from Microsoft's MSRC CVRF release data for 2026-Sep:
    679  CVEs whose remediation list cites KB5122871 (Windows Server 2025 only)
      1  of those with the threat string "Exploited:Yes" -> CVE-2026-81963
The release-wide September count is 966-974 across all Microsoft products.
That is NOT this number and must never be used on this card.

Output: social/linkedin/out/creative/you-cant-triage-a-bundle.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

INK = (10, 10, 10)
BONE = (233, 230, 223)
RUST = (194, 90, 46)

S = 2
W = H = 1080 * S

GEORGIA_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
HELV = "/System/Library/Fonts/Helvetica.ttc"

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "creative"


def f(path, size, index=0):
    return ImageFont.truetype(path, int(size * S), index=index)


def put(d, x, y, text, font, fill, tracking=0.0):
    """Draw so the VISIBLE ink starts at (x, y) in 1080-space, not the font box."""
    px, py = x * S, y * S
    bbox = font.getbbox(text)
    ox, oy = bbox[0], bbox[1]
    if tracking:
        cx = px - ox
        for ch in text:
            d.text((cx, py - oy), ch, font=font, fill=fill)
            cx += d.textlength(ch, font=font) + tracking * S
        return cx
    d.text((px - ox, py - oy), text, font=font, fill=fill)
    return px - ox + d.textlength(text, font=font)


def tracked_width(d, text, font, tracking):
    if not text:
        return 0
    return sum(d.textlength(c, font=font) + tracking * S for c in text) - tracking * S


def main() -> int:
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    f_meta = f(HELV, 20)
    f_head = f(GEORGIA_I, 82)
    f_big = f(HELV, 172, index=1)
    f_mid = f(HELV, 44, index=1)
    f_body = f(HELV, 27)
    f_label = f(HELV, 22, index=1)
    f_outcome = f(HELV, 64, index=1)
    f_foot = f(GEORGIA_I, 32)

    # --- metadata line ---
    put(d, 64, 52, "WINDOWS SERVER 2025", f_meta, BONE, tracking=1.0)
    w = tracked_width(d, "SEPTEMBER 2026", f_meta, 1.0)
    put(d, (1016 * S - w) / S, 52, "SEPTEMBER 2026", f_meta, BONE, tracking=1.0)

    # --- proposition ---
    put(d, 60, 111, "One update.", f_head, BONE)
    put(d, 60, 201, "Two bad exits.", f_head, BONE)

    # --- the sealed package: one uninterrupted mass, no internal division ---
    d.rectangle([64 * S, 340 * S, (64 + 952) * S, (340 + 236) * S], fill=BONE)
    put(d, 92, 369, "679", f_big, INK)
    put(d, 490, 385, "CVE fixes.", f_mid, INK)
    put(d, 492, 455, "One cumulative update.", f_body, INK)
    put(d, 492, 497, "No selective install.", f_body, INK)

    # rust seal, flush with the block's lower edge
    d.rectangle([64 * S, 564 * S, (64 + 952) * S, (564 + 12) * S], fill=RUST)

    # --- the fork: identical weight on both branches ---
    lw = 4
    def vline(x, y1, y2):
        d.rectangle([x * S, y1 * S, (x + lw) * S, y2 * S], fill=RUST)

    def hline(x1, x2, y):
        d.rectangle([x1 * S, y * S, (x2 + lw) * S, (y + lw) * S], fill=RUST)

    vline(538, 576, 628)
    hline(286, 794, 628)
    vline(286, 628, 670)
    vline(794, 628, 670)
    for cx in (286, 794):
        d.polygon([((cx - 5) * S, 670 * S), ((cx + 9) * S, 670 * S),
                   ((cx + 2) * S, 680 * S)], fill=RUST)

    # --- the two consequences, paired horizontally, no containers ---
    for x_label, x_word, label, word, l1, l2 in (
        (64, 60, "INSTALL UPDATE", "BROKEN",
         "Remote Desktop", "Services fails."),
        (572, 568, "ROLL BACK UPDATE", "INSECURE",
         "All 679 fixes removed.", "One actively exploited CVE."),
    ):
        put(d, x_label, 705, label, f_label, RUST, tracking=0.7)
        put(d, x_word, 745, word, f_outcome, BONE)
        put(d, x_label, 831, l1, f_body, BONE)
        put(d, x_label, 867, l2, f_body, BONE)

    # --- thesis ---
    faint = tuple(round(INK[i] + (BONE[i] - INK[i]) * 0.25) for i in range(3))
    d.rectangle([64 * S, 937 * S, (64 + 952) * S, (937 + 2) * S], fill=faint)
    put(d, 64, 963, "Prioritisation needs a choice.", f_foot, BONE)
    put(d, 64, 1002, "Cumulative updates remove it.", f_foot, BONE)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "you-cant-triage-a-bundle.png"
    img.resize((1080, 1080), Image.LANCZOS).save(out, format="PNG", optimize=True)
    print(f"✓ wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
