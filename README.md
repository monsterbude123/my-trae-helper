# my-trae-helper

Trae IDE 技能包开发工程 + 跨 Agent 技能市场 CLI。

> 这个仓库既是「技能包开发工程」也是「技能市场 CLI 源码」：
> - `skill-markets/` —— 23+ 个技能包
> - `bin/` + `src/` —— `@my-trae-helper/cli`（已发布到 npm）

## ⚡ 快速开始（推荐：用 npx）

```bash
# 装到 Trae CN（默认）
npx @my-trae-helper/cli add fullstack4TraeV11

# 一次装到多个 agent
npx @my-trae-helper/cli add fullstack4TraeV11 -a trae-cn -a claude-code -a codex

# 全局装（所有项目可用）
npx @my-trae-helper/cli add fullstack4TraeV11 -g -a trae-cn

# 看已装了哪些
npx @my-trae-helper/cli list

# 卸
npx @my-trae-helper/cli remove fullstack4TraeV11
```

## 🎯 支持的 Agent（22+）

| Agent | 路径前缀 | 说明 |
|---|---|---|
| **trae-cn** | `~/.trae-cn/skills/` | Trae CN（项目核心） |
| **trae** | `~/.trae/skills/` | Trae 国际版 |
| **claude-code** | `~/.claude/skills/` | Claude Code |
| **codex** | `~/.codex/skills/` | OpenAI Codex |
| **cursor** | `~/.cursor/skills/` | Cursor |
| **gemini-cli** | `~/.gemini/skills/` | Gemini CLI |
| **opencode** | `~/.config/opencode/skills/` | OpenCode |
| **windsurf** | `~/.windsurf/skills/` | Windsurf |
| **cline** | `~/.agents/skills/` | Cline |
| **kimi-code-cli** | `~/.kimi-code/skills/` | Kimi Code |
| **github-copilot** | `~/.copilot/skills/` | GitHub Copilot |
| ... | | 还有 10+ (antigravity, kiro-cli, qwen-code, roo, devin, ... ) |

## 📦 技能市场

```text
skill-markets/
├── fullstack4TraeV11/      # 全栈文档驱动开发 V11
├── fullstack4TraeV10/      # V10 旧版
├── fullstack4TraeV9/       # V9
├── coding-xinfa/           # 编码心法
├── browser-use-cloud/      # 浏览器自动化云
├── acceptance-discipline/  # 验收铁律
├── goal-mode/              # 目标追逐模式
├── gitnexus4Trae/          # GitNexus 知识图谱
├── ponytail4Trae/          # 懒人开发
├── trae-professional/      # Trae IDE 专业知识
├── product-teardown/       # 产品拆解
├── security-review/        # 安全审查
├── playwright-best-practices/
├── screenshot/             # 截图工具
├── vision-audit/           # 视觉审计
├── doc-map-manager/        # 文档知识图谱
├── game-production-kit/    # 游戏制作工具箱
├── comfyui-api-skills/     # ComfyUI 视频/图片生成
└── ... (23+ skills)
```

## 🛠️ CLI 命令

```bash
trae-skills add <name>           # 装一个 skill
trae-skills list                 # 列已装
trae-skills remove <name>        # 卸
trae-skills update [name]        # 更新（重做 symlink）
trae-skills init <name>          # 创建新 skill 模板
trae-skills --help               # 帮助
trae-skills --version            # 版本
```

### 全局选项

| 选项 | 说明 |
|---|---|
| `-g, --global` | 装到用户目录（`~/...`）而不是项目目录（`./...`） |
| `-a, --agent <name>` | 指定 agent，可多次（`-a trae-cn -a claude-code`） |
| `-y, --yes` | 跳过确认 |
| `--copy` | 复制文件而非软链（牺牲可更新性换兼容） |

## 🔧 安装机制

**默认用 symlink**（单一数据源，`git pull` 后自动生效）：

| 平台 | 方式 |
|---|---|
| Windows | `symlink(..., 'junction')`（无需管理员/开发者模式） |
| macOS / Linux | `symlink(..., 'dir')` |

要复制而不是软链：`trae-skills add xxx --copy`

## 🛠️ 本地开发（这个仓库）

```bash
# 1. 装依赖
pnpm install

# 2. 本地跑
node bin/cli.mjs --help
node bin/cli.mjs list
node bin/cli.mjs add fullstack4TraeV11 -a trae-cn -y

# 3. 测发布
npm pack --dry-run
```

## 📦 发布到 npm

```bash
# 1. 创建 npm org: my-trae-helper（首次）
#    https://www.npmjs.com/settings/yourname/organizations/

# 2. 登录
npm login

# 3. 发布
npm publish --access public
```

发布后用户可以：
- `npx @my-trae-helper/cli add xxx` —— 临时用
- `npm install -g @my-trae-helper/cli` —— 全局装

## 🔗 与 `npx skills` (vercel-labs/skills) 的关系

本 CLI 是 `npx skills` 的 Trae 优化版：

| 维度 | `npx skills` (vercel) | `npx @my-trae-helper/cli` (本仓库) |
|---|---|---|
| 来源 | 从任何 GitHub 仓库 clone | 本仓库 `skill-markets/` 内置 |
| 技能数 | 178+ (搜索) | 23+ (本仓库精选) |
| Agent | 70+ | 22+（专注 Trae 系 + 主流） |
| 特色 | 跨平台开源标准 | Trae CN 原生 + 中文化 |
| YAML 解析 | `yaml` | `yaml`（同款） |
| 交互 | `@clack/prompts` | `@inquirer/prompts` |

## 📚 技能格式（SKILL.md）

```markdown
---
name: my-skill              # 必需，kebab-case
version: "1.0.0"            # 必需
description: "做什么 + 何时用 + 触发词"  # 必需
requires:
  skills: [dep1, dep2]      # 强依赖
  optional: [opt1]          # 软引用
---

# My Skill

详细指令...
```

完整规范见 [AgentSkills.io 开放标准](https://agentskills.io/)。

## 📜 许可

MIT
