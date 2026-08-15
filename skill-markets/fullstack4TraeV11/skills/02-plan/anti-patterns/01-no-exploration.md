# 反例 1：无探索直接规划

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 0 Plan 最常见反例。跳过 3 路探索直接写 plan.md。

## 现象

```
主上下文: 收到需求 → 直接写 plan.md
（未委派 3 路并行子代理探索）
```

**识别信号**:
- plan.md 无 "Evidence（3 路探索）" 段
- 未出现 docs_summary.json / code_summary.json / deps_summary.json
- 委派日志无 sub-agent 调用
- Capabilities 凭经验列出

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得"用户说啥就是啥" | 50% |
| 觉得探索浪费时间 | 30% |
| 不知道 V11 Plan 铁律 1 | 20% |

## 教训

**跳过探索 = 凭空设计 = 后续多次返工。**

真实案例（2026-08-07 蒸馏）:
- 用户要求"加个用户登录"
- 主上下文未探索，凭经验写 plan.md（Capabilities 写 5 项）
- 实际项目已有"用户认证"功能（archive/done/2026-07-15-user-auth/）
- Capabilities 重叠 80% → 浪费 1 天返工

## 正确替代

```
Step 0: Cockpit 读取
Step 1: 意图识别 + 选链
Step 2: 去重检查（扫描历史 change）
Step 3: 3 路并行子代理探索（文档 + 代码 + 依赖）
Step 4: 重构场景 → spec-purge
Step 5: 产出 plan.md
Step 6: 状态卡更新
```

**MUST**: Step 3 必走 3 路并行子代理探索（主上下文不直行）。

**NEVER**: 无 evidence 的 plan.md。

## 检测方法

```yaml
checklist:
  - [ ] docs_summary.json 存在？
  - [ ] code_summary.json 存在？
  - [ ] deps_summary.json 存在？
  - [ ] plan.md 含 "Evidence（3 路探索）" 段？
```

任一未勾选 → 触发本反例 → 回到 Step 3 重新探索。

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md) — EXPLORE FIRST
- [three-path-exploration.md](../workflows/three-path-exploration.md) — 3 路探索
