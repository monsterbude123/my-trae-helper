# 发布管线模式

> 吸收自 godogen publish.sh (242行) + 5 个 scripts/publish/ 脚本 + CC Studio release-checklist。

游戏构建产物到多平台发布的完整流程。

## 发布入口 (publish.sh 模式)

来自 godogen 的发布入口模式：单一 shell 脚本 → 引擎路由 → Agent 分发 → 状态报告。

```bash
# 发布入口: 指定引擎 + 路径
publish.sh --engine {godot,bevy,babylon} --path /path/to/project

# 内部逻辑:
# 1. 验证路径和引擎
# 2. 检测 Agent 环境 (Claude Code / Codex CLI)
# 3. 渲染配置模板 (${KEY} 变量替换)
# 4. 注入 Agent 配置 (注册钩子/技能)
# 5. 启动 Agent 执行构建任务
# 6. 收集结果 → 生成状态报告
```

## 多 Agent 分发

> 来自 godogen 双 Agent 架构。根据用户安装的 CLI 自动分发。

```
Claude Code 已安装 → 注入 .claude/ skills/hooks/rules → 启动 claude
Codex CLI 已安装   → 注入 .codex/ skills/hooks/rules → 启动 codex
两者都无         → 提示安装
```

**Agent 配置注入**:
```bash
# 注册技能: SKILL.md → Agent 可解析格式
python scripts/publish/generate_codex_metadata.py    # → openai.yaml
python scripts/publish/inject_claude_lookup_frontmatter.py  # → context/model/agent

# 注册钩子: 构建后验证/通知
python scripts/publish/merge_claude_stop_hook.py     # → settings.json hooks
python scripts/publish/write_codex_stop_hook.py      # → config.toml hooks
```

## 模板变量渲染

> 来自 godogen render_dir.py。`${KEY}` 占位符替换。

```bash
python scripts/publish/render_dir.py \
  --input template/ \
  --output project/ \
  --define PROJECT_NAME="my_game" \
  --define ENGINE="godot" \
  --define AGENT="claude"
```

**模板目录结构**:
```
template/
├── CLAUDE.md.template       # → CLAUDE.md (${PROJECT_NAME}, ${ENGINE})
├── project.godot.template   # → project.godot
├── .claude/
│   └── skills/
│       └── game.SKILL.md.template
└── AGENTS.md.template
```

## 发布状态报告

```markdown
# Publish Report: {game-key} @ {build-tag}
**引擎**: {engine}
**平台**: {platforms}
**Agent**: {claude/codex}
**状态**: ✅ SUCCESS / ⚠️ WARNING / ❌ FAILURE
**产物**: {paths}
**Proof**: screenshots/result/{build_tag}/
**部署**: {deployment_url}
```

## 与 kit 的集成

Kit 不使用 shell 脚本分发模式（那是外部工具），而是将发布管线的三个关键能力内化：

1. **引擎路由** → SKILL.md §3 引擎表 → Phase 3/5/6 按引擎选择子技能
2. **变量模板** → `templates/` 目录（state-card.md, workflows/）
3. **状态报告** → `.project-state-card.md`（Cockpit 驾驶舱）
