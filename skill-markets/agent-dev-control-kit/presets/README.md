# Presets — 技术栈选型预设系统

> **统一、可扩展、自动识别**的技术栈脚手架与门禁/守卫配置预设。

## 一、定位

`presets/` 是 `agent-dev-control-kit` 的**选型层**。它为不同语言/框架（Node.js、Python、Go、Java…）预置了一组可直接落地的：

- 项目配置文件（`package.json` / `pyproject.toml` / `go.mod` / `pom.xml`）
- 源码目录约定（`src/`、`gates/`、`guards/`、`scripts/`）
- 守卫（Guard）脚本模板
- 门禁（Gate）脚本模板
- 初始化脚本

避免每个新项目从零搭一遍 `gates/` + `guards/` + `scripts/`。

## 二、目录结构

```
presets/
├── README.md                        # 本文件 — 选型系统总览
├── _index.yaml                      # 选型注册表 — 自动加载入口
├── nodejs/                          # Node.js 选型
│   ├── preset.yaml                  # 选型定义
│   ├── template/                    # 脚手架文件
│   │   ├── package.json
│   │   ├── src/
│   │   ├── tests/
│   │   ├── gates/
│   │   ├── guards/
│   │   └── scripts/
│   └── README.md
├── python/                          # Python 选型
├── go/                              # Go 选型
└── java-maven/                      # Java (Maven) 选型
```

## 三、加载优先级

```
1. ~/.agent-dev-control-kit/presets/        # 用户自定义（最高优先级）
2. <项目>/.agent-dev-control-kit/presets/   # 项目级覆写
3. skill-markets/agent-dev-control-kit/presets/  # 内置选型
```

> **优先级规则**：用户自定义 > 项目级 > 内置。同一 `id` 的选型，后加载的会被先加载的覆盖。

## 四、如何使用预设

### 4.1 自动检测（推荐）

`scripts/detect-stack.py` 会扫描当前目录的特征文件（`package.json` / `pyproject.toml` / `go.mod` / `pom.xml`），自动匹配 `_index.yaml` 中的 `detection.files` 字段，返回最匹配的预设 ID。

```bash
python scripts/detect-stack.py
# 输出：{"id": "nodejs", "confidence": 0.95}
```

### 4.2 显式指定

```bash
python scripts/init-from-preset.py --preset nodejs --target ./my-app
```

### 4.3 在 Agent 会话中使用

主 Agent / Sub-Agent 在初始化新项目时调用：

```yaml
execution_skills:
  - id: init-project
    use_preset: nodejs     # ← 引用 preset id
```

## 五、如何添加新选型

### 5.1 创建目录

```bash
mkdir -p presets/<your-preset>/template
```

### 5.2 编写 `preset.yaml`

参照 [`nodejs/preset.yaml`](nodejs/preset.yaml) 的结构，必填字段：

| 字段 | 说明 |
|------|------|
| `id` | 选型唯一 ID（小写 kebab-case） |
| `name` | 显示名 |
| `detection.files` | 用于自动识别的特征文件列表 |
| `toolchain.runtime` | 运行时（node/python/go/java） |
| `commands` | lint / typecheck / test / build 命令映射 |
| `paths` | 源码、测试、配置、文档路径 |
| `guards.default` | 默认守卫列表 |
| `gates.default` | 默认门禁分级 |

### 5.3 实现 `template/`

至少包含：
- 项目配置文件
- `src/` 一个最小可运行示例
- `tests/` 一个最小测试用例
- `gates/` 至少 1 个门禁脚本
- `guards/` 至少 1 个守卫脚本
- `scripts/` 至少 1 个初始化脚本

### 5.4 注册到 `_index.yaml`

在 `presets/_index.yaml` 的 `presets` 数组中追加：

```json
{
  "id": "rust",
  "name": "Rust",
  "description": "Rust 项目（Cargo）",
  "category": "language",
  "tags": ["rust", "cargo"],
  "files": ["preset.yaml"],
  "path": "rust"
}
```

### 5.5 跑通验证

```bash
# 校验 preset.yaml 合法
python scripts/validate-preset.py presets/<your-preset>/preset.yaml

# 校验 template/ 完整
python scripts/validate-template.py presets/<your-preset>
```

## 六、如何自定义选型

### 6.1 项目级覆写

在项目根目录创建 `.agent-dev-control-kit/presets/nodejs/`，覆写任意文件。`init-from-preset.py` 会优先用项目级版本。

### 6.2 用户级扩展

在 `~/.agent-dev-control-kit/presets/` 创建同名目录，最高优先级。

### 6.3 局部变量覆写

通过 `variables` 字段透传：

```bash
python scripts/init-from-preset.py \
  --preset nodejs \
  --var author="张三" \
  --var port=8080 \
  --var license=Apache-2.0
```

## 七、设计原则

1. **约定优于配置** — 选型内已约定好目录结构、命令、门禁分级，开箱即用
2. **可观测可调试** — 每个选型提供 `validate-preset.py` / `validate-template.py` 自检
3. **零外部目录依赖** — 选型内所有脚本只依赖 `presets/<id>/template/` 内部文件
4. **多文件拆分** — 选型遵循 `scripts/` + `gates/` + `guards/` 分目录，禁止单文件架构
5. **跨平台兼容** — 脚本优先 Python 标准库；Shell 脚本用 POSIX 语法并提供 `.ps1` 版本

## 八、与 SKILL 的关系

| 概念 | 目录 | 何时用 |
|------|------|--------|
| Skill（技能） | `skills/<name>/SKILL.md` | 改变 Agent 行为 |
| Preset（选型） | `presets/<name>/preset.yaml` | 初始化新项目 |

- **Skill** 是"怎么做"（流程、约束）
- **Preset** 是"用什么做"（工具链、文件结构、命令）