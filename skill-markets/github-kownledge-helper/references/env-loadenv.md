# 环境变量收口(load_env 模式)

> 业务代码 / 脚本禁止硬编码项目根、Skill 路径、用户目录。
> 所有运行时路径必须通过 `load_env()` + `get(key)` 收口。
> 单文件 ≤ 200 行。
>
> **本文件是通用模式**;具体 env 变量名 / 实现是示例,具体项目可改。

## 1. 核心铁律

```
MUST: 业务代码 / 脚本必须通过 load_env.get(key) 读路径
MUST NOT: 业务代码直读 process.env / os.homedir() / __dirname 拼接绝对路径
```

**原因**:硬编码路径导致:
- 跨平台失灵(`/mnt/c/` / `C:\` / `/Users/`)
- 多项目并行(`~/.trae-cn/skills/` 下多个 skill 实例路径冲突)
- 测试困难(无法 mock)

## 2. 标准接口(语言无关)

| 操作 | 接口 | 返回 |
|------|------|------|
| 加载 env | `load_env()` | 一次性,失败抛错 |
| 读值 | `get(key, default?)` | string,缺 key 报错或返回 default |
| 列出 | `list_keys()` | 返回当前实现支持的 key 列表 |

## 3. 标准 Key 列表(可改)

| key | 含义 | 默认值 |
|-----|------|--------|
| `project_root` | 项目根 | env `PROJECT_ROOT` 或显式 setx |
| `repos_root` | 仓库 clone 落地根 | `<project_root>/repos` |
| `docs_root` | 知识库根 | `<project_root>/docs` |
| `manifest_path` | 清单文件 | `<project_root>/manifest.json` |
| `doc_map_scripts` | doc-map-manager 脚本根 | `~/.trae-cn/skills/doc-map-manager/scripts` |

> **判定原则**:Key 命名 + 语义**沉淀**(通用约定);具体 env 名(如 `GITHUB_KNOWLEDGE_HELPER_SPACE`)是**示例**,具体项目可换。

## 4. 实现示例(TS / Node,参考)

```typescript
// src-cli/src/lib/load_env.ts
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ENV_PROJECT_SPACE = 'GITHUB_KNOWLEDGE_HELPER_SPACE'; // 示例 env 名

let cached: Record<string, string> | null = null;

export function load_env(): Record<string, string> {
  if (cached) return cached;
  const root = process.env[ENV_PROJECT_SPACE];
  if (!root) throw new Error(`env ${ENV_PROJECT_SPACE} not set`);
  cached = {
    project_root: root,
    repos_root: join(root, 'repos'),
    docs_root: join(root, 'docs'),
    manifest_path: join(root, 'manifest.json'),
    doc_map_scripts: join(
      process.env.USERPROFILE ?? process.env.HOME ?? '',
      '.trae-cn/skills/doc-map-manager/scripts'
    ),
  };
  return cached;
}

export function get(key: string, defaultValue?: string): string {
  const env = load_env();
  const v = env[key];
  if (v) return v;
  if (defaultValue !== undefined) return defaultValue;
  throw new Error(`env key ${key} not found`);
}
```

## 5. 测试要求

- 单测覆盖 11 用例(空 env / set 完整 env / get 不存在 key / get 带 default / process.env 直读守门禁 / 跨平台路径拼接)
- CI 守门禁:任何 `process.env` / `os.homedir()` 在业务代码出现 → 失败

## 6. 具体项目配置示例

| 项目 | env 变量名 | 备注 |
|------|-----------|------|
| 本 skill 原项目 | `GITHUB_KNOWLEDGE_HELPER_SPACE` | 已写入 HKCU\Environment(setx) |
| 其他项目 | `MY_PROJECT_SPACE` | 复制本文件实现,改 env 名 + key 列表 |

## 7. 与其他 references 关系

- `manifest-schema.md §4` → 具体项目配置示例表
- `commands.md` → TS CLI 实际怎么用 load_env 的命令模式
- `pitfalls.md §010` → Edit 工具残留反例(强相关:env 收口前后的差异)