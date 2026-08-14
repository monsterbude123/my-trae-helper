# 技能脚本路径解析

> 触发条件：需要执行技能包内嵌的脚本（如 `.ps1`、`.sh`、`.py` 等）时。

---

## §1 路径解析决策树

```
需要执行技能脚本 script_name？
  │
  ├── 已知技能根目录 skill_root？
  │     ├── 是 → 拼接路径: {skill_root}/scripts/{script_name}
  │     │        ├── 文件存在 → 执行
  │     │        └── 文件不存在 → 搜索 skill_root 下所有子目录
  │     │              ├── 找到 → 用找到的路径
  │     │              └── 未找到 → 进入 §2 异常处理
  │     │
  │     └── 否 → 搜索技能根目录
  │            ├── 先查 {workspace}/.codebuddy/skills/{skill_name}/
  │            ├── 再查 {workspace}/.trae/skills/{skill_name}/
  │            ├── 再查 ~/.codebuddy/skills/{skill_name}/
  │            └── 以上都无 → 进入 §2 异常处理
  │
  └── 脚本路径为相对路径？
        ├── 以 ./ 或 ../ 开头 → 相对于当前工作目录解析
        ├── 以 skills/ 开头 → 相对于 workspace 根目录解析
        └── 纯文件名 → 按上述搜索链查找
```

---

## §2 异常处理

| 异常情况 | 处理方式 |
|---------|---------|
| 脚本文件不存在于任何已知路径 | 列表展示所有搜索过的路径，请求用户提供完整路径 |
| 脚本路径引用了不存在的技能 | 确认技能是否已安装：`ls .codebuddy/skills/` 和 `.trae/skills/` |
| 技能存在但脚本目录结构不同 | 列出技能根目录的实际结构，基于实际结构调整路径 |
| 路径跨越 workspace 边界（../ 逃逸） | 检查是否在安全目录范围内，跨边界需询问用户确认 |

---

## §3 路径引用约定速查

| 引用形式 | 相对于 |
|---------|--------|
| `skills/xxx/scripts/y.ps1` | workspace 根 |
| `./scripts/y.ps1` | 当前工作目录（cwd） |
| `y.ps1`（纯文件名） | 按 §1 搜索链查找 |

---

## §4 Context Engineering 5 Pillar — 路径解析维度（2026-08-14 增量）

> 来源：[external-report 2026-08-14 §M-04](../2026-08-14/external-report.md)

`gitnexus4Trae` 已实装:`impact` / `cypher` 是 **语义搜索**(`query`),不是 grep。但本文件 §1 的"先查 .codebuddy/skills/"仍可能让 agent 退化到 **路径搜索 → 多 read 文件 → 95k token** 的老路。

**5 Pillar 第 4 (相关代码示例) 在此处的应用**:

```
✅ 好 (语义优先):
   agent 想知道 skill 是否有 scripts/: 用 gitnexus.query({query:"skill-load-script-paths"})
                                       → 1.9k token,返回结构化清单

❌ 差 (grep 退化):
   agent 跑 find .trae/skills -name 'scripts' -type d + read SKILL.md
                                       → 95k token 扫大半个 monorepo
```

**结论**:脚本路径解析,应**优先**用 gitnexus / skill-dependency-check(语义)而非 `find -name`(grep)。详见 [skill-dependency-check.md §7 Pillar 4 示例](skill-dependency-check.md)。
