# WeChat Publishing Workflow Skills

English | [中文](./README.zh.md)

A collection of [Siada](https://siada.ai) skills for publishing technical articles from Feishu (Lark) to WeChat Official Account with professional diagrams and code compliance review.

## Skills Included

### 🔄 wx-publish-workflow
The main orchestration skill for the full publishing pipeline:

```
Feishu Doc
    ↓
[Style Rewrite]  ← Add intro, ASCII diagrams, tables
    ↓
[archify Diagrams]  ← Generate professional SVG diagrams
    ↓
[wx-article-code-review]  ← Code compliance + AOSP/Linux source verification
    ↓
[feishu-wechat-cli]  ← Publish to WeChat draft box
```

### 📊 archify
Generate professional technical diagrams as standalone HTML files with inline SVG:
- Architecture, Workflow, Sequence, Dataflow, Lifecycle diagram types
- Dark/light theme toggle
- One-click PNG/SVG export

Includes a complete guide for **headless PNG export** (hiding toolbar/footer, forcing light theme, auto-cropping whitespace) for embedding in articles.

### 🔍 wx-article-code-review
Pre-publish code compliance review for technical articles:
- Scan all code blocks for proprietary/confidential code
- Verify against AOSP/Linux upstream source via [elixir.bootlin.com](https://elixir.bootlin.com) and [cs.android.com](https://cs.android.com)
- Provide source-level optimization suggestions

### 🚀 feishu-wechat-cli
CLI tool to publish articles to WeChat Official Account draft box:
- Supports Feishu doc URL or local Markdown file
- Auto-fetches cover image
- Applies [wenyan-md](https://github.com/wenyan-md) typesetting

### 🔎 aosp-linux-source
Helper skill for querying AOSP and Linux kernel source code:
- Search symbols, structures, functions in Linux mainline
- Verify AOSP framework APIs

## Quick Start

### Prerequisites

```bash
# Install feishu-wechat-cli
cd feishu-wechat-cli
pnpm install && pnpm build

# Create .env in your article directory
echo "WECHAT_APP_ID=your_app_id" > .env
echo "WECHAT_APP_SECRET=your_app_secret" >> .env
```

> Add your server IP to the WeChat Official Account IP whitelist:  
> `curl ifconfig.me` → WeChat Admin → Security Center → IP Whitelist

### Publishing an Article

```bash
# From a local Markdown file
feishu-wechat publish -f article.md --auto-cover

# From a Feishu doc
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx" \
  --article-title "Title" --article-author "Author"
```

### Generating Diagrams with archify

```bash
# Render a dataflow diagram
node ~/.siada-cli/skills/archify/bin/archify.mjs render dataflow diagram.dataflow.json output.html

# Export to PNG (headless, light theme, no toolbar/footer, auto-cropped)
python3 -c "
import subprocess, glob
from PIL import Image, ImageChops

# Step 1: Hide toolbar and footer
hide_css = '<style>.toolbar{display:none!important}.footer{display:none!important}</style>'
for fname in glob.glob('*.html'):
    content = open(fname).read()
    if hide_css not in content:
        open(fname, 'w').write(content.replace('</head>', hide_css + '\n</head>', 1))

# Step 2: Screenshot with light theme
import subprocess
for f in glob.glob('*.html'):
    out = f.replace('.html', '-light.png')
    subprocess.run(['google-chrome', '--headless', '--no-sandbox', '--disable-gpu',
        f'--screenshot={out}', '--window-size=1200,3000', '--hide-scrollbars',
        f'file://\$(pwd)/{f}?theme=light'], capture_output=True)

# Step 3: Auto-crop whitespace
for fname in glob.glob('*-light.png'):
    img = Image.open(fname).convert('RGB')
    bg = Image.new('RGB', img.size, img.getpixel((0,0)))
    bbox = ImageChops.difference(img, bg).getbbox()
    if bbox:
        pad = 20
        img.crop((max(0,bbox[0]-pad), max(0,bbox[1]-pad),
                  min(img.width,bbox[2]+pad), min(img.height,bbox[3]+pad))).save(fname)
        print(f'{fname}: cropped')
"
```

## Dependency Tree

```
wx-publish-workflow
├── lark-doc / lark-wiki      (read Feishu docs)
├── archify                   (diagram generation)
├── wx-article-code-review
│   └── aosp-linux-source     (source verification)
└── feishu-wechat-cli         (publish to WeChat)
```

## License

- `feishu-wechat-cli`: See [feishu-wechat-cli/LICENSE](feishu-wechat-cli/LICENSE)
- `archify`: MIT (original by tt-a1i)
- Other skills: MIT
