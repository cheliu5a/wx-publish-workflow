---
name: feishu-wechat-cli
version: 0.1.0
description: "把飞书文档或本地 Markdown 发布到微信公众号草稿箱。当用户提到「发布到公众号」「飞书文档转公众号」「生成公众号排版」「feishu-wechat」「wenyan 排版」时使用。飞书侧通过 lark-cli（siada-cli 默认飞书机器人）抓取文档与图片，无需新建飞书应用；仅需微信公众号凭证。"
---

# feishu-wechat-cli

把飞书 `wiki/docx` 文档或本地 Markdown 渲染为公众号排版并发布到微信公众号草稿箱。

## 飞书机器人说明（重要）

本工具**不创建新的飞书机器人**。飞书文档抓取与图片下载全部通过 `lark-cli` 完成，使用 siada-cli 已配置的默认飞书应用（`lark-cli config show` 中的 appId）。无需额外飞书 App ID/Secret。

- 抓取命令：`lark-cli docs +fetch`、`lark-cli docs +media-download`（见 `src/pipeline/feishu.ts`）。
- 若要抓取的是**你个人的** wiki/docx（bot 身份看不到用户私人文档），需在同一应用下授权用户身份：`lark-cli auth login`（按 scope 授权，增量累积）。这不是新建机器人，只是给默认应用开通用户身份。

## 可执行文件

安装后可直接调用：

```bash
feishu-wechat --version   # 0.1.0
feishu-wechat --help
```

`feishu-wechat` 是 skill 内 wrapper（`~/.siada-cli/skills/feishu-wechat-cli/scripts/feishu-wechat`），通过 `~/.local/bin` 进 PATH。wrapper 会自动选用支持 `require(esm)` 的 Node（优先 `~/.nvm` 默认版本），因依赖树需要 Node ≥ 20.17 / ≥ 22.12。

## 环境变量（在当前工作目录建 `.env`）

工具从 `process.cwd()` 读取 `.env`（见 `src/config.ts`）。发布到公众号前，在工作目录准备：

```bash
cat > .env <<'EOF'
WECHAT_APP_ID=你的公众号AppID
WECHAT_APP_SECRET=你的公众号AppSecret
# 可选：自动生成封面用（--auto-cover）
IMAGE_API_KEY=你的图片模型Key
IMAGE_BASE_URL=https://api.laozhang.ai
EOF
```

- 微信发布必需：`WECHAT_APP_ID`、`WECHAT_APP_SECRET`。
- 自动封面可选：`IMAGE_API_KEY`、`IMAGE_BASE_URL`（默认 `https://api.laozhang.ai`，生图服务可能 429 限流）。
- **IP 白名单**：必须把当前机器出口 IP 加入微信公众号后台白名单，否则微信接口拒绝请求（报 `invalid ip`）。

## 命令

### publish — 发布到公众号草稿箱

```bash
# 从飞书文档发布
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx"

# 从飞书发布并自动生成封面
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx" --auto-cover

# 从飞书发布，指定作者/标题
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx" \
  --article-title "标题" --article-author "作者"

# 发布本地 Markdown
feishu-wechat publish -f ./article.md
```

从飞书抓取时，正文与下载的图片会写入 `./.tmp/feishu-assets/<docToken>/`（当前工作目录），并生成 `article.md`。

### render — 仅渲染排版 HTML（不发布，无需微信凭证）

```bash
feishu-wechat render -f ./article.md          # 输出到 stdout
feishu-wechat render -f ./article.md -t orangeheart   # 指定主题
```

### theme — 主题管理

```bash
feishu-wechat theme -l                       # 列出内置+自定义主题
feishu-wechat theme --add --name mine --path ./my.css
feishu-wechat theme --rm mine
```

### serve — 启动 HTTP API 服务

```bash
feishu-wechat serve -p 3000 --api-key SECRET # /health /verify /publish /upload
```

## 通用选项（publish / render）

| 选项 | 说明 | 默认 |
|------|------|------|
| `[input-content]` | 直接传入 markdown 文本 | - |
| `-f, --file <path>` | 从本地文件或网络 URL 读取 | - |
| `-t, --theme <id>` | 排版主题 | default |
| `-h, --highlight <id>` | 代码高亮主题 | solarized-light |
| `-c, --custom-theme <path>` | 自定义主题 CSS | - |
| `--mac-style` / `--no-mac-style` | 代码块 Mac 风格 | 启用 |
| `--footnote` / `--no-footnote` | 链接转脚注 | 启用 |

publish 专属：`--feishu <urlOrToken>`、`--article-title`、`--article-author`、`--article-cover`、`--auto-cover`、`--article-source-url`、`--server <url>`（走远程 server 模式）、`--api-key`。

## Frontmatter 要求

Markdown 顶部可含 frontmatter（从飞书发布时会自动注入）：

```
---
title: 文章标题
cover: ./cover.jpg
author: 作者
source_url: https://example.com
---
```

未指定 `cover` 时用正文第一张图作封面；`cover` 支持本地路径或网络 URL。

## 自动封面

`--auto-cover` 时，wrapper 会自动把 skill 内的 `scripts/generate-cover.py` 复制到当前目录 `./scripts/`（工具按 `process.cwd()` 解析该脚本路径），再调用生图服务生成 900×383 封面。需 `IMAGE_API_KEY`。

## 常见问题

- **invalid ip**：当前机器 IP 未加入公众号白名单 → 去公众号后台加白名单。
- **invalid appid or secret**：`.env` 里 `WECHAT_APP_ID`/`WECHAT_APP_SECRET` 缺失或错误。
- **抓取飞书文档失败**：确认 `lark-cli` 已配置（`lark-cli config show`）；个人文档需 `lark-cli auth login` 授权用户身份。
- **生图 429**：外部生图服务限流，稍后重试或换 `IMAGE_BASE_URL`。

## 构建与依赖

- 源码与依赖位于 skill 目录 `~/.siada-cli/skills/feishu-wechat-cli/`（pnpm 安装 + `tsc` 构建，产物 `dist/`）。
- 依赖 `@wenyan-md/core`（排版核心）、`lark-cli`（飞书抓取，外部已装）、Python3 + Pillow（封面裁剪，自动封面用）。
- 更新上游源码后需重新 `pnpm install && pnpm build`。
