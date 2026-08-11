# 孤儿契约测试扫描（Orphan Contract Test Sweep）

> Stage 2 Contract Step 4 必走。V10 腐烂点 12 修复。

---

## V10 腐烂点 12（rot #12）

**症状**: `__tests__/contracts/` 中存在引用旧契约 API 的测试，但旧契约已被删除或重命名。导致测试失败但原因不明。

**根因**: 删除/重命名契约 API 时，未同步清理契约测试。

**修复**: 写新契约前必跑 orphan-detector.py，输出孤儿清单 + Plan 含 "Delete obsolete tests" 任务。

---

## orphan-detector.py 用法

```bash
# 扫描孤儿契约测试
python ../../scripts/orphan-detector.py --type contract --output orphans.json

# 输出示例
{
  "scan_at": "2026-08-11T14:30:00",
  "orphans": [
    {
      "test_file": "__tests__/contracts/test_old_login.test.ts",
      "references": ["POST /api/v1/auth/login_v1"],
      "exists_in_contracts": false,
      "action": "delete"
    }
  ],
  "stats": {"total_tests": 30, "orphans": 1, "valid": 29}
}
```

---

## 处置流程

```
Step 4: orphan-detector.py 扫描
  ├─ orphans.json: 0 项 → 直接进入 Step 5
  └─ orphans.json: N 项 →
      ├─ 列出孤儿清单（含 test_file + references）
      ├─ 询问用户：删除 or 修复引用？
      │   ├─ 删除 → 移入 __tests__/contracts/_deprecated/
      │   └─ 修复 → 更新测试引用新契约
      └─ 验证扫描再次为 0 → 进入 Step 5
```

---

## 反例

### 反例 A：未扫直接写新契约

```
主上下文: 写新契约 → 新契约测试骨架 → 提交  # ❌ 旧孤儿仍在
正确: orphan-detector.py → 清理 → 再写
```

### 反例 B：删 API 未删测试

```
主上下文: 删 /api/v1/old_login → 旧测试保留  # ❌ rot #12
正确: 删 API + 删测试（或移入 _deprecated/）
```

---

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — ORPHAN TEST SWEEP
- [contract-four-suite.md](contract-four-suite.md)
- V10 rot #12 详情: `V10 来源` (已蒸馏到本文档)
