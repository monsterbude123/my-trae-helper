# P3 — 跨 skill 文档 / 协议层弱引用

> 状态:P3 = 影响小 / 文档缺陷为主。本文件 6 条。

---

## P3-1 — stacks.yaml 技术栈注册表未参与 scaffold 门禁映射

```yaml
---
id: AUDIT-#7
title: run-all-guards.py 加 stack-gate 交叉校验
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: registry/stacks.yaml L1-22(stacks[0].gates / guards)
              CHANGELOG.md L360-372 V11.5.1
parser_ref: scripts/run-all-guards.py L43/L74(stacks 仅做 YAML 结构合法校验)
fix_path: scripts/run-all-guards.py 加 stack-gate 交叉校验
resolved_at: 2026-08-16
resolved_by: V11 子代理 B (P3 批修)
evidence:
  - scripts/run-all-guards.py 新增 validate_stack() 函数 + gates_ids/guards_ids 收集 + main() 3.5 段 stack 校验循环
  - tests/unit/test_stacks_gate_cross_check.py 新建,7 用例 PASS
  - 真反例:stacks[node-bad-test].gates=["nonexistent-stage-X"] → CLI exit 1 + "未登记 gate" 信息
  - 真反例:stacks[node-bad-test].guards=["ghost-guard-zzz"] → CLI exit 1 + "未登记 guard" 信息
---
```

协议声明"nodejs 必须含 stage-spec + stage-real-verify gates",但 run-all-guards.py 只校验 `stacks: [...]` 是 list,不解析每个 stack 的 gates/guards 字段。

修复:`run-all-guards.py` 加 stack-gate 校验 — `stacks[].gates` 必须在 `gates.yaml` 登记;`stacks[].guards` 必须在 `guards.yaml` 登记。

---

## P3-2 — Article XVII Secret Redaction 无独立 secrets-detector.py

```yaml
---
id: AUDIT-#9
title: scripts/secrets-detector.py 新建 + proactive-scan.py 加第 11 项
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: references/common-iron-rules.md L131-142(Article XVII 17.1-17.6)
              references/secret-in-tool-arg.md
parser_ref: templates/hooks/auto-test.py + complexity-guard.py + session-start.py(3 个 hook 各做局部检测,无独立 scripts/)
fix_path: scripts/secrets-detector.py 新建 + proactive-scan.py 第 11 项
resolved_at: 2026-08-16
resolved_by: V11 子代理 B (P3 批修)
evidence:
  - scripts/secrets-detector.py 新建,接口: --file / --project-root / --json
  - 检测 pattern: AWS / OpenAI / GitHub / Generic credential / Bearer / PEM private key / JWT / 中国手机号 / 身份证号 / 邮箱 PII (10 类)
  - 占位符排除: password="xxx" / "REDACTED" / "${VAR}" 等不命中
  - tests/unit/test_secrets_detector.py 新建,14 用例 PASS
  - 真反例: tmp 造 leaked.txt 含 AKIA + Bearer + password=secret123abc → CLI exit 1 + hit_count ≥ 3
---
```

3 个 hook 模板做 secret 检测,但无独立可被 proactive-scan / state-card-validator 调用的 secrets-detector。

修复:scripts/secrets-detector.py 提供 `--file / --project-root` 接口;proactive-scan.py 加 `secret-redaction` 第 11 项扫描;commit 前必跑。

---

## P3-3 — proactive-scan.py reason-fabrication 已知误报未修

```yaml
---
id: AUDIT-#12
title: proactive-scan.py 修 docs/specs/_invalidated/ + 上下文窗口
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: references/common-iron-rules.md L107(Article XIV.2 列出 10 项含 reason-fabrication)
              skills/12-bug-fix/references/bug-hunt-battle-report.md L516-524 §9.3 V11 缺漏 3
parser_ref: scripts/proactive-scan.py L214-267(scan_reason_fabrication 函数存在但未排除 docs/specs/_invalidated/)
fix_path: scripts/proactive-scan.py 加 _invalidated/ 白名单 + 检测上下文窗口(200 字符)
resolved_at: 2026-08-16
resolved_by: V11 子代理 B (P3 批修)
evidence:
  - scripts/proactive-scan.py scan_reason_fabrication 改造: 加 docs/specs/_invalidated 路径白名单 (parts + path str 双重防漏)
  - 上下文窗口: 命中禁词时检查前后 200 字符,含"反例/误报说明/V11 缺漏/蒸馏/V11 实战/V11 自承认/V11.2.2 NEW"任一即跳过
  - filename_whitelist 增补 8 项(bug-hunt-battle-report / state-card-protocol / trap-instructions / agent-error-diagnosis / skill-optimization-method / unread-rule-pass / audit-history / common-iron-rules)
  - tests/unit/test_proactive_scan_reason_fabrication.py 新建,5 用例 PASS
  - 真反例验证: 把 bug-hunt-battle-report.md 复制到 docs/reports/rot-scan-2026-08-16.md → 扫描返回 ok=True, msg="未发现抽象理由"
---
```

V11 自承认缺漏 3,但未修。报告内"reason-fabrication 误报说明段"引用禁词本身会被误判。

修复:1) 加 `docs/specs/_invalidated/` 路径白名单;2) 检测时增加前后 200 字符上下文判断(出现"反例 / 误报说明 / V11 缺漏"标记时跳过)。

---

## P3-4 — bug-state-machine.md 5 状态机 reason-classifier.py 不消费

```yaml
---
id: AUDIT-#10
title: 新增 bug-state-machine-validator.py 校验 bug 单 status 流转
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: skills/01-intake/references/bug-state-machine.md L11-19(5 状态)
parser_ref: scripts/reason-classifier.py L28-35(REASON_PATTERNS = 6 类,不消费 bug 状态机)
fix_path: scripts/bug-state-machine-validator.py 新建
resolved_at: 2026-08-16
resolved_by: V11 子代理 B (P3 批修)
evidence:
  - scripts/bug-state-machine-validator.py 新建,接口: --bug-state-card / --bug-card / --state-machine / --json
  - 5 状态: OPEN / IN_PROGRESS / CLOSED / BLOCKED / SKIPPED (3 主态 + 2 回退态)
  - 状态转换矩阵: 8 条合法转换(bug-state-machine.md L28-38 + V11 实战扩展)
  - tests/unit/test_bug_state_machine_validator.py 新建,13 用例 PASS
  - 真反例 1: status="ILLEGAL_STATE" → CLI exit 1 + "ILLEGAL_STATE 非法" 信息
  - 真反例 2: status_history OPEN → CLOSED (跳过 IN_PROGRESS) → FAIL 含"非法转换 OPEN → CLOSED"
  - 真反例 3: status_history CLOSED → IN_PROGRESS → FAIL 含"CLOSED → IN_PROGRESS 非法"
---
```

`bug-state-machine.md` 定义 5 状态 + 状态转换矩阵,但 `reason-classifier.py` 完全无关。

修复:scripts/bug-state-machine-validator.py 校验 bug 单 `status` 字段必遵循 5 状态流转;Stage 6 SKILL.md 加"必跑此脚本"硬步骤。

---

## P3-5 — audit_state_card_change 函数未被所有写路径覆盖

```yaml
---
id: AUDIT-#11
title: setup-feature.py + change-status.py 必调 audit_state_card_change
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: references/state-card-protocol.md §5.8 L358-390(子代理禁止直写 5 字段)
parser_ref: scripts/_lib_state_card.py L86-137(audit_state_card_change 已定义)
             + templates/hooks/post-stage.sh L81-100(仅一处调用)
             + scripts/state-card-validator.py L215-231(仅 info 提示)
fix_path: scripts/setup-feature.py + change-status.py 加 audit_state_card_change() 调用
completed_at: 2026-08-16T
evidence: scripts/setup-feature.py L130-150 + change-status.py L45-70/L108-113 + state-card-validator.py L285-336 --strict-audit + _lib_state_card.py L1-11 补 hashlib/json/os/datetime 导入(原有函数因 import 缺失一直不可用,本次修复);tests/unit/test_audit_state_card_change_chain.py 4 用例 PASS
---
```

`audit_state_card_change()` 函数已定义,但只被 post-stage.sh 调用。所有其他状态卡写入路径(setup-feature / change-status / agent Edit)无审计。

修复:state-card-validator.py 加 `--git-diff` 检测状态卡字段变更是否来自主上下文 Edit(真正做 git diff 实际校验,不仅 info 提示);setup-feature.py / change-status.py 入口必调 audit_state_card_change()。

---

## P3-6 — §3.7 #10 范围盲目扩大反例无程序化检测

```yaml
---
id: AUDIT-#13
title: scripts/commit-minimum-check.py 实现 commit 准入最小集
status: done
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: SKILL.md L508 §3.7 #10 commit 准入最小集 ≠ 全量验收
              references/common-anti-patterns.md §7.3
parser_ref: grep `commit.*准入最小集\|MINIMUM_COMMIT_CRITERIA` 在 scripts/ 中零命中
fix_path: scripts/commit-minimum-check.py 新建
resolved_at: 2026-08-16T22:11
resolved_by: V11 子代理 + 主上下文兜底验证
evidence: archive/done/2026-08-16-batch-repair-2/P3-6-commit-minimum.md(本条目抽出独立归档,16 用例 PASS + Windows cp1252 兜底);V11.8.7 followup `02d0d90` 新增第 5 项 secret scan
---
```

§3.7 #10 反例只在 md 描述,scripts/ 无任何程序化检测(主上下文自觉)。

修复:scripts/commit-minimum-check.py 校验 `lint pass + 关键 5 路由 spot-check 存在 + admin 探针 200`;Stage 3.5/4.5 默认异步由本脚本显式声明。
