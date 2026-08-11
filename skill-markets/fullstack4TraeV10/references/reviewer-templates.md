# Reviewer 模板库（V10.8 NEW）

> 来源: reviewer.md 拆分。本文件收录质疑式验收官所有模板和详细说明,reviewer.md 仅保留骨架引用。
> 引用方: [agents/reviewer.md](../agents/reviewer.md)

---

## §Step -2: 验收基准拆解格式

> 验收前必须先拆解,不可直接进入四维 checklist。

**两个产出**:

1. **必须满足的条件清单** — 从 proposal.md / spec.md / plan.md 提取核心需求点,逐条列出"本次任务必须满足什么才算完成"。后续 Step 2 需求溯源必须逐条对照此清单。

2. **高风险/易遗漏区域清单** — 预先识别 implementer 容易遗漏的点:
   - 边界条件（空输入/并发/超时/权限不足/数值溢出）
   - 异常处理（网络失败/资源不存在/并发冲突）
   - 旧功能兼容性（本次改动是否破坏原有 API/数据/交互）
   - 跨模块副作用（公共模块变更的下游影响）
   - 数据迁移（字段变更/格式变更/历史数据兼容）

**输出格式**:

```markdown
## 验收基准拆解
- 必须满足条件清单 ({N} 条):
  1. {需求点1}
  2. {需求点2}
  ...
- 高风险/易遗漏区域清单 ({M} 条):
  1. {风险点1} — 对应 Step 1.5 边界遗漏
  2. {风险点2} — 对应 Step 1.5 依赖污染
  ...
```

**强制联动**: Step 1.5 主动证伪必须逐项核查本步骤识别的高风险清单,任一未核查 = 🛑 拦截。

---

## §Step 0.5: 证据索要机制

> 不可仅凭代码 diff 下结论,必须主动向 implementer 索要证据 + 亲自执行验证。
> 核心立场: implementer 的 Completion Report evidence 字段是"自报",reviewer 必须独立验证或要求补充。

### 证据来源(双轨制)

| 来源 | 含义 | 信任度 |
|------|------|--------|
| A. implementer 提供 | 引用 implementer Completion Report 的 evidence 字段(file:line + 日志摘要) | self_attested,需验证 |
| B. reviewer 亲自执行 | reviewer 实际跑命令/读代码/截图,产出独立证据 | 独立验证,可信 |

### 索要清单(对照 Step -2 必须满足条件清单逐条索要)

```
对每个必须满足条件,索要以下证据(任一缺失 = 证据不全):
[ ] 核心逻辑代码片段 — 证明真正实现,非空壳/TODO
[ ] 实际运行/测试日志 — 证明真的跑通,非声明跑通(末尾 10 行含 pass count)
[ ] API 返回报文(涉及 API 时) — status + body 关键字段
[ ] 截图/录屏(涉及 UI 时) — 实际渲染证据,非 mockup
```

### 证据不全处置流程

```
1. 列出缺失项 → 逐条标注 "缺失证据: {条件N} 需 {证据类型}"
2. 要求 implementer 补充 → 限定补充期限(同会话内 / 下次移交前)
3. 逾期/拒绝补充 → 直接 🛑 FAIL,不计入"待验证",计为"未完成"
4. 不可仅凭 implementer 自报 PASS 字符串放行
```

### 反模式(禁止)

```
❌ implementer 说"测试通过" → reviewer 直接采信
❌ Completion Report 含 "status: ✓" → reviewer 不抽检就放行
❌ evidence 字段为空或仅 file 路径无行号 → 视为"已提供"
❌ 证据不全但 reviewer 自行补跑 → 掩盖 implementer 隐瞒(应要求补充)
```

### 证据索要记录输出格式

```markdown
## 证据索要记录
- 条件1: ✅ 证据齐全 (来源A: implementer 提供 tests/foo.py:42 + 来源B: reviewer 亲自跑 pytest 10 passed)
- 条件2: ❌ 证据缺失 (需 implementer 补充: API 返回报文)
- 条件3: ⚠️ 待验证 (来源A 已提供,来源B 待 reviewer 亲自执行)
```

**判定**:
- 任一条件证据缺失且 implementer 未补充 → 🛑 REJECT(在 Step 1 之前就拒绝)
- 全部条件证据齐全 → 继续 Step 1(基于已索要证据做四维判定)

---

## §Step 2.4: Test Plan 前置门禁（V10.12 NEW — 防"spec 写了但实现漏测"）

> **触发**: §Step 2.5 产品侧验收前必走；§Step 1.5 主动证伪时同步验证。
> **目的**: 强制将 spec.md 测试场景映射到具体测试代码，防止 implementer 漏想场景。
> **根因**: V10.11 之前 spec 模板虽有 `## Edge Cases` 但没强制映射机制，implementer 漏测场景 review 也抓不到。

### §Step 2.4.1 文件存在性

```
[ ] docs/specs/{feature}/test-plan.md 存在
  └─ 不存在 → 🛑 REJECT + 失败分类"测试覆盖缺口"
  └─ 路径: [test-plan.md](../../templates/test-plan.md) 模板来源
```

### §Step 2.4.2 §1 测试场景清单完整性

```
[ ] §1 表格行数 ≥ spec.md §BDD Scenarios + §Edge Cases + §E2E Scenarios 总和
[ ] 每个场景含: 场景 ID + 来源（spec.md §X.Y）+ 测试类型 + 优先级 + 实施者
[ ] 优先级分布合理: P0 = 产品核心功能（必 100% 覆盖），P1 = 重要场景（≥ 80%），P2 = 边缘（≥ 50%）

判定: 任一 ❌ → 🛑 REJECT + 失败分类"测试覆盖缺口"
```

### §Step 2.4.3 §2 覆盖映射表完整性（实施者必填）

```
[ ] §2 表格每个 TS-{N} 必填: 测试文件:行号 + 状态
[ ] P0 场景 100% 状态 ✅
[ ] P1 场景 ≥ 80% 状态 ✅
[ ] P2 场景 ≥ 50% 状态 ✅
[ ] ⚠️ 部分实现必须说明缺什么
[ ] ❌ 未实现必须说明原因

判定: 任一 ❌ → 🛑 REJECT + 失败分类"测试覆盖缺口" → 强制循环（Round 1 退回 implementer）
```

### §Step 2.4.4 §3 未覆盖场景说明（建议登记，非硬性 REJECT）

```
[ ] §3 表格建议包含: spec 场景 + 为何不覆盖 + 风险等级 + 缓解措施
[ ] 风险等级分布合理: 不能全填 🟢（全填绿 = 假装没风险）

判定: §3 为空 ≠ 🛑 REJECT（取消硬性）
  └─ §3 缺失只是 signal "实施者可能漏想场景"，不进失败循环
  └─ reviewer 仍可在 §Step 2.5 产品侧验收时主动询问 "用户看到这个场景会怎么想？"
  └─ 与 spec-template.md `## Out of Scope` 段功能重叠，避免强制透明催生"全 🟢"造假

特殊情况: §2 映射表里出现 🔴 高风险缺口 → review 必走 "退 spec-enhancer" 路径
  └─ 原因: 缺口本质是 spec 漏想，不是 implementer 漏测
  └─ 处理: 退回 spec-enhancer 补 spec.md §Edge Cases 或 §BDD Scenarios，再回到 implementer
```

### §Step 2.4.5 §4.3 验证命令可执行（reviewer 必跑）

```
[ ] §4.3 列出至少 1 个测试命令（unit/e2e/visual/integration）
[ ] reviewer 实际跑 ≥ 1 个命令 + 验证退出码 + 末尾输出
[ ] 命令不存在或跑失败 → 🛑 FAIL（不可信实施者自报）
[ ] reviewer 必须 glob 验证 §2 映射表的"测试文件:行号"实际存在（防 implementer 编造）
  └─ 随机抽 ≥ 3 个 TS-{N} → Read 测试文件对应行 → 确认是真正测试代码
  └─ 任何"行号不存在"或"行号内容非测试代码"→ 🛑 FAIL + 计入 implementer 失败 1 次

判定: 任一 ❌ → 🛑 REJECT + 失败分类"测试覆盖缺口"
```

### §Step 2.4.6 §4.4 已知盲区诚实声明

```
[ ] §4.4 非空（必须诚实声明未覆盖场景）
[ ] 不假装 100% 覆盖

判定: §4.4 为空 + §2 全 ✅ = 🛑 REJECT（怀疑造假，要求重填）
```

### §Step 2.4.7 失败分类（强制循环标签）

```
test-plan-gate FAIL 分类:
  ├─ "测试覆盖缺口:P0 漏测" → implementer 重做 + 补测试
  ├─ "测试覆盖缺口:P1 不足 80%" → implementer 重做 + 补测试
  ├─ "测试覆盖缺口:§4.3 命令不可执行" → implementer 重填命令 + reviewer 重跑
  └─ "测试覆盖缺口:高风险 spec 漏想" → 退 spec-enhancer 补 spec.md §Edge Cases/§BDD Scenarios
      └─ 不是 implementer 责任: 缺口本质是 spec 漏想场景
      └─ spec-enhancer 补 spec 后回到 implementer 重做测试
      └─ 循环路径: spec-enhancer → implementer → reviewer → spec-enhancer (如需要)

注: §3 "未覆盖场景说明" 不进硬性 REJECT（V10.12 §Step 2.4.4 取消强制）
    §3 仅作 reviewer 主动发现的 signal，不催生"全 🟢 造假"
```

### §Step 2.4.8 与 §Step 2.5 的边界

```
§Step 2.4 (Test Plan Gate): 防"spec 写了但实现漏测"（覆盖缺口）
§Step 2.5 (产品侧验收): 防"测了但产品视角不对"（货不对版 / 用户视角 FAIL）
§Step 2.6 (自动循环): 任一 ❌ 都触发

判定顺序: §Step 2.4 先通过 → §Step 2.5 → §Step 2.6
```

---

## §Step 2.5: 产品侧功能有效性验收（V10.12 NEW — 防"货不对版"）

> **根因**: V10.11 之前 reviewer Step 2 写"功能效果验证 + 需求溯源"但无具体定义，
> 导致 implementer 提交"模型管理"任务的欢迎页截图，reviewer 看到"有截图"就放行。
> **本节强制**: reviewer 必须站在产品视角，逐条问"用户看到这个会认可吗"。

### §Step 2.5.1 三件必读（顺序不可换）

```
[1] 用户原始 prompt（chat 历史/issue/工单）
    └─ 不能用"目标用户"或"需求摘要"代替 — 必须原始输入
    └─ 多轮对话时取最新版本的 user 提问

[2] docs/specs/{feature}/spec.md 的 Requirements + Scenarios
    └─ 必须有 v10_simplified 标识 OR Requirements + Scenarios 段
    └─ 抽出"用户视角可观察的行为"清单（UI 文本 / API 返回 / 状态变化）

[3] 当前 evidence 截图/录屏/操作日志的实际内容
    └─ 不是"路径存在" — 是主上下文亲自 Read 截图后内容核对
    └─ 子代理的 AI 描述不算证据（参见 sub-agent-rules.md §10）
```

### §Step 2.5.2 强制核对表（每条需求 3 问）

```markdown
| 需求点(N) | 用户视角可观察行为 | spec.md 描述 | evidence 内容 | 3 问判定 |
|----------|------------------|-------------|--------------|---------|
| 1 | [用户看到这个功能后能做什么/看到什么] | [spec.md §X.Y 原文] | [截图实际显示/录屏帧/操作日志] | ✅ / ❌ |
| 2 | ... | ... | ... | ✅ / ❌ |
| ... | | | | |
```

**3 问判定**（每条都必答）：

```
问1 (需求归属): 这条 evidence 是关于**当前 feature** 的吗？
  ├─ 是 → 继续问2
  └─ 否（是欢迎页/无关页/上一个 feature 残留）→ ❌ 货不对版 FAIL

问2 (行为匹配): evidence 显示的用户视角行为符合 spec.md 描述吗？
  ├─ 是 → 继续问3
  └─ 否（实现少了关键功能/UI 文本错误/状态错误）→ ❌ 功能不达标 FAIL

问3 (用户会认可吗): 真实用户看到 evidence 会认为"这就是我要的功能"吗？
  ├─ 是 → ✅ PASS
  └─ 否（用户会困惑/会质问/会发现和描述不符）→ ❌ 用户视角 FAIL
```

### §Step 2.5.3 判定矩阵

```
[1] 全部 ✅ → 通过，进入 Step 3 评分
[2] 任一 ❌ → 🛑 REJECT，标记：
    ├─ "货不对版" (问1 FAIL) → implementer 必须重新实现当前 feature
    ├─ "功能不达标" (问2 FAIL) → implementer 必须补齐 spec.md 对应行为
    └─ "用户视角 FAIL" (问3 FAIL) → implementer 必须重新审视需求
[3] 任一 ⚠️ (evidence 内容模糊/无法判断) → 要求 implementer 补强 evidence（重新截图/录屏/补操作步骤）
```

### §Step 2.5.4 反模式（V10.12 禁止）

```
❌ "截图存在就 PASS" — 只看 evidence 路径不看内容
❌ "spec.md 没写就不验收" — 不基于 spec.md 显式拒绝
❌ "AI 描述可信" — 拿 implementer 的"我已截图..."字样当证据
❌ "上下文合理" — reviewer 自己脑补没看到的 UI 行为
❌ "测试通过 = 功能完成" — 跳过 3 问直接放行
```

### §Step 2.5.5 输出格式（强制）

```markdown
## §Step 2.5 产品侧验收报告

### 三件必读核对
- [1] 用户原始 prompt: ✅/❌ 来源: <file:line 或消息 ID>
- [2] spec.md Requirements + Scenarios: ✅/❌ 来源: docs/specs/{feature}/spec.md#L##-L##
- [3] evidence 实际内容: ✅/❌ 主上下文亲自 Read 截图/L##-L##

### 强制核对表（每条需求 3 问）
| # | 用户视角行为 | spec 描述 | evidence 内容 | 问1 | 问2 | 问3 | 判定 |
|---|------------|---------|-------------|-----|-----|-----|------|
| 1 | ... | ... | ... | ✅ | ✅ | ✅ | ✅ PASS |
| 2 | ... | ... | ... | ❌ | — | — | ❌ 货不对版 |

### 结论
- [1][2][3] 全 ✅ → 进入 Step 3
- 任一 ❌ → 🛑 REJECT + 失败分类 + 强制循环（见下）
```

---

## §Step 2.6: 自动循环机制（V10.12 NEW — 防"重做又失败"）

> **触发**: Step 2.5 任一 ❌ → 进入自动循环，无需用户介入（最多 2 轮）。

### §Step 2.6.1 循环规则

```
Round 1: Step 2.5 ❌ → 自动退回 implementer 重做
  ├─ 失败分类标签必填（货不对版 / 功能不达标 / 用户视角 FAIL）
  ├─ implementer 必须按失败标签修正 + 重新提交 evidence
  └─ reviewer 重新跑 Step 2.5

Round 2: Step 2.5 仍 ❌ → 自动退回 implementer + 通知用户（升级上报）
  ├─ 通知格式：阻塞报告 5 字段（Article XV）
  ├─ 用户选项：(a) 给出额外指引 (b) 接受部分完成 (c) 终止
  └─ 升级后等用户决策，不进入 Round 3

Round 3+ → rescue hatch（sub-agent-rules.md §5 已定义：回退 Phase 0 重做需求）
```

---

## §Completion Report 模板
- session_id: <uuid>                              # V10.4 必填,主上下文机械验证
- self_attested: true | false                     # V10.4 必填(同 session = true)
- independently_verified_by: <other uuid>        # V10.4 self_attested=true 时必填
- agent: reviewer
- role_stance: 质疑式验收官                         # V10.8 必填,确认角色立场已激活
- code_dimension: PASS|FAIL ({pass}/{total} tests, {cov}%)
- api_dimension: PASS|FAIL|N/A ({pass}/{total} contract tests)
- uiux_dimension: PASS|FAIL|N/A (PhaseA={}, PhaseB={})
- boundary_dimension: PASS|FAIL|N/A (affected: {N} modules)
- total_score: {X.X}/5.0
- functional_check: PASS|FAIL
- requirement_tracing: PASS|FAIL (covered: {N}/{M} requirements)  # V10.8 NEW 需求溯源
- active_falsification: {finds} finds (边界遗漏={N}, 依赖污染={N}, 未提交={N}, 隐藏TODO={N}, 测试篡改={N})  # V10.8 NEW 主动证伪
- evidence_attached: yes|no                       # V10.8 NEW 事实证据已附
- evidence_summary: {列出每维度的关键证据 file:line 或日志摘要}  # V10.8 NEW
- rot_scan: pass|warn|fail (rot_finds={N})        # V10.4 新增,rot-detector 联动
- status: ✓ | ⚠️ | ✗
```

---

## §事实证据清单（V10.8 NEW — 无证据 = 未完成）

```
Reviewer 必须在 Completion Report 附以下事实证据（file:line 或日志摘要）:
[ ] 代码层: 单元测试运行日志末尾 10 行（含 pass count）
[ ] API 层: 真实 HTTP 响应报文（status + body 关键字段）
[ ] UI/UX 层: 截图文件路径 + vision-audit 报告
[ ] 模块边际: detect_changes() + impact() 输出
[ ] 功能效果: 演示证据（截图/录屏/操作步骤）
[ ] 需求溯源: 逐条 PASS/FAIL 对照表

任一证据缺失 → 视为该维度未验证 → 🛑 拦截
```

---

## §验收裁决模板（V10.8 NEW — 标准化输出）

```
【验收裁决】: ✅ 通过放行 / ❌ 拦截打回
【事实依据】:
- 需求点1: 已验证。（附实际证据: "日志显示 xxx","代码第 x 行实现了 xxx"）
- 需求点2: 未通过。（附实际证据: "实际运行报错 xxx","未处理 xxx 边界情况"）
【质疑与追问】（如有）:
- 发现疑点: xxx。需要 implementer 解释或证明。
【打回修改清单】（如裁决为 ❌）:
- 1. 必须补充 xxx 的实现。
- 2. 必须提供 xxx 的测试日志。
```

---

## §Step -1: Analyze 检测维度

| 维度 | 检查项 |
|------|--------|
| **A. 接口签名一致性** | spec.md 提到的 API 端点/方法/参数 vs contracts/api-contracts.md |
| **B. 交互流程一致性** | spec.md User Story 行为 vs prototypes/ui-ux-logic.md 状态/事件流 |
| **C. 数据模型一致性** | spec.md Entities/字段 vs contracts/domain-models.md |
| **D. 验收标准完整性** | 每个 Requirement（FR/SC）都有对应 Acceptance Criteria 或 E2E Scenario |
| **E. Constitution 对齐** | 与 `docs/constitution.md` MUST 原则无冲突（无该文件则跳过） |
| **F. 覆盖度** | 需求 → 任务 → 实现 三层映射是否完整 |

**判定**:
- 阻塞项 ≥ 1 → 🛑 REJECT,退回 implementer / spec-enhancer / contract-writer 修复
- 仅警告项 → 继续 Step 0,在四维验收报告中标注警告项
- 全部通过 → 继续 Step 0

---

## §Step 1: 四维验收 Checklist

> 证据来源: Step 0.5 索要的 evidence。本步骤基于已索要证据做判定。

### 维度 1: 代码层（权重 25%）
```
[ ] 单元测试全绿（{pass}/{total}）→ 附实际运行日志末尾 10 行
[ ] Contract 测试全绿（{pass}/{total}）→ 附实际运行日志末尾 10 行
[ ] Lint 0 error → 附 lint 输出末尾 5 行
[ ] 覆盖率 ≥ 80% → 附覆盖率报告关键行
[ ] 无 TODO/FIXME/HACK（或已有 ponytail 标记）→ 附 grep 输出
```

### 维度 2: API 层（权重 30%）
```
[ ] 契约测试打真实端点（HTTP 请求 → 响应，非 mock）→ 附实际 HTTP 响应报文
[ ] 接口签名 vs api-contracts.md 一致 → 附 diff 对照
[ ] 数据模型 vs domain-models.md 一致 → 附字段对照表
[ ] 错误码 vs validation-rules.md 一致 → 附错误码触发测试
[ ] 事件 vs events.md 一致 → 附事件 payload 实例
触发: contracts/ 存在 → 执行；纯前端项目 → N/A
```

### 维度 3: UI/UX 层（权重 25%）
```
判定: 变更含 .tsx/.jsx/.vue → 执行；否则 N/A
Phase A — 视觉一致性: 截图对比 5 状态 + vision-audit 逐像素比对
Phase B — 交互逻辑: 交互流路径 + 状态变化 + 错误边界处理验证
```

### 维度 4: 模块边际（权重 20%）
```
[ ] GitNexus detect_changes() → 附 detect_changes 输出
[ ] 检查公共模块变更的影响面 → 附 impact() 输出
[ ] 确认无意外副作用（其他模块测试仍全绿）→ 附全量回归日志
[ ] 模块接入文档完整 → 附文档路径 + 关键段
```

---

## 关联

- [acceptance-gates-v10.md](acceptance-gates-v10.md) — 满分硬门禁 + 产物证据链 + 通过依据3类分层
- [agents/reviewer.md](../agents/reviewer.md) — reviewer agent 骨架(本文件被其引用)
