# Bug 诊断方法论 + 反例库

> 调用方：`agents/debugger.md` §Bug 诊断方法论 / §反例库
> 用途：debugger 在根因分析阶段（Step 4）必须参照的方法论与反例警示。
> 原则：复用而非自研、验证而非信任、根因证据先行。

---

## §1. 方法论

### 1.1 全链路 6 层逐层排查

用户报告"数据丢失/不显示"类 Bug 时，从 DB → 组件渲染逐层验证，任一 Layer 未验证不可声称"已排查完毕"。

```
Layer 1 DB → Layer 2 API → Layer 3 推送层(SSE/WebSocket)
Layer 4 前端 Hook(parse/sanitize) → Layer 5 Store(upsert/merge) → Layer 6 组件渲染
```

每层验证: 数据是否存在 → 字段是否映射正确 → 是否被覆盖/过滤 → 是否渲染。任一层断链即根因所在。

### 1.2 采集 vs 解析二分判定法

修改 parser/crawler 前必须先拿 `raw_payload` 判定:

```
字段存在 + 非空 → 解析问题（改 parser）
字段不存在/为空 → 采集缺失（改 crawler）
```

禁止跨层修复（采集缺失却改 parser / 解析问题却改 crawler）。

### 1.3 e2e 先行

修 bug 前必须写 e2e 验收脚本，**e2e 初始必须 FAIL**（证明 bug 真实存在）。
e2e 一跑就 PASS = 没理解 bug 或 bug 已不存在 → 不可进修复阶段。
与 TDD RED 关系: bug 修复用 e2e 先行（高维复现），功能开发用单测 TDD RED（细粒度验证）。

### 1.4 先验后做的昂贵操作保护

```
✅ 正确: 检查前置条件 → 条件满足 → 执行操作
❌ 错误: 执行昂贵操作 → 检查前置条件 → 失败回滚（带宽+I/O+时间全浪费）
```

保护检查点: 文件下载前查 DB 复用 / DB INSERT 前查唯一约束 / 网络请求前查 URL 白名单 / 大文件读取前查大小。
DB 回查幂等性: 文件存在 + 有 DB 记录 → 复用；文件存在无 DB 记录 → 脏状态，删旧重做。

### 1.5 并行诊断委派

用户报告多个独立问题 → 并行委派 `search` 子代理调研，主上下文聚焦主要修复。

```
问题 A 和 B 有关联（同一根因）→ 串行排查，修复根因即可
问题 A 和 B 独立（不同模块/层级）→ 并行委派
  ├── 主上下文/implementer: 修复问题 A（编码类，需 Write/RunCommand）
  └── search 子代理: 调研问题 B（只读，不修改代码）
```

search 子代理注入: 调研范围明确 + 返回格式要求 + [DOC_WHITELIST] 防读无关层 + 禁止任何代码修改。

### 1.6 GitNexus First

修改符号前必须 `impact()`，提交前必须 `detect_changes()`。禁止降级为 grep/glob 分析代码结构。
失败时执行 3 次重试协议（修参数 → 换工具 → list_repos），仍失败 → 停下汇报用户。

---

## §2. 反例库

> 反例价值 > 正例价值。每条 4 行结构: 现象 / 根因 / 教训 / 来源。

### 反例 1: 全链路盲区（仅看后端，漏前端渲染层）

```
现象: 用户报告"任务日志信息丢失"，只排查 DB/API/SSE 三层均正确
根因: Layer 1-5 全部正确，仅 Layer 6 组件未渲染 errorMessage 字段
教训: 必须逐层验证到 Layer 6，不能漏掉前端渲染层
```

### 反例 2: 跨层修复（采集缺失却改 parser）

```
现象: 字段在 raw_payload 中不存在，agent 直接改 parser 加默认值
根因: 实际是 crawler 未采集该字段，parser 加默认值掩盖了采集缺陷
教训: 拿 raw_payload 二分判定（采集 vs 解析），禁止跨层修复
```

### 反例 3: 堆栈推测不复现

```
现象: agent 看堆栈直接定位到某函数，改代码后声称修复，实际 bug 仍在
根因: 未实际复现，堆栈只是表象，真实根因在上游调用方
教训: 必须用浏览器工具实际复现 + 截图，禁止仅凭堆栈推测
```

---

## 关联

- 调用方：`agents/debugger.md` Step 4 根因分析
- 关联铁律：debugger §铁律 1-7（NO FIX WITHOUT ROOT CAUSE / GitNexus First）
- 兄弟文档：[bug-workflow.md](bug-workflow.md)（Bug 编号与目录结构）
