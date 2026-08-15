# Rot Detect and Fix — Stage 4.5

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 4.5 Rot Scan 必走。腐化扫描 + 修复协议。

---

## 流程

```
Step 1: 跑 proactive-scan.py 10 项扫描
  └─ 输出 docs/reports/rot-scan-{date}.md

Step 2: 跑 self-diagnose.py 元检测
  └─ 检查 rot-detector 自身腐化

Step 3: 输出 fix-list.json
  └─ 每项含 type/severity/fix_action

Step 4: 全部 PASS → 进入 Stage 5 Accept
  └─ 任一 FAIL → 🛑 REJECT
```

---

## 10 项扫描（V10.10）

| # | 检查项 | 检测脚本 |
|:---:|------|---------|
| 1 | 视觉腐烂（截图 ≥5KB + 7 天内）| visual-content-check.py |
| 2 | 归档腐烂（archive/ 不可变）| proactive-scan.py §2 |
| 3 | 自验腐烂（自评 vs 抽检）| proactive-scan.py §3 |
| 4 | 孤儿测试腐烂（rot #12）| orphan-detector.py |
| 5 | 构建腐烂（Bundle Staleness）| dist-hash-check.py |
| 6 | 吹嘘腐烂（state-card vs 实际）| proactive-scan.py §6 |
| 7 | 状态卡腐烂（state-card-staleness）| state-card-validator.py |
| 8 | 骨架腐烂（rot #13 stub 堆积）| proactive-scan.py §8 |
| 9 | 障碍诚实（V10.10 NEW）| proactive-scan.py §9 |
| 10 | 抽象理由检测（V10.10 NEW）| reason-classifier.py |

---

## fix-list.json 格式

```json
{
  "generated_at": "2026-08-11T14:30:00Z",
  "fixes": [
    {
      "id": 1,
      "name": "visual",
      "severity": "HIGH",
      "fix_action": "重新生成截图（≥5KB + 7 天内）"
    },
    {
      "id": 3,
      "name": "self-attest",
      "severity": "MEDIUM",
      "fix_action": "reviewer 必亲自跑 pytest --cov"
    }
  ]
}
```

---

## 严重度分级

| 严重度 | 修复 SLA |
|--------|---------|
| **HIGH** | Stage 5 Accept 前必修复 |
| **MEDIUM** | 当前 change 内修复 |
| **LOW** | backlog 记录 |

---

## 反例

### 反例 A：fix-list.json 空

```
proactive-scan.py 跑完 → fix-list.json 是空的  # ❌ rot #14
正确: 扫描出 FAIL 项必填入 fix-list
```

### 反例 B：跳过 rot-detector 直接 Accept

```
Stage 4 Review PASS → 直接 Stage 5 Accept  # ❌ Article XIV
正确: Stage 4.5 rot-scan 必走 → PASS → Stage 5 Accept
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [rot-classification.md](../references/rot-classification.md)
- [scan-protocol.md](../references/scan-protocol.md)
