# 5 把刀详细设计方法论

> 本文件详细说明 fullstack-skill-architect 的 5 把刀的**借鉴来源、具体实现、变体方案**。

---

## §1 物理隔离(借鉴 Docker 镜像层)

### 1.1 Docker 类比

```
Docker 镜像层 = 只读,跨容器共享
Docker 容器层 = 可写,可重建

V12 物理隔离:
  fact/   = 镜像层(只读,跨 stage 共享,不可重置)
  stage/  = 容器层(可写,每 stage 独立,可重置)
```

### 1.2 目录布局模板

```
docs/specs/changes/{change-id}/
├── fact/                       ← 镜像层(只读)
│   ├── spec.md                 ← Layer 1: AC / INV / Edge Cases
│   ├── plan.md                 ← Layer 2: Capabilities / Non-Goals
│   └── contracts/              ← Layer 3: api-contracts / events / domain-models
│       ├── api-contracts.md
│       ├── events.md
│       ├── domain-models.md
│       └── validation-rules.md
├── stage/                      ← 容器层(可写,每 stage 独立)
│   ├── -1-intake/
│   │   ├── .state-card.md      ← 每 stage 独立卡
│   │   ├── intake-notes.md     ← 中转文档
│   │   └── handoff-out.md      ← ≤200 字纯摘要
│   ├── 0-plan/
│   ├── 0.5-test-plan/
│   ├── 1-spec/
│   ├── 1.5-prototype/
│   ├── 2-contract/
│   ├── 3-implement/
│   ├── 3.5-real-verify/
│   ├── 4-review/
│   ├── 4.5-rot-scan/
│   └── 5-accept/
└── archive/                    ← 不可变(归档后冻结)
```

### 1.3 重置协议(借鉴 git reset --hard vs --soft)

```
V11 重置(规则不全):
  状态卡重置到 N stage + 删除 plan 之后所有 docs(易误删)

V12 重置(借鉴 git reset --hard):
  scripts/stage-gate.py --reset-to {stage-id} 自动:
    1. 保留 fact/ 整个目录(默认)
    2. 保留 stage/{N-1} 之前的 stage/(默认)
    3. 删除 stage/{N} 之后的所有 stage/(重置)
    4. 重置当前 stage 状态卡 = pending
    5. 写入 reset_history 字段
```

---

## §2 门禁硬化(借鉴 husky pre-commit)

### 2.1 husky 借鉴来源(2026 WebSearch 对比)

| 工具 | 配置形式 | 并行 | 阻断 | 跨语言 |
|---|---|:-:|:-:|---|
| husky v9 | `.husky/*.sh` | ❌ | ✅ | Node.js only |
| lefthook | `lefthook.yml` | ✅ | ✅ | 任意 |
| pre-commit | `.pre-commit-config.yaml` | ✅ | ✅ | Python |

**V12 借鉴 husky 思路,不引入工具**(标准库优先,Python 生态)。

### 2.2 stage-gate-pre-stage.sh 实现模板

```bash
#!/usr/bin/env bash
# V12 stage-gate-pre-stage.sh — 借鉴 husky pre-commit 硬阻断
# 触发: stage 切换前(TRAE IDE PreToolUse event)
# 退出码: 0 = 放行, 1 = 阻断

set -e

# 1. 必跑 stage-gate.py 验证
python "${PROJECT_ROOT}/scripts/stage-gate.py" \
    --state-card "${PROJECT_ROOT}/docs/specs/.state-card.md" \
    --stage "${CURRENT_STAGE}" \
    --json

if [ $? -ne 0 ]; then
    echo "🛑 BLOCKED: stage ${CURRENT_STAGE} gate FAIL"
    echo "   主上下文不可手动放行,必跑修复脚本"
    exit 1
fi

# 2. 必跑 state-card-validator 验证
python "${PROJECT_ROOT}/scripts/state-card-validator.py" \
    "${CHANGE_DIR}/.state-card.md"

if [ $? -ne 0 ]; then
    echo "🛑 BLOCKED: state-card 字段不完整"
    exit 1
fi

echo "✅ PASS — stage ${CURRENT_STAGE} gate verified"
exit 0
```

### 2.3 阻断硬性约束

```
MUST: 主上下文不可手动标 PASS
MUST: --no-verify 等价物禁止(husky 反模式)
MUST: gate 失败必须修复底层问题,不允许"先继续回头看"

反例:
  - 看到"实施已返回" → 默认放行到 Stage 3.5
  - 看到"测试通过" → 默认跳过 stage-gate
  - 看到"主上下文认为够了" → 手动写 completed

正确:
  - 任何 stage 切换前必跑 stage-gate-pre-stage.sh
  - exit 0 才放行
  - exit 1 必跑修复 → 重跑 → 再 exit 0
```

---

## §3 子代理边界(借鉴 K8s RBAC)

### 3.1 K8s RBAC 类比

```
K8s RBAC:
  role = 子代理身份
  namespace = 文档目录
  roleBinding = 白名单(角色能访问哪些 namespace)
  
V12 子代理边界:
  stage agent = 子代理身份
  docs/specs/changes/{id}/ = namespace
  doc_whitelist = 白名单(agent 只能读哪些文件)
```

### 3.2 委派注入头模板

```yaml
# 委派头(主上下文发往子代理)
[MUST-READ] AGENTS.md + .trae/rules/
[PIPELINE] stage: {N}
[DOC_WHITELIST]  # ← 强白名单(本会话蒸馏)
  - docs/specs/changes/{id}/fact/spec.md
  - docs/specs/changes/{id}/stage/{N-1}/handoff-out.md
  - docs/specs/changes/{id}/stage/{N}/notes.md
[FORBIDDEN]  # 黑名单(已有,继续保留)
  - docs/archive/**
  - .trae/tmp/**
  - diagnostic/bugs/**
[GITNEXUS] impact()
[TASK] {≤200 chars}
[OUTPUT] 4 字段: status / evidence / pass_count / next_hook
[VERIFICATION] "未读白名单外"  # ← 新增,子代理必填
```

### 3.3 白名单矩阵(13 stage)

```
| Stage | 白名单(只读) | 黑名单(不可读) |
|---|---|---|
| -1 Intake | fact/ + AGENTS.md + rules/ | 其他 stage/ 全部 |
| 0 Plan | fact/spec.md + stage/-1-intake/handoff-out.md | 其他 stage |
| 0.5 Test Plan | fact/spec.md + fact/plan.md + stage/0-plan/handoff-out.md | 其他 stage |
| 1 Spec | fact/plan.md + stage/0.5-test-plan/handoff-out.md | 其他 stage |
| 1.5 Prototype | fact/spec.md + stage/1-spec/handoff-out.md | 其他 stage |
| 2 Contract | fact/spec.md + stage/1-spec/handoff-out.md | 其他 stage |
| 3 Implement | fact/contracts/ + stage/2-contract/handoff-out.md | 其他 stage |
| 3.5 Real Verify | fact/contracts/ + stage/3-implement/handoff-out.md + code/ | 其他 stage |
| **4 Review** | **fact/spec.md AC + 截图 + 视频** | **stage/3-implement/(代码细节)** |
| 4.5 Rot Scan | fact/ + 全 stage/(只读诊断) | archive/ |
| 5 Accept | fact/ + stage/4.5-rot-scan/handoff-out.md | archive/(写) |
```

### 3.4 主上下文跨 stage 注入规范

```
主上下文收到 Stage N agent Completion Report:
  Step 1: 读 stage/N/handoff-out.md(agent 必填,≤200 字)
  Step 2: 主上下文提纯跨 stage 信息:
    - Stage 3 → Stage 4 注入: "实现细节: 用 X 库处理 Y"(帮助 reviewer 理解视觉决策)
    - Stage 3 → Stage 5 注入: "实施发现: Z 接口需扩展"(帮助 accept 决策)
  Step 3: 写入 stage/N+1/handoff-in.md(注入到下一 stage agent)
```

---

## §4 验收瘦身(借鉴"用户故事 vs 系统实现")

### 4.1 拆分原则

```
V11 验收: 4 维评分(代码 25%/API 30%/UIUX 25%/边际 20%)— 必读 5 件套
V12 验收: 拆分为 2 个独立验证
  - 页面功能验证(Stage 4 主责): 只读 spec AC + 截图 + prototype ↔ implementation 对照
  - 代码质量验证(Stage 3.5 + Stage 4.5 副责): 代码细节 + 覆盖 + 性能 + rot
```

### 4.2 Stage 4 Reviewer 工作流(8 步)

```
Step 1: 加载《给验收角色的一封信》(配套文档)
Step 2: 加载委派头 [DOC_WHITELIST] + [STAGE_CONTEXT] + handoff-in
Step 3: 读 fact/spec.md §AC(必读)
Step 4: 看 prototype 截图(必读)
Step 5: 看 stage/3.5-real-verify/ 截图 + 视频(必读)
Step 6: 对比 AC vs 实际,走 §3 工具-人类分层判定
Step 7: 写 review-report.md(模板见《信》§1.3)
Step 8: 写 handoff-out.md(≤ 200 字) → 返回 Completion Report
```

### 4.3 验收输出 review-report.md 模板

```yaml
## Stage 4 Review Report — {change-id}

### AC 对照表(必填)
| AC # | 验收标准 | 通过 | 视觉差异 | 阻塞 |
|------|---------|:----:|:-------:|:----:|
| AC-1 | 用户能创建文件夹 | ✅ | 5% | - |
| AC-2 | 用户能拖拽重排 | ⚠️ | 30% | 拖拽后无视觉反馈 |
| AC-3 | 删除确认 modal | ✅ | 8% | - |
| AC-N | ... | ❌ | - | 页面 404 |

### prototype ↔ implementation 对照(必填)
- 截图数: ≤ 5 张
- 工具计算视觉差异: 平均 X%(vision-audit / visual-content-check)
- L1/L2/L3 fidelity 等级: spec/design-prompt 声明,默认 L2 mockup
- L2 容许差异 ≤ 30%

### 主上下文提纯(必填 ≤ 300 字)
- AC 通过率: 8/10(80%)
- 视觉差异: 平均 12%(L2 容许范围内)
- 阻塞: 2 项(AC-2 拖拽反馈 + AC-N 404)
- 决策: 退回 Stage 3 修复
```

---

## §5 革命性瘦身(减法 > 加法)

### 5.1 二元判定表模板

| 类别 | 文件/目录 | 判定 | 理由 |
|---|---|:-:|---|
| **V 蒸馏溯源** | `references/V{N-1}-distillation-source-map.md` | ❌ 删 | V{N-1}→V{N} 蒸馏已完成,过渡产物 |
| **V 实战反例(stage 级)** | `skills/*/anti-patterns/V{N-1}-battle-tested.md` | ❌ 删 | 13 份过渡引用,V{N} 反例已实装 |
| **研究草稿** | `research/` | ❌ 删 | 升级期工作笔记,SKILL.md 未引用 |
| **CHANGELOG.md 段** | 早期 V{N}.0 段 | ⚠ 精简 | 保留版本号,删除实装清单 |

### 5.2 判定方法(可验证)

```bash
# 1. grep 引用 = 0 命中 = 可删
grep -r "{file}" references/ skills/ SKILL.md
  → 必须 0 命中

# 2. git history 查"为何存在"
git log --all --diff-filter=A --follow --name-only --format="" -- "{file}"
  → 必查创建 commit 消息判断用途

# 3. scripts/ 检查(被引用 = 必留)
grep -r "{file}" scripts/
  → 0 命中 = 可删
```

### 5.3 瘦身验证协议

```bash
# 1. 验证无引用断裂
grep -r "{deleted-file}" references/ skills/ scripts/ SKILL.md
  → 必须 0 命中

# 2. 跑全套校验脚本
python scripts/state-card-validator.py docs/specs/.state-card.md  # 项目级
python scripts/proactive-scan.py  # 10/10 PASS
python scripts/self-diagnose.py  # 6/6 PASS
python scripts/hooks-fidelity.py --project-root .

# 3. 写瘦身报告
Write docs/reports/v{N}.x-slim-{date}.md(≤ 60 行)
  ## 体积瘦身统计
  - 删除文件: X
  - 删除行数: Y
  - 体积变化: -Z%
  - 验证: state-card-validator X/X + proactive-scan X/X + self-diagnose X/X
```

---

## §6 借鉴来源汇总

| 设计 | 借鉴来源 | 借鉴什么 |
|---|---|---|
| 物理隔离 | Docker 镜像层 vs 容器层 | 事实层只读 vs 流程层可写 |
| 门禁硬化 | husky pre-commit v9 | exit 0/1 硬阻断 + 不可绕过 |
| 子代理边界 | K8s RBAC | role/namespace/roleBinding 三元组 |
| 验收瘦身 | 用户故事 vs 系统实现 | 业务视角 vs 技术视角拆分 |
| 革命性瘦身 | git reset --hard | 删 stage 后目录 + 保留 fact |
| 精华糟粕二元判定 | skill-optimization-method | MUST FIX / SHOULD ADD / ACCEPTABLE 三级 |
| 质疑性校验 4 维度 | skeptical-validation-protocol | 根因/责任/重叠/成本 |

---

*来源: 2026-08-13 my-trae-helper V11.3 升级会话 + 2026 WebSearch husky/lefthook 对比 + V11 §3.7 反虚假交付原则 + skill-optimization-method 11 铁律。*