# 原型-代码差距分析（Prototype-Code Gap）

> Stage 1.5 Prototype 双源校验时识别 GAP 的方法。

## GAP 类型

| GAP | 含义 | 处置 |
|-----|------|------|
| 设计稿有 / 代码无 | 设计师设计了但代码原型未实现 | 补代码原型 |
| 设计稿无 / 代码有 | 代码原型多余 | 移除 / 标注"待设计" |
| 两者都有但不一致 | 颜色 / 间距 / 交互不同 | designer-handoff 澄清 |

## designer-handoff

设计师移交时必含：
- 设计稿（Figma / Sketch）
- 交互说明（hover / active / focus 状态）
- 设计 token（颜色 / 间距 / 字号）
- 边缘情况（loading / error / empty）

> **Article 锚定**: Article V Verifiable Claims(设计稿+交互+token+边缘情况 = 可验证的设计契约)+ Article IX Cross-Session Verify(设计师 ↔ 工程师双向交叉)。

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — designer-handoff
- [dual-source-protocol.md](dual-source-protocol.md)
