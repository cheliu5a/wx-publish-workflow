# 功能覆盖映射

本文件用于核对：拆分后的 `wx-publish-workflow` 是否保留了拆分前的所有核心功能和硬性要求。

原则：主 `SKILL.md` 负责入口判断、步骤编排、降级和交付级别；具体规则下沉到支持文档。只要映射存在且要求未弱化，就视为功能保留。

## Frontmatter 与触发范围

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 处理“发公众号 / 飞书文档发公众号 / 发布文章 / 公众号发布流程”类请求 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:1) | frontmatter 和“何时使用”保留触发范围 |
| 支持“已有文章”与“先发现 Skills 再发文”两种入口 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:83) | 主文件保留入口判断和总流程 |

## 入口 B：find-skills 发现与整理

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 浏览 `skills.sh` leaderboard | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:5) | 保留 |
| 使用 `npx skills find` 按关键词搜索 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:11) | 保留示例命令 |
| 关注知名来源 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:23) | 保留来源列表 |
| 按安装量 / 来源声誉 / 描述相关度三维筛选 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:29) | 保留 |
| 目标数量 5 到 10 个，覆盖 2 到 3 类 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:37) | 保留 |
| Skill 卡片结构：名称、介绍、场景、核心能力、安装方式、更多链接 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:43) | 保留 |
| 安装命令必须来自真实页面 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:61) | 保留 |
| 组织成分类文章草稿并保存为 `article.md` | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:65) | 保留 |
| Step 0 完成清单 | [`entry-b-find-skills.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/entry-b-find-skills.md:91) | 保留 |

## 前置条件与正文读取

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| `.env` 中配置 `WECHAT_APP_ID` / `WECHAT_APP_SECRET` | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:107) | 保留 |
| IP 加白名单与 `curl ifconfig.me` | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:114) | 保留 |
| 用 `lark-cli docs +fetch` 拉取飞书文档为 `article.md` | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:133) | 保留命令 |

## Step 1.2：公众号风格改写

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 故事钩子 + 金字塔骨架 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:5) | 保留 |
| 故事钩子位置与写法 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:9) | 保留 |
| 技术文章四段式钩子 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:15) | 保留 |
| 前 200 字说明方法 / 问题 / 收获 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:23) | 保留 |
| 结论先行 -> 分组展开 -> 证据落地 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:31) | 保留 |
| 每章首段先给结论、每章至少一个加粗重点句 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:35) | 保留 |
| 结尾回收全文方法链 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:39) | 保留 |
| 表格 >= 3，ASCII 图 >= 2 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:71) | 保留 |
| 段落不超过 5 句 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:78) | 保留 |
| 改写操作清单 | [`style-guide.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/style-guide.md:89) | 保留 |

## Step 1.3：archify 图表生成

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 每篇 `archify` 图 >= 3 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:7) | 保留 |
| 至少 2 种图表类型，同类型不超过 2 张 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:8) | 保留 |
| 图表均匀分布 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:10) | 保留 |
| 图注 `*图N：说明*` | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:11) | 保留 |
| 只允许通用技术名词 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:12) | 保留 |
| architecture / workflow / sequence / dataflow / lifecycle 选择规则 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:16) | 保留 |
| 输出独立 HTML 文件命名规则 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:26) | 保留 |
| `archify` render 示例命令 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:33) | 保留 |
| PNG 导出必须遵守完整 SOP | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:40) | 保留 |
| toolbar/footer 删除、light theme、Retina、背景色差异裁剪 | [`archify-export-sop.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-export-sop.md:1) | 详细恢复 |
| sequence 标签与消息间距规则 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:51) | 保留 |
| 系列文章互链检查 | [`archify-requirements.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/archify-requirements.md:92) | 保留 |

## Step 1.5：审查与源码核实

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 触发 `wx-article-code-review` | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:5) | 保留 |
| 推荐触发语 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:7) | 保留 |
| 合规性扫描 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:13) | 保留 |
| 通过公开源码站点核实关键符号 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:14) | 保留 |
| 修正技术描述、补源码注释、标路径、标版本差异 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:15) | 保留 |
| 审查通过条件：无 `RED` 项 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:21) | 保留 |

## Step 1.9：封面生成

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 从标题 / 钩子 / 导语 / 总结提炼封面信息 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:31) | 保留 |
| 提炼核心冲突 / 对象动作 / 视觉关系 / 文案 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:38) | 保留 |
| `guizang-social-card-skill` 生成主封面和方形封面 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:45) | 保留 |
| 主封面 `2.35:1`，方形 `1:1` | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:47) | 保留 |
| `cover-<slug>.html` + headless Chrome 截图 + `file` 校验 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:58) | 保留 |
| 封面兜底为正文相关图片 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:78) | 保留 |
| 封面验收清单 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:82) | 保留 |

## Step 2：发布到微信草稿箱

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 从飞书文档直接发布 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:196) | 保留命令 |
| 从本地 Markdown 发布并带封面 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:201) | 保留命令 |
| 成功输出 `Media ID` | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:204) | 保留 |
| 失败排查：AppID/Secret、IP、标题、封面路径 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:206) | 保留 |

## Step 3：归档到飞书文档

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 调用 `article-to-lark-doc` 归档 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:213) | 保留 |
| 保留正文版本、图片引用关系、输出文档链接 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:217) | 保留 |
| 失败时保留本地文件并说明归档未完成 | [`SKILL.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/SKILL.md:221) | 保留 |

## Step 4：发布后三问

| 原能力 | 现在位置 | 说明 |
|--------|----------|------|
| 发布成功后提出 3 道理解题 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:90) | 保留 |
| 题型覆盖概念 / 原理 / 应用 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:95) | 保留 |
| 固定格式输出 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:101) | 保留 |
| 用户回答后简洁点评 | [`review-cover-postpublish.md`](/home/lixiang/.siada-cli/skills/content/wx-publish-workflow/docs/review-cover-postpublish.md:115) | 保留 |

## 结论

拆分后的版本保留了原 workflow 的入口、步骤、硬性门槛、命令示例、验收清单和降级策略。变化仅在于：

- 主 `SKILL.md` 不再承载所有细节，而是负责总控与路由
- 细节规则按主题拆分到支持文档
- `archify` 的长脚本从主文件迁移到单独 SOP 文档，避免总控文档膨胀，同时保留原始执行要求
