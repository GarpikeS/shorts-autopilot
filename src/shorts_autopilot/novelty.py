from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .models import EpisodeSpec


TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)
CRITICAL_FIELDS = {"hook", "punchline", "template"}


def tokens(value: str) -> set[str]:
    return {token.casefold() for token in TOKEN_RE.findall(value) if len(token) > 2}


def similarity(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass(frozen=True)
class NoveltyResult:
    passed: bool
    reasons: tuple[str, ...]
    maximum_similarity: float


def check_novelty(
    episode: EpisodeSpec,
    history: list[dict[str, Any]],
    *,
    field_threshold: float = 0.72,
    aggregate_threshold: float = 0.48,
) -> NoveltyResult:
    candidate = episode.novelty_fields()
    reasons: list[str] = []
    maximum = 0.0

    for previous in history:
        label = str(previous.get("id", "unknown"))
        scores = {
            field: similarity(value, str(previous.get(field, "")))
            for field, value in candidate.items()
        }
        maximum = max(maximum, *scores.values())
        for field in CRITICAL_FIELDS:
            if scores[field] >= field_threshold:
                reasons.append(f"{field} is too similar to {label} ({scores[field]:.2f})")
        meaningful = [score for field, score in scores.items() if candidate[field].strip()]
        aggregate = sum(meaningful) / len(meaningful) if meaningful else 0.0
        if aggregate >= aggregate_threshold:
            reasons.append(f"overall concept is too similar to {label} ({aggregate:.2f})")

    return NoveltyResult(not reasons, tuple(dict.fromkeys(reasons)), maximum)
