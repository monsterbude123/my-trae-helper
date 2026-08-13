---
name: fullstack-05-prototype
description: "Stage 1.5 双源兼容原型 — 设计稿 + 代码原型必一致。触发词：prototype / 原型 / 设计稿 / UI 验证。"
stage: 1.5
parent: fullstack4traev11
depends_on:
  skills: [ui-ux-pro-max]
  stages: [1/spec]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
  scripts:
    - ../../scripts/stage-gate.py
---

# Stage 1.5 Prototype — 双源兼容原型

> 第一性原则：**原型是规格的视觉表达，双源必须一致**。设计稿和代码原型互相校验。

## 铁律（7 条 — V11.2 NEW 加 1 条双产物）

```
1. 双源一致        — 设计稿 ↔ 代码原型必须互相校验
2. prototype-reverse-spec — 代码可反向追溯 spec
3. designer-handoff — 设计师移交时必含交互说明
4. NEVER 跳过双源 — UI 改动必走双源校验
5. GAP 标注        — 原型与 spec 不一致必标 GAP
6. prototype 必含 E2E 截图证据
7. 双产物必产(UI 涉及时)(V11.2 NEW — 蒸馏自 V10) — spec-writer 涉及 UI 时必产 design-prompt.md + ui-ux-logic.md,5 状态 + 4 项最低门禁;纯后端/API/CLI 跳过
```

## 骨架流程（5 步）

```
Step 1: 加载 spec.md → 识别 UI 相关 AC
Step 2: 设计稿准备（Figma / Sketch / 截图）
Step 2.5: design-prompt.md + ui-ux-logic.md 双产物(UI 涉及时)(V11.2 NEW — 蒸馏自 V10)
  - spec-writer 必产 2 份文档到 docs/specs/changes/{id}/prototypes/:
    1. design-prompt.md(Trae Work 生成视觉原型的提示词,5 状态 + 响应式断点)
    2. ui-ux-logic.md(开发者用交互逻辑,组件树 + 交互流 + 状态管理)
  - 最低门禁: design-prompt 5 状态全覆盖 + ui-ux-logic 组件树 ≥1 / 交互流 ≥2 / 状态表 ≥3 / 错误处理 ≥3
  - 详见 [references/prototype-dual-source.md](references/prototype-dual-source.md) + [templates/design-prompt.md](templates/design-prompt.md) + [templates/ui-ux-logic.md](templates/ui-ux-logic.md)
Step 3: 代码原型（最小可运行 demo）
Step 4: 双源校验（设计稿 vs 代码截图）
Step 5: prototype 文档产出（含 GAP 标注）
```

## 关键产物

| 产物 | 路径 | 说明 |
|------|------|------|
| design-prompt.md | `docs/specs/changes/{id}/prototypes/design-prompt.md` | Trae Work 生成视觉原型的结构化提示词(5 状态 + 响应式断点 + 组件清单 + 视觉风格) |
| ui-ux-logic.md | `docs/specs/changes/{id}/prototypes/ui-ux-logic.md` | 交互逻辑(组件树 + 交互流 + 状态管理 + 错误边界) |
| HTML 原型 | `docs/specs/changes/{id}/prototypes/design.{html,png,fig}` | Trae Work 按 design-prompt.md 生成的视觉原型 |
| HANDOFF 索引 | `docs/HANDOFF-DESIGNER.md` | Designer ↔ spec-writer 双向映射(三态处理 + 去重统计) |

## 反例

| # | 反例 | 详细 |
|:---:|------|------|
| 1 | 设计稿与代码脱节 | [anti-patterns/01-design-code-mismatch.md](anti-patterns/01-design-code-mismatch.md) |
| 2 | 跳过双源校验 | [anti-patterns/02-skip-dual-source.md](anti-patterns/02-skip-dual-source.md) |
| 3 | prototype 写实现 | [anti-patterns/03-prototype-as-impl.md](anti-patterns/03-prototype-as-impl.md) |

## 参考索引

- [README.md](README.md)
- [dual-source-protocol.md](references/dual-source-protocol.md)
- [prototype-code-gap.md](references/prototype-code-gap.md)
- [prototype-template.md](templates/prototype-template.md)
