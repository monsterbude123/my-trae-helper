# Gate 判定标准

> 来源：CC Studio Director Gates
> 关联：game-quality-gate SKILL.md §Gate 判定逻辑, §审查模式, §铁律

## §1 三态 Verdict 定义

| Verdict | 含义 | 判定标准 |
|---------|------|---------|
| **APPROVE** | 通过 | 自动化检查项 + CoV 5 问 全部满足阈值，无降级 |
| **CONCERNS** | 有风险通过 | 某项接近阈值但未超过 / CoV 自问有"是"但非致命 / 人工确认时用户标注"已知风险" |
| **REJECT** | 阻断 | 任一检查项未达阈值 / CoV 自问发现漏检/不同步 / 素材肉眼可见不合格 |

> CONCERNS 不是"轻微问题"的垃圾桶。连续 3 次同一项 CONCERNS → 自动升级为 REJECT。

## §2 阻断规则

```
REJECT 处理流程（不可跳过、无例外）：
  1. 打印 REJECT 项清单 + 失败阈值对比
  2. 🛑 阻断构建，不得进入 Phase 5
  3. 回退 Phase 2（素材重新生成）
  4. 修复后重新跑完整 Gate（不得只重跑 FAIL 项）
  5. Gate 再次通过后才可继续
```

| 场景 | 是否可跳过 | 审批人 |
|------|-----------|--------|
| 单个立绘尺寸不匹配 | ❌ 不可跳过 | — |
| BGM 文件大小为 0 | ❌ 不可跳过 | — |
| "赶时间，先发布再说" | ❌ **无例外条款** | — |

## §3 CONCERNS 处理流程

```
1. 自动化检查全部通过，但 CoV 自问触发 CONCERNS
   → 输出问题清单（每项标注：检查项名 / 当前值 vs 阈值 / 风险描述）
2. 用户决策：
   ├─ "修复" → 回退 Phase 2 改正具体项 → 重跑 Gate
   └─ "接受并继续" → 继续 §3
3. 接受后：
   - 记录到 .project-state-card.md 的风险区
   - 格式：{检查项} | CONCERNS | {当前值} | {阈值} | {日期} | {用户确认}
   - 下次 Gate 运行时自动复查该 CONCERNS 项
```

## §4 整体状态推导

```
Gate FAIL 汇总分两区：

REJECT 区（阻断项）:
  → 直接加入修复清单，必须回退 Phase 2 改正

CONCERNS 区（风险项）:
  → 单独列出，不自动加入修复清单
  → 询问用户是否修复后继续

────────────────────────
全部 APPROVE                → 🟢 通过，进入 Phase 5
任一 REJECT                 → 🔴 阻断，必须回退 Phase 2
任一 CONCERNS（无 REJECT）   → 🟡 有风险通过
  └─ CONCERNS 项不自动加入修复清单，询问用户是否修复后继续
  └─ solo 模式下 CONCERNS → 自动降为 REJECT（无人确认风险）
```

## §5 Gate 模式矩阵

| 维度 | full | lean（默认） | solo |
|------|------|-------------|------|
| 自动化检查 | ✅ 全部 | ✅ 全部 | ✅ 全部 |
| Chain-of-Verification | ✅ 5 问 | ✅ 5 问 | ❌ 跳过 |
| 人工确认 | ✅ 逐项 verdict | ✅ 整体 PASS/FAIL | ❌ 跳过 |
| CONCERNS 处理 | 用户逐项决策 | 用户整体决策 | 自动降 REJECT |
| 证据要求 | quality-report.md + 截图 | quality-report.md | 终端输出 |
| 适用场景 | 正式发布、团队协作 | 个人项目、快速迭代 | 原型验证、极速构建 |

## §6 跨引擎差异表

> 素材属性检查（§自动化检查项）引擎无关。以下为各引擎**特有**附加检查项占位。

| 引擎 | 特有检查项 | 实现方式 | 状态 |
|------|-----------|---------|:---:|
| WebGAL | scene 文件 JSON schema 校验 / 变量未定义引用 | `scripts/validate_scenes.py` | 规划中 |
| Godot | .tscn 资源引用完整性 / AnimationPlayer 关键帧范围 | `--headless --script check.gd` | 规划中 |
| Unity | Prefab 嵌套层级 / missing script 检测 | EditMode Test Runner | 规划中 |
| Unreal | Blueprint 编译错误 / Niagara 资产引用 | Commandlet | 规划中 |
| Bevy | 组件注册完整性 / system schedule 顺序校验 | `cargo test --test gate` | 规划中 |
| Babylon | .gltf 导出参数 / 材质 missing texture fallback | `scripts/validate_babylon.py` | 规划中 |

> 通用游戏逻辑测试维度见 `references/02-game-logic-checks.md`。
