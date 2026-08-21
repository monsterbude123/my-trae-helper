# common-project-coding-conf — Task

> **任务**: 新建 skill `common-project-coding-conf`，接管 `vibe-coding-routes`(未落地) + `project-rules-gate`(已存在) 的合并职责：路由表 + 自检 + forge + 委派头部。

## TODO 列表

### Phase 1: 准备
- [ ] 查 CAPABILITY-MAP.md 避免能力重复
- [ ] Read project-rules-gate 全量源文件（scripts/templates/workflows/references）

### Phase 2: 落地
- [ ] Step 1 新建目录
- [ ] Step 2 写 SKILL.md
- [ ] Step 3 迁移 forge 脚本 + 模板 + workflows + references
- [ ] Step 4 写 cpcc-self-check.mjs
- [ ] Step 5 改 coding-xinfa description
- [ ] Step 6 补 fullstack4TraeV11 description

### Phase 3: 验证
- [ ] Step 7 跑自检脚本（期望 PASS/WARN，无 FAIL）
- [ ] Step 8 删除 project-rules-gate 目录
- [ ] Step 10 安全审查 scan_skills_dir.py
- [ ] Step 10 更新 SECURITY-MAP.md

### Phase 4: 治理
- [ ] Step 9 写 AGENTS.md 蒸馏记录
- [ ] Step 11 guard-smith 委派注册表更新

## 约束

- §1.1 SKILL.md 必带 `name` + `description`
- §1.4 新建 skill 必跑 `scan_skills_dir.py`
- §1.5 新增前查 `CAPABILITY-MAP.md`
- §1.11 注册表更新走 guard-smith 委派
- skills 开发细则：todo 跟踪完再删本文件