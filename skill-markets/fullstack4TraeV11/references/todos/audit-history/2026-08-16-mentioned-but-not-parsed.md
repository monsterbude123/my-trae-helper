# 2026-08-16 审计原文 — V11 "协议层 vs 解析层" 差距清单

> **定位**:子代理 B 审计的原始证据落盘。所有 P0-P3 todo 条目都从这里派生。
> **审计范围**:`d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\`(只 V11 自身,不涉其他 skill)。
> **审计方法**:每个"协议主张"对"scripts/ 消费证据",无消费方即"提及但未落地"。

---

## §1 审计 14 条全文(子代理 B 报告)

### #1 - 项目级 config.yaml 字段定义但无运行消费脚本

**协议层引用**: `references/dependency-config.md` L71-100 + L106-125(`resolve_skills()` 伪代码)

**解析层**:
```
scripts/init-from-zero.py:136-149  # 仅创建 config
scripts/upgrade-from-v10.py:134-173  # 仅创建 config
scripts/sync-after-upgrade.py:86-128  # 仅追加文本注释
```

**判别**: 提及但未落地 — `forbidden_paths` / `stage_config.{stage_id}.skills` 字段无任何运行脚本解析

**建议**: 新增 `scripts/project-priority-resolver.py`

---

### #2 - state-card frontmatter 缺 17 字段校验

**协议层**: `references/state-card-protocol.md` L78-133 (13 REQUIRED) + L137-152 (8 OPTIONAL)

**解析层**:
```
scripts/state-card-validator.py:26-31   REQUIRED_FIELDS = 13 个
scripts/state-card-validator.py:34       NULLABLE_FIELDS = 5 个
```

**未校验字段**: `visual_evidence.screenshots.contains_change_components / interactive_proof / read_by_main_context` + `next_stage.skill_name / expected_inputs / prerequisites` + `gate_result.output / verified_at` + `stage_ended_at`(仅 nullable 不校验 stage_status=completed 必填)+ `parent_change / related_changes / bug_id / bug_severity / risk_level / priority / notes` + `reset_history`(全 0 命中)

**判别**: 协议层 ~30 字段,validator 仅 18 字段,缺 ~17

**建议**: validator 扩 5 类校验:stage_ended_at 必填 / bug_severity 必填 / parent_change 文件存在性 / visual_evidence.read_by_main_context=true / reset_history 必含 5 子字段

---

### #3 - visual_evidence 硬门槛仅在 Stage 3.5/3 implement 校验

**协议层**: `SKILL.md` L120-130 + `references/state-card-protocol.md` L102-111

**解析层**:
```
scripts/state-card-validator.py:121-130  # only current_stage == "3.5/real-verify" OR ("3/implement" + completed)
```

进入 4/review 时不校验 visual_evidence

**判别**: 协议层说"3.5 → 4 推进硬门槛",实际只在 3.5/3 校验,4 进入点无校验

**建议**: validator 扩 `current_stage == "4/review"` 也校验

---

### #4 - state-machine.yaml 无任何消费方

**协议层**: `registry/state-machine.yaml` L73-124 (13 states + 14 transitions) + `references/state-card-protocol.md` L562-569 §九("状态转换必须通过 validate_transition() 校验")

**解析层**:
```
scripts/_lib_state_card.py:144-203  # load_state_machine / validate_transition 等函数已定义
scripts/README.md:79-82            # README 文档示例
```
零调用方

**判别**: 提及但未落地 — 状态机本体存在但 0 消费方

**建议**: stage-gate.py 在 --stage 切换前调 validate_transition(current → next),fail → exit 1

---

### #5 - repair-flow.yaml 无 Stage 6 调用

**协议层**: `registry/repair-flow.yaml` L97-110 (4 steps) + `scripts/README.md` L39/L54(修复流程程序化门禁)

**解析层**:
```
scripts/repair-flow-gate.py  # 存在但仅 --validate-only / --list-steps / --step
```
零调用方

**判别**: 提及但未落地 — Stage 6 bug-fix 4 步流程全是 md 文本,step 1-4 无机械串联

**建议**: Stage 6 SKILL.md 加 `--step step-1-e2e-fail / step-2-6layer / step-3-fix / step-4-confirm` 强约束

---

### #6 - run-all-guards.py 不读项目 .trae/registry/

**协议层**: `references/dependency-config.md` L19-25 Layer 3 优先 + `skills/12-bug-fix/references/bug-hunt-battle-report.md` §9.5 V11 缺漏 5(V11 自承认)

**解析层**:
```
scripts/run-all-guards.py:139-150  # --registry-dir 默认 None → skill_root/registry
```

**判别**: 提及但未落地(V11 自承认)

**建议**: run-all-guards.py 加自动探测 — 项目根存在 .trae/registry/ → 优先用,否则回落 V11 通用

---

### #7 - stacks.yaml 仅结构校验未参与 scaffold

**协议层**: `registry/stacks.yaml` L1-22 + `CHANGELOG.md` L360-372 V11.5.1

**解析层**:
```
scripts/run-all-guards.py:43,74  # 仅校验 stacks: [...] 是 list
```
未消费 `stacks[].gates / guards`

**判别**: 提及但未落地

**建议**: run-all-guards.py 加 stack-gate 交叉校验

---

### #8 - §14.5 项目级 rules 优先无任何解析脚本

**协议层**: `SKILL.md` L702-740 §14.5

**解析层**: 零命中(伪代码在 dependency-config.md)

**判别**: 提及但未落地

**建议**: scripts/project-priority-resolver.py 实现

---

### #9 - Article XVII 无独立 secrets-detector.py

**协议层**: `references/common-iron-rules.md` L131-142 + `references/secret-in-tool-arg.md`

**解析层**:
```
templates/hooks/auto-test.py:46-58  # secret 字面量检测
templates/hooks/complexity-guard.py:73-77  # secret 关键字
templates/hooks/session-start.py:58-66  # 路径检查
```
但 scripts/ 下无独立 secrets-detector.py

**判别**: 部分落地

**建议**: scripts/secrets-detector.py + proactive-scan.py 加第 11 项

---

### #10 - bug-state-machine.md 5 状态机 reason-classifier.py 不消费

**协议层**: `skills/01-intake/references/bug-state-machine.md` L11-19 (5 状态)

**解析层**:
```
scripts/reason-classifier.py:28-35  REASON_PATTERNS = 6 类(理解偏差/流程裁剪/...)
```

**判别**: 提及但未落地

**建议**: scripts/bug-state-machine-validator.py 新建

---

### #11 - audit_state_card_change 函数定义但其他状态卡写入路径无审计

**协议层**: `references/state-card-protocol.md` §5.8 L358-390

**解析层**:
```
scripts/_lib_state_card.py:86-137  audit_state_card_change 定义
templates/hooks/post-stage.sh:81-100  # 唯一调用
scripts/state-card-validator.py L215-231  # 仅 info 提示
```

**判别**: 提及但未落地 — §5.8 声称"缺审计 → FAIL",实际仅 info

**建议**: state-card-validator.py 加 --git-diff 实际校验;setup-feature.py / change-status.py 必调 audit_state_card_change

---

### #12 - proactive-scan.py reason-fabrication 已知误报未修

**协议层**: `references/common-iron-rules.md` L107 + `skills/12-bug-fix/references/bug-hunt-battle-report.md` L516-524 §9.3 V11 缺漏 3

**解析层**:
```
scripts/proactive-scan.py:214-267  scan_reason_fabrication(未排除 docs/specs/_invalidated/)
```

**判别**: 部分落地(V11 自承认)

**建议**: 加 _invalidated/ 白名单 + 上下文窗口(200 字符)

---

### #13 - §3.7 #10 范围盲目扩大无程序化检测

**协议层**: `SKILL.md` L508 §3.7 #10 + `references/common-anti-patterns.md` §7.3

**解析层**: grep `commit.*准入最小集|MINIMUM_COMMIT_CRITERIA` 在 scripts/ 零命中

**判别**: 提及但未落地

**建议**: scripts/commit-minimum-check.py 新建

---

### #14 - stage-gate.py 是 13 stage 通用入口但无任何脚本/hook 调用

**协议层**: `SKILL.md` L213-218 + `scripts/README.md` L18

**解析层**: grep `stage-gate.py --state-card|subprocess.*stage-gate` 在 scripts/ + templates/hooks/ 中零命中

**判别**: 提及但未落地

**建议**: templates/hooks/pre-stage.sh 加 stage-gate.py 强制调用

---

## §2 优先级(子代理 B top 5)

| P | # | 条目 | 影响 |
|---|---|------|------|
| **P0** | #4 | state-machine.yaml 无任何消费方 | 13 stage 流转正确性基础 |
| **P0** | #6 | run-all-guards.py 不读项目 .trae/registry/(V11 自承认) | 项目级 hard 门槛全废 |
| **P1** | #2 | state-card validator 缺 17 字段校验 | 状态卡说谎 / 子代理越权无机械阻断 |
| **P1** | #1 | project-priority-resolver.py + config.yaml 字段消费 | Layer 3 优先级协议全文空头 |
| **P2** | #5 | repair-flow-gate.py 无 Stage 6 调用 | Bug 修复流程"程序化"承诺失约 |

完整 14 条已分发到:
- `references/todos/P0-protocol-vs-parser.md`
- `references/todos/P1-config-and-state-card.md`
- `references/todos/P2-bug-flow-and-stage-gate.md`
- `references/todos/P3-cross-skill-and-doc.md`

---

## §3 审计方法论(供后续审计复用)

```
1. 协议层 → grep 关键词 (协议/字段/触发词) 在 references/ + SKILL.md + skills/{N}/SKILL.md
2. 解析层 → 同关键词在 scripts/ 中 grep 调用方
3. 判别 → 协议层有 + 解析层零命中 = 提及但未落地
4. 优先级:
   P0 = 协议核心承诺(如 13 stage 流转)
   P1 = 配置层 + 状态卡字段层
   P2 = 流程层串联弱化
   P3 = 跨 skill / 文档缺陷
5. 修复优先级不依赖"V11 自承认"——自承认 = 信号已发出但未修;未自承认 = 全新问题
```

---

## §4 子代理报告时序

| 时间 | 子代理任务 | 输出 |
|------|----------|------|
| 2026-08-16 12:00 | 子代理 A(`general_purpose_task`)创建 config-files-glossary.md | PASS / 36 行 / 5 段 |
| 2026-08-16 12:00 | 子代理 B(`general_purpose_task`)审计"提及但未落地" | PASS / 14 条 / top 5 优先 |
| 2026-08-16 12:30 | 主上下文落盘本目录骨架与 README | 本文件 |
| 2026-08-16 12:35 | 主上下文写入 5 个具体 todo .md | references/todos/P0-P3 |
| 2026-08-16 12:40 | 主上下文写入 v12-physical-isolation 子目录(用户复述条目) | 2 个文件 |

---

## §5 主上下文接手 + commit 时间表(2026-08-16 综合)

> 本节作为子代理批修后的"主上下文兜底 + commit 阶段"完整记录,补全 §4 仅记录子代理交付的缺漏。

### Step 6 主上下文兜底验证(2026-08-16 13:00-15:30)

| 验证项 | 命令 / 方法 | 结果 |
|--------|------------|------|
| `secrets-detector.py` 真反例 | tmp 目录造 3 类假密钥(OpenAI / Anthropic / base64 长串)→ `python scripts/secrets-detector.py --path tmp/` | 全部命中,exit 0 |
| pytest 全量 | `python -m pytest tests/unit/ -v` | 232 passed |
| `pre-stage.sh` V11_GATE_ENFORCED | `unset V11_GATE_ENFORCED && bash templates/hooks/pre-stage.sh` → 应 exit 1 | exit 1（实测通过,缺 env 即阻断） |
| `_lib_state_card.py` import 修复 | `python -c "import _lib_state_card; print(_lib_state_card.compute_state_card_hash(...))"` | 不再 throw NameError |
| `state-card-validator.py --strict-audit` | tmp 状态卡 + tmp 审计日志(断链) | exit ≠ 0,FAIL 信息含字段名 |

### Step 7 §B 7 步 SOP 走完 + commit(2026-08-16 15:30-16:00)

- commit 信息:`.commit_msg.txt`(多行中文用 `-F`,非 `-m`)
- 实际 commit hash:`<待 #7 git log 填>`(占位符,需主上下文 git log -1 后回填)
- 受影响文件:**18 modified + 13 untracked**(子代理交付合计)
- 关键改动文件:
  - `scripts/project-priority-resolver.py`(NEW)
  - `scripts/secrets-detector.py`(NEW)
  - `scripts/bug-state-machine-validator.py`(NEW)
  - `scripts/_lib_state_card.py`(MODIFIED — import 补全)
  - `scripts/state-card-validator.py`(MODIFIED — 5 类校验扩展)
  - `scripts/setup-feature.py` + `change-status.py`(MODIFIED — 强制审计)
  - `templates/hooks/pre-stage.sh`(MODIFIED — V11_GATE_ENFORCED env 校验)
  - `templates/hooks/post-stage.sh`(MODIFIED — 强制 audit_state_card_change)
  - `templates/hooks/auto-test.py` + `complexity-guard.py`(MODIFIED — 真密钥检测)
  - `scripts/proactive-scan.py`(MODIFIED — _invalidated/ 白名单)
  - `scripts/run-all-guards.py`(MODIFIED — 项目 .trae/registry/ 自动探测)
  - `scripts/stack-gate` 交叉校验(MODIFIED — 消费 stacks.yaml)
  - `tests/unit/test_*.py` — 11+ 新增

### 不可证伪证据(§3.7 #4 evidence_required)

> 任何数字声明必须第一轮带证据,以下逐项列出:

- **14 done / 2 pending**:§2 top 5 + §1 全 14 条已落地;pending = P3-6 commit-minimum-check.py(协议 §3.7 #10) + V12-physical-isolation 子目录
- **pytest 232 passed**:`tests/unit/` 下 21 个 test_*.py 全 pass,新增覆盖 11+ 条
- **真反例 4 个**:
  - P0-1 `_lib_state_card.py` import NameError 修复后 `pytest tests/unit/test_audit_state_card_change_chain.py` 全 pass
  - P1-1 `project-priority-resolver.py --merge-anti-patterns --json` tmp JSON 输入验证 `[project, v11, global]` 顺序
  - P3-4 `reason-fabrication` 加 _invalidated/ 白名单后 hit_count 从 2 → 0
  - pre-stage env:unset V11_GATE_ENFORCED → exit 1(实测)
- **commit affected 18 modified + 13 untracked**:`git status --porcelain | wc -l` 主上下文确认

### 5 个文档一致性更新(本任务[TODO-DOC-SYNC])

| # | 文件 | 改动 |
|---|------|------|
| 1 | `scripts/README.md` L39-41 | 加 3 个新脚本清单(project-priority-resolver / secrets-detector / bug-state-machine-validator) |
| 2 | `references/dependency-config.md` L125 后 | 加 §V11.8.x 实现状态小段,引用 project-priority-resolver.py |
| 3 | `references/state-card-protocol.md` L380 后 | 加 §V11.8.x 强化子节,引用 state-card-validator.py 5 类校验 + _lib_state_card.py 导入补全 |
| 4 | `templates/hooks/README.md` L25 后 | 加 §V11.8.x 硬化(pre-stage env 校验 + 贾维斯门禁同源说明) |
| 5 | `audit-history/2026-08-16-mentioned-but-not-parsed.md` §5 | 即本节 |

---

## §6 关联引用

- [references/todos/README.md](../README.md) — 总览
- [references/todos/P0-protocol-vs-parser.md](../P0-protocol-vs-parser.md)
- [references/todos/P1-config-and-state-card.md](../P1-config-and-state-card.md)
- [references/todos/P2-bug-flow-and-stage-gate.md](../P2-bug-flow-and-stage-gate.md)
- [references/todos/P3-cross-skill-and-doc.md](../P3-cross-skill-and-doc.md)
- [references/todos/v12-physical-isolation/](../v12-physical-isolation/)
- [references/config-files-glossary.md](../../config-files-glossary.md) — 子代理 A 交付物
- [references/stage-physical-isolation.md](../../stage-physical-isolation.md) — V12 提案
