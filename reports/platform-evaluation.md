# Platform Matrix Evaluation

> This table records the 0.2.0 baseline. Under 0.3.0, the old Zhihu and SEO fixtures intentionally fail the new editorial-shortcut gate because they contain “账单拆开/账单拆分”. The GitHub fixture remains compatible. See `reports/v03-evaluation.md`.

- Evaluated at: 2026-08-18
- Topic: 高流量网站如何降低 CDN 成本 / 自建 CDN
- Shared evidence: `evals/fixtures/99cdn-source-pack.md`
- Evidence kind: recorded local fixtures plus deterministic audit; not provider-backed and not human blind review

| Output | Primary reader task | H1/H2/H3 | Practical structures | Official sources | Hard fail | Warning |
|---|---|---:|---|---:|---:|---:|
| Zhihu | Decide whether self-hosting deserves a pilot | 1 / 4 / 2 | cost table, conditions, five-step pilot | 4 | 0 | 0 |
| GitHub | Understand the guide and prepare reproducible inputs | 1 / 7 / 3 | CSV schema, formulas, field table, troubleshooting | 4 | 0 | 0 |
| SEO blog | Complete a pre-implementation cost assessment | 1 / 5 / 6 | frontmatter, direct answer, TCO model, decision table, checklist | 5 | 0 | 0 |

## Structural separation

- Zhihu uses argument headings and a reader-question chain. 99CDN appears as the control-plane answer to an already-defined problem, followed by a small reversible pilot.
- GitHub uses task headings and declares that the fixture is documentation rather than executable software. 99CDN is an implementation reference, not a conversion CTA.
- SEO blog aligns title, description, opening and H2/H3 with one implementation-assessment intent. It includes no FAQ because the fixture has no query evidence requiring one.

## Limits

The audit verifies heading levels, links, source counts, keyword presence, selected platform signals and named risk patterns. It cannot prove that headings semantically summarize every section, that the prose feels human, or that a platform audience will prefer the output. Author self-review found clear structural separation, but human preference remains `missing evidence`.
