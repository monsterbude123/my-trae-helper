# 验收门禁 V10 — 满分硬门禁

> Review 阶段的硬性检查点。V10 重构：四维验收 + 满分硬门禁 + 产物证据链。
> **任何非满分 = 🛑 REJECT 整个 change。无降级、无灰色。**

---

## 满分硬门禁

```
✅ 4 维全部满分 = PASS
🛑 任一维度非满分 = REJECT 整个 change
🚫 禁止 N/A 计入分母（不适用维度须在 Plan 阶段显式锁定为 N/A 且不再二次判定）
🚫 禁止"非阻塞 P1"、"降级验收"、"部分扣分"灰色术语
```

---

## 产物证据链（强制）

每个 PASS 维度**必须**附真实命令输出片段（如 `> pytest tests/feature.test.ts → 10 passed in 0.3s`），主上下文 regex 验证：
1. 命令存在
2. 退出码 0
3. 输出包含预期结果

**不附证据链的 PASS 维度 = 🛑 REJECT**（不允许 agent 自报"我跑了"）

### 证据链模板

```markdown
## 代码维度证据链
- 命令: `pytest tests/feature.test.ts -v`
- 输出: `10 passed in 0.3s`
- 退出码: 0

## API 维度证据链
- 命令: `curl -X POST http://localhost:8000/api/feature -d '{"test": true}'`
- 输出: `{"code": 0, "data": {...}}`
- 退出码: 0
```

---

## 四维满分硬指标

### 维度 1: 代码层（必检）

```
[ ] 单元测试全绿（{pass}/{total}，exit 0）
[ ] Contract 测试全绿（{pass}/{total}，exit 0）
[ ] Lint 0 error
[ ] 覆盖率 ≥ 90%
[ ] 无 TODO/FIXME/HACK（或已有 ponytail 标记）
[ ] code-hygiene.py 通过（单文件 ≤ 800 行 / 单函数 ≤ 50 行 / 圈复杂度 ≤ 15）
[ ] 抽查"理解确认"中 2 项符号真实存在（GitNexus query 验证）
```

**满分判定**：7/7 勾选

### 维度 2: API 层（涉及 API 时必检）

```
[ ] 契约测试打真实端点（HTTP 请求 → 响应，非 mock）
[ ] 接口签名 vs api-contracts.md 100% 一致
[ ] 数据模型 vs domain-models.md 100% 一致
[ ] 错误码 vs validation-rules.md 100% 一致
[ ] 事件 vs events.md 100% 一致
```

**满分判定**：5/5 勾选

**N/A 锁定**：纯前端项目（无 API 改动）在 Plan 阶段显式锁定，Review 时不再判定。

### 维度 3: UI/UX 层（涉及 UI 时必检）

```
Phase A — 视觉一致性:
  基准: Trae Work 按 design-prompt.md 生成的原型
  [ ] 截图对比: 5 状态 × 关键页（加载中/空数据/正常/错误/边界）100% 一致
  [ ] vision-audit 逐像素比对 0 差异

Phase B — 交互逻辑:
  基准: prototypes/ui-ux-logic.md
  [ ] 所有交互流路径验证通过
  [ ] 所有状态变化验证通过
  [ ] 所有错误边界处理验证通过
```

**满分判定**：6/6 勾选

**N/A 锁定**：纯后端项目（无 UI 改动）在 Plan 阶段显式锁定。

### 维度 4: 模块边际（涉及公共模块时必检）

```
[ ] GitNexus impact() 列出所有受影响下游
[ ] 每个下游模块无意外副作用（接口签名未破坏、行为未改变）
[ ] 文档同步：docs/modules/{changed-module}.md 更新
[ ] 扩展点（Extension Points）标注清晰
```

**满分判定**：4/4 勾选

**N/A 锁定**：未变更公共模块的独立功能在 Plan 阶段显式锁定。

---

## 功能效果验证（四维通过后必做）

```
[ ] 从用户视角确认：需求描述的功能是否真的做到了
[ ] define/plan 中的 Closure P0 步骤逐项可演示
[ ] 用户场景脚本完整跑通（启动 → 触发 → 结果验证）
```

**满分判定**：3/3 勾选

---

## Reviewer Completion Report 模板（V10）

```markdown
## Completion Report
- agent: reviewer
- artifacts: [审查报告.md, DOC-SYNC-CHANGES.md]
- code_dimension: PASS|FAIL ({pass}/{total} tests, coverage {X}%)
- api_dimension: PASS|FAIL|N/A (locked_at_plan: true|false)
- uiux_dimension: PASS|FAIL|N/A (locked_at_plan: true|false)
- boundary_dimension: PASS|FAIL|N/A (locked_at_plan: true|false)
- functional_verification: PASS|FAIL ({P0}/{total} P0 demoed)
- product_evidence:
  - code: [命令 + 输出 + 退出码]
  - api: [命令 + 输出 + 退出码]
  - uiux: [截图对比结果]
  - boundary: [影响下游列表]
- total_score: {X.X}/5.0
- status: ✓ | 🛑
```

---

## 关联规则

- 主上下文机械校验：`/rules/agent-机械验证.md` Step 0 字段值校验
- 代码卫生：`scripts/code-hygiene.py`
- 阶段转换：`scripts/phase-gate.py`
- 评分制度强化：`rules/agent-机械验证.md` §V10 评分制度

### §3.2 零残留规则 (V10.3.5 NEW)

**Article III 零残留** — install 脚本禁止产生 .bak 副本/旧版本残留:

```
- install-v10.py 禁止 shutil.move 到 .bak.{pid}
- skills/ 下不应有 *.bak.* 文件
- 升级前必跑: Get-ChildItem *.bak.* | Should Be NullOrEmpty
- 违反 → 🛑 REJECT install
```
