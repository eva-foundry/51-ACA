# EVA-STORY: ACA-15-006
"""CLI surface for onboarding orchestration commands."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


def _emit(command: str, **kwargs: object) -> int:
    payload = {
        "command": command,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }
    print(json.dumps(payload, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="aca-onboarding")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init")
    init_cmd.add_argument("subscription_id")

    resume_cmd = sub.add_parser("resume")
    resume_cmd.add_argument("session_id")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--state", default="all")

    get_cmd = sub.add_parser("get")
    get_cmd.add_argument("session_id")

    logs_cmd = sub.add_parser("logs")
    logs_cmd.add_argument("session_id")

    retry_cmd = sub.add_parser("retry-extract")
    retry_cmd.add_argument("session_id")
    retry_cmd.add_argument("--max-attempts", type=int, default=3)

    args = parser.parse_args()

    if args.command == "init":
        return _emit("init", subscription_id=args.subscription_id)
    if args.command == "resume":
        return _emit("resume", session_id=args.session_id)
    if args.command == "list":
        return _emit("list", state=args.state)
    if args.command == "get":
        return _emit("get", session_id=args.session_id)
    if args.command == "logs":
        return _emit("logs", session_id=args.session_id)
    if args.command == "retry-extract":
        return _emit("retry-extract", session_id=args.session_id, max_attempts=args.max_attempts)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
