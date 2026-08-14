# Spec-Driven Development (SDD) 7 规则

> 来源:[external-report 2026-08-14 §M-02](file:///d:/workspace/my-trae-helper/logs/daily-vibe-coding/2026-08-14/external-report.md)
> 元数据:[GitHub Spec Kit](https://github.com/github/spec-kit) (90k+ stars, 2026 共识)+ [MetaMindz SDD 7 Rules](https://www.metamindz.co.uk/post/spec-driven-development-rules-beat-vibe-coding-2026) + AWS Kiro 客户案例 40h→8h 人时压缩
> 状态:**本仓库已部分落地** — fullstack4TraeV10/V11 走 spec-kit-like 5/7 阶段流水线;本规范补齐 7 规则供所有 AI agent 引用

## 为什么 vibe coding 必崩(月 3 之后)

```
46% AI 生成代码带安全漏洞              (Veracode 2025 调研)
29% 开发者不信任 AI 代码质量           (Stack Overflow 2025)
67% AI 代码需大量修改才能合入          (GitHub 实测)
月 3 之后:输出质量开始断崖 + 知识传递断裂 + AI 选型漂移
```

**结论**:vibe coding 适合 weekend 一次性原型,> 1 周工期 / 团队协作 / 生产环境 / 长期维护代码必须走 SDD。

## 7 条规则

### 规则 1 — 写 spec 在前,代码在后

- **MUST**:任何 > 1 天工期的功能,**先写 spec.md**(What + Why + 验收标准),再写 plan.md(How + 任务拆分),再写代码
- **MUST NOT**:不写 spec 就让 agent 写代码 — agent 不知道"什么算完成",必然输出漂移
- **本仓库对接**:fullstack4TraeV11 Stage 1 (spec-writer) 是这一规则的标准实现
- **反例**:让 Claude Code "build me an e-commerce platform" → agent 不知道完成标准,反复推倒重来

### 规则 2 — 不要跳过 plan,plan.md 是 atomic tasks

- **MUST**:plan.md 拆成**可单独验收**的 atomic task,每个 task ≤ 半天
- **MUST NOT**:把"实现 + 测试 + 部署"塞进一个 task — 粒度太粗,失败时无法定位
- **本仓库对接**:fullstack4TraeV11 Stage 0 (plan) → Stage 3 (implement) 中间夹 Stage 0.5 (test-plan),就是为保证 plan 阶段**先**输出 atomic tasks
- **反例**:"实现登录功能"作为一个 task,实际包含 JWT 签发 + 中间件 + 路由 + 前端表单 4 个子任务,任何一个失败整体重来

### 规则 3 — 每个边界人工 review,不要"信任 agent"

- **MUST**:每个 task 完成 → 人工 review(spec 偏离 / 安全漏洞 / 命名规范) → 通过才进下一 task
- **MUST NOT**:"agent 写完我自己没看,直接 commit" — 这是 67% AI 代码需大量修改的根因
- **本仓库对接**:guard-approver 的 Tier 3 路径(.husky / .github / scripts / src)强制要求 `release-manager` 审批 — **边界 review 制度化**
- **反例**:agent 写完整个模块,人工 review 时发现 30% 偏离 spec,但已经"太晚"不愿重写 → 累积技术债

### 规则 4 — 自动化自验,人只看异常

- **MUST**:每个 atomic task 必须有**可自动跑的验证命令**(npm run test:unit / structure-guard.py / scan_skills_dir.py),失败 → 立即阻断
- **MUST NOT**:依赖"人工点击 UI 看看能不能用"作为唯一验收
- **本仓库对接**:三层控制(Gate L1-L4 + Guard × 6 + Execution CP1-CP6)就是为这一规则服务的 — 跑 L1 commit gate 时,任何阶段失败 exit ≠ 0 立即阻断
- **反例**:agent 写完 → 人工"感觉没问题" → commit → CI 第一次跑全红(28% 首次通过率)

### 规则 5 — spec 版本化,可回滚

- **MUST**:spec.md / plan.md / tasks.md 跟代码同仓,git log 可追溯;每次大改前先打 spec tag
- **MUST NOT**:spec 只在 Notion / Confluence — agent 无法读取,人工维护成本高,版本漂移
- **本仓库对接**:fullstack4TraeV11 `.trae/specs/<change-id>/spec.md` + Stage 11 (accept) 走 `spec-knowledge-extract` 把 spec 沉淀为知识资产
- **反例**:"我们 spec 在飞书" → 3 个月后没人记得为什么这么设计 → 重构时再次踩坑

### 规则 6 — 团队对齐,不只单兵

- **MUST**:spec / plan 必须 team-review 通过才开始 implement
- **MUST NOT**:"我一个人 vibe coding 一周,然后让团队 review 我的 PR" — 团队已经晚了
- **本仓库对接**:guard-approver 接入 GitHub PR 流程(下一轮) — team-lead / qa-lead / release-manager 跨角色 review
- **反例**:单兵 vibe coding 3 周,合并时发现跟团队其他模块的接口完全不一致,返工 2 周

### 规则 7 — 失败 metric 公开,数据驱动决策

- **MUST**:跟踪 `重构活动 -60% / 代码重复 4x / AI 代码 CI 首次通过率 / 月 N 后崩率` 等指标
- **MUST NOT**:"感觉 vibe coding 挺好用" 或 "感觉 SDD 慢了" — 都需要数据说话
- **本仓库对接**:acceptance-discipline 提供 metrics.md 模板;GitClear 数据可作外部基准
- **反例**:不跟踪指标,3 个月后才发现 AI 生成代码里 30% 是 dead code,但已经没人愿意清

## 与本仓库的覆盖度

| 规则 | 落地状态 | 关联文件 |
|------|---------|----------|
| 1. 写 spec 在前 | ✅ | fullstack4TraeV11/stage-1-spec |
| 2. 不要跳过 plan | ✅ | fullstack4TraeV11/stage-0-plan + stage-0.5-test-plan |
| 3. 每个边界 review | ✅ | guard-approver Tier 3 |
| 4. 自动化自验 | ✅ | .husky/pre-commit + pre-push + skill-market-gate.yml |
| 5. spec 版本化 | ✅ | .trae/specs/ + stage-11-accept 沉淀 |
| 6. 团队对齐 | ⚠️ 部分 | guard-approver 当前仅 L1/L2,L3 CI 待接入 |
| 7. 失败 metric 公开 | ❌ | 待引入 acceptance-discipline metrics 模板 |

## 一句话总结

**vibe coding 不是被替代,而是被 Harness 装上导航和护栏**。7 条规则 = 导航(spec/plan) + 护栏(边界 review + 自动化自验 + spec 化)。长期维护的代码必经此路。

## 引用

- [external-report §M-02](file:///d:/workspace/my-trae-helper/logs/daily-vibe-coding/2026-08-14/external-report.md) — 原始调研
- [GitHub Spec Kit](https://github.com/github/spec-kit) — 工具实现
- [MetaMindz 7 Rules](https://www.metamindz.co.uk/post/spec-driven-development-rules-beat-vibe-coding-2026) — 规则归纳
- [self-audit 2026-08-14](file:///d:/workspace/my-trae-helper/logs/daily-vibe-coding/2026-08-14/self-audit.md) — 本仓库覆盖度
