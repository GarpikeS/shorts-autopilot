# Shorts Autopilot

A portable pipeline for independent vertical Shorts. It turns an episode JSON
specification into a narrated 1080x1920 video, rejects repeated ideas against a
local history, generates a QA report, and keeps publication state separate from
content production.

The repository intentionally contains no browser profile, cookies, tokens,
channel history, private prompts, or generated media.

## Features

- Novelty gate over topic, hook, visual language, characters, props, punchline,
  and structural template.
- Optional image generation through a provider interface. A Polza provider is
  included and reads `POLZA_API_KEY` only from the environment.
- Edge TTS narration with a Windows System.Speech fallback.
- FFmpeg rendering, decode validation, `ffprobe` metadata, silence detection,
  and contact-sheet generation.
- Atomic JSON manifest that records an item only after an explicit command.
- Headless, muted Chrome launcher for a private YouTube Studio profile.
- Two installable agent skills under `skills/`.

## Requirements

- Python 3.11+
- FFmpeg and ffprobe on `PATH`
- Google Chrome for Studio automation
- A separately stored, already authorized Chrome profile for Studio operations

## Quick Start

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
shorts-autopilot novelty --episode examples\episode.json --manifest workspace\manifest.json
shorts-autopilot build --episode examples\episode.json --manifest workspace\manifest.json --output output
```

If every scene already has an `image` path, no image API is needed. If a scene
has only `image_prompt`, set `POLZA_API_KEY` and choose the `polza` provider in
the episode or CLI.

After a real Studio confirmation, record the publication separately:

```powershell
shorts-autopilot record --episode examples\episode.json `
  --manifest workspace\manifest.json `
  --status scheduled --youtube-id VIDEO_ID --publish-at 2026-08-03T18:00:00+03:00
```

## Episode Format

See [`examples/episode.json`](examples/episode.json) and
[`skills/shorts-autopilot/references/episode-schema.md`](skills/shorts-autopilot/references/episode-schema.md).

Every Short is expected to be standalone. The default gate compares the latest
10 active manifest records and rejects duplicated hooks, endings, templates,
or excessive field-level similarity.

## Studio

Start Chrome without a visible or audible window:

```powershell
.\scripts\start-studio-headless.ps1 -ProfilePath C:\private\youtube-profile
```

The script uses `--headless=new`, `--mute-audio`, an ordinary Windows Chrome
user agent, and a local CDP port. The profile directory is ignored by Git and
must never be committed.

## Skills

- `skills/shorts-autopilot`: concept, novelty, generation, and media QA workflow.
- `skills/youtube-studio-operator`: headless Studio, scheduling, metrics, and
  confirmation safety workflow.

Copy either skill directory into your agent's skills directory, or point the
agent at this repository. On Codex, install both with:

```powershell
.\scripts\install-skills.ps1
```

## Security

Read [`docs/security.md`](docs/security.md) before connecting a real channel.
The design keeps production state and authorization outside the repository.
