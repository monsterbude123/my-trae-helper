---
description: skills 开发细则需要注意的事项(短细则清单)
alwaysApply: true
enabled: true
updatedAt: 2026-08-15
provider:
---

# skills 开发细则需要注意的事项

> **重要**:本文件只列短细则。**完整创建/更新/升级流程**(协议先行 + 多维度一致)请读
> [skill-creation-workflow.md](skill-creation-workflow.md)。

> **V11.8.0.1 路径迁移通知(2026-08-15 NEW)**:本文件原在 `.agents/rules/skills开发细则.md`(中文文件名),V11.8.0.1 起迁移到 `.agents/skills/project-rule-skill/references/skills-development-rules.md`,并改为英文文件名以提升跨平台兼容性。
> **原因**:与 project-rule-skill 同包,作为其 references/;中文文件名在部分 Windows 工具链下有兼容问题。

---

## 短细则(必读)

- MUST: 有需要配置环境的，把 skill 专属的环境变量示例写到 skills 目录下的 `.env.example`。
- MUST: 运行测试的时候，使用脚本自动去项目的根目录加载 `.env`。
- MUST: 创建/更新任何 skill 前,先读 [skill-creation-workflow.md](skill-creation-workflow.md) §3,确定走"新建 / 升级 / 合并 / 废弃"哪条路。
- MUST: 创建/更新任何 skill 时,严格遵守 [skill-creation-workflow.md](skill-creation-workflow.md) §1 协议先行(WHY→WHO→Schema→HOW→Coverage)+ §2 多维度同步(6 维度)。

---

## 反例

- MUST NOT: 有需要配置环境的，把 skill 没有专属的 `.env.example`。
- MUST NOT: 运行测试的时候，没有使用脚本自动去项目的根目录加载 `.env`。
- MUST NOT: skills 的脚本或者 md 里面有具体的 key 的硬编码，导致泄露信息。
- MUST NOT: 不读 [skill-creation-workflow.md](skill-creation-workflow.md) 就改 skill(违反协议先行原则)。
- MUST NOT: 改了 SKILL.md 但不同步 6 个维度的其他 5 个(reference/workflow/script/guard/CAPABILITY-MAP) — 违反多维度一致。