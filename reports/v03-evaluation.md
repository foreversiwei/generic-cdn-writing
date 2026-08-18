# 0.3.0 Evaluation

- Evaluated at: 2026-08-18
- Evidence kind: deterministic regression and recorded fixtures; not a new provider run or human blind review

## Workflow tests

The 13 local unit tests cover the previous URL, keyword, heading and platform behavior plus:

1. a valid claim ledger mapped to outline Claim IDs;
2. rejection of unsupported and unknown claims;
3. sequential user approvals through the source stage;
4. rejection when an approved artifact changes;
5. rejection of “拆账单” in Zhihu prose;
6. warnings for content jargon and unordered-list dominance.

## Old-output regression

| Fixture | 0.3.0 result | Reason |
|---|---|---|
| `work/articles/platform-matrix/zhihu.md` | expected fail | contains “账单拆开”, the user-identified editorial-shortcut class |
| `work/articles/platform-matrix/seo-blog.md` | expected fail | title and body contain “账单拆分” |
| `work/articles/platform-matrix/README.md` | pass | task-oriented GitHub structure remains valid |
| `work/articles/high-traffic-cdn-cost/article.md` | pass with one warning | no banned shortcut; flat H2 hierarchy still needs human review |

The old fixtures do not contain `approval.json`, Claim IDs or claim-audit artifacts because they predate 0.3.0. They are style-regression inputs, not examples of the new approved workflow.

## Release gates

An isolated clean Git repository on `feat/generic-cdn-writing-v03` passed package validation, report consistency, secret scanning, diff checks, feature-branch checks, clean-worktree checks and all 13 unit tests. The release check recorded 7 passes, 2 warnings and 0 blocks. The warnings are intentionally retained for remote clean-install proof and provider-backed or human-reviewed output evidence.

## Missing evidence

A full 0.3.0 article has not been generated because the new workflow correctly requires real user approval after Brief, outline and source audit. Human preference, Zhihu readability, search performance and commercial effectiveness remain missing evidence.
