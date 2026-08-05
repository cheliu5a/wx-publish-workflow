# archify 图表要求

本文件保留原 workflow 中 Step 1.3 的详细规则。主 skill 进入图表阶段后，若调用 `archify`，必须遵守本文件；如果 `archify` 不可用，则只能按主 skill 中的降级路径退回 ASCII 图和表格。

## 图表数量与密度要求

硬性要求：

- 每篇文章 `archify` 图表数量至少 3 张
- 同一篇文章中，单一图表类型不超过 2 张
- 至少覆盖 2 种不同类型
- 大章节至少每 2 个有 1 张 `archify` 图
- 图表不得集中堆在一章
- 每张图下方必须写 1 行图注，格式：`*图N：图表说明*`
- 图表中只允许使用通用技术名词，不得出现内部工具名、内部系统名、公司内部代号

## 图表类型选择

| 文章内容类型 | archify 图表类型 | 典型场景 |
|--------------|------------------|----------|
| 系统架构、模块组成、组件关系 | `architecture` | 内核子系统架构、驱动框架、SoC 结构 |
| 调用流程、数据处理管道、审批链路 | `workflow` | 系统调用链、驱动初始化流程、CI/CD |
| API 交互、请求生命周期、跨模块调用 | `sequence` | 内核/用户态交互、IPC 调用链、DMA 传输 |
| 数据流向、缓冲区传递、ETL | `dataflow` | dma-buf 共享链路、内存拷贝路径、数据总线 |
| 状态机、生命周期、状态转换 | `lifecycle` | buffer 生命周期、进程状态、设备电源状态 |

## 图表生成流程

1. 分析文章，识别最适合用专业图表表达的章节
2. 为每张图选择最合适的类型
3. 输出独立 HTML 文件，命名格式：`<文章名>-<图表描述>.<类型>.html`
4. 导出 PNG 并嵌回 `article.md`

示例：

```bash
node ~/.siada-cli/skills/archify/bin/archify.mjs render dataflow dma-buf.dataflow.json dma-buf-dataflow.html
node ~/.siada-cli/skills/archify/bin/archify.mjs render architecture dma-buf.architecture.json dma-buf-arch.html
```

## PNG 导出规则

必须严格按 `archify` 自己的 `SKILL.md` 中“导出 PNG 嵌入文章的标准操作流程”执行，不得简化或跳过。

在本 workflow 中，还必须同时读取并执行：

- [`archify-export-sop.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-export-sop.md:1)

关键要求如下：

- 截图前必须删除 `.toolbar` 和 `.footer` 对应 DOM 节点，不能仅靠 CSS 隐藏
- 截图 URL 必须加 `?theme=light`
- 必须使用高清截图参数，如 `--force-device-scale-factor=2`
- 裁剪必须采用背景色差异法，不能用固定亮度阈值偷懒

本文件不重复展开 `archify` 自身的完整脚本，只要求最终结果严格符合其导出规范。

## 时序图常见布局问题

当图表类型为 `sequence` 时，必须检查 segment 标签是否被消息箭头覆盖。

修复要求：

- 每个 segment 的 `from` 到第一条消息的 `y`，间距至少 50px
- 多条消息垂直间距至少 30px，避免文字重叠
- 调整完间距后同步增大 `viewBox` 高度，防止底部溢出

错误示例：

```json
"segments": [
  { "from": 155, "to": 310, "label": "Camera 写帧 + 创建 Fence" }
],
"messages": [
  { "from": "camera", "to": "dmabuf", "y": 185, "label": "..." }
]
```

正确示例：

```json
"segments": [
  { "from": 155, "to": 320, "label": "Camera 写帧 + 创建 Fence" }
],
"messages": [
  { "from": "camera", "to": "dmabuf", "y": 205, "label": "..." }
]
```

## 验收清单

- [ ] `archify` 图表总数是否至少为 3 张？
- [ ] 是否使用了至少 2 种类型，且同类型不超过 2 张？
- [ ] 图表是否均匀分布在文章各章节？
- [ ] 每张图是否都有 `*图N：说明*` 图注？
- [ ] 图表内容是否只含通用技术名词？
- [ ] 是否有系统架构图或组件关系图？
- [ ] 是否有核心数据流图或调用时序图？
- [ ] HTML 是否已移除 `.toolbar` 和 `.footer` DOM 节点？
- [ ] 默认英文图例是否改成符合文章语境的中文词汇？
- [ ] 截图 URL 是否使用 `?theme=light`？
- [ ] 是否已用背景色差异法裁剪空白？
- [ ] PNG 是否无按钮、无水印、无大片灰色空白？
- [ ] 每张 PNG 是否已嵌入文章对应位置？
- [ ] ASCII 图与 `archify` 图是否互补而不重复？
- [ ] 如果是系列文章，文末是否有“系列回顾”表格和公众号链接？
- [ ] 时序图标签与消息之间是否留出足够间距？
