# 视觉证据 3 层校验（Visual Evidence 3-Layer）

> Stage 3.5 Real Verify + Stage 4 Review 必走。V10 视觉证据铁律 + 项目级 `.trae/rules/视觉证据铁律.md` 蒸馏。

---

## 3 层校验

### Layer 1：文件存在 + Size 校验

```bash
# 截图文件 ≥ 5KB
ls -la docs/verifications/{change}/*.png | awk '$5 >= 5000 { print $NF }'
```

### Layer 2：PIL 解码 + PNG magic

```python
from PIL import Image
img = Image.open(path)
img.verify()  # PIL 解码验证
```

### Layer 3：直方图 + 关键区域采样

```python
# 平均亮度不在 30-240 范围 = ⚠️ 警告
hist = img.histogram()
avg_brightness = sum(i * h for i, h in enumerate(hist[:256])) / sum(hist[:256])
assert 30 <= avg_brightness <= 240, "截图过暗或过亮"
```

### 文件活跃性

- 截图 ≤ 7 天（避免过期证据）

---

## 主上下文亲自 Read

**V10 视觉证据铁律**: 主上下文必亲自 Read 截图（PNG 像素验证）。

**反模式**: 子代理"已截图"→ 不 Read → 声称完成。

---

## 关联引用

- [SKILL.md §铁律 6](../SKILL.md) — 主上下文必查
- V10 项目级 `.trae/rules/视觉证据铁律.md`（已蒸馏到本文档）
- V10 visual-content-check.py: `V10 来源` (已蒸馏到本文档)
