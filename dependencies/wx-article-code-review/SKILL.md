---
name: wx-article-code-review
description: 发布技术公众号文章前进行源码合规性审查，确保文章中引用的所有代码片段来自开源项目（AOSP、Linux mainline、LLVM、GCC 等），不包含企业私有代码、内部定制代码或保密内容。同时通过 aosp-linux-source skill 对照 AOSP/Linux 上游源码，对文章内容的技术准确性进行校验和优化润色建议。适用场景：用户说"审查文章"、"检查源码合规"、"发布前审查"、"文章里有没有内部代码"、"源码合规性检查"、"公众号文章审查"、"对照源码优化"、"源码校验"。
---

# 公众号文章源码合规性审查 & 源码校验优化

在发布技术公众号文章之前，审查文章中所有代码片段，确保不包含企业私有/保密源码，所有引用均来自开源项目；同时通过 `aosp-linux-source` skill 在线核实代码准确性，并提供源码级优化润色建议。

> ⚠️ **本技能为人工辅助审查，不自动修改文章。最终判断需结合业务上下文，Siada 提供分析意见，用户做最终决策。**

---

## 审查流程

### Step 1：读取文章内容

读取待审查的 Markdown 或 HTML 文章文件，提取其中所有代码块（` ``` ` 包裹的内容）和内联代码（`` ` `` 包裹的内容）。

### Step 2：逐个代码块审查

对每个代码块，按以下维度分析：

#### 2.1 识别代码来源

| 信号 | 判断方向 |
|------|----------|
| 包含标准 Linux 内核头文件（`linux/dma-buf.h`、`linux/mm.h` 等） | ✅ 开源 |
| 包含 AOSP 路径（`frameworks/`、`hardware/interfaces/`、`system/`） | ✅ 开源 |
| 函数/结构体名称可在 [cs.android.com](https://cs.android.com) 或 [elixir.bootlin.com](https://elixir.bootlin.com) 检索到 | ✅ 开源 |
| 包含企业特有命名前缀（如 `li_`、`lixiang_`、`ss4_`、`niro_`、公司内部项目缩写） | ⚠️ 疑似私有 |
| 包含内部路径（如 `/vendor/lixiang/`、`vendor/li-auto/`、内部 git 仓库路径） | 🚫 私有 |
| 包含内部模块名（如 `perfhub`、`sysresourcemanager`、`pvm`、`gvm` 相关私有实现） | 🚫 私有 |
| 注释中出现内部系统名称、产品代号、保密标注 | 🚫 私有 |
| 包含内部 IP 地址、域名、服务名 | 🚫 私有 |

#### 2.2 风险等级分类

| 等级 | 标志 | 含义 |
|------|------|------|
| ✅ 安全 | GREEN | 确认来自开源项目，可公开发布 |
| ⚠️ 需核查 | YELLOW | 疑似私有，需人工确认来源 |
| 🚫 禁止发布 | RED | 包含企业私有/保密内容，必须删除或替换 |

#### 2.3 源码在线核实（通过 aosp-linux-source）

对文章中涉及的**关键结构体、函数、API**，调用 `aosp-linux-source` skill 进行在线源码核实：

**核实方法**：
- **Linux 内核结构体/函数**：通过 `elixir.bootlin.com` 查询
  ```
  https://elixir.bootlin.com/linux/latest/A/ident/<符号名>
  ```
- **AOSP 框架 API**：通过 `cs.android.com` 查询
  ```
  https://cs.android.com/search?q=symbol:<符号名>&ss=android
  ```
- **Android GKI kernel**（android-specific 分支）：
  ```
  https://elixir.bootlin.com/linux/android-<version>/source/<path>
  ```

**核实重点**：
1. 结构体字段是否存在于 mainline/GKI 源码
2. 函数签名是否与上游一致
3. 注释中描述的行为是否与源码实现匹配
4. 文章中「不存在于 AOSP」的字段需标记为企业扩展或错误

### Step 3：生成审查报告

输出结构化报告，包含：

1. **总体结论**：文章是否可直接发布 / 需要修改后发布 / 不可发布
2. **逐条问题列表**：每个有风险的代码块，标注：
   - 代码片段摘要（前 2 行）
   - 风险等级
   - 疑似私有的具体原因
   - 建议处理方式（删除 / 替换为开源等价实现 / 添加来源说明）
3. **安全代码统计**：确认安全的代码块数量
4. **源码核实结果**：关键符号的 elixir/cs.android.com 验证链接

### Step 4：提供修复建议

对每个 YELLOW / RED 代码块，给出具体替换建议：

- 指出对应的开源等价代码（附 cs.android.com 或 elixir.bootlin.com 链接）
- 如果代码是伪代码/示意代码，建议显式标注「示意代码，非实际实现」
- 如果整个代码块需删除，建议用文字描述替代

### Step 5：源码级优化润色建议

基于 `aosp-linux-source` 获取的上游源码，对文章内容提出优化建议：

#### 5.1 技术准确性优化

- **字段/函数描述有误**：对照源码注释和实现，修正文章中不准确的描述
- **遗漏的重要行为**：补充源码中的关键实现细节（如 lock、RCU 保护、错误路径）
- **版本差异**：标注特定内核版本才有的行为（如 Linux 5.x vs 6.x 差异）

#### 5.2 内容深度优化

- **引用上游 commit message**：为重要特性补充 git 提交信息，增加权威性
- **补充官方注释**：将源码中有价值的注释（`/* ... */`）引用到文章中
- **补充内核文档引用**：指向 `Documentation/` 目录相关文档

#### 5.3 示例代码优化

- 将示意性代码替换为或对齐到真实的内核代码片段
- 为代码片段标注来源文件路径（如 `// include/linux/dma-buf.h:L123`）
- 补充代码中 `/* ... */` 省略部分的说明

---

## 开源参考白名单

以下来源的代码**默认视为可公开**：

| 项目 | 参考地址 |
|------|---------|
| Linux kernel mainline | https://elixir.bootlin.com/linux/latest/source |
| Android AOSP | https://cs.android.com |
| Android GKI (common kernel) | https://android.googlesource.com/kernel/common |
| LLVM/Clang | https://github.com/llvm/llvm-project |
| GCC | https://gcc.gnu.org |
| glibc | https://sourceware.org/git/glibc.git |
| Qualcomm 开源驱动 | https://git.codelinaro.org/clo/la |
| ARM Trusted Firmware | https://github.com/ARM-software/arm-trusted-firmware |

---

## 禁止出现的典型内容（参考）

- 企业内部 vendor 路径下的私有驱动实现
- 内部性能框架（perfhub、sysresourcemanager）的非开源实现
- 车型专属硬件抽象层代码
- 内部测试工具、内部 CI/CD 脚本
- 带有版权声明的企业内部代码（`Copyright © LiAuto` 等）
- 含有内部产品代号的注释（SS4、NIRO 等车型内部代号直接暴露于代码注释中）
- 不存在于 AOSP/mainline 的私有内核扩展字段（如企业定制的 `struct dma_buf` 扩展字段）

---

## 使用示例

```
用户：帮我审查 dma-buf-article.md，看看有没有内部代码，并对照源码优化
Siada：
  [Step 1] 读取文章，提取所有代码块
  [Step 2] 逐块合规审查
  [Step 2.3] 通过 elixir.bootlin.com 核实 struct dma_buf、dma_buf_export() 等符号
  [Step 3] 输出审查报告（含源码验证链接）
  [Step 4] 提供私有代码替换建议
  [Step 5] 提供源码级优化润色建议
```

审查报告示例格式：

```
## 公众号文章源码合规审查报告

**文件**：dma-buf-article.md
**总体结论**：✅ 可直接发布（共 12 个代码块，全部来自开源）

### 安全代码块（12 个）
- struct dma_buf 定义 → 来源：Linux kernel include/linux/dma-buf.h ✅
  验证：https://elixir.bootlin.com/linux/latest/A/ident/dma_buf
- dma_buf_export() 调用示例 → 来源：AOSP/kernel 标准 API ✅
- ...

### 源码核实结果
- struct dma_buf.size 字段 ✅ 存在于 mainline
- struct dma_buf.file 字段 ✅ 存在于 mainline
- (之前的) exporter_pid 字段 🚫 不存在于 AOSP mainline，已移除

### 优化润色建议
- 建议在 f_count 说明处补充：内核实际使用 atomic_long_t，操作为 atomic_long_inc/dec
- 建议补充 dma_buf_release() 完整调用链（源码路径：drivers/dma-buf/dma-buf.c）
```
