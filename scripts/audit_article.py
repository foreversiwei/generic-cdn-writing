#!/usr/bin/env python3
"""Run deterministic SEO, link, evidence, and style checks on Markdown articles."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
HEADING_ENTRY_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
ORDERED_LIST_RE = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)
UNORDERED_LIST_RE = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\s*\|.+\|\s*$", re.MULTILINE)
GENERIC_HEADINGS = {
    "背景",
    "背景介绍",
    "核心优势",
    "功能亮点",
    "产品优势",
    "解决方案",
    "总结",
    "总结与展望",
    "未来展望",
    "结语",
}
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
    "值得注意的是",
    "需要注意的是",
    "由此可见",
)
BANNED_EDITORIAL_SHORTCUTS = ("拆账单", "账单拆开", "账单拆分")
JARGON_PHRASES = (
    "打通链路",
    "跑通闭环",
    "拉齐认知",
    "沉淀方法论",
    "赋能",
    "抓手",
    "底层逻辑",
    "全链路能力",
)
FILLER_PHRASES = (
    "在一定程度上",
    "从某种意义上说",
    "可以说",
    "从本质上看",
    "这一点很重要",
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


def prose_paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", visible_text(text))
    paragraphs: list[str] = []
    for block in blocks:
        stripped = block.strip()
        if not stripped or stripped.startswith(("#", "|", "- ", "* ", "+ ")):
            continue
        if re.fullmatch(r"(?:\d+\.\s+.*\n?)+", stripped):
            continue
        if re.search(r"[\u4e00-\u9fffA-Za-z]", stripped):
            paragraphs.append(re.sub(r"\s+", "", stripped))
    return paragraphs


def sentence_lengths(text: str) -> list[int]:
    prose = re.sub(r"\s+", "", visible_text(text))
    return [len(item) for item in re.split(r"[。！？!?；;]+", prose) if item]


def coefficient_of_variation(values: list[int]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance) / mean


def compact_phrase_count(text: str, phrase: str) -> int:
    """Count a phrase while treating whitespace as optional."""
    compact_text = re.sub(r"\s+", "", text).lower()
    compact_phrase = re.sub(r"\s+", "", phrase).lower()
    return compact_text.count(compact_phrase) if compact_phrase else 0


def compact_phrase_present(text: str, phrase: str) -> bool:
    return compact_phrase_count(text, phrase) > 0


def audit(
    text: str,
    platform: str,
    primary_keyword: str,
    required_links: list[str],
    official_domains: list[str],
    minimum_official_sources: int,
) -> dict[str, object]:
    plain = visible_text(text)
    title = first_title(text)
    headings = HEADING_RE.findall(text)
    heading_entries = [
        (len(marks), value.strip())
        for marks, value in HEADING_ENTRY_RE.findall(text)
    ]
    heading_levels = [level for level, _ in heading_entries]
    heading_level_counts = {
        str(level): heading_levels.count(level) for level in range(1, 7)
    }
    heading_jumps = [
        {"from": previous, "to": current, "heading": heading_entries[index][1]}
        for index, (previous, current) in enumerate(
            zip(heading_levels, heading_levels[1:]), start=1
        )
        if current > previous + 1
    ]
    generic_headings = [
        value
        for _, value in heading_entries
        if re.sub(r"[\s：:？?！!]", "", value) in GENERIC_HEADINGS
    ]
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
    banned_shortcuts = {
        phrase: plain.count(phrase)
        for phrase in BANNED_EDITORIAL_SHORTCUTS
        if phrase in plain
    }
    jargon_hits = {
        phrase: plain.count(phrase) for phrase in JARGON_PHRASES if phrase in plain
    }
    filler_hits = {
        phrase: plain.count(phrase) for phrase in FILLER_PHRASES if phrase in plain
    }
    paragraphs = prose_paragraphs(text)
    opening_counts = Counter(paragraph[:5] for paragraph in paragraphs if paragraph)
    repeated_openers = {
        opening: count for opening, count in opening_counts.items() if count >= 3
    }
    lengths = sentence_lengths(text)
    sentence_length_cv = coefficient_of_variation(lengths)
    chinese_character_count = len(re.findall(r"[\u4e00-\u9fff]", plain))
    de_count = plain.count("的")
    de_per_100_chinese = (
        de_count / chinese_character_count * 100 if chinese_character_count else 0.0
    )
    heavy_de_sentences = [
        sentence.strip()
        for sentence in re.split(r"[。！？!?；;]+", plain)
        if sentence.count("的") >= 5
    ]
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
    if heading_level_counts["1"] > 1:
        hard_fail.append("multiple H1 headings detected")
    if heading_jumps:
        hard_fail.append("heading level jumps detected")
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
    if platform in {"zhihu", "seo-blog"} and banned_shortcuts:
        hard_fail.append("banned editorial shortcut detected in audience-facing prose")

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
    if jargon_hits:
        warnings.append("content-industry jargon requires plain-language review")
    if filler_hits:
        warnings.append("low-information filler phrases detected")
    if repeated_openers:
        warnings.append("repeated paragraph openings may expose a writing template")
    if len(lengths) >= 10 and sentence_length_cv < 0.27:
        warnings.append("sentence lengths are unusually uniform")
    if de_per_100_chinese > 7.0 or heavy_de_sentences:
        warnings.append("dense 的 constructions require a natural-Chinese review")
    if len(headings) > 12:
        warnings.append("article has more than 12 headings; review fragmentation")
    if generic_headings:
        warnings.append("generic headings detected; verify that headings summarize their sections")
    if heading_level_counts["2"] >= 4 and heading_level_counts["3"] == 0:
        warnings.append("long outline has no H3; review whether the hierarchy is too flat")

    ordered_items = len(ORDERED_LIST_RE.findall(text))
    unordered_items = len(UNORDERED_LIST_RE.findall(text))
    table_rows = len(TABLE_ROW_RE.findall(text))
    code_fences = len(re.findall(r"^```", text, re.MULTILINE)) // 2
    lower_plain = plain.lower()
    if (
        platform in {"zhihu", "seo-blog"}
        and unordered_items >= 4
        and unordered_items > ordered_items
    ):
        warnings.append(
            "unordered list items dominate; use ordered steps or prose unless items are truly peer-level"
        )
    if platform == "zhihu":
        if (
            len(re.sub(r"\s+", "", plain)) > 1200
            and ordered_items + unordered_items + table_rows + code_fences == 0
        ):
            warnings.append(
                "long Zhihu article has no checklist, table, code, or other structured practical block"
            )
    elif platform == "github":
        if code_fences == 0:
            warnings.append("GitHub content has no fenced command or code example")
        if not any(
            marker in lower_plain
            for marker in ("quick start", "getting started", "快速开始", "安装", "使用")
        ):
            warnings.append("GitHub content has no clear getting-started or usage section")
    elif platform == "seo-blog":
        frontmatter = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        has_description = bool(
            frontmatter
            and re.search(r"^description:\s*.+$", frontmatter.group(1), re.MULTILINE)
        )
        if not has_description:
            warnings.append("SEO blog has no frontmatter meta description")
        if heading_level_counts["2"] == 0:
            warnings.append("SEO blog has no H2 structure")

    anchor_texts = [anchor for anchor, _ in markdown_links]
    duplicate_anchors = sorted(
        {anchor for anchor in anchor_texts if anchor_texts.count(anchor) > 1}
    )
    if duplicate_anchors:
        warnings.append("duplicate link anchors detected; review anchor variety")

    return {
        "ok": not hard_fail,
        "platform": platform,
        "title": title,
        "metrics": {
            "non_whitespace_characters": len(re.sub(r"\s+", "", plain)),
            "heading_count": len(headings),
            "heading_level_counts": heading_level_counts,
            "heading_level_jumps": heading_jumps,
            "generic_heading_count": len(generic_headings),
            "ordered_list_item_count": ordered_items,
            "unordered_list_item_count": unordered_items,
            "unordered_to_ordered_ratio": round(
                unordered_items / ordered_items, 3
            ) if ordered_items else (None if unordered_items else 0.0),
            "table_row_count": table_rows,
            "code_fence_count": code_fences,
            "prose_paragraph_count": len(paragraphs),
            "sentence_length_cv": round(sentence_length_cv, 3),
            "de_count": de_count,
            "de_per_100_chinese": round(de_per_100_chinese, 3),
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
            "banned_editorial_shortcut_hits": banned_shortcuts,
            "content_jargon_hits": jargon_hits,
            "filler_phrase_hits": filler_hits,
            "repeated_paragraph_openers": repeated_openers,
            "heavy_de_sentence_count": len(heavy_de_sentences),
            "heavy_de_sentence_samples": heavy_de_sentences[:3],
            "deceptive_claim_hits": deceptive_hits,
            "risky_quantified_claim_hits": risky_hits,
            "generic_headings": generic_headings,
        },
        "hard_fail": hard_fail,
        "warnings": warnings,
        "manual_review_required": [
            "technical correctness and source-to-claim fidelity",
            f"{platform} platform fidelity and reader-task completion",
            "heading-to-section semantic fit",
            "third-party perspective and disclosure",
            "soft-ad naturalness",
            "semantic SEO and internal-link relevance",
            "claim-ledger coverage and approval-state integrity",
            "paragraph-level information gain and natural Chinese",
            "ordered versus unordered list fit",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit a Markdown article for deterministic content quality signals."
    )
    parser.add_argument("article", type=Path)
    parser.add_argument(
        "--platform",
        choices=("zhihu", "github", "seo-blog"),
        default="zhihu",
    )
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
        args.platform,
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
