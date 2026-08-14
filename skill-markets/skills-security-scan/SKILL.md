---
name: skills-security-scan
status: deprecated
redirect_to: trae-security-review
description: [DEPRECATED → trae-security-review] 本地优先版 Skill 安全审查能力已整合。扫描功能由 trae-security-review/scripts/scan_skills_dir.py V2.1 提供（8 类风险 + 三层白名单）；平台兼容性识别已迁至 trae-security-review/scripts/lib/platform_detector.py。
triggers: [skill 安全审查, skill 安全扫描, skill 准入, skill 风险, skill 安全, 本地安全扫描, skills security]
intent: [DEPRECATED → trae-security-review] 本地优先版 Skill 安全审查能力已整合
category: cli
audience: [developer]
---
# ⚠️ DEPRECATED — 已并入 trae-security-review

> 本 skill 已整合至 [`trae-security-review`](../trae-security-review/SKILL.md)。
>
> 迁移说明（2026-08-14）：
>
> | 原能力 | 新位置 |
> |--------|--------|
> | 5 类风险扫描（CMD_RM_RF / DYN_EVAL / SHELL_EXEC / HARDCODED_SECRET / HTTP_INSECURE）| `trae-security-review/scripts/scan_skills_dir.py`（已升级为 **8 类风险 + 三层白名单 + 词边界**，更强） |
> | Skill 类型识别（trae-skill / claude-skill / json-skill / node-skill）| `trae-security-review/scripts/lib/platform_detector.py::classify_skill_type` |
> | 平台兼容性识别（19 类平台：Trae / Claude Code / Cursor / OpenClaw / Codex / Gemini CLI / Aider / Windsurf / Kilo Code / OpenCode / Augment / Antigravity / GitHub Copilot / Kimi / Cline / AMP / Warp / 通用）| `trae-security-review/scripts/lib/platform_detector.py::infer_platforms` |
> | CLI 入口 `python main.py <dir> [output_dir]`| 直接调用 `python trae-security-review/scripts/scan_skills_dir.py <dir> [output_dir]` |
> | Markdown 报告（中文，含 Skill 基本信息表）| `scan_skills_dir.py` 输出报告 + 调用 platform_detector 拼接基本信息段 |
>
> **CLI 兼容壳**：原 `skills-security-scan/main.py` 行为已等价于 `scan_skills_dir.py`。`skills-security-scan/scripts/main.py` 保留为 redirect 壳，转发到 trae-security-review。

## 历史文件保留

`skills-security-scan/references/` 下的文档保留供查阅：
- `docs/skills-security介绍.md` — 工具介绍（已被 trae-security-review SKILL.md 替代）
- `checklists/delivery-checklist.md` — 交付检查清单（仍可独立使用）
- `examples/batch-assess.md` / `examples/watch-new-skills.md` — 用法示例（迁移到 trae-security-review/examples/）

`install.ps1` / `install.sh` 已不再需要 — 直接走 trae-security-review。

`templates/assessment-request-template.md` 可继续使用，作为发起 Skill 审查的请求模板。