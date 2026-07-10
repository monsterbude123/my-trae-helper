# 量化验收方法论（Quantitative Acceptance）V6.0

> **定位**：SDD 流程的最终门禁。用 **Checklist 机械判定 + 评分自动推导 + 一致性校验** 三层结构替代"凭直觉验收"和"纯 checklist 被游戏"两个极端。
>
> **V6.0 核心变化**：
> 1. 评分从 checklist 刚性推导，reviewer 不可手动调分
> 2. checklist 项带质量阈值（不是"改没改"而是"改够了没"）
> 3. checklist 通过率 ↔ 计算评分 一致性校验（偏差 ≥ 0.5 = 异常）
> 4. 废除"非阻塞"分类 — FAIL 就是 FAIL
>
> **触发**：fullstack-reviewer 移交后、acceptance 阶段强制执行；任意阶段 Agent 汇报时也用打分卡的子集做"量化汇报"。
>
> **模板**：[templates/acceptance-scorecard.md](../templates/acceptance-scorecard.md)

---

## 一、设计动机：为什么 checklist 和评分都要

| 方案 | 怎么被游戏 | 实例 |
|------|-----------|------|
| 纯 checklist | "更新了 ARCHITECTURE.md" = 加了一行空格 → ✅ | 全绿，实际全不及格 |
| 纯评分 | 3 项文档缺失，reviewer 仍打 4.0 → PASS | 分数好看，产出缺失（P0-3） |

**解法**：checklist 和评分交叉验证 — checklist 每项带质量阈值，评分从 checklist 刚性计算，两者偏差 ≥ 0.5 直接报警。

---

## 二、精密门禁模型

```
┌──────────────────────────────────────────────────────┐
│                    精密门禁机                          │
│                                                      │
│  Step 1 — Checklist 机械判定                          │
│  ├── 每项带质量阈值（行数/字数/文件数/覆盖率）           │
│  ├── 判定结果: PASS / FAIL / N/A（本阶段不适用）        │
│  └── N/A 项需预先声明于 spec Out of Scope，不允许事后归类 │
│                                                      │
│  Step 2 — 评分自动计算                                │
│  ├── 维度得分 = (PASS数 / 可适用项总数) × 5.0          │
│  ├── 总分 = 各维度得分 × 权重 之和                      │
│  └── 人工不可干预                                     │
│                                                      │
│  Step 3 — 一致性校验                                  │
│  ├── checklist 通过率 ↔ 计算评分 偏差 < ±0.5          │
│  ├── 单维度 < 3.0 → 一票否决                          │
│  └── 安全维度 < 4.0 → 一票否决                        │
│                                                      │
│  Step 4 — 不可降级                                    │
│  └── 不存在"非阻塞"分类。FAIL = FAIL。                 │
│      如果某项本阶段确实做不了 → Step 1 标 N/A           │
│      N/A 需要在 spec 的 Out of Scope 里预先声明        │
│                                                      │
│  Step 5 — N/A 预声明验证（V9.1 NEW — 防事后归类）       │
│  ├── 每个 N/A 项：检查 spec Out of Scope 是否有对应声明 │
│  ├── 无对应声明 → N/A 无效 → 强制回退为 FAIL         │
│  ├── 禁止在 Review 阶段新增 N/A                        │
│  └── N/A 的来源只有 spec 阶段的 Out of Scope 声明      │
└──────────────────────────────────────────────────────┘
```

---

## 三、7 维度 Checklist（带质量阈值）

### 维度 1: Spec 对齐度（权重 15%）

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 1.1 | spec.md 所有 Requirement 已实现 | 逐一对照，缺 0 个 | PASS/FAIL |
| 1.2 | spec.md 所有 Scenario 已实现 | 逐一对照，覆盖率 ≥ 90% | PASS/FAIL |
| 1.3 | Non-Goals 未被违反 | grep Non-Goals 关键词 vs 代码 | PASS/FAIL |
| 1.4 | spec 场景与测试用例有映射关系 | 每个 Scenario 至少 1 个测试 | PASS/FAIL |

**维度得分 = (PASS数 / 4) × 5.0**

### 维度 2: 契约一致性（权重 15%）

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 2.1 | 接口路径与 api-contracts.md 一致 | 0 漂移 | PASS/FAIL |
| 2.2 | 请求/响应字段与 api-contracts.md 一致 | 0 漂移 | PASS/FAIL |
| 2.3 | 错误码与 api-contracts.md 一致 | 0 漂移 | PASS/FAIL |
| 2.4 | 字段类型与 domain-models.md 一致 | 0 严重漂移 | PASS/FAIL |
| 2.5 | 契约测试全部通过 | 100% 通过 | PASS/FAIL |

**维度得分 = (PASS数 / 5) × 5.0**

### 维度 3: 测试质量（权重 15%）

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 3.1 | 单元测试覆盖率 | ≥ 80% | PASS/FAIL |
| 3.2 | 关键路径覆盖率 | 100% | PASS/FAIL |
| 3.3 | TDD RED/GREEN 标记完整 | 每个任务有 RED+GREEN | PASS/FAIL |
| 3.4 | E2E 场景覆盖 | 主路径 ≥ 3 场景 | PASS/FAIL/N/A |

**维度得分 = (PASS数 / 可适用项数) × 5.0**

### 维度 4: 代码质量（权重 15%）

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 4.1 | 无 any 类型 / console.log | lint 0 warning | PASS/FAIL |
| 4.2 | 函数 < 50 行，文件 ≤ 800 行 | 0 违规 | PASS/FAIL |
| 4.3 | 错误处理完善 | 所有 async 有 try/catch 或 error boundary | PASS/FAIL |
| 4.4 | 无死代码 | grep 未使用的 import/函数 = 0 | PASS/FAIL |

**维度得分 = (PASS数 / 4) × 5.0**

### 维度 5: 文档一致性（权重 10%）

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 5.1 | ARCHITECTURE.md 已更新 | diff ≥ 5 行实质性变更 | PASS/FAIL |
| 5.2 | README.md 已更新 | 索引状态 + 变更记录 | PASS/FAIL |
| 5.3 | 文档索引已重建 | 通过 doc-map-manager 技能重建 | PASS/FAIL |
| 5.4 | modules/ 全部标记实施状态 | 每个相关模块有 🟢🟡🔴 | PASS/FAIL |
| 5.5 | prototypes/ 非空（如涉 UI） | prototypes/ 目录非空 | PASS/FAIL/N/A |

**维度得分 = (PASS数 / 可适用项数) × 5.0**

### 维度 6: 安全性（权重 15%）— 一票否决

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 6.1 | 无硬编码凭证 | grep sk- / password / token = 0 | PASS/FAIL |
| 6.2 | 无 SQL 注入风险 | 参数化查询 / ORM | PASS/FAIL |
| 6.3 | 无 XSS 漏洞 | 输出转义 | PASS/FAIL |
| 6.4 | 安全扫描通过 | 0 HIGH 真实风险 | PASS/FAIL |

**维度得分 = (PASS数 / 4) × 5.0**
**一票否决**：维度得分 < 4.0 → 🛑 无论其他维度多高，不交付。

### 维度 7: 业务闭环完整度（权重 15%）— 一票否决

> ⚠️ 以下 checklist 项从 `closure-checklist.md` 生成，禁止使用通用默认值。

| # | Checklist 项 | 质量阈值 | 判定 |
|---|-------------|---------|:---:|
| 7.1 | 最小业务闭环所有 P0 步骤可达 | 闭环步骤 100% 浏览器可操作 + 有截图 | PASS/FAIL |
| 7.2 | 闭环中无阻塞性 UI 缺失 | 0 个"功能未实现 UI"阻断 | PASS/FAIL |
| 7.3 | 空状态/错误状态有用户可操作入口 | 所有空态有 CTA，所有错误态有重试 | PASS/FAIL |
| 7.4 | 闭环步骤与 Spec Scenario 1:1 对应 | 每个闭环步骤引用 ≥ 1 个 BDD 场景 | PASS/FAIL |

**维度得分 = (PASS数 / 4) × 5.0**
**一票否决**：7.1 或 7.2 FAIL → 总分自动封顶 3.0（不可交付，无论其他维度多高）

---

## 四、评分自动计算公式

```
维度得分 = (该维度 PASS 的 checklist 项数 / 该维度可适用 checklist 项总数) × 5.0
总分     = Σ(维度得分 × 权重)

例:
  维度 5 文档一致性: 3 PASS / 4 可适用 = 0.75 × 5.0 = 3.75
  维度 1 Spec 对齐:  4 PASS / 4 = 1.0 × 5.0 = 5.0
  
  总分 = 5.0×0.15 + 4.0×0.15 + 3.0×0.15 + 4.0×0.15 + 3.75×0.10 + 5.0×0.15 + 5.0×0.15
       = 0.75 + 0.6 + 0.45 + 0.6 + 0.375 + 0.75 + 0.75
       = 4.275
```

### 评分等级

| 等级 | 分数 | 行动 |
|------|------|------|
| 🟢🟢 优 | 4.5-5.0 | 可交付 |
| 🟢 良 | 4.0-4.4 | 可交付 |
| 🟡 中 | 3.0-3.9 | 必须修复后交付 |
| 🔴 差 | 2.0-2.9 | 必须回流重做 |
| 🔴🔴 极差 | < 2.0 | 立即回流 specs/proposal |

---

## 五、一致性校验（防游戏机制）

```
Step 2 计算出的评分 vs 各维度 checklist 通过率

偏差检测:
  checklist 报告通过率 80% (4/5 PASS)
  → 计算评分应为 4.0
  → 如果 reviewer 报告中评分为 2.0 → 偏差 2.0 ≥ 0.5 → 🛑 数据不一致
  
处理:
  → 禁止进入 commit
  → 退回 reviewer 解释偏差
  → reviewer 要么修正 checklist（重新检查），要么修正评分
```

**此机制防止两种作弊**：
- checklist 全 PASS 但 reviewer 暗地把分打低
- checklist 有 FAIL 但 reviewer 硬说成 PASS

---

## 六、废除"非阻塞"分类

```
旧: 文档完整性有 3 项缺失 → 标记 "P1 非阻塞" → PASS → commit（P0-3）
新: 文档完整性 checklist 3/5 FAIL → 维度得分 2.0 → < 3.0 → 🛑 REJECT

不存在 "非阻塞 P1"。
如果某项本阶段确实做不了（如 E2E 测试需 Playwright 就绪）：
  → 在 spec 的 Out of Scope 中预先声明
  → 在 checklist 中标记为 N/A（不计入总分）
  → 不允许事后归类为 N/A
```

---

## 七、子 Agent 量化汇报（提交给主 Agent）

> 格式与 [completion-report-protocol.md](completion-report-protocol.md) 一致。子 Agent 不产出 Completion Report = 视为未完成。

---

## 八、打分卡的归档与追溯

打分卡归档到 `docs/reports/{change}-acceptance-scorecard-{YYYYMMDD}.md`（**不是 test-plan/ 下**）。

打分卡必须包含：
- 7 维度 checklist（PASS/FAIL/N/A）+ 证据
- 自动计算的维度得分 + 加权总分
- 一致性校验结果
- 判定结果（PASS/REJECT）
- 失败项的精确定位（哪个 checklist 项、什么原因）

---

## 九、反面范例

| 反面（禁止） | 正确（必须） |
|---|---|
| reviewer 手动打 4.0 分 | checklist 自动推导 4.0 分 |
| 3 项缺失标记"非阻塞 P1" | FAIL = FAIL，不存在非阻塞 |
| 评分与 checklist 矛盾但无人发现 | 一致性校验自动拦截 |
| checklist 无质量阈值（改 1 行 = ✅） | 每项带阈值（≥ 5 行 / ≥ 80% / 0 漂移） |
| N/A 事后归类 | N/A 需预先在 Out of Scope 声明 |
| 打分卡放在 test-plan/ | 放在 docs/reports/ |
| checklist 查 `__tests__/` 非空 | checklist 查"用户能否添加挂载点" |
| 验收只看测试通过数 | 验收跑浏览器操作 + 截图 |
| 通用模板应用于任何业务 | 每个 change 生成自己的闭环 checklist |
| 闭环断了仍 APPROVED | 闭环断了 → 总分封顶 3.0 → REJECT |

---

## 十、与其他方法论的关系

| 方法论 | 关系 |
|--------|------|
| [completion-report-protocol.md](completion-report-protocol.md) | Agent 完成时必须产出 Completion Report（V9 NEW） |
| [state-card.md](state-card.md) | 打分卡分数更新状态卡健康度 |
| [feedback-loop.md](feedback-loop.md) | checklist 任一项 FAIL → 触发回流 |
| [contract-first.md](contract-first.md) | 维度 2 契约一致性 checklist |
| [fullstack-intake.md](fullstack-intake.md) | 维度 2 影响面处理 checklist（合并入契约一致性 2.6） |
