from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SceneSpec:
    caption: str
    narration: str
    image: str | None = None
    image_prompt: str | None = None
    min_duration: float = 2.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SceneSpec":
        scene = cls(
            caption=str(data.get("caption", "")).strip(),
            narration=str(data.get("narration", "")).strip(),
            image=str(data["image"]).strip() if data.get("image") else None,
            image_prompt=str(data["image_prompt"]).strip() if data.get("image_prompt") else None,
            min_duration=float(data.get("min_duration", 2.0)),
        )
        if not scene.caption or not scene.narration:
            raise ValueError("Each scene needs non-empty caption and narration")
        if not scene.image and not scene.image_prompt:
            raise ValueError("Each scene needs image or image_prompt")
        return scene


@dataclass(frozen=True)
class EpisodeSpec:
    id: str
    title: str
    description: str
    topic: str
    hook: str
    visual_language: str
    punchline: str
    template: str
    scenes: tuple[SceneSpec, ...]
    tags: tuple[str, ...] = field(default_factory=tuple)
    characters: tuple[str, ...] = field(default_factory=tuple)
    props: tuple[str, ...] = field(default_factory=tuple)
    voice: str = "ru-RU-DmitryNeural"
    image_provider: str = "polza"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EpisodeSpec":
        required = ("id", "title", "topic", "hook", "visual_language", "punchline", "template")
        missing = [key for key in required if not str(data.get(key, "")).strip()]
        if missing:
            raise ValueError(f"Missing required episode fields: {', '.join(missing)}")
        scenes = tuple(SceneSpec.from_dict(item) for item in data.get("scenes", []))
        if not 2 <= len(scenes) <= 8:
            raise ValueError("An episode must contain between 2 and 8 scenes")
        return cls(
            id=str(data["id"]).strip(),
            title=str(data["title"]).strip(),
            description=str(data.get("description", "")).strip(),
            topic=str(data["topic"]).strip(),
            hook=str(data["hook"]).strip(),
            visual_language=str(data["visual_language"]).strip(),
            punchline=str(data["punchline"]).strip(),
            template=str(data["template"]).strip(),
            scenes=scenes,
            tags=tuple(str(v).strip() for v in data.get("tags", []) if str(v).strip()),
            characters=tuple(str(v).strip() for v in data.get("characters", []) if str(v).strip()),
            props=tuple(str(v).strip() for v in data.get("props", []) if str(v).strip()),
            voice=str(data.get("voice", "ru-RU-DmitryNeural")).strip(),
            image_provider=str(data.get("image_provider", "polza")).strip(),
        )

    def resolve_scene_image(self, scene: SceneSpec, base_dir: Path) -> Path | None:
        return (base_dir / scene.image).resolve() if scene.image else None

    def novelty_fields(self) -> dict[str, str]:
        return {
            "topic": self.topic,
            "hook": self.hook,
            "visual_language": self.visual_language,
            "characters": " ".join(self.characters),
            "props": " ".join(self.props),
            "punchline": self.punchline,
            "template": self.template,
        }
