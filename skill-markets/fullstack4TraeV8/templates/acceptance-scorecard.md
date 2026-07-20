# 🎯 精密门禁计分卡

> **V8.0**: 8 维度 Checklist 机械判定 + 评分自动推导 + 一致性校验。评分是算出来的，不是给的。

---

## Checklist 判定 + 自动评分

### 维度 1: Spec 对齐度（权重 15%）

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 1.1 | spec.md 所有 Requirement 已实现 | 逐一对照，缺 0 个 | PASS/FAIL | |
| 1.2 | spec.md 所有 Scenario 已实现 | 覆盖率 ≥ 90% | PASS/FAIL | |
| 1.3 | Non-Goals 未被违反 | 0 违反 | PASS/FAIL | |
| 1.4 | spec 场景与测试有映射 | 每个 Scenario ≥ 1 测试 | PASS/FAIL | |
| **维度得分** | **{N}/4 PASS** | — | **{score}** | |

### 维度 2: 契约一致性（权重 15%）

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 2.1 | 接口路径一致 | 0 漂移 | PASS/FAIL | |
| 2.2 | 请求/响应字段一致 | 0 漂移 | PASS/FAIL | |
| 2.3 | 错误码一致 | 0 漂移 | PASS/FAIL | |
| 2.4 | 字段类型一致 | 0 严重漂移 | PASS/FAIL | |
| 2.5 | 契约测试全部通过 | 100% 通过 | PASS/FAIL | |
| 2.6 | 影响面处理 | 逐项对照 intake 清单 | PASS/FAIL | |
| **维度得分** | **{N}/6 PASS** | — | **{score}** | |

### 维度 3: 测试质量（权重 15%）

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 3.1 | 单元测试覆盖率 | ≥ 80% | PASS/FAIL | |
| 3.2 | 关键路径覆盖率 | 100% | PASS/FAIL | |
| 3.3 | TDD RED/GREEN 标记完整 | 每任务有 RED+GREEN | PASS/FAIL | |
| 3.4 | E2E 场景覆盖 | 主路径 ≥ 3 场景 | PASS/FAIL/N/A | |
| **维度得分** | **{N}/{M} PASS** | — | **{score}** | |

### 维度 4: 代码质量（权重 15%）

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 4.1 | 无 any / console.log | lint 0 warning | PASS/FAIL | |
| 4.2 | 函数 < 50 行，文件 ≤ 800 行 | 0 违规 | PASS/FAIL | |
| 4.3 | 错误处理完善 | 所有 async 有 try/catch | PASS/FAIL | |
| 4.4 | 无死代码 | grep 未使用 = 0 | PASS/FAIL | |
| **维度得分** | **{N}/4 PASS** | — | **{score}** | |

### 维度 5: 文档一致性（权重 10%）

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 5.1 | ARCHITECTURE.md 已更新 | diff ≥ 5 行实质性变更 | PASS/FAIL | |
| 5.2 | README.md 已更新 | 索引状态 + 变更记录 | PASS/FAIL | |
| 5.3 | 文档索引已重建 | 通过 doc-map-manager 技能重建 | PASS/FAIL | |
| 5.4 | modules/ 全部标记 | 每模块有 🟢🟡🔴 | PASS/FAIL | |
| 5.5 | prototypes/ 非空（如涉UI） | 非空 | PASS/FAIL/N/A | |
| **维度得分** | **{N}/{M} PASS** | — | **{score}** | |

### 维度 6: 安全性（权重 15%）— 一票否决

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 6.1 | 无硬编码凭证 | grep = 0 | PASS/FAIL | |
| 6.2 | 无 SQL 注入风险 | 参数化/ORM | PASS/FAIL | |
| 6.3 | 无 XSS 漏洞 | 输出转义 | PASS/FAIL | |
| 6.4 | 安全扫描通过 | 0 HIGH 真实风险 | PASS/FAIL | |
| **维度得分** | **{N}/4 PASS** | — | **{score}** | |

### 维度 7: 业务闭环完整度（权重 15%）— 一票否决

> ⚠️ 以下 checklist 项必须从 `closure-checklist.md` 生成，禁止使用此模板默认值。

| # | 闭环步骤 | 对应 Spec | 阈值 | 结果 | 截图 |
|---|---------|----------|------|:---:|------|
| 7.1 | {步骤1描述} | {spec引用} | 浏览器可操作 | | {path} |
| 7.2 | {步骤2描述} | {spec引用} | 浏览器可操作 | | {path} |
| ... | ... | ... | ... | ... | ... |

**验证手段**:
- 截图存放: `docs/reports/screenshots/{change}/`
- 每步截图数量 ≥ 1
- 任一 7.1 或 7.2 FAIL → 一票否决，总分封顶 3.0

| **维度得分** | **{N}/{M} PASS** | — | **{score}** | |

### 维度 8: UI/UX 一致性（权重 10%）

> 涉及 UI 的变更强制执行。不涉及 UI → 整维度 N/A，权重重新分配。

| # | Checklist 项 | 质量阈值 | 结果 | 证据 |
|---|-------------|---------|:---:|------|
| 8.1 | prototype 比对覆盖率 | ≥ 80% 区域匹配 | PASS/FAIL/N/A | |
| 8.2 | 5 状态截图齐全（idle/loading/data/empty/error） | 5/5 | PASS/FAIL/N/A | |
| 8.3 | visual-acceptance 报告无 HIGH 风险 | 0 HIGH | PASS/FAIL/N/A | |
| 8.4 | 截图已归档到 docs/reports/screenshots/ | 文件存在 + 非空 | PASS/FAIL/N/A | |
| **维度得分** | **{N}/{M} PASS** | — | **{score}** | |

---
## 自动计算总分

| 维度 | PASS/适用 | 得分 | 权重 | 加权 |
|------|:---:|------|------|------|
| 1. Spec 对齐 | {N}/4 | {score} | 12% | {weighted} |
| 2. 契约一致 | {N}/6 | {score} | 12% | {weighted} |
| 3. 测试质量 | {N}/{M} | {score} | 12% | {weighted} |
| 4. 代码质量 | {N}/4 | {score} | 12% | {weighted} |
| 5. 文档一致性 | {N}/{M} | {score} | 10% | {weighted} |
| 6. 安全性 | {N}/4 | {score} | 15% | {weighted} |
| 7. 业务闭环 | {N}/{M} | {score} | 12% | {weighted} |
| 8. UI/UX 一致性 | {N}/{M} | {score} | 15% | {weighted} |
| **总分** | **{total PASS}/{total 适用}** | — | 100% | **{total}** |

---

## 一致性校验

- 计算评分: {computed}
- checklist 整体通过率: {rate}% → 对应评分 {equivalent}
- 偏差: |{computed} - {equivalent}| = {delta}
- {delta < 0.5 → ✅ 一致 | delta ≥ 0.5 → 🛑 异常}

---

## 门禁逐项

| 门禁 | 标准 | 实际 | 判定 |
|------|------|------|:---:|
| 总分 ≥ 4.0 | 4.0 | {total} | ✅/❌ |
| 单维度 ≥ 3.0 | 3.0 | 最低 {min} | ✅/❌ |
| 安全 ≥ 4.0 | 4.0 | {security} | ✅/❌ |
| 一致性校验 | 偏差 < 0.5 | {delta} | ✅/❌ |

---

## FAIL 项明细（无"非阻塞"分类）

| # | 维度 | Checklist 项 | FAIL 原因 | 修复建议 |
|---|------|-------------|---------|---------|
| 1 | {dim} | {item} | {reason} | {suggestion} |

---

## 判定

- **判定结果**: 🟢 PASS / 🛑 REJECT
- **审查者**: reviewer agent
- **下一步**: {commit / 回流修复}
