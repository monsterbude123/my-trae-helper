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

## §Completion Report 模板

```
## Completion Report
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
| **E. Constitution 对齐** | 与 `memory/constitution.md` MUST 原则无冲突（无该文件则跳过） |
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
