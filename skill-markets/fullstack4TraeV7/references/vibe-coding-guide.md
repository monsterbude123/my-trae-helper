# Vibe Coding 指南（写给人类看的日常开发手册）

> AI Agent 体系会自动处理流程，你只需要知道"说什么"和"什么时候说"。

---

## 工具准备

```
GitNexus - AI 分析代码的工具
https:/github.com/abhigyanpatwari/GitNexus
npm install -g gitnexus

ui-ux-pro-max-skill - AI 设计端的工作
https:/github.com/nextlevelbuilder/ui-ux-pro-max-skill
```

### MCP

```json
{
  "mcpServers": {
    "Filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "d:\\workspace\\示例文件夹1",
        "D:\\workspace\\示例文件夹2"
      ],
      "env": {}
    }
  }
}
```

Context7（按需配置）

---

## 快速开始

### 第一次打开项目

跟 AI 说：

```
这是我的项目，请阅读 .trae/00-overview/README.md 和 .trae/agents/ 目录，
了解项目架构和开发规范
```

AI 会花 1-2 分钟读取项目上下文，之后所有对话都基于正确的知识。

---

## 日常开发对话模板

### 🎯 第一步：写规格（Spec-First）

```
帮我写个 [功能描述] 的 spec
```

AI 自动切换到 **fullstack-spec-writer**，会：

1. 苏格拉底式提问（5 类问题：背景、范围、用户故事、业务规则、验收标准）
2. 输出 13 章 Spec 文档（`docs/specs/{编号}-{feature}/spec.md`）
3. 等你确认 → 状态变为 approved

**你只需要**：回答问题、确认 Spec。

---

### 🎯 第二步：规划

```
帮我规划这个 [功能]
```

AI 自动切换到 **fullstack-planner**，会：

1. 阅读已 approved 的 Spec
2. 输出文档影响清单（DOC FIRST）
3. 苏格拉底式追问（补足 Spec 没覆盖的细节）
4. 列出 2-3 个方案让你选
5. 拆解成任务清单（2-5 分钟粒度）

**你只需要**：回答问题、选方案、说"确认"。

---

### 🌫️ 开发现有模块（文档可能缺失）

```
帮我改进 [现有模块] 的 [功能]
```

AI 检测到模块文档缺失时，会自动进入**迷雾消除模式**：

1. 从代码分析出接口、模型、依赖
2. 向你汇报："这个模块文档缺失，需要补全"
3. 提出推断性问题（"从代码看，它的核心职责是 X，对吗？"）
4. 你确认或纠正后，AI 以代码为依据生成模块文档
5. 文档补全后，继续正常开发

**关键**：不需要一次补全所有文档，开发哪个模块就消除哪个模块的迷雾，文档会逐步完整。

---

### 🔨 第三步：开始写代码

```
开始实现这个规划
```

AI 自动切换到 **fullstack-implementer**，会：

1. **DOC SYNC GATE** — 先同步 P0 文档（接口契约、数据模型）
2. **TDD 红绿重构** — 先写测试 → 看到失败 → 写实现 → 通过
3. 完成后更新模块文档

**你只需要**：等测试全绿，或中途说"先停下来，需求有变化"。

---

### 🔍 第四步：审查代码

```
审查一下刚才的代码
```

AI 自动切换到 **fullstack-reviewer**，会：

1. 代码质量审查（安全性、可读性、最佳实践）
2. 测试覆盖检查（>80%）
3. 文档一致性验证（接口、模型、依赖是否与文档同步）
4. 自动化验证门禁（构建、类型检查、Lint、安全扫描）
5. 输出审查报告

**你只需要**：看报告，决定修不修。

---

### 🐛 遇到 Bug

```
[错误信息] 报错了，帮我调试
```

AI 自动切换到 **fullstack-debugger**，会：

1. 收集错误信息
2. 稳定复现问题
3. 5 Whys 根因分析（输出根因证据清单）
4. TDD 修复（先写重现 bug 的测试 → 🔴 RED → 🟢 GREEN）
5. 文档同步回退到 20-development
6. 验证修复

**你只需要**：粘贴错误信息，回答 AI 的问题。

---

### 📊 生成架构文档

```
生成一下 codemap
```

AI 自动切换到 **fullstack-doc-updater**，从代码结构生成架构地图到 `docs/CODEMAPS/`。

---

## 高效 Vibe Coding 的秘诀

### 1. 一次说一件事

| ✅ 好的做法 | ❌ 不好的做法 |
|------------|------------|
| "帮我规划模型批量下载功能" | "帮我规划模型下载，然后实现，然后审查" |
| "开始实现这个规划" | "写代码"（没上下文） |
| "审查刚才的代码" | "看看有没有问题"（太模糊） |

AI 一次只做一个角色的事，把流程走完再进入下一步。

### 2. Spec 阶段多聊，编码阶段少聊

- **Spec 阶段**：多回答 fullstack-spec-writer 的问题，目标、范围、验收标准都要说清
- **规划阶段**：多回答 fullstack-planner 的问题，多问"为什么这样做"，方案对比时认真选
- **编码阶段**：让 AI 自己跑 TDD，不用每一步都问。它会在关键决策点停下来问你

### 3. 需求变更时立即说

```
等等，需求有变化：[新的需求描述]
```

AI 会回到 fullstack-spec-writer 阶段，更新 Spec，重新评估文档影响面，不会在旧方案上继续写代码。

### 4. 不满意就说

```
这个方案太重了，有没有更轻量的做法？
```

```
我不喜欢方案 A，方案 B 和 C 能再详细说说吗？
```

AI 会重新出方案。fullstack-planner 的铁律是"无确认不编码"，你有绝对的决定权。

### 5. 善用"完成"触发文档更新

```
完成了
```

fullstack-implementer 会自动检测变更范围：
- 大迭代（>5 文件）→ 自动更新所有受影响文档
- 小迭代（≤5 文件）→ 问你是否更新

---

## 项目目录速查

| 位置 | 用途 | 何时关心 |
|------|------|---------|
| `docs/specs/{编号}-{feature}/` | Spec 文档 | 写需求时 |
| `src/app/` | Next.js 页面和 API 路由 | 开发功能时 |
| `src/lib/` | 业务逻辑 | 开发核心逻辑时 |
| `src/components/` | React 组件 | 开发 UI 时 |
| `docs/modules/` | 模块文档 | AI 会自动同步，你不需要手动维护 |
| `docs/CODEMAPS/` | 架构地图 | 需要全局视图时说"生成 codemap" |
| `docs/ARCHITECTURE.md` | 架构总览 | 大迭代后由 fullstack-doc-updater 更新 |
| `docs/DECISIONS.md` | ADR 架构决策 | 架构调整时记录 |
| `scripts/debug/` | 联调脚本 | 对接新外部 API 时 AI 会自动创建 |
| `.trae/agents/` | Agent 定义 | 想调整 AI 行为时修改 |

---

## 完整流程示例

### 场景 1：完整新功能

```
你: 帮我写个 [功能] 的 spec
AI: [fullstack-spec-writer 苏格拉底提问 → 输出 13 章 Spec]
你: 确认 spec
AI: [Spec 状态变为 approved]

你: 帮我规划这个 [功能]
AI: [fullstack-planner 输出文档影响清单 + 模块文档草稿 + 方案对比]
你: 确认方案 B
AI: [fullstack-planner 输出实施计划]

你: 开始实现这个规划
AI: [fullstack-implementer DOC SYNC → TDD 编码 → 文档更新]
你: 审查一下
AI: [fullstack-reviewer 代码审查 + 验证门禁 + 文档一致性]
你: ✅ 完成
```

### 场景 2：紧急 Bug

```
你: [报错信息]，帮我调试
AI: [fullstack-debugger 根因分析 → 🔴RED → 🟢GREEN → 文档同步]
你: 审查一下
AI: [fullstack-reviewer 阶段 0 根因验证 → 常规审查]
```

### 场景 3：需求变更

```
你: 需求变了，[新需求]
AI: [fullstack-spec-writer 更新 Spec → fullstack-planner 重新评估影响 → 新方案]
你: 确认
AI: [fullstack-implementer 更新文档 → 修改代码]
```

### 场景 4：只想改一个小东西

```
你: 把 [某接口] 的返回值加个 [字段]
AI: [小变更流程：更新模块文档 → 改代码 → 验证]
（不会走完整 Spec 流程，直接轻量执行）
```

---

## 什么时候需要你介入

| 时机 | 你需要做什么 |
|------|------------|
| AI 输出 Spec 后 | 确认 Spec（approved） |
| AI 输出方案后 | 选方案、确认 |
| AI 发现文档与代码不一致 | 决定以哪个为准 |
| 测试覆盖率不够 | 决定是否补充测试 |
| 需求变更 | 立即告诉 AI |

## 什么时候不需要介入

| 时机 | AI 自己会做 |
|------|------------|
| DOC SYNC | 编码前自动执行 |
| TDD 红绿重构 | 自动循环 |
| 构建和类型检查 | 自动验证 |
| 变更范围检测 | 自动运行 |
| 文档同步 | 编码前自动执行 |

---

## Agent 速查

| 说这些词 | AI 变成 | 它会做什么 |
|---------|--------|----------|
| "写 spec"、"定义规格" | fullstack-spec-writer | 13 章 Spec、需求澄清 |
| "规划"、"设计"、"架构" | fullstack-planner | 需求澄清、方案对比、文档影响清单、ADR |
| "实现"、"开发"、"TDD" | fullstack-implementer | DOC SYNC、TDD 红绿重构、文档更新 |
| "审查"、"验证"、"提交前" | fullstack-reviewer | 代码审查、文档一致性验证、构建验证 |
| "调试"、"bug"、"报错" | fullstack-debugger | 根因分析、TDD 修复 |
| "生成文档"、"架构图" | fullstack-doc-updater | Codemap、全局架构文档 |

---

## 调整 AI 行为

### 想增加规则？

编辑 `.trae/00-overview/README.md` 的"DOC FIRST 三条铁律"章节，加入你的项目特有约束。

### 想调整某个 Agent 的行为？

编辑 `.trae/agents/` 下对应的文件，修改流程或检查清单。

### 想增加新的工作流？

1. 在对应阶段目录（如 `20-development/`）创建新文档
2. 在对应的 agent 文件中引用
3. 在 `.trae/00-overview/README.md` 的目录结构中登记

---

## 项目启动命令

```bash
npm run dev              # 启动开发服务器
npm test                 # 跑测试
npx vitest --project=core        # 核心测试（3-5 秒）
npx vitest --project=integration # 集成测试（10-15 秒）
npm run build            # 生产构建
```
