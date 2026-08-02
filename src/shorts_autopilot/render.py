from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .io import require_tools, run
from .models import EpisodeSpec, SceneSpec
from .providers import polza
from .tts import synthesize


WIDTH, HEIGHT = 1080, 1920


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _prepare_frame(source: Path, caption: str, destination: Path) -> None:
    with Image.open(source).convert("RGB") as image:
        scale = max(WIDTH / image.width, HEIGHT / image.height)
        resized = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)))
        left = (resized.width - WIDTH) // 2
        top = (resized.height - HEIGHT) // 2
        canvas = resized.crop((left, top, left + WIDTH, top + HEIGHT))

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _font(68)
    lines = _wrap(draw, caption, font, WIDTH - 150)
    line_height = 88
    box_height = len(lines) * line_height + 64
    y0 = HEIGHT - box_height - 180
    draw.rounded_rectangle((55, y0, WIDTH - 55, y0 + box_height), radius=28, fill=(5, 7, 10, 210))
    for index, line in enumerate(lines):
        box = draw.textbbox((0, 0), line, font=font)
        x = (WIDTH - (box[2] - box[0])) / 2
        draw.text((x, y0 + 30 + index * line_height), line, font=font, fill="white")
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, quality=94)


def _duration(audio: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio),
        ],
        capture=True,
    )
    return float(result.stdout.strip())


def _scene_image(
    scene: SceneSpec, episode_dir: Path, work: Path, index: int, provider: str
) -> Path:
    if scene.image:
        source = (episode_dir / scene.image).resolve()
        if not source.exists():
            raise FileNotFoundError(source)
        return source
    target = work / f"generated-{index:02d}.png"
    if provider != "polza":
        raise ValueError(f"Unsupported image provider: {provider}")
    return polza.generate(scene.image_prompt or "", target)


def build_video(
    episode: EpisodeSpec, episode_path: Path, output_root: Path, provider: str | None = None
) -> Path:
    require_tools(("ffmpeg", "ffprobe"))
    provider = provider or episode.image_provider
    work = output_root / episode.id
    work.mkdir(parents=True, exist_ok=True)
    segments: list[Path] = []

    for index, scene in enumerate(episode.scenes, start=1):
        source = _scene_image(scene, episode_path.parent, work, index, provider)
        frame = work / f"frame-{index:02d}.jpg"
        _prepare_frame(source, scene.caption, frame)
        audio = synthesize(scene.narration, episode.voice, work / f"voice-{index:02d}.mp3")
        duration = max(scene.min_duration, _duration(audio) + 0.25)
        segment = work / f"segment-{index:02d}.mp4"
        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-framerate",
                "30",
                "-i",
                str(frame),
                "-i",
                str(audio),
                "-t",
                f"{duration:.3f}",
                "-vf",
                "zoompan=z='min(zoom+0.00035,1.035)':d=1:s=1080x1920:fps=30,format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "19",
                "-c:a",
                "aac",
                "-ar",
                "48000",
                "-b:a",
                "160k",
                "-shortest",
                str(segment),
            ]
        )
        segments.append(segment)

    concat_file = work / "segments.txt"
    concat_file.write_text(
        "".join(
            f"file '{str(path.resolve()).replace(chr(39), chr(39) * 2)}'\n" for path in segments
        ),
        encoding="utf-8",
    )
    final = work / f"{episode.id}.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(final),
        ]
    )
    metadata = {
        "id": episode.id,
        "title": episode.title,
        "description": episode.description,
        "tags": list(episode.tags),
        "video": str(final.resolve()),
        "thumbnail": str((work / "frame-01.jpg").resolve()),
    }
    (work / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return final
