# 反例 5：跳过真登录取证 7 步（Stage 6 Bug Fix Phase A）

> **V11.8.2 NEW**（Phase A 批量发现专属）。
>
> Stage 6 Bug Fix & Hunt 铁律 #6：受 supabase auth 保护的路由必走真登录 7 步（含 visible_text 验证）。
>
> 详见 [../references/bug-hunt-phase-a.md](../references/bug-hunt-phase-a.md) §A.1 + [../references/bug-hunt-battle-report.md §8 反例 1](../references/bug-hunt-battle-report.md)。

## 现象

```
debugger / 主代理: 一上来就 playwright_navigate /zh/home + screenshot  # ❌ 跳过 signin 凭据
middleware 静默重定向到 /zh/auth/signin（无 error overlay）
screenshot 实际是登录表单（不是目标页）
debugger: "OK, 看着像 PASS" → 落单 → 浪费 1+ 小时假证据返工
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得 navigate 200 OK = 到达目标页 | 60% |
| 不知道 middleware 静默重定向无 error overlay | 30% |
| 信任 screenshot 不 Read 文本 | 10% |

## 失败案例（2026-08-15）

- **现象**：主代理未登录态截 `/zh/home` → middleware 重定向 → 截图全是登录表单但代理未 Read 直接标 PASS
- **位置**：[V11.8.2 实战报告 §8 反例 1](../references/bug-hunt-battle-report.md)
- **影响**：bug 单 evidence 段假证据 → 下游 stage 阻塞

## 教训

**必走 7 步**（铁律 #6）：

```yaml
1. 启动 dev server（dev-hmr-recovery.{sh,ps1}）
2. playwright_navigate /zh/auth/signin
3. playwright_fill email + password + click submit
4. 等 1-2s 让 supabase 写 session
5. playwright_navigate <target_route>
6. playwright_get_visible_text  # ★必含期望路由关键字
7. playwright_screenshot + archive-screenshot.{sh,ps1} -Slug <bug-id>-<state>
```

**判定**：
- ✅ 通过：visible_text 含期望关键字（如 /zh/home → "欢迎回来" + 邮箱）
- ❌ 假证据：visible_text 含 "邮箱"/"password" → 还在登录前态，回到第3 步
- ❌ 后端异常：visible_text 含 "error.tsx" 内容 → 查 dev server log

## 正确替代

- 临时取证走 7 步（详见 [bug-hunt-phase-a.md §A.1](../references/bug-hunt-phase-a.md)）
- 长期 e2e 走 fixture（`tests/e2e/fixtures/auth-fixture.ts` signedInPage）

## 关联引用

- [../references/bug-hunt-phase-a.md](../references/bug-hunt-phase-a.md) — Phase A 3 步流程骨架
- [../references/bug-hunt-battle-report.md §8 反例 1](../references/bug-hunt-battle-report.md) — V11.8.2 实战报告
- [../references/bug-hunt-4d-observation.md](../references/bug-hunt-4d-observation.md) — 4 维度观察法
- [../scripts/bug-hunt/dev-hmr-recovery.ps1](../scripts/bug-hunt/dev-hmr-recovery.ps1) — HMR 恢复脚本
- [../SKILL.md §铁律 6](../SKILL.md) — 真登录取证必走
- V11 SKILL.md §3.7 #6 — AI 描述 ≠ 真实像素