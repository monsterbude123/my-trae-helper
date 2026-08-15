# V10 实战蒸馏 — Stage 0.5 Test Plan 战役反例

> **定位**:V10 `templates/test-plan-example.md` L62-64 + `references/reviewer-templates.md` L172-176 蒸馏出的 2 条实战反例集。与 01-04 反例聚焦"做错事"互补,本文件聚焦"实施者假装做对了"。
>
> **薄版说明**(V11.5 自检缩窄):V10 关于 Stage 0.5 实战素材偏弱(模板反例演示而非战役蒸馏),**仅 2 条 15-20 行**。Stage 0.5 入口的实战反例集仍以 01-04 为主,本文件作为补充。

---

## 反例 5:假装 100% 覆盖(§2 全填 ✅ + 本段空白)

**蒸馏来源**:[V10 templates/test-plan-example.md L62-64](../../../fullstack4TraeV10/templates/test-plan-example.md)

**现象**:

```yaml
# ❌ 反例:test-plan.md §2 覆盖映射表 全填 ✅
| 场景 ID | 测试类型 | 测试文件:行号 | 状态 | 备注 |
|---------|---------|-------------|------|------|
| TS-001 | e2e | tests/e2e/list.spec.ts:15 | ✅ | Playwright ... |
| TS-002 | e2e | tests/e2e/delete.spec.ts:22 | ✅ | Playwright ... |
| ... (100 项全 ✅)

# 但 §3 未覆盖场景说明 段空白
## 3. 未覆盖场景
[空白]
```

**根因**:
- §2 强制非空 = 实施者全填 ✅ 应付 + §3 空白 = **自评"完美覆盖"但实际未识别风险**
- 缺失反例思维:以为"全 ✅ = 好 test-plan"

**V11 改进**:SKILL.md 铁律 4「测试用例可追溯」+ 03-coverage-too-low 反例已覆盖门槛 ≥ 90% 量化,但**未覆盖"全填 ✅ 但 §3 空白"的假装场景** — 本条作为补充。

**正确替代**:

```yaml
# ✅ §2 必含至少 1 条 ⚠️ 或 🟡 标注(诚实风险)
| TS-007 | unit (P2 自动化难度高) | tests/unit/concurrent.spec.ts:N/A | 🟡 | 并发场景复杂,手动验证 |

# ✅ §3 必含未覆盖说明
## 3. 未覆盖场景
- TS-007 P2 未覆盖:并发删同模型 — 自动化难度高,manual 验证已记录(参见 §4.4 已知盲区)
```

---

## 反例 6:编造测试文件路径(填 `tests/foo.test.ts:999` 无人抓)

**蒸馏来源**:[V10 references/reviewer-templates.md L105 + L172-176](../../../fullstack4TraeV10/references/reviewer-templates.md)(原 §Step 2.4.5 glob 验证)

**现象**:

```yaml
# ❌ 反例:implementer 铁律 10 填测试文件:行号,缺 reviewer 验证
## 2. 覆盖映射表
| 场景 ID | 测试文件:行号 | 状态 |
|---------|-------------|------|
| TS-001 | tests/foo.test.ts:999 | ✅ |   # ❌ 文件不存在 + 行号瞎编
| TS-002 | tests/bar.test.ts:42  | ✅ |   # ❌ 文件不存在
| TS-003 | tests/baz.test.ts:1   | ✅ |   # ❌ 文件不存在
```

**根因**:
- V10 实施者填了文件路径,但 **reviewer 没 glob 验证** → 编造无人抓
- Stage 3 实施者走完 test,Stage 4 reviewer 看到 ✅ = 放行,真实测试代码不存在

**V11 改进**:
- 反例 4 02-test-not-traceable.md 已含"test docstring capability 注解" 强制(测试代码层追溯)
- 但**未触及"test-plan.md 写路径但实际不存在"的 plan 层编造** — 本条作为补充

**正确替代**:

```yaml
# ✅ 实施者提交前必跑(主上下文 glob 验证)
$ ls tests/foo.test.ts tests/bar.test.ts tests/baz.test.ts
ls: cannot access 'tests/foo.test.ts': No such file or directory
# → 🛑 REJECT + 失败分类"测试覆盖缺口:测试文件不存在"

# ✅ reviewer §Step 2.4.5 强制 glob 验证 ≥3 个 TS-{N},行号不存在计入失败 1 次
```

---

## 与现有 01-04 反例的差异化

| 反例 | 焦点 | 与 V10-battle-tested 关系 |
|------|------|-----------------------------|
| 01 无验收维度直接测试 | Capability → 维度拆解 | 互补:V10-battle-tested 5 聚焦"拆完假装完美" |
| 02 测试不可追溯 | test-to-capability 映射 | 互补:V10-battle-tested 6 聚焦"映射到不存在的文件" |
| 03 覆盖率门槛宽松 | ≥90% 量化 | 互补:V10-battle-tested 5 聚焦"✅ 凑数但 §3 空白" |
| 04 跳过 E2E/INV | 3 层级组合 | 不重叠 — V10-battle-tested 不补 E2E |

---

## 关联引用

- [01-no-acceptance-dimension.md](01-no-acceptance-dimension.md) — Capability → 维度拆解
- [02-test-not-traceable.md](02-test-not-traceable.md) — test-to-capability 映射
- [03-coverage-too-low.md](03-coverage-too-low.md) — 门槛 ≥ 90%
- [04-skip-e2e.md](04-skip-e2e.md) — E2E ≥ 2 + INV ≥ 1 + UNIT ≥ 5
- [V10 模板 test-plan-example.md L62-64](../../../fullstack4TraeV10/templates/test-plan-example.md) — 反例 5 来源
- [V10 reviewer-templates.md L105 + L172-176](../../../fullstack4TraeV10/references/reviewer-templates.md) — 反例 6 来源