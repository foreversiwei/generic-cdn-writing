#!/usr/bin/env python3
"""Extract, normalize, classify, and deduplicate Markdown source links."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
TRACKING_KEYS = {"fbclid", "gclid", "ref", "source"}


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_KEYS
    ]
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), "")
    )


def domain_matches(host: str, configured: list[str]) -> bool:
    host = host.lower().split(":", 1)[0]
    return any(host == item or host.endswith(f".{item}") for item in configured)


def classify(url: str, official_domains: list[str], style_domains: list[str]) -> str:
    host = urlsplit(url).netloc
    if domain_matches(host, official_domains):
        return "official"
    if domain_matches(host, style_domains):
        return "style"
    return "third_party"


def paragraph_context(text: str, start: int, end: int) -> str:
    left = text.rfind("\n\n", 0, start)
    right = text.find("\n\n", end)
    left = 0 if left < 0 else left + 2
    right = len(text) if right < 0 else right
    value = re.sub(r"\s+", " ", text[left:right]).strip()
    return value[:800]


def build_cards(
    inputs: list[Path],
    official_domains: list[str],
    style_domains: list[str],
    captured_at: str,
) -> list[dict[str, object]]:
    cards: dict[str, dict[str, object]] = {}
    for input_path in inputs:
        text = input_path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            title, raw_url = match.groups()
            url = canonical_url(raw_url)
            context = paragraph_context(text, match.start(), match.end())
            if url in cards:
                sources = cards[url]["input_files"]
                if str(input_path) not in sources:
                    sources.append(str(input_path))
                continue
            cards[url] = {
                "id": hashlib.sha256(url.encode("utf-8")).hexdigest()[:12],
                "title": re.sub(r"\s+", " ", title).strip(),
                "url": url,
                "domain": urlsplit(url).netloc.lower(),
                "source_type": classify(url, official_domains, style_domains),
                "captured_at": captured_at,
                "context": context,
                "context_sha256": hashlib.sha256(context.encode("utf-8")).hexdigest(),
                "input_files": [str(input_path)],
                "trust_grade": None,
                "supported_claims": [],
                "unsupported_claims": [],
                "duplicate_of": None,
            }
    return sorted(cards.values(), key=lambda card: (card["source_type"], card["url"]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build deduplicated JSONL source cards from Markdown links."
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Markdown input files.")
    parser.add_argument("--output", required=True, type=Path, help="JSONL output path.")
    parser.add_argument("--official-domain", action="append", default=[])
    parser.add_argument("--style-domain", action="append", default=[])
    parser.add_argument("--captured-at", default=date.today().isoformat())
    args = parser.parse_args()

    missing = [str(path) for path in args.inputs if not path.is_file()]
    if missing:
        parser.error(f"input files not found: {', '.join(missing)}")

    cards = build_cards(
        args.inputs,
        [item.lower() for item in args.official_domain],
        [item.lower() for item in args.style_domain],
        args.captured_at,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for card in cards:
            handle.write(json.dumps(card, ensure_ascii=False) + "\n")

    counts: dict[str, int] = {}
    for card in cards:
        key = str(card["source_type"])
        counts[key] = counts.get(key, 0) + 1
    print(
        json.dumps(
            {"ok": True, "output": str(args.output), "total": len(cards), "types": counts},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
