from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def validate(root: Path) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    skill_file = root / "SKILL.md"
    manifest_file = root / "manifest.json"

    if not skill_file.is_file():
        failures.append("missing SKILL.md")
        meta = {}
    else:
        meta = frontmatter(skill_file.read_text(encoding="utf-8"))
        if not NAME_PATTERN.fullmatch(meta.get("name", "")):
            failures.append("SKILL.md name must use lowercase hyphenated form")
        if not meta.get("description"):
            failures.append("SKILL.md description is missing")

    if not manifest_file.is_file():
        failures.append("missing manifest.json")
    else:
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            if manifest.get("name") != meta.get("name"):
                failures.append("manifest name does not match SKILL.md")
            if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
                failures.append("manifest version must be semantic X.Y.Z")
        except json.JSONDecodeError as exc:
            failures.append(f"invalid manifest.json: {exc}")

    nested = [path for path in root.rglob("SKILL.md") if path != skill_file]
    if nested:
        failures.append("nested discoverable SKILL.md files are not allowed")
    for required in ("README.md", "agents/interface.yaml", "evals/trigger_cases.json"):
        if not (root / required).is_file():
            failures.append(f"missing {required}")
    for reference in re.findall(r"\]\((references/[^)]+)\)", skill_file.read_text(encoding="utf-8") if skill_file.is_file() else ""):
        if not (root / reference).is_file():
            failures.append(f"missing referenced file: {reference}")

    return {"ok": not failures, "root": str(root), "failures": failures, "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Generic CDN Writing skill package.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    args = parser.parse_args()
    report = validate(Path(args.skill_dir).resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
