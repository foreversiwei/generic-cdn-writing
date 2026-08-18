# Creation Handoff

## Result

- Skill: `generic-cdn-writing` 0.3.0
- Job: route evidence-bound CDN content through user-confirmed Brief, argument outline, claim-level source audit, draft and final stages into one of three platform-native outputs.
- Path: `.agents/skills/generic-cdn-writing`
- Status: 0.3.0 governed release candidate, prepared for publication through a feature branch, pull request and immutable versioned release.

## 0.3.0 iteration

- `jamditis/claude-skills-journalism:source-verification`: contributed claim-specific verification trails; broad OSINT procedures were rejected.
- `jamditis/claude-skills-journalism:editorial-workflow`: contributed explicit statuses and sign-off; newsroom calendars and staffing were rejected.
- `rampstackco/claude-skills:ai-content-collaboration`: contributed the rule that humans own outline, facts, voice and final approval; broad team governance was rejected.
- `vercel/eve:technical-writing`: contributed current-source verification and minimum effective edits; repository-specific conventions were rejected.

Original additions are `approval-gates.md`, artifact-hash approvals, `audit_claims.py`, `check_approval.py`, and platform-aware natural-Chinese/list checks in `audit_article.py`.

## Reference skills studied

- `samber/cc-skills:technical-article-writer`: kept content-type selection, a one-sentence thesis and one job per section; rejected mandatory interviews, title quotas and runtime writer delegation.
- `oil-oil/beautify-github-readme:beautify-github-readme`: kept audience/value/proof/first-action ordering and README-to-docs boundaries; rejected visual redesign and asset-generation scope.
- `sickn33/agentic-awesome-skills:seo-aeo-blog-writer`: kept an early direct answer and semantic heading hierarchy; rejected the fixed `What Is → Why → How → five FAQ` skeleton.
- `acedatacloud/skills:zhihu`: confirmed that Zhihu search/read/publish is a connector concern; rejected it as style prior art.
- `miles990/claude-software-skills:content-platforms`: rejected as a CMS implementation keyword collision.

Official guidance from GitHub Docs and Google Search Central anchors README and SEO behavior. Zhihu has no equivalent official prose specification, so its adapter uses diverse public technical answers plus Chinese technical-writing norms as a baseline without imitating individual authors.

## Absorbed and invented

- Keep: source ledger, claim status, third-party disclosure, product-boundary checks and deterministic audit.
- Adapt: the old Zhihu-only argument stage becomes `platform → archetype → outline`; SEO depth changes by platform; product placement has three distinct roles.
- Reject: one universal article format, fixed H2/FAQ/table/word-count quotas, fake first-person experience and GitHub soft-ad copy.
- Invent: mutually exclusive `zhihu / github / seo-blog` adapters, shared three-pass human editing, heading hierarchy and generic-heading signals, and same-topic platform-matrix fixtures.

## Advantages and evidence

- **Design advantage:** each platform has a separate reader task, content archetype set, heading grammar, layout behavior and commercial boundary. Evidence: `platform-router.md` and three adapter references.
- **Validated advantage:** trigger evaluation and package validation are rerun for each candidate version; deterministic tests now cover source-claim mapping, sequential user approvals, tamper detection, editorial shorthand and unordered-list dominance.
- **Validated regression:** the stricter 0.3.0 audit rejects the previous Zhihu and SEO fixtures for “账单拆开/账单拆分”, while the GitHub fixture remains compatible with its task-oriented style.
- **Hypothesis:** human checkpoints plus claim-level evidence and natural-Chinese editing should improve editorial preference. A new article must pass real user confirmations before that claim can be evaluated; platform engagement, search ranking and cross-model stability remain missing evidence.

## Verification and limits

- Completed: dual-catalog prior-art search, five source Skill inspections, official platform guidance review, trigger eval, unit tests, structure validation and three platform-specific output audits.
- Same-topic fixtures: `work/articles/platform-matrix/zhihu.md`, `README.md` and `seo-blog.md`.
- An isolated clean Git fixture proved the branch, worktree, package, report, secret-scan and 13-test gates. Remote discovery and clean-install evidence are tracked separately by the governed publisher.
- No independent editor or user preference review has been recorded. The current Zhihu profile is a public baseline, not a claim that the user's personal voice is fully learned.
