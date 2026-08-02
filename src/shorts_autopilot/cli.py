from __future__ import annotations

import argparse
import json
from pathlib import Path

from .io import load_env_file, load_json
from .manifest import recent_active, record_episode
from .models import EpisodeSpec
from .novelty import check_novelty
from .qa import write_report
from .render import build_video


def load_episode(path: Path) -> EpisodeSpec:
    return EpisodeSpec.from_dict(load_json(path))


def novelty_or_exit(episode: EpisodeSpec, manifest: Path, limit: int) -> None:
    result = check_novelty(episode, recent_active(manifest, limit))
    print(
        json.dumps(
            {"passed": result.passed, "reasons": result.reasons}, ensure_ascii=False, indent=2
        )
    )
    if not result.passed:
        raise SystemExit(2)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="shorts-autopilot")
    commands = root.add_subparsers(dest="command", required=True)

    novelty = commands.add_parser("novelty", help="Check an episode against recent history")
    novelty.add_argument("--episode", type=Path, required=True)
    novelty.add_argument("--manifest", type=Path, required=True)
    novelty.add_argument("--limit", type=int, default=10)

    build = commands.add_parser("build", help="Run novelty gate, render, and media QA")
    build.add_argument("--episode", type=Path, required=True)
    build.add_argument("--manifest", type=Path, required=True)
    build.add_argument("--output", type=Path, default=Path("output"))
    build.add_argument("--provider")
    build.add_argument("--limit", type=int, default=10)

    qa = commands.add_parser("qa", help="Validate a rendered video")
    qa.add_argument("video", type=Path)

    record = commands.add_parser("record", help="Record an externally confirmed state")
    record.add_argument("--episode", type=Path, required=True)
    record.add_argument("--manifest", type=Path, required=True)
    record.add_argument(
        "--status",
        choices=["ready", "scheduled", "published", "cancelled", "deleted"],
        required=True,
    )
    record.add_argument("--youtube-id")
    record.add_argument("--publish-at")
    return root


def main() -> None:
    load_env_file(Path(".env"))
    args = parser().parse_args()
    if args.command == "novelty":
        novelty_or_exit(load_episode(args.episode), args.manifest, args.limit)
        return
    if args.command == "build":
        episode = load_episode(args.episode)
        novelty_or_exit(episode, args.manifest, args.limit)
        video = build_video(episode, args.episode, args.output, args.provider)
        report = write_report(video)
        print(json.dumps({"video": str(video), "qa": str(report)}, indent=2))
        return
    if args.command == "qa":
        print(write_report(args.video))
        return
    if args.command == "record":
        record = record_episode(
            args.manifest,
            load_episode(args.episode),
            status=args.status,
            youtube_id=args.youtube_id,
            publish_at=args.publish_at,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
