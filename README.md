# Generic CDN Writing

> 不再记住一串写作 Skill：只描述 CDN 文章任务，就能得到来源账本、SEO/内链计划、知乎式技术文章和审计结果。

## 为什么值得用

普通写作流程容易在“研究、SEO、软广、去 AI 味”之间反复切换，而且多个泛写作 Skill 会争夺大纲和文风。本 Skill 只提供一个入口，后台仍保留完整阶段，并用明确产物把事实、策略、正文和审校隔离开。

它主要面向 99CDN、自建 CDN、CDN 成本、缓存、回源和 DNS 调度等中文技术内容。第三方口吻用于独立分析，不用于伪造亲测或隐藏必须披露的商业关系。

## 安装

发布后使用以下命令安装：

```bash
npx skills add foreversiwei/generic-cdn-writing
```

验证可发现的 Skill：

```bash
npx skills add foreversiwei/generic-cdn-writing --list
```

在本工作区中也可以自然语言触发，或明确写 `$generic-cdn-writing`。

## 你可以直接这样说

- “用标准模式写一篇知乎技术文章：高流量网站如何降低 CDN 成本，平衡推广 99CDN。”
- “先搜集并去重自建 CDN、缓存命中率和回源成本的中文样本，不写正文。”
- “这是初稿、关键词和三个内链，改成第三方技术分析口吻并去 AI 味。”
- “审校这篇 99CDN 软文，逐条核验产品声明、SEO 和内链。”
- “用深度模式先分析搜索结果的内容缺口，再给大纲和文章。”

## 它会交付什么

标准模式默认在 `work/articles/<slug>/` 形成：

```text
brief.md       任务、读者、关键词、链接和禁止声明
sources.jsonl  规范化、分级、去重后的来源卡片
seo-plan.md    搜索意图、关键词簇和内链映射
outline.md     核心判断、追问链、证据和产品出现位置
article.md     知乎式第三方技术文章
audit.json     自动信号、hard fail、warning 和人工检查项
```

快速模式复用已有语料；标准模式增量检索并完整审校；深度模式增加搜索结果、第三方样本和技术来源分析。三种模式都不能跳过事实和终稿门禁。

## 前置条件

- [x] Python 3.10 或更高：`python --version`
- [x] 当前工作区可写，用于文章中间产物和报告
- [ ] 需要补充互联网资料时，环境应提供只读网页搜索或读取能力
- [ ] 需要当前 99CDN 产品事实时，发布前应能访问官网或帮助文档

不需要 API key。脚本只处理本地 Markdown 和审计结果；互联网检索由宿主环境已有能力完成。

## 验证

在 Skill 根目录运行：

```powershell
python scripts/validate_skill.py .
python -m unittest discover -s evals -p "test_*.py" -v
```

来源卡片示例：

```powershell
python scripts/build_source_cards.py evals/fixtures/99cdn-source-pack.md `
  --official-domain 99cdn.com `
  --official-domain docs.99cdn.com `
  --output work/sources.jsonl
```

文章审计示例：

```powershell
python scripts/audit_article.py article.md `
  --primary-keyword "自建CDN" `
  --internal-link "https://www.99cdn.com/" `
  --official-domain 99cdn.com `
  --min-official-sources 4 `
  --output audit.json
```

## 配置

Skill 不使用环境变量。每篇文章的变化项写进 Brief：平台、读者、主次关键词、必须内链、推广对象、软广强度、篇幅、来源限制和禁止声明。

## 风险与边界

- 不保证搜索排名、收录、流量、转化或成本节省。
- 不虚构亲测、客户、价格、性能数字和回本周期。
- 不自动发布知乎、不写入线上 CMS、不操作账号。
- 不抓取登录、付费或禁止访问内容。
- 自动审计只检查确定性信号，不能替代技术编辑和人类盲评。

## Troubleshooting

| 问题 | 原因 | 解决 |
|---|---|---|
| 没有自动触发 | 工作区未发现 Skill，或请求只涉及安装排障 | 重新打开工作区并明确写 `$generic-cdn-writing`；安装排障使用专门 CDN 教练 |
| 抓到很多重复文章 | 同一稿件被多个站转载 | 规范化 URL，并在来源账本标记正文近似重复，只保留原始来源 |
| 审计提示关键词不在标题 | 标题使用了同义表达 | 判断是否影响搜索意图；需要时自然加入，不能机械堆词 |
| 审计通过但文章仍像广告 | 自动脚本不能判断语义与自然度 | 按 `references/quality-rubric.md` 做人工软广和知乎文风复核 |
| 官网暂时不可达 | 当前产品事实无法复核 | 标记 `missing evidence`，不要把旧快照写成当前事实 |
| 必须内链很生硬 | 链接目标与论点不相关 | 更换文章角度、锚文本或目标页；不要强行植入 |

## 致谢

设计研究参考了以下公开 Skill 的机制，不复制其私有内容或长段文字：

- `SpaceZephyr/myskill` 的 `doc-coauthoring`、`commercial-brief`、`content-topic-generator` 和 `ai-writing-assistant`
- `anthropics/knowledge-work-plugins` 的 `brand-voice-enforcement`
- `epicenterhq/epicenter` 的 `technical-articles`
- `blink-new/claude` 的 `seo-article-writing`

完整取舍和证据见 `reports/prior-art-research.md`。

## License

MIT。详见 `LICENSE`。
