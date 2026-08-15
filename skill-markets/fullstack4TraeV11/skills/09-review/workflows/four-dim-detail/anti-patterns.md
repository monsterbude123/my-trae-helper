# 反例（3 条）— four-dim-acceptance.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
> 来源：原 four-dim-acceptance.md 第 203-224 行（保留信息密度）

---

## 反例

### 反例 A：凑分

```
代码 3.0 / API 4.0 / UIUX 2.5 / 边际 3.0 → 总分 3.1  # ❌
正确: 任一维度 0 分 = REJECT
```

### 反例 B：reviewer 改代码

```
reviewer: 发现代码 bug → 直接 Edit  # ❌ REVIEWER DOES NOT FIX
正确: 退回 implementer 修改
```

### 反例 C：边际维度只跑 impact() 不跑 detect_changes / 全量回归 / 模块文档

```
reviewer: 边际证据只有 `gitnexus_impact` 一行  # ❌ V10 完整 4 项
正确: 必跑 detect_changes + impact + 公共模块 + 全量回归 + 模块文档
```

---

## 关联引用

- 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
