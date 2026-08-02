from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://api.polza.ai/api/v1/chat/completions"


def _media_url(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    if isinstance(value, dict):
        for key in ("url", "image_url", "output", "result"):
            found = _media_url(value.get(key))
            if found:
                return found
        for nested in value.values():
            found = _media_url(nested)
            if found:
                return found
    if isinstance(value, list):
        for nested in value:
            found = _media_url(nested)
            if found:
                return found
    return None


def generate(prompt: str, destination: Path, *, model: str = "bytedance/seedream-4") -> Path:
    key = os.environ.get("POLZA_API_KEY", "").strip()
    if not key:
        raise RuntimeError("POLZA_API_KEY is required for the polza image provider")
    payload = json.dumps(
        {"model": model, "messages": [{"role": "user", "content": prompt}]}
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=240) as response:
        data = json.loads(response.read().decode("utf-8"))
    url = _media_url(data)
    if not url:
        raise RuntimeError("Image provider returned no downloadable media URL")
    destination.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, destination)
    return destination
