---
name: generic-cdn-writing
description: "通过 Brief、论点大纲、逐声明信源审计、初稿和终稿的人工确认流程，为 99CDN、自建 CDN 和 CDN 成本优化主题创作有证据、符合平台语境的中文技术内容。适用于知乎技术文章与第三方口吻软广、GitHub README/仓库指南、SEO 博客、关键词与内链规划、公开样本搜集、文章改写和发布前审校；当用户只要官方产品介绍、CDN 安装排障、平台代发布、虚构测评或抓取登录/付费内容时不要触发。"
---

# Generic CDN Writing

## 目标

用一个入口完成 CDN 内容的研究、平台适配、写作与审校。平台不是同一篇文章的格式皮肤：知乎、GitHub 和 SEO 博客分别使用不同的读者任务、文章原型、标题逻辑、排版语法和产品植入边界。

## Router Rules

在选择写作模式之前读取 [平台路由](references/platform-router.md)，规范化为：

- `zhihu`：知乎回答、专栏文章、第三方技术软文。
- `github`：仓库 README、`docs/` 指南、架构或决策记录。
- `seo-blog`：以搜索意图、页面元数据、关键词和内链为约束的博客。

平台未指定但任务是 99CDN 第三方软文时，默认 `zhihu` 并在 Brief 明示。每篇只加载一个平台适配器，不混用三套结构。

### 任务模式

- `素材模式`：搜集、分级、去重公开样本，交付来源卡片与缺口。
- `规划模式`：生成平台原型、搜索意图、关键词/链接计划与论证大纲。
- `成稿模式`：研究、规划、写作、平台编辑与审校；完整文章默认使用。
- `改写模式`：保留可证实事实，重建平台结构和论证，不做同义替换。
- `审校模式`：先交付问题、证据缺口和修改动作，不默认重写全文。

深度分为 `快速 / 标准 / 深度`。默认标准；三种深度都不能跳过事实门禁和终稿审校。

## Compact Workflow

完整文章与实质改写必须读取 [人工确认门](references/approval-gates.md)，按阶段暂停：

1. 生成 Brief，展示后等待用户确认。
2. 生成论点与大纲，为拟使用的事实分配 Claim ID，展示后等待确认。
3. 逐条建立信源账本并运行声明审计，展示后等待确认。
4. 通过前三道确认后才写初稿，展示初稿与问题后等待确认。
5. 用户批准初稿后编辑终稿；用户再次确认后才标记为最终稿。

用户说“直接写”不能跳过确认门。`快速 / 标准 / 深度` 只改变研究范围，不改变阶段数。

## Output Contract

- 共享产物：`brief.md`、`approval.json`、`sources.jsonl`、`seo-plan.md`、`outline.md`、`claims.jsonl`、`claim-audit.json`、`draft.md`、`review.md` 和 `audit.json`。
- 知乎：`article.md`，采用论点推进和可执行决策方法。
- GitHub：`README.md` 或 `docs/<slug>.md`，采用仓库任务与可复现输入。
- SEO 博客：`article.md` 加 frontmatter 或 `seo-meta.md`，采用单一搜索意图。

## 强制工作流

### 1. 固化 Brief

记录主题、Platform ID、文章原型、目标读者、读者任务、核心判断、主次关键词、必须链接、产品角色、推广强度、篇幅、来源限制、禁止声明与交付路径。采用保守默认时也必须展示给用户确认，不能在内部直接越过 Brief。

标准模式输出到 `work/articles/<slug>/`：

```text
brief.md
approval.json
sources.jsonl
seo-plan.md
outline.md
claims.jsonl
claim-audit.json
draft.md
article.md / README.md / docs/<slug>.md
review.md
audit.json
```

完整字段和各模式产物见 [工作流](references/workflow.md)。生成 `brief.md` 后立即暂停，按 [人工确认门](references/approval-gates.md) 等待用户确认。

### 2. 建立来源账本

执行 [来源与样本政策](references/source-policy.md)。区分产品官方事实、通用技术证据、第三方判断和平台风格样本。样本只用于抽象结构特征，不得冒充产品证据，也不得近似模仿具体作者。

产品能力、价格、版本、性能、节点数和量化收益优先回到当前官方页面。大纲中的每个外部可核验事实都要分配 Claim ID，写入 `claims.jsonl`，再运行：

```powershell
python scripts/audit_claims.py claims.jsonl `
  --outline outline.md `
  --output claim-audit.json
```

为每条声明标记 `supported / partially-supported / inference / unsupported` 和 `use / qualify / omit`。审计通过后展示给用户确认；证据不足时删除或降级表达，禁止补造数据、案例、亲测和独立评测身份。

### 3. 选择平台原型

读取 [平台路由](references/platform-router.md)，选择一个主原型，再只读取对应适配器：

- [知乎适配器](references/zhihu-style.md)
- [GitHub 适配器](references/github-style.md)
- [SEO 博客适配器](references/seo-blog-style.md)

先写一句核心判断和读者追问/任务链，再设计标题。每节注明将使用的 Claim ID 和结构组件。标题层级由信息关系决定，不设置固定 H2 数量，不强制每篇使用表格、FAQ 或相同目录。展示 `outline.md` 后暂停，等待用户确认。

### 4. 规划 SEO 与链接

执行 [SEO 与内链](references/seo-linking.md)。SEO 博客需要完整页面级计划；知乎只保留自然可发现性与相关链接；GitHub 优先仓库任务和相对链接，不做关键词堆叠。

### 5. 起草并控制软广

先运行 `python scripts/check_approval.py approval.json --require sources`。未通过时不得起草。

执行 [第三方软广](references/soft-ad.md)。先解决读者问题，再让 99CDN 对应已经提出的技术变量或操作任务。用户要求单独产品段落时必须满足，但标题要说明产品在当前论证中的角色，不能退化成官网功能清单。

第三方口吻是独立分析视角，不是伪装成无商业关系的用户。至少说明一个不适用条件、成本转移、实施风险或回退路径。

初稿写入 `draft.md`，展示给用户确认；未确认前不要覆盖为最终 `article.md`。

### 6. 做平台编辑

收到“确认初稿”后，读取 [人工编辑层](references/human-editing.md)，分逻辑、节奏、可信感三遍编辑。优先删掉无推进作用的句子，修复空泛标题、机械列表、对称段落、黑话和重复总结；不要通过错别字、随意口语或随机句长伪装成人类。知乎和 SEO 博客优先采用自然段和有序步骤，无序列表只承载真正并列且顺序无意义的项目。

### 7. 独立审校

重新打开 Brief、来源账本和 [质量评分](references/quality-rubric.md)，不要沿用起草时的自我解释。运行：

```powershell
python scripts/audit_article.py article.md `
  --platform zhihu `
  --primary-keyword "主关键词" `
  --internal-link "必须链接" `
  --official-domain 99cdn.com `
  --official-domain docs.99cdn.com `
  --output audit.json
```

`--platform` 可取 `zhihu`、`github`、`seo-blog`。脚本只提供确定性信号；技术推导、平台文风和软广自然度仍需人工逐项判断。

## Gate Ladder

只有以下条件全部满足，且用户明确“确认终稿”，才标记最终稿：

1. 产品关键声明能回到当前来源，没有虚构数据、测试、客户或节省结果。
2. 已选择且只使用一个平台适配器，交付路径和格式符合该平台任务。
3. 标题层级连续，标题能总领正文，不是随意截取句子或通用目录词。
4. 文章交付模型、步骤、清单、验证方法或停止条件等真实实用价值。
5. 关键词和链接自然、相关、可解释；产品内容不取代主体论证。
6. 自动审计无 hard fail，人工 rubric 任一维度不低于满分的 60%。
7. Brief、大纲、信源、初稿和终稿的批准记录顺序完整，批准文件哈希与当前文件一致。

仍有缺口时标记 `草稿 / 待核验`，不要降低门禁。

## 边界

- 不负责 CDN 安装、生产配置和故障排查。
- 不自动发布知乎、写入 CMS、修改线上仓库或操作账号。
- 不抓取非公开、登录后、付费或禁止访问内容。
- 不保证排名、收录、流量、转化或具体成本节省。
- 不用第三方口吻隐藏必须披露的商业关系。

## 资源

- [平台路由](references/platform-router.md)
- [工作流与产物](references/workflow.md)
- [人工确认门](references/approval-gates.md)
- [来源与样本政策](references/source-policy.md)
- [SEO 与内链](references/seo-linking.md)
- [知乎适配器](references/zhihu-style.md)
- [GitHub 适配器](references/github-style.md)
- [SEO 博客适配器](references/seo-blog-style.md)
- [人工编辑层](references/human-editing.md)
- [第三方软广](references/soft-ad.md)
- [质量评分](references/quality-rubric.md)
