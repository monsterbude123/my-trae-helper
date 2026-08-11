# Process 层文档位置指引（V10.11 NEW）

> 来源: 2026-08-08 会话蒸馏 03/06 — C3 歧义修复。
> 规则只说"禁读 process 层"，没说"放哪"。本文件补齐标准位置。

---

## 标准位置

| 文档类型 | 层级 | 推荐位置 | 子代理可读性 |
|---------|------|---------|-------------|
| **Bug 诊断结论** | fact | `docs/bugs/{bug-id}.md` | ✅ debugger/implementer 必读（任务输入） |
| **Bug 诊断草稿** | process | `docs/bugs/{bug-id}-draft.md` | ❌ 主上下文摘要注入 |
| **修复记录** | process | `.trae/tmp/{fix-id}.md` | ❌ 子代理禁读 |
| **调试手记** | process | `.trae/tmp/debug-{ts}.md` | ❌ 子代理禁读 |
| **腐化扫描报告** | fact | `docs/reports/rot-scan-{date}.json` | ✅ phase-gate 机械验证用 |
| **阻塞报告** | process | `.trae/tmp/blocker-{ts}.md` | ❌ 主上下文汇报给用户 |

---

## 禁止项

- ❌ 把 process 层文档放入 `docs/specs/changes/`（fact 层）
- ❌ 子代理读取 process 层作为验收依据（见 sub-agent-rules.md §1）
- ❌ process 层文档作为 spec 增量提交（不回流）

---

## 层级判定

| 文档 | 层级 | 可读性 | 用途 |
|------|------|--------|------|
| `docs/specs/changes/*/spec.md` | fact | ✅ task-execution-mode 必读 | 任务规格 |
| `docs/specs/changes/*/contracts/*.md` | fact | ✅ task-execution-mode 必读 | 契约定义 |
| `docs/bugs/{bug-id}.md` | fact | ✅ debugger/implementer 必读 | Bug 诊断结论（任务输入） |
| `docs/bugs/{bug-id}-draft.md` | process | ❌ 主上下文摘要注入 | 诊断过程草稿 |
| `.trae/tmp/*.md` | process | ❌ 子代理禁读 | 临时文档 |
| `docs/reports/*.md` | log | ⚠️ 可读但不作验收依据 | 历史报告 |

---

## 与归档路径防护的关系

本文件是"process 层位置指引"，与 `归档路径防护.md`（archive/ 禁读）互为补充：

| 规则 | 管辖范围 | 目的 |
|------|---------|------|
| 归档路径防护 | `docs/archive/` | 防止误读历史快照 |
| Process 层位置指引 | process 层文档 | 标准化位置 + 禁止子代理读取 |

---

## 关联引用

- 子代理禁读规则 → [sub-agent-rules.md](sub-agent-rules.md) §1
- 委派注入头部 → [SKILL.md](../SKILL.md) §1.5
- Article XIV rot-detector 必跑 → [constitution-detail.md](constitution-detail.md)