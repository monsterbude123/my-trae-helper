# V10 实战蒸馏（Battle-Tested Patterns）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 3.5 Real Verify 从 V10 §0.10 + .trae/rules/视觉证据铁律.md + scenarios.md §3 蒸馏。

---

## V10 实战反例（3 条：2 部分 + 1 完全重叠）

### 蒸馏 1："启动 = 完成"反复失误（完全重叠）

→ 见 [01-startup-equals-done.md](01-startup-equals-done.md)（V10.10 反虚假交付，铁律 1 启动可见产物 + 5 类项目启动验证表 + visual-evidence.md 3 层校验）。

### 蒸馏 2：Playwright MCP 路径陷阱（部分重叠）

**独特差异**: 不同于 03-skip-screenshot.md 聚焦"跳过截图"，本条聚焦截图**已拍但路径错**——playwright_screenshot 默认存 Downloads/ → 主上下文声称"已截图"但未归档 docs/verifications/ → Stage 4 Review 找不到返工。V11 改进为 SKILL.md §3 Step 4 + visual-evidence.md 主上下文亲自 Read。

→ 关联 [03-skip-screenshot.md](03-skip-screenshot.md)。

### 蒸馏 3：抽象理由"理解偏差"（部分重叠）

**独特差异**: 不同于 02-container-not-started.md 聚焦"容器未启动"，本条聚焦 Real Verify FAIL 后用"流程裁剪，等下次一起修"抽象理由搪塞 → 用户要求必须有 5 字段报告。V11 改进为铁律 5（阻塞诚实）+ blockage-report.md 5 字段必含。

→ 关联 [02-container-not-started.md](02-container-not-started.md)。

---

## V10 实战蒸馏经验（3 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| 启动可见产物 ≠ 进程存活 | §0.10 强约束 | 铁律 1 + 5 类验证 |
| Playwright 归档必走 | 视觉证据铁律 §3.2 | visual-evidence.md |
| 抽象理由禁（V10.10）| Article XVI | 铁律 5 + blockage-report.md |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 SKILL.md §0.10 | → `../../08-real-verify/SKILL.md` 铁律 1-6 + `references/startup-verification.md` |
| V10 .trae/rules/视觉证据铁律.md | → `../../08-real-verify/references/visual-evidence.md` |
| V10 visual-content-check.py | → V11 `scripts/visual-content-check.py`（重写） |
| V10 dist-hash-check.py | → V11 `scripts/dist-hash-check.py`（重写） |

---

## 关联引用

- [SKILL.md](../SKILL.md) | [README.md](../README.md)
- [startup-verification.md](../references/startup-verification.md) | [visual-evidence.md](../references/visual-evidence.md) | [blockage-report.md](../references/blockage-report.md)
- 其他反例: [01-startup-equals-done.md](01-startup-equals-done.md) / [02-container-not-started.md](02-container-not-started.md) / [03-skip-screenshot.md](03-skip-screenshot.md)
