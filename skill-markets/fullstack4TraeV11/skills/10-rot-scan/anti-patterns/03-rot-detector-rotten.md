# 反例 3：rot-detector 自身腐烂未检测

> rot-detector 自己也会腐烂。来源：V10 实战教训（self-diagnose.py 蒸馏）。

## 现象

```
# rot-detector 上次跑是 6 个月前 → 自身腐烂
# 新加的反模式 / 规则 rot-detector 不识别
agent: proactive-scan.py PASS → 但 rot-detector 自身 6 个月未更新
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 没有自检机制 | 50% |
| 不知道 self-diagnose.py | 30% |
| 嫌更新耗时 | 20% |

## 教训

**rot-detector 自身必自检**（V10 self-diagnose.py）：
- 定期跑 self-diagnose.py
- 检查 rot-detector 是否包含最新反例库
- 检查规则是否过期

## 正确替代

```bash
# ✅ V10 self-diagnose.py 蒸馏
python scripts/self-diagnose.py
# 输出: self-diagnose-report.json
# 必含: rot-detector 自身健康度

# 周期性建议：每周 + 每次新增反例后必跑
```

## 检测方法

```yaml
rot_detector_self_check:
  self_diagnose_pass: true
  last_self_diagnose: "{30 天内}"
  rules_version: "{最新}"
  false_negative_test: pass  # 用已知腐烂点反测
```

任一 FAIL → 立即跑 self-diagnose.py → 修 rot-detector。

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — rot-detector 自身腐烂
- [self-diagnose.py 文档](../../../scripts/self-diagnose.py)
- V10 来源（已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/process-rot-analysis.md`