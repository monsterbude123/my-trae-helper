# Stage Skill Agent 协议（V11）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> agent 如何使用 V11 stage skill 的标准协议。**不创建新的 stage agent skill**——TRAE IDE 已有 Task 子代理能力，本协议定义 agent 调用 stage skill 的标准接口。

---

## 1. 概念

| 概念 | 含义 |
|------|------|
| **stage skill** | V11 13 个 stage skill（intake / plan / spec / implement / review / ...） |
| **agent** | TRAE IDE Task 子代理（task-notification-agent / explore-agent 等） |
| **stage skill agent** | 用 Task 启动子代理 + 注入 stage skill 调用约定 = 完成的代理 |

**关键**：V11 不新增"stage agent skill"，而是给现有 agent 一个**调用 stage skill 的标准协议**。

---

## 2. agent 调用 stage skill 的 4 步协议

### Step 1: agent 委派头部（V11 §1 已定义）

```
[PIPELINE] stage: {N}    # 必填：哪个 stage
[DOC_WHITELIST] {paths}  # 必填：可读路径
[FORBIDDEN] docs/archive/**, .trae/tmp/**
  # V11.8.5 反馈补完 — 全局配置文件白名单（sub-agent 禁止改）:
  # playwright.config.ts, vitest.config.ts, acceptance_manifest.yaml,
  # .trae/fullstack4traev11.config.yaml, .trae/hooks.json, .trae/registry/*.yaml
[GITNEXUS] impact()      # 必填：必跑 gitnexus
[TASK] {一句话 ≤200 chars}
[OUTPUT] 4 字段: status / evidence / pass_count / next_hook
```

**agent 启动时主上下文必填**。

### Step 2: agent 加载 stage skill（V11 §0.5）

```
# agent 必走（sub-agent 也走）
1. 读 stage skill 的 SKILL.md frontmatter (stage_config + depends_on)
2. 读 references/common-iron-rules.md（含 Article XVII）
3. 读 references/common-anti-patterns.md（含 §19-22）
4. 读当前 stage 的 references/（如 07-implement/gitnexus-impact.md）
5. 读当前 stage 的 anti-patterns/
6. 列出"我能踩的雷"清单
7. 列状态卡 + 上游 Completion Report 输入
8. 执行 stage workflow
9. 输出 4 字段 Completion Report
```

### Step 3: agent 必读的 stage skill 文档

```yaml
stage_skill_loading:
  required:
    - SKILL.md                      # 主入口
    - references/*.md               # 引用清单
    - anti-patterns/*.md            # 反例
    - workflows/*.md                # 工作流
  scripts_to_use:
    - stage-gate.py                  # 门禁
    - state-card-validator.py        # 状态卡
    - <stage_specific>.py            # stage 特定脚本
```

### Step 4: agent 完成必走（V11 §3 + §4）

```yaml
agent_completion:
  output_format: # 4 字段（V11 §1 已定义）
    status: PASS | FAIL | PARTIAL
    evidence: # 命令 + 输出 + file:line
      - command: "..."
        output: "..."
        file_line: "file:line"
    pass_count: N  # 必填数字
    next_hook: |  # 下一阶段必走
      hook: pre-stage.sh | post-stage.sh | pre-accept.sh
      env:
        CHANGE_ID: "..."
        EXPECTED_STAGE: "..."
  blocker_report:  # Article XV 5 字段（如有阻塞）
    type: ...
    description: ...
    attempted_solution: ...
    time_consumed_minutes: ...
    attempt_count: ...
```

---

## 3. 主上下文 vs agent 责任边界

| 责任 | 主上下文 | agent |
|------|:---:|:---:|
| 加载 skill 入口 | ✅ | ❌ |
| 列"我能踩的雷" | ✅ | ⚠️ 接到委派后必列 |
| 跑门禁脚本（stage-gate.py） | ✅ | ⚠️ 接委派后跑 |
| 子代理委派 | ✅ | ❌ |
| 子代理完成验证 | ✅（Article IX）| ❌ |
| 子代理报告自评 | ❌ | ✅（self_attested）|
| 子代理报告抽检 | ✅（Article IX.1）| ❌ |
| 上游 Completion Report 必读 | ✅（主控）| ✅（被委派时）|
| 跨层证据（后端 + UI + 用户视角）| ✅ 必亲自跑 | ⚠️ 至少跑自己负责的层 |
| 阻塞报告 | ⚠️ 主上下文汇总 | ✅ agent 必 5 字段 |

---

## 4. 13 stage × agent 调用清单

> **V11.9 角色协议接线**: "agent 类型"列已映射为角色 id（见 [role-protocol.md](../role-protocol.md) §1 矩阵）。角色定义文件见 [skills/00-boot/agents/](../skills/00-boot/agents/)。一个角色可跨多 stage（如 jarvis 全域 gate），一个 stage 可多角色协作（如 explore-agent 拆为 tech-planner / test-expert）。

| Stage | 角色 id（agent 类型） | 必跑 gitnexus | 必跑脚本 |
|-------|-----------|:---:|------|
| -1 Intake | jarvis | ❌ | setup-feature.py + state-card-validator.py |
| 0 Plan | tech-planner / test-expert（3 路径并行）| ✅ impact | stage-gate.py + spec-purge.py |
| 0.5 Test Plan | test-expert | ✅ | state-card-validator.py |
| 1 Spec | product-manager / tech-planner | ❌ | code-hygiene.py + state-card-validator.py |
| 1.5 Prototype | prototype-designer | ❌ | visual-content-check.py + prototype-backfill-check.py |
| 2 Contract | tech-planner | ❌ | orphan-detector.py + state-card-validator.py |
| 3 Implement | backend-implementer / frontend-implementer（**TDD**）| ✅ 必跑 | code-hygiene.py + state-card-validator.py |
| 3.5 Real Verify | test-expert | ✅ | visual-content-check.py + dist-hash-check.py |
| 4 Review | test-expert（**不修代码**）| ✅ | acceptance-audit.py + state-card-validator.py |
| 4.5 Rot Scan | jarvis | ❌ | proactive-scan.py + self-diagnose.py |
| 5 Accept | product-manager | ❌ | spec-knowledge-extract.py + spec-purge.py |
| 6 Bug Fix | qa-submitter(**e2e 先行 FAIL**)| ✅ impact / context / query / detect_changes | code-hygiene.py + state-card-validator.py + reason-classifier.py(SKEPTICAL VALIDATION 触发时) |
| 7 Project Health | jarvis | ✅ impact | proactive-scan.py + self-diagnose.py |

**注**：TRAE IDE 默认 task-notification-agent / explore-agent 可用于大部分场景；复杂场景（如 spec-writer / contract-writer / debugger）可自定义 agent 类型。角色 id 与 agent 类型映射关系以 [role-protocol.md §1](../role-protocol.md) 矩阵 + [spec.md](../../../.trae/specs/adopt-v11-role-protocol/spec.md) MODIFIED Requirements 为准。

---

## 5. 反例（agent 必走 V11）

| 反例 | 触发 |
|------|------|
| ❌ agent 启动时**不读 stage skill SKILL.md** 就直接做 | Article IX 违反 |
| ❌ agent 不列"我能踩的雷"清单 | 反例 §21 触发 |
| ❌ agent 把 secret 写到工具调用参数 | Article XVII 违反 |
| ❌ agent 跨 stage（intake agent 做 implement 工作）| Article XII 违反 |
| ❌ agent 自评 PASS 但无 evidence | Article V 违反 |
| ❌ agent 反复"我搞错了"循环 | 反例 §19 触发 |
| ❌ agent 甩锅用户 | 反例 §20 触发 |
| ❌ review-agent 帮 implement 修代码 | Article IX + 反例 §3 触发 |
| ❌ agent 跳过 gitnexus 用 grep | Article V.6 违反 |

---

## 6. agent handoff 模板

```yaml
# agent → 主上下文 handoff
handoff:
  stage: "{stage_id}"
  agent_type: "{explore-agent|custom}"
  skill_loaded:
    - path: "skills/{NN}-{name}/SKILL.md"
    - references: ["..."]
    - anti_patterns: ["..."]
  landmines_listed: # 必填
    - "Article V.2: '已完成'必附证据"
    - "反例 §21: rule 通读"
    - "..."
  completion_report:
    status: PASS
    evidence:
      - file: "src/auth/login.ts"
        line: 42
        test: "tests/auth/login.test.ts PASS"
        coverage: "94.2%"
    pass_count: 24
    next_hook:
      hook: post-stage.sh
      env:
        CHANGE_ID: "2026-08-11-add-feature"
  blockers: []  # 或 Article XV 5 字段
```

---

## 7. 主上下文验收（必走 Article IX.1）

```yaml
main_context_verification:
  # 主上下文亲自抽检 agent 报告（不依赖子代理自评）
 抽检清单:
    - [ ] agent 必读 5 步都执行了？
    - [ ] agent 列的"我能踩的雷"清单完整？
    - [ ] agent evidence 中 file:line 可点击？
    - [ ] agent 未跨 stage 工作？
    - [ ] agent 无循环 PASS？
    - [ ] agent 无甩锅用户？
    - [ ] agent 无 secret 泄露？
  抽检方式:
    - 亲自 Read agent 提到的 file:line
    - 亲自跑 agent 提到的命令
    - 亲自 Read agent 提到的截图
  任意未 PASS → 🛑 REJECT agent 报告 → 让 agent 重做（不是委派给同一 agent）
```

---

## 8. 关联引用

- [V11 SKILL.md §1 委派速查](../SKILL.md) — 4 字段委派头部
- [V11 SKILL.md §0.5 加载协议](../SKILL.md) — agent 加载 stage skill 必走
- [Article V / IX / XI / XVII](common-iron-rules.md) — 4 铁律
- [反例 §19-22](common-anti-patterns.md) — agent 失败模式
- [stage-interaction-protocol.md](stage-interaction-protocol.md) — stage 间移交
- [agent-error-diagnosis.md](agent-error-diagnosis.md) — agent 失败根因诊断
