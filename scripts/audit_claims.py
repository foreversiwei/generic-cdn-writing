#!/usr/bin/env python3
"""Validate a claim ledger before an article is drafted."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


ID_RE = re.compile(r"^C\d{3,}$")
OUTLINE_ID_RE = re.compile(r"\[(C\d{3,})\]")
CLAIM_TYPES = {
    "product-capability",
    "technical-mechanism",
    "quantitative-result",
    "price-version",
    "third-party-observation",
    "analysis",
}
VERDICTS = {"supported", "partially-supported", "inference", "unsupported"}
DECISIONS = {"use", "qualify", "omit"}
SOURCE_TYPES = {
    "official",
    "standard",
    "primary-data",
    "independent-test",
    "engineering-doc",
    "third-party",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    records: list[dict[str, object]] = []
    failures: list[str] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            failures.append(f"line {line_number}: invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            failures.append(f"line {line_number}: record must be an object")
            continue
        records.append(value)
    return records, failures


def audit_claims(ledger: Path, outline: Path) -> dict[str, object]:
    records, hard_fail = load_jsonl(ledger)
    warnings: list[str] = []
    seen: set[str] = set()
    usable: set[str] = set()
    omitted: set[str] = set()
    source_urls: list[str] = []

    for index, record in enumerate(records, start=1):
        prefix = f"record {index}"
        claim_id = str(record.get("id", ""))
        claim_type = str(record.get("claim_type", ""))
        verdict = str(record.get("verdict", ""))
        decision = str(record.get("decision", ""))
        claim = str(record.get("claim", "")).strip()
        section = str(record.get("section", "")).strip()
        sources = record.get("sources", [])

        if not ID_RE.fullmatch(claim_id):
            hard_fail.append(f"{prefix}: invalid claim id {claim_id!r}")
        elif claim_id in seen:
            hard_fail.append(f"{prefix}: duplicate claim id {claim_id}")
        else:
            seen.add(claim_id)
        if not claim or not section:
            hard_fail.append(f"{prefix}: claim and section are required")
        if claim_type not in CLAIM_TYPES:
            hard_fail.append(f"{prefix}: invalid claim_type {claim_type!r}")
        if verdict not in VERDICTS:
            hard_fail.append(f"{prefix}: invalid verdict {verdict!r}")
        if decision not in DECISIONS:
            hard_fail.append(f"{prefix}: invalid decision {decision!r}")
        if not isinstance(sources, list):
            hard_fail.append(f"{prefix}: sources must be a list")
            sources = []

        valid_source_types: set[str] = set()
        for source_index, source in enumerate(sources, start=1):
            source_prefix = f"{prefix} source {source_index}"
            if not isinstance(source, dict):
                hard_fail.append(f"{source_prefix}: source must be an object")
                continue
            url = str(source.get("url", "")).strip()
            source_type = str(source.get("type", ""))
            locator = str(source.get("locator", "")).strip()
            accessed_at = str(source.get("accessed_at", "")).strip()
            supports = str(source.get("supports", "")).strip()
            parts = urlsplit(url)
            if parts.scheme not in {"http", "https"} or not parts.netloc:
                hard_fail.append(f"{source_prefix}: invalid public URL")
            else:
                source_urls.append(url)
            if source_type not in SOURCE_TYPES:
                hard_fail.append(f"{source_prefix}: invalid source type {source_type!r}")
            else:
                valid_source_types.add(source_type)
            if not locator or not supports:
                hard_fail.append(f"{source_prefix}: locator and supports are required")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", accessed_at):
                hard_fail.append(f"{source_prefix}: accessed_at must be YYYY-MM-DD")

        if verdict in {"supported", "partially-supported", "inference"} and not sources:
            hard_fail.append(f"{prefix}: {verdict} claim has no source")
        if verdict == "unsupported" and decision != "omit":
            hard_fail.append(f"{prefix}: unsupported claim must be omitted")
        if verdict in {"partially-supported", "inference"} and decision != "qualify":
            hard_fail.append(f"{prefix}: {verdict} claim must be qualified")
        if verdict == "supported" and decision == "qualify":
            warnings.append(f"{claim_id}: supported claim is conservatively qualified")
        if decision == "use" and verdict != "supported":
            hard_fail.append(f"{prefix}: only supported claims may use decision=use")
        if claim_type in {"product-capability", "price-version"} and decision != "omit":
            if "official" not in valid_source_types:
                hard_fail.append(f"{prefix}: current product claim requires an official source")
        if claim_type == "quantitative-result" and decision != "omit":
            if not valid_source_types.intersection({"primary-data", "independent-test"}):
                hard_fail.append(
                    f"{prefix}: quantitative result requires primary-data or independent-test evidence"
                )

        if decision == "omit":
            omitted.add(claim_id)
        elif claim_id:
            usable.add(claim_id)

    outline_text = outline.read_text(encoding="utf-8")
    outline_ids = set(OUTLINE_ID_RE.findall(outline_text))
    if not outline_ids:
        hard_fail.append("outline contains no [C###] claim references")
    unknown = sorted(outline_ids - seen)
    if unknown:
        hard_fail.append(f"outline references unknown claims: {unknown}")
    omitted_references = sorted(outline_ids & omitted)
    if omitted_references:
        hard_fail.append(f"outline still references omitted claims: {omitted_references}")
    unused = sorted(usable - outline_ids)
    if unused:
        warnings.append(f"usable claims not referenced by outline: {unused}")
    duplicate_urls = sorted({url for url in source_urls if source_urls.count(url) > 1})
    if duplicate_urls:
        warnings.append("some sources support multiple claims; verify each locator independently")

    return {
        "ok": not hard_fail,
        "ledger_sha256": sha256(ledger),
        "outline_sha256": sha256(outline),
        "metrics": {
            "claim_count": len(records),
            "outline_claim_count": len(outline_ids),
            "usable_claim_count": len(usable),
            "omitted_claim_count": len(omitted),
            "unique_source_count": len(set(source_urls)),
        },
        "hard_fail": hard_fail,
        "warnings": warnings,
        "drafting_rule": "Draft only after this report passes and the user approves the source stage.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a per-claim source ledger before drafting.")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--outline", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.ledger.is_file():
        parser.error(f"ledger not found: {args.ledger}")
    if not args.outline.is_file():
        parser.error(f"outline not found: {args.outline}")
    payload = audit_claims(args.ledger, args.outline)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if payload["ok"] else 2)


if __name__ == "__main__":
    main()
