# Stage Physical Isolation — 阶段物理隔离规范（V12 NEW）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> **核心思想（借鉴 husky）**: 每个 stage 是独立"提交门",stage 之间通过物理目录隔离而非软链接 / 逻辑层。
> **必读**: V11 SKILL.md §0.5 + document-layer.md + state-card-protocol.md
> **替代**: V11 document-layer.md §4 层架构（保留为逻辑概念,本文件为物理映射）

---

## §0 设计哲学（V12 蒸馏自 canvas-asset-folders）

```
1. 物理隔离 > 逻辑分层: 文档不只是标注"这是 process 层",而是直接放在 stage/ 子目录隔离读取
2. 阶段门禁 > 流程建议: husky 式硬阻断,失败 = stage 冻结（不允许"先继续回头看"）
3. 事实唯一源: 项目的最终落地标准(spec/contract/code)只放 fact/ 目录,不被 stage 重置影响
4. 子代理边界: 每个 stage agent 只读自己 stage/ + fact/,主上下文负责跨 stage 注入
5. 验收瘦身: 验收 stage 只看页面 + 功能,不读代码细节（代码细节已通过 stage 3 自身门禁）
```

---

## §1 目录物理布局（V12 NEW）

```
docs/specs/changes/{change-id}/
├── fact/                       ← 事实唯一源（不可重置，跨 stage 共享）
│   ├── spec.md                 ← Layer 1: AC / INV / Edge Cases
│   ├── plan.md                 ← Layer 2: Capabilities / Non-Goals
│   └── contracts/              ← Layer 3: domain-models / api-contracts / events / validation-rules
│       ├── domain-models.md
│       ├── api-contracts.md
│       ├── events.md
│       └── validation-rules.md
├── stage/                      ← 流程文档（重置时按需删除/保留）
│   ├── -1-intake/              ← 状态卡 + 中转文档
│   │   ├── .state-card.md      ← 独立状态卡（每 stage 一张）
│   │   ├── intake-notes.md     ← 中转文档（只在本 stage 活跃时存在）
│   │   └── handoff-out.md      ← 交给下一 stage 的纯摘要（≤200 字）
│   ├── 0-plan/
│   │   ├── .state-card.md
│   │   ├── plan-notes.md       ← 重置时保留（用户决策）
│   │   └── handoff-out.md      ← ≤200 字纯摘要
│   ├── 0.5-test-plan/
│   ├── 1-spec/
│   ├── 1.5-prototype/
│   ├── 2-contract/
│   ├── 3-implement/
│   ├── 3.5-real-verify/
│   ├── 4-review/               ← ⚙ 仅验页面+功能（不读代码细节）
│   ├── 4.5-rot-scan/
│   └── 5-accept/
└── archive/                    ← 归档后由 5-accept 写入（不可变）
```

---

## §2 重置协议（V12 强化 — 借鉴 husky 强制门禁）

### 2.1 用户命令"把 stage7 spec 打回 stage3"

**操作**（物理重置，不污染 fact 层）:

```
Step 1: 保留 fact/ 整个目录（spec/plan/contract 是事实源）
Step 2: 删除 stage/3-implement/ ~ stage/5-accept/ 全部内容（重置后 stage 流程文档）
Step 3: 保留 stage/-1-intake/ ~ stage/2-contract/（如果用户决策"保留"则跳过删除）
Step 4: 重置当前 stage 状态卡 = 3-implement,stage_status=pending
Step 5: 写入 reset_history 字段（V11 §7.4 沿用）
```

**V12 强制**：

```bash
python scripts/stage-gate.py --change {id} --reset-to stage/3-implement
# 此命令不可被主上下文手动覆盖（husky 式阻断）
```

### 2.2 stage 重置脚本（husky 思想核心）

```
scripts/stage-gate.py V12 NEW:
  --check {stage-id}:     强制门禁校验（FAIL = 退出码 1，阻断下一 stage 启动）
  --reset-to {stage-id}:  物理重置（保留 fact/，删除 stage/ 后续目录）
  --status {change-id}:   列出当前 stage 状态 + 门禁结果
```

**husky 类比**:

| husky 概念 | V12 stage-gate.py 类比 |
|---|---|
| pre-commit hook | stage 切换前强制门禁 |
| hook 失败 = 阻断 commit | 门禁 FAIL = 阻断 stage 切换 |
| 强制 lint/test pass | stage 产物必经校验脚本 |
| 不可绕过 | 主上下文不可手动标记 PASS |

---

## §3 子代理白名单（V12 NEW — 防过度处理范围外）

每个 stage agent 启动时，**只读**：

| Stage | 白名单（只读） | 黑名单（不可读） |
|---|---|---|
| -1 Intake | fact/spec.md（如果存在）+ AGENTS.md + rules/ | 其他 stage/ 全部 |
| 0 Plan | fact/spec.md + stage/-1-intake/handoff-out.md + 同 stage | 其他 stage |
| 0.5 Test Plan | fact/spec.md + fact/plan.md + stage/0-plan/handoff-out.md | 其他 stage |
| 1 Spec | fact/plan.md + stage/0.5-test-plan/handoff-out.md | 其他 stage |
| 1.5 Prototype | fact/spec.md + stage/1-spec/handoff-out.md | 其他 stage |
| 2 Contract | fact/spec.md + stage/1-spec/handoff-out.md | 其他 stage |
| 3 Implement | fact/contracts/ + stage/2-contract/handoff-out.md | 其他 stage |
| 3.5 Real Verify | fact/contracts/ + stage/3-implement/handoff-out.md + code/ | 其他 stage |
| **4 Review** | **fact/spec.md AC + 截图 + 视频** | **stage/3-implement/*（代码细节）** |
| 4.5 Rot Scan | fact/ + 全 stage/（只读诊断） | archive/ |
| 5 Accept | fact/ + stage/4.5-rot-scan/handoff-out.md | archive/（写） |

**主上下文责任**:

```
委派 Stage X agent 时:
  1. 注入 doc_whitelist = 白名单路径列表
  2. 注入 handoff-in = 上一 stage 的 handoff-out.md 全文（≤200 字）
  3. 不注入其他 stage 内容
  4. Stage agent 完成任务 → 返回 handoff-out.md（≤200 字）
  5. 主上下文接收 → 校验范围（agent 不应读过白名单外文件）→ 进入下一 stage
```

---

## §4 验收 stage 瘦身（V12 NEW — 防过度处理）

**Stage 4 Review 只做 4 件事**:

```
1. 读 fact/spec.md AC 清单（验收标准）
2. 看 prototype 截图（如有）
3. 看 real-verify 截图/视频
4. 对比 AC vs 实际功能（页面是否可见？交互是否通？）

不做:
  ❌ 读代码细节（Stage 3 实施已通过自身门禁）
  ❌ 评判代码风格（不属本 stage 职责）
  ❌ 重构建议（Stage 4.5 rot-scan 职责）
  ❌ 性能优化建议（超出验收范围）
```

**Stage 4 输出**: `review-report.md` 含

- AC 对照表（每条 AC: 通过/不通过/不适用）
- prototype 截图 vs 实际截图对比（≤5 张）
- 视觉差异 %（工具自动）
- 阻塞清单（如有）

**主上下文从 review-report 提纯**:

```
review-report 必填 ≤ 300 字:
  - AC 通过率（如 8/10）
  - 视觉差异（如 prototype vs 实际差异 15%）
  - 阻塞清单（如有）
  
不带代码细节 / 不带重构建议 / 不带性能分析
```

---

## §5 主上下文跨 stage 信息注入规范

每个 stage agent 只读白名单，但主上下文负责跨 stage 信息桥接:

```
主上下文收到 Stage N agent Completion Report:
  1. 读 stage/N/handoff-out.md（agent 必填）
  2. 读 stage/N/notes.md（仅主上下文，agent 不可读）
  3. 主上下文提纯跨 stage 信息：
     - Stage 3 → Stage 4 注入: "实现细节: 用 X 库处理 Y"（帮助 reviewer 理解视觉决策）
     - Stage 3 → Stage 5 注入: "实施发现: Z 接口需扩展"（帮助 accept 决策）
  4. 写入 stage/N+1/handoff-in.md（注入到下一 stage agent）
```

**核心**：

```
子代理 = 单一职责（不越界）
主上下文 = 跨 stage 信息桥（注入摘要）
事实层 = 唯一真相源（不可重置）
流程层 = 物理隔离（重置时按 stage 删除）
```

---

## §6 反例（V12 蒸馏自 canvas-asset-folders）

### 反例 1：sub-agent 读过白名单外文件

```
现象: Stage 3 implementer 读了 stage/4-review/ 的旧 review-report 试图"避免之前提的问题"
后果: 上下文膨胀 + agent 决策被旧报告污染 + Stage 4 反而失去独立性
纠正: 委派注入 doc_whitelist 严格边界 + Completion Report 校验"未读白名单外"
```

### 反例 2：验收 stage 评判代码细节

```
现象: Stage 4 reviewer 读 src/*.ts 评判命名风格 / 函数抽象 / 性能
后果: review 时间膨胀（简单功能跑一天）+ 与 Stage 3 职责重叠 + 主上下文 review 链冗长
纠正: Stage 4 SKILL.md §铁律 1 = "只看页面和功能，不读代码细节"
```

### 反例 3：状态卡膨胀未隔离

```
现象: 单张 change 级状态卡塞入 13 stage 进度 + 跨 stage notes + 阻塞 + 验证截图
后果: 主上下文每次 stage 切换要读全卡（context 击穿）+ 跨 stage 信息互相污染
纠正: 每 stage 独立 .state-card.md（仅本 stage 字段）+ 主上下文持汇总卡（project-level）
```

### 反例 4：阶段门禁放水

```
现象: 主上下文看到 "Stage 3 implementer 已返回" → 直接放行到 Stage 3.5，跳过 gate 校验
后果: 实施未通过 TDD / drift-check 就进入验证 → 腐化累积 → Stage 4 才暴露
纠正: scripts/stage-gate.py --check 强制门禁（FAIL = 退出码 1，husky 式阻断）
```

### 反例 5：重置时误删 fact 层

```
现象: "stage 7 spec 打回 stage 3" 时 agent 把 fact/spec.md / fact/plan.md / fact/contracts/ 全删
后果: 事实源丢失 + 需重新做 Stage 0/1/2（耗时数小时）
纠正: scripts/stage-gate.py --reset-to 默认保留 fact/ 整个目录（除非用户明确说"重做 fact"）
```

---

## §7 与现有规则关系

| 现有规则 | 关系 | V12 处理 |
|---|---|---|
| V11 document-layer.md §4 层 | 保留作为逻辑概念 | 本文件为其物理映射 |
| V11 state-card-protocol.md §1.2 | 改为每 stage 独立卡 | 主上下文持项目级 + change 级汇总卡 |
| V11 SKILL.md §4 Hook 清单 | 保留 hook 框架 | scripts/stage-gate.py 为门禁执行器 |
| V11 sub-agent-rules.md §3 上下文经济 | 强化 | 委派注入 doc_whitelist 严格边界 |

---

## §8 实施步骤（用户授权后）

```
Step 1: Edit references/document-layer.md §文档分层 → 引用本文件为物理映射
Step 2: 新建 scripts/stage-gate.py（参考 V11 phase-gate.py，强化为 husky 式硬阻断）
Step 3: 新建 templates/state-card-per-stage.md（每 stage 独立卡模板）
Step 4: Edit SKILL.md frontmatter version: "12.0.0" + 加 stage_config 引用本文件
Step 5: Edit skills/09-review/SKILL.md §铁律 → "只看页面和功能，不读代码细节"
Step 6: Edit references/sub-agent-rules.md §3 → 引用本文件 §3 白名单
Step 7: 跑 scripts/init-from-zero.py --upgrade-from-v11（升级已用 V11 的项目）
Step 8: 更新 CHANGELOG.md 写 V12 升级说明
```

**不立即实施原因**: 用户尚未确认方案 + 质疑性校验需用户复核 + V12 是主版本升级（按 §B L1 决策层级走 ADR）

---

## §9 一句话铁律

```
V12 = 物理隔离（stage/ 子目录）+ 事实唯一源（fact/ 不可重置）+ husky 式门禁（scripts/stage-gate.py 硬阻断）+ 子代理边界（白名单严格隔离）
```

---

*来源: 2026-08-12/13 canvas-asset-folders 实战蒸馏（用户反馈"stage 7 打回 stage 3 想干净重置"+"子代理过度处理"+"验收 stage 太漫长"）+ husky 思想借鉴 + V11 §3.7 反虚假交付原则。*
*版本: 1.0.0（V12 提案）*
