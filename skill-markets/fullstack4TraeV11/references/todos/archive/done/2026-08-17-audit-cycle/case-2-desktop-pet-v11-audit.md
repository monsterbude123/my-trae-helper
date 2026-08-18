# case-2-desktop-pet-v11-audit — V11 规范审计待修清单

> **来源**:case 2 桌面宠物 (desktop-pet-v11) 子代理 self-attest + 主代理硬验收
> **日期**:2026-08-17
> **状态**:�� 审计完成,修补待决定
> **关联**:[feedback04.md](../../../.trae/reports/feedback04.md) 完整记录

---

## A. 待修 V11 脚本问题(HIGH)

### A-1: init-from-zero.py --rules-as-skill 双写路径冲突

- **位置**: `scripts/init-from-zero.py` `--rules-as-skill` 模式
- **现象**:子代理跑完后,4 rule 同时存在于 `.trae/skills/project_rules_skills/references/` 和 `.trae/rules/`
- **修复**:init 脚本加 `--rules-as-files` 模式,或让 `--rules-as-skill` 不在 `.trae/rules/` 留文件
- **预估**:改 1 个文件 + 1 个 commit

### A-2: spec-purge.py 不支持 V12 物理布局

- **位置**: `scripts/spec-purge.py` L26-29 (REQUIRED_ARTIFACTS 检查 L58-59)
- **现象**:V12 物理布局 `change/{fact,stage/{N}/,archive}/` 不含 spec.md / plan.md,spec-purge FAIL
- **修复**:V12 模式扫描 `stage/{N}/notes.md` + `fact/conventions.md / stack.md / intent.md` 当 fact 等价物
- **预估**:改 1 个文件 + 1 个 commit

### A-3: 状态卡 schema 文档 vs stage-gate.py 校验漂移

- **位置**: `references/state-card-protocol.md` VS `scripts/stage-gate.py` validate_state_card()
- **现象**:文档说 health = green,实现要求 `�� on-track`;文档没提 `card_type / card_id / gate_result` 等
- **修复**:`references/state-card.schema.json` 单源,文档 + 脚本都读
- **预估**:改 3 文件 + 1 commit

## B. 待修 V11 文档问题(MEDIUM)

### B-1: SKILL.md 缺 `paths.*` 字段说明

- **位置**: `SKILL.md` §0.5.1 / § 配置化部分
- **现象**:AGENTS.md §4.1 / feedback03-answer.md 都提 `paths.archive`,但 SKILL.md 无
- **修复**:SKILL.md 加新章节,链接 `_lib_paths.py` + `config.example.yaml`
- **预估**:改 1 文件 + 1-2 段

## C. 待入 trap-instructions.yaml(LOW)

### C-1: `_invalidated/` 入 commit

- **场景**:spec-purge 中转层 `_invalidated/{ts}-{id}/` 应不入 VCS
- **修复**:AP-16 新增,提示 .gitignore 加 `_invalidated/`

## D. 已完成(验收通过)

- ✅ A-1 走了 workaround(子代理双写 .trae/rules/),**实测可行,不改脚本也能用**
- ✅ A-2 走了 workaround(子代理加 6 forwarder),**实测可行,不改脚本也能用**
- ✅ A-3 在 case 1 E2E 暴露,子代理在 case 2 提前学到,**未阻断**
- ✅ B-1 主代理口头补充,子代理按 `paths.archive` 默认值跑通

## E. 优先级

| 优先级 | 项 | 原因 |
|--------|-----|------|
| P0 | A-1 init-from-zero 双写 | 每次新建项目都踩 |
| P0 | A-2 spec-purge V12 不兼容 | V12 是默认布局,踩坑高频 |
| P1 | A-3 状态