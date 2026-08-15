# 5 项证据独立抽检（V11.8.2 NEW — Phase A/B 验收共用）

> **Stage 6 铁律 #12**：主代理收到 sub-agent 报告后**必须**跑 5 项独立抽检，**不可盲信 sub-agent 产物**。
>
> **反例**：V11 §3.7 #7 盲信子代理"已完成" + 2026-08-15 wave_1 子代理报 BUG-018 FIXED 但 visible_text 实测仍 "加载无限画布..." → 浪费 30 min。

---

## §C.0 — 为什么主代理必抽检（铁律 #12）

```
MUST: 子代理返回 Completion Report 后，主上下文必须独立验证 5 项（M6.1 - M6.5）
NEVER: 子代理返回 "PASS" 就直接接受
任一层不匹配 = 🛑 REJECT + 计入失败 1 次
```

V11 §3.7 #7 + §3.7 #6 + Article IX 质疑式验收 = 主代理必跑 5 项。

---

## §C.1 — M6.1 抽检 screenshot 视觉内容

```yaml
工具: Read <screenshot_path>（file:// 链接）
验证:
  - 截图是否对齐 sub-agent 描述（DOM 文本 / 关键 widget 出现）
  - 是否有 Next.js red error overlay
  - 是否有 signin 表单泄露（未登录态假证据）
反例: 盲信 "截图已归档" → 未读图 → 假证据通过
触发 REJECT: 任何 mismatch
```

**典型反例**：2026-08-15 主代理未登录态截 `/zh/home` → middleware 重定向 → 截图全是登录表单但代理未 Read 直接标 PASS。

---

## §C.2 — M6.2 抽检 visible_text 关键句

```yaml
工具: mcp__playwright__playwright_get_visible_text
验证:
  - 重新 navigate 目标路由 + 取 visible_text
  - 与 bug 单 evidence 段 quoted 文本 diff
反例: 盲信 sub-agent visible_text → 实际环境已变
触发 REJECT: 任何缺失关键字
```

**典型反例**：sub-agent 报 BUG-018 FIXED（visible_text="第 1 集 工作流 资产 已保存 70%"）但主代理独立验 visible_text 仍"加载无限画布..."。

---

## §C.3 — M6.3 抽检 console error / 401

```yaml
工具: mcp__playwright__playwright_console_logs
验证:
  - 0 [error] level errors
  - 0 401 / 403 / 404 / 500
  - 0 hydration mismatch
反例: 盲信 "console 干净" → 实际 401 仍在（sub-agent 没注意）
触发 REJECT: 任何 [error] 或 4xx/5xx
```

**典型反例**：BUG-003 dev server console 报 `[useArtStyles] Failed to fetch art styles: 401` 但 sub-agent 报告无 401。

---

## §C.4 — M6.4 抽检 bug 单 + index.md + .state-card.md 三文件状态

```yaml
工具: Grep "BUG-NNN" docs/bugs/index.md + Grep "status" docs/bugs/<date>/<BUG-NNN>.md
验证:
  - bug 单 status 字段 == index.md status 列 == .state-card.md 行
  - 无 OPEN / FIXED 错位
反例: 盲信 sub-agent "已回写" → 实际只改 bug 单 → index.md 仍 OPEN
触发 REJECT: 任何文件不一致
```

**典型反例**：2026-08-15 BUG-003/004/015 修复后 bug 单 `.md` `status: OPEN` 未改；只有 index.md 标 FIXED → 主代理二次误判。

**自动同步命令**：

```bash
bash scripts/bug-hunt/close-bug.sh BUG-003 <agent-id>
# 三文件同步：bug 单 .md + index.md + .state-card.md

# 反向校验（必 0 命中）
grep -l "^| status | OPEN" docs/bugs/<change>/BUG-003*.md
grep -lE "^\s*-\s*\[" docs/bugs/index.md | xargs grep -L "FIXED"
```

---

## §C.5 — M6.5 抽检 git diff / commit message

```yaml
工具: git log --oneline -5 <branch> + git show <hash> --stat
验证:
  - 是否仅改必要 file（最小变更原则）
  - commit message 是否引用 bug_id（issue tracker 习惯）
  - 是否含 vitest pass / playwright verify 证据
反例: 盲信 "commit 已落" → 实际改了一堆无关文件
触发 REJECT: 任何不在 bug-fix 范围的文件
```

**典型反例**：sub-agent 修复 BUG-003 改了 8 个文件（含 2 个无关文件），commit message 无 bug_id 引用。

---

## §C.6 — 抽检流程

```yaml
sequence: M6.1 → M6.2 → M6.3 → M6.4 → M6.5

任一失败:
  - 立即退回 sub-agent 重做（按"先修哪条"标注）
  - 🛑 REJECT 报告
  - 计入 sub-agent 失败次数

全部通过:
  - stage_status = completed
  - 进入下一路由 / 下一 bug 单
  - close-bug.sh 三文件同步
```

---

## §C.7 — 与 V11 §3.7 反例的精确对位

| V11 §3.7 反例 | 本文件 §C 对位 | 关键差异 |
|---------------|---------------|----------|
| §3.7 #6 AI 描述当成真实像素 | M6.1 抽检 screenshot | M6.1 **强制主代理 Read**（V11 §3.7 #6 只声明） |
| §3.7 #7 盲信子代理"已完成" | M6.2-M6.5 抽检 | M6.2-M6.5 **强制 5 项抽检**（V11 §3.7 #7 只声明） |
| §3.7 #2 跳过测试声称完成 | M6.5 抽检 git diff | M6.5 **强制 verify 命令在 commit 中** |
| Article IX 自评=self_attested | 全部 5 项 | 主代理必二次抽检（不依赖 sub-agent 自评）|

---

## §C.8 — 抽检成本 vs 价值

- 抽检成本：< 1 min / 次（5 项 Read + grep）
- 价值：可避免 1+ 小时假证据修复返工（2026-08-15 wave_1 单次浪费 30 min）

**ROI 极高**——主代理不可跳过。

---

## 关联引用

- [bug-hunt-phase-a.md](bug-hunt-phase-a.md) — Phase A 整体 3 步
- [bug-hunt-4d-observation.md](bug-hunt-4d-observation.md) — 4 维度观察法
- [bug-hunt-battle-report.md](bug-hunt-battle-report.md) — V11.8.2 实战报告
- [../SKILL.md §铁律 12](../SKILL.md) — 5 项证据独立抽检铁律
- V11 §3.7 #6 + #7 — AI 描述≠像素 / 盲信子代理
- [V11 sub-agent-rules §8 三层验证](../../../references/sub-agent-rules.md)