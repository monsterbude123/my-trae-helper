# ai-testmate Skill — Checklist(全维度自检)

> **依据**:V11 §2.3 全维度自检 checklist + AGENTS.md §2.4 Gate 自验收
> **使用**:每个文件落地后勾选,任务结束前全量勾完

---

## §1 6 维度同步检查(V11 §2.3)

| # | 维度 | 检查项 | 状态 |
|:-:|------|--------|:---:|
| 1 | SKILL.md 本体 | `SKILL.md` frontmatter(name + description + version + requires.mcp) | ☐ |
| 2 | references/ | 8 份齐全(protocol/workflow/zentao-integration/env-config-spec/lark-webhook-spec/pytest-patterns/playwright-patterns/report-templates/trap-instructions) | ☐ |
| 3 | agents/ | 5 角色齐全(planner/credential-keeper/api-tester/ui-tester/reporter) | ☐ |
| 4 | scripts/ | publish-protocol.py + run-test.sh + detect-python.sh(共享)+ ai-testmate-guard.py | ☐ |
| 5 | guard | 三态自检 PASS(脚本 + 真反例 + 边界) | ☐ |
| 6 | 其他引用 | pytest ≥ 3 用例 + .env.example + tests/unit/ | ☐ |

---

## §2 vibe-coding-standards 行数弹性(v2.5)

| 文件 | 弹性 | 实测 | 状态 |
|------|:---:|:---:|:---:|
| SKILL.md | ≤350 行 | _ | ☐ |
| agents/*.md | ≤200 行 | _ | ☐ |
| references/*.md | ≤250 行 | _ | ☐ |

> 行数超阈 = 🛑 REJECT,按 V11 §0.5 瘦身(指针化 references/)

---

## §3 雷清单逐条(本 skill §3)

| 雷 | 检测命令 | 期望 | 状态 |
|----|----------|:----:|:---:|
| 1 工作空间硬编码 | `grep '/workspace/' scripts/*.sh` | 空 | ☐ |
| 2 账号池泄露 | `grep -r 'TEST_USER_' skill-markets/ai-testmate/ \| grep -v .env.example` | 空 | ☐ |
| 3 禅道写权越界 | `grep 'zentao bug create' agents/*.md` | 仅 reporter.md | ☐ |
| 4 飞书直连 webhook | `grep 'hooks.lark\\|webhook' scripts/` | 空(必须走 lark MCP) | ☐ |
| 5 截图脱敏漏做 | `grep 'mask\\|redact' agents/ui-tester.md` | 非空 | ☐ |
| 6 跨平台 Python 硬编码 | `grep '/mnt/c/\\|/usr/bin/python' scripts/` | 空 | ☐ |
| 7 报告时间戳 | `grep 'YYYYMMDD\\|%Y%m%d' scripts/run-test.sh` | 非空 | ☐ |
| 8 SKILL.md 行数 | `wc -l SKILL.md` | ≤350 | ☐ |

---

## §4 pytest 用例 ≥ 3(必填/推荐/反例各 1)

| 用例类型 | 用例名 | 覆盖反例 | 状态 |
|---------|--------|---------|:---:|
| 必填 | test_required_variables_missing_blocks_run | AP-6(.env 缺失即停) | ☐ |
| 推荐 | test_zentao_write_authority_converged_to_reporter | AP-3(写权越界) | ☐ |
| 反例 | test_lark_webhook_must_use_mcp_not_direct_url | AP-4(直连 webhook) | ☐ |

> pytest 结果:`pytest tests/unit/test_ai_testmate.py -v` 期望 ≥ 3 passed

---

## §5 三态自检(AGENTS.md §2.4)

| 状态 | 样本 | 期望 | 状态 |
|------|------|:----:|:---:|
| PASS | 正常 .env + 正常 agent 文件 | exit 0 | ☐ |
| BLOCK | .env 缺失必填变量 | exit ≠ 0 + 报错信息 | ☐ |
| 边界 | zentao 写权越界到 planner | exit ≠ 0 + 定位 planner | ☐ |

---

## §6 publish-protocol.py 协议覆盖

| 检查项 | 命令 | 状态 |
|--------|------|:---:|
| 协议覆盖 8 份 references | `python scripts/publish-protocol.py` | ☐ |
| 必备章节齐全 | 每份必带 §1 + §2 + 反例指针 | ☐ |
| SKILL frontmatter 完整 | name + description + version + requires | ☐ |

---

## §7 蒸馏完整性(任务结束前)

- [ ] todos/task.md §1 11 步全部状态 ✅
- [ ] todos/checklist.md 全部勾完
- [ ] pytest ≥ 3 用例 PASS
- [ ] 三态自检 PASS/BLOCK/边界 全跑
- [ ] publish-protocol.py PASS
- [ ] logs/agent-hints.jsonl 记录本次踩雷(若有)
- [ ] §4 Batch B 留置事项明确告知用户

---

## §8 完成签名

- 主代理身份:`todo-tracker + skill-creator`
- 完成日期:____
- pytest 结果:____
- 自验收 3 步:____
- Batch B 留置:见 task.md §4
```