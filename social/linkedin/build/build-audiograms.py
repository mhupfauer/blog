#!/usr/bin/env python3
"""
Render native-LinkedIn audiograms for each podcast cut.

Each output is a 1080x1080 H.264/AAC MP4 with:
  - the post cover image as a still background,
  - a live waveform overlay in the post's rust accent across the bottom strip,
  - a short attribution line.

Pick clips by ear from the corresponding script.txt files in
static/audio/. Adjust the CLIPS list below — `start` and `dur` are in
seconds — then re-run this script.

Outputs land at social/linkedin/out/audiograms/<slug>.mp4.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # repo root
AUDIO_DIR = ROOT / "static" / "audio"
COVER = ROOT / "assets" / "covers" / "which-agent-bricked-prod.jpg"
OUT_DIR = ROOT / "social" / "linkedin" / "out" / "audiograms"

# Edit these. Listen to static/audio/<slug>.mp3 to find a 60-90 sec slice
# that lands a single complete thought. The defaults take the closing
# section of each cut — usually punchy by construction.
#
#   "audio":   filename under static/audio/
#   "start":   start time in seconds
#   "dur":     clip duration in seconds (60-90 ideal for LinkedIn native video)
#   "out":     output filename under out/audiograms/

CLIPS = [
    {
        "audio": "which-agent-bricked-prod-bench-en.mp3",
        "start": 615,  # ~10:15 into the 11:45 cut — closes on the bar
        "dur":   85,
        "out":   "bench-en.mp4",
    },
    {
        "audio": "which-agent-bricked-prod-bench-de.mp3",
        "start": 735,  # ~12:15 into the 13:48 cut
        "dur":   85,
        "out":   "bench-de.mp4",
    },
    {
        "audio": "which-agent-bricked-prod-boardroom-en.mp3",
        "start": 505,  # ~8:25 into the 9:53 cut
        "dur":   80,
        "out":   "boardroom-en.mp4",
    },
    {
        "audio": "which-agent-bricked-prod-boardroom-de.mp3",
        "start": 500,  # ~8:20 into the 9:46 cut
        "dur":   80,
        "out":   "boardroom-de.mp4",
    },
]


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def render(clip: dict) -> Path:
    audio_path = AUDIO_DIR / clip["audio"]
    if not audio_path.exists():
        raise FileNotFoundError(f"audio missing: {audio_path}")
    if not COVER.exists():
        raise FileNotFoundError(f"cover missing: {COVER}")

    out_path = OUT_DIR / clip["out"]

    # filter chain:
    #   - scale + crop cover to 1080x1080
    #   - dim the cover slightly so the waveform reads on top
    #   - render waveform 1080x220, rust colour, centered cline mode
    #   - overlay waveform at y=830 (bottom strip)
    vf = (
        "[1:v]scale=1080:1080:force_original_aspect_ratio=increase,"
        "crop=1080:1080,eq=brightness=-0.06:saturation=0.95,setsar=1[bg];"
        "[0:a]aformat=channel_layouts=mono,"
        "showwaves=s=1080x220:mode=cline:rate=30:colors=0xC25A2E,"
        "format=yuva420p,colorchannelmixer=aa=0.92[wave];"
        "[bg][wave]overlay=x=0:y=830:format=auto[out]"
    )

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(clip["start"]), "-t", str(clip["dur"]), "-i", str(audio_path),
        "-loop", "1", "-i", str(COVER),
        "-filter_complex", vf,
        "-map", "[out]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    return out_path


def main() -> int:
    if not have("ffmpeg"):
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
