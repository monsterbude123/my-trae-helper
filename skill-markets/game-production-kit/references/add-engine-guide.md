# 新增引擎接入指南

当需要支持新引擎时，按以下步骤操作。

## 步骤

### 1. 在 §3 路由表注册

在 SKILL.md 的引擎替换方案表中新增一行：

```markdown
| [Engine Name] | `[name]-scripting` (待建) | `[name]-engine-build` (待建) | `[name]-engine-build` (待建) |
```

### 2. 创建脚本技能 `skills/[name]-scripting/`

必做：
- `SKILL.md`：定义脚本语法参考（类似 webgal-scripting 的子文档索引模式）
- `references/`：脚本命令、变量、场景管理等子文档
- 在 description 中声明"engine-specific: [Engine Name]"

禁止：
- 引用 engine-agnostic 技能不存在的路径
- 引用其他引擎的脚本技能

### 3. 创建构建技能 `skills/[name]-engine-build/`

必做：
- `SKILL.md`：定义构建流程和部署方式
- `references/`：构建详解、部署详解
- 在 description 中声明"engine-specific: [Engine Name]"

禁止：
- 引用 engine-agnostic 技能不存在的路径
- 引用其他引擎的构建技能

### 4. 更新 engine-decision-guide.md

在对应的游戏类型决策表（VN / 2D / 3D）中新增该引擎的条目。

### 5. 更新 CAPABILITY-MAP.md

在游戏制作群岛区新增该引擎的子技能条目。

## 技能命名规范

```
引擎无关: game-{domain}          (e.g., game-story-design, game-asset-pipeline)
引擎特定: {engine}-{domain}      (e.g., webgal-scripting, renpy-engine-build)
外部技能: {name} (ext)           (e.g., godogen, comfyui-api-skills)
```

## 引擎特定技能必须遵守

1. `description` 不含"跨引擎""引擎无关"字样
2. 不引用其他引擎技能的路径
3. 通过 `game-production-kit` 编排器接入，不独立暴露给用户（user-invocable: false）
4. 引用 engine-agnostic 技能时使用 skill name，不引用路径
