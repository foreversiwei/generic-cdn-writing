# Prior-Art Research

- Researched at: 2026-08-17
- Queries: `SEO article writing`; `content research writing workflow`; `technical article fact checking`; `branded content writing`
- Catalogs: skills.sh and SkillsMP, both completed for all four queries
- Candidate families returned: 97
- Rating evidence: unavailable; install counts and repository stars are not ratings

| Candidate | Relevance | skills.sh installs | GitHub repository stars | Source and license | Adopt | Reject |
|---|---|---:|---:|---|---|---|
| `SpaceZephyr/myskill` writing family (`doc-coauthoring`, `commercial-brief`, `content-topic-generator`, `ai-writing-assistant`) | Structured Chinese co-writing and commercial integration | not measured in this run | 335 | GitHub inspected; repository license not declared | Context gathering, staged outlining, material integration, honest weakness and natural placement | Overlapping root triggers, private persona files, hard-coded paths, fabricated-experience risk |
| `anthropics/knowledge-work-plugins:brand-voice-enforcement` | Voice constants, contextual tone and final validation | 3,000 | 23,527 | Apache-2.0; source inspected | Separate durable voice from platform- and audience-specific tone; validate voice after drafting | Dependence on absent brand files and multi-agent delegation as a runtime requirement |
| `epicenterhq/epicenter:technical-articles` | Direct technical argument and anti-template writing | 71 | 4,756 | repository reports `NOASSERTION`; source inspected | Takeaway titles, argument headings, mechanism-first prose, visuals only when useful | Code-heavy rhythm rule and house-voice dependency as universal requirements |
| `blink-new/claude:seo-article-writing` | Search intent, keyword research and internal links | 87 | 1 | no repository license declared; source inspected | Search intent, competitor gaps, title and internal-link planning | Fixed 1–2% keyword density, mandatory images, FAQ/table quotas, MDX and sitemap coupling |

Catalog metrics observed on 2026-08-17. skills.sh installs indicate ecosystem adoption only. GitHub stars describe repository attention, not the quality of an individual Skill.

## Keep / Adapt / Reject / Invent

### Keep

- Stage research, structure, drafting and review instead of drafting directly.
- Build the private model and reader question chain before public prose.
- Treat headings as arguments and product features as evidence for a reader problem.
- Validate voice, evidence and links after drafting.

### Adapt

- Convert commercial-brief product placement into evidence-bound third-party analysis.
- Replace generic brand voice with a 99CDN third-party voice plus Zhihu tone flex.
- Keep SEO search intent and internal links, but report keyword distribution rather than enforce density.
- Use source cards and a claim ledger instead of loading many full samples into every article.

### Reject

- Mandatory images, comparison tables, FAQs, fixed word counts and fixed keyword density.
- Fabricated personal experience, surprise reactions, customer cases or independent-review identity.
- Private style files, author signatures, macOS paths, CMS and MDX assumptions.
- Runtime dependence on multiple broad writing Skills with overlapping triggers.

### Invent

- One root router with five specialist reference modules and deterministic corpus/audit scripts.
- A five-layer corpus policy that separates product facts, third-party evidence, technical evidence, style samples and SEO samples.
- Explicit SEO/internal-link and soft-ad gates added to the existing technical-writing rubric.
- A hard-fail boundary for fake tests, unsupported product claims, missing required links and deceptive third-party voice.

## Evidence and limitations

- The dual-catalog research run is stored at workspace `work/prior-art-candidates.json`.
- Canonical source files for shortlisted candidates were inspected read-only; no third-party scripts were run or installed.
- Public ratings and skill-specific user reviews were unavailable.
- Design differences are source-visible. Article-quality improvement remains a hypothesis until output comparison and human blind review are completed.

## Platform-adapter iteration

- Researched at: 2026-08-18
- Queries: `Zhihu technical article writing`; `GitHub README technical writing`; `SEO blog article writing`; `platform specific content writing`
- Catalog result: skills.sh and SkillsMP completed all four queries; 95 candidate families
- Source review: canonical GitHub `SKILL.md` files inspected read-only; no candidate scripts executed
- Rating evidence: unavailable

| Candidate | skills.sh installs | GitHub stars | License | Keep / adapt | Reject |
|---|---:|---:|---|---|---|
| `samber/cc-skills:technical-article-writer` | 2,100 | 186 | MIT | Content-type routing, one thesis, one job per section, show-then-explain and opposing-view checks | Mandatory multi-stop interview, ten-title quota, runtime delegation to other broad writing Skills |
| `oil-oil/beautify-github-readme:beautify-github-readme` | 732 | 1,617 | MIT | README audience, value, proof and first-successful-action sequence; move long material to docs | Visual-design workflow, hero assets and beautification rules outside this Skill's writing job |
| `sickn33/agentic-awesome-skills:seo-aeo-blog-writer` | 93 | 45,072 | MIT | Direct answer near the top, continuous H2/H3, self-contained answers when FAQ evidence exists | Mandatory `What Is → Why → How`, exactly five FAQs, fixed length and extraction-oriented template |
| `acedatacloud/skills:zhihu` | 196 | 15 | NOASSERTION | Confirms that platform search/read/publish is a separate connector concern | Not a writing-style Skill; cookie/API and publication behavior stay outside scope |
| `miles990/claude-software-skills:content-platforms` | 50 | 20 | MIT | None for prose generation | CMS implementation patterns are a keyword collision, not writing prior art |

Mutable metrics were observed on 2026-08-18. Installs and repository stars remain adoption/attention signals, not quality ratings.

### Platform authorities and public samples

- [GitHub Docs: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) supports the project purpose, usefulness, getting-started, help and maintainer information model; it also recommends relative repository links and keeping long documentation elsewhere.
- [Google Search Central: helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) supports original analysis, clear sourcing, audience/task completion and avoiding search-engine-first mass content.
- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) supports natural organization, descriptive headings, relevant links and reader search terms; it explicitly rejects magic word counts, keyword stuffing and ideal heading quotas.
- Zhihu exposes no equivalent official prose template. Public technical answers such as [CPU 和 GPU 的区别](https://www.zhihu.com/question/19903344), [如何写出优雅的 React 组件](https://www.zhihu.com/question/304049417), [RabbitMQ 如何实现延时队列](https://www.zhihu.com/question/485302187) and [WebTransport 适用场景](https://www.zhihu.com/question/436182145) show multiple valid shapes: concise mechanism answers, long design arguments, implementation walkthroughs and scenario explainers. They are diversity samples, not a ranking or imitation set.

### New contribution ledger

- Keep: one root entry, evidence ledger, third-party disclosure boundary and deterministic audit.
- Adapt: article-type routing becomes platform + archetype routing; README story order becomes a text-only repository-task adapter; direct-answer SEO becomes conditional rather than a mandatory global skeleton.
- Reject: a universal Zhihu format, fixed FAQ/table/word-count quotas, GitHub beautification, publication connectors and CMS implementation.
- Invent: three mutually exclusive platform adapters, shared human-editing pass, platform-specific commercial roles, heading-level/generic-heading checks, and same-topic three-platform regression fixtures.

### Evidence boundary

The platform rules are a defensible public baseline, not the user's personal voice profile. Same-topic deterministic tests show structural separation and absence of named hard failures. They do not prove editorial preference, Zhihu engagement, search ranking or human-perceived naturalness. Those remain `missing evidence` until reviewed by the user or an independent editor.

## Human-gated evidence iteration

- Researched at: 2026-08-18
- Queries: `human in the loop editorial approval workflow`; `claim evidence audit article writing`; `source verified content writing workflow`; `natural Chinese technical article editing`
- Catalog result: skills.sh and SkillsMP completed all four queries; 98 candidate families
- Raw result: workspace `work/generic-cdn-writing-v03-prior-art.json`
- Rating evidence: unavailable

| Candidate | Useful mechanism | Adopt / adapt | Deliberate rejection |
|---|---|---|---|
| `jamditis/claude-skills-journalism:source-verification` | Claim-first verification record, source provenance, corroboration and explicit confidence | Adapted into one JSONL record per article claim, page locator, support boundary and `use / qualify / omit` decision | Broad OSINT, synthetic-media and newsroom investigation procedures are outside CDN article writing |
| `jamditis/claude-skills-journalism:editorial-workflow` | Named editorial statuses, reporter/editor handoffs and final sign-off | Adapted into sequential Brief, outline, source, draft and final approvals | Calendars, staffing, deadlines and newsroom administration add no value to this single-article skill |
| `rampstackco/claude-skills:ai-content-collaboration` | Humans own outline, voice, fact verification and final approval; AI accelerates bounded tasks | Kept human ownership at every transition and made fact verification a halt condition | Broad team policy, disclosure taxonomy and programmatic content governance remain outside this package |
| `vercel/eve:technical-writing` | Verify claims against current authoritative sources, preserve exact terms, make the minimum effective edit | Applied to source hierarchy, claim adjacency and natural-language review | Repository-specific commands, navigation and product naming do not transfer to CDN editorial work |

### Keep / adapt / reject / invent

- Keep: one platform adapter per article, source hierarchy, evidence-bound product claims and human semantic review.
- Adapt: the previous continuous workflow becomes a human-gated state machine; the old page-level source ledger becomes a claim-level ledger tied to the outline.
- Reject: one-click full-article generation, AI self-approval, mandatory newsroom overhead, universal punctuation bans and additional voice personas.
- Invent: approval records bound to artifact hashes; deterministic claim-to-outline coverage checks; a hard stop on unapproved source stages; Zhihu/SEO checks for editorial shorthand, jargon, filler, unordered-list dominance and dense “的” constructions.

### Evidence boundary

- Validated: both catalogs completed; four canonical source skills were inspected read-only; no third-party code was executed.
- Design advantage: every stage now has a visible user decision and every planned fact has an auditable record before drafting.
- Validated advantage: local tests cover claim audit, approval order and artifact tampering; the updated style audit rejects the prior Zhihu and SEO fixtures for the exact “账单拆开/账单拆分” class raised by the user.
- Hypothesis: repeated human checkpoints and paragraph-level material rules will improve final editorial preference. A new article cannot be generated under the new workflow until the user confirms its stages, so blind human output evidence remains missing.
