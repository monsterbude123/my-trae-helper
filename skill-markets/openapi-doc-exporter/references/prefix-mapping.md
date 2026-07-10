# 前缀映射配置说明

> 本文档描述 `prefix-map` 配置文件的格式、字段、匹配规则和使用方法。
> 仅在 `split` 模式（`render_md.py --mode split`）下必填。

## 1. 文件格式

支持 YAML（推荐）和 JSON 两种格式。脚本根据文件后缀自动判断，无后缀时优先尝试 YAML。

### YAML 示例

```yaml
- prefix: /api/health
  module: 01-health
  title: 健康检查
  order: 1

- prefix: /api/packages
  module: 02-packages
  title: 包管理 API
  order: 2
```

### JSON 示例

```json
[
  {
    "prefix": "/api/health",
    "module": "01-health",
    "title": "健康检查",
    "order": 1
  },
  {
    "prefix": "/api/packages",
    "module": "02-packages",
    "title": "包管理 API",
    "order": 2
  }
]
```

## 2. 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prefix` | string | 是 | 路由前缀，用于匹配 openapi.json 中的 path |
| `module` | string | 是 | 模块标识，用于生成输出文件名（不含 `.md` 后缀） |
| `title` | string | 是 | 章节标题，显示在文档中 |
| `order` | integer | 否 | 章节顺序，数字越小越靠前（默认 99） |

### 2.1 `prefix` 字段

- 必须以 `/` 开头
- 大小写不敏感匹配（路径通常小写）
- 支持多级前缀：`/api/v1/users`、`/api/v1/users/{id}/posts`
- **最长前缀匹配**：`/api/packages` 会优先于 `/api` 匹配 `/api/packages/123`

### 2.2 `module` 字段

- 建议格式：`{两位序号}-{slug}`，如 `02-packages`、`03-writing-engine`
- 输出文件名：`{order:02d}-{module}.md`，如 `02-packages.md`
- 不要包含 `.md` 后缀（脚本会自动添加）
- 建议用英文 kebab-case，避免中文和特殊字符

### 2.3 `title` 字段

- 显示在文档章节标题中：`## 第 N 章：{title}`
- 可包含中文：`包管理 API`、`写作引擎`
- 建议简洁明了，能体现模块业务含义

### 2.4 `order` 字段

- 整数，数字越小章节越靠前
- 第 1、2 章固定为概览和通用约定，`order` 从 3 开始
- 未指定时默认 99
- 建议预留间隔（3, 5, 7, ...）方便后续插入新模块

## 3. 匹配规则

### 3.1 最长前缀匹配

当多个 prefix 都能匹配某个 path 时，选择**最长**的那个：

```yaml
- prefix: /api
  module: 99-misc
  title: 其他 API
  order: 99

- prefix: /api/packages
  module: 02-packages
  title: 包管理 API
  order: 2
```

对于 path `/api/packages/123`：
- `/api` 匹配（长度 4）
- `/api/packages` 匹配（长度 13）
- 选择 `/api/packages`，归到 `02-packages.md`

### 3.2 大小写不敏感

path `/api/Health` 和 prefix `/api/health` 视为匹配。

### 3.3 前缀必须完整段匹配？

**否**。当前实现是字符串前缀匹配，不要求段边界。

- prefix `/api/users` 匹配 path `/api/users-extra`（不推荐这样命名）
- 若需严格段匹配，可在 prefix 末尾加 `/`：`/api/users/`

## 4. 未匹配接口处理

任何 path 如果不匹配 prefix-map 中的任何条目，自动归到 `99-unclassified.md`。

```yaml
# 假设 prefix-map 只有 /api/packages 和 /api/writing
# 以下 path 会归到 99-unclassified.md：
# - /api/health
# - /api/stats
# - /admin/users
```

README 中会显式列出 `99-unclassified.md`，提示用户补全 prefix-map。

## 5. 示例配置解读

```yaml
# ShuXia 项目的前缀映射

- prefix: /api/health
  module: 01-health
  title: 健康检查
  order: 1
  # 匹配 /api/health，单独成章（虽然是 1 个接口但很重要）

- prefix: /api/packages
  module: 02-packages
  title: 包管理 API
  order: 2
  # 匹配 /api/packages、/api/packages/{id} 等所有包管理路径

- prefix: /api/v1/writing
  module: 03-writing-v1
  title: 写作引擎 API v1
  order: 3
  # 匹配 /api/v1/writing/* 路径

- prefix: /api/writing
  module: 04-writing
  title: 写作引擎 API
  order: 4
  # 匹配 /api/writing/* 路径（与 v1 分开）

- prefix: /api/v1/settings
  module: 05-settings-v1
  title: 设置 API v1
  order: 5

- prefix: /api/settings
  module: 06-settings
  title: 设置 API
  order: 6

- prefix: /api
  module: 99-misc
  title: 其他 API
  order: 99
  # 兜底：匹配所有未归类的 /api/* 路径
```

## 6. 调试技巧

### 6.1 查看实际 path 分布

在写 prefix-map 前，先统计 openapi.json 中的 path 前缀分布：

```python
import json, re
from collections import Counter

spec = json.load(open("openapi.json", encoding="utf-8"))
paths = spec.get("paths", {})
c = Counter()
for p in paths:
    m = re.match(r"(/api/v\d+/[^/]+|/api/[^/]+)", p)
    if m:
        c[m.group(1)] += 1
for k, v in sorted(c.items()):
    print(f"{k}: {v}")
```

### 6.2 验证匹配结果

跑完 split 模式后，检查 `99-unclassified.md` 是否有内容：
- 有内容 → prefix-map 不完整，需补全
- 无内容或文件不存在 → 所有接口都已归类

### 6.3 多版本共存

如 `/api/foo` 和 `/api/v1/foo` 共存，建议拆为两个 module：

```yaml
- prefix: /api/foo
  module: 03-foo
  title: Foo API
  order: 3

- prefix: /api/v1/foo
  module: 04-foo-v1
  title: Foo API v1
  order: 4
```

## 7. 常见问题

### Q1：prefix-map 文件放哪里？

- 项目级：`docs/api/prefix-map.yaml`（推荐，跟随项目版本管理）
- Skill 级：`.trae/skills/openapi-doc-exporter/assets/prefix-map.example.yaml`（仅作模板）
- 临时：任意路径，通过 `--prefix-map` 参数指定

### Q2：JSON 格式怎么写？

把 YAML 数组转为 JSON 数组即可，字段名完全一致。脚本根据文件后缀（`.json` / `.yaml` / `.yml`）自动判断。

### Q3：PyYAML 没装怎么办？

用 JSON 格式的 prefix-map，脚本会自动降级解析 JSON。

### Q4：能不能不用 prefix-map？

可以。`single` 模式无需 prefix-map，会自动按路径前缀分组。`split` 模式必须提供 prefix-map。
