import pytest

from shorts_autopilot.manifest import load_manifest, record_episode
from shorts_autopilot.models import EpisodeSpec


def sample_episode():
    return EpisodeSpec.from_dict(
        {
            "id": "sample",
            "title": "Sample",
            "topic": "topic",
            "hook": "hook with enough words",
            "visual_language": "paper collage",
            "punchline": "unexpected ending",
            "template": "a unique shape",
            "scenes": [
                {"caption": "one", "narration": "one", "image": "one.png"},
                {"caption": "two", "narration": "two", "image": "two.png"},
            ],
        }
    )


def test_scheduled_requires_youtube_id(tmp_path):
    with pytest.raises(ValueError):
        record_episode(tmp_path / "manifest.json", sample_episode(), status="scheduled")


def test_record_is_atomic_and_replaceable(tmp_path):
    path = tmp_path / "manifest.json"
    record_episode(path, sample_episode(), status="ready")
    record_episode(path, sample_episode(), status="published", youtube_id="abc")
    items = load_manifest(path)
    assert len(items) == 1
    assert items[0]["status"] == "published"
