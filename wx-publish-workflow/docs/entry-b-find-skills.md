# 入口 B：find-skills 发现并整理 Skills 推荐文

本文件保留原 workflow 中“先发现 Skills，再整理成公众号文章”的完整要求。只有当用户明确要做 Skills 推荐文时才进入这一入口。

## Step 0.1：发现候选 Skills

优先方式：浏览 `skills.sh` leaderboard。

目的：先找到安装量高、来源可靠、用户实际在用的 Skills，缩短搜索路径。

可选方式：关键词搜索。

```bash
npx skills find [关键词]

# 示例
npx skills find react performance
npx skills find code review
npx skills find deployment
npx skills find documentation
npx skills find testing
npx skills find workflow automation
```

补充方式：浏览知名来源。

- `vercel-labs/agent-skills`
- `anthropics/skills`
- `ComposioHQ/awesome-claude-skills`

## Step 0.2：质量筛选

收集候选后，必须逐项检查以下三个维度：

| 维度 | 筛选标准 | 备注 |
|------|----------|------|
| 安装量 | 优先 1K+ 安装，慎选 100 以下 | 安装量反映真实采用度 |
| 来源声誉 | 官方来源或长期维护者优先 | 未知作者需额外验证 |
| 描述相关度 | 描述是否清楚说明触发场景 | 描述模糊的 Skill 往往质量不稳定 |

筛选目标：

- 准备 5 到 10 个有代表性的 Skills
- 覆盖至少 2 个类别，建议 2 到 3 个类别
- 保留多样性，不要全是同一方向

## Step 0.3：为每个 Skill 生成介绍卡片

每个 Skill 统一按以下结构整理：

````markdown
### 🔧 [Skill 名称]

**一句话介绍**：[一句话说清这个 Skill 解决什么问题]

**适用场景**：
- [场景 1]
- [场景 2]
- [场景 3]

**核心能力**：[2~3 条核心功能点]

**安装方式**：
```bash
npx skills add [owner/repo@skill-name]
```

**了解更多**：https://skills.sh/[owner]/[repo]/[skill-name]
````

硬性要求：

- 描述必须站在用户视角，说清“我什么时候用它”
- 安装命令必须准确，直接从搜索结果或 `skills.sh` 页面复制
- 不得凭空编造安装命令、作者名或来源页

## Step 0.4：组织整篇文章结构

将所有 Skill 卡片组织成文章草稿，建议结构：

````markdown
# [文章标题]

[导语：100~200 字，用问题钩子或场景引出 Skills 的价值]

## 一、[类别名称]

[类别简介]

[Skill 卡片 1]
[Skill 卡片 2]

## 二、[类别名称]

[类别简介]

[Skill 卡片 3]
[Skill 卡片 4]

## 三、[类别名称]

...

## 总结

[50~100 字总结，强调 Skills 的核心价值]

> 你用过哪些让你效率倍增的 Skills？欢迎留言分享。
````

将草稿保存为 `article.md`，然后进入正文改写主线。

## 完成清单

- [ ] 是否通过 `skills.sh` leaderboard 或 `npx skills find` 收集候选？
- [ ] 是否检查了安装量、来源声誉、描述相关度？
- [ ] 入选数量是否在 5 到 10 个之间，且覆盖至少 2 个类别？
- [ ] 每个 Skill 是否整理了名称、场景、核心能力、安装命令？
- [ ] 安装命令是否来自真实页面，而不是手写猜测？
- [ ] 是否已保存为 `article.md` 并准备进入正文改写？
