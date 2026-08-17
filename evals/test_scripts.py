from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class ScriptTests(unittest.TestCase):
    def test_source_cards_normalize_and_deduplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sources.md"
            output = root / "sources.jsonl"
            source.write_text(
                "[Docs](https://docs.99cdn.com/user/site/cache?utm_source=x)\n\n"
                "[Duplicate](https://docs.99cdn.com/user/site/cache#rules)\n\n"
                "[Style](https://zhuanlan.zhihu.com/p/123)\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "build_source_cards.py"),
                    str(source),
                    "--official-domain",
                    "docs.99cdn.com",
                    "--style-domain",
                    "zhihu.com",
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            cards = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(cards), 2)
            self.assertEqual({card["source_type"] for card in cards}, {"official", "style"})

    def test_article_audit_passes_supported_article(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            article = root / "article.md"
            report = root / "audit.json"
            article.write_text(
                "# 自建CDN如何改变成本结构\n\n"
                "自建CDN不会让流量消失，它改变的是成本结构。\n\n"
                "## 自建CDN先看缓存与回源\n\n"
                "参考[缓存文档](https://docs.99cdn.com/user/site/cache)并查看"
                "[99CDN](https://www.99cdn.com/)。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--primary-keyword",
                    "自建CDN",
                    "--internal-link",
                    "https://www.99cdn.com/",
                    "--official-domain",
                    "99cdn.com",
                    "--output",
                    str(report),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["ok"])

    def test_article_audit_blocks_missing_link_and_fake_test(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "bad.md"
            article.write_text(
                "# 自建CDN体验\n\n我亲测自建CDN一定能省钱。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--primary-keyword",
                    "自建CDN",
                    "--internal-link",
                    "https://www.99cdn.com/",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertGreaterEqual(len(payload["hard_fail"]), 2)

    def test_article_audit_treats_keyword_spacing_as_equivalent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "spaced.md"
            article.write_text(
                "# 自建 CDN 成本\n\n自建 CDN 需要计算总成本。\n\n"
                "## 自建 CDN 的边界\n\n"
                "参考[官网](https://www.99cdn.com/)。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--primary-keyword",
                    "自建CDN",
                    "--internal-link",
                    "https://www.99cdn.com/",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["metrics"]["primary_keyword_exact_count"], 0)
            self.assertEqual(payload["metrics"]["primary_keyword_count"], 3)


if __name__ == "__main__":
    unittest.main()
