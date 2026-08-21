# bug-storage — 本地 bug 生命周期(禅道降级路径)

> v1.1 增量。当 `.env` 缺 `ZENTAO_PRODUCT_ID` 或 zentao-cli 不可用时,reporter 自动降级到本地 markdown bug 单。

---

## §1 触发降级条件(满足任一)

```
1. .env 缺 ZENTAO_PRODUCT_ID
2. .env 缺 ZENTAO_TESTTASK_AUTO_CREATE=true(默认 true,显式关掉也算降级)
3. zentao-cli 探测失败(CommandNotFound / 连接超时)
4. 用户环境无外网(开发机纯本地)
```

降级触发后 reporter 不写 zentao,**全部 bug 单写到本地 markdown**。

---

## §2 bug 单 frontmatter(7 字段,V11 简化版)

路径:`<ws>/<app-test>/docs/bugs/<YYYYMMDD>-<id>.md`

```markdown
---
id: BUG-001
title: 用户登录失败(密码错误期望 401,实际 200)
status: OPEN            # OPEN / FIXED / CLOSED
created: 2026-08-20T17:55:00
priority: P0            # P0 / P1 / P2
severity: high          # high / medium / low
source: qa-found        # 测试 agent 自动来源(本 skill 唯一值)
case_id: TC-001          # 关联 test-cases.yaml 用例 ID
report_run: reports/20260820_175500/  # 关联报告目录
---

## 复现步骤(Steps)
1. /login
2. 输入错误密码 test_wrong
3. 点击登录

## 预期(Expected)
HTTP 401 + 错误提示"账号或密码错误"

## 实际(Actual)
HTTP 200 + 跳转 /dashboard

## 截图与证据(Evidence)
- 截图:screenshots/TC-001-failure.png
- 报告:reports/20260820_175500/report.md

## 根因建议(Reporter Suggest)
trap-instructions.yaml 匹配:rule_id=unauthorized
"检查 TEST_USER_* 凭据是否过期"

## 状态变更记录(Status Log)
- 2026-08-20T17:55:00 OPEN(reporter 自动建单)
```

**字段说明**(7 字段):
1. `id`:BUG-NNN 序号
2. `title`:一句话描述
3. `status`:OPEN / FIXED / CLOSED(3 选 1)
4. `created`:ISO 时间戳
5. `priority` + `severity`:双标签,priority 来自用例 P 级,severity 由 reporter 判定
6. `source`:固定 `qa-found`(测试 agent 自动)
7. `case_id` + `report_run`:反向追溯链

---

## §3 状态转换(3 状态)

```
OPEN ──→ FIXED ──→ CLOSED
  │                  ↑
  └───(回退)──────┘ (开发流人工)
```

| From → To | 触发 | 谁执行 |
|-----------|------|--------|
| (无) → OPEN | reporter 失败用例自动建 | reporter(本 skill) |
| OPEN → FIXED | 开发流修复完成 + 复测通过 | **开发流人工**(reporter 不自动) |
| FIXED → CLOSED | 三方确认(代码提测 + 测试专家会签 + 用户确认) | **开发流人工**(reporter 不自动)|
| FIXED → OPEN | 复测失败 | **开发流人工** |
| OPEN → CLOSED | (直接关闭,绕过 FIXED)— **禁止** | - |

> **铁律**:reporter **只能**建 OPEN 状态单。FIXED / CLOSED 由开发流人工维护。

---

## §4 索引文件(可选)

`<app-test>/docs/bugs/README.md`(自动生成):

```markdown
# Bugs(<app>)

## 当前状态

| OPEN | FIXED | CLOSED |
|:----:|:-----:|:------:|
| 3    | 1     | 5      |

## 待处理 OPEN(按 priority 排序)

- [BUG-001](20260820-001.md) P0 用户登录失败
- [BUG-002](20260820-002.md) P1 列表页加载超时
- [BUG-003](20260820-003.md) P2 提交按钮未禁用

## 最近 CLOSED(7 天内)

- [BUG-005](20260818-005.md) FIXED → CLOSED
```

reporter 每次建新 bug 时同步更新此 README。

---

## §5 与 zentao 的等价映射(降级时记录)

| zentao 字段 | 本地 bug 单字段 | 备注 |
|------------|---------------|------|
| bug.id | id | BUG-NNN 自增 |
| bug.title | title |  |
| bug.status | status | 3 选 1,非 zentao 全状态 |
| bug.severity | severity | high/medium/low |
| bug.pri | priority | P0/P1/P2 |
| bug.steps | 复现步骤 | markdown body |
| bug.files | 截图与证据 | markdown body |
| bug.product | (无对应) | 本地无 product 概念 |

---

## §6 反例(V2-AP-2 / V2-AP-3)

- ❌ 禅道不可用时硬 exit → reporter 应降级继续
- ❌ reporter 自动标 FIXED 状态 → 必须留给开发流
- ❌ reporter 自动标 CLOSED 状态 → 必须留给开发流
- ❌ bug 单 frontmatter 缺 source 字段 → reporter 必填
- ❌ bug 单缺 case_id → 无法反向追溯报告
- ❌ 多个 bug 用同一 ID → reporter 必读现有 README 自增序号