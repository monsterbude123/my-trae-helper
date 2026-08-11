# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 3.5 Real Verify 从 V10 §0.10 + .trae/rules/视觉证据铁律.md + scenarios.md §3 蒸馏。

---

## V10 实战反例（3 条）

### 蒸馏 1："启动 = 完成"反复失误（V10.10 反虚假交付）

**实战场景**（V10.10 蒸馏）:
- 用户: "启动验证通过了吗"
- 主上下文: "vite 启动了，应该没问题" → 声称 PASS
- 用户截图证伪："页面空白，截图呢" → 信任坍塌

**V11 改进**: 铁律 1（启动可见产物）+ 5 类项目启动验证表 + visual-evidence.md 3 层校验。

**V10 源**: SKILL.md §0.10 NEW + .trae/rules/视觉证据铁律.md §1。

---

### 蒸馏 2：Playwright MCP 路径陷阱（V10.11 实战）

**实战场景**（V10.11 蒸馏）:
- playwright_screenshot 默认保存到 Downloads/
- 主上下文声称"已截图"但未归档到 docs/verifications/
- 文件留在 Downloads → Stage 4 Review 找不到 → 返工

**V11 改进**: SKILL.md §3 标准流程 Step 4 + visual-evidence.md 主上下文亲自 Read。

**V10 源**: .trae/rules/视觉证据铁律.md §3.2 Playwright MCP 路径陷阱。

---

### 蒸馏 3：抽象理由"理解偏差"（V10.10 Article XVI）

**实战场景**（V10.10 蒸馏）:
- 主上下文: Real Verify FAIL → "流程裁剪，等下次一起修"
- 用户: "流程裁剪不算理由，必须有 5 字段报告"

**V11 改进**: 铁律 5（阻塞诚实）+ blockage-report.md 5 字段必含。

**V10 源**: SKILL.md §3.7 反虚假交付 + §10 抽象理由 6 类。

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
