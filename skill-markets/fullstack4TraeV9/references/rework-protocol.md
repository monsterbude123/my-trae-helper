# 返工协议（Rework Protocol）

> V8 遗产。5 层深度判定 + 下游可操作重置清单。Reviewer 和 Implementer 共同执行。

## 5 层返工深度

| 层 | 问题范围 | 示例 | 回流目标 | 重走范围 | DOC SYNC 重置 |
|---|---------|------|---------|---------|:---:|
| L1 实现层 | 代码正确性 BUG / 测试不足 / lint | 逻辑错误、边界漏、覆盖率不足 | Implementer | Step 4-6 (TDD→DRIFT→量化) | 否 |
| L2 契约层 | 接口定义错误 / 数据模型不对齐 | API 路径错、字段类型错、事件名错 | Contract-Writer → Implementer | Phase 3→4 (Contract→Implement) | 是，重构契约文档 |
| L3 规格层 | Spec 描述错误 / 场景遗漏 / Acceptance 不完备 | Spec 缺边界场景、BDD 不完整 | Spec-Writer → Contract-Writer → Implementer | Phase 2→3→4 | 是，重写 Spec |
| L4 目标层 | define.md 目标偏差 / Capabilities 理解错误 | 做错了功能、Non-Goals 没覆盖 | Definer → Spec-Writer → ... | Phase 1→2→3→4 | 是，重写 Define |
| L5 UI/UX 层 | 视觉不对齐 / 交互逻辑不符原型 | 颜色错、组件位置错、交互顺序错 | Implementer (UI) | Step 4-6 (重写UI→Visual Gate) | 否 |

## 下游重置清单（L2+ 层必须执行）

```
[ ] 所有旧产物移到 _invalidated/（不可覆盖、不可修改）:
    spec.md  define.md  design.md  tasks.md  contracts/
    prototypes/design-prompt.md  prototypes/ui-ux-logic.md
    .state-card.md
[ ] 新产物从模板生成（不复制旧内容）:
    .state-card.md ← 空模板，只记录当前方向
    tasks.md ← 全部 [ ]，无历史勾选
    define.md ← 全新定义
    prototypes/ ← 从零重写，不引用旧版
[ ] _invalidated/ 盖上时间戳目录名: _invalidated/{YYYYMMDD-HHMM}/
[ ] 确认 agent 不读取 _invalidated/ 中的任何文件
```

## _invalidated/ 隔离规则（铁律 11 延伸）

```
方向变（用户重置/需求回撤/重构/Review L2+ 返工）:
  → 旧产物全量 mv → _invalidated/{timestamp}/
  → 新产物从模板生成
  → 禁止在原文件上编辑（看似省事，实则留下"已验收"标记噪音）

_invalidated/ 的定位:
  - 只可写入，不可读取 ← 硬规则
  - 对 agent 而言，_invalidated/ = 不存在
  - 对用户而言，_invalidated/ = 历史追溯（需要时手动查看）

禁止模式:
  ✗ 在原 spec.md 上追加 MODIFIED/REMOVED 段（修改旧文件）
  ✗ implementer 看到 tasks.md 有 [x] 就跳过（历史验收残留）
  ✗ reviewer 比对旧 define.md 和当前实现（旧状态干扰）
  ✗ spec-writer 复用旧 design-prompt.md 的部分内容

正确模式:
   ✓ 旧文件全部进 _invalidated/ + 新文件从零写
   ✓ tasks.md 全部 [ ]，implementer 逐项执行
   ✓ reviewer 只看当前 define.md 的任务和当前 Spec
   ✓ spec-writer 从零生成 design-prompt.md + ui-ux-logic.md
```

## _invalidated/ 防膨胀规则

```
每次写入 _invalidated/ 时:
  检查 _invalidated/ 下子目录数量
  → > 3 个时间戳目录 → 最旧的 mv archive/out/_invalidated/
  → 保持 _invalidated/ 干净（agent 扫不动大目录）
```

## 3 次上限

```
同一 change Review FAIL 3 次 → 🛑 标记 🔴 高风险，汇报用户
原因: 同一路径反复失败说明根本设计/理解有问题，不是执行问题
```

## 判定流程

```
Review FAIL
  ↓
判定层深:
  ├── 代码逻辑错误 / 测试不足 / lint → L1 → 退回 implementer 修复
  ├── API 签名/模型/事件不一致 → L2 → 退回 contract-writer 修正 → implementer 重实现
  ├── Spec 场景遗漏/描述错误 → L3 → 退回 spec-writer 重写 → contract → implement
  ├── define.md 目标偏差/Capabilities 理解错 → L4 → 退回 definer 重新定义 → spec → contract → implement
  ├── UI 视觉/交互不匹配 → L5 → 退回 implementer 修正 UI → Visual Gate 重跑
  └── 无法归类 → 汇报用户，请求人工判定
```
