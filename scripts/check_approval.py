#!/usr/bin/env python3
"""Verify sequential, user-confirmed editorial stage approvals."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


STAGES = ("brief", "outline", "sources", "draft", "final")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check(state_path: Path, require: str, root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"ok": False, "hard_fail": [f"invalid approval JSON: {exc}"], "warnings": []}

    approvals = state.get("approvals", {})
    if not isinstance(approvals, dict):
        return {"ok": False, "hard_fail": ["approvals must be an object"], "warnings": []}

    required_index = STAGES.index(require)
    verified: list[str] = []
    for stage in STAGES[: required_index + 1]:
        record = approvals.get(stage)
        if not isinstance(record, dict):
            failures.append(f"{stage}: approval record missing")
            continue
        if record.get("status") != "approved":
            failures.append(f"{stage}: status is not approved")
        confirmed_by = str(record.get("confirmed_by", ""))
        if not confirmed_by.startswith("user"):
            failures.append(f"{stage}: confirmation must come from the user")
        confirmation = str(record.get("confirmation", "")).strip()
        if not confirmation:
            failures.append(f"{stage}: confirmation text is missing")
        confirmed_at = str(record.get("confirmed_at", ""))
        try:
            datetime.fromisoformat(confirmed_at)
        except ValueError:
            failures.append(f"{stage}: confirmed_at must be an ISO-8601 datetime")

        artifacts = record.get("artifacts", [])
        if not isinstance(artifacts, list) or not artifacts:
            failures.append(f"{stage}: at least one approved artifact is required")
            continue
        for item in artifacts:
            if not isinstance(item, dict):
                failures.append(f"{stage}: artifact entry must be an object")
                continue
            relative = Path(str(item.get("path", "")))
            artifact = root / relative
            if not inside(root, artifact):
                failures.append(f"{stage}: artifact escapes task root: {relative}")
                continue
            if not artifact.is_file():
                failures.append(f"{stage}: approved artifact missing: {relative}")
                continue
            expected = str(item.get("sha256", "")).lower()
            actual = sha256(artifact)
            if expected != actual:
                failures.append(f"{stage}: artifact changed after approval: {relative}")
        if not any(item.startswith(f"{stage}:") for item in failures):
            verified.append(stage)

    for later in STAGES[required_index + 1 :]:
        record = approvals.get(later)
        if isinstance(record, dict) and record.get("status") == "approved":
            warnings.append(f"later stage {later} is approved; verify stage history was not backfilled")

    return {
        "ok": not failures,
        "required_stage": require,
        "verified_stages": verified,
        "hard_fail": failures,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check sequential human approval records.")
    parser.add_argument("state", type=Path)
    parser.add_argument("--require", choices=STAGES, required=True)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.state.is_file():
        parser.error(f"approval state not found: {args.state}")
    root = (args.root or args.state.parent).resolve()
    payload = check(args.state.resolve(), args.require, root)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if payload["ok"] else 2)


if __name__ == "__main__":
    main()
