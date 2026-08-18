from __future__ import annotations

import json
import hashlib
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

    def test_article_audit_blocks_heading_level_jump(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "jump.md"
            article.write_text(
                "# 自建 CDN 指南\n\n"
                "参考[官网](https://www.99cdn.com/)。\n\n"
                "### 跳过二级标题\n\n正文。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--primary-keyword",
                    "自建CDN",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertIn("heading level jumps detected", payload["hard_fail"])

    def test_github_platform_reports_task_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "README.md"
            article.write_text(
                "# 自建 CDN 成本评估工具\n\n"
                "用一份可复现的清单核对成本，并参考"
                "[99CDN](https://www.99cdn.com/)。\n\n"
                "## 快速开始\n\n"
                "```powershell\npython audit.py --input costs.csv\n```\n\n"
                "## 使用范围\n\n只评估账单结构，不生成生产配置。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--platform",
                    "github",
                    "--primary-keyword",
                    "自建CDN",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["platform"], "github")
            self.assertEqual(payload["metrics"]["code_fence_count"], 1)
            self.assertFalse(
                any("getting-started" in item for item in payload["warnings"])
            )

    def test_seo_blog_platform_detects_metadata_and_hierarchy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text(
                "---\n"
                "title: 自建 CDN 成本怎么评估\n"
                "description: 从流量、节点和运维三项判断自建 CDN 是否值得。\n"
                "slug: self-hosted-cdn-cost\n"
                "---\n\n"
                "# 自建 CDN 成本怎么评估\n\n"
                "自建 CDN 是否省钱，取决于总拥有成本。参考"
                "[99CDN](https://www.99cdn.com/)。\n\n"
                "## 先拆总拥有成本\n\n"
                "### 流量与回源\n\n先记录流量命中率。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--platform",
                    "seo-blog",
                    "--primary-keyword",
                    "自建CDN",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["platform"], "seo-blog")
            self.assertNotIn(
                "SEO blog has no frontmatter meta description",
                payload["warnings"],
            )
            self.assertEqual(payload["metrics"]["heading_level_counts"]["3"], 1)

    def test_article_audit_blocks_banned_zhihu_shortcut(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text(
                "# 自建 CDN 成本\n\n先拆账单，再判断自建 CDN 是否值得。\n\n"
                "## 记录现有支出\n\n参考[官网](https://www.99cdn.com/)。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--platform",
                    "zhihu",
                    "--primary-keyword",
                    "自建CDN",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2)
            self.assertIn("拆账单", payload["signals"]["banned_editorial_shortcut_hits"])

    def test_article_audit_warns_on_jargon_and_unordered_list_dominance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text(
                "# 自建 CDN 的评估方法\n\n自建 CDN 需要先明确成本范围。\n\n"
                "## 需要核对的条件\n\n"
                "- 打通链路\n- 形成抓手\n- 检查流量\n- 检查回源\n\n"
                "参考[官网](https://www.99cdn.com/)。\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_article.py"),
                    str(article),
                    "--platform",
                    "seo-blog",
                    "--primary-keyword",
                    "自建CDN",
                    "--official-domain",
                    "99cdn.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            joined = " ".join(payload["warnings"])
            self.assertIn("jargon", joined)
            self.assertIn("unordered list items dominate", joined)

    def test_claim_audit_passes_supported_outline_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = root / "outline.md"
            ledger = root / "claims.jsonl"
            report = root / "claim-audit.json"
            outline.write_text(
                "# 大纲\n\n## 缓存规则需要单独验证\n\n- [C001] 说明文档中的缓存控制范围。\n",
                encoding="utf-8",
            )
            ledger.write_text(
                json.dumps(
                    {
                        "id": "C001",
                        "section": "缓存规则需要单独验证",
                        "claim": "99CDN 文档提供按路径设置缓存规则的说明",
                        "claim_type": "product-capability",
                        "verdict": "supported",
                        "decision": "use",
                        "sources": [
                            {
                                "url": "https://docs.99cdn.com/user/site/cache.html",
                                "type": "official",
                                "locator": "缓存设置章节",
                                "accessed_at": "2026-08-18",
                                "supports": "页面说明了缓存规则入口与匹配方式",
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_claims.py"),
                    str(ledger),
                    "--outline",
                    str(outline),
                    "--output",
                    str(report),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["ok"])

    def test_claim_audit_blocks_unsupported_and_unmapped_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            outline = root / "outline.md"
            ledger = root / "claims.jsonl"
            outline.write_text("# 大纲\n\n- [C002] 固定节省比例。\n", encoding="utf-8")
            ledger.write_text(
                json.dumps(
                    {
                        "id": "C001",
                        "section": "成本",
                        "claim": "所有网站都能节省 50%",
                        "claim_type": "quantitative-result",
                        "verdict": "unsupported",
                        "decision": "use",
                        "sources": [],
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "audit_claims.py"),
                    str(ledger),
                    "--outline",
                    str(outline),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2)
            self.assertTrue(any("unsupported claim must be omitted" in item for item in payload["hard_fail"]))
            self.assertTrue(any("unknown claims" in item for item in payload["hard_fail"]))

    def test_approval_gate_passes_sequential_user_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifacts = {}
            for name in ("brief.md", "outline.md", "claim-audit.json"):
                path = root / name
                path.write_text(name + "\n", encoding="utf-8")
                artifacts[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            state = {
                "schema_version": "1.0",
                "current_stage": "sources",
                "approvals": {
                    "brief": {
                        "status": "approved",
                        "confirmed_by": "user",
                        "confirmed_at": "2026-08-18T15:30:00+08:00",
                        "confirmation": "确认 Brief",
                        "artifacts": [{"path": "brief.md", "sha256": artifacts["brief.md"]}],
                    },
                    "outline": {
                        "status": "approved",
                        "confirmed_by": "user",
                        "confirmed_at": "2026-08-18T15:40:00+08:00",
                        "confirmation": "确认大纲",
                        "artifacts": [{"path": "outline.md", "sha256": artifacts["outline.md"]}],
                    },
                    "sources": {
                        "status": "approved",
                        "confirmed_by": "user",
                        "confirmed_at": "2026-08-18T16:00:00+08:00",
                        "confirmation": "确认信源",
                        "artifacts": [
                            {"path": "claim-audit.json", "sha256": artifacts["claim-audit.json"]}
                        ],
                    },
                },
            }
            state_path = root / "approval.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "check_approval.py"),
                    str(state_path),
                    "--require",
                    "sources",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_approval_gate_blocks_changed_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            brief = root / "brief.md"
            brief.write_text("before\n", encoding="utf-8")
            state = {
                "approvals": {
                    "brief": {
                        "status": "approved",
                        "confirmed_by": "user",
                        "confirmed_at": "2026-08-18T15:30:00+08:00",
                        "confirmation": "确认 Brief",
                        "artifacts": [
                            {
                                "path": "brief.md",
                                "sha256": hashlib.sha256(brief.read_bytes()).hexdigest(),
                            }
                        ],
                    }
                }
            }
            state_path = root / "approval.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            brief.write_text("after\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "check_approval.py"),
                    str(state_path),
                    "--require",
                    "brief",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(result.returncode, 2)
            self.assertTrue(any("changed after approval" in item for item in payload["hard_fail"]))


if __name__ == "__main__":
    unittest.main()
