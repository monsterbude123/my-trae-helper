---
description: V11.8.2 Stage 6 Phase A bug-hunt 实战报告 — 蒸馏自 2026-08-15 单次 90 min / 14 模块 / 16 bug 全流程。V11.8.2 起本报告迁入 Stage 6 子段（references/bug-hunt-battle-report.md），与 bug-hunt 工具脚本折叠进 Stage 6 scripts/bug-hunt/ 子包。下次项目用 V11 自动带出 bug-hunt 能力，无需独立 install 任何 sub-skill。
alwaysApply: false
enabled: true
updatedAt: 2026-08-15
version: 1.1.0
provider:
---

# Bug-Hunt 实战报告（V11.8.2 Stage 6 Phase A 子段）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../../../../skills/09-review/SKILL.md) · [贾维斯门禁守护](../../../../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.8.2](../../../../CHANGELOG.md)

> **本文件定位**（V11.8.2 NEW）：Stage 6 Bug Fix & Hunt 统一工序的 **Phase A 实战段**（批量 bug 发现）。本报告与 [bug-hunt-phase-a.md](bug-hunt-phase-a.md) / [bug-hunt-4d-observation.md](bug-hunt-4d-observation.md) / [bug-hunt-5-check.md](bug-hunt-5-check.md) 三段协同 — Phase A 是 3 步流程骨架，本报告是 90 min / 14 模块实战数据蒸馏。
>
> **V11.8.2 升级（关键）**：本报告从 `references/stage-08-real-verify-battle-report.md`（V11 公共层）迁入 `skills/12-bug-fix/references/bug-hunt-battle-report.md`（Stage 6 子段），bug-hunt-tooling 工具脚本折叠进 Stage 6 `scripts/bug-hunt/` 子包。下次项目用 V11 自动带出 bug-hunt 能力，无需独立 install bug-hunt-tooling skill。

---

## §0 为什么需要本报告

### 0.1 三层痛点（V11 实战蒸馏）

V11 13 stage 流水线虽然完整，但**真实 bug-hunt / E2E 场景**往往**横跨多个 stage**，产生 3 类痛点：

| 痛点 | 失败案例（2026-08-15） | V11 现状 |
|------|----------------------|----------|
| **A 反虚假交付失效** | Stage 3.5/4 自评 PASS，但真浏览器端到端 UI 截图含 signin 重定向（不是目标页） | V11 §3.7 #6/8 已声明，但缺**强制 Read 截图 + visible_text 验证**的子代理头部模板 |
| **B 14 模块串行未委派** | 90 min / 14 模块串行，主代理亲自 navigate，27 min 浪费（V11 §1.6 反 AI 自律） | V11 §1.6 已声明，但缺**模块数判定 + 自动拆 sub-agent** 的工具脚本 |
| **C bug 单 status 状态分裂** | BUG-003/004/015 修复后 bug 单 `.md` `status: OPEN` 未回写，只有 index.md 改 FIXED | V11 §8 已声明，但缺 **status 三文件同步守恒**（bug 单 + index.md + state-card.md） |

### 0.2 与现有 references 的差异化论证（Article XVI §1.3）

| 现有 references | 主题 | 本报告差异化 |
|----------------|------|--------------|
| `stage-physical-isolation.md` | 阶段物理隔离（fact/ + stage/ 目录布局） | 本报告聚焦 **bug-hunt 跨 stage 实战**，不重复目录布局 |
| `sub-agent-rules.md` | 子代理通用铁律（8 大类） | 本报告提供 **bug-hunt 专用 [TOOL-HINTS] 注入**，不重复通用铁律 |
| `stage-card-protocol.md` | 状态卡协议 | 本报告聚焦 **bug 单（独立于 change 卡）+ 三文件同步**，不重复 change 状态机 |
| `agent-error-diagnosis.md` | 5 模式失败根因 | 本报告聚焦 **bug-hunt 专属反例**（截图假证据 / HMR stale / status 分裂），不重复通用失败模式 |
| `unread-rule-pass.md` | 跳读反例库 | 本报告聚焦 **bug-hunt 工具脚本强制复用**，不重复跳读反例 |
| `loop-pass-pattern.md` | 循环通过模式 | 本报告聚焦 **bug-hunt 单次循环的 5 步流程**，不重复循环反例 |

**结论**：本报告**不重复**任何现有 references，**只补充** bug-hunt / E2E 跨 stage 实战的工具脚本集合 + 委派头部模板 + 反例库。

---

## §1 bug-hunt/E2E 在 V11 13 stage 的位置

### 1.1 跨 stage 映射

bug-hunt / E2E 工序**不是某个 stage 独占**，而是**横跨 3 个 stage**：

```
Stage -1 Intake（bug 录入触发词识别）           → V11 §8 bug 单 6 字段
   ↓
Stage 6 Bug Fix（独立支线，可由任一 stage 触发）   → V11 6 层排查 + e2e 先行
   ↓
Stage 3.5 Real Verify（实施后端到端真验证）       → V11 §3.7 启动可见产物
   ↓
Stage 4 Review（AC 核销门禁）                     → V11 V11.6.0 ac-gate.py
```

### 1.2 bug-hunt / E2E 工序全景（5 步）

```
Step 1 [观察]  N 模块按 4 维度（visible_text / behavior / data / console_logs）扫描
              → 差异即 bug
Step 2 [落单]  bash scripts/bug-hunt/new-bug.sh BUG-NNN <module> <route> [severity] [evidence]
              → 主代理补 Description + Fix（V11 §8 6 字段 + Severity L1-L4）
Step 3 [修复]  委派 sub-agent：[TOOL-HINTS] 头部（见 §5）+ sed -i 回写 status
Step 4 [归档]  pwsh scripts/bug-hunt/archive-screenshot.ps1 -Slug "<bug-id>-<state>"
              → 删除中间截图（signin-redirect / ssr-loading / 失败状态）
Step 5 [回写]  sed -i 改 status: FIXED；主代理改 index.md + state-card.md
              → grep 反向校验一致（见 §6）
```

### 1.3 与 V11 Stage 6 Bug Fix 的关系

| 维度 | V11 Stage 6 Bug Fix | 本报告 bug-hunt 工序 |
|------|---------------------|---------------------|
| 触发 | 单 bug 录入 | 批量扫描（≥10 个模块） |
| 范围 | 单 bug 根因 → TDD 修复 | 14 模块观察 → 16 bug 落单 → 批量修复 |
| 委派模式 | V11 §0.5 头部 + Stage 6 SKILL.md | 本报告 §5 [TOOL-HINTS] 头部 |
| 产物 | 1 个 bug 单 CLOSED | N 个 bug 单 + 状态机守恒 |

---

## §2 真登录取证 7 步（必走 — V11 §3.7 #6 反例）

### 2.1 7 步方法论

> **铁律**：任何受 supabase auth 保护的路由（`/zh/home`、`/zh/workspace/*`、`/zh/admin/*`、`/zh/auth/*`），必须先走完 7 步取得**已登录态**真实证据，再截屏 + 落单。

```yaml
M2.1 — 启动 dev server:
  目的: 确保 next-server + worker + watchdog + board 全部就绪
  执行: pwsh -NoProfile -File scripts/bug-hunt/dev-hmr-recovery.ps1
  验证: dev log 输出 "✓ Ready in Xs"（X 可接受 5-30s）
  反例: 未等 Ready 就 navigate → 拿到 SSR loading 中间态 → 误判 stale

M2.2 — Playwright 打开 signin 路由:
  目的: 在受保护路由 navigate 之前，必须先打开 signin 灌 session
  <!-- scan-whitelist:HTTP_INSECURE -->执行: mcp__playwright__playwright_navigate http://localhost:3000/zh/auth/signin<!-- /scan-whitelist -->
  验证: playwright_get_visible_text 出现 "邮箱" / "password" / "登录" 任一关键字
  反例: 直接 navigate /zh/home → middleware 重定向 → navigate 失效 → 误以为页面空白

M2.3 — 灌入凭据 + 提交:
  目的: 让 supabase 写入 session cookie + 完成 auth.users 查询
  执行: |
    mcp__playwright__playwright_fill("input[name='email']", "<email>")
    mcp__playwright__playwright_fill("input[name='password']", "<password>")
    mcp__playwright__playwright_click("button[type='submit']")
  验证: 等 1-2s 让 supabase server 写 session
  反例: 提交后 0s 立即 navigate → session 未写入 → 仍受 middleware 重定向

M2.4 — 等 supabase 写入 session + redirect:
  目的: 让 client useEffect 触发页面跳转 / 状态同步
  执行: 等 1-2s 或直接 navigate 目标路由让 client 跳
  验证: URL 已 redirect 出 /zh/auth/signin
  反例: 未等就 navigate → 拿到 signin 页内容 → 误判

M2.5 — Navigate 目标路由:
  目的: 进入真正要观察的受保护路由
  执行: mcp__playwright__playwright_navigate <target_route>
  验证: URL 保持目标路由（未被重定向回 signin）
  反例: 未登录 session 就 navigate → 永远被弹回 signin

M2.6 — 截图前必 verify visible_text:
  目的: ⭐ 防止"截图里是 signin 表单但主代理没读图直接标 PASS"假证据
  执行: mcp__playwright__playwright_get_visible_text
  判定:
    ✅ 通过 — 出现 1 个 + 期望路由关键字
            例: /zh/home → "欢迎回来" + "2910226625@qq.com"
            例: /zh/workspace → "进行中" + 剧集列表
            例: /zh/admin/cinema-knowledge/vocabulary → "规范词汇" + 表格
    ❌ 假证据 — 可见文本是 signin 表单内容（"邮箱"/"password"）
               → 还在登录前态，必须回到 M2.3
    ❌ 后端异常 — 可见文本是 error.tsx 内容（"返回工作区"/"500"/"刷新重试"）
               → 后端报错，必须查 dev server log 找根因
  反例: 仅截图不读图 → 误导主代理标 PASS（V11 §3.7 #6 AI 描述≠像素）

M2.7 — screenshot + 归档:
  目的: 落 evidence 到版本控制
  执行: |
    mcp__playwright__playwright_screenshot   # 写到 $USERPROFILE/Downloads
    pwsh -NoProfile -File scripts/bug-hunt/archive-screenshot.ps1 -Slug "<bug-id>-<state>" -SubDir "bug-hunt"
  验证: ls docs/evidence/<date>/bug-hunt/<slug>.png 存在
  反例: 信任 screenshot filename 参数 → 实际写到 Downloads → 截图散落
```

### 2.2 真登录 7 步 vs V11 fixture

| 场景 | 真登录 7 步手写 | fixture（auth-fixture.ts signedInPage） |
|------|----------------|----------------------------------------|
| 主代理 / sub-agent 临时观察 | ✅ 适用（一次性） | ❌ 不适用（要重启 dev server） |
| 长期 e2e 测试 | ❌ 浪费（每次重跑） | ✅ 推荐（一次 setup + storageState 复用） |
| bug-hunt 临时取证 | ✅ 适用 | ❌ 不适用 |

**MUST**：bug-hunt 场景**走 7 步手写**（临时取证）；长期 e2e 测试**走 fixture**（开发测试）。两者不混用。

---

## §3 4 维度观察法（V11 §3.7 跨维度验证）

### 3.1 4 维度定义

| 维度 | 工具 | 检查点 | 失败对应 |
|------|------|--------|----------|
| **视觉** | playwright_screenshot + get_visible_text | 截图含期望关键字/图标/配色；字体未降级；布局未塌缩；主题色应用到 | L3 视觉走样 |
| **行为** | playwright_click + hover + press_key | 关键 CTA 点击触发期望动作；hover 显示 tooltip；表单提交成功；路由跳转带 query | L2 局部不可用 |
| **数据** | playwright_get_visible_text + i18n key 检查 | mock 列表非空；i18n key 翻译；数据字段完整；dropdown 选项对齐后端 | L2/L3 |
| **控制台** | playwright_console_logs | 0 [error] / 0 401/403/404/500 / 0 hydration mismatch / 0 Unhandled Rejection | L2（API 401 类） |

### 3.2 4 维度交叉判定

| 视觉 | 行为 | 数据 | 控制台 | 判定 |
|:---:|:---:|:---:|:---:|:---:|
| ✅ | ✅ | ✅ | ✅ | **PASS** |
| ✅ | ❌ | * | * | **L2** |
| ✅ | * | ❌ | * | **L2** |
| ✅ | * | * | ❌ | **L2**（API 401 类） |
| ❌ | * | * | * | **L3** 视觉走样 |

**反 V11 §3.7 #8 反例**：API 200 + 空 fallback → 视觉仍 OK → 误判 PASS。**4 维度全过才 PASS**。

---

## §4 5 项证据独立抽检（M6 — V11 §3.7 #7 盲信反例）

### 4.1 主代理抽检 5 项（必走）

> **铁律**：主代理收到 sub-agent 报告后**必须**跑 5 项独立抽检，**不可盲信 sub-agent 产物**。
> **反例**：V11 §3.7 #7 盲信子代理"已完成" → 不抽检 evidence → 假证据通过。

```yaml
M6.1 — 抽检 screenshot 视觉内容:
  工具: Read <screenshot_path>（file:// 链接）
  验证:
    - 截图是否对齐 sub-agent 描述（DOM 文本 / 关键 widget 出现）
    - 是否有 Next.js red error overlay
    - 是否有 signin 表单泄露（未登录态假证据）
  反例: 盲信 "截图已归档" → 未读图 → 假证据通过
  触发 REJECT: 任何 mismatch

M6.2 — 抽检 visible_text 关键句:
  工具: mcp__playwright__playwright_get_visible_text
  验证:
    - 重新 navigate 目标路由 + 取 visible_text
    - 与 bug 单 evidence 段 quoted 文本 diff
  反例: 盲信 sub-agent visible_text → 实际环境已变
  触发 REJECT: 任何缺失关键字

M6.3 — 抽检 console error / 401:
  工具: mcp__playwright__playwright_console_logs
  验证:
    - 0 [error] level errors
    - 0 401 / 403 / 404 / 500
    - 0 hydration mismatch
  反例: 盲信 "console 干净" → 实际 401 仍在
  触发 REJECT: 任何 [error] 或 4xx/5xx

M6.4 — 抽检 bug 单 + index.md + .state-card.md 三文件状态:
  工具: Grep "BUG-NNN" docs/bugs/index.md + Grep "status" docs/bugs/<date>/<BUG-NNN>.md
  验证:
    - bug 单 status 字段 == index.md status 列 == .state-card.md 行
    - 无 OPEN / FIXED 错位
  反例: 盲信 sub-agent "已回写" → 实际只改 bug 单 → index.md 仍 OPEN
  触发 REJECT: 任何文件不一致

M6.5 — 抽检 git diff / commit message:
  工具: git log --oneline -5 <branch> + git show <hash> --stat
  验证:
    - 是否仅改必要 file（最小变更原则）
    - commit message 是否引用 bug_id（issue tracker 习惯）
    - 是否含 vitest pass / playwright verify 证据
  反例: 盲信 "commit 已落" → 实际改了一堆无关文件
  触发 REJECT: 任何不在 bug-fix 范围的文件
```

### 4.2 抽检流程

```yaml
sequence:
  M6.1 → M6.2 → M6.3 → M6.4 → M6.5
  任一失败: 立即退回 sub-agent 重做（按"先修哪条"标注）
  全部通过: stage_status = completed, 进入 V11 下一 stage
```

### 4.3 与 V11 §3.7 #7 反例的精确对位

| V11 §3.7 反例 | 本报告 §4 对位 | 关键差异 |
|---------------|---------------|----------|
| §3.7 #6 AI 描述当成真实像素 | M6.1 抽检 screenshot | M6.1 **强制主代理 Read**（V11 §3.7 #6 只声明） |
| §3.7 #7 盲信子代理"已完成" | M6.2-M6.5 抽检 | M6.2-M6.5 **强制 5 项抽检**（V11 §3.7 #7 只声明） |
| §3.7 #2 跳过测试声称完成 | M6.5 抽检 git diff | M6.5 **强制 verify 命令在 commit 中** |

---

## §5 sub-agent 委派头部 6 字段 + [TOOL-HINTS]

### 5.1 头部模板（V11 §0.5 + bug-hunt-tooling 对齐）

```yaml
[PROJECT-RULE-GATE]
  必读 skill: Skill(name="project-rule-skill")
  必读后输出 needed_rules 清单
  只 Read needed_rules,禁止 Read 未声明的 rules
  在响应中必含字段:
    rules_loaded: [...]
    rules_skipped: [...]

[TASK]
  一句话明确任务目标（如"修复 BUG-003 useArtStyles 401"）
  关联 file:line（如 "src/hooks/useArtStyles.ts:fetchArtStyles"）
  验收标准（如 "Stage 3.5 playwright verify 401 → 200"）

[TOOL-HINTS]
  - 已 commit: <hash>（如有前置 commit）
  - 已有 script: |
      scripts/bug-hunt/auth-fixture.{ts}          # 长期 e2e 适用
      scripts/bug-hunt/new-bug.sh <id> <route>   # bug 单生成
      scripts/bug-hunt/dev-hmr-recovery.ps1      # HMR stale 恢复
      scripts/bug-hunt/archive-screenshot.ps1    # 截图归档
  - 已落 bug 单: docs/bugs/<date>/<BUG-NNN>.md
  - 必回写 status: bug 单 + index.md + .state-card.md 三文件同步

[OUTPUT]
  status: PASS / FAIL
  evidence: file:line + 截图/visible_text/console_logs 摘要
  pass_count: N/M 任务达验收标准
  next_hook: 阻塞 / 待观察 / 完成

[FORBIDDEN]
  - 跳过 §2 真登录 7 步走 auth-fixture 替代（长期 e2e）或手写真登录（临时取证）
  - 跳过 bug 单 status 回写（即使修复成功也需 FAIL — V11 §3.7 #7）
  - 跳过 Playwright visible_text 验证（V11 §3.7 #6 AI 描述≠像素）
  - 跨目录写 docs/（docs 是独立 git 仓库；如项目是单仓则不受此限）

[EVIDENCE-EXPECTED]
  - 修复前 bug 单 6 字段 status = OPEN 截图
  - 修复后 visible_text screenshot（归档到 docs/evidence/<date>/bug-hunt/）
  - control plane console log（0 error / 401/404 → 200）
  - sed -i status 回写三文件 diff
```

### 5.2 头部 6 字段与 V11 §0.5 委派头部的关系

| V11 §0.5 §7 头部 | 本报告 bug-hunt 头部 | 关系 |
|------------------|---------------------|------|
| [MUST-READ] | （隐含在 PROJECT-RULE-GATE） | 本报告用项目级网关更严 |
| [PIPELINE] stage: {N} | （未注入，bug-hunt 跨 stage） | 本报告不强制 stage 编号 |
| [DOC_WHITELIST] | （未注入，bug-hunt 全局读） | 本报告允许 read docs/bugs/* |
| [FORBIDDEN] | [FORBIDDEN]（5 项扩充） | 本报告扩展为 5 项 bug-hunt 专属 |
| [GITNEXUS] impact() | （隐含在 [TASK] file:line） | 本报告不强求 impact() |
| [TASK] | [TASK] + [TOOL-HINTS] + [EVIDENCE-EXPECTED] | 本报告加 [TOOL-HINTS] 注入 |
| [OUTPUT] | [OUTPUT] | 一致 |

### 5.3 Completion Report 必含字段（sub-agent → 主代理）

```yaml
rules_loaded:
  - governance.md (reason: 改 API)
  - code-style.md (reason: 改 src)
  - anti-patterns.md (reason: 修复 bug, 必防假连通)
  - bug-hunt-tooling/SKILL.md (reason: e2e / bug-hunt 场景)
rules_skipped:
  - asset-hygiene.md
  - git.md
  - stack.md
  - paths.md
  - kill-rules.md
  - git-commit-message.md
  - docs-analysis.md
  - style.md

status: PASS
evidence: |
  - src/hooks/useArtStyles.ts:42 新增 Authorization header
  - playwright visible_text screenshot: docs/evidence/2026-08-15/bug-hunt/BUG-003-fixed.png
  - console log: [useArtStyles] Loaded 12 art styles (无 401)
  - sed -i status: BUG-003 OPEN → FIXED（三文件同步）
pass_count: 4/4 验收标准全过
next_hook: 主代理 §4 抽检 5 项
```

---

## §6 bug 单状态机守恒 + 三文件同步（V11 §8 + state-card-protocol）

### 6.1 bug 单 6 字段（V11 §8）

| 字段 | 必填 | 自动化 |
|------|------|--------|
| bug_id | ✅ | `new-bug.sh BUG-NNN` 校验 |
| module | ✅ | `new-bug.sh M4-asset` |
| observed_at | ✅ | `new-bug.sh` 用 `TZ=Asia/Shanghai` 写入 |
| route | ✅ | `new-bug.sh /zh/workspace/asset-hub` |
| evidence | ✅ | 主代理补 Description + Fix |
| severity | ✅ | L1 阻断 / L2 局部不可用 / L3 视觉走样 / L4 体验瑕疵 |
| status | ✅ | OPEN → IN-FIX → FIXED → VERIFIED → CLOSED |

### 6.2 状态机守恒（三文件同步）

> **铁律**：每次状态转换必须**同步** bug 单 `.md` + `index.md` + `.state-card.md` 三文件，缺一即**状态机不一致** → 🛑 REJECT。

```bash
# 修复 BUG-NNN 后必跑（V11 §3.7 #7 反例）
sed -i 's|^| status | OPEN$|| status | FIXED (YYYY-MM-DDTHH:MM:SS by <agent-id>) |' \
  docs/bugs/<change-id>/BUG-NNN.md

# index.md 同步
sed -i 's|^| BUG-NNN | OPEN | | BUG-NNN | FIXED (YYYY-MM-DDTHH:MM:SS) |' \
  docs/bugs/index.md

# .state-card.md 同步
sed -i 's|^BUG-NNN: OPEN$|BUG-NNN: FIXED|' \
  docs/bugs/.state-card.md

# 反向校验（必须 0 命中）
grep -l "^| status | OPEN" docs/bugs/<change>/BUG-003*.md
grep -lE "^\s*-\s*\[ \]" docs/bugs/index.md | xargs grep -L "FIXED"
```

### 6.3 状态机守恒与 V11 §8 / state-card-protocol.md 的关系

| V11 现有 | 本报告新增 |
|----------|----------|
| V11 §8 bug 单 6 字段 | 必填列表 |
| state-card-protocol.md 状态机（OPEN/IN-FIX/FIXED/VERIFIED/CLOSED） | 三文件同步守恒（bug 单 + index.md + state-card.md） |
| V11 §3.7 #7 盲信子代理"已完成" | 强制 status 回写命令 |

---

## §7 工具脚本清单（4 工具 + fixture — 不重复造轮子）

> **本节是引用，不是落地实现**。所有工具脚本由 [bug-hunt-tooling skill](../../bug-hunt-tooling/SKILL.md) 提供。

### 7.1 4 工具脚本 + 1 fixture

| 脚本 / fixture | 用途 | 触发条件 | 反 V11 §3.7 反例 |
|---------------|------|---------|------------------|
| `scripts/bug-hunt/auth-fixture.ts` | signedInPage fixture（长期 e2e） | 任何受 supabase 保护路由 | §3.7 #6（fixture 复用） |
| `scripts/bug-hunt/new-bug.sh` | 6 字段 bug 单生成 | 主代理 Phase A 落单 | §3.7 #2（脚本化） |
| `scripts/bug-hunt/dev-hmr-recovery.ps1` | HMR stale 4 步恢复 | 3 次重 navigate 未恢复 | §3.7 #5（脚本化） |
| `scripts/bug-hunt/archive-screenshot.ps1` | 截图归档（替代 Copy-Item） | Playwright screenshot 后 | §3.7 #2（脚本化） |
| `scripts/bug-hunt/close-bug.sh` | bug 单 status 回写（sed 封装） | sub-agent 修复后必跑 | §3.7 #7（status 回写） |

### 7.2 工具脚本 vs V11 §3.7 #2 假通过

**反例**：用 `echo "skipping lint"` 占位脚本假装存在（V11 §3.7 #2）。
**正例**：
```bash
# ✅ 真跑 close-bug.sh
bash scripts/bug-hunt/close-bug.sh BUG-003 <agent-id>
# 输出 [OK] BUG-003 status → FIXED (<timestamp>)
```

---

## §8 6 反例库（蒸馏自 90 min / 14 模块 / 16 bug 全流程）

> **每条反例含**：触发条件 / 错误代价 / 正例 / 失败案例 file:line / 根因 / 教训

### §反例 1 — 跳过 fixture 手写真登录

| 字段 | 内容 |
|------|------|
| **触发** | 主代理一上来就 `playwright_navigate` + `playwright_screenshot`，跳过 signin 凭据注入 |
| **代价** | 截图内容是 signin 表单（middleware 把页面重定向到 `/zh/auth/signin`）→ 主代理把 signin 表单截图当成"目标页面"判 PASS → **假证据 PASS** |
| **正例** | 走 §2 真登录 7 步（含 M2.6 必 visible_text 验证） |
| **失败案例** | 2026-08-15 主代理未登录态截 `/zh/home` → middleware 重定向 → 截图全是登录表单但代理未 Read 直接标 PASS |
| **根因** | middleware 在 supabase session 缺失时静默重定向到 signin，**没有 error overlay** 提示；主代理把"navigate 200 OK = 到达目标页"误判成功 |
| **教训** | **下次必走 §2 7 步** 或 import `signedInPage` fixture；不要凭"navigate 没报错"判 PASS；截图后必须 Read |

### §反例 2 — 14 模块串行未委派

| 字段 | 内容 |
|------|------|
| **触发** | bug hunt spec 列出 ≥ 7 个模块（14 模块属重度场景），主代理按顺序 navigate 串行 |
| **代价** | **14 × 平均 3 min = 42 min 串行**；3 sub-agent 并行：14 ÷ 3 ≈ 5 模块/agent × 3 min = 15 min（**节约 27 min**） |
| **正例** | V11 §1.6 反 AI 自律：≤6 Task + LOW 风险 → 主代理亲自；>6 Task 或 ≥MEDIUM → 必委派 sub-agent 并行。14 模块拆 3 sub-agent × ~5 模块 |
| **失败案例** | 2026-08-15 14 模块全程主代理亲自 navigate，全流程 90 min 中 42 min 浪费在串行 |
| **根因** | 主代理接到 bug hunt 任务时倾向"先自己跑一两个试试"，没在 spec 阶段就识别"14 模块 = 必委派" |
| **教训** | **模块数判定**：spec 列模块数 ≤ 6 → 主代理；> 6 → 必拆 sub-agent 并行（V11 §1.6 强制） |

### §反例 3 — bug 单手填 6 字段

| 字段 | 内容 |
|------|------|
| **触发** | 主代理或子代理手写 `docs/bugs/.../BUG-017.md` 含 bug_id / module / observed_at / route / severity / status 全 6 字段 |
| **代价** | 16 个 bug 单每个 1 min 手填 = 16 min 浪费 |
| **正例** | `bash scripts/bug-hunt/new-bug.sh BUG-017 M4-asset /zh/workspace/asset-hub L2 "evidence"` → 主代理补 Description + Fix |
| **失败案例** | 2026-08-15 16 个 bug 单 6 字段全部手填（无 new-bug.sh） |
| **根因** | V11 §8 6 字段模板未脚本化；缺 `new-bug.sh` 占位符注入 |
| **教训** | **bug 单生成必走 new-bug.sh**；禁止手写 6 字段模板 |

### §反例 4 — 修复后 bug 单 status 未回写

| 字段 | 内容 |
|------|------|
| **触发** | sub-agent 修完 BUG-003 后，bug 单 `.md` 文件 `status: OPEN` 字段未改；主代理只在 `index.md` 标 FIXED |
| **代价** | bug 单本体（BUG-NNN.md）`status: OPEN` 与 `index.md` `status: FIXED` **不一致**；主代理二次扫 bug 列表时按 BUG-NNN.md 判定 → 误判 OPEN → 重复委派修复 |
| **正例** | sub-agent 报告末尾必含 `sed -i 's/^status: OPEN$/status: FIXED/' docs/bugs/.../BUG-NNN.md`（详见 §6.2） |
| **失败案例** | 2026-08-15 BUG-003/004/015 修复后 bug 单 `.md` 文件 status 仍是 OPEN；只有 index.md（主代理手动改）写 FIXED |
| **根因** | 修复委派 TOOL-HINTS 缺 `sed -i` 步骤；状态分散两文件无强制一致 |
| **教训** | **sub-agent report 模板必含** "回写 status" 字段 + 必跑 `close-bug.sh <bug-id> <agent-id>`；主代理收到 report 后**必验** bug 单 status 已更新 |

### §反例 5 — HMR 反复重 navigate（未跑 dev-hmr-recovery）

| 字段 | 内容 |
|------|------|
| **触发** | `playwright_navigate` 后 `playwright_get_visible_text` 仍为空 + dev server 日志含 `Module not found` / `ChunkLoadError` → 主代理反复 `playwright_navigate` 同路由 ≥ 3 次 |
| **代价** | 5+ 次重 navigate + 5+ 次空文本 visible_text + 1 次截图 + 1 次 Read ≈ **5 min 浪费** |
| **正例** | 连续 3 次重 navigate 未恢复 → `pwsh scripts/bug-hunt/dev-hmr-recovery.ps1`（4 步打包） |
| **失败案例** | 2026-08-15 BUG-001 HMR stale 反复 navigate 浪费 5+ 次 tool 调用 |
| **根因** | Next.js 15.5+ Turbopack + Windows 高频 navigate 偶发 stale（[next.js#86363](https://github.com/vercel/next.js/discussions/86363) 已知） |
| **教训** | **failure budget = 3**：同路由连续 3 次 `navigate + visible_text` 空文本 → 必跑 `dev-hmr-recovery.ps1`，不再重试 |

### §反例 6 — 主代理证据未独立抽检（盲信 sub-agent）

| 字段 | 内容 |
|------|------|
| **触发** | 主代理收到 sub-agent "PASS" 后直接标 stage 完成；未 Read 截图 / 未跑 visible_text / 未 grep status |
| **代价** | sub-agent 截图含 signin 重定向 + console 401 仍存在 → 主代理标 PASS → 下游 stage 阻塞 |
| **正例** | 走 §4 5 项抽检（M6.1 Read 截图 + M6.2 visible_text + M6.3 console + M6.4 三文件状态 + M6.5 git diff） |
| **失败案例** | 2026-08-15 wave_1 子代理报 BUG-018 FIXED（visible_text="第 1 集 工作流 资产 已保存 70%"），但主代理独立验 visible_text 仍"加载无限画布..."（回滚 OPEN，浪费 ~30 min） |
| **根因** | V11 §3.7 #7 盲信子代理"已完成"；缺 5 项独立抽检清单 |
| **教训** | **5 项抽检必走**；sub-agent PASS ≠ 主代理 PASS；抽检成本 < 1 min / 次，但可避免 1+ 小时假证据返工 |

---

## §9 V11.5 5 个 V11 缺漏吸收（项目级补救 + 贾维斯 PR 建议）

> **来源**：2026-08-15 V11.5 跨项目适配蒸馏报告（用户工作区）。这些是 V11 通用层（`~/.trae-cn/skills/fullstack4TraeV11/scripts/*.py`）的已知缺陷，**项目级不能改**（贾维斯 hash 锁保护）。本报告吸收到 V11 references 层，提供**项目级补救命令 + 贾维斯委派 PR 建议**。

### §9.1 V11 缺漏 1 — `run-all-guards.py` 不替换 `{change_id}` 占位符

| 字段 | 内容 |
|------|------|
| **位置** | `~/.trae-cn/skills/fullstack4TraeV11/scripts/run-all-guards.py`（V11 通用层，贾维斯 hash 锁保护） |
| **现象** | `gates.yaml` 中 `required_artifacts: ["docs/specs/changes/{change_id}/spec.md"]` 是 V11 默认写法，但 `run-all-guards.py` 没替换 `{change_id}` → 即使 spec.md 存在，仍报 9/13 FAIL |
| **项目级补救** | ```bash mkdir -p .trae/registry cp ~/.trae-cn/skills/fullstack4TraeV11/registry/*.yaml .trae/registry/ # 编辑 .trae/registry/gates.yaml 把 {change_id} 改为实际路径 python ~/.trae-cn/skills/fullstack4TraeV11/scripts/run-all-guards.py --project-root . --registry-dir .trae/registry ``` |
| **贾维斯 PR 建议** | `run-all-guards.py` 读 `state-card.md` 的 `current_change` 字段自动替换 `{change_id}` |
| **V11 bug-hunt 场景应用** | bug-hunt 跨 stage 时，state-card.md 的 `current_change` 可能未更新 → 必须手动改 `gates.yaml` 避免误报 |

### §9.2 V11 缺漏 2 — `hooks-fidelity.py` frontmatter 解析算法脆弱

| 字段 | 内容 |
|------|------|
| **位置** | `~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py` 第 213 行 `content.index("\n---", 3)` |
| **现象** | 状态卡 frontmatter 内部 `output: \|` 缩进块可能含 `---` 字符；或 state-card 末尾缺闭合 `---` → 脚本崩溃而不是报"invalid_yaml"或优雅降级 |
| **项目级补救** | 状态卡 frontmatter 闭合必校验（`grep -c "^---$" docs/bugs/.state-card.md` ≥ 2）；frontmatter 内不放 `#` 注释 + 不放可能含 `---` 字符的内容 |
| **贾维斯 PR 建议** | 用 `yaml.safe_load` + `try/except` 替代 `content.index` 暴力正则 |
| **V11 bug-hunt 场景应用** | bug-hunt 阶段频繁更新 `.state-card.md` → frontmatter 闭合校验必跑 |

### §9.3 V11 缺漏 3 — `proactive-scan.py` reason-fabrication 不看上下文

| 字段 | 内容 |
|------|------|
| **位置** | `~/.trae-cn/skills/fullstack4TraeV11/scripts/proactive-scan.py` scan_reason_fabrication 函数 |
| **现象** | 报告内"reason-fabrication 误报说明段"引用禁词本身 → 被误判为使用禁词 |
| **项目级补救** | 把禁词改为同义词；承认违反 V11 Article VIII 归档不可变 + 在 commit message + 项目级 notes 标注 |
| **贾维斯 PR 建议** | `proactive-scan.py` 排除 `docs/archive/` `docs/bugs/` `docs/reports/` 但**未排除** `docs/specs/_invalidated/`（spec-purge 历史区） |
| **V11 bug-hunt 场景应用** | bug-hunt 阶段产生大量 evidence 文件（含 `加载失败` / `报错` 关键词）→ 必排除 docs/evidence/ 避免误报 |

### §9.4 V11 缺漏 4 — 项目级 hook `gitnexus-session-check.py` 不写 last-run 文件

| 字段 | 内容 |
|------|------|
| **位置** | 项目侧 `.trae/hooks/gitnexus-session-check.py` 是 V11 早期版本，**不写** `.gitnexus/last-run.json` |
| **现象** | hooks-fidelity.py 第 9 节检查 `.gitnexus/last-run.json` + `last-run-check.json` 存在 → 但项目侧 hook 不写 → GitNexus 痕迹过期 FAIL |
| **项目级补救** | 手动写 `.gitnexus/last-run*.json`，字段 `at`（不是 `timestamp`）：```json {"event":"SessionStart","reason":"index_stale","action":"analyze","head":"<sha>","dirty":false,"at":"2026-08-15T18:00:00+08:00"} ``` |
| **贾维斯 PR 建议** | 项目级 hook 统一从 V11 默认 templates 重新安装，或在项目级 hooks 安装脚本（`init-from-zero.py`）必走 `--hooks-from-v11-templates` 参数 |
| **V11 bug-hunt 场景应用** | bug-hunt 阶段会话开始 / 结束必须跑 GitNexus hook → last-run 文件必写 |

### §9.5 V11 缺漏 5 — `run-all-guards.py` 不带 `--registry-dir` 时不读项目级覆盖

| 字段 | 内容 |
|------|------|
| **位置** | V11 默认 `run-all-guards.py --project-root .` 读 V11 通用 `registry/`，不看项目 `.trae/registry/` |
| **现象** | 项目级覆盖必**每次**手动带 `--registry-dir .trae/registry` |
| **项目级补救** | 在 `.trae/hooks.json` `UserPromptSubmit` 注册时**写死** `--registry-dir .trae/registry` 参数 |
| **贾维斯 PR 建议** | `run-all-guards.py` 默认探测 `.trae/registry/` 项目级 registry，存在则优先用，否则回落 V11 通用 registry |
| **V11 bug-hunt 场景应用** | bug-hunt 阶段每次跑 4 守卫（hooks-fidelity / orphan-detector / proactive-scan / run-all-guards）→ 必带 `--registry-dir` |

---

## §10 一句话铁律 + 验证矩阵

### 10.1 一句话铁律

**bug-hunt / E2E 跨 stage 实战 = 复用脚本 + 4 维度观察 + 5 项抽检 + 6 反例避坑 + V11.5 5 缺漏项目级补救**。

### 10.2 验证矩阵（必跑）

| 编号 | 验证项 | 命令 | 期望 |
|:----:|--------|------|------|
| V1 | 真登录 fixture 复用（长期 e2e） | `grep -rE "playwright_(navigate\|fill).*signin" tests/e2e/` | 0 命中（仅 fixture 内允许） |
| V2 | bug 单脚本生成 | `head -20 BUG-*.md \| grep "generated by new-bug.sh"` | 100% 命中 |
| V3 | HMR 恢复脚本可用 | `pwsh scripts/bug-hunt/dev-hmr-recovery.ps1 -DryRun` | 5s 内打印 4 步命令 |
| V4 | 截图归档脚本可用 | `pwsh scripts/bug-hunt/archive-screenshot.ps1 -DryRun` | 5s 内打印归档命令 |
| V5 | bug 单 status 回写 | `grep -l "^status: OPEN" docs/bugs/.../BUG-NNN*.md` | 0 命中（修复完） |
| V6 | 三文件状态同步 | `grep -lE "^\s*-\s*\[" docs/bugs/index.md \| xargs grep -L "FIXED"` | 0 命中 |
| V7 | V11 5 缺漏项目级补救（任选 1） | `python ~/.trae-cn/skills/fullstack4TraeV11/scripts/run-all-guards.py --project-root . --registry-dir .trae/registry` | exit 0 |

### 10.3 与 V11 gate 矩阵的对接

| V11 gate 层级 | 本报告验证项 | 协同关系 |
|---------------|--------------|----------|
| Stage 6 Bug Fix 完成 | V5 + V6 | bug 单状态机守恒是 Stage 6 完成证据 |
| Stage 3.5 Real Verify 完成 | V1 + V3 + V4 | 真登录 + HMR + 截图归档是 Real Verify 产物 |
| Stage 4 Review PASS | V7（V11.6.0 ac-gate.py G1-G5） | AC 核销门禁 + 5 项抽检是 Review 通过依据 |

---

## 关联引用

### V11.8.2 Stage 6 同包 references（直接引用）
- [bug-hunt-phase-a.md](bug-hunt-phase-a.md) — Phase A 3 步流程骨架（启动 / 14 模块 / 落单）
- [bug-hunt-4d-observation.md](bug-hunt-4d-observation.md) — 4 维度观察法（visual/behavior/data/console）
- [bug-hunt-5-check.md](bug-hunt-5-check.md) — 5 项证据独立抽检（M6.1-M6.5）
- [five-step-flow.md](five-step-flow.md) — Phase B 5 步精简流程（理解期望 / e2e 先行 / 数据分析 / TDD / 验收）
- [six-layer-diagnosis.md](six-layer-diagnosis.md) — Phase B 6 层排查
- [bug-state-machine.md](bug-state-machine.md) — OPEN/IN-FIX/FIXED/VERIFIED/CLOSED
- [../SKILL.md](../SKILL.md) — Stage 6 总入口（13 铁律 + 7 步统一工序）
- [../scripts/bug-hunt/](../scripts/bug-hunt/) — 6 工具脚本（new-bug.sh / close-bug.sh / dev-hmr-recovery.{sh,ps1} / archive-screenshot.{sh,ps1}）

### V11 公共 references（同包外）
- [../../../references/constitution.md](../../../references/constitution.md) — 17 Articles 宪法
- [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md) — 公共铁律（Article XVII Secret Redaction）
- [../../../references/common-anti-patterns.md](../../../references/common-anti-patterns.md) — 22 反例库
- [../../../references/sub-agent-rules.md](../../../references/sub-agent-rules.md) — 子代理通用铁律
- [../../../references/state-card-protocol.md](../../../references/state-card-protocol.md) — 状态卡协议
- [../../../references/agent-error-diagnosis.md](../../../references/agent-error-diagnosis.md) — 5 模式失败根因

### V11.5 缺漏 PR 来源（跨工作区）
- 用户工作区 `D:\workspace\ai-collaborate\ai-short-studio-monster\docs\specs\sessions\2026-08-15-v11.5-fullstack-upgrade-distillation-report.md` §4

---

## 变更日志

| 日期 | 版本 | 变更 | 来源 |
|------|------|------|------|
| 2026-08-15 | 1.0.0 | 首版（10 段齐全 + 6 反例 + V11.5 5 缺漏吸收） | 2026-08-15 V11.5 跨项目适配蒸馏 + bug-hunt 90 min 实战 |
| 2026-08-15 | 1.1.0 | V11.8.2：报告迁入 Stage 6 子段（`references/stage-08-real-verify-battle-report.md` → `skills/12-bug-fix/references/bug-hunt-battle-report.md`）；删 §0.3 「与 bug-hunt-tooling 关系」段（V11.8.2 不外挂 skill）；关联引用全改同包路径；frontmatter description + version 升级 | V11.8.2 Stage 6 升级 |