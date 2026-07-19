---
name: wx-publish-workflow
description: 将飞书文档发布为微信公众号文章的完整工作流。先按公众号风格规范（导语 + 图文并茂 + 多图表）对文章进行改写润色，再用 archify 根据文章技术内容生成专业架构图/流程图/时序图/数据流图（输出独立 HTML 文件，支持导出 PNG/SVG），嵌入文章后用 wx-article-code-review 审查源码合规（含通过 aosp-linux-source 对照 AOSP/Linux 上游源码进行技术准确性校验），通过后用 feishu-wechat-cli 直接发布到微信草稿箱。适用场景：用户说"发公众号"、"把飞书文档发到公众号"、"发布文章"、"公众号发布流程"、"按工作流发布"。
---

# 公众号发布工作流

```
飞书文档
   ↓
【Step 1.2 风格改写润色】← 导语 + 图文并茂 + 多图表（ASCII/表格）
   ↓
【Step 1.3 archify 图表生成】← 根据技术内容生成架构图/流程图/时序图/数据流图（HTML+PNG）
   ↓
【Step 1.5 wx-article-code-review】← 合规审查 + aosp-linux-source 源码校验
   ↓ 通过（无 🚫 RED 项）
【人工确认】← 确认内容无误
   ↓
【Step 2 feishu-wechat-cli】← 直接发布到微信草稿箱（需 AppID/Secret）
```

---

## 前置条件

在工作目录准备 `.env` 文件：

```bash
WECHAT_APP_ID=你的公众号AppID
WECHAT_APP_SECRET=你的公众号AppSecret
```

还需把当前机器 IP 加入公众号后台白名单（安全中心 → IP 白名单，`curl ifconfig.me` 查询当前 IP）。

---

## Step 1：读取飞书文档

用 `lark-doc` 读取飞书文档内容（如已有本地 Markdown 可跳过）：

```bash
lark-cli docs +fetch --api-version v2 \
  --doc "https://your.feishu.cn/wiki/xxxx" \
  --doc-format markdown --as user > article.md
```

---

## Step 1.2：按公众号风格规范改写润色

拿到原始 Markdown 后，按以下风格规范对文章进行改写，**直接输出改写后的完整 Markdown**（在原文件上修改）：

### 🎯 风格规范

#### 1. 导语（必须有）

- 文章开头（正文第一段，在标题下方、第一个二级标题之前）必须有一段 **100~200 字的导语**
- 导语用「场景切入」或「问题钩子」的方式引出主题，让读者快速感知文章价值
- 示例格式：
  ```
  你知道拍一张照片，数据是怎么从摄像头流向屏幕的吗？……
  让这条链路高效运转的幕后英雄，叫做 `dma-buf`。……
  ```

#### 2. 图文并茂（必须有图 / 图表）

- 每个一级概念（每个大章节）至少配一个可视化元素：ASCII 流程图、Markdown 表格、或代码 + 注释
- 优先顺序：**ASCII 流程图 > Markdown 表格 > 代码块注释**
- 微信不支持 Mermaid 渲染，统一改用 ASCII 流程图或表格

#### 3. 图表密度要求

- 文章中 **表格数量 ≥ 3**（关键 API 对比、参数说明、场景对比等都用表格呈现）
- 文章中 **ASCII 流程图 / 示意图 ≥ 2**（数据流向、生命周期、调用链等用 ASCII 图呈现）
- 避免连续超过 3 段纯文字，超过则插入一张图或一个表格打断

#### 4. 段落节奏

- 每段不超过 5 句话，避免大段密集文字
- 重要结论用 `> 引用块` 或加粗单独成行突出
- 列表（`-`）用于枚举，表格用于对比，流程图用于流程

#### 5. 标题层级

- 一级标题（`#`）：仅文章标题
- 二级标题（`##`）：大章节（如「一、为什么需要...」「二、架构全景图」）
- 三级标题（`###`）：小节

### 🔧 改写操作清单

改写时逐项检查：

- [ ] 文章开头是否有导语（100~200 字）？没有则补写
- [ ] 每个大章节是否有 ASCII 图或表格？没有则补充
- [ ] 全文表格数量是否 ≥ 3？不足则将适合表格化的内容转为表格
- [ ] 全文 ASCII 流程图是否 ≥ 2？不足则补充架构图或数据流图
- [ ] 有无连续 3 段以上纯文字段落？有则插入图表打断
- [ ] 重要结论是否突出显示？

---

## Step 1.3：archify 专业技术图表生成

完成风格改写后，分析文章的技术内容，用 `archify` skill 为文章生成专业的可视化图表，**输出为独立 HTML 文件**（内嵌 SVG，支持明暗主题切换，可一键导出 PNG/SVG）。

### 📊 图表类型选择

根据文章内容匹配最合适的图表类型：

| 文章内容类型 | archify 图表类型 | 典型场景 |
|------------|---------------|---------|
| 系统架构、模块组成、组件关系 | `architecture` | 内核子系统架构、驱动框架、SoC 结构 |
| 调用流程、数据处理管道、审批链路 | `workflow` | 系统调用链、驱动初始化流程、CI/CD |
| API 交互、请求生命周期、跨模块调用 | `sequence` | 内核/用户态交互、IPC 调用链、DMA 传输 |
| 数据流向、缓冲区传递、管道/ETL | `dataflow` | dma-buf 共享链路、内存拷贝路径、数据总线 |
| 状态机、生命周期、状态转换 | `lifecycle` | buffer 生命周期、进程状态、设备电源状态 |

### 🔧 图表生成操作

1. **分析文章**：识别哪些章节最适合用专业图表替换或补充 ASCII 图
2. **选择类型**：根据上表选择最匹配的 archify 图表类型
3. **生成图表**：调用 archify skill 生成，每张图输出为独立 HTML 文件，命名格式：`<文章名>-<图表描述>.<类型>.html`

```bash
# 示例：生成 dma-buf 数据流图
node ~/.siada-cli/skills/archify/bin/archify.mjs render dataflow dma-buf.dataflow.json dma-buf-dataflow.html

# 示例：生成架构图
node ~/.siada-cli/skills/archify/bin/archify.mjs render architecture dma-buf.architecture.json dma-buf-arch.html
```

4. **导出 PNG**：打开 HTML 文件，点击右上角导出菜单，选择「Download PNG」（最高 4× 分辨率），保存为 `<图表名>.png`
5. **嵌入文章**：将 PNG 图片插入 `article.md` 对应章节，替换该章节原有的 ASCII 示意图，或作为补充图表添加

### ✅ 图表生成清单

- [ ] 是否有系统/组件架构图（整体架构章节）？
- [ ] 是否有核心数据流图或调用时序图（关键流程章节）？
- [ ] 每张 archify 图表是否已导出 PNG 并嵌入文章对应位置？
- [ ] ASCII 流程图与 archify PNG 是否互补（不重复）？

---

## Step 1.5：源码合规审查 + 源码校验 & 优化润色

对 `article.md` 触发 `wx-article-code-review` skill，执行完整的五步审查：

> 说：「帮我审查 article.md，看看有没有内部代码，并对照 AOSP/Linux 源码优化润色」

**该步骤包含**：
1. 合规性扫描（无企业私有代码）
2. 通过 `aosp-linux-source` skill 在线核实关键符号（elixir.bootlin.com / cs.android.com）
3. 源码级优化润色建议：
   - 修正技术描述与上游源码不符之处
   - 补充源码注释中的关键信息
   - 为代码片段标注来源文件路径
   - 标注内核版本差异

**审查通过条件**：无 🚫 RED 项。

**优化润色**（可选）：根据审查报告中的「Step 5 优化建议」修改文章，再次确认后进入 Step 2。

---

## Step 2：feishu-wechat-cli 发布到草稿箱

在工作目录执行（含 `.env` 文件）：

```bash
# 从飞书文档直接发布（推荐）
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx" \
  --article-title "文章标题" \
  --article-author "作者名"

# 或从本地 Markdown 发布（Step 1 已抓取的 article.md，需有封面图）
feishu-wechat publish -f article.md
```

成功输出：
```
发布成功，Media ID: xxxxx
```

---

## 各 Skill 分工

| Step | Skill / 工具 | 职责 |
|------|-------------|------|
| Step 1 | `lark-doc` / `lark-wiki` | 读取飞书文档内容，输出原始 Markdown |
| Step 1.2 | Siada（本 skill 内嵌指令） | 按风格规范改写润色：补导语、补图表、优化段落节奏 |
| Step 1.3 | `archify` | 根据文章技术语言生成专业架构图/流程图/时序图/数据流图/生命周期图，输出独立 HTML + 可导出 PNG/SVG，嵌入文章 |
| Step 1.5 | `wx-article-code-review` | 合规审查 + aosp-linux-source 源码校验 + 技术准确性优化 |
| Step 1.5 | `aosp-linux-source` | 通过 elixir.bootlin.com / cs.android.com 在线核实 AOSP/Linux 源码 |
| Step 2 | `feishu-wechat-cli` | 从本地 Markdown 或飞书直接抓取，发布到微信草稿箱（自带 wenyan 排版） |

---

## 常见问题

- **invalid ip**：`curl ifconfig.me` 查出口 IP，去公众号后台安全中心加白名单
- **invalid appid or secret**：检查 `.env` 中 `WECHAT_APP_ID`/`WECHAT_APP_SECRET`
- **未能找到文章标题**：在 Markdown 文件顶部加 frontmatter（`title: 你的标题`）
- **必须指定一张封面图**：用 `--article-cover <img路径或URL>` 或在正文中插入图片，或用 `--auto-cover`（需配置 `IMAGE_API_KEY`）
- **源码核实访问超时**：elixir.bootlin.com 或 cs.android.com 网络问题，可重试或手动查询
