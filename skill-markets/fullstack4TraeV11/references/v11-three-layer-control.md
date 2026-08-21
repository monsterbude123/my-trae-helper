# V11 三层架构详细协议(Gate / Guard / Execution)

> **来源**:V12 SKILL.md §0 + §1(贾维斯分层模型 / L1-L4 Gate / Stage Gate / Hook / Execution 流水线)
> **蒸馏日期**:2026-08-19(vibe-coding-standards v2.5 瘦身 — 从 SKILL.md §0 §1 抽出)
> **目的**:减轻 SKILL.md 体积,把分层模型 / 贾维斯防线 / Stage 子层门禁细节抽到 references/

---

## §0.0 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                     Gate 层（门禁）                          │
│   Git 操作级阻断（L1-L4）+ Stage 切换级阻断（pre/post-stage）│
│              ↓ PASS（才进入下一层）                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Guard 层（守卫）                          │
│         TRAE IDE event hook + Shell hook 自动化检查          │
│              ↓ PASS（才进入下一层）                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Execution 层（执行）                        │
│              13 stage 流水线标准化执行                       │
└─────────────────────────────────────────────────────────────┘
```

**联动规则(V12 沿用 V11.4 铁律)**:
- Gate PASS → Guard 层启动
- Guard PASS → Execution 层启动
- 任一层 FAIL → 阻断 + 5 字段阻塞报告(见 Article XV)

---

## §0.0.5 贾维斯分层模型(V12 沿用 V11.7.0 — 防 agent 改标准)

> 详见 [skills/00-boot/agents/jarvis.md](../skills/00-boot/agents/jarvis.md)。三层防线 + 三层 guard/gate,详见 [gate-configuration-protocol.md](gate-configuration-protocol.md)。

```
防线三(由软到硬):
  协议层 — [JARVIS-DELEGATION] 委派头部(挡守规矩的 agent)
  白名单层 — jarvis.md §3 路径白名单(挡越权直改的 agent)
  机械层 — gate-integrity-guard.py hash 锁(挡一切绕过行为,事前拦截)

分层三(L-module / L-app / L-system,docs 流程前置层按 stage 顺序跑):
  L-module 模块基础层 — CRUD 单测 + 模块结构      → 挂 L1 pre-commit
  L-app    应用层      — 契约对齐 + 模块集成 + E2E → 挂 L2 pre-push
  L-system 系统层      — AC 核销 + 腐化扫描 + 发布 → 挂 L3 merge / L4 release

唯一写权: 贾维斯 sub-agent(白名单机制 + 委派协议 + hash 锁兜底)
```

**硬化状态(V12 沿用 V11.5 更新)**:
- **Gate 层**:部分硬化(husky pre-commit/pre-push 绑定 L1→Stage 1 + L2→Stage 3.5);**13 个 stage 门禁已全部声明式登记**到 [registry/gates.yaml](../registry/gates.yaml)(flow 层),`run-all-guards.py` 可程序化断言每 stage 门禁存在性
- **Guard 层**:部分硬化(hooks-fidelity.py 验证 TRAE IDE event hooks 完整性)
- **Execution 层**:未硬化(依赖 Agent 自律 + Article IV 委派纪律)

> **Flow 层 Registry(V12 沿用 V11.5)**:fact 层(人类+agent 读 .md)与 flow 层(纯程序化解析 .yaml)分离。四表 = `gates.yaml`(13 stage 门禁)+ `guards.yaml`(守卫)+ `state-machine.yaml`(状态机)+ `repair-flow.yaml`(修复流程)。**状态卡本质是状态机**,驾驶舱角色(主上下文)唯一可改状态字段(见 `state-card-protocol.md` 九章)。统一消费脚本 `run-all-guards.py` 读四表输出 PASS/FAIL 矩阵,任一 FAIL → exit 1。详见 [registry/README.md](../registry/README.md)。

> **⚠️ 对齐诊断(V12 沿用 V11.4.1)**:虽有 13 stage 门禁声明,但**仅 Stage 1(L1)+ Stage 3.5(L2)绑定 Git 钩子层**,其余 11 个 stage 依赖 `stage-gate.py`(shell 手动触发)无强制宿主,Agent 仍可能跳过执行。registry 解决了"门禁可被程序化断言",但"执行强制"仍需后续把 L3/L4 绑定到 CI。完整逐 stage 矩阵见 [v7-to-v11-evolution.md §F](v7-to-v11-evolution.md)。

---

## §0.1 Gate 层 — Git 级 + Stage 级门禁

### §0.1.1 Git 子层(L1-L4 Gate)

| Gate | 触发 | 检查项 | 阻断级别 |
|:---:|------|--------|:-------:|
| **L1 Commit** | `git commit` | lint + typecheck + unit + security/structure | 🛑 阻断 |
| **L2 Push** | `git push` | integration + coverage + dependency + build | 🛑 阻断 |
| **L3 Merge** | PR merge | L2 + CAPABILITY-MAP 同步 + SECURITY-MAP 同步 | 🛑 阻断 |
| **L4 Publish** | Release | L3 + 全量扫描 + 灰度发布 + 自动升级 tag | 🛑 阻断 |

**Gate 自验收铁律(V12 沿用 V11.4 强化)**:
```
MUST: 写完任何 Gate 脚本后必须用真反例跑自验收
验证:
  - tmp 目录造违规样本 → 跑 Gate → 期望 exit ≠ 0
  - PASS 态 / BLOCK 态 / 边界态 三态必跑
固化:
  - 反例样本必须写进 tests/unit/test_*.py
```

详见 [skill-acceptance §7](../../skill-acceptance/SKILL.md) + [agent-dev-control-kit §11](../../agent-dev-control-kit/SKILL.md)

### §0.1.2 Stage 子层(pre-stage / post-stage / pre-accept)

| Stage | 入口 → 出口 | 门禁 | 用户确认 |
|:---:|------|------|:---:|
| -1 | 用户意图 → 状态卡 + 路由决策 | 意图识别 + 路由 | ⚙ |
| 0 | 状态卡 → plan.md | 3 路并行探索 + GitNexus impact | 🛑 |
| 0.5 | plan.md → test-plan.md | 验收维度 → 测试用例映射 | ⚙ |
| 1 | test-plan.md → spec.md | Enhanced Acceptance + clarify ≥2 轮 | 🛑 |
| 1.5 | spec.md → prototype | 双源兼容 | ⚙ |
| 2 | spec.md → contracts/ | contract-gate.py | ⚙ |
| 3 | contracts/ → 代码 + 测试 | TDD GREEN + DRIFT CHECK | 🛑 |
| 3.5 | Implement → verify-report | 5 项必跑 + 启动可见产物 | 🛑 |
| 4 | Real Verify → review-report | 质疑式 4 维验收 + DOC SYNC | ⚙ |
| 4.5 | Review → rot-scan | proactive-scan 10 项 | 🛑 |
| 5 | Rot Scan PASS → archive/done | 归档不可变 + 知识沉淀 | 🛑 |
| 6 | bug 单 → 修复 + CLOSED | e2e 先行 + 6 层排查 | 🛑 |
| 7 | 任一阶段 → project-health | 4 维度 + 优先级分级 | ⚙ |

**Stage Gate 通用 Hook(所有 stage)**:
- Stage 切换前 → 当前 stage 门禁 → 产出门禁报告 → **阻塞**(shell pre-stage.sh)
- Stage 启动 → 加载 stage skill + 解析 depends_on + 检查前置 → **阻塞**
- Stage 结束 → 更新状态卡 + 交接物 4 件套 → 非阻塞(shell post-stage.sh)

---

## §0.2 Guard 层 — TRAE IDE event hook + Shell hook

> 原 §4 Hook 生命周期(V11.4 迁移到本节)

Guard 层负责自动化检查,**不阻断工作流,但记录异常**(除显式标注"阻塞"外)。

### §0.2.1 TRAE IDE event Hook(5 种 event)

| Event | Hook 脚本 | 检查维度 | 阻断级别 |
|-------|----------|---------|:-------:|
| **SessionStart** | gitnexus-session-check.py + session-start.py | 6 层知识发现 + GitNexus 索引 freshness | ⚙ 提示 |
| **UserPromptSubmit** | complexity-guard.py | 复杂度 + GitNexus First + Article XVII secret | ⚙ 提示 |
| **PreToolUse** | doc-sync-gate.py + contract-gate.py | 写代码前门禁 | ⚙ 提示 |
| **PostToolUse** | spec-validate-hook.py + auto-test.py + drift-detect.py | 写代码后验证 | ⚙ 提示 |
| **Stop** | tasks-integrity.py + gitnexus-session-finalize.py | 任务完整性 + GitNexus 索引刷新 | ⚙ 提示 |

> **V11.4 降级说明**:TRAE IDE event hooks 由于依赖 IDE 对 exit code 的处理,**不承担硬阻断**,仅作辅助提示。真正的硬阻断由 **Git 钩子层**(husky pre-commit/pre-push + GitHub Actions CI)承担,见 §0.1.1。运行任何 stage 前必须先跑 `launch-guard.sh` 自校验,确认 Git 钩子层就绪,否则阻断。

> **GitNexus 双端触发时机(V11.4)**:`gitnexus-session-check.py`(SessionStart)**会话开始必跑一次**;`gitnexus-session-finalize.py`(Stop)**会话结束若工作区脏(agent 改过代码)才跑**,非编辑时实时触发。两端每次执行都写运行痕迹(`.gitnexus/last-run-check.json` / `last-run.json`),stdout 统一为 `[gitnexus]` 前缀 + key=value 格式,可直接 grep 验证;`hooks-fidelity.py` 校验痕迹存在 + 24h 内新鲜,过期/缺失计入 FAIL。

### §0.2.2 Shell Hook(Stage 切换专用)

| Hook | 触发时机 | 职责 | 阻断级别 |
|------|---------|------|:-------:|
| **pre-stage.sh** | Stage 切换前 | 当前 stage 门禁 + state-card-validator | 🛑 阻断 |
| **post-stage.sh** | Stage 结束后 | 更新状态卡 + 交接物 4 件套 | ⚙ 非阻塞 |
| **pre-accept.sh** | Stage 5 Accept 前 | 归档前检查 + spec-purge + knowledge-extract | 🛑 阻断 |

### §0.2.3 各 stage 完成 Hook(必阻塞)

| Stage | 完成时 Hook | 阻断级别 |
|:---:|------------|:-------:|
| -1 | 状态卡初始化 + 路由决策表 + Bug 录入判断 | 🛑 |
| 0 | 3 路并行探索 + GitNexus impact + 追问点 | 🛑 |
| 0.5 | 验收维度 → 测试用例映射(覆盖率门槛)| 🛑 |
| 1 | Enhanced Acceptance + INV ≥1 + clarify ≥2 轮 + spec-validate-hook.py | 🛑 |
| 1.5 | 双源兼容校验(设计稿 vs 代码原型)| 🛑 |
| 2 | contract-gate.py 验证四件套 + 测试骨架 | 🛑 |
| 3 | TDD GREEN + DRIFT CHECK + code-hygiene.py + auto-test.py + drift-detect.py | 🛑 |
| 3.5 | 5 项必跑 + 启动可见产物 + visual-content-check.py | 🛑 |
| 4 | 4 维评分 + 证据链 3 层 + DOC SYNC | 🛑 |
| 4.5 | proactive-scan.py 10 项 + self-diagnose.py | 🛑 |
| 5 | 归档前检查 + spec-purge.py + spec-knowledge-extract.py + pre-accept.sh | 🛑 |
| 6 | e2e 先行 FAIL + 6 层排查 + 全量回归 + bug 单 CLOSED | 🛑 |
| 7 | 4 维度检查 + 优先级分级(**非阻塞**,异步)| ⚙ |

### §0.2.4 hooks-fidelity 硬化要求(V12 沿用 V11.4)

```bash
# 加载协议后必跑(见 SKILL.md §0.5.2)
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .

# hooks-fidelity.py 检查项:
# 1. TRAE IDE event hooks 完整性(5 种 event 必注册)
# 2. Shell hooks 存在性(pre-stage.sh / post-stage.sh / pre-accept.sh)
# 3. Hook 脚本可执行性(权限 + 路径)
# 4. Git 钩子层就绪性(husky pre-commit/pre-push + CI v11-gate.yml)——缺失视为 FAIL(阻断)
```

**Hook 失败反应模式**:
- PASS → 继续
- FAIL → 🛑 阻断 + 5 字段阻塞报告 + 回退路径
- N/A → 标注理由 + 继续

**安装与验证**:
- 安装: `python scripts/install-hooks.py --project-root .`
- 验证: `python scripts/hooks-fidelity.py --project-root .`

---

## §0.3 Execution 层 — 13 stage 流水线

> 原 §0 骨架流程(V11.4 重命名)

> 🛑 以下流水线不可跳过。跳过任一 stage = 技能失效,必须回退重来。
> Bug Fix(Stage 6)与 Project Health(Stage 7)是独立支线,可由任一 stage 触发或并行。

**主链路(必走)**: -1 Intake → 0 Plan → 0.5 Test Plan → 1 Spec → 1.5 Prototype → 2 Contract → 3 Implement → 3.5 Real Verify → 4 Review → 4.5 Rot Scan → 5 Accept

**支线(独立)**: 6 Bug Fix(Intake 触发 / 任一 stage 阻塞触发)/ 7 Project Health(异步自检,可与任一 stage 并行)

**🛑 不可跳过**: -1 / 0 / 1 / 3.5 / 4.5

**回退路径**: [stage-interaction-protocol.md §四](stage-interaction-protocol.md)

**用户确认分级(V12 沿用 V10 传承)**:
- 完整 13 stage(Plan/Spec/Implement 必确认)
- 小任务流线化(≤6 Task + LOW + 无新 API → 无 Contract)
- Bug 快速链(Plan/Review lite-gate)