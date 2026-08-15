# 双源兼容协议（Dual-Source Protocol）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 1.5 Prototype 核心协议。设计稿 + 代码原型双源必须一致。

## 协议

```
设计稿 ──→ 截图比对 ──→ 一致？
                              ├─ 是 → 通过
                              └─ 否 → GAP 标注 + 修复
代码原型 ──→ 截图比对 ──→ 一致？
```

## prototype-reverse-spec

代码原型必可反向追溯 spec.md AC：
- 每个 UI 元素标注对应的 AC ID
- 缺失 UI 元素 → spec 不全
- 多余 UI 元素 → prototype 越界

## 详细参考

详见 [prototype-code-gap.md](prototype-code-gap.md)。
