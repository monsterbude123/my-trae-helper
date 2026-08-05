# §15 FAQ

---

### Q1：我们团队很小（3-5 人），需要这么完整的体系吗？

**A**：体系大小应该匹配团队规模。3-5 人团队建议：
- 必做：5 条铁律（§0.1）+ PR Self-Check（checklists.md）+ Workflow B（e2e-audit-agent.md）
- 选做：度量看板（metrics.md）+ 性能基线（perf-verification-agent.md）
- 暂缓：L3 Release Gate 全套（gate-keeper-agent.md）—— 用简化版

**核心原则**：铁律不可妥协，流程可以裁剪。

---

### Q2：AI Agent 真的会按 AI 协议执行吗？

**A**：会，但需要：
1. skill 文件放在 agent 可加载的位置（如 `~/.trae-cn/skills/` 或项目内）
2. 触发词匹配正确
3. 主 agent 监督子 agent 的执行，违反协议必须修正
4. worklog 记录每次验收任务，可追溯

**关键**：协议不是文档，是**可执行规则**。agent 不遵守时，主 agent 必须强制重做。

---

### Q3：测试覆盖率 70% 是不是太低了？

**A**：70% 是下限，不是目标。建议：
- 核心模块（auth / payment / 核心业务）：≥ 90%
- 一般模块：≥ 70%
- 工具函数 / 边角代码：≥ 50%

**反模式**：为了凑覆盖率写 Assertion-Free Test（bad-test-cases.md 案例 9）。覆盖率不是目的，能 catch bug 才是。

---

### Q4：E2E 跑一次太慢，能不能不跑？

**A**：不能不跑，但可以聪明地跑：
- 日常开发：Workflow B（即时诊断，秒级）
- PR 检查：只跑改动模块的 E2E（按目录分区）
- 夜间 CI：全量 E2E
- 发版前：必跑全量 E2E（Workflow A）

**铁律**：发版前必跑全量 E2E，没有例外。其他场景按需。

---

### Q5：Flaky Test 修不好怎么办？

**A**：按以下优先级处理：
1. **5 次内修复**：分析根因，重写测试
2. **5 次修不好**：标记 `@pytest.mark.skip(reason="Flaky: <issue链接>")`
3. **立 issue**：进入验收债务看板，Tech Lead 月度 review
4. **30 天内必须修复或删除**：不允许长期 skip

**禁止**：把 Flaky Test 标 `xfail` 凑数。xfail 是"已知失败但暂时不修"，不是 Flaky 的借口。

---

### Q6：性能基线和实际生产环境不一致怎么办？

**A**：基线环境与生产环境的差距是客观存在的。建议：
1. **基线环境规格 ≥ 生产环境 1/10**：保证基线有参考价值
2. **关注相对变化而非绝对值**：基线对比看"退化 10%"，不看"P99 必须 < 100ms"
3. **关键路径定期在生产灰度验证**：用真实流量抽样压测
4. **大促前必须跑容量测试**：在基线环境模拟峰值

---

### Q7：安全扫描报告一堆 HIGH 漏洞，修不完怎么办？

**A**：分级处理：
1. **CRITICAL**：立即修，阻断发版
2. **HIGH**：发版前必须修或例外申请
3. **MEDIUM**：30 天内修复
4. **LOW**：季度修复

**例外申请流程**（见 gate-keeper-agent.md）：提交影响评估 + 缓解措施 + 修复时间表，Tech Lead + 安全 Owner 双签字。

**禁止**：直接忽略扫描结果。所有 HIGH+ 必须有明确处置（修 / 例外 / 接受）。

---

### Q8：多 agent 并行开发时，怎么避免验收冲突？

**A**：按 ai-agent-protocol.md 的 RACI 矩阵执行：
1. 每个验收任务有且只有一个 Accountable
2. 主 agent 是发版门禁的 Accountable
3. 子 agent 完成自己的验收任务后，结果汇总到主 agent
4. 主 agent 跨子 agent 的冲突必须人工裁决

**典型冲突**：子 agent A 改了 API，子 agent B 的 E2E 因此失败。处理：主 agent 评估影响 → 协调 A 修复 B 的 E2E 或回滚 A 的 API 变更。

---

### Q9：本 skill 与原始三份 skill 的关系？

**A**：本 skill 是三份原始 skill 的**整合 + 扩展**：
- `test-experience` → 整合到 unit-test-agent + integration-test-agent
- `e2e-module-audit` → 整合到 e2e-audit-agent
- `test-partition-runner` → 整合到 blockage-resolver-agent
- 新增：perf-verification-agent / security-verification-agent / gate-keeper-agent / metrics / checklists / bad-test-cases / ai-agent-protocol / toolchain-guide / roadmap

**建议**：本 skill 上线后，原始三份可保留作为"深度参考"，但日常加载优先用本 skill。

---

### Q10：本 skill 多久 review 一次？

**A**：
- **每季度**：案例库 review（bad-test-cases.md）+ Checklist review（checklists.md）
- **每半年**：工具链评估（toolchain-guide.md）
- **每年**：完整体系年度复盘
- **事件驱动**：发生 P0/P1 事故后，立即 review 相关章节

**review 流程**：发起 issue → Tech Lead 主持 review 会议 → 修订 skill → 全员通知 → worklog 记录。

---

### Q11：如果 agent 不按协议执行，怎么追责？

**A**：agent 没有"追责"概念，但有"修正"机制：
1. 主 agent 发现子 agent 违反协议 → 立即停止子 agent → 重做
2. 主 agent 自己违反协议 → 用户/Tech Lead 发现 → 强制重做
3. 多次违反 → 在 worklog 记录 → 协议 review 时作为案例

**核心**：协议是规则，不是建议。违反必须修正，没有"这次就算了"。

---

### Q12：怎么衡量本 skill 自身的效果？

**A**：看以下指标的趋势：
- 验收债务条目数：应该单调下降
- 门禁一次通过率：应该上升
- 诊断闭环时长：应该缩短
- Flaky Test 数：应该减少
- 团队满意度（季度调研）：应该提升

如果以上指标 6 个月内没有改善，说明 skill 本身需要 review。
