# AGENTS.md — 项目级 AI 规则模板（让 agent 按需配置）

> **设计原则（无冗余）**：
> - V11 内部已含的（16 Articles / stage 流水线 / 4 维评分 / 反模式库 / Hook 协议）→ **绝不复制**
> - 本模板只列**项目级独有**章节，agent 根据项目实际情况填充
> - 部署位置：项目根目录 `AGENTS.md`

> **如何使用本模板**：
> 1. agent 加载 V11 skill 后读取本模板
> 2. 按项目实际 stack / 团队约定填充占位符
> 3. **省略不适用的章节**（如 backend 项目无浏览器自动化，可删 §5）
> 4. 输出到项目根 `AGENTS.md`

---

## 模板

```markdown
# AGENTS.md — {项目名}

> 本文件由 AI Agent 根据 V11 skill 模板 + 项目实际情况生成。
> 编排器已部署在 `~/.trae-cn/skills/fullstack4TraeV11/`（独立部署）。

## 1. V11 入口

使用 Skill: **fullstack4traev11**（V11）。

V11 入口加载协议、stage 流水线、16 Articles 宪法、铁律、反模式库 → 全部在 `~/.trae-cn/skills/fullstack4TraeV11/SKILL.md` + `references/`。

**禁止**在本文件重复 V11 内部规则（Article XVI §1.4 修复成本 vs 价值 → 重复是低价值修改）。

## 2. 项目栈

| 维度 | 值 |
|------|----|
| 类型 | {web / tauri / cli / library / backend} |
| 语言 | {语言 + 主版本} |
| 框架 | {框架} |
| 测试 | {测试框架} |
| 包管理 | {npm / pnpm / yarn / cargo / pip / uv} |

详细命令 → [.trae/rules/stack.md](.trae/rules/stack.md)

## 3. 项目级 stage_config

参见: [.trae/fullstack4traev11.config.yaml](.trae/fullstack4traev11.config.yaml)

## 4. 项目级 rules（独立于 V11 skill）

- [.trae/rules/stack.md](.trae/rules/stack.md) — 构建/测试/lint 命令
- [.trae/rules/paths.md](.trae/rules/paths.md) — 项目级禁读路径
- [.trae/rules/git.md](.trae/rules/git.md) — Git 工作流

## 5. 项目级钩子（V11 默认 + 项目扩展）

参见: [.trae/hooks/](.trae/hooks/)

V11 默认 3 个 hook（pre-stage / post-stage / pre-accept）由 init-from-zero.py 生成。
项目可加 hook（如 pre-commit / pre-push），规则在 [.trae/rules/git.md](.trae/rules/git.md)。

## 6. 验收门禁

```bash
# V11 hooks 必跑 + Fresh 验证
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/hooks-fidelity.py --project-root .
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/upgrade-from-v10.py --project-root . --fidelity-check-only
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/state-card-validator.py .trae/state-card.md
```

## 7. 紧急通道（5 字段阻塞报告）

参见 V11 Article XV（无需在本文件重复）：

```yaml
blocker:
  type: "[env_dependency|test_fail|type_error|startup_fail|other]"
  description: "[具体错误信息]"
  attempted_solution: "[已尝试方案]"
  time_consumed_minutes: N
  attempt_count: N
```
```

---

## Agent 生成 AGENTS.md 的步骤（4 步）

```
Step 1: 读本模板 + 项目实际信息（语言 / 框架 / 测试）
Step 2: 删掉不适用的章节（如 backend 无浏览器自动化 → 删 §5.2）
Step 3: 填充 {xxx} 占位符
Step 4: 输出项目根 AGENTS.md
```

## 反例（agent 必走 V16）

- ❌ 在 AGENTS.md 复制 16 Articles 全文 → 🛑 低价值重复（Article XVI §1.4）
- ❌ 在 AGENTS.md 复制 stage 流水线 → 🛑 V11 SKILL.md 已含
- ❌ 在 AGENTS.md 复制铁律 / 反模式 → 🛑 V11 references/ 已含
- ❌ AGENTS.md > 200 行 → 🛑 项目级应精简

---

## 不放本模板的内容（已在 V11 skill 内）

| 内容 | 在哪里 |
|------|--------|
| 16 Articles 宪法 | `~/.trae-cn/skills/fullstack4TraeV11/references/constitution.md` |
| 13 stage 流水线 | `~/.trae-cn/skills/fullstack4TraeV11/SKILL.md` §0 |
| 4 维评分 + 3 类通过依据 | `~/.trae-cn/skills/fullstack4TraeV11/skills/09-review/SKILL.md` |
| 10 项腐化扫描 | `~/.trae-cn/skills/fullstack4TraeV11/skills/10-rot-scan/SKILL.md` |
| 公共反模式库 | `~/.trae-cn/skills/fullstack4TraeV11/references/common-anti-patterns.md` |
| 状态卡 schema | `~/.trae-cn/skills/fullstack4TraeV11/references/state-card-protocol.md` |
| §0.5 加载协议 | `~/.trae-cn/skills/fullstack4TraeV11/SKILL.md` |
| Hook 生命周期 | `~/.trae-cn/skills/fullstack4TraeV11/SKILL.md` §4 |
| Stage 移交约定 | `~/.trae-cn/skills/fullstack4TraeV11/references/stage-interaction-protocol.md` |
| 5 字段阻塞报告 | `~/.trae-cn/skills/fullstack4TraeV11/references/constitution.md` Article XV |
| 质疑性校验 4 维度 | `~/.trae-cn/skills/fullstack4TraeV11/references/constitution.md` Article XVI |

---

## 关联引用

- [project-rules-example/](project-rules-example/) — rules 模板
- [init-from-zero.py](../scripts/init-from-zero.py) — 仅生成 config + hooks（不生成 AGENTS / rules）
- [V11 SKILL.md §0.5 加载协议](../../SKILL.md)