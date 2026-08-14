# skill4Trae — 懒惰高级开发模式 for TRAE IDE

> 此文件是给 AI 代理（TRAE）的使用说明书。告诉你在什么情况下应该加载哪个 skill。

---

## 三角心法互引（2026-08-14 收敛说明）

| 关注维度 | 推荐加载 | 本聚合覆盖 |
|---------|---------|------------|
| **通用编码心法 + 精简 Goal Mode + 表达风格** | [`coding-xinfa`](../coding-xinfa/SKILL.md) | 不重复（独立 skill） |
| **目标追逐完整协议 + 六步审计门禁 + Agent 编排** | [`goal-mode`](../goal-mode/SKILL.md) | 不重复（独立 skill） |
| **懒人开发模式 + 过度工程审查 + ponytail: 技术债分类账 + 快速参考** | **本聚合（`trae-ponytail` 等 4 子 Skill）** | 全文 |

**循环互引消除原则**：
- 本聚合的 4 个子 Skill（`trae-ponytail` / `-review` / `-debt` / `-help`）不引用 `coding-xinfa` 或 `goal-mode` 的全文，避免双向耦合。
- 用户触发"用懒人模式"/"过度工程"/"技术债盘点" → 加载本聚合。
- 用户触发"目标追逐"/"完成审计" → 加载 `goal-mode`（不在本聚合重复）。
- 用户触发"通用风格"/"改动要小" → 加载 `coding-xinfa`（不在本聚合重复）。

---

## 可用 Skills 总览

本项目为 TRAE IDE 提供三个独立 skill，每个都完整内聚、可单独使用：

| Skill                  | 用途                                    | 触发词                                                   |
| ---------------------- | --------------------------------------- | -------------------------------------------------------- |
| `trae-ponytail`        | 在你写代码时切换到懒惰高级开发模式      | "懒人模式"、"简化一下"、"用最少的代码"、"ponytail"       |
| `trae-ponytail-review` | 审查已有代码中是否有过度工程            | "审查一下"、"有没有过度设计"、"有什么可以删的"、"review" |
| `trae-ponytail-debt`   | 盘点项目中所有 `ponytail:` 标记的技术债 | "看看技术债"、"盘点标记"、"有哪些简化点"、"debt"         |

---

## 何时加载哪个 Skill

### 场景一：用户要你写代码

**你首先应该判断用户意图**：

```
用户说：                    → 你应该：

"帮我写一个防抖函数"          → 不加载任何 skill，直接写
"用最少的代码实现防抖"        → 加载 trae-ponytail，按决策阶梯来
"用懒人模式写这个功能"        → 加载 trae-ponytail
"用 ponytail 模式"            → 加载 trae-ponytail
"简化这段代码"                → 加载 trae-ponytail
```

**关键判断标准**：如果用户明确表达"想偷懒"、"用最少代码"、"不要过度工程"、"ponytail"、"懒人"——加载 `trae-ponytail`。

### 场景二：用户要审查代码

```
用户说：                    → 你应该：

"帮我审查一下这段代码"        → 判断：是找 bug 还是找过度工程？
  如果是找过度工程           → 加载 trae-ponytail-review
  如果是找 bug/安全问题       → 加载 TRAE-code-review 或 TRAE-security-review

"看看这里有没有过度设计"      → 加载 trae-ponytail-review
"有没有可以删掉的东西"        → 加载 trae-ponytail-review
"review over-engineering"     → 加载 trae-ponytail-review
"审查一下这个 PR"             → 先加载 trae-ponytail-review 看过度工程
                               再加载 TRAE-code-review 看正确性
```

### 场景三：用户要盘点技术债

```
用户说：                    → 你应该：

"看看有哪些技术债"            → 判断：是泛指所有技术债还是 ponytail 标记的？
  如果是 ponytail 标记的     → 加载 trae-ponytail-debt
  如果是泛指                 → 直接通过代码搜索来找

"有哪些 ponytail 标记的简化点" → 加载 trae-ponytail-debt
"盘点 pomytail 注释"           → 加载 trae-ponytail-debt
"check ponytail debt"          → 加载 trae-ponytail-debt
```

### 场景四：用户不确定，想了解有什么可用

```
用户说：                    → 你应该：

"有什么 skill 可以用"                     → 加载 trae-ponytail-help（快速参考卡）
"ponytail 怎么用"                         → 加载 trae-ponytail-help
"帮我看看怎么简化"                        → 先加载 trae-ponytail-help 让用户选择
```

---

## Skill 组合使用指南

### 工作流一：日常开发

```
1. 用户："用懒人模式帮我写这个 XXX 功能"
2. 你加载 trae-ponytail → 按决策阶梯写出最简代码 → 标注 ponytail: 注释 → 加自检
3. （可选）用户："审查一下刚写的有没有过度设计" → 加载 trae-ponytail-review
```

### 工作流二：重构前评估

```
1. 用户："我想重构这个模块，先看看有哪些可以删的"
2. 你加载 trae-ponytail-review → 审查指定文件 → 输出简化建议清单
3. 用户选择哪些要简化
4. 你加载 trae-ponytail → 按最简方案实现
```

### 工作流三：技术债健康检查

```
1. 用户："定期盘点一下技术债"
2. 你加载 trae-ponytail-debt → grep 全仓库 → 输出分类账
3. 用户看到几个"无触发条件"的高风险标记 → 补充升级路径
4. 用户看到一些已经到了天花板 → 加载 trae-ponytail → 升级
```

---

## 自动加载判断逻辑

当用户说话时，先过一遍这个判断树：

```
1. 话语中包含 "ponytail"、"懒人"、"懒惰"、"最简"、"最少代码"、"能不做就不做"？
   └─ 是 → 加载 trae-ponytail

2. 话语中包含 "审查"、"review"、"过度"、"可以删"、"能简化"？
   └─ 是 → 判断是找过度工程还是找 bug
          ├─ 过度工程 → 加载 trae-ponytail-review
          └─ bug/安全  → 加载 TRAE-code-review / TRAE-security-review

3. 话语中包含 "技术债"、"债务"、"debt"、"ponytail 标记"、"盘点标记"？
   └─ 是 → 加载 trae-ponytail-debt

4. 话语中包含 "ponytail 怎么用"、"有哪些 skill"、"help"？
   └─ 是 → 加载 trae-ponytail-help

5. 用户写代码的需求感觉太复杂、想引入新依赖？
   └─ 主动建议："要不要用 ponytail 懒人模式？也许标准库就够了。"
      如果用户同意 → 加载 trae-ponytail

6. 用户让你审查一段看起来很复杂的代码？
   └─ 主动建议："要不要用 ponytail 审查一下有没有过度设计？"
      如果用户同意 → 加载 trae-ponytail-review
```

---

## 重要原则

1. **不要自动加载**：除非用户的意图明确，不要主动加载 skill。等用户确认。
2. **可以主动建议**：当你觉得某个 skill 能帮到用户时，主动提议，让用户决定。
3. **三个 skill 独立**：每个 skill 都是完整独立的，不需要同时加载多个。
4. **加载后立即生效**：skill 加载后注入 rules 到当前会话，后续所有输出都受影响。
5. **会话结束就失效**：skill 只在当前会话中生效。新会话需要重新加载。
