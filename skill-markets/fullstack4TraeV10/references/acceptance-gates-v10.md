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

---

## 通过依据 3 类分层（V10.8 NEW）

> 来源: agent-apology-discipline §11 通过依据透明度协议。
> 核心立场: 用户问"你这次通过的依据是啥"时，主上下文必须能**瞬间分层回答**。
> 触发条件: 任何"完成 / 通过 / PASS / 修复"声明（尤其是涉及用户可见 UI 的任务）。

### 3 类分层

```
[1] 后端/编译类（机器可验证）         → 不证用户视角
    ├─ tsc --noEmit (0 错误)
    ├─ curl /api/v1/... (字段/状态码正确)
    ├─ cargo build / cargo test
    └─ vitest / pytest 全绿

[2] UI 渲染类（用户可见，机器可验证）  → 主上下文亲自 Read
    ├─ Playwright 截图 (≥ 1 张/任务)
    ├─ 主上下文亲自 Read 抽检 (verify 描述 vs 实际像素)
    └─ 视觉验证协议 → reset-and-verify-protocol.md V10.8 G1/G2/G3

[3] 用户视角类（必须用户验收）        → 不可由主上下文代签
    ├─ 用户在 dev server 上亲眼看到效果
    ├─ 用户书面确认"通过"（非"看起来 OK"）
    └─ 任一闭环用户签字
```

### 强制声明格式（主上下文回复模板）

```markdown
## 本次通过依据

[1] 后端/编译类（跑了哪些）
  - ✅ tsc --noEmit: 0 错误
  - ✅ curl /api/v1/...: 返回正确字段
  - ⚠️ cargo test: 略（非本次范围）

[2] UI 渲染类（跑了吗？没跑要明说）
  - ⚠️ 未跑 Playwright 截图
  - ⚠️ 主上下文未亲自 Read 截图
  - ⚠️ 组件是否实际渲染未验证

[3] 用户视角类（用户验收了吗？）
  - ⏳ 用户尚未打开 dev server 验收
  - ⏳ 闭环未获用户签字

结论: [1] 通过, [2][3] 未通过 → 不能声称"完成"
下一步: (1) Playwright 跑 [2] (2) 邀请用户验收 [3]
```

### 反例（V10.8）

- 当时做了: implementer 跑通后端 4 项验证（tsc 0 错误 + curl camelCase + POST 200 + cargo build），声称"完成"
- 导致后果: 用户打开页面截图证伪 UI 没改善，质疑"你这次通过的依据是啥"
- 根因: 用 [1] 后端/编译类验证充当 UI 任务"完成"依据，省略 [2][3] 类目
- 教训: UI 任务必须含 [2] Playwright 截图 + 主上下文亲自 Read + [3] 用户验收

### 反向提示词

```
NEVER: 用 [1] 后端/编译类验证充当"完成"声明
触发条件: 任务涉及用户可见 UI（任何前端组件/页面/交互/路由）
错误代价: 用户截图证伪，信任坍塌，用户应激"你这次通过的依据是啥"
正确替代: 必须含 [2] Playwright 截图 + [3] 用户验收

NEVER: 在声明"完成"时省略 [2][3] 类目（暗示完成但未跑）
触发条件: 用户没问"通过依据"时主动声明完成
错误代价: 用户视角发现 UI 没改善时被迫问"通过的依据是啥"
正确替代: 主动按 3 类分层声明，有就跑，没跑就明说"未跑 UI 验证"
```

### 检查清单（每次"完成"声明前）

```
[ ] [1] 后端/编译类: 列出跑了哪些命令 + 结果
[ ] [2] UI 渲染类: Playwright 截图 + 主上下文亲自 Read 抽检
[ ] [3] 用户视角类: 用户书面签字（非"看起来 OK"）
[ ] 3 类都通过 → 可声明"完成"
[ ] 任一缺失 → 必须显式标注"未跑 XX 验证"，不得暗示完成
```

---

## UI 细节遗漏检查清单（V10.8 NEW）

> 来源: 编码心法 §2.3 — 非功能性 UI 细节容易在 Review 阶段被忽略，因为代码审查和功能测试不会覆盖它们。
> 适用: 涉及 UI 变更的 change，在 Review 阶段必须逐项检查，不可仅凭"看起来没问题"跳过。

### 检查清单

```
[ ] 全局滚动条样式（Firefox scrollbar-width + Chrome ::-webkit-scrollbar，Windows/macOS 均验证）
[ ] Focus ring 可见性（Tab 键盘导航时元素有可见焦点指示器，非 outline:none）
[ ] @media (prefers-reduced-motion: reduce) — 禁用所有 transition/animation
[ ] font-smoothing / antialiased / text-rendering 一致性
[ ] 断点过渡动画（sidebar 折叠、panel toggle）流畅且无闪烁
[ ] 暗色主题下所有区域背景色有视觉区分（非纯黑大平面）
```

### 检查方式

```
启动应用 → 逐项目视验证 → 每项截图或标注 ✅/❌
任一 ❌ → uiux 维度不通过，退回 implementer 修复
```

### 反例（V10.8）

- 当时做了: Review 阶段代码审查 + 功能测试全绿，声明 uiux PASS
- 导致后果: 用户使用时发现 Tab 键导航无焦点指示器 + 暗色主题纯黑大平面 + 滚动条样式不一致
- 根因: 代码审查和功能测试不覆盖非功能性 UI 细节，仅凭"看起来没问题"跳过
- 教训: UI 细节检查清单必须逐项机械验证，不可凭主观判断跳过

### 与四维满分硬门禁的关系

```
uiux 维度满分判定（V10.8 强化）:
  Phase A — 视觉一致性: 截图对比 + vision-audit 逐像素比对
  Phase B — 交互逻辑: 所有交互流路径 + 状态变化 + 错误边界
  Phase C — UI 细节（NEW）: 上述 6 项检查清单逐项通过

  满分判定: Phase A + B + C 全部勾选
  任一 ❌ → uiux 维度非满分 → 🛑 REJECT 整个 change
```
