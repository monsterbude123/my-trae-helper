# 反例 2：扫完不改（fix-list.json 空）

> rot-scan 跑完 fix-list.json 必产出且不可空。来源：V11 Article XIV.3 + V10 process-rot-analysis.md。

## 现象

```bash
# ❌ 反例
proactive-scan.py → 输出 rot-scan-{date}.json（10 项 PASS）→ fix-list.json 是空 []
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得"全 PASS 不用 fix" | 50% |
| 不知道 fix-list.json 必填 | 30% |
| 输出格式错 | 20% |

## 教训

**fix-list.json 不可空**的含义：
- 即使 10 项 PASS → 必含"N/A 理由"或"低优改进"
- 空 fix-list = 扫描未真跑 或 必填漏项

**V11 Article XIV.3**：fix-list.json 必产出且不可空。

## 正确替代

```json
// docs/reports/fix-list-{date}.json
{
  "scan_date": "2026-08-11",
  "rot_scan_results": {
    "visual": "PASS",
    "archive": "PASS",
    "self_attest": "PASS",
    "orphan_tests": "PASS",
    "bundle_staleness": "PASS",
    "self_aggrandizing": "PASS",
    "state_card_staleness": "PASS",
    "stub_pileup": "PASS",
    "obstacle_honesty": "PASS",
    "reason_fabrication": "PASS"
  },
  "fix_list": [
    {
      "id": "FIX-001",
      "priority": "P3",
      "category": "code-hygiene",
      "description": "src/legacy/auth.ts 单文件 850 行（超 800 行）",
      "fix": "按 module 拆分（可后续 P3）",
      "owner": "implementer",
      "deadline": "next-sprint"
    }
  ],
  "summary": "10/10 PASS + 1 P3 改进项"
}
```

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — fix-list.json 空
- [proactive-scan.py 文档](../../../../scripts/proactive-scan.py)
- V11 Article XIV.3
- V10 来源: `../../../../fullstack4TraeV10/references/process-rot-analysis.md`