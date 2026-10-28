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
- `article-review-gate`（本 workflow 内置）：审查核心断言、证据边界、反方解释与修订闭环
- `article-to-lark-doc`：发布后归档带图版本
- `archify`：为技术文章生成高质量正文图表（架构/流程/时序/数据流图）
- `lanshu-animated-architecture-diagram`：可选，为文章封面或展示场景生成黑底手绘风格动图 GIF

### 可选增强依赖

- `find-skills`：当文章入口是“先发现 Skills 再写推荐文”
- `grill-me`：仅在选题、主张、读者对象或关键前提仍有实质歧义时，做发布前的交互式追问；不得默认要求用户走完整访谈
- `karpathy-guidelines`：仅用于审查 workflow/脚本等代码改动，不作为事实审稿器
- `ask`：用户明确要求第二意见，或高风险争议结论仍存在两种合理解释时，可询问本地 Claude/Gemini；不替代来源核验
- `guizang-social-card-skill`：生成主封面和方形封面
- `lanshu-animated-architecture-diagram`：可选，当封面需要更吸睛的黑底手绘动图效果时使用
- `drawio-mcp`：可选，通过 MCP 调用 draw.io 生成图表，适合需要人工拖拽编辑或导出为 .drawio 格式的场景（降级为 archify 或 ASCII 图）
- `aosp-linux-source`：当文章涉及 AOSP/Linux 源码核实时使用

## 降级规则

当某个依赖不可用时，按以下方式降级，不要卡死在中间步骤：

- 缺少 `find-skills`：跳过线上发现入口，只处理现有文章
- 缺少 `archify`：保留 ASCII 图和 Markdown 表格，不阻塞发布
- 缺少 `lanshu-animated-architecture-diagram`：跳过动图封面，回归正常封面生成流程
- 缺少 `drawio-mcp`：跳过 draw.io 图表生成，使用 archify 或 ASCII 图代替
- 缺少 `wx-article-code-review`：至少做一轮人工可读的公开信息合规检查，并明确标注“未完成正式审查”
- 核心来源不可访问：保留可核实部分，收窄或删除无法核实的断言，并在交付时标注具体未核验项；不得因审稿工具不可用而把推断写成事实
- 缺少 `guizang-social-card-skill`：从正文中选一张最相关、无私有信息的图片作为临时封面
- 缺少 `article-to-lark-doc`：发布后仅保留本地 Markdown 和图片文件，并说明未完成飞书归档
- 缺少 `aosp-linux-source`：不要伪造源码核实结果，明确标注“待人工核实上游源码”

降级只影响执行路径，不影响质量说明义务。凡是跳过的环节，都必须明确标注为“未完成”或“已降级处理”。

如果依赖本身存在，但外部网站、上游源码站或网络条件导致该环节无法真正完成，也按同样规则处理：不得假装已完成验证，必须显式标注“未完成”或“待人工核实”。

## 交付级别

### P0 必须完成

- 得到可发布的 `article.md` 或等价正文
- 存在可用封面图 `article-cover.png`
- 文章经过至少一轮内容审查，关键断言的证据边界和未核实项已记录
- 发布前公众号渲染检查与 preflight 通过
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

**开工第一步（任何发布任务）：先跑 kickoff 检查**，一次性暴露凭据/工具缺失，不留到封面/发布环节才发现：

```bash
python3 ~/.siada-cli/skills/content/wx-publish-workflow/scripts/preflight.py --kickoff <文章目录>
```

检查项：文章目录 `.env`（缺失自动从兄弟文章目录复制最新一份并置 600）、LABNANA_API_KEY（仅告警，缺则封面降级矢量方案）、node playwright 可用性。

```text
入口 A：已有文章
飞书文档 / 本地 Markdown
  -> 读取正文
  -> 改写润色
  -> 文章审查与修订
  -> 图表补强
  -> 发布前终审
  -> 封面生成
  -> 检查授权：明确发布指令则直接创建草稿；仅准备稿则等待确认
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

**生命周期原则（硬规则）：** 写任意一篇主题文章，都要先判断主题对象是否具有生命周期特
点（创建、初始化、使用/运行、销毁/释放、回收/退役等阶段）。如果有，就一定要把该对象的
生命周期写进文章：交代它的一头一尾和中间的流转，而不是只讲某一片段。这一条长期适用，不限
于系统/资源/源码类题材——凡是有“生老病死”的对象（进程、连接、资源、组件、订单、版本、
账户、数据等）都应带上完整生命周期视角。

进入本步骤后，必须读取并遵守：

- [`docs/style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:1)

主文件只保留该步骤的目标；故事钩子、金字塔结构、图文密度、标题层级和改写检查清单都以支持文档为准。

初稿完成后，立即进入 Step 4 的“文章审查门”做一轮早期校准；后续修改和补充来源后，发布前再做一次最终审查。

### Step 3：补充专业图表

如果文章是技术分析、架构拆解、源码机制说明，优先调用 `archify` 补专业图表；如果 `archify` 不可用，则保留 ASCII 图和表格即可。

进入本步骤且实际调用 `archify` 时，必须读取并遵守：

- [`docs/archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:1)
- [`docs/archify-export-sop.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-export-sop.md:1)

主文件只保留是否进入图表阶段的判断；图表数量门槛、类型分布、PNG 导出要求、时序图布局和图表验收清单都以支持文档为准。

硬规则：只要进入 `archify` 图表阶段，生成 HTML、删除 toolbar/footer、headless Chrome 截图、背景色差异裁剪、嵌回正文都属于必须子步骤；不能只生成 HTML 或只截图就算完成。

### Step 4：文章严谨性审查

本步骤承担初稿校准和发布前终审：初稿完成后轻量检查；事实、图表与来源补齐后做完整终审。详细审查清单与评审 Skill 适配规则统一见 [`docs/review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:1)。技术文章优先核查代码合规与上游实现；所有题材均核对关键断言、证据边界、反方解释及标题/正文/图表一致性。根据结果直接修订，并记录已修正项、未核实项及阻塞项；来源不可访问时须收窄或删除相关断言，不得把推断写成事实。

### Step 5：生成封面

正式发布前必须有封面图，但默认策略是“生成封面优先，正文选图兜底”。不要把“从正文随便抓一张技术图”当成默认方案。

进入本步骤后，必须继续遵守：

- [`docs/review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:1)

其中 Step 1.9 对应的封面内容提取、主封面和方形封面规格、导出操作、兜底方案和验收清单都以支持文档为准。

### Step 6：发布授权

按以下授权规则执行：

- 用户在当前任务中明确要求“发布”“继续发布”或“发公众号”，视为直接授权：在素材、审查与 preflight 均通过后，直接创建微信草稿，不再额外询问一次确认。
- 用户仅要求“写文章”“准备发布稿”“做成可发布版本”时，完成全部准备并展示正文、标题、图表和封面预览；只有用户随后明确说“确认/发布”才创建草稿。
- 用户明确要求修改已存在的草稿时，先核对 Media ID 与目标草稿标题；更新操作只限于用户指定版本。
- 用户在生成可审阅版本后回复“确认”“发布”或等义短指令，直接视为对当前已展示版本的发布授权，不重复询问。

发布授权不降低质量门槛。若审查发现未解决的高风险隐私/保密问题、关键数据矛盾、标题承诺无法兑现或来源冲突，应先修正并重新检查；只有在确认用户意图发生变化、原指令无法涵盖实质变更时，才返回用户确认。

“发布”在本 workflow 中仅指创建或更新微信草稿，不代表正式群发。任何情况下均不得自动群发。

### Step 6.5：本地预览检查（可选增强）

发布前，可生成一个本地 HTML 预览页，查看文章在微信中的实际排版效果。预览页包含：

- 顶部工具栏
- 一个 `复制 HTML` 按钮（点击后复制正文 HTML，可直接粘贴到公众号编辑器）
- 居中的微信正文预览区域（`max-width: 677px`）
- 响应式手机布局

预览页生成后，用浏览器打开确认排版无误再发布。如果发现问题，可返回修改文章后重新生成预览。

```bash
# 生成预览页后，在浏览器中打开确认
# 确认无误后复制 HTML 粘贴到公众号编辑器，或直接执行下一步发布
```

微信 HTML 约束（预览页复制的正文必须遵守）：

- 使用内联样式
- 禁用外部 CSS、脚本、Web 字体、CSS 变量
- 使用简单语义块：`section`、`h1`-`h3`、`p`、`table`、`blockquote`
- 卡片 `border-radius` 不超过 8px
- 复制内容为正文 HTML（不含外层 chrome）

此步骤为可选增强，不阻塞发布流程。

### Step 7：发布到微信草稿箱

**发布前必须先跑 preflight（硬门槛，不过不发）**：

```bash
python3 ~/.siada-cli/skills/content/wx-publish-workflow/scripts/preflight.py .
```

检查：主封面 2100×900、方形封面 1080×1080、正文所有本地图片引用存在、无「> 📷 图：」占位符残留。封面尺寸不合格时当场重生成，不流入 publish。

然后在工作目录执行，目录内需有 `.env`。

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

发布成功后，调用 `article-to-lark-doc` 归档。**归档直接复用 Step 7 发布用的同一份 `article.md`**——此时它已过 preflight，图片是真实本地引用，不再需要「归档图片范围」之类的二次确认；占位符替换由 article-to-lark-doc 内部完成。若该篇已有归档文档（目录下存在 `.archive*/doc-url` 或 `.lark-archive-url`），用 `docs +update` 更新已建文档，不要新建。

归档目标：

- 保留最终正文版本
- 保留图片引用关系
- 输出最终飞书文档链接

如果归档失败，至少保留本地 `article.md`、封面和配图，并说明“微信已发布，飞书归档未完成”。

### Step 8.5：系列回顾表同步（sync-series）

文章属于「Linux 延迟」系列时，发布新篇后必须同步所有已发布文章的「## 系列回顾」表，不要逐篇手动改。

1. 先把新篇补进 `~/.siada-cli/workspace/articles/planforlinux.md` 的「## 已发布」段（篇号、标题、飞书文档、本地文件）。planforlinux 是系列表的唯一权威来源。
2. 运行：

```bash
python3 ~/.siada-cli/skills/content/wx-publish-workflow/scripts/sync-series.py           # dry-run 看差异
python3 ~/.siada-cli/skills/content/wx-publish-workflow/scripts/sync-series.py --apply   # 批量写回 article.md
```

3. 如需对已建草稿的文章重建草稿（表格变了但正文没变）：

```bash
python3 .../sync-series.py --apply --publish
```

`--publish` 只对表格有变化且带 `.wechat-draft-media-id*` marker 的文章重跑 `feishu-wechat publish`，新 Media ID 存为下一个 `-vN` marker，不覆盖旧 marker。

注意：旧格式系列表（mp.weixin 链接、一二三编号）不在同步范围，脚本会跳过并提示。

**对外链接规则：** `planforlinux.md` 是内部规划，可保留飞书文档链接用于团队追溯；同步到文章正文的「系列回顾」表时，读者可见的链接必须指向对应的公众号文章（`mp.weixin.qq.com`），不得把飞书文档链接发布给读者。公众号文章链接尚未取得时，系列回顾行先显示纯标题，不生成飞书链接；取得公众号链接后再补入权威来源并同步。

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
- [ ] 已判断主题对象是否具有生命周期特点；若有，已将完整生命周期写入正文
- [ ] 已补充必要图表或确认本次跳过图表增强
- [ ] 已完成文章审查、适用的源码/合规核验及修订复查，并明确记录未完成项
- [ ] 已完成公众号渲染检查与 preflight
- [ ] 已准备 `article-cover.png`
- [ ] 发布授权符合 Step 6；明确发布指令不再重复询问
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
| 文章严谨性审查 | `docs/review-cover-postpublish.md` + 按需 `wx-article-code-review` / `aosp-linux-source` | 核验断言、证据边界、反方解释并闭环修订 |
| 源码核实 | `aosp-linux-source` | 核对 AOSP/Linux 公开源码 |
| 封面生成 | `guizang-social-card-skill` + `docs/review-cover-postpublish.md` | 生成公众号封面 |
| 微信发布 | `feishu-wechat-cli` | 发布到微信草稿箱 |
| 飞书归档 | `article-to-lark-doc` | 归档最终带图文章 |

## 一句话原则

先把文章变成“可公开发布、可被读懂、可被追溯”的版本，再去追求更完整的图表、封面和发布后互动；但只要进入某个阶段，就必须把该阶段对应的详细要求执行完整，不能因为主文件变短而少做步骤。
