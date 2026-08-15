# 反例 1：无意图识别直接动手

> Stage -1 Intake 最常见的反例。收到用户需求立即写 spec / 改代码，跳过意图识别。

---

## 现象

```
用户: "我想加一个用户登录功能"
主上下文: 立即打开 skills/04-spec/SKILL.md → 开始写 spec.md
（或者更糟：直接打开 IDE 改代码）
```

**识别信号**:
- 用户输入 → 主上下文直接进入 spec / plan / implement 阶段
- 状态卡未初始化（无 current_stage 字段或为 null）
- next_stage 字段缺失或未填写
- 路由决策无 evidence

---

## 根因

| 根因 | 占比 | 说明 |
|------|:---:|------|
| 觉得"用户说啥就是啥" | 60% | 不假思索，自信"听懂"了 |
| 觉得意图识别是"冗余步骤" | 25% | 节省 Intake 工作量 |
| 不知道 V11 §0.5 加载协议要求 | 15% | 不熟悉 SKILL.md 强制流程 |

---

## 教训

**跳过意图识别 = 路由错误概率上升 → 后续 stage 全部返工。**

真实案例（2026-08-07 蒸馏）:
- 用户说"重构一下 auth 模块" → 主上下文直接写 spec（未识别为 refactor）
- 实际意图：change-start (refactor) → 应走 Stage 0 Plan → Stage 1 Spec (REFACTOR 模式)
- 结果：spec.md 写成新建功能规范，与重构意图不符 → 返工 3 轮

---

## 正确替代

```
Step 1: 接收用户输入
Step 2: 触发词扫描（5 种意图分类）
  ├─ 命中 → 直接路由（写状态卡 next_stage）
  └─ 未命中 → AskUserQuestion（5 选 1）
Step 3: 初始化状态卡（project / change / bug）
Step 4: 交接下一 stage
```

**MUST**: 永远先识别意图（5 种类型），不确定就 AskUserQuestion。

**NEVER**:
- ❌ 不识别意图直接进 spec / plan / implement
- ❌ 跳过状态卡初始化
- ❌ AskUserQuestion 用经验主义臆断（违反 Article XVI §1.4 质疑性校验）

---

## 检测方法

主上下文每收到用户输入时自检：

```yaml
checklist:
  - [ ] 已识别意图类型？（5 种之一）
  - [ ] 已填写状态卡 next_stage？
  - [ ] 状态卡 health 字段已设置？
  - [ ] 路由决策有 evidence（触发词 / AskUserQuestion 选项）？
```

任一未勾选 → 触发本反例 → 回到 Step 2 重新识别。

---

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md) — 意图不明不路由
- [SKILL.md §铁律 5](../SKILL.md) — 路由决策不臆断
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [intent-types.md](../references/intent-types.md) — 5 种意图类型详解
- [routing-decision-tree.md](../references/routing-decision-tree.md) — 路由决策树
