# 代码卫生（Code Hygiene）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 3 Implement 必走。V10 implementer 铁律 6 + Ponytail First。

---

## 硬指标

| 指标 | 门槛 | 检测 |
|------|:---:|------|
| 单文件行数 | ≤ 800 | code-hygiene.py |
| 函数行数 | ≤ 50 | code-hygiene.py |
| 魔法数字 | 0 | code-hygiene.py |
| L0/L1 外置 | 100% | code-hygiene.py |

---

## 拆分原则（Ponytail First）

- 函数超过 50 行 → 拆函数
- 文件超过 800 行 → 拆模块
- 重复代码 ≥ 3 处 → 提取公共函数
- 复杂条件 → 提取为命名函数

---

## L0/L1 外置（V10 硬编码治理）

| Level | 类别 | 处置 |
|:---:|------|------|
| L0 | API Key / Token / Secret | ❌ 严禁；走 DB → env 二级 fallback；`mask_key()` 遮蔽 |
| L1 | 第三方服务 URL | ⚠️ 外置到 `config.toml` provider registry |
| L2 | 端口号 | ✅ `default_*()` + env 覆盖 |
| L3 | 文件路径 | ✅ `dirs::data_dir()` + env 覆盖 |
| L4 | URL placeholder | ✅ 占位符合理 |

详见 `.trae/rules/硬编码治理.md`（V10 蒸馏；项目可按需创建）。

---

## 反例

### 反例 A：800+ 行单文件

```
src/auth/user_service.py: 1200 行  # ❌
正确: 拆为 user_service / auth_token / session 模块
```

### 反例 B：魔法数字

```python
if retry_count > 3:  # ❌ 魔法数字
正确: MAX_RETRY = 3
if retry_count > MAX_RETRY:
```

### 反例 C：硬编码 API Key

```python
<!-- scan-whitelist -->api_key = "sk-1234567890"  # ❌ L0 硬编码<!-- /scan-whitelist -->
正确: api_key = os.environ["API_KEY"]
```

---

## 关联引用

- [SKILL.md §铁律 6](../SKILL.md) — 代码卫生
- V10 `.trae/rules/硬编码治理.md`（已蒸馏到本文档）
- V10 implementer.md 铁律 6: `V10 来源` (已蒸馏到本文档)