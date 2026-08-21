# Forge Protocol — 把 .trae/rules/ 锻造为 project_rules_skills

> 锻造器(本 skill 自带 `scripts/forge_project_rules_skill.py`)的协议。
> 目的:把项目级 rules 从「永久注入主上下文」改为「按需加载的入口 skill」。

---

## §0 适用场景

| 场景 | 触发条件 | 是否锻造 |
|------|---------|---------|
| 项目无 `.trae/rules/` | 主 agent 检查发现空目录 | ❌ 跳过(提示用户先创建) |
| 项目 `.trae/rules/` 1-2 个文件 | 总量 < 200 行,直接 Read 不爆 context | ❌ 跳过(收益太小) |
| 项目 `.trae/rules/` ≥3 个文件 | 总量 ≥200 行,全量注入会撑爆 | ✅ 锻造 |
| 项目已有 `.trae/skills/project_rules_skills/` | 主 agent 检测 mtime 过期 | ✅ 重跑(同步内容) |
| 高安全等级项目(防 sub-agent 绕过) | 需要物理隔离源 rules | ✅ 锻造 + `--move` |

---

## §1 锻造步骤(脚本实现)

### Step 0.5 — 自动注入 frontmatter(V0.2 NEW)

```python
for rule_name in existing_rules:
    rule_path = rules_dir / rule_name
    content = rule_path.read_text(encoding="utf-8")
    if has_frontmatter(content):
        continue  # 已有,跳过
    # 注入最小 frontmatter: description 字段从文件名推断
    frontmatter = "---\ndescription: <推断的描述>\n---\n\n"
    rule_path.write_text(frontmatter + content, encoding="utf-8")
```

**为什么**: 每个 rule 文件如果没元信息声明,sub-agent 加载后不知道"我是谁 / 何时用 / 关键约束"。frontmatter 让 rule 文件自带 description,可被 Skill 描述、文档索引、规则路由器识别。

**推断规则**(默认 description 字典):

| 文件名 | description |
|--------|-------------|
| `stack.md` | 项目栈命令速查 — 构建/测试/lint/dev server + V11 验收命令 |
| `paths.md` | 项目级禁读路径 + MCP 查询防护 + 脏逻辑记录 + 安全红线 |
| `git.md` | Git 工作流 — 分支策略 + commit 标签规范 + PR 模板 + 提交前自检 |
| `coding-standards.md` | 项目专属编码规范 — 桩代码标记 + 模型重复判定等 |
| 其他 | `项目级 rule: {文件名}` 通用兜底 |

**如何自定义**: 在 rule 文件**已有 frontmatter** 时脚本不会覆盖。手动写 `description: <你的描述>` 即可。

### Step 1 — 扫描源

```python
rules_dir = project_root / ".trae/rules"
existing_rules = sorted([
    f.name for f in rules_dir.glob("*.md")
    if f.name != "README.md"
])
```

**白名单**: 只处理 `.md` 文件。
**黑名单**: 跳过 `README.md`(入口文件,由脚本改写)。

### Step 2 — 创建入口 skill 目录

```
.trae/skills/project_rules_skills/
├── SKILL.md              ← 从本 skill 的 templates/SKILL.md.template 渲染
├── README.md             ← 从本 skill 的 templates/README.md.template 渲染
├── workflows/
│   └── sub-agent-delegate-load.md  ← 从本 skill 的 workflows/ 复制
└── references/           ← 创建空目录
```

**关键点**: SKILL.md 的 §3 路由表由脚本根据 `existing_rules` 动态填充,模板留占位符 `{{RULES_LIST}}` / `{{ROUTES_TABLE}}`。

### Step 3 — 同步源文件到 references/

```python
for rule_name in existing_rules:
    src = rules_dir / rule_name
    dst = refs_dir / rule_name
    # 包装: 加头尾注释,标注 single source of truth
    dst.write_text(
        f"<!-- 来源: .trae/rules/{rule_name} (single source of truth) -->\n"
        f"<!-- 不要直接修改本文件,改完后跑 forge_project_rules_skill.py 同步 -->\n\n"
        f"{src.read_text(encoding='utf-8')}\n",
        encoding="utf-8"
    )
```

**为什么用复制而非软链接**:
- Windows 软链接需要 admin 权限 + 开发体验差
- 复制 = 内容一致即可,文件路径解耦(规则源改路径也不影响)
- 头部注释明示 single source of truth,避免双写

### Step 3.5 — 可选 `--move` 物理移走(V0.2 NEW)

```bash
python forge_project_rules_skill.py --project-root . --move
```

**行为**: 把 `.trae/rules/{rule}.md` 物理移走到 `.trae/rules/_archived/{rule}.md`,然后继续 Step 3 复制到 `references/`。

**为什么需要**:

| 模式 | 物理位置 | 防绕过强度 | 适用 |
|------|---------|-----------|------|
| 默认(无 --move) | `.trae/rules/{rule}.md` 仍存在 | 🟡 中(README.md 引导 + 协议禁止) | 信任内部 agent |
| `--move` | `.trae/rules/_archived/{rule}.md` 归档 | 🟢 高(物理隔离,绕不过) | 多团队 / 外部 agent / 安全敏感项目 |

**归档目录设计**: `_archived/` 子目录(前缀 `_`)
- 命名带 `_` 前缀,显式标识为内部归档
- `pathlib glob("*.md")` 不递归,自动防二次扫描
- 归档文件**仍可 git 跟踪**,历史完整可回溯
- 如需恢复某个 rule,手动从 `_archived/` 移回即可

**回滚**: 用户手动 `mv .trae/rules/_archived/{rule}.md .trae/rules/`(脚本不自动回滚,避免误操作)

### Step 4 — 改写 .trae/rules/README.md 为强制入口

```python
readme_content = f"""# .trae/rules/ 强制入口

> **🔴 必读 · 本目录是规则源,本 README.md 是唯一可被 Read 的文件**
> 
> 任何 agent(主 agent / sub-agent)进入本项目执行任务前,
> **必须先调用** `Skill(name="project-rules")` 获取本会话所需 rules。
> 
> **禁止绕过本入口**直接 Read `.trae/rules/*.md` 中除本 README.md 外的其他文件。
> 
> skill 入口: `.trae/skills/project_rules_skills/SKILL.md`
> 
> ---
> 
> ## 本项目 rules 列表(由 forge 检测)
> 
> {chr(10).join(f"- `{r}`" for r in existing_rules)}
> 
> ## 加载协议
> 
> ```
> Step 1: 调用 Skill(name="project-rules")
> Step 2: 按路由表拿本会话所需 rules(SKILL.md §3)
> Step 3: 只 Read 选中的 rules(在 .trae/skills/project_rules_skills/references/)
> Step 4: sub-agent 必须在 Completion Report 声明 rules_loaded / rules_skipped
> ```
"""
rules_dir / "README.md" → 写入 readme_content
```

**效果**: 任何 agent 即使直接 Read README.md,也会被引导到 skill 入口,不会去 Read 其他 rule。

### Step 5 — 输出报告

```
✅ .trae/skills/project_rules_skills/ 已创建/更新
✅ 收纳 N 个 rules 到 references/
✅ .trae/rules/README.md 改为强制入口
📋 agent 必走 Skill(name="project-rules")
```

---

## §2 增量同步

**何时重跑**:
- `.trae/rules/*.md` 任一文件修改后
- `.trae/skills/project_rules_skills/SKILL.md` 路由表需要更新时(主 agent 可手动编辑,本 skill 不强制)
- 项目交接 / 新成员加入时

**重跑行为**:
- 已存在的 `references/{rule}.md` 会被覆盖(从源同步)
- 已存在的 SKILL.md 会被覆盖(用模板 + 新路由表)
- **不**删除项目自定义的 §3 路由表扩展(脚本会保留用户加的行)— 实际上脚本每次都全量重写,主 agent 应在 forge 后手动恢复自定义行

**未来改进**(v0.2 候选): 增加 `--preserve-custom-routes` 开关。

---

## §3 卸载

<!-- scan-whitelist:CMD_RM_RF -->
```bash
# 1. 删除入口 skill 目录
rm -rf .trae/skills/project_rules_skills

# 2. 如果之前跑过 --move,恢复归档的 rules
mv .trae/rules/_archived/*.md .trae/rules/

# 3. 删除归档目录
rmdir .trae/rules/_archived

# 4. 还原 .trae/rules/README.md(手动)
#    恢复成项目原本的 README.md(如果原本有)
```
<!-- /scan-whitelist -->

**警告**: 卸载后 sub-agent 失去强制入口保护,会直接 Read `.trae/rules/*.md`,可能撑爆 context。

---

## §4 反模式

```
❌ 跳过本 skill 自己写脚本(本 skill 自带 forge_project_rules_skill.py)
❌ 改 .trae/skills/project_rules_skills/references/ 而不同时改源 rules
❌ 把 .trae/rules/README.md 改成普通的 rules 列表入口(必须保持强制引导)
❌ 在项目里跑两次 forge 但路由表不同(以最后一次为准,中途会丢自定义)
❌ 高安全等级项目跑 forge 不加 --move(sub-agent 可绕过 skill 直接 Read 源)
❌ 直接 rm 归档目录下的 rule(归档 ≠ 删除,归档是为了 git 历史 + 回溯)
❌ rule 文件已有 frontmatter 时手动跑 forge 期望被覆盖(脚本检测已有则跳过,保护用户自定义)
```
