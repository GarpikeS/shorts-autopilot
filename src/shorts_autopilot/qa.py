from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from .io import atomic_write_json, require_tools, run


def inspect_video(video: Path) -> dict[str, Any]:
    require_tools(("ffmpeg", "ffprobe"))
    probe = run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)],
        capture=True,
    )
    data = json.loads(probe.stdout)
    run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"])
    silence = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(video),
            "-af",
            "silencedetect=n=-42dB:d=1.0",
            "-f",
            "null",
            "-",
        ],
        capture=True,
    )
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    width, height = video_stream.get("width"), video_stream.get("height")
    duration = float(data.get("format", {}).get("duration", 0.0))
    issues: list[str] = []
    if (width, height) != (1080, 1920):
        issues.append(f"unexpected dimensions: {width}x{height}")
    if not audio_stream:
        issues.append("missing audio stream")
    if duration <= 0:
        issues.append("invalid duration")
    return {
        "passed": not issues,
        "issues": issues,
        "width": width,
        "height": height,
        "duration": duration,
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "silence_log": silence.stderr,
    }


def contact_sheet(video: Path, destination: Path, count: int = 6) -> Path:
    report = inspect_video(video)
    duration = report["duration"]
    frames: list[Path] = []
    frame_dir = destination.parent / "contact-frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for index in range(count):
        timestamp = duration * (index + 0.5) / count
        frame = frame_dir / f"frame-{index:02d}.jpg"
        run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(frame),
            ]
        )
        frames.append(frame)
    thumbs = [Image.open(path).convert("RGB").resize((270, 480)) for path in frames]
    sheet = Image.new("RGB", (810, 960), "#111111")
    draw = ImageDraw.Draw(sheet)
    for index, thumb in enumerate(thumbs):
        x, y = (index % 3) * 270, (index // 3) * 480
        sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + 8), str(index + 1), fill="white")
        thumb.close()
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, quality=92)
    return destination


def write_report(video: Path) -> Path:
    report = inspect_video(video)
    report_path = video.with_suffix(".qa.json")
    atomic_write_json(report_path, report)
    contact_sheet(video, video.with_suffix(".contact.jpg"))
    return report_path
