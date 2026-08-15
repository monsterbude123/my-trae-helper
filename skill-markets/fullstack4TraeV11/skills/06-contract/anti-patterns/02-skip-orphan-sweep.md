# 反例 2：跳过孤儿契约测试清理（Skip Orphan Test Sweep）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 写新契约前必跑 orphan-detector.py 清理悬挂测试。跳过 = 旧测试仍在 + 新契约测试失败被掩盖 + V10 腐烂点 12 复发。

**违反**：铁律 3（ORPHAN TEST SWEEP）
**严重度**：P1（直接导致腐烂点 12 复发 + Stage 4 Review 失败定位失真）

---

## 现象

```yaml
# Stage 2 流程（反例版本）

Step 1: 写新 api-contracts.md
  POST /api/v2/users  (v2 新契约)

Step 2: 写新契约测试
  tests/contracts/test_user_v2.py
  # 测试新 API 行为

Step 3: ❌ 未跑 orphan-detector.py
  # 旧契约测试 tests/contracts/test_user_v1.py 仍在
  # 测试的是 v1 API 行为（已废弃）

Step 4: 跑测试
  pnpm test
  # tests/contracts/test_user_v1.py 仍 PASS（孤儿测试）
  # tests/contracts/test_user_v2.py 也 PASS（新测试）
  # 看起来全 PASS，实际 v1 API 已无人调用，但测试仍在跑
```

**识别信号**:
- 写新契约前未跑 orphan-detector.py
- 旧契约对应的 API/事件/字段已删除/废弃，但测试未删除
- `pnpm test` 全 PASS 但实际包含已废弃功能的测试
- Stage 4 Review 时腐烂点 12（孤儿测试）报告 ≥ 5 个

---

## 根因

- **认知维度**：不知道"旧契约测试"算"腐烂"（视为"历史记录"）
- **流程维度**：跳过 orphan-test-sweep.md §Step 4 清理流程
- **工具维度**：未运行 orphan-detector.py 自动检测

| 根因 | 占比 |
|------|:---:|
| 视旧测试为历史记录（非腐烂）| 50% |
| 跳过 orphan-test-sweep §Step 4 | 30% |
| 未运行 orphan-detector.py | 20% |

---

## 教训

- **V11 实战**：v1 API 已废弃 6 个月，但 tests/contracts/test_user_v1.py 仍在。某次重构误改 v1 测试 → 测试仍 PASS（v1 已无人调用）→ 腐烂点 12 报告累积 8 个孤儿 → Stage 4 Review 大面积腐烂 → 紧急清理 + 返工 1 天
- **真实场景**：旧事件 `UserCreatedV1` 已被 `UserCreatedV2` 替换，但 `test_event_user_created_v1.py` 仍在测试 v1 schema。生产环境发 v1 事件时（bug）→ 测试仍 PASS → bug 被掩盖 → 数据格式错误传到下游
- **测试噪音反例**：100 个 contract test 中 30 个是孤儿（占 30%）。实施者改新契约时误改旧测试 → 旧测试失败 → 实施者以为是新契约问题 → 排错 4 小时

---

## 正确替代

```yaml
# ✅ 正确：Stage 2 必走 orphan-detector.py 流程

## Step 4 强制流程（orphan-test-sweep.md）

Step 4.1: 跑 orphan-detector.py 自动检测
  python scripts/orphan-detector.py
  # 输出: { orphan_count: N, orphan_tests: [...] }

Step 4.2: 审查 orphan 列表（contract-writer 必看）
  tests/contracts/test_user_v1.py::test_v1_schema       # v1 已废弃
  tests/contracts/test_order_v1.py::test_old_format    # 老格式已替换
  tests/contracts/test_payment_legacy.py::test_xml     # XML 改 JSON 后未删

Step 4.3: 决策（每个孤儿测试 4 选 1）
  - 删除（确认 v1 API 已无人调用）
  - 标记 deprecated（保留作回归测试，加 @deprecated 标记）
  - 迁移到 v2（重写测试以测试 v2）
  - 保留（确认仍有调用方）

Step 4.4: 清理后再写新契约
  # 此时已无孤儿测试 → 新契约测试不会被噪音掩盖

Step 4.5: 写新契约测试
  tests/contracts/test_user_v2.py::test_v2_schema

Step 4.6: 重跑 orphan-detector.py 验证
  # orphan_count: 0（理想）或仅 deprecated 标记的
```

```python
# ✅ orphan-detector.py 检测逻辑

def detect_orphan_tests():
    """
    1. 扫描 tests/contracts/ 所有测试
    2. 提取测试引用的契约元素（API path / event name / field）
    3. 检查契约元素是否在当前 api-contracts.md / events.md 中存在
    4. 不存在 → 标记为 orphan
    """
    contracts = load_active_contracts()  # 当前生效契约
    test_refs = extract_test_references()  # 测试中的契约引用

    orphans = []
    for ref in test_refs:
        if ref not in contracts:
            orphans.append(ref)

    return orphans
```

```yaml
# ✅ @deprecated 标记保留的合法模式

# tests/contracts/test_user_v1.py
"""
保留原因 (L8 决策): v1 API 仍有 3% 调用方（老客户），需逐步迁移
L9 计划: 2026-Q4 全部迁移后删除
"""
@pytest.mark.deprecated(reason="v1 迁移期保留")
def test_v1_schema():
    # 测试 v1 行为（确保迁移期兼容）
    ...
```

---

## orphan-test-sweep.md 强制流程

```yaml
# V11 Stage 2 强制执行
pre_condition:
  - 写新契约前必跑 orphan-detector.py
  - orphan_count > 0 → 必先清理

decision_matrix:
  - 删除: 确认无调用方（grep / 监控 / 客户反馈）
  - 迁移: 测试可重写以测试新契约
  - 保留: 含 @deprecated 标记 + 保留原因 + L9 计划

post_condition:
  - orphan_count == 0 或仅有 deprecated 标记
  - 重跑测试 → 全 PASS（无噪音）
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. Stage 2 提交前必跑 orphan-detector.py
2. orphan-detector.py 输出必含在 commit message
3. orphan_count > 0 无决策记录 → 🛑 REJECT
4. @deprecated 标记测试无保留原因 → � REJECT（视为死代码）
5. 新契约测试与旧孤儿测试并存 → �腐烂点 12 复发
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| 写新契约前未跑 orphan-detector | 腐烂点 12 累积 |
| 旧 API 已删但测试仍在 | 测试噪音 → bug 被掩盖 |
| 旧测试标 deprecated 但无保留原因 | 🛑 死代码（必删） |
| 旧测试改 PASS（v1 已无人调用）| 误导实施者以为兼容 |
| orphan_count 累积 ≥ 5 | Stage 4 Review 大面积腐烂 |

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — ORPHAN TEST SWEEP
- [orphan-test-sweep.md](../references/orphan-test-sweep.md) — §Step 4 清理流程
- [orphan-detector.py](../../../scripts/orphan-detector.py) — 自动检测工具
- V10 腐烂点 #12: 已蒸馏到本文档（V11 实战案例）
- 公共铁律 Article VIII: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
