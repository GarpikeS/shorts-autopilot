from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io import atomic_write_json, load_json
from .models import EpisodeSpec


ARCHIVE_STATUSES = {"deleted", "cancelled"}


def load_manifest(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = load_json(path)
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        raise ValueError("Manifest must be a list or an object with an items list")
    return [item for item in data if isinstance(item, dict)]


def recent_active(path: Path, limit: int = 10) -> list[dict[str, Any]]:
    active = [item for item in load_manifest(path) if item.get("status") not in ARCHIVE_STATUSES]
    return active[-limit:]


def record_episode(
    path: Path,
    episode: EpisodeSpec,
    *,
    status: str,
    youtube_id: str | None = None,
    publish_at: str | None = None,
) -> dict[str, Any]:
    if status in {"scheduled", "published"} and not youtube_id:
        raise ValueError("youtube_id is required for scheduled or published records")
    items = load_manifest(path)
    record = {
        "id": episode.id,
        "title": episode.title,
        "status": status,
        "youtube_id": youtube_id,
        "publish_at": publish_at,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **episode.novelty_fields(),
    }
    replaced = False
    for index, item in enumerate(items):
        if item.get("id") == episode.id:
            items[index] = record
            replaced = True
            break
    if not replaced:
        items.append(record)
    atomic_write_json(path, {"version": 1, "items": items})
    return record
