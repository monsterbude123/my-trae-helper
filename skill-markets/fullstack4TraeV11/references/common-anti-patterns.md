# Common Anti-Patterns — 公共反模式库

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> V11 所有 stage 必读的公共反模式索引。每个反例指向具体 stage 的 anti-patterns/ 目录。

---

## 反例索引（按严重度）

### P0 阻断类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 1 | **跳过必走 stage**（V11 §0 硬门禁）| 各 stage SKILL.md §铁律 |
| 2 | **编造证据**（V10.12 ANTI-反模式）| Stage 3 implement/anti-patterns/02-fabricate-evidence.md |
| 3 | **reviewer 帮忙修代码**（REVIEWER DOES NOT FIX）| Stage 9 review/anti-patterns/02-reviewer-fix-code.md |
| 4 | **不可证伪理由**（如未定义术语、未指明位置的偏差、未量化裁剪、未测量心理负担、未定义的概念迁移）| 公共铁律 Article XV §15.4 |
| 19 | **循环 PASS 模式**（不止一次"我搞错了"+ 重新委派，无具体改进）| [./loop-pass-pattern.md](./loop-pass-pattern.md) |
| 20 | **甩锅用户模式**（"请你去做 X"代替自己能做的部分）| [./user-orchestration-pattern.md](./user-orchestration-pattern.md) |
| 21 | **未读 rule 就自评 PASS**（rule 太长不读 + 反复踩同一雷）| [./unread-rule-pass.md](./unread-rule-pass.md) |
| 22 | **secret 写入工具调用参数**（V11 实战 P0 安全事件）| [./secret-in-tool-arg.md](./secret-in-tool-arg.md)（Article XVII）|

### P1 高优类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 5 | **虚假绿灯**（修改测试让用例通过）| Stage 3 implement/anti-patterns/01-skip-red.md |
| 6 | **漂移静默**（实现与契约不一致不报告）| Stage 3 implement/anti-patterns/04-drift-silent.md |
| 7 | **跳过 rot-scan 直接 Accept** | Stage 10 rot-scan/anti-patterns/01-skip-rot-scan.md |
| 8 | **修复完不改 bug 单** | Stage 12 bug-fix/anti-patterns/03-not-update-bug.md |
| 9 | **跳过 e2e 先行直接修** | Stage 12 bug-fix/anti-patterns/01-skip-e2e-first.md |

### P2 中优类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 10 | **跳过 DOMAIN FIRST 直接写 API** | Stage 6 contract/anti-patterns/01-skip-domain.md |
| 11 | **跳过孤儿契约测试清理** | Stage 6 contract/anti-patterns/02-skip-orphan-sweep.md |
| 12 | **BREAKING 变更不用户确认** | Stage 6 contract/anti-patterns/03-breaking-without-confirm.md |
| 13 | **契约漂移**（代码与契约不一致）| Stage 6 contract/anti-patterns/04-contract-drift.md |
| 14 | **"非阻塞 FAIL" 放水** | Stage 9 review/anti-patterns/01-non-blocking-fail.md |
| 15 | **编造测试覆盖** | Stage 9 review/anti-patterns/03-fabricate-coverage.md |
| 23 | **GitNexus 可用却 grep / glob**（V10 process-rot-analysis.md 蒸馏） | 反例 23 本节已展开（Article V.5 + §19-22 cross-ref） |

## §23 GitNexus 可用却用 grep / glob（V12.0.0 沿用 V10.12 — 反例 23 独立标题段）

> **位置说明**: 本节按"反例 23"的独立标题段形式追加,便于 cross-stage 引用与 common-anti-patterns.md §23 在 unread-rule-pass.md §24 中同名编号引用时不冲突。

**现象**: Agent 知道 GitNexus 可用,仍 `grep -r "X" src/` / `Glob "**/*.ts"`,而非 `query({query: "X"})` / `context({name: "X"})`。

**根因**: `query()` / `context()` / `impact()` 调用需参数格式正确,部分 agent 偷懒用 grep 绕过。

**识别信号**:
- Agent 输出含 `grep -rn`、`find` 命令而非 `query()` / `impact()`
- 主上下文重跑工具发现 `gitnexus index` 已建但未被引用

**教训**: GitNexus 是项目级索引（32516 symbols / 39969 relationships,见项目 README gitnexus block）,不是装饰。grep 只能匹配字面文本,query() 走语义图谱;项目规模大时 grep 必然漏。

**正确替代**: 
```bash
# ❌ 错
grep -rn "create_user" src/

# ✅ 对
gitnexus query --query "create_user"
gitnexus context --name create_user
gitnexus impact --target create_user --direction upstream
```

### P3 低优类

| # | 反例 | 详细位置 |
|:---:|------|---------|
| 16 | **跳过知识沉淀直接归档** | Stage 11 accept/anti-patterns/01-skip-knowledge-extract.md |
| 17 | **修改归档文件** | Stage 11 accept/anti-patterns/02-modify-archive.md |
| 18 | **"启动 = 完成" 软指标** | Stage 8 real-verify/anti-patterns/01-startup-equals-done.md |

---

## 反例自检清单

```yaml
anti_patterns_checklist:
  P0:
    - [ ] 不跳 stage？
    - [ ] 不编证据？
    - [ ] reviewer 不改代码？
    - [ ] 无抽象理由？
    - [ ] 不循环 PASS（无具体改进的"我搞错了"+ 重新委派）？
    - [ ] 不甩锅用户（自己能做的部分不交给用户）？
    - [ ] rule 通读后才自评 PASS？
    - [ ] secret 不写入工具调用参数？
  P1:
    - [ ] 不虚假绿灯？
    - [ ] 漂移必报告？
    - [ ] 必跑 rot-scan？
    - [ ] 修复回写 bug 单？
    - [ ] e2e 必先 FAIL？
  P2:
    - [ ] DOMAIN FIRST？
    - [ ] 孤儿契约测试清理？
    - [ ] BREAKING 用户确认？
    - [ ] 契约三方同步？
    - [ ] 无"非阻塞 FAIL"？
    - [ ] 真实覆盖？
    - [ ] GitNexus 可用却 grep？（Article V.5 不可降级）
  P3:
    - [ ] 知识沉淀先于归档？
    - [ ] 归档不可修改？
    - [ ] 启动有可见产物？
```

---

## §7 commit 准入与全量验收分层反模式（V11.8.4 NEW — 蒸馏自 2026-08-15 merged-commits）

> **核心**: commit 准入最小集 ≠ 全量验收，二者必须解耦。这是 V11 §3.7 反虚假交付 #5 的镜像陷阱（反向 #10）。

### §7.1 视觉证据"至少 1 张"原则（V11.5+ 原条款）

```markdown
MUST: 任何 change 推进 Stage 4 之前,必须有真实浏览器截图证明 UI 集成层可见。
要求清单:
- 至少 1 张真实浏览器截图
- 截图必须包含本 change 实施的关键 UI 组件
- 截图必须证明端到端可交互(点击 → API 调用 → 状态变化)
- 截图必须由 Playwright MCP / Chrome DevTools MCP / 真实浏览器驱动
- 截图必须落盘到 docs/verifications/web/<change-id>/
```

### §7.2 视觉证据"几张是过度"原则（V11.8.4 NEW）

```markdown
NEVER: 把"至少 1 张"过度推论为"必须全量"
触发条件: 一个 change 涉及 >10 路由视觉验证
错误代价: 测试 30+ min,失败改 5 个 spec 版本仍卡,阻塞 commit
正确替代:
  - 关键 5 路由 spot-check(L3 真实浏览器截图,证明 UI 集成可见)
  - 60+ 路由视觉证据按 wave 拆模块 spec 异步跑(commit 后执行)
  - 用 §7.1 "至少 1 张" 作为下限,而非全量
```

### §7.3 commit 准入最小集 vs 全量验收（V11.8.4 NEW — 必读）

```markdown
MUST: commit 准入最小集 ≠ Stage 3.5 全量验收,二者解耦

commit 准入最小集(阻塞 commit):
  - typecheck 0 错(`tsc --noEmit`)
  - 关键 5 路由 spot-check(L3 真实浏览器截图)
  - 涉及 admin/auth/数据接口:1 个 admin 探针端点 200
  - lint 预存问题不阻塞(入 BUG-XX,后续单独修)

全量验收(commit 之后异步):
  - 60+ 路由视觉证据(按 wave 拆模块 spec 异步跑)
  - rot-scan / self-diagnose
  - 完整 vitest / build

NEVER: 把 Stage 3.5 全量视觉验证塞入 commit 阻塞路径
NEVER: 为避免"假完成"反例(V11 §3.7 #5)而把范围扩大到不可能完成(V11 §3.7 #10 反向陷阱)
```

### §7.4 测试"修一点跑一次"循环反模式（V11.8.4 NEW — 必读）

```markdown
NEVER: 失败 → 改一行 → 重跑 → 又失败 → 再改(无 Read 失败证据)
触发条件: 同一 spec 连续修改 ≥3 次仍失败
错误代价: 浪费 ~30 min,spec 文件 5 个版本未收敛

正确替代(模块化测试铁律):
  1. 立刻 StopCommand
  2. Read error-context.md / trace.zip
  3. Read fixture 实际行为(不能假设 timeout = 失败)
  4. Read 已有 PASS 视觉证据(如果存在)
  5. 列出"失败 vs 实际"差异表
  6. 一个 spec 一个模块,失败独立反馈,不耦合其他模块(模块化是反循环核心武器)
  7. 才改 spec
```

### §7.5 fixture timeout ≠ 登录失败（V11.8.4 NEW — 必读）

```markdown
NEVER: 假设 fixture timeout = 登录失败
触发条件: fixture 用 waitForURL 等路由跳转超时
错误代价: 反复修改无关 spec,浪费 5 个迭代版本

正确替代:
  1. Read fixture 实现(了解实际行为,如 supabase client-side 是否自动 redirect)
  2. Read 视觉 spec 已 PASS 的截图(证明登录成功)
  3. 检查 supabase/next-auth session 实际建立情况(cookie 是否落地)
  4. 用 page.waitForAuthed(email) 验证 cookie 已落地(项目侧约定)
  5. 跨 context cookie 必须用 page.evaluate(fetch) 而非 page.request(APIRequestContext 隔离)
```

### §7.6 自检清单（V11.8.4 NEW）

```yaml
commit_readiness_check:
  P0:
    - [ ] 不把"至少 1 张"推论为"必须全量"?
    - [ ] commit 准入最小集与全量验收已解耦?
    - [ ] 不为避免假完成而盲目扩大范围?
    - [ ] 同一 spec 失败 ≥3 次后立即 Read 失败证据?
    - [ ] fixture 状态用证据验证,不假设?
    - [ ] 跨 context cookie 用 page.evaluate(fetch)?
```

---

## 关联引用

- [constitution.md](constitution.md) — 17 Articles 宪法
- [common-iron-rules.md](common-iron-rules.md) — 公共铁律
- 各 stage anti-patterns/: skills/{NN}-{name}/anti-patterns/README.md
- [../SKILL.md §0.3 Stage 3.5 异步性声明](../SKILL.md) — V11.8.4 蒸馏同步
- [../SKILL.md §3.7 #10 范围盲目扩大](../SKILL.md) — 反虚假交付镜像陷阱
