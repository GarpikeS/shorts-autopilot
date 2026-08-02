from shorts_autopilot.models import EpisodeSpec
from shorts_autopilot.novelty import check_novelty


def episode(**overrides):
    data = {
        "id": "new",
        "title": "New idea",
        "description": "",
        "topic": "heat wave turns a miner into a weather station",
        "hook": "a thermometer submits an electricity bill",
        "visual_language": "silent film collage",
        "characters": ["thermometer"],
        "props": ["paper fan"],
        "punchline": "the fan invoices by the degree",
        "template": "object courtroom then a temperature check",
        "scenes": [
            {"caption": "one", "narration": "one", "image": "one.png"},
            {"caption": "two", "narration": "two", "image": "two.png"},
        ],
    }
    data.update(overrides)
    return EpisodeSpec.from_dict(data)


def test_unique_episode_passes():
    history = [{"id": "old", "hook": "a coin misses the bus", "template": "sports replay"}]
    assert check_novelty(episode(), history).passed


def test_repeated_template_fails():
    candidate = episode()
    history = [{"id": "old", **candidate.novelty_fields()}]
    result = check_novelty(candidate, history)
    assert not result.passed
    assert any("template" in reason for reason in result.reasons)
