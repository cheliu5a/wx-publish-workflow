---
name: wx-publish-workflow
description: Use when publishing a Feishu doc or local Markdown article to a WeChat Official Account draft in this environment, especially when the workflow should include rewriting, review, cover generation, and archive steps.
---

# 公众号发布工作流

这个 skill 负责把一篇文章从“已有内容”推进到“微信草稿箱 + 飞书归档”。

它是一个总控 workflow，用来判断入口、编排步骤、约束最低交付门槛，并把详细规则路由到对应支持文档。为了保证功能不缩水，凡是进入某个阶段，就必须同时遵守主文件和对应支持文档的要求。

## 何时使用

在以下场景使用本 skill：

- 用户明确说“发公众号”“发布到公众号”“把飞书文档发到微信公众号”
- 用户已经有飞书文档或本地 Markdown，希望按固定流程发布到微信草稿箱
- 用户希望先整理一批可分享的 Skills，再写成公众号文章发布
- 用户希望发布前包含内容润色、图表补强、合规审查、封面生成和归档

## 不适用场景

以下情况不要直接套用整套 workflow：

- 只是想写文章，不打算发到微信草稿箱
- 只是想做封面图，不需要文章改写和发布
- 只是想把 Markdown 转成飞书文档归档
- 没有微信公众号发布凭证，且当前任务不要求走真实发布链路
- 短通知、纯新闻快讯、无结构公告，不值得套用完整图表和封面流程

## 支持文档

以下支持文档是本 skill 的正式组成部分，不是可选参考。命中对应阶段时，必须读取并遵守：

- [`docs/entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:1)：入口 B 的候选发现、质量筛选、Skill 卡片和文章草稿组织规则
- [`docs/style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:1)：正文改写规范、故事钩子、金字塔结构、图文密度与检查清单
- [`docs/archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:1)：`archify` 图表数量、类型分布、导出要求、时序图布局和验收清单
- [`docs/archify-export-sop.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-export-sop.md:1)：`archify` 删除 toolbar/footer、Chrome 截图、Retina 参数、背景色差异裁剪的详细脚本
- [`docs/review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:1)：源码审查、封面生成、封面导出和发布后三问的详细要求

## 依赖分层

### 必需依赖

- `feishu-wechat-cli`：发布到微信草稿箱
- `lark-doc` 或等价方式：从飞书读取正文

### 强烈建议依赖

- `wx-article-code-review`：发布前做合规和技术审查
- `article-to-lark-doc`：发布后归档带图版本
- `archify`：为技术文章生成高质量图表

### 可选增强依赖

- `find-skills`：当文章入口是“先发现 Skills 再写推荐文”
- `guizang-social-card-skill`：生成主封面和方形封面
- `aosp-linux-source`：当文章涉及 AOSP/Linux 源码核实时使用

## 降级规则

当某个依赖不可用时，按以下方式降级，不要卡死在中间步骤：

- 缺少 `find-skills`：跳过线上发现入口，只处理现有文章
- 缺少 `archify`：保留 ASCII 图和 Markdown 表格，不阻塞发布
- 缺少 `wx-article-code-review`：至少做一轮人工可读的公开信息合规检查，并明确标注“未完成正式审查”
- 缺少 `guizang-social-card-skill`：从正文中选一张最相关、无私有信息的图片作为临时封面
- 缺少 `article-to-lark-doc`：发布后仅保留本地 Markdown 和图片文件，并说明未完成飞书归档
- 缺少 `aosp-linux-source`：不要伪造源码核实结果，明确标注“待人工核实上游源码”

降级只影响执行路径，不影响质量说明义务。凡是跳过的环节，都必须明确标注为“未完成”或“已降级处理”。

如果依赖本身存在，但外部网站、上游源码站或网络条件导致该环节无法真正完成，也按同样规则处理：不得假装已完成验证，必须显式标注“未完成”或“待人工核实”。

## 交付级别

### P0 必须完成

- 得到可发布的 `article.md` 或等价正文
- 存在可用封面图 `article-cover.png`
- 文章经过至少一轮发布前检查
- 成功进入微信草稿箱，或明确说明为什么未能发布

### P1 强烈建议完成

- 内容按公众号风格改写
- 技术文章补充图表或表格
- 完成正式 code review / 源码核实
- 发布后归档到飞书文档

### P2 可选增强

- 从线上发现 Skills 并组织成推荐文
- 生成 21:9 主封面和 1:1 方形封面
- 在用户明确不需要互动时，才跳过发布后的 3 个理解问题

## 入口判断

按下面顺序判断入口：

1. 用户已经提供飞书文档链接或本地 Markdown：走“入口 A”
2. 用户要“推荐一批 skills 并发公众号”：走“入口 B”
3. 两种材料都没有：先让用户提供文章来源，或说明当前只能输出草稿，不能真实发布

## 总流程

```text
入口 A：已有文章
飞书文档 / 本地 Markdown
  -> 读取正文
  -> 改写润色
  -> 图表补强
  -> 发布前审查
  -> 封面生成
  -> 人工确认
  -> 发布到微信草稿箱
  -> 归档到飞书文档

入口 B：先发现 Skills 再成文
find-skills 发现候选
  -> 质量筛选
  -> 生成卡片和文章草稿
  -> 接入入口 A 的“改写润色”步骤继续执行
```

## 前置条件

在工作目录准备 `.env`：

```bash
WECHAT_APP_ID=你的公众号AppID
WECHAT_APP_SECRET=你的公众号AppSecret
```

还需把当前机器出口 IP 加入公众号后台白名单。

```bash
curl ifconfig.me
```

## 入口 B：先发现 Skills 再整理成文

只有当用户明确要“找几个 skills 推荐给大家”“整理 skills 发公众号”时才走这一入口。

进入该入口后，必须读取并遵守：

- [`docs/entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:1)

主文件只保留入口判断和衔接逻辑；候选发现、质量筛选、Skill 卡片格式、文章草稿结构和完成清单都以支持文档为准。

硬规则：入口 B 产出的 `article.md` 只是草稿，后续必须进入 Step 2 做公众号风格改写，不能跳过改写直接进入发布。

## 主线步骤

### Step 1：读取正文

如果用户给的是飞书文档，优先用 `lark-doc` 读取为 Markdown；如果用户已经给了本地 Markdown，可直接进入下一步。

示例：

```bash
lark-cli docs +fetch --api-version v2 \
  --doc "https://your.feishu.cn/wiki/xxxx" \
  --doc-format markdown --as user > article.md
```

### Step 2：按公众号风格改写正文

目标不是“把原文重新说一遍”，而是把文章整理成适合公众号阅读的结构。

进入本步骤后，必须读取并遵守：

- [`docs/style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:1)

主文件只保留该步骤的目标；故事钩子、金字塔结构、图文密度、标题层级和改写检查清单都以支持文档为准。

### Step 3：补充专业图表

如果文章是技术分析、架构拆解、源码机制说明，优先调用 `archify` 补专业图表；如果 `archify` 不可用，则保留 ASCII 图和表格即可。

进入本步骤且实际调用 `archify` 时，必须读取并遵守：

- [`docs/archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:1)
- [`docs/archify-export-sop.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-export-sop.md:1)

主文件只保留是否进入图表阶段的判断；图表数量门槛、类型分布、PNG 导出要求、时序图布局和图表验收清单都以支持文档为准。

硬规则：只要进入 `archify` 图表阶段，生成 HTML、删除 toolbar/footer、headless Chrome 截图、背景色差异裁剪、嵌回正文都属于必须子步骤；不能只生成 HTML 或只截图就算完成。

### Step 4：发布前审查

优先调用 `wx-article-code-review`。如果文章涉及 AOSP/Linux 机制，再结合 `aosp-linux-source` 做上游核实。

进入本步骤后，必须读取并遵守：

- [`docs/review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:1)

其中 Step 1.5 对应的合规扫描、源码核实、优化润色、通过条件都以支持文档为准。

### Step 5：生成封面

正式发布前必须有封面图，但默认策略是“生成封面优先，正文选图兜底”。不要把“从正文随便抓一张技术图”当成默认方案。

进入本步骤后，必须继续遵守：

- [`docs/review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:1)

其中 Step 1.9 对应的封面内容提取、主封面和方形封面规格、导出操作、兜底方案和验收清单都以支持文档为准。

### Step 6：人工确认

在真正发布前，必须让用户或执行者确认以下几点：

- 标题和导语没有偏题
- 图表没有暴露内部信息
- 封面可接受
- 文章已通过基本审查

如果用户没有明确确认，可以继续准备草稿，但不要假装“已获确认”。

硬规则：没有人工确认时，可以继续整理草稿，但不得执行真实发布到微信草稿箱。

### Step 7：发布到微信草稿箱

在工作目录执行，目录内需有 `.env`。

```bash
# 从飞书文档直接发布
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx" \
  --article-title "文章标题" \
  --article-author "作者名"

# 或从本地 Markdown 发布
feishu-wechat publish -f article.md --article-cover ./article-cover.png
```

成功标志：输出包含类似“发布成功，Media ID: xxxxx”的结果。

如果发布失败，要优先检查：

- AppID / Secret 是否正确
- IP 是否已加白名单
- 正文是否缺标题
- 封面路径是否有效

### Step 8：归档到飞书文档

发布成功后，优先调用 `article-to-lark-doc`，把包含图片的最终版本归档到飞书文档。

归档目标：

- 保留最终正文版本
- 保留图片引用关系
- 输出最终飞书文档链接

如果归档失败，至少保留本地 `article.md`、封面和配图，并说明“微信已发布，飞书归档未完成”。

### Step 9：发布后三问

默认应执行发布后三问；只有当用户明确只要求发布、不要求互动时，才可跳过，但跳过时必须显式说明。

进入本步骤后，必须继续遵守：

- [`docs/review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:1)

其中题目数量、题型范围、提问格式和回答后的处理方式都以支持文档为准。

## 常见问题

- `invalid ip`：检查出口 IP 是否已加入公众号后台白名单
- `invalid appid or secret`：检查 `.env` 中的 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`
- 未能找到文章标题：在 Markdown 顶部补 `title` 或等价 frontmatter
- `archify` 不可用：退回 ASCII 图和表格，不阻塞发布主线
- 源码核实超时：明确标注“待人工补充核实”，不要伪造校验结论

## 最终检查清单

- [ ] 已判断入口 A 或入口 B
- [ ] 已得到可发布的 `article.md`
- [ ] 已完成至少一轮内容改写或结构整理
- [ ] 已补充必要图表或确认本次跳过图表增强
- [ ] 已完成发布前检查，并明确记录未完成项
- [ ] 已准备 `article-cover.png`
- [ ] 已发布到微信草稿箱，或明确说明失败原因
- [ ] 已归档到飞书，或明确说明归档未完成
- [ ] 若执行 Skills 推荐文入口，是否已完成候选筛选和卡片整理
- [ ] 若执行发布后三问，是否严格按 3 道题输出

## 各能力分工

| 环节 | 默认能力 | 责任 |
|------|----------|------|
| Skills 发现 | `find-skills` | 搜索和筛选候选 Skills |
| 飞书读取 | `lark-doc` | 把飞书文档拉成 Markdown |
| 正文改写 | 本 skill + `docs/style-guide.md` | 规定公众号结构和质量门槛 |
| 技术图表 | `archify` + `docs/archify-requirements.md` + `docs/archify-export-sop.md` | 生成专业图表和导出图片 |
| 发布前审查 | `wx-article-code-review` + `docs/review-cover-postpublish.md` | 做合规和技术准确性检查 |
| 源码核实 | `aosp-linux-source` | 核对 AOSP/Linux 公开源码 |
| 封面生成 | `guizang-social-card-skill` + `docs/review-cover-postpublish.md` | 生成公众号封面 |
| 微信发布 | `feishu-wechat-cli` | 发布到微信草稿箱 |
| 飞书归档 | `article-to-lark-doc` | 归档最终带图文章 |

## 一句话原则

先把文章变成“可公开发布、可被读懂、可被追溯”的版本，再去追求更完整的图表、封面和发布后互动；但只要进入某个阶段，就必须把该阶段对应的详细要求执行完整，不能因为主文件变短而少做步骤。
