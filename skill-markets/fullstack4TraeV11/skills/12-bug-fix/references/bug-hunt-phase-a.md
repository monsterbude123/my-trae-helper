# Phase A 批量 bug 发现流程（V11.8.2 NEW）

> **Stage 6 Phase A 专属 references**。覆盖 7 步统一工序的 Step 1-3。
>
> **第一性原则**：受 auth 路由必走真登录 7 步（防 signin 重定向假证据）→ 14 模块按 4 维度扫 → 一键批量落 bug 单。

---

## §A.1 — 启动 dev + 真登录 7 步（Step 1）

> **铁律 #6**：受 supabase auth 保护的路由（`/zh/home`、`/zh/workspace/*`、`/zh/admin/*`、`/zh/auth/*` 等），必须先走完 7 步取得**已登录态**真实证据，再截屏 + 落单。
>
> **反例**：2026-08-15 主代理未登录态截 `/zh/home` → middleware 重定向 → 截图全是登录表单但代理未 Read 直接标 PASS。

```yaml
A.1.1 — 启动 dev server:
  目的: 确保 next-server + worker + watchdog + board 全部就绪
  执行: |
    # 触发 HMR stale 时必跑（详见 §A.4）
    pwsh scripts/bug-hunt/dev-hmr-recovery.ps1      # Windows
    bash scripts/bug-hunt/dev-hmr-recovery.sh       # bash
  验证: dev log 输出 "✓ Ready in Xs"（X 可接受 5-30s）
  反例: 未等 Ready 就 navigate → 拿到 SSR loading 中间态 → 误判 stale

A.1.2 — Playwright 打开 signin 路由:
  目的: 在受保护路由 navigate 之前，必须先打开 signin 灌 session
  执行: <!-- scan-whitelist:HTTP_INSECURE -->mcp__playwright__playwright_navigate http://localhost:3000/zh/auth/signin<!-- /scan-whitelist -->
  验证: playwright_get_visible_text 出现 "邮箱" / "password" / "登录" 任一关键字
  反例: 直接 navigate /zh/home → middleware 重定向 → navigate 失效 → 误以为页面空白

A.1.3 — 灌入凭据 + 提交:
  目的: 让 supabase 写入 session cookie + 完成 auth.users 查询
  执行: |
    mcp__playwright__playwright_fill("input[name='email']", "<email>")
    mcp__playwright__playwright_fill("input[name='password']", "<password>")
    mcp__playwright__playwright_click("button[type='submit']")
  验证: 等 1-2s 让 supabase server 写 session
  反例: 提交后 0s 立即 navigate → session 未写入 → 仍受 middleware 重定向

A.1.4 — 等 supabase 写入 session + redirect:
  目的: 让 client useEffect 触发页面跳转 / 状态同步
  执行: 等 1-2s 或直接 navigate 目标路由让 client 跳
  验证: URL 已 redirect 出 /zh/auth/signin
  反例: 未等就 navigate → 拿到 signin 页内容 → 误判

A.1.5 — Navigate 目标路由:
  目的: 进入真正要观察的受保护路由
  执行: mcp__playwright__playwright_navigate <target_route>
  验证: URL 保持目标路由（未被重定向回 signin）
  反例: 未登录 session 就 navigate → 永远被弹回 signin

A.1.6 — 截图前必 verify visible_text:
  目的: ⭐ 防止"截图里是 signin 表单但主代理没读图直接标 PASS"假证据
  执行: mcp__playwright__playwright_get_visible_text
  判定:
    ✅ 通过 — 出现 1 个 + 期望路由关键字
            例: /zh/home → "欢迎回来" + "2910226625@qq.com"
            例: /zh/workspace → "进行中" + 剧集列表
            例: /zh/admin/cinema-knowledge/vocabulary → "规范词汇" + 表格
    ❌ 假证据 — 可见文本是 signin 表单内容（"邮箱"/"password"）
               → 还在登录前态，必须回到 A.1.3
    ❌ 后端异常 — 可见文本是 error.tsx 内容（"返回工作区"/"500"/"刷新重试"）
               → 后端报错，必须查 dev server log 找根因
  反例: 仅截图不读图 → 误导主代理标 PASS（V11 §3.7 #6 AI 描述≠像素）

A.1.7 — screenshot + 归档:
  目的: 落 evidence 到版本控制
  执行: |
    mcp__playwright__playwright_screenshot   # 写到 $USERPROFILE/Downloads
    pwsh scripts/bug-hunt/archive-screenshot.ps1 -Slug "<bug-id>-<state>" -SubDir "bug-hunt"  # Windows
    bash scripts/bug-hunt/archive-screenshot.sh -Slug "<bug-id>-<state>" -SubDir "bug-hunt"   # bash
  验证: ls docs/evidence/<date>/bug-hunt/<slug>.png 存在
  反例: 信任 screenshot filename 参数 → 实际写到 Downloads → 截图散落
```

### 真登录 7 步 vs V11 fixture

| 场景 | 真登录 7 步手写 | fixture（auth-fixture.ts signedInPage）|
|------|----------------|----------------------------------------|
| 主代理 / sub-agent 临时观察 | ✅ 适用（一次性） | ❌ 不适用（要重启 dev server） |
| 长期 e2e 测试 | ❌ 浪费（每次重跑） | ✅ 推荐（一次 setup + storageState 复用） |
| **bug-hunt 临时取证** | **✅ 适用** | **❌ 不适用** |

**MUST**：bug-hunt 场景**走 7 步手写**（临时取证）；长期 e2e 测试**走 fixture**（开发测试）。两者不混用。

---

## §A.2 — 14 模块 × 4 维度观察（Step 2）

> **铁律 #7**：每个路由观察必须覆盖 4 个维度，**单维度不可证伪**。
> **铁律 #8**：模块数 ≤ 6 主代理亲自；> 6 必拆 sub-agent 并行（V11 §1.6）。
>
> **反例**：2026-08-15 14 模块全程主代理亲自 navigate，27 min 浪费。

### 4 维度观察清单

| 维度 | 工具 | 检查点 | 失败对应 |
|------|------|--------|----------|
| **视觉** | playwright_screenshot + get_visible_text | 截图含期望关键字/图标/配色；字体未降级；布局未塌缩；主题色应用到 | L3 视觉走样 |
| **行为** | playwright_click + hover + press_key | 关键 CTA 点击触发期望动作；hover 显示 tooltip；表单提交成功；路由跳转带 query | L2 局部不可用 |
| **数据** | playwright_get_visible_text + i18n key 检查 | mock 列表非空；i18n key 翻译；数据字段完整；dropdown 选项对齐后端 | L2/L3 |
| **控制台** | playwright_console_logs | 0 [error] / 0 401/403/404/500 / 0 hydration mismatch / 0 Unhandled Rejection | L2（API 401 类）|

**详见 [bug-hunt-4d-observation.md](bug-hunt-4d-observation.md)**。

### 委派策略（V11 §1.6）

```yaml
≤ 6 模块: 主代理亲自跑（4 维度 × N 模块串行）
> 6 模块: 必拆 sub-agent 并行
         14 模块拆 3 sub-agent:
           sub_agent_1: [M1 home, M2 art-style, M3 character, M4 asset, M5 script]
           sub_agent_2: [M6 storyboard, M7 shot, M8 video, M9 voice, M10 music]
           sub_agent_3: [M11 export, M12 publish, M13 analytics, M14 admin]
```

每个 sub-agent 必含 `[TOOL-HINTS]` 头部（详见实战报告 §5）。

---

## §A.3 — 批量落 bug 单（Step 3）

> **铁律 #9**：bug 单生成必走 `scripts/bug-hunt/new-bug.sh`，**禁止手写 6 字段模板**。
>
> **反例**：2026-08-15 16 个 bug 单 6 字段全部手填（无 new-bug.sh），浪费 16 min。

### 用法

```bash
# 6 字段机器生成（bug_id / module / observed_at / route / severity / status）
# 主代理补 Description + Fix 段
bash scripts/bug-hunt/new-bug.sh BUG-017 M4-asset /zh/workspace/asset-hub L2 "playwright 404"
```

### 6 字段（V11 §8）

| 字段 | 必填 | 自动化 |
|------|------|--------|
| bug_id | ✅ | `new-bug.sh BUG-NNN` 校验 |
| module | ✅ | `new-bug.sh M4-asset` |
| observed_at | ✅ | `new-bug.sh` 用 `TZ=Asia/Shanghai` 写入 |
| route | ✅ | `new-bug.sh /zh/workspace/asset-hub` |
| evidence | ✅ | 主代理补 Description + Fix |
| severity | ✅ | L1 阻断 / L2 局部不可用 / L3 视觉走样 / L4 体验瑕疵 |
| status | ✅ | OPEN → IN-FIX → FIXED → VERIFIED → CLOSED |

### 归档截图

每次截图后**立刻**归档（不滞留 Downloads）：

```bash
pwsh scripts/bug-hunt/archive-screenshot.ps1 -Slug "BUG-017-fixed" -SubDir "bug-hunt"
bash scripts/bug-hunt/archive-screenshot.sh -Slug "BUG-017-fixed" -SubDir "bug-hunt"
```

---

## §A.4 — HMR stale 触发 + 恢复（铁律 #10）

> **铁律**：连续 3 次重 navigate 未恢复即跑 `dev-hmr-recovery.{sh,ps1}`。
>
> **反例**：2026-08-15 BUG-001 HMR stale 反复 navigate 浪费 5+ 次 tool 调用。

### 触发条件（满足任一即跑）

1. playwright_navigate 后 visible_text 异常为空
2. dev server log 含 "Module not found" / "ChunkLoadError" / "Failed to fetch"
3. 连续 3 次重 navigate 仍未恢复
4. 任意路由出现 Next.js red error overlay

### 4 步恢复脚本（已脚本化）

```bash
# Windows
pwsh scripts/bug-hunt/dev-hmr-recovery.ps1
pwsh scripts/bug-hunt/dev-hmr-recovery.ps1 -DryRun  # 先打印 4 步命令

# bash
bash scripts/bug-hunt/dev-hmr-recovery.sh
bash scripts/bug-hunt/dev-hmr-recovery.sh -DryRun
```

**禁止**：

- ❌ 反复重 navigate（≥ 3 次未恢复即跑 M4）
- ❌ 仅删 .next/ 不 kill 进程（lock 文件残留）
- ❌ 不重启 dev server 只改 next.config（必须重启）

---

## §A.5 — 自验收 5 项命令（Phase A 完成前必跑）

```bash
# 铁律 6：真登录 fixture 复用（应 0 命中）
grep -rE "playwright_(navigate|fill).*signin" tests/e2e/

# 铁律 9：bug 单脚本生成（应 100% 命中）
head -20 BUG-*.md | grep "generated by new-bug.sh"

# 铁律 10：HMR 恢复脚本可用（应 5s 内打印）
pwsh scripts/bug-hunt/dev-hmr-recovery.ps1 -DryRun

# 铁律 11：截图归档脚本可用
pwsh scripts/bug-hunt/archive-screenshot.ps1 -DryRun

# 三文件状态一致（应 0 命中）
grep -l "^status: OPEN" docs/bugs/<change>/BUG-*.md  # OPEN 残留
```

---

## 关联引用

- [bug-hunt-4d-observation.md](bug-hunt-4d-observation.md) — 4 维度观察法
- [bug-hunt-5-check.md](bug-hunt-5-check.md) — 5 项证据独立抽检
- [bug-hunt-battle-report.md](bug-hunt-battle-report.md) — V11.8.2 实战报告
- [../SKILL.md §铁律 6-12](../SKILL.md) — Phase A 专属铁律
- [bug-state-machine.md](bug-state-machine.md) — OPEN/IN-FIX/FIXED/VERIFIED/CLOSED