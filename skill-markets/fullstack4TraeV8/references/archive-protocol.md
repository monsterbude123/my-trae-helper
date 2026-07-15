# Archive 归档协议

> **核心铁律**：归档 = 项目完成的最终声明。Agent 禁止自行判定"完成"后静默归档。
> **根因**：agent 在文档阶段完成后即执行归档，但 V2 REDESIGN 对应的代码根本没写。

---

## §1 归档前置硬门禁（6 项全部满足才放行）

```
归档前机械验证（Agent 逐项执行，写入门禁结果）:

  [ ] GATE 0 — 用户显式审批
      必须向用户展示:
        "以下内容将被归档:"
        "  - 已完成: [tasks.md 中已完成的任务清单]"
        "  - 未实现 V2 NEW/REDESIGN: [grep 结果清单]  ← 关键"
        "  - Mock 占位残留: [grep -c MOCK_ 统计]  ← 关键"
        "  - 确认归档？[Y/n]"
      Agent 不自行回答此问题，必须等用户明确输入。

  [ ] GATE 1 — tasks.md 完成度检查
      机械规则:
        - `[ ]` 或空 checkbox → 视为未完成 → 🛑 FAIL
        - `[x]` → 完成
        - `[SKIP]` → 显式跳过（需有原因注释）→ 接受
        - 全部为 [x] 或 [SKIP] → ✅ PASS
      命令: grep "\[ \]" tasks.md → 空 = PASS

  [ ] GATE 2 — V2 REDESIGN 标记解析审计
      机械规则:
        - grep "V2 NEW\|V2 REDESIGN\|V2 重大" specs/ prototypes/
        - 有匹配 → 列出未解析项清单
        - 每项检查 design.md 是否有对应的 RESOLVED 声明
        - 有 RESOLVED → 通过
        - 无 RESOLVED → 🛑 FAIL
      命令: grep -r "V2 NEW\|V2 REDESIGN\|V2 重大" specs/ prototypes/

  [ ] GATE 3 — 实现代码存在性检查
      机械规则:
        - git diff --stat HEAD~1 必须包含 src/ 或 src-tauri/ 变更
        - 若 diff 仅含 docs/ → 🛑 FAIL（纯文档提交伪装成实现）
      命令: git diff --stat HEAD~1 | grep "src/"

  [ ] GATE 4 — DECISIONS.md 决议完整性
      机械规则:
        - DECISIONS.md 中所有决策条目 → 必须是 [x] 状态
        - 有 [ ] 条目 → 🛑 FAIL (未决议不可归档)
      命令: grep "\[ \]" DECISIONS.md → 空 = PASS

  [ ] GATE 5 — Mock 占位检测（V9.5+1 NEW）
      机械规则:
        - grep -c "MOCK_" src/ → 统计 mock 常量数量
        - > 10 → 🛑 FAIL "mock 数据过多（{N}处），真实实施不完整"
        - 3~10 → ⚠️ 警告 "检测到 {N} 处 mock 数据，可能未完成真实实现"
        - ≤ 3 → ✅ PASS（少量 mock 可能是测试 fixture，可接受）
        - 检查 closure-checklist.md Stage 5 状态
        - STAGE_5_PENDING → 🛑 FAIL "真实数据联调未启动"
      命令: grep -r "MOCK_" src/ | wc -l && grep "Stage 5" closure-checklist.md
      注意: 检测不限于 MOCK_ 前缀，扩展覆盖常见 mock 模式:
        - 全大写 MOCK_* 常量
        - todo!() / unimplemented!() 宏（Rust）
        - stub_ / fake_ / dummy_ 前缀（任何语言）
        - throw new Error('Not implemented') / raise NotImplementedError
```

---

## §2 归档与完成的语义分离

```
当前职责混淆:
  Phase 8 Accept → 📦 Archive
  (验收通过即归档，但验收可能只是功能验收，并非项目完成)

分离后:
  Phase 8   Accept           → E2E + 性能 + 安全门禁（功能层面验收）
  Phase 9   Pre-Archive Audit → 实现完成度验证（6 项门禁 §1）
  Phase 10  Archive           → 验证通过后才归档
```

---

## §3 门禁判定表

| 门禁 | 检查对象 | 判定标准 | FAIL 动作 |
|------|---------|---------|----------|
| GATE 0 | 用户审批 | 用户显式输入 Y | 🛑 等待用户 |
| GATE 1 | tasks.md | 无 `[ ]` 条目 | 🛑 列出未完成项，阻塞 |
| GATE 2 | specs/ + prototypes/ | V2 NEW/REDESIGN 全有 RESOLVED | 🛑 列出 UNSOLVED 项，阻塞 |
| GATE 3 | git diff | 含 src/ 变更 | 🛑 "无代码变更，不能归档" |
| GATE 4 | DECISIONS.md | 全 [x] 状态 | 🛑 列出未决议项，阻塞 |
| GATE 5 | src/ mock 密度 + Stage 5 | MOCK_ ≤ 3 且 Stage 5 非 PENDING | 🛑 mock > 10 → FAIL；Stage 5 PENDING → FAIL |

---

## §4 归档执行流程

```
Phase 9 Pre-Archive Audit 通过（6 GATE 全 ✅）
  ↓
主上下文输出归档预览:
  ┌─────────────────────────────────────────┐
  │ 📦 归档预览                              │
  │                                          │
  │ Change: {编号} - {标题}                   │
  │ Tasks:   12/12 [x]                       │
  │ V2标记:  2 RESOLVED, 0 UNSOLVED          │
  │ 代码变更: src/ctl/mod.rs + src/ui/app.rs  │
  │ 决策:    4/4 [x]                         │
  │ Mock:    2/3 (≤3)  Stage 5: ✅ COMPLETED     │
  │                                          │
  │ → 已满足全部归档门禁。确认归档？[Y/n]      │
  └─────────────────────────────────────────┘
  ↓
用户确认 Y
  ↓
Phase 10 Archive:
  1. 移动 changes/{编号} → archive/done/{编号}
  2. 更新 Cockpit 驾驶舱（归档记录 + 健康度）
  3. 提交: git add + commit "[Archive] {编号} - {标题}"
```

---

## §5 归档后缺陷处理

```
归档后发现的缺陷 → 禁止解封 archive/ → 创建新 change:
  1. Intake 识别缺陷影响面
  2. 创建新 change（编号递增）
  3. spec 引用原 change archive 路径
  4. 独立走流水线修复 → 独立归档
```

---

## §6 禁止行为

| 禁止 | 后果 | 替代 |
|------|------|------|
| Agent 自行判定"完成"后静默归档 | 用户不知道被归档，未实现功能被"完成" | GATE 0 用户显式审批 |
| 文档阶段完成后直接归档 | V2 REDESIGN 原型写完代码没写 | GATE 2 V2标记解析审计 |
| tasks.md 有 [ ] 仍归档 | 未完成任务被标记为完成 | GATE 1 机械检查 |
| 纯文档变更伪装成实现归档 | 只有设计没有代码 | GATE 3 src/ diff 检查 |
| Mock/Stub 代码伪装成完成实施 | mock 密度 > 10 或 Stage 5 未启动 | GATE 5 mock 密度 + Stage 5 检查 |
| 归档后解封修改 archive/ 文件 | 破坏归档完整性 | 创建新 change 处理缺陷 |
