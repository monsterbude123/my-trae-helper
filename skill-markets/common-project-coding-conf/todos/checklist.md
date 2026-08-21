# common-project-coding-conf — Checklist（门禁复核清单）

> **触发**: skill 功能开发完 + 所有 agent 复核之后再删除本文件（按 .trae/rules/skills开发细则.md 铁律）

## §1 功能复核（开发完成度）

- [ ] SKILL.md 含 `name` + `description` + 路由表 + 自检协议 + forge 协议 + 委派头部
- [ ] cpcc-self-check.mjs 6 项检查全实现 + 输出格式符合 §0.5
- [ ] forge_project_rules_skill.py 从 project-rules-gate 迁移 + 改 4 处引用
- [ ] SKILL.md.template 迁移
- [ ] workflows/sub-agent-delegate-load.md 迁移
- [ ] references/forge-protocol.md + agent-delegate-protocol.md 迁移

## §2 description 复核（trigger 词）

- [ ] common-project-coding-conf/SKILL.md 含触发词
- [ ] coding-xinfa/SKILL.md 含触发词（已补）
- [ ] fullstack4TraeV11/SKILL.md 含触发词（已补）

## §3 安全审查

- [ ] 跑 `python skill-markets/trae-security-review/scripts/scan_skills_dir.py skill-markets/common-project-coding-conf` 期望 PASS
- [ ] 更新 `SECURITY-MAP.md` 增加 common-project-coding-conf 条目

## §4 注册表

- [ ] guard-smith sub-agent 已委派更新 `registry/skills.yaml` + 生成 `scripts/cpcc-guard.py` + `.husky/cpcc-gate`

## §5 删除与归档

- [ ] 删除 `skill-markets/project-rules-gate/` 目录（迁移完成后）
- [ ] git status 无未跟踪敏感文件

## §6 蒸馏

- [ ] AGENTS.md 顶部加 2026-08-19 蒸馏记录

## §7 复核签名

- [ ] 主 agent 自查全部 ✅
- [ ] 用户最终确认