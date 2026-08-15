# 10 项扫描协议（Scan Protocol）

> Stage 4.5 Rot Scan Step 1 必走。V10.5 8 项 + V10.10 +2 项（obstacle-honesty + reason-fabrication）。

---

## 扫描流程

```bash
# 跑全部 10 项扫描
python ../../scripts/proactive-scan.py --output docs/reports/rot-scan-{date}.md

# 输出示例
{
  "scan_at": "2026-08-11T14:30:00",
  "checks": [
    {"id": 1, "name": "visual", "status": "PASS", "items": 5},
    {"id": 2, "name": "archive", "status": "PASS", "items": 0},
    {"id": 3, "name": "self-attest", "status": "FAIL", "items": 1, "details": "..."},
    {"id": 4, "name": "orphan-tests", "status": "PASS", "items": 0},
    {"id": 5, "name": "bundle-staleness", "status": "PASS", "items": 0},
    {"id": 6, "name": "self-aggrandizing", "status": "PASS", "items": 0},
    {"id": 7, "name": "state-card-staleness", "status": "FAIL", "items": 1},
    {"id": 8, "name": "stub-pileup", "status": "PASS", "items": 0},
    {"id": 9, "name": "obstacle-honesty", "status": "PASS", "items": 0},
    {"id": 10, "name": "reason-fabrication", "status": "PASS", "items": 0}
  ],
  "stats": {"total_checks": 10, "passed": 8, "failed": 2}
}
```

---

## 10 项详细

### Check 1: 视觉腐烂

- 截图 ≥5KB + ≤7 天
- PIL 解码 + 直方图校验

### Check 2: 归档腐烂

- `archive/` 不可修改
- git diff archive/ 应为空

### Check 3: 自验腐烂

- reviewer 必亲自跑测试（不自评）
- coverage 命令必跑

### Check 4: 孤儿测试

- orphan-detector.py
- 删除 API 时同步删测试

### Check 5: Bundle Staleness

- 改 TS 后 dist/ 必重生成
- dist-hash-check.py

### Check 6: 吹嘘腐烂（self-aggrandizing）

- 报告说"全部通过"但实际有 FAIL
- reason-classifier.py 检测 6 类抽象理由

### Check 7: 状态卡腐烂

- state-card-staleness
- updated_at ≥30 分钟前

### Check 8: 骨架腐烂

- stub-pileup 扫描
- `.bak` / `.old` / `STUB:` 标记

---

## 修复清单

```bash
# 输出 fix-list.json
python ../../scripts/proactive-scan.py --output-fix-list docs/reports/fix-list.json

{
  "fixes": [
    {
      "id": 3,
      "name": "self-attest",
      "severity": "HIGH",
      "fix_action": "reviewer 必亲自跑 pytest --cov"
    }
  ]
}
```

---

## 关联引用

- [SKILL.md §铁律 5](../SKILL.md)
- [rot-classification.md](rot-classification.md)
- V10 proactive-scan.py: `V10 来源` (已蒸馏到本文档)
