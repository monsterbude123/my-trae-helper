# 反例 1：跳过 rot-scan 直接 Accept（Stage 4.5 Rot Scan）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 4.5 必跑。V11 Article XIV NO ROT NO ACCEPT + V10 Article XIV。

## 现象

```
agent: Stage 4 Review PASS → 直接 Stage 5 Accept  # ❌ 跳了 4.5 rot-detector
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得"Review PASS 够了" | 50% |
| 不知道 rot-scan 是什么 | 30% |
| 嫌耗时 | 20% |

## 教训

**V11 Article XIV NO ROT NO ACCEPT**（蒸馏自 V10）：
```
14.1 Phase 4.5 rot-detector 不可跳过
14.2 腐化扫描必跑（10 项：视觉/归档/自验/孤儿/构建/吹嘘/状态卡/骨架/obstacle-honesty/reason-fabrication）
14.3 fix-list.json 必产出且不可空
14.4 NO ROT NO ACCEPT — 任一 FAIL = 🛑 REJECT Accept
```

## 正确替代

```bash
# ✅ 必跑 10 项腐化扫描
python scripts/proactive-scan.py --project-root .
# 输出: docs/reports/rot-scan-{date}.json + fix-list.json

# fix-list.json 必须有内容
# 空 = 扫描未真跑（默认禁止）

# 跑完才进 Stage 5 Accept
```

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md) — 跳过 rot-scan
- [proactive-scan.py 文档](../../../scripts/proactive-scan.py)
- V11 Article XIV（铁律不可降级）
- V10 来源（已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/process-rot-analysis.md`
