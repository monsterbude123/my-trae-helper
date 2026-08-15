# Rot Scan Report Template — Stage 4.5

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 位置: `docs/reports/rot-scan-{date}.md`

---

```yaml
# Rot Scan Report: {date}

## 总览

| 检查项 | 状态 | 详情 |
|--------|:---:|------|
| 1. 视觉腐烂 | PASS | {N} 个截图全部 ≥5KB + 7 天内 |
| 2. 归档腐烂 | PASS | archive/ 不可变 |
| 3. 自验腐烂 | PASS | reviewer 亲自跑测试 |
| 4. 孤儿测试 | PASS | orphan-detector.py 扫描 0 项 |
| 5. Bundle Staleness | PASS | src/ 与 dist/ 时序一致 |
| 6. 吹嘘腐烂 | PASS | 无"全通过"无 evidence |
| 7. 状态卡陈旧 | PASS | 0 项陈旧 |
| 8. 骨架腐烂 | PASS | stub 标记 < 阈值 |
| 9. 障碍诚实 | PASS | 阻塞报告均含 5 字段 |
| 10. 抽象理由 | PASS | 未发现 6 类抽象理由 |

**总分**: 10/10 PASS

## fix-list.json

参见 `docs/reports/fix-list.json`

## 详细记录

### Check 1: 视觉腐烂
- 命令: `python ../../scripts/visual-content-check.py`
- 输出: {N} 个截图
- 结果: PASS

### Check 2: 归档腐烂
- 命令: `git diff archive/`
- 输出: 无 diff
- 结果: PASS

...

## 元检测（self-diagnose.py）

| 元检查项 | 状态 |
|---------|:---:|
| rot_detector_logic | PASS |
| phase_gate_help | PASS |
| score_formula | PASS |
| constitution_articles | PASS |
| state_card_schema | PASS |
| stub_markers | PASS |

## 结论

✅ rot-scan PASS — 进入 Stage 5 Accept
```

---

## 关联引用

- [Stage 4.5 Rot Scan](../../skills/10-rot-scan/SKILL.md)
- [rot-classification.md](../../skills/10-rot-scan/references/rot-classification.md)
- [scan-protocol.md](../../skills/10-rot-scan/references/scan-protocol.md)
