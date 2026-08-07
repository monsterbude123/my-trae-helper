# Constitution 14 Articles 详细解释

> 本文档为 [../SKILL.md](../SKILL.md) §-1 的引用详情，供需要深入理解的场景阅读。

---

## Article I — TDD 强制

**主旨**: 无失败测试不写实现。

**适用范围**: 编码类 change。

**例外**: Bug 修复路径允许 e2e 先行替代单测 RED，详见 [bug-workflow.md](bug-workflow.md)。

**Rationale**: 测试先行是质量底线，防止"先写代码再补测试"的自欺欺人。

**Enforcement**: phase-gate.py implement-to-review 检查 test 新增数量 ≥ impl 新增数量。

---

## Article II — 满分硬门禁

**主旨**: 任一非满分 = 🛑 REJECT 整个 change。

**Rationale**: "降级"是退路，降一次就会降两次。满分硬门禁倒逼 Agent 在每个维度都不妥协。

**Enforcement**: acceptance-audit.py 四维验收必须全 PASS；任一维度 FAIL = reject。

---

## Article III — 零残留迁移

**主旨**: 无 `*.bak` / `*.old` 后缀文件。

**Rationale**: 残留文件是噪声，Git 已有历史，不需要在文件系统留备份。

**Enforcement**: phase-gate.py review-to-accept 检查无 `.bak` / `.old` 文件。

---

## Article IV — 委派纪律

**主旨**: 主上下文不直行代码，只做协调。

**Rationale**: 主上下文上下文有限，直行代码会导致理解深度不足、遗漏边界。

**Enforcement**: 主上下文禁止直接 Edit/Write，必须委派给 implementer/contract-writer。

---

## Article V — GitNexus First

**主旨**: 影响面评估用工具不用 grep。

**Rationale**: grep 不理解符号语义，容易漏掉跨模块影响。GitNexus 提供准确的 call graph。

**Enforcement**: 主上下文改符号前必须调 GitNexus impact()，禁止手动 grep。

---

## Article VI — Ponytail First

**主旨**: 最简实现优先。

**Rationale**: 过度工程是腐烂之源。Ponytail 强制"最小依赖、标准库优先、少于 X 行"。

**Enforcement**: implementer 输出必须通过 code-hygiene.py（单文件 ≤ 800 行，函数 ≤ 50 行）。

---

## Article VII — 文档与代码冲突以文档为准

**主旨**: 漂移立即回流。

**Rationale**: Spec 是真相源，代码为规格服务。代码偏离 Spec = 隐性 bug。

**Enforcement**: Reviewer 必跑 drift-check，发现漂移立即回流。

---

## Article VIII — 归档不可变

**主旨**: `archive/` 下文件禁止修改。

**Rationale**: 归档是历史记录，修改归档破坏可追溯性。

**Enforcement**: 主上下文禁止 Edit/Write `archive/` 路径下文件。

---

## Article IX — TDD 即时（V10.4 新）

**主旨**: 改实现/删组件 → 立即同步改测试/删测试。

**Rationale**: 测试与实现不同步 = 孤儿测试/组件，腐烂点 12。

**Enforcement**: phase-gate.py implement-to-review 检查测试与实现变更一致性。

---

## Article X — 异会话验证（V10.4 新）

**主旨**: 自评 = self_attested，主上下文必二次抽检。

**Rationale**: Agent 知道规则但选择应付——编 status=✓ / 编 evidence。主上下文亲自验证让"应付成本 > 真实完成成本"。

**Enforcement**: 主上下文 Read evidence(file:line) 验证内容匹配。

---

## Article XI — 视觉真实验证（V10.4 新）

**主旨**: PIL 解码 + 直方图 + 关键区域采样。

**适用范围**: 含 UI 的 Tauri/Web 项目。

**不适用**: 纯后端/CLI/无 UI 模块（Plan 阶段显式锁定 uiux=N/A 可跳过）。

**Rationale**: 进程在跑 + 端口 LISTEN + audit PASS ≠ 用户能看到应用。必须亲眼看到 UI 渲染。

**Enforcement**: acceptance-audit.py uiux 维度调用 visual-content-check.py。

---

## Article XII — 文档诚实（V10.5 新）

**主旨**: state-card/INDEX 声称的 INV 必在 spec.md 落地，不可自评"完成"无证据。

**Rationale**: 自我吹嘘是腐烂点 15，"已完成"无证据 = 虚假承诺。

**Enforcement**: proactive-scan.py 第 6 项检查 self-aggrandizing-doc。

---

## Article XIII — 骨架是债（V10.5 新）

**主旨**: 🟡 骨架 = 隐性技术债，2 周未推进必冻结或归档。

**Rationale**: 骨架堆积是腐烂点 17，只 define.md 的 change 拖久必腐烂。

**Enforcement**: proactive-scan.py 第 7 项检查 stub-pileup。

---

## Article XIV — rot-detector 必跑（V10.4 新）

**主旨**: Phase 4.5 Proactive Rot Scan 不可跳过，任一 FAIL = 🛑 REJECT。

**Rationale**: 腐烂点 14 — Agent 不主动诊断，等用户问才发现已腐烂。

**Enforcement**: 主上下文 Phase 4 必委派 rot-detector，proactive-scan.py 任一 FAIL 阻断 Accept。

---

## 冲突判定顺序

Constitution > Spec > Contract > Code > 个人判断。

## 永不可降级

即使修改流程也维持底线：Articles I、II、IV、V、VIII、IX、XIV。

---

## 相关文档

- [acceptance-gates-v10.md](acceptance-gates-v10.md) — 验收门禁详细协议
- [sub-agent-rules.md](sub-agent-rules.md) — 子代理通用铁律
- [bug-workflow.md](bug-workflow.md) — Bug 修复工作流（Article I 例外）
- [process-rot-analysis.md](process-rot-analysis.md) — 腐烂点分析与治理