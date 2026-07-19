# 微信公众号发布工作流 Skills

[English](./README.md) | 中文

一套用于将飞书文档发布到微信公众号的 [Siada](https://siada.ai) Skills，集成专业技术图表生成和代码合规审查。

## 包含的 Skills

### 🔄 wx-publish-workflow
完整发布流程的主编排 skill：

```
飞书文档
    ↓
【风格改写润色】← 补导语、ASCII 流程图、表格
    ↓
【archify 图表生成】← 生成专业 SVG 架构图/流程图/时序图/数据流图
    ↓
【wx-article-code-review】← 代码合规审查 + AOSP/Linux 源码校验
    ↓
【feishu-wechat-cli】← 发布到微信草稿箱
```

### 📊 archify
生成独立 HTML 文件形式的专业技术图表（内嵌 SVG）：
- 支持架构图、工作流、时序图、数据流图、生命周期图五种类型
- 内置明暗主题切换
- 一键导出 PNG / SVG

包含完整的**无头截图 PNG 导出指南**（隐藏工具栏/水印、强制亮色主题、自动裁剪空白），适合嵌入文章使用。

### 🔍 wx-article-code-review
公众号技术文章发布前的代码合规性审查：
- 扫描所有代码块，确认不含企业私有/保密代码
- 通过 [elixir.bootlin.com](https://elixir.bootlin.com) 和 [cs.android.com](https://cs.android.com) 对照 AOSP/Linux 上游源码核实
- 提供源码级技术优化润色建议

### 🚀 feishu-wechat-cli
将文章发布到微信公众号草稿箱的 CLI 工具：
- 支持飞书文档 URL 或本地 Markdown 文件
- 自动获取封面图
- 集成 [wenyan-md](https://github.com/wenyan-md) 排版

### 🔎 aosp-linux-source
查询 AOSP 和 Linux 内核源码的辅助 skill：
- 在 Linux mainline 中检索符号、结构体、函数
- 核实 AOSP 框架 API

## 快速开始

### 前置条件

```bash
# 安装 feishu-wechat-cli
cd feishu-wechat-cli
pnpm install && pnpm build

# 在文章工作目录创建 .env 文件
echo "WECHAT_APP_ID=你的AppID" > .env
echo "WECHAT_APP_SECRET=你的AppSecret" >> .env
```

> 需要将服务器 IP 加入微信公众号后台 IP 白名单：  
> `curl ifconfig.me` 查出口 IP → 微信公众号后台 → 安全中心 → IP 白名单

### 发布文章

```bash
# 从本地 Markdown 文件发布
feishu-wechat publish -f article.md --auto-cover

# 从飞书文档发布
feishu-wechat publish --feishu "https://your.feishu.cn/wiki/xxxx" \
  --article-title "标题" --article-author "作者"
```

### 用 archify 生成图表

```bash
# 渲染数据流图
node ~/.siada-cli/skills/archify/bin/archify.mjs render dataflow diagram.dataflow.json output.html

# 导出为 PNG（无头截图，亮色主题，无工具栏/水印，自动裁剪）
# 步骤一：注入 CSS 隐藏 toolbar 和 footer
python3 << 'EOF'
import glob
hide_css = '<style>.toolbar{display:none!important}.footer{display:none!important}</style>'
for fname in glob.glob('*.html'):
    content = open(fname).read()
    if hide_css not in content:
        open(fname, 'w').write(content.replace('</head>', hide_css + '\n</head>', 1))
    print(f"已处理: {fname}")
EOF

# 步骤二：headless Chrome 截图（URL 加 ?theme=light 强制亮色）
for f in *.html; do
  google-chrome --headless --no-sandbox --disable-gpu \
    --screenshot="${f%.html}-light.png" --window-size=1200,3000 --hide-scrollbars \
    "file://$(pwd)/${f}?theme=light" 2>/dev/null
done

# 步骤三：PIL 自动裁剪空白（保留 20px padding）
python3 << 'EOF'
from PIL import Image, ImageChops
import glob
for fname in glob.glob('*-light.png'):
    img = Image.open(fname).convert('RGB')
    bg = Image.new('RGB', img.size, img.getpixel((0,0)))
    bbox = ImageChops.difference(img, bg).getbbox()
    if bbox:
        pad = 20
        img.crop((max(0,bbox[0]-pad), max(0,bbox[1]-pad),
                  min(img.width,bbox[2]+pad), min(img.height,bbox[3]+pad))).save(fname)
        print(f'{fname}: 裁剪完成')
EOF
```

## 依赖关系

```
wx-publish-workflow
├── lark-doc / lark-wiki      （读取飞书文档）
├── archify                   （图表生成）
├── wx-article-code-review
│   └── aosp-linux-source     （源码核实）
└── feishu-wechat-cli         （发布到微信）
```

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| `invalid ip` | `curl ifconfig.me` 查出口 IP，加入微信公众号后台 IP 白名单 |
| `invalid appid or secret` | 检查 `.env` 中的 `WECHAT_APP_ID` / `WECHAT_APP_SECRET` |
| 未找到文章标题 | 在 Markdown 文件顶部加 frontmatter：`title: 你的标题` |
| 必须指定封面图 | 用 `--auto-cover` 或 `--article-cover <图片路径>` |
| 截图是暗色背景 | URL 加 `?theme=light` 参数 |
| 截图有 Light/Export 按钮 | 截图前注入 CSS 隐藏 `.toolbar` |
| 图片底部有水印文字 | 截图前注入 CSS 隐藏 `.footer` |
| 图片底部大量空白 | 用 PIL `ImageChops.difference` 自动裁剪 |

## License

- `feishu-wechat-cli`：见 [feishu-wechat-cli/LICENSE](feishu-wechat-cli/LICENSE)
- `archify`：MIT（原作者 tt-a1i）
- 其他 skills：MIT
