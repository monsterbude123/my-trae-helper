# Common Iron Rules — 公共铁律（所有 stage 必读）

> V11 所有 13 stage skill 必读的公共铁律。每条铁律引用 16 Articles 宪法。

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
11.1 所有 skill 文件遵循 ≤10 铁律
11.2 所有 skill 文件遵循 ≤150 行（V10.12 减肥）
11.3 新增铁律必走 Article XVI §1.4 修复成本校验
11.4 引用 references/ 而非内联（不腐化自己）
```

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
14.2 腐化扫描必跑（8 项：视觉/归档/自验/孤儿/构建/吹嘘/状态卡/骨架）
14.3 fix-list.json 必产出且不可空
14.4 NO ROT NO ACCEPT — 任一 FAIL = 🛑 REJECT Accept
```

## Article XV — Obstacle Honesty（V11 全 stage 适用）

```
15.1 任何阻塞必 5 字段诚实汇报（type/description/attempted_solution/time_consumed/attempt_count）
15.2 禁止跳过（"先继续，回头再看"）
15.3 禁止隐藏（"等下修，先标完成"）
15.4 禁止抽象理由（"理解偏差"/"流程裁剪"/"心理障碍"）
```

## Article XVI — Skeptical Validation（V11 全 stage 适用）

```
16.1 P0/P1 修复或升级方案必走质疑性校验 4 维度
16.2 根因验证（每个主张是否真实存在，附 file:line）
16.3 责任主体校验（修复点是否在正确层）
16.4 重叠校验（与已有规则是否重叠，差异化论证）
16.5 修复成本 vs 价值校验（避免低价值修复）
```

---

## 关联引用

- [constitution.md](constitution.md) — 16 Articles 全文
- [common-anti-patterns.md](common-anti-patterns.md) — 公共反模式
- [stage-card-protocol.md](state-card-protocol.md) — 状态卡协议