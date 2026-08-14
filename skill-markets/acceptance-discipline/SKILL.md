---
name: acceptance-discipline
description: 高质量验收铁律 — 面向 AI agent 与团队的统一项目验收体系。覆盖单测 / 集成 / E2E / 性能 / 安全 / 验收门禁全生命周期。当 agent 进行 PR 提交、发版前检查、E2E 回归、性能压测、安全扫描、测试阻塞排查时加载。整合并扩展 test-experience / e2e-module-audit / test-partition-runner 三个能力。
triggers: [验收, 交付, 发版, 上线前, release gate, acceptance, verify, gate, 跑 E2E, 跑测试, 测试卡住, 测试阻塞, 测试挂起, 测试失败, 测试超时, 测试慢, mock 不生效, fixture, 坏测试, bad test, flaky test, 分区测试, 性能压测, 安全扫描, 依赖扫描, PR check, 门禁]
requires:
intent: 高质量验收铁律 — 面向 AI agent 与团队的统一项目验收体系
category: guard
audience: [agent]
---
# Acceptance Discipline — 高质量验收铁律

> **核心命题**：高质量验收是产品可交付的必要铁律。验收不是 QA 的"最后一步"，而是嵌入每一次提交、每一次合并、每一次发版的连续防护网。
>
> 本 skill 整合并扩展了三份原始沉淀（`test-experience` / `e2e-module-audit` / `test-partition-runner`），新增性能验收、安全验收、验收门禁、度量指标体系、AI Agent 协议、工具链推荐、落地路线图，形成可由 AI agent 直接加载执行的统一验收体系。

---

## §0 写在前面：验收是交付的必要铁律

### 0.1 五条铁律

```
铁律 1：测试不是"能跑就行"。坏测试 > 没有测试，因为坏测试给虚假信心。
铁律 2：截图是线索，日志是证据。没有日志证据的"修好了"等于没修。
铁律 3：修复后必须重新验证。不验证的修复是猜，不是修。
铁律 4：全局测试挂起时禁止盲目重试。先分区定位，再修复或跳过。
铁律 5：全量 E2E 是重武器，不要默认触发。已知有问题时先 Workflow B 即时诊断。
```

### 0.2 跳过验收的代价模型

| 跳过环节 | 短期看似节省 | 真实代价（含隐性） |
|---------|------------|----------------|
| 单测 mock 漏写 | 5 分钟 | 上线后真实 API 异常，回滚 + hotfix 4 小时 |
| E2E 不拉日志 | 10 分钟 | "页面有问题"无根因，反复猜改 2-3 轮，每轮 30 分钟 |
| 修复不重验证 | 1 分钟 | "声称修好"实际未修，下次发版重爆，信任崩塌 |
| 性能验收省略 | 30 分钟 | 上线后 P99 飙升，业务损失 + 紧急扩容成本 |
| 安全扫描跳过 | 1 小时 | 依赖漏洞被利用，事故级别 P0 |

**结论**：验收的时间投入是"廉价保险"，跳过验收是"高利贷"。一个 10 分钟的日志检查可以避免一个 4 小时的回滚事故，杠杆比通常在 10×–50×。

### 0.3 验收债务的复利效应

验收债务和金融债务一样有复利。一旦允许"先发版，下个迭代补测试"，下一次发版会继承上一次的暴露面，三次迭代后整个模块变成"没人敢动"的雷区。**铁律的本质是阻止债务复利**：每一次提交都要把验收做扎实，哪怕慢一点。

### 0.4 本 skill 的使用对象

| 角色 | 使用方式 |
|------|---------|
| **AI Agent**（主要消费者）| 通过 triggers 关键词自动加载，按 §12 协议执行验收任务 |
| **工程师**（PR 提交者）| 按 `references/checklists.md` 自检，按 agent 模板编写测试 |
| **Reviewer**（代码评审）| 按 [gate-keeper-agent](agents/gate-keeper-agent.md) 门禁清单逐项核验，按 [bad-test-cases](references/bad-test-cases.md) 识别坏测试 |
| **Tech Lead**（发版决策）| 按 [metrics](references/metrics.md) 判断发版风险，按 [roadmap](references/roadmap.md) 推进体系改造 |

---

## §1 验收体系全景图

### 1.1 验收金字塔

```
                    ┌─────────────┐
                    │  验收门禁   │  §7  发版决策层
                    └─────────────┘
                  ┌───────────────────┐
                  │ 安全验收 │ 性能验收 │  §5-§6  非功能性验收
                  └───────────────────┘
                ┌───────────────────────────┐
                │      E2E 验收（双工作流）    │  §4  端到端验证
                └───────────────────────────┘
              ┌───────────────────────────────────┐
              │        集成测试验收（Mocked）        │  §3  服务集成验证
              └───────────────────────────────────┘
            ┌───────────────────────────────────────────┐
            │           单元测试验收（Pure Unit）           │  §2  纯函数验证
            └───────────────────────────────────────────┘
```

**金字塔原则**：底层宽、顶层窄。底层（单测）应该占 70%+，速度最快、确定性最高；顶层（门禁）应该最少触发，但每次发版必须通过。**倒金字塔（E2E 占大头）是反模式**——慢、贵、Flaky、难维护。

### 1.2 各层验收职责矩阵

| 层 | 做什么 | 不做什么 | 速度预算 | 谁负责 |
|----|-------|---------|---------|-------|
| Unit | 纯函数 / 模型 / 工具方法验证 | 不碰 DB / 网络 / 文件系统固定路径 | < 50ms / 用例 | 提交者 |
| Integration | DB / 内部服务 / Mock 外部依赖 | 不调真实 LLM / 第三方 API | < 5s / 用例 | 提交者 |
| E2E | 关键用户路径 + 视觉 + 交互 | 不覆盖所有分支（留给单测） | < 30s / 模块 | 模块 Owner |
| 性能 | 关键接口 P99 / 吞吐 / 内存 | 不做功能验证 | 分钟级 | 性能 Owner |
| 安全 | 静态扫描 / 依赖扫描 / 鉴权矩阵 | 不做业务逻辑验证 | 分钟级 | 安全 Owner |
| 门禁 | 汇总上面所有层 + 人工评审 | 不重复跑已有测试 | 决策时长 | Tech Lead |

### 1.3 速度预算模型（Speed Budget）

> 一个真实网络调用的集中式代价，足以毁掉整个测试套件的可用性。

```
假设 250 个测试：
- 每个测试额外 0.5s DB init   → 125s  浪费（×17 倍基准）
- 每个测试额外 30s LLM 调用    → 7500s 浪费（×468 倍基准）
- 只有 10 个测试调 LLM         → 300s  浪费（×19 倍基准）

基准：250 个纯单测全量应在 15s 内完成。
```

**预算分配**（按 250 测试规模）：
- Unit 层：≤ 10s（autouse fixture 关闭所有外部服务）
- Integration 层：≤ 30s（仅 DB，LLM/外部 API 全 Mock）
- E2E 层：≤ 5 分钟（按模块分批，不强制全跑）
- 性能 / 安全：按需触发，不进入日常开发回路

### 1.4 分层标记与触发策略

| 标记 | 触发场景 | 命令 |
|------|---------|------|
| `@pytest.mark.unit` / 默认 | 每次提交 | `pytest -m "not slow and not e2e"` |
| `@pytest.mark.integration` | 每次提交（DB 已就绪） | `pytest -m integration` |
| `@pytest.mark.slow` | 手动 / 发版前 | `pytest -m slow` |
| `@pytest.mark.e2e` | 模块验收 / CI 夜间 | `pytest -m e2e` |
| `@pytest.mark.perf` | 性能回归基线对比 | `pytest -m perf` |
| 环境变量 `*_TEST_REAL_LLM=1` | 真实 LLM 联调 | 显式开启 |

---

## Agent 触发速查表

| 用户说什么 | 加载哪个 Agent | 核心内容 |
|-----------|--------------|---------|
| "写测试""加测试""补测试" | [unit-test-agent](agents/unit-test-agent.md) | §2 单元测试验收 |
| "集成测试""DB 测试" | [integration-test-agent](agents/integration-test-agent.md) | §3 集成测试验收 |
| "跑 E2E""回归""发版""XX 有问题""修一下" | [e2e-audit-agent](agents/e2e-audit-agent.md) | §4 E2E 验收（双工作流） |
| "性能压测""P99""压测""性能基线" | [perf-verification-agent](agents/perf-verification-agent.md) | §5 性能验收 |
| "安全扫描""依赖扫描""CVE""鉴权矩阵" | [security-verification-agent](agents/security-verification-agent.md) | §6 安全验收 |
| "门禁""release gate""上线前""PR check" | [gate-keeper-agent](agents/gate-keeper-agent.md) | §7 验收门禁 |
| "测试卡住""测试阻塞""测试挂起""分区测试" | [blockage-resolver-agent](agents/blockage-resolver-agent.md) | §8 阻塞应急 |

---

## 深度参考文档

| 文档 | 内容 |
|------|------|
| [metrics](references/metrics.md) | §9 度量指标体系 — 指标定义、Flaky Score、Mock 覆盖率、验收债务看板 |
| [checklists](references/checklists.md) | §10 统一 Checklist — PR 自检、模块发版、系统发版、紧急回滚 |
| [bad-test-cases](references/bad-test-cases.md) | §11 坏测试案例库 — 12 类 Bad Test 反模式（症状+根因+修复+预防） |
| [ai-agent-protocol](references/ai-agent-protocol.md) | §12 AI Agent 验收协议 — 触发词、模式选择、行为契约、多 Agent RACI、子 Agent 委派规范 |
| [toolchain-guide](references/toolchain-guide.md) | §13 工具链推荐 — Python/TS/E2E/性能/安全/日志/CI 全栈工具选型 |
| [roadmap](references/roadmap.md) | §14 落地路线图 — 止血→加固→优化 三阶段推进 |
| [faq](references/faq.md) | §15 FAQ — 12 个高频问题与解答 |

---

## 子 Skill（向后兼容）

本 skill 整合并扩展了三份原始沉淀，保留**根级独立 SKILL.md**（DEPRECATED 标记）+ `skills/` 子壳（redirect 入口）双重兼容：

| 旧 Skill | DEPRECATED 根级入口 | 兼容壳 | 实际加载 |
|---------|-------------------|--------|---------|
| `test-experience` | [test-experience/SKILL.md](../test-experience/SKILL.md) | [skills/test-experience/SKILL.md](skills/test-experience/SKILL.md) | [unit-test-agent](agents/unit-test-agent.md) + [integration-test-agent](agents/integration-test-agent.md) |
| `e2e-module-audit` | [e2e-module-audit/SKILL.md](../e2e-module-audit/SKILL.md) | [skills/e2e-module-audit/SKILL.md](skills/e2e-module-audit/SKILL.md) | [e2e-audit-agent](agents/e2e-audit-agent.md) |
| `test-partition-runner` | [test-partition-runner/SKILL.md](../test-partition-runner/SKILL.md) | [skills/test-partition-runner/SKILL.md](skills/test-partition-runner/SKILL.md) | [blockage-resolver-agent](agents/blockage-resolver-agent.md) |

**加载协议**：碰到 `status: deprecated` + `redirect_to` 字段 → 主 agent 应改加载 `redirect_to` 指向的 skill。

---

## AI Agent 验收协议（核心摘要）

> 完整协议见 [references/ai-agent-protocol.md](references/ai-agent-protocol.md)

### 模式选择决策树

```
用户输入
  │
  ├─ "跑一下 E2E" / "全量" / "回归" / "CI" / "发版"
  │   → Workflow A（批量验收）→ [e2e-audit-agent](agents/e2e-audit-agent.md)
  │
  ├─ "XX 页面有问题" / "帮我看看" / "为什么" / "修一下"
  │   → Workflow B（即时诊断）→ [e2e-audit-agent](agents/e2e-audit-agent.md)
  │
  ├─ "测试卡住" / "测试挂起" / 全量测试不结束
  │   → [blockage-resolver-agent](agents/blockage-resolver-agent.md)
  │
  ├─ "写测试" / "加测试" / "补测试"
  │   → [unit-test-agent](agents/unit-test-agent.md) + [integration-test-agent](agents/integration-test-agent.md)
  │
  ├─ "mock 不生效" / "测试报错"
  │   → mock 检查清单 + [bad-test-cases](references/bad-test-cases.md)
  │
  ├─ "性能压测" / "P99 飙升"
  │   → [perf-verification-agent](agents/perf-verification-agent.md)
  │
  ├─ "安全扫描" / "CVE"
  │   → [security-verification-agent](agents/security-verification-agent.md)
  │
  ├─ "上线前" / "发版前" / "门禁"
  │   → [gate-keeper-agent](agents/gate-keeper-agent.md)
  │
  └─ 不确定
      → 问用户
```

### AI 行为契约（通用）

```
✅ MUST DO
- 加载本 skill 后，明确告诉用户当前选用哪种模式
- 每个关键决策点说明依据（引用具体章节 / 检查项）
- 修复后必须验证（截图 + 日志 + 操作）
- 输出根因时引用具体日志行 / 代码行号
- 识别到 Bad Test 按案例库模板记录
- 度量指标异常时主动告警

❌ MUST NOT DO
- 只截图不拉日志就下结论
- 跳过日志检查直接猜根因
- 修复后不验证就声称完成
- 盲目重试整个测试套件
- 已知有问题还跑全量 E2E
- 把失败测试标 xfail 凑数
- 用 --no-verify 强推
- 只说"模块有问题"而没有根因
- 只看后端不看前端（或反过来）
- 忽略 WARNING 日志
```

---

## 快速导航

| 我想... | 看哪 |
|--------|------|
| 写一个新测试 | [unit-test-agent](agents/unit-test-agent.md) |
| Mock 不生效 | [unit-test-agent](agents/unit-test-agent.md) + [bad-test-cases](references/bad-test-cases.md) |
| 测试卡住整个套件 | [blockage-resolver-agent](agents/blockage-resolver-agent.md) |
| E2E 跑全量回归 | [e2e-audit-agent](agents/e2e-audit-agent.md) |
| 修一个页面 bug | [e2e-audit-agent](agents/e2e-audit-agent.md) |
| 准备发版 | [gate-keeper-agent](agents/gate-keeper-agent.md) + [checklists](references/checklists.md) |
| 看哪些指标健康 | [metrics](references/metrics.md) |
| 找坏测试案例 | [bad-test-cases](references/bad-test-cases.md) |
| 知道 agent 该怎么行为 | [ai-agent-protocol](references/ai-agent-protocol.md) |
| 选工具 | [toolchain-guide](references/toolchain-guide.md) |
| 制定改造计划 | [roadmap](references/roadmap.md) |

---

## 目录结构

```
acceptance-discipline/
├── SKILL.md                         # 本文件 — 编排层
├── agents/                          # 7 个验收 Agent 定义
│   ├── unit-test-agent.md           # §2 单元测试验收
│   ├── integration-test-agent.md    # §3 集成测试验收
│   ├── e2e-audit-agent.md           # §4 E2E 验收（双工作流）
│   ├── perf-verification-agent.md   # §5 性能验收
│   ├── security-verification-agent.md  # §6 安全验收
│   ├── gate-keeper-agent.md         # §7 验收门禁
│   └── blockage-resolver-agent.md   # §8 阻塞应急
├── references/                      # 深度参考文档
│   ├── metrics.md                   # §9 度量指标体系
│   ├── checklists.md                # §10 统一 Checklist
│   ├── bad-test-cases.md            # §11 坏测试案例库
│   ├── ai-agent-protocol.md         # §12 AI Agent 验收协议
│   ├── toolchain-guide.md           # §13 工具链推荐
│   ├── roadmap.md                   # §14 落地路线图
│   └── faq.md                       # §15 FAQ
└── skills/                          # 兼容壳 — 旧 skill 的 redirect 入口（DEPRECATED）
    ├── test-experience/SKILL.md       # → unit-test-agent
    ├── e2e-module-audit/SKILL.md      # → e2e-audit-agent
    └── test-partition-runner/SKILL.md # → blockage-resolver-agent
```

---

## 附录：版本与维护

- **当前版本**：v1.0
- **创建日期**：2026-06-25
- **维护者**：Tech Lead
- **下一版计划**：
  - v1.1：补充真实项目接入案例
  - v1.2：增加合约测试（Contract Test）章节
  - v1.3：增加混沌工程（Chaos Engineering）章节

---

> **最后的话**：验收不是成本，是保险。每一条铁律、每一项 Checklist、每一个度量指标，都是用真实事故换来的经验。遵守它们，不是因为你不够聪明，而是因为聪明人也会犯错——而验收体系存在的意义，就是让错误在到达用户之前被拦下。

---
