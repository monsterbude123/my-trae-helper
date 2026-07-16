# 委派注入模板（Delegation Injection Template）

> V9.2 NEW → V9.5 重构：抽取通用基底，减少重复注入，控制委派 prompt 体积。
>
> **原则**：agent 自己的 SKILL.md 定义"agent 应该做什么"（自我约束）。本模板定义"主上下文必须在委派时告诉 agent 做什么"（注入约束）。

---

## §0 使用方式（V9.5 精简版）

> 与 [context-economy.md](context-economy.md) §2 联动。

```
委派 any agent:
  1. 确定 subagent_type: general_purpose_task（仅 intake 用 search）
  2. 写入任务描述（≤200 字符，增量部分）
  3. 引用: "注入: §A 通用基底 + §{agent} 特化模板 → delegation-injection-template.md"
  4. ⚠️ 不内联模板全文到 prompt — agent 自行读取本文件

主上下文不注入 → 🛑 委派无效。
注入但 prompt > 1KB → 🛑 压缩后再委派（见 context-economy.md §2）。
```

### subagent_type 强制规则

```
coding agent → general_purpose_task:
  implementer, contract-writer, spec-writer, planner,
  doc-updater, proposal-writer, prototype-writer, reviewer

仅 intake → search（纯信息搜索）

错误 subagent_type → 结构性失败 → 主上下文路由错误，立即重委派
```

---

## §A 通用注入基底（所有 agent 共享）

> 以下 5 条对所有 agent 生效，不再在每个 agent 模板中重复。

```
[MUST] 🚫 绝对禁止操作文档索引文件 — 通过 `doc-map-manager` 技能查询/更新
[MUST] 涉及文档查询时加载 doc-map-manager 技能（query-index.py --grab/--lookup/--file）
[MUST] DELTA ONLY: 只写此变更的增量。项目级通用内容引用 docs/ 路径，禁止复制全文
[MUST] 产出 Completion Report ≤ 800 字符（见 completion-report-protocol.md §二·0）
[MUST] 禁止硬编码端口/地址/密钥 — 从环境变量读取
[MUST] SELECTIVE READING: 读工件前查 minimum-knowledge.md §2（你自己的行）→ MUST READ 段先读 → ON DEMAND 段按需 Grep → DON'T READ 段跳过
```

---

## implementer 特化注入

```
[MUST] 编码前: GitNexus impact(target=..., direction="upstream")，汇报风险等级
[MUST] 编码后: detect_changes()，确认变更范围符合预期
[MUST] 前端代码: 每个组件/页面对应 __tests__ 目录，文件非空
[MUST] Rust 集成测试: contract test skeleton → tests/ 独立文件，非空
```

---

## reviewer 特化注入

```
[MUST] 合规性回溯验证:
  ├── __tests__/ 目录: 每个前端源文件有对应测试（文件存在 + 非空）
  ├── tests/ 集成测试: contract test 独立文件非空
  ├── 硬编码端口: grep "localhost:\d+" / "127.0.0.1:\d+"
  └── 任一缺失 → FAIL（无 N/A 或"非阻塞"）
[MUST] Visual Gate（V9.5 NEW）: 审查时对涉及 UI 的变更执行视觉验收（见 visual-acceptance.md）→ 与 prototype 比对 → 截图归档
```

---

## doc-updater 特化注入

```
[MUST] 文档索引通过 doc-map-manager 技能更新（禁止裸 python build-index.py）
[MUST] 索引更新后通过 doc-map-manager 技能验证
```

---

## spec-writer 特化注入

```
[MUST] 涉及 UI → 委派 prototype-writer 产出 prototypes/（不自行画原型）
[MUST] 不涉及 UI → Out of Scope 声明 "无 UI，跳过原型"
[MUST] 编写前: doc-map-manager --grab "{能力名}" 确认无重复，有则标注复用引用
[MUST] 输出前判定拆分模式: 单文件 or 父文件+子文件 → progressive-disclosure.md §2 spec.md
```

---

## prototype-writer 特化注入

```
[MUST] 4 条铁律: UI MUST HAVE PROTOTYPE / REAL TEXT / ALL STATES / MODULAR
[MUST] 每个文件 5 段: 线框图 + 交互 + 样式 + 状态变化 + 移交清单
[MUST] 每页面 4 状态 ASCII 图: 默认/加载中/空数据/错误
```

---

## contract-writer 特化注入

```
[MUST] contracts/ 四件套齐全: domain-models + api-contracts + events + validation
[MUST] api-contracts.md 含 contract test 骨架（每 endpoint ≥1 happy path + 1 error case）
[MUST] 发现同名 domain model → 引用复用，冲突 → 回流 spec-writer
```

---

## planner 特化注入

```
[MUST] 方案对比 ≥ 2，引用已有 ADR 作为论据
[MUST] 文档影响清单通过 doc-map-manager --lookup 确认（非手动枚举）
[MUST] 产出 closure-checklist.md，P0 闭环步骤非空
```

---

## proposal-writer 特化注入

```
[MUST] 核心四段完整优先（Why/What/Capabilities/Non-Goals），不限长度
[MUST] Capabilities 每项可验证，Non-Goals 非空
[MUST] 超过 150 行 → 按 progressive-disclosure.md §2 拆分为多文件
```

---

## 铁律

```
1. 未注入 → 🛑 禁止委派
2. 注入模板 [MUST] 不可被 agent 跳过或标记 N/A
3. 注入模板与 agent SKILL.md 冲突 → 以注入模板为准
4. 新增 agent → 同步新增注入模板
5. 所有 agent 注入 = §A 通用基底 + agent 特化（≤4 条，V9.5 精简）
```

