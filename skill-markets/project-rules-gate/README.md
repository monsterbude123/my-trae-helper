# project-rules-gate

> 项目级 Rules 强制加载与子代理门禁 — 把散落的 `.trae/rules/*.md` 锻造为入口 skill,并强制任何 sub-agent 行动前必走该入口 + Completion Report 声明 rules_loaded/skipped。

## 这是什么

`fullstack4TraeV11` 内部有一个机制叫 `[PROJECT-RULES-GATE]`:把项目的多个 rule 文件收纳成一个入口 skill,强制 sub-agent 必须走这个入口(而不是直接 Read rule 文件撑爆 context)。

**本 skill 是该机制的独立分发版** — 完全不依赖 V11,不依赖 GitNexus,不依赖任何编排器。可单独安装,适用于任何项目。

## 解决的问题

```
.trae/rules/
├── stack.md           ← 200+ 行
├── paths.md           ← 100+ 行
├── git.md             ← 150+ 行
├── coding-standards.md ← 100+ 行
└── ... (更多)
```

这些文件通过 `workspace_rules` **永久注入主上下文**,每次启动都加载 ~800+ 行,**直接撑爆 context**。而且 sub-agent 默认会绕过 skill 入口,直接 Read 文件。

**解法**: 一次性把这些文件锻造为 `.trae/skills/project_rules_skills/` 入口 skill,通过路由表按需加载 + 强制 sub-agent 走入口。

## 结构

```
project-rules-gate/
├── SKILL.md                                  ← 技能入口(10 铁律 + 路由表 + 委派协议)
├── README.md                                 ← 本文件
├── scripts/
│   └── forge_project_rules_skill.py         ← 锻造器(自包含,零依赖)
├── references/
│   ├── forge-protocol.md                    ← 锻造协议
│   └── agent-delegate-protocol.md           ← 委派 GATE 头 + Completion Report 校验
├── workflows/
│   └── sub-agent-delegate-load.md           ← 委派头部模板(自动复制到项目)
└── templates/
    ├── SKILL.md.template                    ← 入口 SKILL.md 模板
    └── README.md.template                   ← 入口 README.md 模板
```

## 安装

```powershell
# Windows
$skillPath = "$env:USERPROFILE\.trae-cn\skills\project-rules-gate"
if (Test-Path $skillPath) {
    Write-Host "⚠️ 已安装: $skillPath"
} else {
    New-Item -ItemType SymbolicLink -Path $skillPath -Target "${PWD}\skill-markets\project-rules-gate" -Force
    Write-Host "✅ 安装完成,请重启 IDE"
}
```

```bash
# macOS / Linux
ln -s "$(pwd)/skill-markets/project-rules-gate" ~/.trae-cn/skills/project-rules-gate
```

## 使用

### Step 1: 项目准备

确保项目根有 `.trae/rules/`,放你的项目级 rule 文件(stack.md / paths.md / git.md / coding-standards.md 等)。

### Step 2: 跑锻造器

```bash
# Windows
python "$env:USERPROFILE\.trae-cn\skills\project-rules-gate\scripts\forge_project_rules_skill.py" --project-root .

# macOS / Linux
python ~/.trae-cn/skills/project-rules-gate/scripts/forge_project_rules_skill.py --project-root .

# 加 --move(高安全等级项目推荐)
python ~/.trae-cn/skills/project-rules-gate/scripts/forge_project_rules_skill.py --project-root . --move

# 先演练不写文件
python ~/.trae-cn/skills/project-rules-gate/scripts/forge_project_rules_skill.py --project-root . --dry-run
```

输出:
```
[OK] 已注入 frontmatter: paths.md
[OK] 已注入 frontmatter: stack.md
[OK] 已创建 .trae/skills/project_rules_skills
[OK] 已渲染 SKILL.md / README.md
[OK] 已同步 4 个 rule 到 references/
[OK] (--move) 已移走 4 个 rule 到 _archived/
[OK] 已复制 workflows/
[OK] 已改写 .trae/rules/README.md 为强制入口
```

**默认行为**:
- 自动给 rule 文件注入 YAML frontmatter(已有则跳过,保护自定义)
- 复制到 `.trae/skills/project_rules_skills/references/`(源不动)

**`--move` 行为额外**:
- 把 `.trae/rules/{rule}.md` 物理移走到 `.trae/rules/_archived/{rule}.md`
- 防 sub-agent 绕过 skill 直接 Read 源 rules
- 归档仍可 git 跟踪 + 手动回滚

### Step 3: 主 agent 委派时注入 GATE 头

```python
Task(
    subagent_type="general-purpose",
    description="改 API",
    prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
  在 Completion Report 中必须声明 rules_loaded / rules_skipped 清单。
[/PROJECT-RULES-GATE]

[TASK]
  帮我改 user API 加分页参数
[/TASK]
"""
)
```

### Step 4: sub-agent Completion Report 校验

```yaml
artifacts: [user-api.ts 修改完成]
status: PASS
evidence: ...
rules_loaded:
  - coding-standards.md (reason: 改 API)
  - paths.md (reason: 改 API)
rules_skipped:
  - stack.md
  - git.md
```

缺 `rules_loaded` / `rules_skipped` = 🛑 REJECT。

## 依赖

**零外部依赖**。仅 Python 3.8+ 标准库。

## 与 fullstack4TraeV11 共存

两个 skill 可同时装,行为完全一致(V11 内部用的就是同一份协议)。装两个不冲突,只是 V11 会自动调用本 skill 的产物。

## 安全

- 锻造器仅在 `--project-root` 指定目录内操作
- 不联网、不执行 shell
- 不删除任何用户文件
- 详见 [SECURITY-MAP.md 评分](../../SECURITY-MAP.md)

## 协议说明

| 文档 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 技能入口 + 10 铁律 + 路由表 |
| [references/forge-protocol.md](references/forge-protocol.md) | 锻造协议细节 |
| [references/agent-delegate-protocol.md](references/agent-delegate-protocol.md) | 委派 GATE 协议 |
| [workflows/sub-agent-delegate-load.md](workflows/sub-agent-delegate-load.md) | 委派头部模板 |

---

*版本: v0.1*
*锻造协议来源: fullstack4TraeV11 [PROJECT-RULES-GATE] 机制(独立分发版)*
