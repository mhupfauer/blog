#!/usr/bin/env python3
"""
Render the LinkedIn creative for "You can't triage a bundle" at 1080x1080 PNG.

The card states the dilemma an RDS operator actually faced in September 2026 —
install the cumulative update and Remote Desktop Services goes unstable, or
roll it back and hand every security fix in the package back with it — then
hangs the honest caveats off asterisks, so the hook stays sharp without lying.

Every figure is counted from Microsoft's own machine-readable release data
(MSRC CVRF for 2026-Sep), not from press coverage:

    679  CVEs whose remediation list cites KB5122871 (Windows Server 2025 only)
      1  of those with the MSRC threat string "Exploited:Yes"
           -> CVE-2026-81963, Windows Update Stack elevation of privilege

The release-wide September 2026 count is 966-974 across all Microsoft
products. That is NOT this number and must never be used on this card.

Drawn at 2x and downsampled so the rules and small type come out crisp.

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
FAINT = (116, 114, 110)
HAIRLINE = (46, 45, 44)

S = 2  # supersample factor
W = H = 1080 * S
PAD = 93 * S

SERIF_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS = "/System/Library/Fonts/Helvetica.ttc"

KICKER = "KB5122871  ·  WINDOWS SERVER 2025  ·  8 SEPTEMBER 2026"
HEADLINE = "Tough luck if you run RDS. Either it’s broken, or it’s insecure."
ATTRIB = "hupfauer.one  ·  you can’t triage a bundle"

LEFT_LABEL = "INSTALL THE UPDATE"
LEFT_VERDICT = "BROKEN"
LEFT_STAR = "*"
LEFT_BODY = (
    "Remote Desktop Services goes unstable. Connections fail after minutes, "
    "sign-ins hang, hosts wedge at logoff. Microsoft’s published workaround: "
    "stop the VM, deallocate it, start it again, and wait for a future update."
)

RIGHT_LABEL = "ROLL IT BACK"
RIGHT_VERDICT = "INSECURE"
RIGHT_STAR = "**"
RIGHT_BODY = (
    "All 679 CVE fixes in the package go back with it. There is no way to keep "
    "678 and drop the one that broke you, and one of the 679 is already under "
    "active exploitation.***"
)

NOTES = [
    ("*", "Not everywhere. Microsoft says “some organizations” and has confirmed no cause. "
          "Administrators trace the trigger to a change in remote audio redirection — that is "
          "community attribution, not a vendor statement."),
    ("**", "Most of those 679 will never be used against you. That is not the point: "
           "prioritisation assumes you can act on the ranking, and inside a cumulative update "
           "you cannot express it at all."),
    ("***", "CVE-2026-81963, Windows Update Stack elevation of privilege, flagged by Microsoft "
            "as Exploitation Detected. The month’s other exploited zero-day ships in a "
            "different package."),
    ("†", "There is a third option nobody advertises: keep the update, disable remote audio "
          "redirection by policy. Reader-reported, unconfirmed — and for a call centre the "
          "feature you just switched off is the product."),
]

OUT_DIR = Path(__file__).resolve().parent.parent / "out" / "creative"


def track(d, xy, text, font, fill, spacing):
    """Draw text with manual letter-spacing. Returns the end x."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing
    return x


def wrap(d, text, font, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
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

    f_head = ImageFont.truetype(SERIF_ITALIC, 50 * S)
    f_kick = ImageFont.truetype(SANS, 17 * S)
    f_label = ImageFont.truetype(SANS, 16 * S)
    f_verdict = ImageFont.truetype(SANS, 52 * S, index=1)   # Helvetica Bold
    f_body = ImageFont.truetype(SANS, 18 * S)
    f_note = ImageFont.truetype(SANS, 15 * S)
    f_or = ImageFont.truetype(SERIF_ITALIC, 22 * S)
    f_attrib = ImageFont.truetype(SANS, 19 * S)

    # rust corner mark and rule, matching the quote cards
    d.rectangle([W - PAD - 18 * S, 90 * S, W - PAD, 108 * S], fill=RUST)
    d.rectangle([PAD, 150 * S, PAD + 100 * S, 154 * S], fill=RUST)

    track(d, (PAD, 178 * S), KICKER, f_kick, MUTED, 1.6 * S)

    # headline
    y = 224 * S
    for line in wrap(d, HEADLINE, f_head, W - 2 * PAD):
        d.text((PAD, y), line, font=f_head, fill=PAPER)
        y += 62 * S

    # --- the two options ---
    top = int(y) + 44 * S
    gutter = 58 * S
    col_w = (W - 2 * PAD - gutter) // 2
    lx = PAD
    rx = PAD + col_w + gutter

    d.line([PAD, top, W - PAD, top], fill=HAIRLINE, width=2)

    # the "or" sits on the rule, in the gutter — the dilemma made visual
    f_dag = ImageFont.truetype(SANS, 15 * S)
    ow = d.textlength("or", font=f_or) + d.textlength("†", font=f_dag) + 3 * S
    ocx = lx + col_w + gutter / 2
    d.rectangle([ocx - ow / 2 - 12 * S, top - 17 * S, ocx + ow / 2 + 12 * S, top + 17 * S],
                fill=INK)
    ex = ocx - ow / 2
    d.text((ex, top - 16 * S), "or", font=f_or, fill=RUST)
    d.text((ex + d.textlength("or", font=f_or) + 3 * S, top - 18 * S), "†",
           font=f_dag, fill=RUST)

    for x, label, verdict, star, body in (
        (lx, LEFT_LABEL, LEFT_VERDICT, LEFT_STAR, LEFT_BODY),
        (rx, RIGHT_LABEL, RIGHT_VERDICT, RIGHT_STAR, RIGHT_BODY),
    ):
        track(d, (x, top + 32 * S), label, f_label, MUTED, 1.5 * S)
        vy = top + 68 * S
        endx = track(d, (x, vy), verdict, f_verdict, PAPER, 1.0 * S)
        d.text((endx + 4 * S, vy - 6 * S), star, font=f_verdict, fill=RUST)
        by = vy + 88 * S
        for line in wrap(d, body, f_body, col_w):
            d.text((x, by), line, font=f_body, fill=FAINT)
            by += 26 * S

    # --- the asterisks ---
    ny = 762 * S
    d.line([PAD, ny - 34 * S, W - PAD, ny - 34 * S], fill=HAIRLINE, width=2)
    for star, text in NOTES:
        d.text((PAD, ny), star, font=f_note, fill=RUST)
        for line in wrap(d, text, f_note, W - 2 * PAD - 36 * S):
            d.text((PAD + 36 * S, ny), line, font=f_note, fill=FAINT)
            ny += 20 * S
        ny += 8 * S

    d.text((PAD, H - 74 * S), ATTRIB, font=f_attrib, fill=MUTED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "you-cant-triage-a-bundle.png"
    img.resize((1080, 1080), Image.LANCZOS).save(out, format="PNG", optimize=True)
    print(f"✓ wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
