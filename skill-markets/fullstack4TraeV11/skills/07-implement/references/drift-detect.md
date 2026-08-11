# 漂移检测（Drift Detect）

> Stage 3 Implement Step 3 DRIFT CHECK 必走。V10 implementer 铁律 3 + drift-detect.md 蒸馏。

---

## DRIFT CHECK 流程

```
🔍 DRIFT CHECK 触发时机:
  ├─ 每完成 1 个 TDD 循环后
  ├─ 提交前
  └─ Stage 4 Review 前
  ↓
对照 contracts/ 验证:
  ├─ 接口签名一致？（method / path / params）
  ├─ 字段类型一致？（string / number / bool）
  ├─ 错误码一致？（V10 D-009 错误码规范）
  ├─ 必填字段一致？
  └─ 鉴权要求一致？
  ↓
任一不一致 → 立即报告回流（不静默修改）
```

---

## 漂移处置流程

```
检测到漂移:
  ├─ 是契约问题（契约与 spec 不一致）？
  │   └─ 是 → 报告用户 → 更新契约（走 BREAKING 流程）
  └─ 是实现问题（代码与契约不一致）？
      └─ 是 → 立即修代码（不改契约）
```

**V10 铁律 3**: 漂移必报告，禁止静默。

---

## DRIFT CHECK 工具

```bash
# 自动检测接口签名漂移
python ../../scripts/drift-detect.py --contracts contracts/ --src src/

# 输出
{
  "drift_count": 3,
  "drifts": [
    {
      "contract": "POST /api/v1/auth/login",
      "field": "password",
      "contract_type": "string",
      "code_type": "any",
      "severity": "high"
    }
  ]
}
```

---

## 反例

### 反例 A：静默修改契约

```
实现改了接口 → 不更新契约文档 → 测试通过 → 上线后客户端报错
正确: 实现与契约不一致 → 报告用户 → 走 ADDITIVE/BREAKING 流程
```

### 反例 B：契约与代码双向漂移

```
契约改了 → 实现未跟进 → 测试通过（mock）→ 上线后真实环境失败
正确: 契约修改必同步代码 + 测试（V10 配置治理 D-009 三方同步）
```

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — 漂移必报告
- [tdd-workflow.md](tdd-workflow.md)
- V10 drift-detect.md: `V10 来源` (已蒸馏到本文档)
