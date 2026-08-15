---
name: openapi-doc-exporter
version: 1.0.0
version: 1.0.0
description: "通用 OpenAPI 文档导出工具。当用户提到\"导出 API 文档\"\"生成接口 spec\"\"openapi 转 markdown\"\"API 协议文档\"\"前后端接口契约\"\"FastAPI openapi\"\"Swagger 转 markdown\"等场景时主动使用。框架无关，只消费 openapi.json，支持一体导出和按路由前缀分模块导出两种模式。适合任何能产出 OpenAPI 3.0/3.1 规范的 Web 框架（FastAPI/Flask/Express/Spring/NestJS 等）。"
intent: 通用 OpenAPI 文档导出工具
category: other
audience: [developer]
---
# OpenAPI 文档导出工具

通用 OpenAPI → Markdown 渲染器。框架无关：只消费 `openapi.json`，不依赖任何具体框架的运行时。

## 何时使用

主动触发场景：

- 用户说"导出 API 文档""生成接口 spec""API 协议文档""前后端接口契约"
- 用户说"openapi 转 markdown""Swagger 转 markdown""openapi.json 渲染"
- 用户说"FastAPI openapi""Flask openapi""Spring openapi"等导出需求
- 前后端联调前需要一份接口契约文档
- API 重构/迁移前的现状梳理
- 发版前生成 API 参考文档

## 核心工作流

### Step 1：确认输入源

询问/检测用户当前状态：

- **A. 已有 `openapi.json`** → 直接进入 Step 2
- **B. 需要从框架导出** → 查 `references/export-guide.md`，按对应框架方法导出
  - FastAPI：`app.openapi()` 或 `GET /openapi.json`
  - Spring Boot：`GET /v3/api-docs`
  - NestJS：`SwaggerModule.loadPluginMetadata(document)`
  - 其他框架见 export-guide

### Step 2：确认输出模式

二选一：

| 模式 | 适用场景 | 产物 |
|------|---------|------|
| `single` 一体导出 | 接口数 < 50 / 单文件易检索 / 团队习惯单文件 | 1 个 `.md` |
| `split` 分模块导出 | 接口数 ≥ 50 / 多团队按模块分工 / Git 友好 | README + 多个模块 md + 附录 |

> 经验法则：接口数 ≥ 50 或单文件 > 5000 行 → 强烈建议 `split`。

### Step 3：确认前缀映射（仅 split 模式）

- 复制 `assets/prefix-map.example.yaml` 作为模板
- 按项目实际路由前缀编辑（字段说明见 `references/prefix-mapping.md`）
- **最长前缀匹配**：`/api/packages` 优先于 `/api`，避免被父前缀吞掉
- 未匹配的接口自动归到 `99-unclassified.md`

### Step 4：执行渲染

```bash
# 一体导出
python scripts/render_md.py --input openapi.json --output api-protocol.md --mode single

# 分模块导出
python scripts/render_md.py --input openapi.json --output-dir docs/api/ --mode split --prefix-map assets/prefix-map.example.yaml
```

### Step 5：验证产物

```bash
# 先校验输入
python scripts/validate_openapi.py --input openapi.json

# 检查输出
# - single 模式：确认 .md 文件存在 + 包含所有接口
# - split 模式：确认目录下有 README.md + 多个模块 md + appendix-schemas.md
```

## 脚本使用说明

### `scripts/validate_openapi.py` — 格式校验

校验 openapi.json 是否符合 OpenAPI 3.0/3.1 规范，输出诊断报告。

```bash
python scripts/validate_openapi.py --input openapi.json
```

校验项：必填字段（openapi/info/paths）、method 合法性、responses 存在性、`$ref` 可解析性、schema 基本合规。

### `scripts/render_md.py` — 渲染 markdown

核心渲染脚本，支持 single / split 两种模式。

```bash
python scripts/render_md.py \
  --input openapi.json \
  --output api-protocol.md \      # mode=single 必填
  --mode single \                  # 或 split
  --title "API 协议 Spec" \         # 可选，默认 "API 协议 Spec"
  --version 1.0 \                  # 可选，默认读 openapi.json info.version
  --output-dir docs/api/ \         # mode=split 必填
  --prefix-map prefix-map.yaml     # mode=split 必填
```

参数说明：

| 参数 | 必填条件 | 说明 |
|------|---------|------|
| `--input` | 总是必填 | openapi.json 路径 |
| `--output` | `mode=single` 必填 | 单文件输出路径 |
| `--output-dir` | `mode=split` 必填 | 输出目录 |
| `--mode` | 可选 | `single`（默认）/ `split` |
| `--prefix-map` | `mode=split` 必填 | 前缀映射 YAML/JSON |
| `--title` | 可选 | 文档总标题 |
| `--version` | 可选 | 文档版本 |

### `scripts/split_by_prefix.py` — 拆分工具

独立的拆分工具，可单独使用。输入一个已渲染的大 markdown，按章节拆分为多文件。

```bash
python scripts/split_by_prefix.py \
  --input api-protocol.md \
  --output-dir docs/api/ \
  --prefix-map prefix-map.yaml    # 可选，无则按 ## 标题拆分
```

## 输出格式规范

详见 `references/output-format.md`。核心要点：

- 接口标题：`### {METHOD} {path}`
- 请求/响应用 Markdown 表格
- Schema 定义统一在附录
- SSE 端点（`text/event-stream`）显式标注
- WebSocket 端点（`ws://`/`wss://`）显式标注

## 前缀映射配置

详见 `references/prefix-mapping.md` 和 `assets/prefix-map.example.yaml`。

```yaml
- prefix: /api/packages
  module: 02-packages
  title: 包管理 API
  order: 2
```

字段：`prefix`（最长匹配优先）/ `module`（文件名）/ `title`（章节标题）/ `order`（顺序）。

## 各框架导出指引

详见 `references/export-guide.md`，覆盖 FastAPI / Flask / Express / NestJS / Spring Boot / Django / 手动构造。

## 常见问题

### Q1：openapi.json 不存在怎么办？

查 `references/export-guide.md` 找到对应框架的导出方法。多数框架有原生 OpenAPI 支持，访问 `/openapi.json` 或 `/v3/api-docs` 即可拿到。

### Q2：路由前缀不在映射表里怎么办？

未匹配的接口自动归到 `99-unclassified.md`，并在 README 中标红提示。补全 prefix-map 后重跑即可。

### Q3：接口数过多导致单文件过大怎么办？

切换 `split` 模式。建议阈值：接口数 ≥ 50 或单文件 > 5000 行。

### Q4：PyYAML 不可用怎么办？

prefix-map 支持降级为 JSON 格式（`.json` 文件），脚本会自动识别。

### Q5：OpenAPI 3.0 和 3.1 都支持吗？

支持。脚本根据 `openapi` 字段自动判断版本，3.0/3.1 共用渲染逻辑。

### Q6：如何重新拆分已渲染的单文件？

用 `scripts/split_by_prefix.py`，输入单文件 md + prefix-map，输出多文件。

## 示例命令

```bash
# 1. 仅校验
python scripts/validate_openapi.py --input openapi.json

# 2. 一体导出
python scripts/render_md.py \
  --input openapi.json \
  --output api-protocol.md \
  --mode single \
  --title "My API Spec"

# 3. 分模块导出
python scripts/render_md.py \
  --input openapi.json \
  --output-dir docs/api/ \
  --mode split \
  --prefix-map assets/prefix-map.example.yaml \
  --title "My API Spec"

# 4. 拆分已渲染的单文件
python scripts/split_by_prefix.py \
  --input api-protocol.md \
  --output-dir docs/api/ \
  --prefix-map assets/prefix-map.example.yaml
```

## 依赖

- Python 3.8+（标准库：json / argparse / pathlib / datetime / re / collections）
- PyYAML（可选，用于解析 YAML 格式的 prefix-map；不可用时降级支持 JSON）

## 文件清单

```
.trae/skills/openapi-doc-exporter/
├── SKILL.md                         # 本文件
├── scripts/
│   ├── render_md.py                 # 核心：openapi.json → markdown
│   ├── split_by_prefix.py           # 按前缀拆分多文件
│   └── validate_openapi.py          # 格式校验
├── references/
│   ├── export-guide.md              # 各框架如何导出 openapi.json
│   ├── output-format.md             # markdown 渲染规范
│   └── prefix-mapping.md            # 前缀映射配置说明
└── assets/
    └── prefix-map.example.yaml      # 前缀映射示例
```
