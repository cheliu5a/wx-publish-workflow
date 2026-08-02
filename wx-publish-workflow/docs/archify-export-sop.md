# archify 导出 PNG 嵌入文章的标准操作流程

本文件恢复原 workflow 中 `archify` 导出 PNG 的详细脚本与命令。只要进入 `archify` 图表导出阶段，就必须按本文件执行，不得简化。

## 步骤 1：删除 toolbar 和 footer DOM 节点

⚠️ 不能用 CSS `display:none` 隐藏。`archify` 的 JS 会在 `DOMContentLoaded` 后重新显示 `.toolbar`，导致截图仍带出工具栏和页脚。

唯一可靠方式：直接从 HTML 中删除 toolbar 的整个 `<div>` 和 footer 的 `<p>` 节点。

```python
import re

def remove_toolbar_footer(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 删除 <div class="toolbar">...</div>（按 div 深度计数匹配闭合标签）
    start_marker = '<div class="toolbar"'
    start_idx = content.find(start_marker)
    if start_idx >= 0:
        depth = 0
        i = start_idx
        while i < len(content):
            if content[i:i+4] == '<div':
                depth += 1
                i += 4
            elif content[i:i+6] == '</div>':
                depth -= 1
                i += 6
                if depth == 0:
                    content = content[:start_idx] + content[i:]
                    break
            else:
                i += 1

    # 删除 <p class="footer">...</p>
    content = re.sub(r'<p class="footer">.*?</p>', '', content, flags=re.DOTALL)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 对所有待截图的 HTML 文件调用此函数
```

## 步骤 2：用 headless Chrome 截图

硬性要求：

- URL 必须加 `?theme=light`
- 必须使用 `--force-device-scale-factor=2`
- 窗口高度使用 `3000`，避免内容被截断

```bash
google-chrome --headless --no-sandbox --disable-gpu \
  --screenshot="${f}-light.png" --window-size=1200,3000 --hide-scrollbars \
  --force-device-scale-factor=2 \
  "file://$(pwd)/${f}.html?theme=light" 2>/dev/null
```

说明：

- `?theme=light` 确保输出白色背景
- `--force-device-scale-factor=2` 生成 2x Retina 级别截图
- `1200 x 3000` 是稳定的默认窗口尺寸，适合大多数图表页面

## 步骤 3：用 PIL + numpy 做背景色差异裁剪

⚠️ 必须用背景色差异法，不能用固定亮度阈值如 `<235`。`archify` 的 light 主题背景色是 `(248,250,252)`，不是纯白；如果偷懒用固定阈值，会留下四周大片灰色空白。

正确做法：采样四角颜色作为背景色基准，用容差做差异裁剪，并保留 `30px` padding。

```python
from PIL import Image
import numpy as np

def smart_crop(image_path, output_path=None, tolerance=8, padding=30):
    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img)

    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]
    h, w = rgb.shape[:2]

    corners = np.array([
        rgb[0, 0],
        rgb[0, w - 1],
        rgb[h - 1, 0],
        rgb[h - 1, w - 1],
    ])
    bg_color = np.median(corners, axis=0)

    diff = np.abs(rgb.astype(np.int16) - bg_color.astype(np.int16)).max(axis=2)
    mask = (diff > tolerance) & (alpha > 0)

    coords = np.argwhere(mask)
    if coords.size == 0:
        cropped = img
    else:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        x0 = max(0, x0 - padding)
        y0 = max(0, y0 - padding)
        x1 = min(w, x1 + padding)
        y1 = min(h, y1 + padding)
        cropped = img.crop((x0, y0, x1, y1))

    if output_path is None:
        output_path = image_path
    cropped.save(output_path)
    return output_path
```

## 推荐执行顺序

1. 生成 `.html`
2. 对每个 `.html` 执行 `remove_toolbar_footer`
3. 用 headless Chrome 生成 `-light.png`
4. 对 `-light.png` 执行 `smart_crop`
5. 检查输出图是否白底、无按钮、无页脚、无灰边
6. 将裁剪后的 PNG 嵌入 `article.md`

## 最终验收

- [ ] HTML 中已删除 `.toolbar` 和 `.footer` 的 DOM 节点
- [ ] 截图 URL 已加 `?theme=light`
- [ ] 已使用 `--force-device-scale-factor=2`
- [ ] 已采用背景色差异法裁剪而不是固定亮度阈值
- [ ] 输出 PNG 白底、清晰、无按钮、无页脚、无大片灰边
- [ ] PNG 已嵌回正文对应章节
