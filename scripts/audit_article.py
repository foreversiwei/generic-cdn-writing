#!/usr/bin/env python3
"""Run deterministic SEO, link, evidence, and style checks on Markdown articles."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
AI_PHRASES = (
    "在当今数字化时代",
    "随着科技的发展",
    "随着技术的发展",
    "众所周知",
    "不言而喻",
    "综上所述",
    "总而言之",
    "值得一提的是",
    "不难发现",
    "希望对你有所帮助",
)
DECEPTIVE_PATTERNS = (
    r"我亲测",
    r"亲测(?:有效|可用|省)",
    r"用了?之后.{0,16}(?:下降|提升|节省)",
    r"我们\s*99CDN",
    r"我司",
    r"本公司",
)
RISKY_CLAIM_PATTERNS = (
    r"(?:节省|降低|下降|提升|提高)\s*\d+(?:\.\d+)?\s*%",
    r"\d+(?:\.\d+)?\s*倍",
    r"(?:百万|千万|亿)级并发",
    r"\d+\s*(?:天|周|月|年)(?:内)?回本",
)


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in {"ref", "source"}
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


def first_title(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    frontmatter = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if frontmatter:
        title = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", frontmatter.group(1), re.MULTILINE)
        if title:
            return title.group(1).strip()
    return ""


def visible_text(text: str) -> str:
    value = CODE_FENCE_RE.sub("", text)
    value = re.sub(r"`[^`]+`", "", value)
    return value


def compact_phrase_count(text: str, phrase: str) -> int:
    """Count a phrase while treating whitespace as optional."""
    compact_text = re.sub(r"\s+", "", text).lower()
    compact_phrase = re.sub(r"\s+", "", phrase).lower()
    return compact_text.count(compact_phrase) if compact_phrase else 0


def compact_phrase_present(text: str, phrase: str) -> bool:
    return compact_phrase_count(text, phrase) > 0


def audit(
    text: str,
    primary_keyword: str,
    required_links: list[str],
    official_domains: list[str],
    minimum_official_sources: int,
) -> dict[str, object]:
    plain = visible_text(text)
    title = first_title(text)
    headings = HEADING_RE.findall(text)
    markdown_links = MARKDOWN_LINK_RE.findall(text)
    all_urls = sorted({canonical_url(url) for url in URL_RE.findall(text)})
    official_urls = [
        url
        for url in all_urls
        if domain_matches(urlsplit(url).netloc, official_domains)
    ]
    required = [canonical_url(url) for url in required_links]
    missing_links = [url for url in required if url not in all_urls]

    intro = re.split(r"^##\s+", plain, maxsplit=1, flags=re.MULTILINE)[0]
    keyword_exact_count = plain.lower().count(primary_keyword.lower()) if primary_keyword else 0
    keyword_count = compact_phrase_count(plain, primary_keyword) if primary_keyword else 0
    keyword_headings = sum(
        1 for heading in headings if compact_phrase_present(heading, primary_keyword)
    ) if primary_keyword else 0

    ai_hits = {phrase: plain.count(phrase) for phrase in AI_PHRASES if phrase in plain}
    deceptive_hits = [
        match.group(0)
        for pattern in DECEPTIVE_PATTERNS
        for match in re.finditer(pattern, plain, re.IGNORECASE)
    ]
    risky_hits = [
        match.group(0)
        for pattern in RISKY_CLAIM_PATTERNS
        for match in re.finditer(pattern, plain, re.IGNORECASE)
    ]

    hard_fail: list[str] = []
    warnings: list[str] = []
    if not title:
        hard_fail.append("missing H1 or frontmatter title")
    if primary_keyword and keyword_count == 0:
        hard_fail.append("primary keyword is absent")
    if missing_links:
        hard_fail.append(f"required internal links missing: {', '.join(missing_links)}")
    if len(official_urls) < minimum_official_sources:
        hard_fail.append(
            f"official source count {len(official_urls)} is below required {minimum_official_sources}"
        )
    if deceptive_hits:
        hard_fail.append("deceptive or unsupported first-person claims detected")

    if primary_keyword and not compact_phrase_present(title, primary_keyword):
        warnings.append("primary keyword is not present in title")
    if primary_keyword and not compact_phrase_present(intro, primary_keyword):
        warnings.append("primary keyword is not present before the first H2")
    if primary_keyword and keyword_headings == 0:
        warnings.append("primary keyword is not present in any heading")
    if risky_hits:
        warnings.append("quantified marketing or capacity claims require claim-ledger review")
    if ai_hits:
        warnings.append("common AI-style phrases detected")
    if len(headings) > 12:
        warnings.append("article has more than 12 headings; review fragmentation")

    anchor_texts = [anchor for anchor, _ in markdown_links]
    duplicate_anchors = sorted(
        {anchor for anchor in anchor_texts if anchor_texts.count(anchor) > 1}
    )
    if duplicate_anchors:
        warnings.append("duplicate link anchors detected; review anchor variety")

    return {
        "ok": not hard_fail,
        "title": title,
        "metrics": {
            "non_whitespace_characters": len(re.sub(r"\s+", "", plain)),
            "heading_count": len(headings),
            "primary_keyword": primary_keyword,
            "primary_keyword_count": keyword_count,
            "primary_keyword_exact_count": keyword_exact_count,
            "primary_keyword_heading_count": keyword_headings,
            "unique_url_count": len(all_urls),
            "official_source_count": len(official_urls),
            "required_internal_link_count": len(required),
        },
        "links": {
            "all": all_urls,
            "official": official_urls,
            "missing_required": missing_links,
            "duplicate_anchors": duplicate_anchors,
        },
        "signals": {
            "ai_phrase_hits": ai_hits,
            "deceptive_claim_hits": deceptive_hits,
            "risky_quantified_claim_hits": risky_hits,
        },
        "hard_fail": hard_fail,
        "warnings": warnings,
        "manual_review_required": [
            "technical correctness and source-to-claim fidelity",
            "Zhihu technical voice and argument quality",
            "third-party perspective and disclosure",
            "soft-ad naturalness",
            "semantic SEO and internal-link relevance",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit a Markdown article for deterministic content quality signals."
    )
    parser.add_argument("article", type=Path)
    parser.add_argument("--primary-keyword", default="")
    parser.add_argument("--internal-link", action="append", default=[])
    parser.add_argument("--official-domain", action="append", default=[])
    parser.add_argument("--min-official-sources", type=int, default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.article.is_file():
        parser.error(f"article not found: {args.article}")
    result = audit(
        args.article.read_text(encoding="utf-8"),
        args.primary_keyword,
        args.internal_link,
        [item.lower() for item in args.official_domain],
        args.min_official_sources,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
