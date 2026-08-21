---
name: ai-testmate
description: |
 AI 端到端测试助理。读产品文档 + 测试计划 → 在指定工作空间新建测试项目 →
 并行执行 API(requests)+ UI(playwright)端到端测试 → 输出 HTML/MD/JUnit 报告 →
 通过禅道登记测试单 + 同步 Bug → 飞书群推送结果。
 触发词:ai testmate / 跑 e2e / 新建测试项目 <app> / 出测试报告 / 同步 Bug 到禅道 / 禅道登记测试单 / UI API 混合测试。
version: 1.0.0
changelog:
  - version: 1.0.0
    date: 2026-08-20
    note: 独立专精测试工程师 Skill 首版。借鉴 fullstack4TraeV11 三层骨架(不替代)。
requires:
  mcp: [zentao, lark]
---

# ai-testmate — AI 端到端测试助理

## §0 定位 — 独立专精测试工程师

```
ai-testmate = 独立 Skill
  ├─ 借鉴:fullstack4TraeV11 三层骨架 + 协议程序化解析思路
  ├─ 调用:zentao-cli(只读 + 唯一写权收敛 reporter)
  └─ 调用:lark MCP(报告推送)
  ❌ 不替代 V11 / zentao-cli / lark MCP
```

**与其他 skill 的关系**:

| Skill | 关系 |
|-------|------|
| `fullstack4TraeV11` | 借鉴三层骨架;不调其 13 stage / qa-loop / guard-smith |
| `zentao-cli` | 调用其命令;不重写命令实现;写权仅 reporter |
| `lark MCP` | 调用 `lark_im_message send`;不直连 webhook URL |

---

## §1 铁律(8 条)

| # | 铁律 | 关联反例 |
|:-:|------|----------|
| 1 | 工作空间强约束 — 测试物料只能写在 `<workspace>/tests/<app>/` 与 `<workspace>/reports/<timestamp>/` | AP-1 |
| 2 | .env 缺失即停 — `<project>/.agents/.env` 缺任一必填变量,credential-keeper 直接退出 | AP-6 |
| 3 | 禅道写权收敛 — 只有 reporter 可调 `zentao bug create` / `zentao testtask create` | AP-3 |
| 4 | 飞书走 lark MCP — 禁止直连 webhook URL | AP-4 |
| 5 | 跨平台探测 — 复用 `scripts/detect-python.sh`,禁硬编码 Python 路径 | AP-6 |
| 6 | 反假通过 — 三态自检(PASS / BLOCK / 边界)必跑 | AGENTS.md §2.4 |
| 7 | 报告时间戳目录 — `<workspace>/reports/YYYYMMDD_HHMMSS/` 强制,禁覆盖 | AP-7 |
| 8 | 截图脱敏 — ui-tester 必 mask 密码字段后再截图 | AP-5 |

---

## §2 流水线(6 步)

```
[planner] ─→ 读 PRD + 禅道需求/用例 ─→ test-cases.yaml
                ↓
[credential-keeper] ─→ 读 <project>/.agents/.env ─→ env dict
                ↓
       ┌────────┴────────┐
       ↓                 ↓
[api-tester]      [ui-tester]   (并行异步)
   ↓ API 用例        ↓ UI 用例
api-report.json  ui-report.json + screenshots/
                ↓
[reporter] ─→ 聚合 + 4 份报告 + 禅道回写 + 飞书推送
```

详见 [references/workflow.md](references/workflow.md)。

---

## §3 禅道集成时机(摘要)

| 时机 | 角色 | 动作 | 反例 |
|------|------|------|------|
| planner 启动 | planner | `zentao product story list`(只读) | - |
| planner 启动 | planner | `zentao testcase list`(只读) | - |
| reporter 收尾 | reporter | `zentao testtask create`(写) | AP-3 |
| reporter 收尾 | reporter | `zentao bug create`(写) | AP-3 |

详见 [references/zentao-integration.md](references/zentao-integration.md)。

---

## §4 `.env` 变量规范(摘要)

```bash
ZENTAO_PRODUCT_ID=1               # 必填
LARK_WEBHOOK_CHAT_ID=oc_xxxxx     # 必填
TEST_USER_A_EMAIL=xxx@yyy.com     # 必填
TEST_USER_A_PASSWORD=__FROM_VAULT__  # 必填(vault 占位)
REPORT_PUSH_USERS=ou_aaa,ou_bbb   # 推荐
ZENTAO_TESTTASK_AUTO_CREATE=true  # 推荐
```

详见 [references/env-config-spec.md](references/env-config-spec.md)。

---

## §5 报告格式(4 份)

| 文件 | 用途 | 路径 |
|------|------|------|
| `report.html` | 可视化 + 截图对比 | `<workspace>/reports/<ts>/` |
| `report.md` | 可读(MR/邮件附件) | 同上 |
| `junit.xml` | CI 对接(GitHub Actions) | 同上 |
| `manifest.json` | 禅道回写元数据 | 同上 |

详见 [references/report-templates.md](references/report-templates.md)。

---

## §6 三层架构(借鉴 V11,自洽)

| 层 | 本 skill 实现 |
|---|--------------|
| **Execution** | 5 agent 流水线(planner → credential-keeper → [api-tester ∥ ui-tester] → reporter) |
| **Guard** | `scripts/ai-testmate-guard.py`(项目侧,待 guard-smith 委派)+ `scripts/publish-protocol.py`(协议覆盖) |
| **Gate** | 仅挂 L1 pre-commit 结构守卫(`.husky/ai-testmate-gate`,待 guard-smith 委派) |

---

## §7 Gate 自验收(强制)

按 AGENTS.md §2.4:

```bash
# 1. 真反例跑 BLOCK 态(必 exit ≠ 0)
python scripts/ai-testmate-guard.py --test-block

# 2. 真合规跑 PASS 态(必 exit 0)
python scripts/ai-testmate-guard.py --test-pass

# 3. 边界样本跑不误报
python scripts/ai-testmate-guard.py --test-edge

# 4. 协议覆盖
python scripts/publish-protocol.py
```

三态全过 + 协议 PASS = 任务完成。

---

## §8 反模式(雷清单)

| # | 雷 | 检测命令 |
|:-:|----|----------|
| 1 | 工作空间硬编码 | `grep '/workspace/' scripts/*.sh` |
| 2 | 账号池泄露 | `grep -r 'TEST_USER_' skill-markets/ai-testmate/ \| grep -v .env.example` |
| 3 | 禅道写权越界 | `grep 'zentao bug create' agents/*.md`(仅 reporter.md 命中) |
| 4 | 飞书直连 webhook | `grep 'hooks.lark\|webhook.*http' scripts/` |
| 5 | 截图脱敏漏 | `grep 'mask\|redact' agents/ui-tester.md` |
| 6 | 跨平台硬编码 | `grep '/mnt/c/\|/usr/bin/python' scripts/` |
| 7 | 报告无时间戳 | `grep 'YYYYMMDD\|%Y%m%d' scripts/run-test.sh` |
| 8 | SKILL.md 超 350 行 | `wc -l SKILL.md` |

详见 [references/ai-testmate-protocol.md §4](references/ai-testmate-protocol.md)。

---

## §9 目录结构

```
skill-markets/ai-testmate/
├── SKILL.md                          # 本文件
├── agents/                           # 5 角色
│   ├── planner.md
│   ├── credential-keeper.md
│   ├── api-tester.md
│   ├── ui-tester.md
│   └── reporter.md
├── references/                       # 8 份
│   ├── ai-testmate-protocol.md       # 协议先行(本 skill 顶级)
│   ├── workflow.md
│   ├── zentao-integration.md
│   ├── env-config-spec.md
│   ├── lark-webhook-spec.md
│   ├── pytest-patterns.md
│   ├── playwright-patterns.md
│   ├── report-templates.md
│   └── trap-instructions.yaml
├── scripts/                          # 4 份
│   ├── publish-protocol.py           # 协议覆盖自检
│   ├── ai-testmate-guard.py          # 结构守卫
│   ├── run-test.sh                    # 一键入口
│   └── detect-python.sh              # 跨平台 Python 探测(共享)
├── tests/unit/                       # ≥ 3 用例
├── todos/                            # task.md + checklist.md
└── .env.example                      # 变量名模板
```

---

## §10 蒸馏 + 留置

**蒸馏**:
- 2026-08-20 用户提出 ai-testmate 需求 → 蒸馏出独立 Skill(混合 UI/API + 4 份报告 + 禅道/lark 双 MCP)

**留置**(用户明示本次不做):
- registry/skills.yaml 注册(需 guard-smith 委派)
- scripts/ai-testmate-guard.py(项目侧,需 guard-smith 委派)
- .husky/ai-testmate-gate(需 guard-smith 委派)
- AGENTS.md §7 + CHANGELOG + SECURITY-MAP + catalog(独立完成原则,本次不动)
```