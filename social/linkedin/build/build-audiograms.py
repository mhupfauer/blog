#!/usr/bin/env python3
"""
Render preview-style audiograms for each podcast cut.

LinkedIn viewers scroll on mute, so the static backdrop has to do all the
selling: post title, show label, cut/language, attribution. We render the
backdrop in Pillow (full typography control, matches the rest of the
blog's ink/rust/paper system) and let ffmpeg overlay a reactive waveform
in the bottom strip + mux in the audio clip.

Edit the CLIPS list to tune start/dur per cut. Defaults take the closing
~80 seconds, which on these scripts is the bar landing.

Outputs land at social/linkedin/out/audiograms/<slug>.mp4.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- palette ----------------------------------------------------------------
INK = (12, 12, 13)
PAPER = (233, 230, 223)
RUST = (194, 90, 46)
MUTED = (141, 141, 138)
LINE = (42, 42, 46)

SIZE = (1080, 1080)
PAD = 90
WAVEFORM_H = 170
WAVEFORM_BOTTOM_PAD = 60  # tight bottom margin so the waveform anchors the frame
WAVEFORM_TOP = SIZE[1] - WAVEFORM_H - WAVEFORM_BOTTOM_PAD

SERIF_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_ITALIC_PATH = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS_PATH = "/System/Library/Fonts/Helvetica.ttc"

ROOT = Path(__file__).resolve().parents[3]
AUDIO_DIR = ROOT / "static" / "audio"
OUT_DIR = ROOT / "social" / "linkedin" / "out" / "audiograms"

# --- per-clip configuration -------------------------------------------------
# show_label & language_label go in the eyebrow up top.
# title & subtitle land in the upper third.
# attribution goes above the waveform.

CLIPS = [
    {
        "audio": "which-agent-bricked-prod-bench-en.mp3",
        "start": 615, "dur": 85,
        "out":   "bench-en.mp4",
        "show_label":     "From the Bench",
        "language_label": "English  ·  ~85s",
        "title":          "Which agent bricked prod?",
        "subtitle":       "Whose authority. Which agent. Two questions every hop has to answer.",
        "attribution":    "Markus Hupfauer  ·  hupfauer.one",
    },
    {
        "audio": "which-agent-bricked-prod-bench-de.mp3",
        "start": 735, "dur": 85,
        "out":   "bench-de.mp4",
        "show_label":     "From the Bench",
        "language_label": "Deutsch  ·  ~85s",
        "title":          "Which agent bricked prod?",
        "subtitle":       "Wessen Autorität. Welcher Agent. Zwei Fragen, die jeder Hop beantworten muss.",
        "attribution":    "Markus Hupfauer  ·  hupfauer.one",
    },
    {
        "audio": "which-agent-bricked-prod-boardroom-en.mp3",
        "start": 505, "dur": 80,
        "out":   "boardroom-en.mp4",
        "show_label":     "From the Boardroom",
        "language_label": "English  ·  ~80s",
        "title":          "Which agent bricked prod?",
        "subtitle":       "The governance cut. What the auditor sees when an agent makes the change.",
        "attribution":    "Markus Hupfauer  ·  hupfauer.one",
    },
    {
        "audio": "which-agent-bricked-prod-boardroom-de.mp3",
        "start": 500, "dur": 80,
        "out":   "boardroom-de.mp4",
        "show_label":     "From the Boardroom",
        "language_label": "Deutsch  ·  ~80s",
        "title":          "Which agent bricked prod?",
        "subtitle":       "Der Governance-Cut. Was der Auditor sieht, wenn ein Agent die Änderung macht.",
        "attribution":    "Markus Hupfauer  ·  hupfauer.one",
    },
]


# --- typesetting helpers ----------------------------------------------------
def wrap(draw, text, font, max_w):
    out = []
    for raw in text.split("\n"):
        words, line = raw.split(), ""
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


def fit(draw, text, font_path, max_w, max_h, start, min_size, line_h_factor=1.18):
    for size in range(start, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size=size)
        lines = wrap(draw, text, font, max_w)
        line_h = int(size * line_h_factor)
        if line_h * len(lines) <= max_h:
            return font, lines, line_h
    font = ImageFont.truetype(font_path, size=min_size)
    return font, wrap(draw, text, font, max_w), int(min_size * line_h_factor)


def render_backdrop(clip: dict) -> Path:
    img = Image.new("RGB", SIZE, INK)
    d = ImageDraw.Draw(img)

    # 1px frame so the still reads as a card
    d.rectangle([0, 0, SIZE[0] - 1, SIZE[1] - 1], outline=LINE)

    # rust accent — top-left short stroke
    d.rectangle([PAD, PAD, PAD + 80, PAD + 4], fill=RUST)

    # eyebrow: SHOW NAME · LANGUAGE · DURATION
    eyebrow_text = f"{clip['show_label'].upper()}   ·   {clip['language_label'].upper()}"
    eyebrow_font = ImageFont.truetype(SANS_PATH, size=22)
    d.text((PAD, PAD + 28), eyebrow_text, fill=RUST, font=eyebrow_font)

    # title
    title_max_w = SIZE[0] - 2 * PAD
    title_font, title_lines, title_lh = fit(
        d, clip["title"], SERIF_PATH, title_max_w,
        max_h=int(SIZE[1] * 0.35),
        start=98, min_size=60, line_h_factor=1.12,
    )
    y = PAD + 90
    for line in title_lines:
        d.text((PAD, y), line, fill=PAPER, font=title_font)
        y += title_lh

    # subtitle, italic, muted
    sub_font, sub_lines, sub_lh = fit(
        d, clip["subtitle"], SERIF_ITALIC_PATH, title_max_w,
        max_h=int(SIZE[1] * 0.22),
        start=40, min_size=28, line_h_factor=1.32,
    )
    y += 18
    for line in sub_lines:
        d.text((PAD, y), line, fill=MUTED, font=sub_font)
        y += sub_lh

    # attribution above the waveform strip
    attrib_font = ImageFont.truetype(SANS_PATH, size=22)
    attrib_y = WAVEFORM_TOP - 36
    d.text((PAD, attrib_y), clip["attribution"], fill=MUTED, font=attrib_font)

    # a thin line above the waveform strip to anchor it visually
    d.rectangle([PAD, WAVEFORM_TOP - 6, SIZE[0] - PAD, WAVEFORM_TOP - 5], fill=LINE)

    # small rust square top-right — same corner mark as the quote cards
    d.rectangle([SIZE[0] - PAD - 18, PAD, SIZE[0] - PAD, PAD + 18], fill=RUST)

    tmp = Path(tempfile.mkstemp(suffix=".png", prefix=f"audiogram-{clip['out']}-")[1])
    img.save(tmp, "PNG", optimize=True)
    return tmp


# --- ffmpeg muxing -----------------------------------------------------------
def render(clip: dict) -> Path:
    audio_path = AUDIO_DIR / clip["audio"]
    if not audio_path.exists():
        raise FileNotFoundError(f"audio missing: {audio_path}")

    backdrop = render_backdrop(clip)
    out_path = OUT_DIR / clip["out"]

    # The waveform is drawn into a 1080xWAVEFORM_H tile, then overlaid at
    # y=WAVEFORM_TOP onto the static backdrop. cline gives a continuous
    # editorial line; p2p would be more "podcast bars" if you ever want
    # that look — swap mode below.
    # showwaves with scale=cbrt makes voice peaks visibly bigger without
    # over-distorting transients; cline gives the editorial waveform shape;
    # we lift the audio with volume= before visualizing (visualization only —
    # the audio stream that gets muxed comes from the original mp3 unchanged).
    vf = (
        f"[1:v]format=rgba[bg];"
        f"[0:a]asplit=2[a_mux][a_vis];"
        f"[a_vis]aformat=channel_layouts=mono,volume=4.0,"
        f"showwaves=s=1080x{WAVEFORM_H}:mode=cline:rate=30:scale=cbrt:colors=0xC25A2E,"
        f"format=yuva420p,colorchannelmixer=aa=0.95[wave];"
        f"[bg][wave]overlay=x=0:y={WAVEFORM_TOP}:format=auto,format=yuv420p[out]"
    )

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(clip["start"]), "-t", str(clip["dur"]), "-i", str(audio_path),
        "-loop", "1", "-i", str(backdrop),
        "-filter_complex", vf,
        "-map", "[out]", "-map", "[a_mux]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, check=True)
    finally:
        try:
            backdrop.unlink()
        except OSError:
            pass
    return out_path


def main() -> int:
    if not shutil.which("ffmpeg"):
        print("ffmpeg not on PATH", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for clip in CLIPS:
        p = render(clip)
        size_kb = p.stat().st_size // 1024
        print(f"wrote {p.relative_to(ROOT)} ({size_kb} KB, {clip['dur']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
