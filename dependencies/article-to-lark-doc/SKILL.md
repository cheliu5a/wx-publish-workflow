---
name: article-to-lark-doc
description: 将本地 Markdown 文章（含嵌入图片）备份到飞书文档。创建飞书文档后逐张上传本地图片并移动到正文对应位置（替换占位符）。当用户说"把文章存到飞书""备份到飞书文档""文章归档到飞书"，或在 wx-publish-workflow 发布成功后自动触发时使用。
metadata:
  requires:
    bins: ["lark-cli"]
---

# article-to-lark-doc

将带本地图片的 Markdown 文章一键备份到飞书文档：先创建文档（Markdown 正文，图片位置用占位符标记），再逐张上传图片，最后将图片移动到正文对应位置并删除占位符。

## 前置条件

执行前必须先读取：
- [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) — 认证、`--as` 参数、全局规则
- [`../lark-doc/references/lark-doc-create.md`](../lark-doc/references/lark-doc-create.md) — `docs +create` 用法
- [`../lark-doc/references/lark-doc-media-insert.md`](../lark-doc/references/lark-doc-media-insert.md) — `docs +media-insert` 用法
- [`../lark-doc/references/lark-doc-update.md`](../lark-doc/references/lark-doc-update.md) — `docs +update` 用法（block_move_after / block_delete）

---

## 输入参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `article_path` | 是 | 本地 Markdown 文件的绝对路径（如 `/path/to/article.md`） |
| `parent_token` | 否 | 目标飞书文件夹 token；不填则创建到个人空间根目录 |
| `as_user` | 否 | 使用用户身份（`--as user`）；默认用 bot 身份 |

---

## 执行步骤

### Step 1：解析 Markdown 文件

读取 `article_path`，做以下解析：

1. **提取文章标题**：优先从 frontmatter `title:` 字段读取；没有则取正文第一个 `# 标题`。
2. **提取图片列表**：用正则 `!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp))\)` 提取所有图片引用，按出现顺序记录 `{alt, path}` 列表。路径是相对路径时，相对于 `article_path` 所在目录解析为绝对路径。
3. **预处理 Markdown 正文**：将每处 `![alt](path)` 替换为占位 blockquote，飞书文档创建后可通过 block ID 精确定位：
   ```
   > 📷 图：{alt}
   ```
   占位符作用是：创建文档时保留图片的位置锚点，后续用 `block_move_after` 把真实图片块移到占位符后方，再 `block_delete` 删掉占位符。

用 Python 完成上述解析（示例）：

```python
import re, os, sys

article_path = sys.argv[1]
base_dir = os.path.dirname(os.path.abspath(article_path))

with open(article_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 frontmatter title
title_match = re.search(r'^---\s*\ntitle:\s*(.+?)\s*\n', content, re.MULTILINE)
title = title_match.group(1) if title_match else ''

# 去掉 frontmatter
body = re.sub(r'^---\n.*?\n---\n', '', content, count=1, flags=re.DOTALL)

# 如果 frontmatter 没有 title，从正文取第一个 #
if not title:
    h1 = re.search(r'^#\s+(.+)', body, re.MULTILINE)
    title = h1.group(1).strip() if h1 else '未命名文章'

# 提取图片（保留原始路径 + alt）
images = re.findall(r'!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp))\)', body)
images = [(alt, os.path.join(base_dir, p) if not os.path.isabs(p) else p) for alt, p in images]

# 替换图片为占位文字（用于后续 block_move_after 定位）
def replace_img(m):
    alt = m.group(1)
    return f'> 📷 图：{alt}'

body_no_img = re.sub(r'!\[([^\]]*)\]\([^)]+\)', replace_img, body)

print('TITLE:', title)
print('BODY_FILE:', '/tmp/article_body.md')
with open('/tmp/article_body.md', 'w', encoding='utf-8') as f:
    f.write(body_no_img)

for alt, path in images:
    print(f'IMAGE: {path} | {alt}')
```

运行：
```bash
env -u PYTHONPATH python3 /tmp/parse_article.py <article_path>
```

### Step 2：创建飞书文档

用解析出的 `title` 和正文创建飞书文档（Markdown 格式，因为输入源本身就是 Markdown）：

```bash
# 将 title 注入 Markdown 正文顶部作为 # 标题（如果正文已有则跳过）
lark-cli docs +create --api-version v2 \
  --doc-format markdown \
  --content "$(cat /tmp/article_body.md)" \
  [--parent-token <parent_token>] \   # 可选，指定目标文件夹
  [--as user]                         # 可选，使用用户身份
```

记录返回值中的 `document_id`（格式：`doxcnXXXX`）。

> ⚠️ 如果用 `--as bot` 创建，CLI 会自动为当前用户授予可管理权限。如果未登录用户身份，在结果中 `permission_grant.status = skipped` 时提示用户先运行 `lark-cli auth login`。

### Step 3：逐张上传图片，记录 block_id

对 Step 1 提取的每张图片，**在当前工作目录下**按顺序执行（`--file` 需要相对路径）：

```bash
cd <article所在目录>
lark-cli docs +media-insert \
  --doc <document_id> \
  --file ./<image_filename> \
  --align center \
  --caption "<alt文字>"
```

- 如果某张图片文件不存在，跳过并记录警告，继续上传其余图片
- **记录每张图片上传返回的 `block_id`**，与图片顺序对应（后续 Step 4 需要）

### Step 4：将图片移到占位符位置

文档中每个 `> 📷 图：{alt}` 占位 blockquote 都有唯一 block ID。用 `docs +fetch --scope keyword --keyword "📷"` 一次性拿到所有占位符的 block ID：

```bash
lark-cli docs +fetch --api-version v2 \
  --doc <document_id> \
  --detail with-ids \
  --scope keyword --keyword "📷" 2>&1
```

从返回的 XML 中提取各 `blockquote` 的 `id` 属性，按顺序与图片列表对齐（第 N 个占位符 ↔ 第 N 张图片）。

然后对每张图片执行两步操作：

**① 移动图片到占位符后方：**
```bash
lark-cli docs +update --api-version v2 --doc <document_id> \
  --command block_move_after \
  --block-id <占位符_block_id> \
  --src-block-ids <图片_block_id>
```

**② 删除占位符（所有图片移动完成后批量删除）：**
```bash
lark-cli docs +update --api-version v2 --doc <document_id> \
  --command block_delete \
  --block-id <占位符1_id>,<占位符2_id>,...
```

> ⚠️ 先完成所有图片的移动，再统一删除占位符。若先删占位符，后续图片将失去定位锚点。

### Step 5：输出结果

完成后输出：

```
✅ 飞书文档已创建
标题：<title>
URL：https://xxx.feishu.cn/docx/<document_id>
图片：共 N 张，成功 M 张（已移至正文对应位置），跳过 K 张
```

---

## 注意事项

- **图片路径**：`--file` 只支持相对路径（相对于当前工作目录）。执行前须 `cd` 到 article 所在目录。
- **占位符顺序**：`docs +fetch --scope keyword --keyword "📷"` 返回的 blockquote 顺序与 Markdown 中图片出现顺序一致，直接按顺序对齐即可。
- **先移后删**：必须等所有图片都移动完毕，才能批量删除占位符。顺序不能颠倒。
- **文档身份**：默认用 bot 身份创建（`--as bot`），bot 创建后自动授予当前用户可管理权限。如遇权限问题，改用 `--as user`。
- **重复执行**：每次调用都会创建新文档，不会覆盖已有文档。如需更新已有文档，改用 `docs +update`。
