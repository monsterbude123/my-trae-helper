# 质疑式验收（Skeptical Acceptance）

> Stage 4 Review 必走。V10 reviewer 铁律 9 质疑式验收 SUITE 蒸馏。

---

## ZERO TRUST（零信任）

```
默认立场: implement 阶段工作未完成/有隐瞒
默认动作: 索要事实证据
默认响应: 证据不全就拦截
```

**反模式**: 默认"已完成"→ 找证据确认 → 找不到放过 = 盖章者。

---

## EVIDENCE MANDATORY（证据强制）

每个验收结论必含：

```yaml
claim: "代码覆盖率 92%"
evidence:
  - command: "pytest --cov"
  - output: "TOTAL 92% 150/163"
  - exit_code: 0
```

**反模式**: claim 无 evidence → reviewer 不接受。

---

## ACTIVE FALSIFICATION（主动证伪）

reviewer 不接受未经证伪的结论，必主动找反例：

| 高风险清单 | 证伪动作 |
|-----------|---------|
| 边界遗漏 | 测边界值（0/1/max/null）|
| 依赖污染 | 检查 import 是否有未声明依赖 |
| 未提交文件 | git status 是否有 untracked |
| 隐藏 TODO | grep TODO / FIXME / XXX |
| 测试篡改 | 比对测试 commit + 验证断言非空 |

**反模式**: 不主动证伪 = 默认信任 = 失真风险。

---

## REQUIREMENT TRACING（需求溯源）

```
spec.md AC-001 → test_AC_001 → code path → 截图
```

任一环断 = REJECT。

---

## 关联引用

- [SKILL.md §铁律 9](../SKILL.md) — 质疑式验收 SUITE
- [evidence-3-layer.md](evidence-3-layer.md)
- V10 reviewer.md: `V10 来源` (已蒸馏到本文档)
