# Agent Completion Report 协议（精密交付标准）

> **定位**：所有 Agent 完成委派后必须产出的结构化交付报告。替代"说做完了"的口头汇报。
> **原则**：交付物可验证（Verifiable Artifacts），判定去人化（Mechanical Gates），自证生效（Self-Proving）。
> **触发**：任意 Agent 完成委派任务后强制执行。

---

## 一、核心命题

```
旧:  Agent 说 "做完了" → 主上下文相信 → 进入下一阶段（P1-1 不可见问题）
新:  Agent 返回结构化 Completion Report → 主上下文机械比对 → 全部匹配才放行
```

**Completion Report 不是建议，是门禁。不产出 Completion Report = 视为未完成。**

---

## 二、Completion Report 结构

```yaml
completion:
  # 必须字段
  status: COMPLETE | INCOMPLETE | FAILED
  agent: {agent-name}
  task: {委派时的任务描述}
  timestamp: {ISO 8601}

  # 需求清单（由委派方在任务分配时给定，Agent 不可修改）
  required_artifacts:
    - path: {文件路径}
      requirement: {对该文件的变更要求（可验证的阈值描述）}
      updated: true | false
    - path: {文件路径}
      requirement: {要求}
      updated: true | false

  # 实际产出（Agent 必须列出所有实际变更的文件）
  artifacts_produced:
    - path: {文件路径}
      change_summary: {一句话描述做了什么}
      lines_added: {N}
      lines_removed: {N}
      quality_evidence: {如何证明变更满足要求}

  # 遗漏项（如果 required_artifacts 中有未完成的）
  artifacts_missing:
    - path: {文件路径}
      reason: {为什么没完成}
      can_delegate: true | false   # 是否可委派其他人完成

  # 验证命令（主上下文可执行以验证产出的命令）
  verification_hint: "git diff --stat -- {paths}"
```

---

## 三、Completion Report 判定规则

### 3.1 状态判定（机械，不依赖人判断）

```
if status == "COMPLETE":
  → 所有 required_artifacts 的 updated == true
  → artifacts_missing 为空
  → verification_hint 可执行且非空

if status == "INCOMPLETE":
  → 部分 required_artifacts 的 updated == true
  → artifacts_missing 非空，每项有 reason
  → 主上下文判断：missing 项是否阻塞下一阶段？

if status == "FAILED":
  → 无法完成，或发现阻塞问题
  → artifacts_missing 说明原因
  → can_delegate 标记是否可转交
```

### 3.2 主上下文验证步骤（每阶段交接强制执行）

```
Agent 返回 Completion Report
  ↓
Step 1 — 文件存在性验证:
  git ls-files {artifacts_produced 中的每个 path}
  → 任一文件不存在 → 🛑 REJECT（Agent 声称产出但不存在）
  ↓
Step 2 — 变更非空验证:
  git diff --stat {paths}
  → diff 为空但 Agent 声称有变更 → 🛑 REJECT（空提交）
  ↓
Step 3 — 完整性验证:
  required_artifacts 中 updated=true 的数量 vs artifacts_produced 数量
  → 不一致 → 🛑 REJECT（数据矛盾）
  ↓
Step 4 — gitignore 误杀检查:
  git check-ignore {artifacts_produced 中的每个 path}
  → 任一文件被忽略 → 🛑 REJECT（产出被屏蔽，见 P0-2）
  → 根因修复：检查 build-index.py 或其他构建脚本是否静默修改了 .gitignore
  → 禁止构建脚本自动写入 .gitignore（P0-2 根因：build-index.py 静默添加了 docs/ 排除规则）
  ↓
Step 5 — 路径规范检查:
  {reports 类文件} 必须在 docs/reports/ 下
  {prototypes 类文件} 必须在 docs/prototypes/ 或 specs/{change}/prototypes/ 下
  → 路径错误 → 🛑 REJECT（放错路径，见 P2-3）
  ↓
全部通过 → 🟢 可进入下一阶段
```

---

## 四、各 Agent 的 required_artifacts 定义

### 4.1 doc-updater（文档同步）

```yaml
required_artifacts:
  - path: ARCHITECTURE.md
    requirement: "§实施状态段已更新（≥5 行实质性变更）"
  - path: README.md
    requirement: "索引状态 + 变更记录已更新"
  - path: specs/.state-card.md
    requirement: "阶段标记 + 健康度已更新"
  - path: scaffold-roadmap.md
    requirement: "阶段标记 + 产出说明已更新（如存在此文件）"
  - path: modules/*.md
    requirement: "所有相关模块的实施状态行已标记（🟢/🟡/🔴）+ 实际交付物说明"
  - path: 文档索引
    requirement: "已通过 doc-map-manager 技能重建"
  - path: prototypes/
    requirement: "spec §2 原型已提取导出（如本阶段涉及 UI）"
  - path: docs/reports/
    requirement: "验收报告已归档（如本阶段走完 Review）"
```

### 4.2 implementer（代码实现）

```yaml
required_artifacts:
  - path: {tasks.md 中列出的每个源文件}
    requirement: "TDD RED→GREEN 完成，测试通过"
  - path: {对应的测试文件}
    requirement: "覆盖率 ≥ 80%，关键路径 100%"
  - path: {modules/ 模块文档}
    requirement: "P0 内容（接口契约+数据模型）已同步"
  - path: {docs/specs/changes/{change}/}
    requirement: "tasks.md 全部 [x]，量化汇报已输出"
```

### 4.3 reviewer（审查）

```yaml
required_artifacts:
  - path: docs/reports/{change}-acceptance-scorecard-{date}.md
    requirement: "7 维度 checklist + 自动计算评分 + 一致性校验通过"
  - path: docs/reports/{change}-drift-report-{date}.md
    requirement: "契约漂移检测完成（如有漂移）"
```

---

## 五、反模式

| 禁止（旧模式） | 必须（新模式） |
|--------------|-------------|
| "已完成文档同步" | Completion Report + diff 验证 |
| acceptEdits 静默操作无 diff 回显 | artifacts_produced 列出所有文件 + verification_hint |
| Agent 自行判断哪些文件需要同步 | required_artifacts 由委派方给定 |
| artifacts_missing 为空但实际有遗漏 | artifacts_missing 必须诚实列出 |
| gitignore 屏蔽了产出无人知晓 | Step 4 gitignore 检查拦截 |
| build-index.py 静默写 .gitignore 排除 docs/ | 构建脚本禁止自动修改 .gitignore；如需修改必须显式警告 |
| 直接编辑文档索引文件 | 通过 doc-map-manager 技能更新文档索引 |

---

## 六、与现有体系的衔接

| 现有文档 | 变更 |
|---------|------|
| [quantitative-acceptance.md](quantitative-acceptance.md) | 评分逻辑改为 checklist 自动推导（见该文档 V6.0） |
| [feedback-loop.md](feedback-loop.md) | 回流触发条件增加 "Completion Report status != COMPLETE" |
| [state-card.md](state-card.md) | 阶段切换时增加 "Completion Report 验证通过" 标记 |
