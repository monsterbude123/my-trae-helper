# Common Iron Rules — 公共铁律（所有 stage 必读）

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> V11 所有 13 stage skill 必读的公共铁律。每条铁律引用 17 Articles 宪法。

---

## Article I — Quality First（V11 全 stage 适用）

```
1.1 代码质量优先于开发速度
1.2 不可为赶进度降低测试覆盖（≥90%）
1.3 不可为赶进度降低代码卫生（≤800行/文件 ≤50行/函数）
1.4 不可为赶进度跳过文档（spec/contract/README 同步）
```

## Article IV — TDD Driven（Stage 3 强制，其他 stage 适用）

```
4.1 改实现/删组件 → 立即同步改测试/删测试
4.2 RED → GREEN → REFACTOR + DRIFT CHECK 三步循环
4.3 不可修改测试让用例通过（虚假绿灯）
4.4 不可跳过 RED 阶段（必先写失败测试）
```

## Article V — Verifiable Claims + GitNexus First（V11 全 stage 适用，V11 强化）

```
5.1 每个主张必附事实证据（command + output + file:line）
5.2 不可声称"已完成"而无证据
5.3 量化必汇报（test/contract_tests/coverage 三个数字必填）
5.4 不量化不验收
5.5 GitNexus First：改 symbol 前必跑 impact()（V10 Article V 蒸馏，V11 不可降级）
5.6 探索代码用 query() / context()，不用 grep
5.7 实施 / Bug / Health 4 个 stage 必走 GitNexus MCP 工具
5.8 GitNexus 不可用 → L4 异常 → 标注风险 + 汇报用户（不静默降级）
```

**主旨（V10 Article V 蒸馏）**: 影响面评估用工具不用 grep。

**Rationale**: grep 不理解符号语义，容易漏掉跨模块影响。GitNexus 提供准确的 call graph。

**Enforcement（V11 蒸馏 V10）**:
- 主上下文改符号前必须调 GitNexus impact()，禁止手动 grep
- 实施者必读 impact / context / query / detect_changes 4 工具调用清单
- Reviewer 边际维度必跑 impact + 公共模块 + 全量回归 + 模块文档（4 项检查）
- 失败时执行 **3 次重试协议**（修参数 → 换工具 → list_repos），仍失败 → 停下汇报用户

### 反例索引

- 反例 23（V10 process-rot-analysis.md 蒸馏；见 references/common-anti-patterns.md）
- [common-anti-patterns.md](common-anti-patterns.md) — 公共反例库

## Article VIII — Archive Immutable（Stage 5 强制）

```
8.1 归档目录（docs/archive/done/）下文件禁止修改
8.2 归档只能新增，不可删除
8.3 修改归档 = 🛑 REJECT 流程违规
8.4 归档修改必新建 change 重新走流程
```

## Article IX — Cross-Session Verify（V11 全 stage 适用）

```
9.1 自评 = self_attested，主上下文必二次抽检
9.2 子代理"已通过"不等于主上下文已通过
9.3 reviewer 必亲自跑测试，不接受 implementer 自评
9.4 e2e 必 INITIAL FAIL（证明 bug/功能真实存在）
```

## Article XI — Self-Contained Constraints（所有 skill 文件适用）

```
11.1 所有 skill 文件遵循 vibe-coding-standards v2.5 弹性 100~350 行（非硬上限）
11.2 超阈按"指针引用"原则瘦身（拆 references/），而非裁剪内容
11.3 新增铁律必走 Article XVI §1.4 修复成本校验
11.4 引用 references/ 而非内联（不腐化自己）
```

> 修订：原 11.1/11.2 "≤10 铁律 + ≤150 行" 与 2026-08-14 AGENTS.md §1 #3 修订冲突（已删除硬编码铁律上限）。本条目现引用 vibe-coding-standards v2.5 弹性范围。

## Article XII — Workflow Discipline（V11 全 stage 适用）

```
12.1 必走完整流程：Intake → Plan → Spec → Contract → Implement → Real Verify → Review → Rot Scan → Accept
12.2 不可跳过 stage（除非显式豁免）
12.3 不可反向（Stage 4 Review 不修代码，Stage 5 Accept 不重写代码）
12.4 状态卡必更新（每 stage 必改 stage_status + updated_at）
```

## Article XIII — Visible Product（Stage 3.5 强制）

```
13.1 启动可见产物是唯一信任基础，不接受自评
13.2 Web/Tauri/CLI/Library/Backend 5 类项目分别定义验证产物
13.3 必有可见产物（截图 ≥5KB / curl 200 / 输出 ≥10 行）
13.4 主上下文必亲自 Read（不委派子代理）
```

## Article XIV — No Rot No Accept（Stage 4.5 强制）

```
14.1 Phase 4.5 rot-detector 不可跳过
14.2 腐化扫描必跑（10 项：V10.5 8 项 + V10.10 +2 项；视觉/归档/自验/孤儿/构建/吹嘘/状态卡/骨架/obstacle-honesty/reason-fabrication）
14.3 fix-list.json 必产出且不可空
14.4 NO ROT NO ACCEPT — 任一 FAIL = 🛑 REJECT Accept
```

## Article XV — Obstacle Honesty（V11 全 stage 适用）

```
15.1 任何阻塞必 5 字段诚实汇报（type/description/attempted_solution/time_consumed/attempt_count）
15.2 禁止跳过（"先继续，回头再看"）
15.3 禁止隐藏（"等下修，先标完成"）
15.4 禁止以不可证伪术语作为失败归因。允许的失败归因形式见 [agent-error-diagnosis.md](agent-error-diagnosis.md) §3 5 模式诊断。
```

## Article XVI — Skeptical Validation（V11 全 stage 适用）

```
16.1 P0/P1 修复或升级方案必走质疑性校验 4 维度
16.2 根因验证（每个主张是否真实存在，附 file:line）
16.3 责任主体校验（修复点是否在正确层）
16.4 重叠校验（与已有规则是否重叠，差异化论证）
16.5 修复成本 vs 价值校验（避免低价值修复）
```

## Article XVII — Secret Redaction（V11 全 stage 适用，P0 安全）

> **新增**：蒸馏自 V10.12 V11 实战反馈。Agent 把用户提供的密码/token 写到工具调用参数 → 工具调用日志 = 明文泄露。

```
17.1 用户提供的 secret（密码 / token / API key / cookie）→ 必通过环境变量 / .env 注入，**绝不**写到工具调用参数里
17.2 工具调用参数中出现 secret → 🛑 REJECT + 立即通知用户改密码
17.3 .env / secrets/ / credentials/ → forbidden_paths 强制禁读
17.4 即使"测试用"的 secret 也不写到 commit / tool log / 截图
17.5 secret 误写 → 立即回滚 + 用户重置 + 写入 audit log
17.6 shell / script 中出现的 $PASSWORD / $TOKEN → 必用 ${VAR:-} 形式 + 在 audit log 中 redacted
```

### Article XVII 反例索引

详见 [common-anti-patterns.md](common-anti-patterns.md) §反例索引 P0 §22 secret-in-tool-arg

---

## 关联引用

- [constitution.md](constitution.md) — 17 Articles 全文
- [common-anti-patterns.md](common-anti-patterns.md) — 公共反模式
- [stage-card-protocol.md](state-card-protocol.md) — 状态卡协议
