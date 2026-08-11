---
name: prototype
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

## 铁律（6 条）

```
1. 双源一致        — 设计稿 ↔ 代码原型必须互相校验
2. prototype-reverse-spec — 代码可反向追溯 spec
3. designer-handoff — 设计师移交时必含交互说明
4. NEVER 跳过双源 — UI 改动必走双源校验
5. GAP 标注        — 原型与 spec 不一致必标 GAP
6. prototype 必含 E2E 截图证据
```

## 骨架流程（5 步）

```
Step 1: 加载 spec.md → 识别 UI 相关 AC
Step 2: 设计稿准备（Figma / Sketch / 截图）
Step 3: 代码原型（最小可运行 demo）
Step 4: 双源校验（设计稿 vs 代码截图）
Step 5: prototype 文档产出（含 GAP 标注）
```

## 关键产物

| 产物 | 路径 |
|------|------|
| prototype.md | `docs/specs/changes/{id}/prototype.md` |
| 设计稿 | `docs/specs/changes/{id}/prototypes/design.{png|fig}` |
| 代码原型 | `prototypes/{id}/` |

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
